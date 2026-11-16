// 촬영 중 사고 방지: 화면을 만지다가 앱이 "웹페이지처럼" 반응하는 일을 막는다.
// (확대, 길게 눌러 뜨는 메뉴, 글자 선택, 가로 회전, 뒤로 가기로 앱 종료)

export function installGuards() {
  // 길게 누르면 뜨는 메뉴 (복사 / 붙여넣기 / 이미지 저장 / 링크 미리보기)
  document.addEventListener('contextmenu', (e) => e.preventDefault());

  // 글자 선택과 끌어서 옮기기
  document.addEventListener('selectstart', (e) => e.preventDefault());
  document.addEventListener('dragstart', (e) => e.preventDefault());
  // 입력창: 길게 눌러 생긴 선택 영역은 바로 커서(문장 끝)로 되돌린다
  document.addEventListener('selectionchange', () => {
    const el = document.activeElement;
    if (!el || el.tagName !== 'TEXTAREA') return;
    const end = el.value.length;
    if (el.selectionStart !== end || el.selectionEnd !== end) {
      try { el.setSelectionRange(end, end); } catch { /* 무시 */ }
    }
  });

  // 확대: 두 손가락 벌리기, Ctrl+휠, (iOS) gesture 이벤트
  document.addEventListener('touchmove', (e) => { if (e.touches.length > 1) e.preventDefault(); }, { passive: false });
  document.addEventListener('wheel', (e) => { if (e.ctrlKey) e.preventDefault(); }, { passive: false });
  for (const type of ['gesturestart', 'gesturechange']) document.addEventListener(type, (e) => e.preventDefault());

  // 가로 회전: 설치한 앱은 manifest의 "orientation": "portrait"가 막아 준다. 가능한 환경에서는 한 번 더 잠근다.
  try { screen.orientation?.lock?.('portrait').catch(() => {}); } catch { /* 미지원: 무시 */ }

  // 설치하지 않고 브라우저로 열어 화면이 가로로 돌아간 경우: CSS가 앱을 세로 모양 그대로 눕혀 보여 준다.
  // 어느 쪽으로 눕혔는지 알려 줘서 글자가 거꾸로 서지 않게 한다.
  const markAngle = () => {
    const angle = screen.orientation?.angle ?? window.orientation ?? 0;
    document.documentElement.classList.toggle('land-flip', angle === 270 || angle === -90);
  };
  markAngle();
  window.addEventListener('orientationchange', markAngle);
  screen.orientation?.addEventListener?.('change', markAngle);

  // Android 뒤로 가기(버튼·화면 가장자리 쓸기)로 앱이 닫히지 않게: 기록을 하나 쌓아 두고, 뒤로 가면 다시 쌓는다.
  // 브라우저는 사용자가 화면을 만진 뒤에 쌓은 기록만 인정하므로 첫 탭에서 시작한다.
  let armed = false;
  const arm = () => {
    if (armed) return;
    armed = true;
    try { history.pushState({ mapture: 1 }, ''); } catch { /* 무시 */ }
  };
  document.addEventListener('pointerdown', arm, { once: true });
  window.addEventListener('popstate', () => {
    if (!armed) return;
    try { history.pushState({ mapture: 1 }, ''); } catch { /* 무시 */ }
  });
}
