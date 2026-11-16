// Mapture 마스코트 SVG (Main.dc.html 기준). 문자열을 돌려주므로 innerHTML로 넣어 쓴다.

/** 전체 마스코트: 얼굴 구체 + 기울어진 궤도 고리 + 반짝임 */
export function mascotSVG(size = 128) {
  return `<svg class="mascot" width="${size}" height="${size}" viewBox="0 0 120 120" role="img" aria-label="Mapture mascot">
  <g class="mascot-ring-back"><ellipse cx="60" cy="64" rx="56" ry="15" fill="none" stroke="#0F7B6C" stroke-opacity="0.35" stroke-width="4" transform="rotate(-14 60 64)"/></g>
  ${faceShapes()}
  <path class="mascot-ring-front" d="M7 79Q60 92 113 49" fill="none" stroke="#0F7B6C" stroke-width="4" stroke-linecap="round"/>
  <path class="mascot-sparkle" d="M101 8l3 7 7 3-7 3-3 7-3-7-7-3 7-3z" fill="#0F7B6C"/>
</svg>`;
}

/** 앱 아이콘용: 고리·반짝임 없이 얼굴 구체만 */
export function faceSVG(size = 64) {
  return `<svg width="${size}" height="${size}" viewBox="22 22 76 76" role="img" aria-label="Mapture">${faceShapes()}</svg>`;
}

function faceShapes() {
  return `<circle cx="60" cy="60" r="38" fill="#0F7B6C"/>
  <circle cx="46" cy="44" r="8" fill="#FFFFFF" fill-opacity="0.22"/>
  <circle cx="48" cy="58" r="5" fill="#FFFFFF"/>
  <circle cx="72" cy="58" r="5" fill="#FFFFFF"/>
  <path d="M47 71q13 11 26 0" fill="none" stroke="#FFFFFF" stroke-width="4.5" stroke-linecap="round"/>`;
}
