// 씬 엔진: scenes.json의 씬 하나를 순서대로 재생한다.
// 화면 그리기는 view(js/views/chat.js)가 맡고, 여기는 "지금 몇 번째 단계인가"만 관리한다.
import { dividerLabel } from './time.js';

const DEFAULT_LOADING_TEXT = 'One moment, please…';
const DEFAULT_LOADING_SECONDS = 2;
const PAUSE_BEFORE_LOADING_MS = 350; // 질문이 올라간 뒤 로딩이 뜨기까지 잠깐의 숨
const PROGRESS_DELAY_SECONDS = 0.8;  // Progress Update가 도착하기 전 기본 대기

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
    this.sceneStart = new Date();
  }

  /** 씬을 시작 상태로 완전히 리셋하고 재생 시작 */
  start(scene) {
    this.gen++;
    for (const id of this.timers) clearTimeout(id);
    this.timers.clear();

    const gen = this.gen;
    this.scene = scene;
    this.sceneStart = new Date();
    this.index = 0;
    this.pendingDivider = null;

    this.view.reset(scene);

    // history: 애니메이션 없이 즉시
    for (const step of scene.history || []) {
      if (step.type === 'divider') this.view.addDivider(dividerLabel(step.time, this.sceneStart));
      else if (step.type === 'user') this.view.addUser(step.text, { voice: step.input === 'voice' });
      else if (step.type === 'mapture') this.view.addMaptureInstant(step);
    }
    this.view.scrollToBottom();

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
        // 사용자 동작(Send / 마이크)을 기다린다
        await this.view.awaitUser(step);
        if (!alive()) return;
        this.flushDivider();
        this.view.addUser(step.text, { voice: step.input === 'voice', live: true });
      } else if (step.type === 'mapture') {
        await this.playMapture(step, alive);
        if (!alive()) return;
      }
      this.index++;
    }
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
