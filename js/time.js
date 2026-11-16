// scenes.json의 시각 값 처리
//   "now"            → 그 메시지가 표시되는 순간의 기기 시각
//   "-5m" "-2h" "-1d" → 씬 시작 시각 기준 과거 (history용)
//   "+17m"           → 씬 시작 시각 기준 미래 (리포트용)
//   그 외 문자열      → 그대로 표시

const UNIT = { m: 60e3, h: 3600e3, d: 86400e3, w: 7 * 86400e3, y: 365 * 86400e3 };
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

/** @returns {Date|string|null} Date면 계산된 시각, string이면 그대로 표시할 글자 */
export function resolveTime(value, sceneStart, now = new Date()) {
  if (value == null || value === '') return null;
  if (value === 'now') return now;
  const m = /^([+-])\s*(\d+(?:\.\d+)?)\s*([mhdwy])$/.exec(String(value).trim());
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

/** "14h", "2d", "2y" 같은 간격을 밀리초로 (씬의 gap용). 형식이 틀리면 0 */
export function durationMs(value) {
  const m = /^\s*(\d+(?:\.\d+)?)\s*([mhdwy])\s*$/.exec(String(value ?? ''));
  return m ? Number(m[1]) * UNIT[m[2]] : 0;
}

/**
 * 구분선용. 오늘에서 멀어질수록 날짜가 구체적으로 바뀐다:
 *   Today 9:22 PM / Yesterday 9:22 PM / Mon 10:05 AM (6일 이내) / Nov 3 9:22 PM / Nov 16, 2024 9:22 PM
 * @param now "now" 값이 가리킬 시각 (이어 붙인 앞 씬의 대화는 그 씬의 시각)
 */
export function dividerLabel(value, sceneStart, now) {
  const t = resolveTime(value, sceneStart, now);
  if (t == null) return '';
  if (typeof t === 'string') return t;
  const today = new Date();
  const dayIndex = (d) => Math.floor(new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime() / 86400e3 + 0.5);
  const diff = dayIndex(today) - dayIndex(t);
  let day;
  if (diff === 0) day = 'Today';
  else if (diff === 1) day = 'Yesterday';
  else if (diff === -1) day = 'Tomorrow';
  else if (diff > 1 && diff < 7) day = DAYS[t.getDay()];
  else day = `${MONTHS[t.getMonth()]} ${t.getDate()}${t.getFullYear() !== today.getFullYear() ? ', ' + t.getFullYear() : ''}`;
  return `${day} ${formatClock(t)}`;
}

/** 리포트용: 9:39 PM (3단계에서 사용) */
export function clockLabel(value, sceneStart) {
  const t = resolveTime(value, sceneStart);
  if (t == null) return '';
  return typeof t === 'string' ? t : formatClock(t);
}
