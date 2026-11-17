// Mapture 서비스 워커
// - 앱 파일: cache-first (한 번 열면 비행기 모드에서도 실행)
// - scenes.json: network-first (온라인이면 항상 최신, 오프라인이면 마지막으로 받은 것)
//
// ★ 앱 파일(html/css/js/아이콘)을 고쳐서 배포할 때는 CACHE_VERSION을 올릴 것.
//   scenes.json만 고쳤다면 올릴 필요 없음.

const CACHE_VERSION = 'v11';
const CACHE_NAME = `mapture-${CACHE_VERSION}`;

// 설치 시 미리 받아 둘 파일 (모두 상대 경로 → GitHub Pages 하위 경로에서도 동작)
const APP_FILES = [
  './',
  './index.html',
  './css/app.css',
  './js/app.js',
  './js/engine.js',
  './js/fatal.js',
  './js/guard.js',
  './js/longpress.js',
  './js/mascot.js',
  './js/time.js',
  './js/views/chat.js',
  './js/views/download.js',
  './js/views/overlay.js',
  './js/views/paywall.js',
  './js/views/report.js',
  './js/views/sceneMenu.js',
  './manifest.json',
  './scenes.json', // 첫 실행 직후 오프라인에서도 열리도록 미리 받아 둠 (이후에는 network-first로 갱신)
  './icons/icon-192.png',
  './icons/icon-512.png',
];

const FONT_HOSTS = ['fonts.googleapis.com', 'fonts.gstatic.com'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(APP_FILES.map((u) => new Request(u, { cache: 'reload' }))))
      .then(() => self.skipWaiting()) // 대기 없이 바로 새 버전 활성화
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((k) => k.startsWith('mapture-') && k !== CACHE_NAME).map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // scenes.json → network-first
  if (url.origin === self.location.origin && url.pathname.endsWith('/scenes.json')) {
    event.respondWith(networkFirst(req));
    return;
  }

  // 앱 파일 + Google Fonts → cache-first
  if (url.origin === self.location.origin || FONT_HOSTS.includes(url.hostname)) {
    event.respondWith(cacheFirst(req));
  }
});

async function networkFirst(req) {
  const cache = await caches.open(CACHE_NAME);
  try {
    const res = await fetch(req, { cache: 'no-store' });
    if (res.ok) cache.put(req, res.clone());
    return res;
  } catch (err) {
    const cached = await cache.match(req, { ignoreSearch: true });
    if (cached) return cached;
    throw err;
  }
}

async function cacheFirst(req) {
  const cache = await caches.open(CACHE_NAME);
  // 페이지 이동(?scene=S08 같은 쿼리 포함)은 index.html 캐시로 응답
  const isNav = req.mode === 'navigate';
  const cached = await cache.match(req, { ignoreSearch: isNav })
    || (isNav ? await cache.match('./index.html') : undefined);
  if (cached) return cached;

  const res = await fetch(req);
  if (res.ok || res.type === 'opaque') cache.put(req, res.clone());
  return res;
}
