/** 현장에서 바로 알아볼 수 있도록 화면 전체에 크게 띄우는 오류 */
export function showFatal(title, detail = '') {
  let el = document.querySelector('.fatal');
  if (!el) {
    el = document.createElement('div');
    el.className = 'fatal';
    el.innerHTML = '<strong></strong><div></div>';
    document.body.appendChild(el);
  }
  el.querySelector('strong').textContent = title;
  el.querySelector('div').textContent = String(detail);
}
