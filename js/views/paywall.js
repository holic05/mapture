// ③ 결제 화면 (S05-Paywall) → 처리 중 → 결제 완료 (S05-Done). 실제 결제는 없다.
import { mascotSVG } from '../mascot.js';
import { openOverlay, wait } from './overlay.js';

const PROCESSING_MS = 800;

const PLANS = [
  { id: 'year', title: 'One-Year Subscription', sub: '₩20,833 / month', price: '₩250,000', badge: 'SAVE 9%', note: 'Renews yearly. Cancel anytime in Settings.' },
  { id: 'month', title: 'One-Month Subscription', sub: 'Billed monthly', price: '₩22,900', note: 'Renews monthly. Cancel anytime in Settings.' },
];
const BENEFITS = ['200 prediction tokens per day', 'Enhanced long-term simulation', 'Real-time Progress Updates'];

const CHECK = (size, stroke) => `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${stroke}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12l5 5 9-10"/></svg>`;
const CLOSE = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1A1D1C" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>';

/**
 * @param {HTMLElement} root
 * @param {{onMenuLongPress?: Function, onPaid?: Function, onClose?: Function}} hooks
 *   onPaid: 결제 완료 화면이 뜨는 순간 (플랜 표시를 Premium으로 바꿀 시점)
 */
export function showPaywall(root, hooks = {}) {
  const ov = openOverlay(root, 'paywall', `
    <header class="ov-top">
      <button type="button" class="icon-btn" data-menu data-ref="close" aria-label="Close">${CLOSE}</button>
    </header>
    <main class="pay-main">
      <div class="pay-hero">
        ${mascotSVG(88)}
        <h1>Mapture Premium</h1>
        <p>See further into your future.</p>
      </div>
      <ul class="pay-benefits">${BENEFITS.map((b) => `<li>${CHECK(20, '#0F7B6C')}<span>${b}</span></li>`).join('')}</ul>
      <div class="pay-plans">
        ${PLANS.map((p, i) => `
        <button type="button" class="pay-plan${i === 0 ? ' selected' : ''}" data-plan="${p.id}">
          ${p.badge ? `<span class="pay-badge">${p.badge}</span>` : ''}
          <span class="pay-plan-text"><b>${p.title}</b><small>${p.sub}</small></span>
          <span class="pay-price">${p.price}</span>
        </button>`).join('')}
      </div>
    </main>
    <footer class="pay-foot">
      <button type="button" class="pay-cta" data-ref="cta"></button>
      <p data-ref="note"></p>
    </footer>`, hooks);

  const q = (ref) => ov.el.querySelector(`[data-ref=${ref}]`);
  let plan = PLANS[0];
  let busy = false;

  const render = () => {
    ov.el.querySelectorAll('.pay-plan').forEach((el) => el.classList.toggle('selected', el.dataset.plan === plan.id));
    q('cta').textContent = `Subscribe for ${plan.price}`;
    q('note').textContent = plan.note;
  };
  render();

  ov.el.querySelectorAll('.pay-plan').forEach((el) => el.addEventListener('click', () => {
    if (busy) return;
    plan = PLANS.find((p) => p.id === el.dataset.plan);
    render();
  }));

  q('close').addEventListener('click', () => {
    if (busy) return;
    ov.close();
    hooks.onClose?.();
  });

  q('cta').addEventListener('click', async () => {
    if (busy) return;
    busy = true;
    q('cta').innerHTML = '<span class="btn-spinner" aria-label="Processing"></span>';
    await wait(PROCESSING_MS);
    if (!ov.alive()) return;
    hooks.onPaid?.(plan);
    ov.el.classList.add('overlay-done');
    ov.replace(`
      <div class="done">
        <div class="done-check" data-menu>${CHECK(48, '#FFFFFF')}</div>
        <h1>Welcome to Premium</h1>
        <p>Payment complete · ${plan.price}<br>Your future starts now.</p>
        <button type="button" class="done-btn" data-ref="start">Start predicting</button>
      </div>`);
    q('start').addEventListener('click', () => ov.close());
  });

  return ov;
}
