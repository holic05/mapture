// 길게 누르기(기본 600ms). 숨은 씬 메뉴를 여는 데 쓴다.
// 길게 누르기가 발동하면 손을 뗄 때 따라오는 click은 삼킨다(닫기·뒤로 가기가 같이 눌리지 않게).
export function onLongPress(el, fn, ms = 600) {
  let timer = 0;
  let fired = false;
  const cancel = () => { clearTimeout(timer); timer = 0; };
  el.addEventListener('pointerdown', () => {
    cancel();
    fired = false;
    timer = setTimeout(() => { timer = 0; fired = true; fn(); }, ms);
  });
  for (const type of ['pointerup', 'pointerleave', 'pointercancel']) el.addEventListener(type, cancel);
  el.addEventListener('click', (e) => {
    if (!fired) return;
    fired = false;
    e.preventDefault();
    e.stopImmediatePropagation();
  }, true);
  el.addEventListener('contextmenu', (e) => e.preventDefault());
}
