// hud.js — the "it's a film" furniture: letterbox bars, a title card, a
// running timecode, fading captions, vignette and a little film grain.
// All of it is generated in code (no external assets, no network).

const CSS = `
#film { position: fixed; inset: 0; pointer-events: none; user-select: none; }
#film .bar { position: absolute; left: 0; right: 0; height: 7.5vh; background: #06090c; }
#film .bar.top { top: 0; box-shadow: 0 1px 0 rgba(255, 240, 214, 0.06); }
#film .bar.bot { bottom: 0; box-shadow: 0 -1px 0 rgba(255, 240, 214, 0.06); }

#film .hud {
  position: absolute; inset: 7.5vh 3.2vw;
  font-family: ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, monospace;
  color: #f4e7d2;
  text-shadow: 0 1px 6px rgba(0, 0, 0, 0.45);
}
#film .row { position: absolute; display: flex; align-items: center; gap: .8em;
  font-size: clamp(9px, 1.05vw, 13px); letter-spacing: .34em; text-transform: uppercase; }
#film .tl { top: 0; left: 0; }
#film .tr { top: 0; right: 0; letter-spacing: .18em; }
#film .bl { bottom: 0; left: 0; opacity: .75; letter-spacing: .2em; }

#film .rec { width: .62em; height: .62em; border-radius: 50%; background: #e2543c; }
#film .tc { opacity: .85; }

#film .caption {
  position: absolute; left: 0; right: 0; bottom: 3.4vh; text-align: center;
  font-family: Georgia, "Times New Roman", serif; font-style: italic;
  font-size: clamp(15px, 2.5vw, 34px); letter-spacing: .06em; color: #fff6e6;
  text-shadow: 0 2px 22px rgba(0, 0, 0, 0.55);
  opacity: 0; transition: opacity 1.1s ease; padding: 0 8vw;
}
#film .caption.on { opacity: 1; }

#film .vignette {
  position: absolute; inset: 0;
  background: radial-gradient(120% 90% at 50% 46%, rgba(0,0,0,0) 42%, rgba(4,8,12,.42) 100%);
}
#film .grain {
  position: absolute; inset: -100px; opacity: .045; mix-blend-mode: overlay;
  background-repeat: repeat; background-position: 0 0;
  animation: grain 0.9s steps(6) infinite;
}
@keyframes grain {
  0%   { transform: translate3d(0, 0, 0); }
  25%  { transform: translate3d(-22px, 14px, 0); }
  50%  { transform: translate3d(16px, -18px, 0); }
  75%  { transform: translate3d(-12px, -8px, 0); }
  100% { transform: translate3d(8px, 20px, 0); }
}
#fallback { position: fixed; inset: 0; display: grid; place-items: center; padding: 8vw;
  font: 14px/1.6 ui-monospace, monospace; color: #e8dcc8; text-align: center; }
`;

const CAPTIONS = [
  { at: 2.5, dur: 7.5, text: 'dawn patrol' },
  { at: 25.0, dur: 8.0, text: 'he has never been a good flyer' },
  { at: 47.0, dur: 8.0, text: 'but he is an excellent passenger' },
];

export function createHud(stage, cycleSeconds) {
  const style = document.createElement('style');
  style.textContent = CSS;
  document.head.appendChild(style);

  const film = document.createElement('div');
  film.id = 'film';
  film.innerHTML = [
    '<div class="bar top"></div>',
    '<div class="bar bot"></div>',
    '<div class="hud">',
    '  <div class="row tl"><span class="rec" id="rec"></span><span>surfing pelican</span></div>',
    '  <div class="row tr"><span class="tc" id="tc">00:00:00</span></div>',
    '  <div class="row bl"><span>16 mm &middot; no birds were hurried</span></div>',
    '</div>',
    '<div class="caption" id="cap"></div>',
    '<div class="vignette"></div>',
    '<div class="grain" id="grain"></div>',
  ].join('');
  stage.appendChild(film);

  // film grain texture, generated on a canvas at runtime
  const g = document.createElement('canvas');
  g.width = 96;
  g.height = 96;
  const gc = g.getContext('2d');
  const img = gc.createImageData(96, 96);
  for (let i = 0; i < img.data.length; i += 4) {
    const v = 120 + Math.random() * 135;
    img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
    img.data[i + 3] = 255;
  }
  gc.putImageData(img, 0, 0);
  const grainEl = film.querySelector('#grain');
  grainEl.style.display = 'none'; // TEMP
  grainEl.style.backgroundImage = `url(${g.toDataURL()})`;
  grainEl.style.backgroundSize = '96px 96px';

  const tc = film.querySelector('#tc');
  const cap = film.querySelector('#cap');
  const rec = film.querySelector('#rec');
  let shown = null;

  const pad = (x, n) => String(Math.floor(x)).padStart(n, '0');

  return {
    update(t) {
      const frames = Math.floor((t % 1) * 24);
      tc.textContent = `00:${pad((t / 60) % 60, 2)}:${pad(t % 60, 2)}:${pad(frames, 2)}`;
      rec.style.opacity = (0.35 + 0.65 * (Math.sin(t * 4.2) > 0 ? 1 : 0.12)).toFixed(3);

      // captions loop on the same period as the camera plan
      const phase = ((t % cycleSeconds) + cycleSeconds) % cycleSeconds;
      let active = null;
      for (const c of CAPTIONS) {
        if (phase >= c.at && phase < c.at + c.dur) active = c;
      }
      if (active !== shown) {
        shown = active;
        cap.textContent = active ? active.text : '';
        cap.classList.toggle('on', !!active);
      }
    },
  };
}

export function showFallback(message) {
  const div = document.createElement('div');
  div.id = 'fallback';
  div.textContent = message;
  document.body.appendChild(div);
}
