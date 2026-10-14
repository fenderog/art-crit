"""The interactive model picker (`art-crit run` with no -m/--set, or -i/--pick): selection parsing,
the harness -> models -> levels menu, and the CLI wiring. Scripted `ask` functions stand in for a
terminal, so nothing here reads stdin or calls a model.
"""

import os
from pathlib import Path

import pytest

from art_crit.cli import main
from art_crit.harness import Harness, Pi
from art_crit.picker import fuzzy_matches, fuzzy_score, is_selection, parse_selection, pick_models
from art_crit.util import CritError

FAKE_PI = Path(__file__).parent / "fixtures" / "fake_pi"


class FakeHarness(Harness):
    """A harness whose models/levels are a table, or an error (a CLI that isn't installed)."""

    def __init__(self, name, table, error=None):
        self.name, self.table, self.error = name, table, error
        self.listed, self.level_calls = [], []

    def models(self):
        self.listed.append(True)
        if self.error:
            raise self.error
        return list(self.table)

    def levels(self, model):
        self.level_calls.append(model)
        levels = self.table[model]
        if isinstance(levels, Exception):
            raise levels
        return levels


def scripted(*answers):
    """An `ask` that answers in order and echoes each question into `asked`."""
    asked, answers = [], list(answers)

    def ask(question):
        asked.append(question)
        return answers.pop(0)

    return ask, asked


@pytest.fixture
def fake_harnesses(monkeypatch):
    """Two harnesses (pi-like and claude-code-like) plus one that can't list its models. Registered
    as the whole HARNESSES menu, so the picker's list is small and deterministic."""
    pi = FakeHarness("pi", {"openai-codex/gpt-6-sol": ["off", "low", "high"],
                            "test/limited": ["low", "medium", "high"]})
    claude = FakeHarness("claude-code", {"claude-opus-5-5": ["low", "high", "max"]})
    broken = FakeHarness("agy", {}, error=CritError("cannot run agy models: not found"))
    monkeypatch.setattr("art_crit.picker.HARNESSES", {"pi": None, "claude-code": None, "agy": None})
    return {"pi": pi, "claude-code": claude, "agy": broken}


# --- selection parsing -------------------------------------------------------------------------


def test_parse_selection_numbers_ranges_and_all():
    assert parse_selection("2", 4, "models") == [1]
    assert parse_selection("1,3-4", 4, "models") == [0, 2, 3]
    assert parse_selection("3-1", 4, "models") == [0, 1, 2]  # a backwards range is still a range
    assert parse_selection("all", 3, "models") == [0, 1, 2]
    assert parse_selection("2,2,1", 3, "models") == [1, 0]  # repeats collapse, order is kept
    assert parse_selection(" 2 , 3 ", 3, "models") == [1, 2]
    assert parse_selection("", 3, "models") == []


def test_parse_selection_rejects_bad_tokens_and_out_of_range():
    with pytest.raises(CritError, match="bad models selection 'two'"):
        parse_selection("two", 3, "models")
    with pytest.raises(CritError, match="models has no number 7 \\(1-3\\)"):
        parse_selection("1,7", 3, "models")
    with pytest.raises(CritError, match="harness menu has no number 0"):
        parse_selection("0", 3, "harness menu")


def test_is_selection_tells_numbers_from_search_text():
    assert is_selection("1") and is_selection("1,3-5") and is_selection("all") and is_selection(" 2 4 ")
    assert not is_selection("luna") and not is_selection("5.5") and not is_selection("1 luna") and not is_selection("")


# --- fuzzy search ------------------------------------------------------------------------------

MODEL_IDS = ["anthropic/claude-opus-5-5", "anthropic/claude-sonnet-5-5", "openai-codex/gpt-6-sol",
             "openai-codex/gpt-6-luna", "openrouter/openai/gpt-6-sol:batch", "google/gemini-3.8-flash"]


def test_fuzzy_score_matches_subsequences_ignoring_separators():
    assert fuzzy_score("claudeop55", "anthropic/claude-opus-5-5") is not None
    assert fuzzy_score("claude opus", "anthropic/claude-opus-5-5") is not None  # a space is just a separator
    assert fuzzy_score("g6sol", "openai-codex/gpt-6-sol") is not None
    assert fuzzy_score("luna", "openai-codex/gpt-6-sol") is None
    assert fuzzy_score("sol6", "openai-codex/gpt-6-sol") is None  # order matters
    assert fuzzy_score("opus", "anthropic/claude-opus-5-5") > fuzzy_score("opus", "anthropic/claude-o-p-u-s-5-5")
    assert fuzzy_score("---", "anthropic/claude-opus-5-5") is None  # a query with no letters or digits
    assert fuzzy_score("opus", "anthropic/claude-opus-5-5") > fuzzy_score("opus", "anthropic/claude-opus-5-5-longer-name")


def test_fuzzy_matches_ranks_the_closest_model_first():
    assert fuzzy_matches("luna", MODEL_IDS) == ["openai-codex/gpt-6-luna"]
    assert fuzzy_matches("claudeop55", MODEL_IDS) == ["anthropic/claude-opus-5-5"]
    assert fuzzy_matches("opus", MODEL_IDS)[0] == "anthropic/claude-opus-5-5"
    # A contiguous run in the shorter id outranks the same query spread over a longer one.
    assert fuzzy_matches("sol", MODEL_IDS)[0] == "openai-codex/gpt-6-sol"
    assert fuzzy_matches("zzz", MODEL_IDS) == []


# --- the menu ----------------------------------------------------------------------------------


def test_pick_models_returns_prefixed_specs_in_pick_order(fake_harnesses):
    ask, asked = scripted("2", "1", "high")  # claude-code, its only model, one level
    echoed = []
    assert pick_models(fake_harnesses, ask=ask, echo=echoed.append) == ["claude-code:claude-opus-5-5:high"]
    assert asked == ["harness [1]: ", "models [none]: ", "levels for claude-opus-5-5 (low, high, max) [all]: "]
    assert any(line.endswith("claude-code models  (pick numbers like 1,3-4 or all, or type to search)") for line in echoed)
    assert " 1. claude-opus-5-5" in echoed


def test_pick_models_several_harnesses_and_levels(fake_harnesses):
    ask, _ = scripted("1,2", "2,1", "low,high", "", "1", "max")  # pi, then claude-code
    specs = pick_models(fake_harnesses, ask=ask, echo=lambda *_: None)
    # pi: test/limited with low,high, then gpt-6-sol with its default (all); claude-code: max
    assert specs == ["pi:test/limited:low,high", "pi:openai-codex/gpt-6-sol:all",
                     "claude-code:claude-opus-5-5:max"]


def test_pick_models_defaults_to_pi_and_all_levels(fake_harnesses):
    ask, asked = scripted("", "1", "")  # empty harness answer -> pi; first model; empty levels -> all
    assert pick_models(fake_harnesses, ask=ask, echo=lambda *_: None) == ["pi:openai-codex/gpt-6-sol:all"]
    assert asked[0] == "harness [1]: "


def test_pick_models_skips_a_harness_that_cannot_list_models(fake_harnesses):
    ask, _ = scripted("3")  # agy is the only pick, and its models() fails
    echoed = []
    specs = pick_models(fake_harnesses, ask=ask, echo=echoed.append)
    assert specs == []
    assert "agy: cannot run agy models: not found (skipped)" in echoed
    assert fake_harnesses["agy"].level_calls == []


def test_pick_models_reasks_on_a_bad_selection_and_a_bad_level(fake_harnesses):
    ask, asked = scripted("9", "1", "2", "xhigh", "")  # 9 is out of range; xhigh isn't supported
    echoed = []
    specs = pick_models(fake_harnesses, ask=ask, echo=echoed.append)
    assert specs == ["pi:test/limited:all"]
    assert any("harness menu has no number 9" in line for line in echoed)
    assert any("level(s) xhigh not supported (supported: low, medium, high)" in line for line in echoed)
    assert asked.count("models [none]: ") == 1


def test_pick_models_filters_the_list_by_a_fuzzy_query(fake_harnesses):
    # The full list is [gpt-6-sol, test/limited]; '1' after the query picks test/limited, so the matches
    # were renumbered and picked from the filtered list.
    ask, answered = scripted("1", "limited", "1", "")
    echoed = []
    assert pick_models(fake_harnesses, ask=ask, echo=echoed.append) == ["pi:test/limited:all"]
    assert " 1. test/limited" in echoed
    assert "  no model matches" not in "".join(echoed)
    assert answered.count("models [none]: ") == 2


def test_pick_models_query_refines_and_empty_goes_back_to_the_full_list(fake_harnesses):
    fake_harnesses["pi"] = FakeHarness("pi", {"openai-codex/gpt-6-luna": ["low", "high"],
                                              "openai-codex/gpt-6-sol": ["low", "high"],
                                              "test/limited": ["low", "high"]})
    ask, _ = scripted("1", "zzz", "luna", "", "3", "")
    echoed = []
    # 'zzz' matches nothing (the full list stays), 'luna' filters to one, '' brings the full list back,
    # and '3' picks test/limited — a number that only exists in the full listing.
    assert pick_models(fake_harnesses, ask=ask, echo=echoed.append) == ["pi:test/limited:all"]
    assert "  no model matches 'zzz'" in echoed


def test_pick_models_out_of_range_number_is_an_error_and_is_reasked(fake_harnesses):
    ask, _ = scripted("1", "9", "1", "")
    echoed = []
    specs = pick_models(fake_harnesses, ask=ask, echo=echoed.append)
    assert specs == ["pi:openai-codex/gpt-6-sol:all"]
    assert "  pi models has no number 9 (1-2)" in echoed


def test_pick_models_empty_selection_picks_nothing(fake_harnesses):
    ask, _ = scripted("1", "")  # pi, then no models
    assert pick_models(fake_harnesses, ask=ask, echo=lambda *_: None) == []


def test_pick_models_reports_a_harness_with_no_models(fake_harnesses):
    fake_harnesses["pi"] = FakeHarness("pi", {})
    ask, _ = scripted("1")
    echoed = []
    assert pick_models(fake_harnesses, ask=ask, echo=echoed.append) == []
    assert "pi: no models to offer (skipped)" in echoed


def test_pick_models_skips_a_model_whose_levels_cannot_be_read(fake_harnesses):
    fake_harnesses["pi"] = FakeHarness("pi", {"broken/model": CritError("cannot ask broken/model: timed out")})
    ask, _ = scripted("1", "1")
    echoed = []
    assert pick_models(fake_harnesses, ask=ask, echo=echoed.append) == []
    assert "broken/model: cannot ask broken/model: timed out (skipped)" in echoed


def test_pick_models_skips_a_model_that_only_offers_off(fake_harnesses):
    fake_harnesses["pi"] = FakeHarness("pi", {"weird/model": ["off"]})
    ask, _ = scripted("1", "1", "")
    echoed = []
    assert pick_models(fake_harnesses, ask=ask, echo=echoed.append) == []
    assert "  weird/model: no levels besides off (skipped)" in echoed


def test_pi_harness_levels_and_models_are_used_by_the_picker(monkeypatch):
    """The picker talks to a real Harness object (fake pi on PATH), not a test double."""
    monkeypatch.setenv("PATH", f"{FAKE_PI}{os.pathsep}{os.environ['PATH']}")
    pi = Pi()
    assert "test/limited" in pi.models()
    ask, _ = scripted("1", str(sorted(pi.models()).index("test/limited") + 1), "low..medium")
    assert pick_models({"pi": pi}, ask=ask, echo=lambda *_: None) == ["pi:test/limited:low..medium"]


# --- CLI wiring --------------------------------------------------------------------------------


@pytest.fixture
def tty(monkeypatch):
    """A fake interactive terminal: isatty() true and `input` answered from a script."""
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    answers = []

    def input_(prompt=""):
        return answers.pop(0)

    monkeypatch.setattr("builtins.input", input_)
    return answers


@pytest.fixture
def picker_root(bench_root, tmp_path, git_repo, monkeypatch):
    runs_dir = tmp_path / "art-crit-runs"
    (bench_root / "art-crit.toml").write_text(f'[run]\ndir = "{runs_dir}"\nparallel = 8\ntimeout = "30m"\n')
    git_repo(bench_root)
    monkeypatch.setenv("PATH", f"{FAKE_PI}{os.pathsep}{os.environ['PATH']}")
    return bench_root


def test_no_models_on_a_tty_picks_them(picker_root, tty, capsys):
    tty += ["1", "6", "low,high"]  # pi; test/limited (6th of the fake pi list); two levels
    assert main(["run", "--dry-run", "a picked run", "--root", str(picker_root)]) == 0
    out = capsys.readouterr().out
    assert "harnesses:" in out and " 6. test/limited" in out
    assert "  1. test/limited:low" in out and "  2. test/limited:high" in out
    assert not (picker_root / "docs" / "data").exists()


def test_a_fuzzy_query_filters_the_model_list(picker_root, tty, capsys):
    tty += ["1", "luna", "1", "low"]  # pi; search; the single match; one level
    assert main(["run", "--dry-run", "a searched run", "--root", str(picker_root)]) == 0
    out = capsys.readouterr().out
    filtered = out.index(" 1. openai-codex/gpt-6-luna\n")  # the re-listed match, renumbered from 1
    assert "  1. openai-codex/gpt-6-luna:low" in out  # the plan
    assert "openai-codex/gpt-6-sol" not in out[filtered:]  # the search listed only the match


def test_pick_flag_adds_to_the_given_models(picker_root, tty, capsys):
    tty += ["1", "6", "low"]
    rc = main(["run", "--dry-run", "--pick", "a mixed run", "-m", "openai-codex/gpt-6-sol:low", "--root", str(picker_root)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "  1. openai-codex/gpt-6-sol:low" in out and "  2. test/limited:low" in out


def test_cancelled_pick_with_given_models_still_runs(picker_root, tty, capsys):
    tty += ["1", ""]  # no models picked
    rc = main(["run", "--dry-run", "--pick", "a run", "-m", "openai-codex/gpt-6-sol:low", "--root", str(picker_root)])
    assert rc == 0
    assert "  1. openai-codex/gpt-6-sol:low" in capsys.readouterr().out


def test_no_models_and_nothing_picked_is_an_error(picker_root, tty, capsys):
    tty += ["1", ""]
    assert main(["run", "--dry-run", "a run", "--root", str(picker_root)]) == 1
    assert "no models were picked" in capsys.readouterr().err


def test_pick_is_only_interactive(picker_root, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    assert main(["run", "--dry-run", "--pick", "a run", "-m", "openai-codex/gpt-6-sol:low", "--root", str(picker_root)]) == 1
    assert "--pick needs an interactive stdin" in capsys.readouterr().err


def test_no_models_on_a_non_tty_is_still_an_error(picker_root, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    assert main(["run", "a run", "--root", str(picker_root)]) == 1
    assert "at least one -m MODEL or --set is required" in capsys.readouterr().err


def test_pick_with_resume_is_refused(picker_root, tty, tmp_path, capsys):
    tty += []
    rc = main(["run", "--pick", "--resume", str(tmp_path / "nogbatch"), "--root", str(picker_root)])
    assert rc == 1
    assert "--pick can't be combined with --resume" in capsys.readouterr().err
