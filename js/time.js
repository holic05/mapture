// scenes.json의 시각 값 처리
//   "now"            → 그 메시지가 표시되는 순간의 기기 시각
//   "-5m" "-2h" "-1d" → 씬 시작 시각 기준 과거 (history용)
//   "+17m"           → 씬 시작 시각 기준 미래 (리포트용)
//   그 외 문자열      → 그대로 표시

const UNIT = { m: 60e3, h: 3600e3, d: 86400e3 };
const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

/** @returns {Date|string|null} Date면 계산된 시각, string이면 그대로 표시할 글자 */
export function resolveTime(value, sceneStart) {
  if (value == null || value === '') return null;
  if (value === 'now') return new Date();
  const m = /^([+-])\s*(\d+(?:\.\d+)?)\s*([mhd])$/.exec(String(value).trim());
  if (m) {
    const ms = Number(m[2]) * UNIT[m[3]] * (m[1] === '-' ? -1 : 1);
    return new Date(sceneStart.getTime() + ms);
  }
  return String(value);
}

/** 9:39 PM */
export function formatClock(date) {
  const h = date.getHours();
  const mm = String(date.getMinutes()).padStart(2, '0');
  return `${h % 12 || 12}:${mm} ${h < 12 ? 'AM' : 'PM'}`;
}

/** 구분선용: Today 9:22 PM / Yesterday 9:22 PM / Mon 10:05 AM */
export function dividerLabel(value, sceneStart) {
  const t = resolveTime(value, sceneStart);
  if (t == null) return '';
  if (typeof t === 'string') return t;
  const dayIndex = (d) => Math.floor(new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime() / 86400e3 + 0.5);
  const diff = dayIndex(new Date()) - dayIndex(t);
  const day = diff === 0 ? 'Today' : diff === 1 ? 'Yesterday' : diff === -1 ? 'Tomorrow' : DAYS[t.getDay()];
  return `${day} ${formatClock(t)}`;
}

/** 리포트용: 9:39 PM (3단계에서 사용) */
export function clockLabel(value, sceneStart) {
  const t = resolveTime(value, sceneStart);
  if (t == null) return '';
  return typeof t === 'string' ? t : formatClock(t);
}
