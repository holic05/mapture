// 채팅 화면 위를 덮는 전체 화면(다운로드, 결제, 리포트)의 공통 틀.
// 채팅 화면은 아래에 그대로 살아 있어서, 닫으면 대화가 이어진다.
import { onLongPress } from '../longpress.js';

/**
 * @param {HTMLElement} root  #app
 * @param {string} name       CSS 클래스 (overlay-<name>)
 * @param {string} html
 * @param {{onMenuLongPress?: Function}} hooks  [data-menu] 요소를 길게 누르면 숨은 씬 메뉴
 */
export function openOverlay(root, name, html, hooks = {}) {
  const el = document.createElement('div');
  el.className = `overlay overlay-${name}`;
  el.innerHTML = html;
  root.appendChild(el);
  bindMenu(el, hooks);
  return {
    el,
    /** 화면이 아직 떠 있는지 (타이머 콜백에서 확인) */
    alive: () => el.isConnected,
    /** 내용을 통째로 바꾼다 (결제 → 완료처럼 같은 흐름의 다음 화면) */
    replace(nextHtml) { el.innerHTML = nextHtml; bindMenu(el, hooks); },
    close() { el.remove(); },
  };
}

function bindMenu(el, hooks) {
  el.querySelectorAll('[data-menu]').forEach((target) => onLongPress(target, () => hooks.onMenuLongPress?.()));
}

/** 열려 있는 전체 화면을 모두 닫는다 (씬 리셋 시) */
export function closeOverlays(root) {
  root.querySelectorAll('.overlay').forEach((el) => el.remove());
}

export const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
