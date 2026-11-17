// scenes.json의 시각 값 처리
//
// 날짜는 극 중 달력, 시각만 폰 시계:
//   씬마다 "date"(극 중 날짜, 예: "2040-09-13")가 있다. iPhone 상태바에는 날짜가 나오지 않으므로 실제 날짜는 쓰지 않는다.
//   지금 씬의 "지금" = 그 씬의 극 중 날짜 + 폰 시계의 시각. Today / Yesterday / 요일도 극 중 날짜로 계산한다.
//
//   "now"            → 그 메시지가 표시되는 순간 (극 중 날짜 + 폰 시각)
//   "-5m" "-2h" "-1d" → 씬 시작 시각 기준 과거 (history용)
//   "+17m"           → 씬 시작 시각 기준 미래 (리포트용)
//   "-2d 11:14 PM"   → 씬 시작 날짜에서 이틀 전, 시각은 11:14 PM (더미 대화용. "-0d 1:32 PM" = 같은 날)
//   그 외 문자열      → 그대로 표시

const UNIT = { m: 60e3, h: 3600e3, d: 86400e3, w: 7 * 86400e3, y: 365 * 86400e3 };
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

/** @returns {Date|string|null} Date면 계산된 시각, string이면 그대로 표시할 글자 */
export function resolveTime(value, sceneStart, now = new Date()) {
  if (value == null || value === '') return null;
  if (value === 'now') return now;
  // "-2d 11:14 PM": 기준 날짜에서 이틀 전, 시각은 11:14 PM으로 고정 (더미 대화처럼 그날의 시각이 정해진 경우)
  const d = /^([+-])\s*(\d+)\s*d\s+(.+)$/.exec(String(value).trim());
  const clock = d && parseClock(d[3]);
  if (clock) {
    const t = new Date(sceneStart);
    t.setDate(t.getDate() + Number(d[2]) * (d[1] === '-' ? -1 : 1));
    t.setHours(clock.h, clock.m, 0, 0);
    return t;
  }
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

/** "2040-09-13" → 그날 0시 (기기 시간대). 형식이 틀리면 null */
export function parseDate(value) {
  const m = /^\s*(\d{4})-(\d{2})-(\d{2})\s*$/.exec(String(value ?? ''));
  if (!m) return null;
  const d = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
  return d.getMonth() === Number(m[2]) - 1 ? d : null;
}

/** 극 중 날짜(date) + 폰 시계의 시각. date가 없으면 실제 오늘 */
export function onStoryDate(date, clock = new Date()) {
  const day = parseDate(date);
  if (!day) return new Date(clock);
  day.setHours(clock.getHours(), clock.getMinutes(), clock.getSeconds(), clock.getMilliseconds());
  return day;
}

/** "9:22 PM" → { h: 21, m: 22 }. 형식이 틀리면 null */
export function parseClock(value) {
  const m = /^\s*(\d{1,2}):(\d{2})\s*([AaPp])\.?\s*[Mm]\.?\s*$/.exec(String(value ?? ''));
  if (!m) return null;
  const h = Number(m[1]) % 12 + (/[Pp]/.test(m[3]) ? 12 : 0);
  const min = Number(m[2]);
  return h < 24 && min < 60 ? { h, m: min } : null;
}

/**
 * 구분선용. 오늘에서 멀어질수록 날짜가 구체적으로 바뀐다. 연도는 쓰지 않는다 (영화 배경이 2040년):
 *   Today 9:22 PM / Yesterday 9:22 PM / Mon 10:05 AM (6일 이내) / Nov 3 9:22 PM / Aug 25 10:59 AM
 * @param now   "now" 값이 가리킬 시각 (이어 붙인 앞 씬의 대화는 그 씬의 시각)
 * @param today 지금 씬의 "오늘" (극 중 날짜). Today·Yesterday·요일을 이 날짜 기준으로 정한다
 */
export function dividerLabel(value, sceneStart, now, today = new Date()) {
  const t = resolveTime(value, sceneStart, now);
  if (t == null) return '';
  if (typeof t === 'string') return t;
  const dayIndex = (d) => Math.floor(new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime() / 86400e3 + 0.5);
  const diff = dayIndex(today) - dayIndex(t);
  let day;
  if (diff === 0) day = 'Today';
  else if (diff === 1) day = 'Yesterday';
  else if (diff === -1) day = 'Tomorrow';
  else if (diff > 1 && diff < 7) day = DAYS[t.getDay()];
  else day = `${MONTHS[t.getMonth()]} ${t.getDate()}`;
  return `${day} ${formatClock(t)}`;
}

/** 리포트용: 9:39 PM (3단계에서 사용) */
export function clockLabel(value, sceneStart) {
  const t = resolveTime(value, sceneStart);
  if (t == null) return '';
  return typeof t === 'string' ? t : formatClock(t);
}
