// 씬 엔진: scenes.json의 씬 하나를 순서대로 재생한다.
// 화면 그리기는 view(js/views/chat.js)가 맡고, 여기는 "지금 몇 번째 단계인가"만 관리한다.
import { dividerLabel, durationMs, gapDays, parseClock } from './time.js';

const DEFAULT_LOADING_TEXT = 'One moment, please…';
const DEFAULT_LOADING_SECONDS = 2;
const PAUSE_BEFORE_LOADING_MS = 350; // 질문이 올라간 뒤 로딩이 뜨기까지 잠깐의 숨
const PROGRESS_DELAY_SECONDS = 0.8;  // Progress Update가 도착하기 전 기본 대기
const NOTICE_DROP_SECONDS = 1;       // 공지 카드 appear: "drop" — 씬 시작 후 이만큼 뒤에 위에서 내려온다

/** headline만 있고 body·list가 없는 맵쳐 메시지 = Progress Update */
export function isProgressUpdate(step) {
  return !!step.headline && !step.body && !(step.list && step.list.length);
}

export class Engine {
  /** @param view js/views/chat.js의 createChat()이 돌려준 객체 */
  constructor(view) {
    this.view = view;
    this.gen = 0;            // 씬을 리셋할 때마다 1 증가 → 이전 씬의 비동기 작업은 전부 무효
    this.timers = new Set();
    this.scene = null;
    this.scenes = [];        // 전체 씬 목록 (app.js가 넣어 준다)
    this.chainScenes = true; // 앞 씬 대화 이어 붙이기 (?solo=1 이면 끔)
    this.sceneStart = new Date();
  }

  /** 진행 중인 재생을 멈춘다 (타이머 전부 취소) */
  stop() {
    this.gen++;
    for (const id of this.timers) clearTimeout(id);
    this.timers.clear();
  }

  /**
   * 씬 시작 시 애니메이션 없이 깔아 둘 메시지 목록: 앞 씬들의 대화 + 이 씬의 history.
   *
   * 씬에 "after": "<앞 씬 id>"가 있으면 그 씬(과 그 앞의 앞 씬들)의 대화가 이어 붙어
   * 하나의 대화창처럼 보인다. "gap"은 앞 씬으로부터 지난 시간("14h", "2d", "2y")이고,
   * 앞 씬의 시간 구분선은 그만큼 과거의 시각으로 표시된다(날짜가 바뀌면 Yesterday / 요일 / 날짜).
   *
   * @returns {{step: object, base: Date, now: Date, chained: boolean}[]}
   *   base: 그 단계가 속한 씬의 시작 시각, now: 그 단계의 "now"가 가리킬 시각
   */
  historyFor(scene) {
    // 앞 씬들을 오래된 순서로
    const chain = [];
    const seen = new Set([scene.id]);
    for (let s = scene; this.chainScenes && s.after;) {
      const prev = this.scenes.find((x) => x.id === s.after);
      if (!prev || seen.has(prev.id)) break; // 없는 씬이거나 순환이면 여기까지
      seen.add(prev.id);
      chain.unshift(prev);
      s = prev;
    }

    // 각 앞 씬의 시각: 날짜는 지금 씬에서 gap만큼씩 거슬러 올라가고(분·시간 단위 gap은 같은 날),
    // 시각은 그 씬의 대본 시각(phoneTime)으로 고정한다. 예: S06에서 본 S04 대화 = 8일 전 9:22 PM.
    // phoneTime이 없는 씬은 예전처럼 지금 시각에서 gap만큼 뺀 시각을 쓴다.
    const bases = new Map();
    let t = this.sceneStart.getTime();
    let days = 0;
    let later = scene;
    for (let i = chain.length - 1; i >= 0; i--) {
      const prev = chain[i];
      days += gapDays(later.gap);
      const dayStart = new Date(t).setHours(0, 0, 0, 0);
      t -= durationMs(later.gap);
      if (/[mh]\s*$/.test(String(later.gap ?? '')) && t < dayStart) t = dayStart; // 같은 날 gap은 전날로 넘기지 않는다
      const clock = parseClock(prev.phoneTime);
      if (clock) {
        const d = new Date(this.sceneStart);
        d.setDate(d.getDate() - days);
        d.setHours(clock.h, clock.m, 0, 0);
        t = d.getTime();
      }
      bases.set(prev, new Date(t));
      later = prev;
    }

    // 각 앞 씬이 끝나야 하는 시각 = 그다음 씬의 시작 시각
    const ends = new Map();
    chain.forEach((prev, i) => ends.set(prev, (i + 1 < chain.length ? bases.get(chain[i + 1]) : this.sceneStart).getTime()));

    const out = [];
    for (const prev of chain) {
      const base = bases.get(prev);
      let minutes = 0; // 그 씬 안에서 흐른 시간(질문 하나에 1분으로 어림) → 구분선 "now"가 조금씩 뒤로 간다
      for (const step of [...(prev.history || []), ...(prev.steps || [])]) {
        if (step.type === 'user' && step.sendDisabled) continue; // 보내지 못한 질문은 대화에 남지 않는다
        // 그 씬 안에서 흐른 시간이 다음 씬의 시각을 넘지 않게 한다
        const at = Math.min(base.getTime() + minutes * 60e3, ends.get(prev) - 60e3);
        out.push({ step, base, now: new Date(Math.max(at, base.getTime())), chained: true });
        if (step.type === 'user') minutes++;
      }
    }
    for (const step of scene.history || []) {
      out.push({ step, base: this.sceneStart, now: this.sceneStart, chained: false });
    }
    return out;
  }

  /** 씬을 시작 상태로 완전히 리셋하고 재생 시작 */
  start(scene) {
    this.stop();

    const gen = this.gen;
    this.scene = scene;
    this.sceneStart = new Date();
    this.index = 0;
    this.pendingDivider = null;

    this.view.reset(scene);

    // 앞 씬들의 대화 + history: 애니메이션 없이 즉시
    for (const { step, base, now, chained } of this.historyFor(scene)) {
      if (step.type === 'divider') this.view.addDivider(dividerLabel(step.time, base, now));
      else if (step.type === 'user') this.view.addUser(step.text, { voice: step.input === 'voice' });
      else if (step.type === 'mapture') this.view.addMaptureInstant(step, { shownAt: now, inert: chained });
    }
    this.view.scrollToBottom();

    // 확률 공지 카드: 씬 시작부터 떠 있거나(기본), 잠시 뒤 위에서 내려온다(appear: "drop")
    const notice = scene.notice;
    if (notice) {
      if (notice.appear === 'drop') {
        this.sleep((notice.delay ?? NOTICE_DROP_SECONDS) * 1000).then(() => {
          if (this.alive(gen)) this.view.showNotice(notice, true);
        });
      } else {
        this.view.showNotice(notice, false);
      }
    }

    this.run(gen);
  }

  alive(gen) { return gen === this.gen; }

  sleep(ms) {
    return new Promise((resolve) => {
      const id = setTimeout(() => { this.timers.delete(id); resolve(); }, ms);
      this.timers.add(id);
    });
  }

  /** 구분선은 바로 그리지 않고, 다음 메시지가 실제로 표시되는 순간에 함께 그린다.
      (그래야 "now"가 그 메시지의 시각이 되고, 첫 질문 전에는 빈 상태 화면이 유지된다) */
  flushDivider() {
    if (!this.pendingDivider) return;
    this.view.addDivider(dividerLabel(this.pendingDivider.time, this.sceneStart), { live: true });
    this.pendingDivider = null;
  }

  async run(gen) {
    const steps = this.scene.steps || [];
    const alive = () => this.alive(gen);

    while (this.index < steps.length) {
      const step = steps[this.index];

      if (step.type === 'divider') {
        this.pendingDivider = step;
      } else if (step.type === 'user') {
        // 사용자 동작(Send / 마이크)을 기다린다. 기다리는 동안은 목록을 스크롤할 수 있다.
        this.view.setBusy(false);
        await this.view.awaitUser(step);
        if (!alive()) return;
        this.flushDivider();
        this.view.addUser(step.text, { voice: step.input === 'voice', live: true });
      } else if (step.type === 'mapture') {
        this.view.setBusy(true); // 맵쳐가 답하는 동안(대기·로딩 포함)은 스크롤 잠금
        await this.playMapture(step, alive);
        if (!alive()) return;
      }
      this.index++;
    }
    this.view.setBusy(false);
  }

  async playMapture(step, alive) {
    const progress = isProgressUpdate(step);

    // 아무것도 보이지 않는 대기
    const delay = step.delay ?? (progress && !step.loading ? PROGRESS_DELAY_SECONDS : 0);
    if (delay > 0) {
      await this.sleep(delay * 1000);
      if (!alive()) return;
    }

    // 로딩 (Progress Update는 loading을 적지 않으면 로딩 없이 도착)
    const loading = step.loading ?? (progress ? null : {});
    if (loading) {
      await this.sleep(PAUSE_BEFORE_LOADING_MS);
      if (!alive()) return;
      this.flushDivider();
      const seconds = loading.seconds ?? DEFAULT_LOADING_SECONDS;
      this.view.showLoading({
        text: loading.text || DEFAULT_LOADING_TEXT,
        seconds,
        progressBar: !!loading.progressBar,
      });
      await this.sleep(seconds * 1000);
      if (!alive()) return;
      this.view.hideLoading();
    }

    this.flushDivider();
    await this.view.playMapture(step, alive);
  }
}
