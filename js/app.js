// 진입점: scenes.json 로딩, 씬 선택, 키보드 대응, Wake Lock, 서비스 워커 등록
import { showFatal } from './fatal.js';
import { installGuards } from './guard.js';
import { Engine } from './engine.js';
import { createChat } from './views/chat.js';
import { openSceneMenu } from './views/sceneMenu.js';
import { closeOverlays } from './views/overlay.js';
import { showDownload } from './views/download.js';
import { showPaywall } from './views/paywall.js';
import { showReport } from './views/report.js';

const STORAGE_KEY = 'mapture.scene';
const app = document.getElementById('app');

installGuards();

window.addEventListener('error', (e) => {
  if (/ResizeObserver/.test(e.message || '')) return; // 브라우저의 무해한 경고
  showFatal('App error', `${e.message}\n${(e.filename || '').split('/').pop()}:${e.lineno || ''}`);
});
window.addEventListener('unhandledrejection', (e) => showFatal('App error', e.reason?.message || e.reason));

// ===== 화면 높이 = 실제로 보이는 영역 (키보드 대응) =====
// 키보드가 올라오면 visualViewport.height가 줄어든다. 그 값을 --vvh로 넘겨 앱 전체 높이를 맞추면
// 입력창이 항상 키보드 바로 위에 붙고, 메시지 목록만 줄어든다.
// (index.html의 interactive-widget=resizes-content와 같은 효과이며, 그 설정을 무시하는 브라우저를 위한 보강)
(function trackViewport() {
  const vv = window.visualViewport;
  if (!vv) return;
  const root = document.documentElement;
  let tallest = 0;
  const update = () => {
    tallest = Math.max(tallest, vv.height);
    root.style.setProperty('--vvh', `${vv.height}px`);
    root.classList.toggle('kb-open', vv.height < tallest - 120);
    if (window.scrollY) window.scrollTo(0, 0); // 브라우저가 페이지 자체를 밀어 올리는 것 방지
  };
  vv.addEventListener('resize', update);
  vv.addEventListener('scroll', update);
  window.addEventListener('orientationchange', () => { tallest = 0; });
  update();
})();

// ===== Wake Lock: 촬영 중 화면이 저절로 꺼지지 않게 =====
// 사용자 동작이 있어야 요청할 수 있어서 첫 탭에서 요청한다. 앱이 가려지면 자동 해제되므로 다시 보일 때 재요청.
(function keepAwake() {
  if (!('wakeLock' in navigator)) return; // 미지원이면 조용히 무시
  let lock = null;
  let wanted = false;
  const request = async () => {
    if (!wanted || document.visibilityState !== 'visible' || lock) return;
    try {
      lock = await navigator.wakeLock.request('screen');
      lock.addEventListener('release', () => { lock = null; });
    } catch { /* 배터리 절약 모드 등: 무시 */ }
  };
  document.addEventListener('pointerdown', () => { wanted = true; request(); }, { once: true });
  document.addEventListener('visibilitychange', request);
})();

// ===== scenes.json =====
async function loadScenes() {
  let text;
  try {
    const res = await fetch('scenes.json', { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    text = await res.text();
  } catch (err) {
    showFatal('scenes.json could not be loaded', err.message || err);
    return null;
  }

  let data;
  try {
    data = JSON.parse(text);
  } catch (err) {
    showFatal('scenes.json has a syntax error', describeJsonError(err, text));
    return null;
  }

  const problems = validate(data);
  if (problems.length) {
    showFatal('scenes.json has a problem', problems.join('\n'));
    return null;
  }
  return data;
}

/** JSON 오류 위치를 줄 번호와 그 줄 내용으로 보여 준다 */
function describeJsonError(err, text) {
  const msg = String(err.message || err);
  const m = /position (\d+)/.exec(msg);
  if (!m) return msg;
  const pos = Number(m[1]);
  const before = text.slice(0, pos).split('\n');
  const lineNo = before.length;
  const line = text.split('\n')[lineNo - 1] || '';
  return `${msg}\n\nLine ${lineNo}:\n${line.trim().slice(0, 200)}`;
}

function validate(data) {
  const out = [];
  if (!data || !Array.isArray(data.scenes) || !data.scenes.length) return ['"scenes" must be a non-empty array.'];
  const seen = new Set();
  data.scenes.forEach((scene, si) => {
    const name = scene?.id || `scenes[${si}]`;
    if (!scene?.id) out.push(`scenes[${si}]: missing "id"`);
    else if (seen.has(scene.id)) out.push(`${name}: duplicate id`);
    seen.add(scene?.id);
    if (scene?.after != null && !data.scenes.some((x) => x?.id === scene.after)) out.push(`${name}: "after" points to unknown scene "${scene.after}"`);
    if (scene?.gap != null && !/^\s*\d+(\.\d+)?\s*[mhdwy]\s*$/.test(String(scene.gap))) out.push(`${name}: "gap" must look like "14h", "2d" or "2y"`);
    if (scene?.notice != null) {
      const n = scene.notice;
      if (typeof n !== 'object' || n.value == null) out.push(`${name}.notice: needs "value"`);
      else if (n.size != null && !['compact', 'large'].includes(n.size)) out.push(`${name}.notice.size: must be "compact" or "large"`);
      else if (n.appear != null && !['start', 'drop'].includes(n.appear)) out.push(`${name}.notice.appear: must be "start" or "drop"`);
    }
    for (const key of ['history', 'steps']) {
      const steps = scene?.[key];
      if (steps == null) continue;
      if (!Array.isArray(steps)) { out.push(`${name}.${key}: must be an array`); continue; }
      steps.forEach((step, i) => {
        const where = `${name}.${key}[${i}]`;
        if (!['divider', 'user', 'mapture'].includes(step?.type)) out.push(`${where}: unknown type "${step?.type}"`);
        else if (step.type === 'user') {
          if (typeof step.text !== 'string' || !step.text) out.push(`${where}: user step needs "text"`);
          if (!['typing', 'voice'].includes(step.input)) out.push(`${where}: "input" must be "typing" or "voice"`);
        } else if (step.type === 'mapture' && !step.headline && !step.body && !step.list && !step.compare) {
          out.push(`${where}: mapture step needs "headline", "body", "list" or "compare"`);
        } else if (step.type === 'mapture' && step.compare && !(Array.isArray(step.compare.items) && step.compare.items.length === 2)) {
          out.push(`${where}: "compare" needs exactly two "items"`);
        }
      });
    }
  });
  return out;
}

// ===== 씬 선택 =====
function remembered() {
  try { return localStorage.getItem(STORAGE_KEY); } catch { return null; }
}
function remember(id) {
  try { localStorage.setItem(STORAGE_KEY, id); } catch { /* 시크릿 모드 등: 무시 */ }
}

async function main() {
  let scenes = [];
  let current = null;

  const openMenu = () => {
    if (scenes.length) openSceneMenu(app, scenes, current?.id, startScene);
  };

  /** 결제 화면. 완료되면 플랜 표시가 Premium으로 바뀌고, 닫으면 아래의 채팅 화면이 그대로 이어진다 */
  const openPaywall = () => showPaywall(app, {
    onMenuLongPress: openMenu,
    onPaid: () => chat.setPlan('Premium'),
  });

  const chat = createChat(app, {
    onMenuLongPress: openMenu,
    onAction: (action) => { if (action === 'paywall') openPaywall(); },
    onReport: (step, shownAt) => showReport(app, step.report, {
      sceneStart: engine.sceneStart, shownAt, onMenuLongPress: openMenu,
    }),
  });
  const engine = new Engine(chat);

  /** 씬을 시작 상태로 완전히 리셋한다. scene.start에 따라 첫 화면이 달라진다 */
  function startScene(scene) {
    current = scene;
    remember(scene.id);
    closeOverlays(app);
    engine.stop();

    if (scene.start === 'download') {
      // 스토어 화면 아래에 빈 채팅 화면을 준비해 두고, 실행 애니메이션이 끝날 때 씬을 시작한다
      chat.reset(scene);
      showDownload(app, {
        seconds: scene.downloadSeconds,
        onMenuLongPress: openMenu,
        onLaunched: () => engine.start(scene),
      });
      return;
    }
    engine.start(scene);
    if (scene.start === 'paywall') openPaywall();
  }

  const data = await loadScenes();
  if (!data) return;
  scenes = data.scenes;
  engine.scenes = scenes;

  // 우선순위: URL ?scene=S08 → 마지막으로 고른 씬 → 첫 번째 씬
  const params = new URLSearchParams(location.search);
  const wanted = params.get('scene');
  // 개발용: ?solo=1 이면 앞 씬 대화를 이어 붙이지 않고 그 씬만 연다
  engine.chainScenes = !params.has('solo');
  const find = (id) => id && scenes.find((s) => s.id.toLowerCase() === id.toLowerCase());
  if (wanted && !find(wanted)) {
    showFatal('Unknown scene', `?scene=${wanted}\n\nAvailable: ${scenes.map((s) => s.id).join(', ')}`);
    return;
  }
  startScene(find(wanted) || find(remembered()) || scenes[0]);
}

main();

// ===== PWA: 서비스 워커 등록 =====
// 서비스 워커(sw.js)는 브라우저 백그라운드에서 동작하며 앱 파일을 캐시해 오프라인에서도 열리게 한다.
// HTTPS(또는 localhost)에서만 동작한다.
if ('serviceWorker' in navigator) {
  // 새 버전(sw.js의 CACHE_VERSION 변경)이 설치되어 제어권을 넘겨받으면 한 번 새로고침해 새 파일을 적용
  const hadController = !!navigator.serviceWorker.controller;
  let reloaded = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (!hadController || reloaded) return; // 첫 설치 때는 새로고침 불필요
    reloaded = true;
    location.reload();
  });

  window.addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js').catch((err) => {
      console.warn('Service worker registration failed:', err);
    });
  });
}
