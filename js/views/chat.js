// 채팅 화면: 상단 바, 메시지 목록, 입력창(고스트 타이핑), 음성 모드
import { mascotSVG } from '../mascot.js';
import { isProgressUpdate } from '../engine.js';
import { onLongPress } from '../longpress.js';

const MIC_PATH = '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>';
const ICON = {
  menu: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1A1D1C" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M5 9h14M5 15h14"/></svg>',
  chevron: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#5B6360" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>',
  plus: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1A1D1C" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>',
  mic: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1A1D1C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${MIC_PATH}</svg>`,
  micBig: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1A1D1C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${MIC_PATH}</svg>`,
  micSmall: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" aria-hidden="true">${MIC_PATH}</svg>`,
  close: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1A1D1C" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  send: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M6 11l6-6 6 6"/></svg>',
  // 로딩용 작은 마스코트: 얼굴 뒤에서 궤도 고리가 돈다
  spinner: `<svg class="spin-mascot" width="28" height="28" viewBox="0 0 120 120" aria-hidden="true">
    <g class="spin-ring"><ellipse cx="60" cy="60" rx="56" ry="22" fill="none" stroke="#0F7B6C" stroke-opacity="0.45" stroke-width="7"/></g>
    <circle cx="60" cy="60" r="36" fill="#0F7B6C"/>
    <circle cx="48" cy="58" r="6" fill="#FFFFFF"/><circle cx="72" cy="58" r="6" fill="#FFFFFF"/>
    <path d="M47 71q13 11 26 0" fill="none" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round"/></svg>`,
};

const DEFAULT_TYPING_SPEED = 18; // 초당 글자 수
const INPUT_MAX_HEIGHT = 132;

function h(tag, className, text) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (text != null) el.textContent = text;
  return el;
}

/**
 * @param {HTMLElement} root
 * @param {{onMenuLongPress?: Function, onAction?: Function, onReport?: Function}} hooks
 */
export function createChat(root, hooks = {}) {
  root.innerHTML = `
  <div class="screen chat" data-ref="screen">
    <header class="topbar">
      <button type="button" class="icon-btn" data-ref="menu" aria-label="Menu">${ICON.menu}</button>
      <button type="button" class="title-btn">Mapture <span class="plan" data-ref="plan"></span>${ICON.chevron}</button>
      <button type="button" class="icon-btn profile-btn" data-ref="profile" aria-label="Profile"></button>
    </header>

    <main class="chat-main">
      <div class="empty" data-ref="empty">
        <div class="empty-hero">
          ${mascotSVG(128)}
          <h1>Hello, user!<br>How can I help you today?</h1>
        </div>
        <p class="empty-foot">Oracle Inc. · Mapture 6</p>
      </div>
      <div class="scroller" data-ref="scroller" hidden>
        <div class="messages" data-ref="messages"></div>
      </div>
    </main>

    <div class="composer-wrap">
      <div class="composer">
        <button type="button" class="round attach" aria-label="Attach">${ICON.plus}</button>
        <label for="ask" class="sr-only">Ask Mapture</label>
        <textarea id="ask" data-ref="input" rows="1" placeholder="Ask Mapture"
               autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" enterkeyhint="send"></textarea>
        <button type="button" class="round mic" data-ref="mic" aria-label="Voice input">${ICON.mic}</button>
        <button type="button" class="round send" data-ref="send" aria-label="Send">${ICON.send}</button>
      </div>
    </div>

    <div class="voice-panel" data-ref="voice" hidden>
      <p class="voice-status" data-ref="voiceStatus">Listening…</p>
      <div class="voice-row">
        <button type="button" class="voice-btn" aria-label="Microphone">${ICON.micBig}</button>
        <div class="voice-pill" aria-hidden="true"></div>
        <button type="button" class="voice-btn voice-x" data-ref="voiceX" aria-label="End voice mode">${ICON.close}</button>
      </div>
    </div>
  </div>`;

  const refs = {};
  root.querySelectorAll('[data-ref]').forEach((el) => { refs[el.dataset.ref] = el; });
  const { screen, scroller, messages, input } = refs;

  let scene = null;
  let loadingEl = null;
  let voiceOn = false;
  let autoTimer = 0; // 음성 질문 자동 올리기(autoSubmit) 타이머
  /** 지금 기다리는 사용자 단계. { step, n, resolve } 또는 null */
  let pending = null;

  // ---------- 스크롤 ----------
  function scrollToBottom() { scroller.scrollTop = scroller.scrollHeight; }
  // 키보드가 열려 목록이 줄어들거나, 글자가 늘어 말풍선이 커질 때마다 맨 아래 유지
  if ('ResizeObserver' in window) {
    const ro = new ResizeObserver(scrollToBottom);
    ro.observe(scroller);
    ro.observe(messages);
  }

  function showMessages() {
    if (!scroller.hidden) return;
    refs.empty.hidden = true;
    scroller.hidden = false;
  }

  function append(el, live) {
    showMessages();
    el.classList.add('msg');
    if (live) el.classList.add('live');
    messages.appendChild(el);
    scrollToBottom();
    return el;
  }

  // ---------- 씬 리셋 ----------
  function reset(nextScene) {
    scene = nextScene;
    pending = null;
    loadingEl = null;
    resetKeyState();
    setVoice(false);
    messages.textContent = '';
    scroller.hidden = true;
    refs.empty.hidden = false;
    refs.plan.textContent = scene.plan || 'Free';
    refs.profile.textContent = scene.profile || 'E';
    root.style.setProperty('--text-scale', String(scene.textScale || 1));
    input.blur();
    renderInput();
  }

  // ---------- 메시지 ----------
  function addDivider(text, { live = false } = {}) {
    if (!text) return;
    append(h('p', 'time-divider', text), live);
  }

  function addUser(text, { voice = false, live = false } = {}) {
    const el = h('div', 'bubble-user');
    if (voice) {
      el.classList.add('voice');
      el.innerHTML = ICON.micSmall;
      el.appendChild(h('span', '', text));
    } else {
      el.textContent = text;
    }
    append(el, live);
  }

  function showLoading({ text, seconds, progressBar }) {
    hideLoading();
    const el = h('div', 'bubble-loading');
    const row = h('div', 'loading-row');
    row.innerHTML = ICON.spinner;
    row.appendChild(h('span', '', text));
    el.appendChild(row);
    if (progressBar) {
      el.classList.add('with-bar');
      const bar = h('div', 'loading-bar');
      const fill = h('i');
      fill.style.animationDuration = `${seconds}s`;
      bar.appendChild(fill);
      el.appendChild(bar);
    }
    loadingEl = append(el, true);
  }

  function hideLoading() {
    if (loadingEl) loadingEl.remove();
    loadingEl = null;
  }

  function headlineEl(hl, progress) {
    const wrap = h('div', 'headline' + (hl.size === 'huge' ? ' huge' : ''));
    const label = hl.label || (progress ? 'Progress Update' : '');
    if (label) wrap.appendChild(h('span', 'headline-label', label));
    const row = h('div', 'headline-row');
    row.appendChild(h('span', 'headline-value', hl.value ?? ''));
    if (typeof hl.up === 'boolean' || hl.delta) {
      const up = hl.up === true;
      row.appendChild(h('span', 'headline-delta ' + (up ? 'up' : 'down'), `${up ? '▲' : '▼'}${hl.delta ? ' ' + hl.delta : ''}`));
    }
    wrap.appendChild(row);
    return wrap;
  }

  /** 한 글자씩 출력. 끝까지 쓰면 true, 씬이 리셋되어 중단되면 false */
  function typeText(node, text, cps, ctl) {
    return new Promise((resolve) => {
      const textNode = document.createTextNode('');
      node.appendChild(textNode);
      const startedAt = performance.now();
      let shown = 0;
      const frame = (now) => {
        if (!ctl.alive()) return resolve(false);
        const n = ctl.skip ? text.length : Math.min(text.length, Math.floor(((now - startedAt) / 1000) * cps) + 1);
        if (n !== shown) {
          shown = n;
          textNode.data = text.slice(0, n);
          scrollToBottom();
        }
        if (n >= text.length) return resolve(true);
        requestAnimationFrame(frame);
      };
      requestAnimationFrame(frame);
    });
  }

  /**
   * 맵쳐 말풍선을 만든다.
   * ctl.skip이 처음부터 true면(history) await 없이 한 번에 전부 그린다.
   * 순서: headline(한 번에) → 구분선 → body·list(한 글자씩) → disclaimer·button·report(한 번에)
   */
  async function buildMapture(step, ctl, live) {
    const progress = isProgressUpdate(step);
    const el = h('div', 'bubble-mapture' + (progress ? ' progress' : ''));
    el.addEventListener('click', () => { ctl.skip = true; }); // 출력 중 탭 → 즉시 완성
    const cps = step.typingSpeed > 0 ? step.typingSpeed : DEFAULT_TYPING_SPEED;
    const shownAt = live ? new Date() : null; // 리포트의 "질문 시각"에 쓰인다

    // 글자를 넣는다. skip이면 동기, 아니면 타이핑(Promise)
    const put = (node, text) => {
      if (ctl.skip) { node.textContent = text; return true; }
      return typeText(node, text, cps, ctl);
    };

    if (step.headline) {
      el.appendChild(headlineEl(step.headline, progress));
      if (!progress) el.appendChild(h('div', 'rule'));
    }
    append(el, live);

    const paragraphs = [].concat(step.body || []).flatMap((b) => String(b).split(/\n\s*\n/)).filter(Boolean);
    for (const para of paragraphs) {
      const p = el.appendChild(h('p', 'body-text'));
      const r = put(p, para);
      if (r !== true && !(await r)) return;
    }

    for (const list of [].concat(step.list || [])) {
      if (list.title) {
        const t = el.appendChild(h('p', 'list-title'));
        const r = put(t, list.title);
        if (r !== true && !(await r)) return;
      }
      const ul = el.appendChild(h('ul'));
      for (const item of list.items || []) {
        const li = ul.appendChild(h('li'));
        const r = put(li, String(item));
        if (r !== true && !(await r)) return;
      }
    }

    if (step.disclaimer) el.appendChild(h('p', 'disclaimer', step.disclaimer));
    if (step.button) {
      const btn = el.appendChild(h('button', 'bubble-btn', step.button.label || ''));
      btn.type = 'button';
      btn.addEventListener('click', () => hooks.onAction?.(step.button.action, step));
    }
    if (step.report) {
      const link = el.appendChild(h('button', 'report-link', 'Detailed Analysis Report ›'));
      link.type = 'button';
      link.addEventListener('click', () => hooks.onReport?.(step, shownAt));
    }
    scrollToBottom();
  }

  function addMaptureInstant(step) {
    buildMapture(step, { skip: true, alive: () => true }, false);
  }

  function playMapture(step, alive) {
    return buildMapture(step, { skip: false, alive }, true);
  }

  // ---------- 사용자 단계 ----------
  /** 사용자 동작(타이핑 후 Send, 또는 음성 모드에서 탭)을 기다린다 */
  function awaitUser(step) {
    return new Promise((resolve) => {
      pending = { step, n: 0, resolve };
      resetKeyState();
      if (step.input !== 'voice') setVoice(false); // 타이핑 차례면 음성 모드를 닫는다
      renderVoice();
      renderInput();
    });
  }

  function finishPending() {
    const p = pending;
    pending = null;
    resetKeyState();
    renderVoice();
    renderInput();
    input.blur(); // 키보드를 내려 답변이 넓게 보이도록
    p.resolve();
  }

  const typing = () => (pending && pending.step.input !== 'voice' ? pending : null);
  const voicePending = () => !!pending && pending.step.input === 'voice';

  // ---------- 음성 모드 (S04-Voice 목업) ----------
  // 실제 음성 인식은 없다. 마이크 탭 → 음성 모드, 화면 아무 곳이나 한 번 더 탭 → 질문이 올라간다.
  // 음성 모드는 다음 음성 질문을 위해 유지되고, X를 누르면 일반 입력창으로 돌아간다.
  function setVoice(on) {
    voiceOn = on;
    screen.classList.toggle('voice-on', on);
    refs.voice.hidden = !on;
    if (on) input.blur();
    renderVoice();
  }

  function renderVoice() {
    const listening = voicePending();
    refs.voice.classList.toggle('listening', listening);
    refs.voiceStatus.textContent = listening ? 'Listening…' : '\u00A0';
    armAutoSubmit();
  }

  // 음성 단계에 autoSubmit(초)이 있으면, 음성 모드에서 듣기 시작한 뒤 그 시간이 지나면 질문이 저절로 올라간다.
  // 그 전에 탭하면 즉시 올라가고, 값이 없으면 탭으로만 올라간다.
  function armAutoSubmit() {
    clearTimeout(autoTimer);
    autoTimer = 0;
    if (!voiceOn || !voicePending()) return;
    const seconds = Number(pending.step.autoSubmit);
    if (!(seconds > 0)) return;
    const waitingFor = pending;
    autoTimer = setTimeout(() => {
      autoTimer = 0;
      if (pending === waitingFor && voiceOn) finishPending();
    }, seconds * 1000);
  }

  screen.addEventListener('click', (e) => {
    const target = e.target;
    if (target.closest('[data-ref=voiceX]')) { setVoice(false); return; }
    if (target.closest('[data-ref=mic]')) {
      if (voicePending()) setVoice(true);
      return;
    }
    if (!voiceOn || !voicePending()) return;
    // 상단 바와 말풍선 안의 버튼·링크는 제 기능을 한다. 그 밖의 어디를 탭해도 질문이 올라간다.
    if (target.closest('.topbar, .bubble-btn, .report-link')) return;
    finishPending();
  });

  // ---------- 고스트 타이핑 ----------
  // 어떤 키를 눌러도 정해진 문장이 한 글자씩 써진다. 백스페이스는 한 글자 지움.
  //
  // 원칙: "키를 한 번 눌렀다 = 한 글자". 입력기가 실제로 무슨 글자를 넣으려 했는지는 보지 않는다.
  // 한글처럼 글자를 조합하는 입력기는 키 하나에 이벤트를 여러 개 보내거나(앞 글자 확정 + 새 글자 시작),
  // 길이가 그대로인 채 글자만 바뀌므로(ㄱ → 가 → 간) 이벤트의 내용이나 개수로 세면 멈추거나 건너뛴다.
  //
  //  1) keydown이 오면 그것이 키 한 번이다. 일반 키보드는 여기서 방향(입력/지우기)까지 알 수 있다.
  //     화면 키보드(Gboard 등)는 keyCode 229만 주므로, 바로 뒤따르는 입력 이벤트로 방향만 판정한다.
  //  2) keydown 없이 입력 이벤트만 오는 환경에서는, 아주 짧은 시간 안에 몰려오는 이벤트를 키 한 번으로 묶는다.
  function renderInput() {
    const t = typing();
    const value = t ? t.step.text.slice(0, t.n) : '';
    if (input.value !== value) input.value = value;
    if (document.activeElement === input) {
      try { input.setSelectionRange(value.length, value.length); } catch { /* 무시 */ }
    }
    // 내용에 맞춰 높이 조절 (긴 질문은 여러 줄로)
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, INPUT_MAX_HEIGHT) + 'px';
    input.scrollTop = input.scrollHeight;
  }

  const KEY_LINK_MS = 500;      // keydown 뒤 이 시간 안의 입력 이벤트는 그 키에 속한다
  const KEY_FALLBACK_MS = 60;   // keydown(229) 뒤 입력 이벤트가 안 오면 한 글자 입력으로 처리
  const SOLO_WINDOW_MS = 20;    // keydown이 없는 환경: 이 시간 안의 이벤트는 같은 키

  let key = null;          // 마지막 keydown: { at, applied, timer }
  let soloAt = -1e9;       // keydown 없이 처리한 마지막 입력 시각
  let lastComp = '';       // 진행 중인 조합 문자열
  let beforeSeen = false;  // 이 input 이벤트에 앞서 beforeinput이 있었는지

  function resetKeyState() {
    if (key) clearTimeout(key.timer);
    key = null;
    soloAt = -1e9;
    lastComp = '';
    beforeSeen = false;
  }

  /** 한 번의 키 입력을 반영. dir: 1(입력) / -1(지우기) / 'enter' */
  function applyPress(dir) {
    const t = typing();
    if (!t) return;
    const full = t.step.text.length;
    if (dir === 'enter') {
      // 문장을 다 쓴 뒤 Enter(키보드의 보내기 키) = Send
      if (t.n >= full) { trySend(); return; }
      dir = 1;
    }
    t.n = Math.max(0, Math.min(full, t.n + dir));
    renderInput();
    requestAnimationFrame(renderInput); // 입력기가 뒤늦게 넣은 글자까지 덮어쓴다
  }

  function flushKey() {
    if (!key || key.applied) return;
    clearTimeout(key.timer);
    key.applied = true;
    applyPress(1);
  }

  /** 조합 문자열을 낱자 단위로 푼다 (간 → ㄱㅏㄴ). 한글 조합 중 백스페이스 판정용 */
  const jamo = (s) => s.normalize('NFKD');

  /** 입력 이벤트의 방향: 1 / -1 / 'enter' */
  function directionOf(e) {
    const type = e.inputType || '';
    if (type === 'insertCompositionText') {
      // 같은 조합 안에서 문자열이 줄어들면 백스페이스다 (hello → hell, 간 → 가, ㄱ → 빈 문자열)
      const data = jamo(e.data || '');
      const prev = lastComp;
      lastComp = data;
      return data.length < prev.length && prev.startsWith(data) ? -1 : 1;
    }
    lastComp = '';
    if (type.startsWith('delete') || type === 'historyUndo') return -1;
    if (type === 'insertLineBreak' || type === 'insertParagraph') return 'enter';
    return 1;
  }

  /** 입력 이벤트 하나를 "키 한 번"에 대응시킨다 */
  function onTextEvent(e) {
    const dir = directionOf(e);
    const now = performance.now();
    if (key && now - key.at < KEY_LINK_MS) {
      if (key.applied) return;       // 이 키는 이미 셌다 (같은 키의 나머지 이벤트)
      clearTimeout(key.timer);
      key.applied = true;
      applyPress(dir);
      return;
    }
    if (now - soloAt < SOLO_WINDOW_MS) return;
    soloAt = now;
    applyPress(dir);
  }

  input.addEventListener('keydown', (e) => {
    flushKey(); // 앞 키가 아직 처리 전이면 먼저 반영
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    let dir = null;
    if (e.key === 'Backspace' || e.key === 'Delete') dir = -1;
    else if (e.key === 'Enter' && !e.isComposing && e.keyCode !== 229) dir = 'enter';
    else if (e.isComposing || e.keyCode === 229 || e.key === 'Unidentified' || e.key === 'Process') dir = null; // 입력기가 처리하는 키
    else if (e.key.length === 1) dir = 1; // 글자·숫자·기호·스페이스
    else return; // Shift, 방향키, 한/영 전환 등은 글자를 만들지 않는다

    key = { at: performance.now(), applied: false, timer: 0 };
    if (dir === null) {
      key.timer = setTimeout(flushKey, KEY_FALLBACK_MS);
      return;
    }
    e.preventDefault();
    key.applied = true;
    applyPress(dir);
  });

  input.addEventListener('beforeinput', (e) => {
    beforeSeen = true;
    onTextEvent(e);
    e.preventDefault();
    // 조합 입력은 취소할 수 없다 → 이어서 오는 input 이벤트에서 값을 다시 덮어쓴다
    if (e.defaultPrevented) beforeSeen = false;
    renderInput();
  });
  input.addEventListener('input', (e) => {
    if (!beforeSeen) onTextEvent(e); // beforeinput이 없는 브라우저 대비
    beforeSeen = false;
    renderInput();
  });
  input.addEventListener('compositionstart', () => { lastComp = ''; });
  input.addEventListener('compositionend', renderInput);
  input.addEventListener('focus', renderInput);
  input.addEventListener('blur', () => { lastComp = ''; });
  for (const type of ['paste', 'drop', 'cut']) input.addEventListener(type, (e) => e.preventDefault());

  function trySend() {
    const t = typing();
    if (!t) return;
    if (t.n < t.step.text.length) return; // 아직 다 안 씀
    if (t.step.sendDisabled) return;      // S#15: Send가 반응하지 않는다
    finishPending();
  }

  // Send·마이크를 눌러도 입력창 포커스(키보드)를 뺏지 않게
  for (const btn of [refs.send, refs.mic]) btn.addEventListener('pointerdown', (e) => e.preventDefault());
  refs.send.addEventListener('click', trySend);

  // ---------- ☰ 길게 누르기 → 숨은 씬 메뉴 ----------
  onLongPress(refs.menu, () => hooks.onMenuLongPress?.());

  renderInput();

  return {
    reset,
    addDivider,
    addUser,
    addMaptureInstant,
    playMapture,
    showLoading,
    hideLoading,
    awaitUser,
    scrollToBottom,
    setPlan(plan) { refs.plan.textContent = plan; },
  };
}
