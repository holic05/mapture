// ④ Detailed Analysis Report (S04-Report)
import { openOverlay } from './overlay.js';
import { resolveTime, formatClock } from '../time.js';

const BACK = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1A1D1C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 6l-6 6 6 6"/></svg>';

const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

/**
 * @param {HTMLElement} root
 * @param {object} report      scenes.json의 report
 * @param {{sceneStart: Date, shownAt: Date|null, onMenuLongPress?: Function}} ctx
 *   shownAt: 그 답변이 화면에 뜬 시각. askedAt이 "now"면 이 시각이 질문 시각이 된다.
 */
export function showReport(root, report, ctx) {
  // 질문 시각
  let asked = report.askedAt === 'now' || report.askedAt == null
    ? (ctx.shownAt || ctx.sceneStart)
    : resolveTime(report.askedAt, ctx.sceneStart);
  const askedLabel = asked instanceof Date ? formatClock(asked) : String(asked);
  // 예측 시각 "+17m"은 질문 시각 기준 (질문 시각이 글자면 씬 시작 기준)
  const anchor = asked instanceof Date ? asked : ctx.sceneStart;
  const timeLabel = (v) => {
    const t = resolveTime(v, anchor);
    return t instanceof Date ? formatClock(t) : (t ?? '');
  };

  const items = report.items || [];
  const ov = openOverlay(root, 'report', `
    <header class="ov-top">
      <button type="button" class="icon-btn" data-menu data-ref="back" aria-label="Back">${BACK}</button>
      <span class="ov-title">Detailed Analysis Report</span>
    </header>
    <main class="report-main">
      <div class="report-q">
        <span class="cap">Your question · ${esc(askedLabel)}</span>
        <span class="report-q-text">${esc(report.question)}</span>
      </div>
      <span class="cap">Predicted timeline</span>
      <div class="timeline">
        ${items.map((it, i) => `
        <div class="tl-item">
          <div class="tl-rail"><i></i>${i < items.length - 1 ? '<b></b>' : ''}</div>
          <div class="tl-body">
            <span class="tl-time">${esc(timeLabel(it.time))}</span>
            <span class="tl-event">${esc(it.event)}</span>
            ${it.prob ? `<span class="tl-prob">${esc(it.prob)}</span>` : ''}
          </div>
        </div>`).join('')}
      </div>
      ${(report.basedOn || []).length ? `
      <div class="report-based">
        <span class="cap">Based on</span>
        <div class="chips">${report.basedOn.map((b) => `<span>${esc(b)}</span>`).join('')}</div>
      </div>` : ''}
    </main>`, ctx);

  ov.el.querySelector('[data-ref=back]').addEventListener('click', () => ov.close());
  return ov;
}
