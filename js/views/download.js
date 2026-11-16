// ① 다운로드 페이지: 앱 안의 가짜 스토어 화면 → Download → Open → 실행 애니메이션
import { mascotSVG, faceSVG } from '../mascot.js';
import { openOverlay, wait } from './overlay.js';

const DEFAULT_DOWNLOAD_SECONDS = 3; // 씬의 downloadSeconds로 바꿀 수 있다
const SWITCH_MS = 560;              // 스토어 카드가 밀려 나가고 맵쳐 카드가 들어와 커지는 시간 (css의 switch-out/in과 같게)
const SPLASH_MS = 1100;             // 마스코트 시작 화면

const ICON = {
  back: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1A1D1C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 6l-6 6 6 6"/></svg>',
  search: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1A1D1C" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4 4"/></svg>',
  more: '<svg width="20" height="20" viewBox="0 0 24 24" fill="#1A1D1C" aria-hidden="true"><circle cx="12" cy="5.5" r="1.7"/><circle cx="12" cy="12" r="1.7"/><circle cx="12" cy="18.5" r="1.7"/></svg>',
  star: '<svg width="12" height="12" viewBox="0 0 24 24" fill="#1A1D1C" aria-hidden="true"><path d="M12 3l2.7 5.8 6.3.8-4.6 4.3 1.2 6.3L12 17.1 6.4 20.2l1.2-6.3L3 9.6l6.3-.8z"/></svg>',
};

/**
 * @param {HTMLElement} root
 * @param {{seconds?: number, onMenuLongPress?: Function, onLaunched?: Function}} hooks
 *   seconds: 다운로드 진행 바가 차는 시간(초)
 *   onLaunched: 실행 애니메이션이 끝나 채팅 화면이 드러나는 순간
 */
export function showDownload(root, hooks = {}) {
  const ov = openOverlay(root, 'download', `
    <header class="ov-top">
      <button type="button" class="icon-btn" data-menu aria-label="Back">${ICON.back}</button>
      <span class="ov-top-spacer"></span>
      <button type="button" class="icon-btn plain" aria-label="Search">${ICON.search}</button>
      <button type="button" class="icon-btn plain" aria-label="More">${ICON.more}</button>
    </header>
    <main class="store">
      <div class="store-head">
        <div class="store-icon">${faceSVG(56)}</div>
        <div class="store-name">
          <h1>Mapture</h1>
          <p class="store-dev">Oracle Inc.</p>
          <p class="store-sub">Productivity · AI assistant</p>
        </div>
      </div>
      <div class="store-stats">
        <div><strong>4.8 ${ICON.star}</strong><span>2.1M reviews</span></div>
        <div><strong>50M+</strong><span>Downloads</span></div>
        <div><strong>12+</strong><span>Age rating</span></div>
      </div>
      <div class="store-action">
        <button type="button" class="store-btn" data-ref="btn">Download</button>
        <div class="store-progress" data-ref="progress" hidden>
          <div class="store-bar"><i data-ref="fill"></i></div>
          <span data-ref="pct">0%</span>
        </div>
      </div>
      <section class="store-about">
        <h2>About this app</h2>
        <p>Mapture predicts what happens next. It analyzes your behavioral patterns to answer any question about your future, with a probability you can act on.</p>
        <div class="store-tags"><span>Prediction</span><span>Long-term simulation</span><span>Progress Updates</span></div>
      </section>
      <div class="store-shots" aria-hidden="true">
        <div class="store-shot"><span>Probability of Success</span><b>71.13%</b></div>
        <div class="store-shot alt"><span>10-year outlook</span><b>See further.</b></div>
      </div>
    </main>`, hooks);

  const q = (ref) => ov.el.querySelector(`[data-ref=${ref}]`);
  const btn = q('btn');
  const downloadMs = (Number(hooks.seconds) > 0 ? Number(hooks.seconds) : DEFAULT_DOWNLOAD_SECONDS) * 1000;
  let state = 'idle'; // idle → downloading → ready → launching

  btn.addEventListener('click', () => {
    if (state === 'idle') {
      state = 'downloading';
      btn.disabled = true;
      btn.textContent = 'Downloading…';
      q('progress').hidden = false;
      const startedAt = performance.now();
      const tick = (now) => {
        if (!ov.alive()) return;
        const p = Math.min(1, (now - startedAt) / downloadMs);
        // 실제 다운로드처럼 처음엔 빠르고 끝에서 살짝 느려진다
        const eased = 1 - Math.pow(1 - p, 1.6);
        q('fill').style.transform = `scaleX(${eased})`;
        q('pct').textContent = `${Math.round(eased * 100)}%`;
        if (p < 1) { requestAnimationFrame(tick); return; }
        state = 'ready';
        q('progress').hidden = true;
        btn.disabled = false;
        btn.textContent = 'Open';
      };
      requestAnimationFrame(tick);
    } else if (state === 'ready') {
      state = 'launching';
      launch(root, hooks, ov);
    }
  });

  return ov;
}

/**
 * Open을 눌렀을 때의 전환 (iPhone에서 다른 앱이 열릴 때의 모션):
 *  1) 스토어 화면이 둥근 모서리 카드로 작아지면서 동시에 왼쪽으로 밀려 나간다
 *  2) 어두운 배경 위로 맵쳐 카드가 바로 뒤따라 오른쪽에서 들어와 가운데서 전체 화면으로 커진다 (1~2 합쳐 약 0.56초)
 *  3) 마스코트 시작 화면 (가운데서 커지며 등장, 고리 한 바퀴)
 *  4) 채팅 인사 화면으로 넘어간다
 */
async function launch(root, hooks, store) {
  const backdrop = document.createElement('div');
  backdrop.className = 'overlay switch-backdrop';
  root.appendChild(backdrop);
  store.el.classList.add('switch-out');
  const splash = openOverlay(root, 'launch', `<div class="launch-mascot">${mascotSVG(128)}</div>`);
  splash.el.classList.add('switch-in');

  await wait(SWITCH_MS);
  if (!splash.alive()) return; // 도중에 씬이 바뀜 (closeOverlays가 전부 치웠다)
  store.close();
  backdrop.remove();
  splash.el.classList.remove('switch-in');
  splash.el.classList.add('show-mascot');

  await wait(SPLASH_MS);
  if (!splash.alive()) return;
  hooks.onLaunched?.();
  splash.el.classList.add('leaving');
  await wait(260);
  splash.close();
}
