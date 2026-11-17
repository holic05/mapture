// ① 다운로드 페이지: iPhone 앱 스토어의 앱 상세 화면 구조를 흉내 낸 가짜 스토어 → GET → 진행 링 → OPEN → 실행 애니메이션
// (레이아웃만 참고. 실제 스토어의 로고·이름·다른 앱 이미지는 쓰지 않는다)
import { mascotSVG, faceSVG } from '../mascot.js';
import { openOverlay, wait } from './overlay.js';

const DEFAULT_DOWNLOAD_SECONDS = 4; // 씬의 downloadSeconds로 바꿀 수 있다
const SWITCH_MS = 560;              // 스토어 카드가 밀려 나가고 맵쳐 카드가 들어와 커지는 시간 (css의 switch-out/in과 같게)
const SPLASH_HOLD_MS = 220;         // 전체 화면이 된 뒤 인사 화면으로 넘어가기 전 잠깐 머무는 시간
const RING_R = 13;
const RING_LEN = 2 * Math.PI * RING_R;

const ICON = {
  back: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1C1C1E" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>',
  share: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1C1C1E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 15V3M7 8l5-5 5 5M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"/></svg>',
  developer: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="12" cy="10" r="3"/><path d="M6 19c1.5-3 3.5-4 6-4s4.5 1 6 4"/></svg>',
  // 탭 바 아이콘: 단순한 도형으로 직접 그린 것
  today: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="3" width="14" height="18" rx="3"/><path d="M8.5 15h7M8.5 18h4" stroke-linecap="round"/></svg>',
  games: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 8h10a4 4 0 0 1 4 4v2a3 3 0 0 1-5.4 1.8L14.5 14h-5l-1.1 1.8A3 3 0 0 1 3 14v-2a4 4 0 0 1 4-4z"/><path d="M8 11v3M6.5 12.5h3"/></svg>',
  apps: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l9 4.5-9 4.5-9-4.5z"/><path d="M3 12l9 4.5 9-4.5M3 16.5L12 21l9-4.5" stroke-linecap="round"/></svg>',
  search: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L20 20"/></svg>',
};

/** Events 카드의 마스코트 (청록 배경 위의 밝은 얼굴) */
const EVENT_MASCOT = `<svg class="store-event-mascot" width="170" height="170" viewBox="0 0 120 120" aria-hidden="true">
  <ellipse cx="60" cy="64" rx="56" ry="15" fill="none" stroke="#7FCFC1" stroke-opacity="0.6" stroke-width="3" transform="rotate(-14 60 64)"/>
  <circle cx="60" cy="60" r="36" fill="#EAF6F3"/><circle cx="48" cy="58" r="5" fill="#0F7B6C"/><circle cx="72" cy="58" r="5" fill="#0F7B6C"/>
  <path d="M48 70q12 10 24 0" fill="none" stroke="#0F7B6C" stroke-width="4" stroke-linecap="round"/>
  <path d="M7 79Q60 92 113 49" fill="none" stroke="#7FCFC1" stroke-width="3" stroke-linecap="round"/></svg>`;

/** Preview 스크린샷 한 장: 홍보 문구 + 폰 틀 안의 실제 앱 화면 (img/preview-*.jpg, tools/make-previews.py로 다시 만듦) */
const shot = (title, n) => `<div class="store-shot"><span>${title}</span><div class="store-shot-phone">`
  + `<img src="img/preview-${n}.jpg" alt="" width="585" height="1149" draggable="false" decoding="async"></div></div>`;

// 스토어 문구 초안 [TODO: 작가 확인] — 극 중 세계관(Mapture 6 출시, 미래 예측 앱). docs/content-drafts.md에 같은 목록.
const REVIEWS = [
  { title: 'Scarily accurate', stars: 5, who: 'nightowl_jin', when: '2d ago',
    text: 'Asked if my bus would be late. 96.8%. I left ten minutes early and made my interview. Mapture 6 hasn’t been wrong once.' },
  { title: 'Worth every token', stars: 5, who: 'minseo.p', when: '5d ago',
    text: 'Premium raised my probability of success by 4.2 points in one semester. I don’t make a single decision without it anymore.' },
  { title: 'Stopped overthinking', stars: 4, who: 'hyun_w', when: '1w ago',
    text: 'I used to agonize over every choice. Now I just ask. One star off because it told me not to adopt a cat.' },
];
const DESCRIPTION = [
  'Mapture 6 is here — our most accurate prediction engine yet.',
  'Ask anything about your future and get an answer you can act on, with a probability attached. Mapture analyzes your behavioral patterns, contacts, schedule and academic records to tell you what happens next, and what to do about it.',
  '• Instant predictions, by voice or text<br>• Long-term simulation up to 10 years ahead<br>• Real-time Progress Updates on your probability of success',
];
const RATING_BARS = [92, 5, 1.5, 0.5, 1]; // ★5 → ★1 비율(%)

const stars = (n) => '★'.repeat(n) + '<i>' + '★'.repeat(5 - n) + '</i>';

/** GET 버튼과 진행 링. 본문(앱 정보 옆)과 상단 바(스크롤해서 본문 버튼이 가려졌을 때) 두 곳에 같은 것이 있다 */
const action = (where) => `
  <button type="button" class="${where === 'mini' ? 'store-mini-btn' : 'store-btn'}" data-act="btn">GET</button>
  <button type="button" class="store-ring" data-act="ring" aria-label="Stop download" hidden>
    <svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true">
      <circle cx="15" cy="15" r="${RING_R}" fill="none" stroke="#D6DBE1" stroke-width="2.5"/>
      <circle data-act="arc" cx="15" cy="15" r="${RING_R}" fill="none" stroke="#0A7AFF" stroke-width="2.5" stroke-linecap="round"
              stroke-dasharray="${RING_LEN.toFixed(2)}" stroke-dashoffset="${RING_LEN.toFixed(2)}" transform="rotate(-90 15 15)"/>
      <rect x="11" y="11" width="8" height="8" rx="1.5" fill="#0A7AFF"/>
    </svg>
  </button>`;

/**
 * @param {HTMLElement} root
 * @param {{seconds?: number, onMenuLongPress?: Function, onLaunched?: Function}} hooks
 *   seconds: 진행 링이 다 차는 시간(초)
 *   onLaunched: 실행 애니메이션이 끝나 채팅 화면이 드러나는 순간
 *
 * 화면은 세로로 스크롤되고(에밀리가 훑어보며 망설이는 장면), 정보 줄과 Preview 줄은 옆으로 넘길 수 있다.
 * GET(OPEN) 말고는 눌러도 반응하지 않는다. 뒤로 가기 버튼은 길게 누르면 숨은 씬 메뉴.
 * 본문 GET이 위로 스크롤되어 사라지면 상단 바 가운데에 작은 아이콘, 오른쪽에 작은 GET이 나타난다(같은 동작).
 */
export function showDownload(root, hooks = {}) {
  const ov = openOverlay(root, 'download', `
    <header class="store-top" data-ref="top">
      <button type="button" class="store-round" data-menu aria-label="Back">${ICON.back}</button>
      <div class="store-mini-icon" aria-hidden="true">${faceSVG(30)}</div>
      <div class="store-top-right">
        <div class="store-mini" data-ref="mini">${action('mini')}</div>
        <button type="button" class="store-round" aria-label="Share">${ICON.share}</button>
      </div>
    </header>
    <main class="store" data-ref="store">
      <div class="store-head">
        <div class="store-icon">${faceSVG(84)}</div>
        <div class="store-name">
          <h1>Mapture</h1>
          <p class="store-dev">Oracle Inc.</p>
          <div class="store-action" data-ref="main">
            ${action('main')}
            <span class="store-iap">In-App<br>Purchases</span>
          </div>
        </div>
      </div>
      <div class="store-info-wrap">
        <div class="store-info hscroll">
          <div><span class="k">7.2M Ratings</span><b>4.9</b><span>★★★★★</span></div>
          <div><span class="k">Age</span><b>12+</b><span>Years Old</span></div>
          <div><span class="k">Chart</span><b>#1</b><span>Productivity</span></div>
          <div><span class="k">Developer</span><b>${ICON.developer}</b><span>Oracle Inc.</span></div>
          <div><span class="k">Language</span><b>EN</b><span>+ 41 More</span></div>
          <div><span class="k">Size</span><b>212.4</b><span>MB</span></div>
        </div>
      </div>
      <section class="store-sec">
        <h2>Events</h2>
        <div class="store-event">
          ${EVENT_MASCOT}
          <span class="store-badge">NOW AVAILABLE</span>
          <div class="store-event-text">
            <span class="store-event-kicker">MAJOR UPDATE</span>
            <b>Meet Mapture 6</b>
            <span>Our most accurate predictions yet</span>
          </div>
        </div>
      </section>
      <section class="store-sec">
        <h2>Preview</h2>
        <div class="store-shots hscroll" aria-hidden="true">
          ${shot('Know what<br>happens next', 1)}
          ${shot('Every decision,<br>analyzed', 2)}
          ${shot('Every step,<br>predicted', 3)}
        </div>
      </section>
      <section class="store-sec">
        <h2>Ratings &amp; Reviews</h2>
        <div class="store-rating">
          <div class="store-rating-big"><b>4.9</b><span>out of 5</span></div>
          <div class="store-rating-bars">
            ${RATING_BARS.map((pct, i) => `<div><span>${'★'.repeat(5 - i)}</span><i><u style="width:${pct}%"></u></i></div>`).join('')}
            <small>7.2M Ratings</small>
          </div>
        </div>
        <div class="store-reviews hscroll">
          ${REVIEWS.map((r) => `<article class="store-review">
            <div class="store-review-top"><b>${r.title}</b><span>${r.when}</span></div>
            <div class="store-review-meta"><span class="stars">${stars(r.stars)}</span><span>${r.who}</span></div>
            <p>${r.text}</p></article>`).join('')}
        </div>
      </section>
      <section class="store-sec store-desc">
        ${DESCRIPTION.map((t) => `<p>${t}</p>`).join('')}
        <div class="store-dev-row"><div><span>Developer</span><b>Oracle Inc.</b></div></div>
      </section>
    </main>
    <nav class="store-tabs" aria-hidden="true">
      <div>${ICON.today}<span>Today</span></div>
      <div>${ICON.games}<span>Games</span></div>
      <div class="on">${ICON.apps}<span>Apps</span></div>
      <div>${ICON.search}<span>Search</span></div>
    </nav>`, hooks);

  const q = (ref) => ov.el.querySelector(`[data-ref=${ref}]`);
  const sets = ['main', 'mini'].map((where) => {
    const box = q(where);
    const get = (name) => box.querySelector(`[data-act=${name}]`);
    return { btn: get('btn'), ring: get('ring'), arc: get('arc') };
  });
  const store = q('store');
  const top = q('top');
  const downloadMs = (Number(hooks.seconds) > 0 ? Number(hooks.seconds) : DEFAULT_DOWNLOAD_SECONDS) * 1000;
  let state = 'idle'; // idle → downloading → ready → launching

  // 본문 GET 줄이 상단 바 밑으로 사라지면 상단 바에 작은 아이콘과 GET을 보인다
  const onScroll = () => {
    const limit = q('main').getBoundingClientRect().bottom - top.getBoundingClientRect().bottom;
    top.classList.toggle('scrolled', limit < 0);
    top.classList.toggle('shadow', store.scrollTop > 2);
  };
  store.addEventListener('scroll', onScroll, { passive: true });

  const show = (fn) => sets.forEach(fn);

  const tap = () => {
    if (state === 'idle') {
      // GET → 버튼 자리에 원형 진행 링(가운데 정지 사각형). 퍼센트 숫자는 없다.
      state = 'downloading';
      show((x) => { x.btn.hidden = true; x.ring.hidden = false; });
      const startedAt = performance.now();
      const tick = (now) => {
        if (!ov.alive()) return;
        const p = Math.min(1, (now - startedAt) / downloadMs);
        // 처음 잠깐은 준비하듯 천천히, 그다음 꾸준히 차고 끝에서 살짝 느려진다
        const eased = p < 0.12 ? p * 0.25 : 0.03 + (1 - Math.pow(1 - (p - 0.12) / 0.88, 1.5)) * 0.97;
        show((x) => x.arc.setAttribute('stroke-dashoffset', (RING_LEN * (1 - eased)).toFixed(2)));
        if (p < 1) { requestAnimationFrame(tick); return; }
        state = 'ready';
        show((x) => { x.ring.hidden = true; x.btn.hidden = false; x.btn.textContent = 'OPEN'; });
      };
      requestAnimationFrame(tick);
    } else if (state === 'ready') {
      state = 'launching';
      launch(root, hooks, ov);
    }
  };
  show((x) => x.btn.addEventListener('click', tap));

  return ov;
}

/**
 * Open을 눌렀을 때의 전환 (readme/화면전환_예시.mp4: iPhone에서 다른 앱이 열릴 때의 모션):
 *  1) 스토어 화면이 둥근 모서리 카드로 작아지면서 동시에 왼쪽으로 밀려 나간다
 *  2) 어두운 배경 위로 맵쳐 카드가 바로 뒤따라 오른쪽에서 들어와 가운데서 전체 화면으로 커진다 (1~2 합쳐 약 0.56초)
 *     카드에는 처음부터 마스코트 시작 화면이 보인다 (참고 영상에서 카드 안에 앱 화면이 이미 보이는 것처럼)
 *  3) 전체 화면이 되면 곧바로 인사 화면으로 넘어간다. 마스코트는 인사 화면의 마스코트와 같은 자리에 있어서
 *     마스코트는 그대로 있고 인사말·상단 바·입력창이 나타나는 것처럼 보인다
 */
async function launch(root, hooks, store) {
  const backdrop = document.createElement('div');
  backdrop.className = 'overlay switch-backdrop';
  root.appendChild(backdrop);
  store.el.classList.add('switch-out');
  const splash = openOverlay(root, 'launch', SPLASH_HTML);
  splash.el.classList.add('switch-in');

  await wait(SWITCH_MS);
  if (!splash.alive()) return; // 도중에 씬이 바뀜 (closeOverlays가 전부 치웠다)
  store.close();
  backdrop.remove();
  splash.el.classList.remove('switch-in');

  await wait(SPLASH_HOLD_MS);
  if (!splash.alive()) return;
  hooks.onLaunched?.();
  splash.el.classList.add('leaving');
  await wait(260);
  splash.close();
}

// 시작 화면: 채팅 인사 화면과 똑같은 뼈대(같은 CSS 클래스)에 마스코트만 보이게 한 것.
// 뼈대가 같아서 화면 크기가 달라도 마스코트가 인사 화면의 마스코트와 정확히 같은 자리에 온다.
const SPLASH_HTML = `
  <div class="topbar"></div>
  <div class="chat-main">
    <div class="empty">
      <div class="empty-hero">
        <div class="launch-mascot">${mascotSVG(128)}</div>
        <h1 class="ghost">Hello, user!<br>How can I help you today?</h1>
      </div>
      <p class="empty-foot ghost">Oracle Inc. · Mapture 6</p>
    </div>
  </div>
  <div class="composer-wrap ghost"><div class="composer"><div class="round"></div></div></div>`;
