"""Pick what `art-crit run` runs, interactively, when no -m/--set was given (or with -i/--pick).

Plain `input()` prompts, standard library only: a harness menu, then that harness's models (numbers
select; any other text is an fzf-style fuzzy search that filters the list), then the effort levels of each
picked model (the same LEVELS syntax as -m, `all` by default). A catalog too long to read in a terminal
is not listed up front: the prompt asks for a search first, and every listing is capped. The result is a
list of `-m` specs, so it goes through exactly the same planning and validation as a spec typed on the
command line — including the harness prefix, so a `--pick` next to existing specs can't be misread.

`ask`/`echo` are injectable so tests drive the prompts without a terminal."""

import re
import subprocess

from .harness import HARNESSES
from .util import CritError, expand_levels

# How many models one listing shows. More than a screenful is not a list to pick from, it is a scrollback
# to lose the prompt in — a search (or `list`, on purpose) is how you get further than this.
LIST_LIMIT = 20


def parse_selection(text, count, what):
    """'1,3-5' or 'all' -> 0-based indexes, in the order typed and without repeats; '' -> []
    (the caller decides what empty means). Anything else (a non-number, or a number outside 1..count)
    is a CritError naming `what`; `is_selection` says which inputs are meant as a selection at all."""
    picked = []
    for token in re.split(r"[,\s]+", text.strip()):
        if not token:
            continue
        if token.lower() == "all":
            picked += list(range(count))
        elif re.fullmatch(r"\d+-\d+", token):
            first, last = (int(n) for n in token.split("-"))
            picked += list(range(min(first, last) - 1, max(first, last)))
        elif token.isdigit():
            picked.append(int(token) - 1)
        else:
            raise CritError(f"bad {what} selection {token!r}: use numbers such as 1,3-5, or all")
    outside = [i + 1 for i in picked if not 0 <= i < count]
    if outside:
        raise CritError(f"{what} has no number {', '.join(map(str, outside))} (1-{count})")
    return list(dict.fromkeys(picked))


def is_selection(text):
    """True when every token is a number, a range or 'all' — i.e. the user meant the shown numbering,
    not a search. Anything else ('luna', '5.5', 'gpt-6') is a query for `fuzzy_matches`."""
    tokens = [t for t in re.split(r"[,\s]+", text.strip()) if t]
    return bool(tokens) and all(t.lower() == "all" or t.isdigit() or re.fullmatch(r"\d+-\d+", t) for t in tokens)


def fuzzy_score(query, model):
    """fzf-style subsequence score of `query` against a model id: its letters and digits must appear in
    order, ignoring separators, so 'claudeop55' and 'claude opus' both find claude-opus-5-5. Higher is
    better: hits that start a word and runs of consecutive hits score more, a shorter id breaks ties.
    None when the query doesn't fit the id at all. Every possible start is tried, so the best run wins."""
    query = "".join(ch for ch in query.lower() if ch.isalnum())
    if not query:
        return None
    text = model.lower()
    chars = [(i, c) for i, c in enumerate(text) if c.isalnum()]
    best = None
    for start in range(len(chars)):
        if chars[start][1] != query[0]:
            continue
        score, previous, streak, j = 0, None, 0, start
        for q in query:
            while j < len(chars) and chars[j][1] != q:
                j += 1
            if j == len(chars):
                break
            i = chars[j][0]
            score += 1
            if previous is not None and i == previous + 1:
                streak += 1
                score += 4 * streak  # a run of consecutive hits ('luna' in ...,-luna) is a strong signal
            else:
                streak = 0
                if i == 0 or not text[i - 1].isalnum():
                    score += 3  # the hit starts a word or path segment
            previous, j = i, j + 1
        else:
            best = score if best is None else max(best, score)
    return None if best is None else best * 1000 - len(text)


def fuzzy_matches(query, models):
    """The models a query matches, best first (see `fuzzy_score`); [] when nothing matches."""
    scored = [(s, m) for m in models if (s := fuzzy_score(query, m)) is not None]
    return [m for _, m in sorted(scored, key=lambda sm: (-sm[0], sm[1]))]


def choose(ask, echo, question, count, what, default=""):
    """A selection prompt, re-asked until it parses. '' accepts `default`, or picks nothing."""
    while True:
        text = ask(question).strip() or default
        try:
            return parse_selection(text, count, what)
        except CritError as e:
            echo(f"  {e}")


def pick_models(harnesses, ask=None, echo=None):
    """The harness -> models -> levels menu, as `-m` specs in pick order. [] when nothing was picked."""
    ask, echo = ask or input, echo or print
    names = list(HARNESSES)
    echo("harnesses:")
    for i, name in enumerate(names, 1):
        echo(f"{i:>2}. {name}")
    picked = choose(ask, echo, "harness [1]: ", len(names), "harness menu", "1")
    specs = []
    for name in (names[i] for i in picked):
        specs += _harness_specs(harnesses[name], name, ask, echo)
    return specs


def _harness_specs(harness, name, ask, echo):
    """One harness's models, then a levels prompt per picked model -> ['NAME:MODEL:LEVELS', ...].
    A harness that can't list its models (not installed) is reported and skipped."""
    try:
        models = sorted(harness.models())
    except (CritError, OSError, subprocess.SubprocessError) as e:
        echo(f"{name}: {e} (skipped)")
        return []
    if not models:
        echo(f"{name}: no models to offer (skipped)")
        return []
    specs = []
    for model in choose_models(ask, echo, name, models):
        try:
            levels = _levels_spec(harness, model, ask, echo)
        except (CritError, OSError, subprocess.SubprocessError) as e:
            echo(f"{model}: {e} (skipped)")
            continue
        if levels:
            specs.append(f"{name}:{model}:{levels}")
    return specs


def choose_models(ask, echo, name, models):
    """The models prompt for one harness -> the picked models, in pick order. Numbers, ranges or 'all'
    select from the listing currently shown; any other text is a search that re-lists just the fuzzy
    matches (`fuzzy_matches`), at most LIST_LIMIT of them. A catalog longer than that is not listed until
    the user searches, or asks for it with 'list'. '' goes back to the full list (or, when that is the
    search-first view, just stays there), or picks nothing while a listing is shown."""
    if len(models) <= LIST_LIMIT:
        echo(f"\n{name} models  (pick numbers like 1,3-4 or all, or type to search)")
        listing = models
        _render_models(echo, listing)
    else:
        echo(f"\n{name} models: {len(models)} (too many to list: type a fuzzy search such as 'opus 5', "
             f"'list' to list them all, or Enter to pick none)")
        listing = []
    while True:
        text = ask("models [none]: ").strip()
        if not text:
            if listing is models or not listing:
                return []
            listing = models if len(models) <= LIST_LIMIT else []
            if listing:
                echo("")
                _render_models(echo, listing)
            continue
        if text.lower() == "list":
            listing = models
            echo("")
            _render_models(echo, listing)
            continue
        if is_selection(text):
            if not listing:
                echo(f"  search first (or 'list' to list all {len(models)}, then pick a number)")
                continue
            try:
                return [listing[i] for i in parse_selection(text, len(listing), f"{name} models")]
            except CritError as e:
                echo(f"  {e}")
                continue
        matches = fuzzy_matches(text, models)
        if not matches:
            echo(f"  no model matches {text!r}")
            continue
        listing = matches[:LIST_LIMIT]
        echo("")
        _render_models(echo, listing)
        if len(matches) > len(listing):
            echo(f"  … {len(matches) - len(listing)} more match — type a longer search to narrow these down")


def _render_models(echo, models):
    for i, model in enumerate(models, 1):
        echo(f"{i:>2}. {model}")


def _levels_spec(harness, model, ask, echo):
    """The LEVELS text for one model, re-asked until `expand_levels` accepts it; '' means every
    supported level, like a `-m` spec without a suffix. None when the model has nothing but 'off'."""
    supported = harness.levels(model)
    while True:
        text = ask(f"levels for {model} ({', '.join(supported)}) [all]: ").strip() or "all"
        try:
            levels = expand_levels(text, supported, model)
        except CritError as e:
            echo(f"  {e}")
            continue
        if not levels:
            echo(f"  {model}: no levels besides off (skipped)")
            return None
        return text
