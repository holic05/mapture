# Mapture — 단편 영화 소품 앱

단편 영화 「Mapture」 촬영용 소품 앱입니다. 실제 AI·음성 인식·결제·네트워크 기능은 없고,
`scenes.json`에 적힌 시나리오를 순서대로 재생할 뿐입니다.
빌드 도구 없이 순수 HTML/CSS/JS로 되어 있어서 파일을 그대로 GitHub Pages에 올리면 동작합니다.

## 파일 구성

```
index.html            앱 진입 HTML
css/app.css           디자인 토큰 + 전체 스타일
js/app.js             진입점: scenes.json 로딩, 씬 선택, 키보드 대응, Wake Lock, 서비스 워커 등록
js/engine.js          씬 엔진 (단계 진행, 로딩, 타이머)
js/time.js            시각 값 처리 ("now", "-5m", "+17m")
js/fatal.js           화면 전체 오류 표시
js/mascot.js          마스코트 SVG
js/views/chat.js      채팅 화면 (말풍선, 타이핑 출력, 고스트 타이핑)
js/views/sceneMenu.js 숨은 씬 메뉴
scenes.json           씬 내용 ← 대사·숫자는 여기만 고치면 됨
manifest.json         PWA 설치 정보 (이름, 아이콘, 주소창 없는 실행)
sw.js                 서비스 워커 (오프라인 캐시)
icons/                앱 아이콘 (192, 512, svg)
tools/make-icons.py   아이콘 재생성 스크립트 (python3 tools/make-icons.py)
tools/check.py        Playwright 자동 확인 스크립트 (아래 8장)
```

> `readme/`는 기획 참고 자료라서 `.gitignore`로 배포에서 빠집니다.

---

## PWA 짧은 설명

- **PWA**는 웹 페이지를 앱처럼 홈 화면에 설치하는 방식입니다. 설치하면 주소창 없이 전체 화면으로 열립니다.
- **manifest.json**: 앱 이름, 아이콘, `display: "standalone"`(주소창 없음) 같은 설치 정보.
- **서비스 워커(sw.js)**: 브라우저가 백그라운드에서 돌리는 스크립트. 앱 파일을 폰에 캐시해 두고
  다음부터는 네트워크 대신 캐시에서 꺼내 줍니다. 그래서 비행기 모드에서도 열립니다.
- 서비스 워커와 설치는 **HTTPS 또는 `localhost`에서만** 동작합니다.
  (`http://192.168.x.x` 같은 내부 IP로 폰에서 열면 설치가 안 됩니다.)

---

## 1. PC에서 확인하기

프로젝트 루트(이 폴더)에서 아무 정적 서버나 띄웁니다.

```bash
python3 -m http.server 8000
```

1. Chrome에서 `http://localhost:8000` 열기 (WSL에서 띄워도 Windows Chrome의 localhost로 열립니다)
2. `F12` → 왼쪽 위 기기 아이콘(**Toggle device toolbar**, `Ctrl+Shift+M`)
3. 상단 기기 선택에서 **Dimensions: Responsive**, 크기 `390 × 844` 입력 (또는 Pixel 7 등 선택)
4. 확인할 것
   - DevTools → **Application** 탭 → **Manifest**: 이름·아이콘이 보이고 오류가 없는지
   - **Application → Service workers**: `sw.js`가 *activated and is running*인지
   - **Application → Cache storage**: `mapture-v2`(현재 `CACHE_VERSION`)에 파일들이 들어 있는지
   - **Network** 탭에서 *Offline* 체크 후 새로고침 → 그래도 열리는지

> 개발 중에는 **Application → Service workers → "Update on reload"**를 체크해 두면
> 새로고침할 때마다 최신 파일을 받아서 캐시 때문에 헷갈리지 않습니다.

---

## 2. GitHub Pages에 배포하기

1. GitHub에서 새 저장소 만들기 (예: `mapture`). Public이어야 무료 Pages 사용 가능.
2. 이 폴더에서:
   ```bash
   git init
   git add .
   git commit -m "Mapture prop app"
   git branch -M main
   git remote add origin https://github.com/<계정>/mapture.git
   git push -u origin main
   ```
3. 저장소 **Settings → Pages → Build and deployment**
   - Source: **Deploy from a branch**
   - Branch: **main** / **/(root)** → Save
4. 1~2분 뒤 `https://<계정>.github.io/mapture/` 에서 열립니다.
   (모든 경로가 상대 경로라 `/mapture/` 같은 하위 경로에서도 동작합니다.)

---

## 3. Android 폰에 설치하기

1. 폰 **Chrome**으로 `https://<계정>.github.io/mapture/` 열기
2. 화면이 한 번 다 뜰 때까지 기다리기 (이때 서비스 워커가 파일을 캐시합니다)
3. 오른쪽 위 **⋮** → **홈 화면에 추가** (또는 **앱 설치**) → **설치**
   - "설치" 대신 "바로가기 만들기"만 보이면 아직 서비스 워커가 준비 안 된 것 → 새로고침 후 다시 시도
4. 홈 화면의 **Mapture** 아이콘으로 실행 → 주소창이 없고 Android 상태바(시계)는 그대로 보이면 성공
5. 오프라인 확인: 앱을 한 번 연 뒤 완전히 종료 → 비행기 모드 → 다시 실행

---

## 4. 수정 후 폰에 반영하기 (캐시 갱신)

| 고친 것 | 할 일 |
|---|---|
| `scenes.json`만 | 그냥 push. 앱을 다시 열면 반영됩니다 (scenes.json은 항상 네트워크 먼저 받아옴). |
| html / css / js / 아이콘 | `sw.js` 맨 위의 `CACHE_VERSION`을 올리고(`'v2'` → `'v3'`) push. |

`CACHE_VERSION`을 올린 뒤 폰에서:

1. GitHub Pages 반영까지 1~2분 기다리기
2. 앱을 **완전히 종료** (최근 앱 목록에서 위로 밀어서 닫기)
3. 다시 실행 → 새 서비스 워커가 설치되면 앱이 자동으로 한 번 새로고침되어 새 버전이 적용됩니다
4. 그래도 예전 화면이면 한 번 더 완전히 종료 후 실행

새 JS 파일을 추가했다면 `sw.js`의 `APP_FILES` 목록에도 넣어 주세요 (오프라인 동작용).

### 그래도 안 바뀔 때 (최후의 수단)
폰 Chrome → 설정 → 사이트 설정 → 모든 사이트 → `<계정>.github.io` → **데이터 삭제** 후 다시 열기.
(설치된 아이콘은 그대로 둬도 됩니다.)

---

## 5. 촬영 현장에서 쓰는 법

- **씬 고르기:** 왼쪽 위 ☰ 버튼을 **길게(0.6초)** 누르면 씬 목록이 열립니다. 고르면 그 씬의 시작 상태로 완전히 리셋됩니다.
  같은 씬을 다시 고르면 테이크를 처음부터 다시 찍을 수 있습니다. (☰ 짧게 누르기는 아무 일도 없음)
- 마지막으로 고른 씬은 기억되어, 앱을 다시 열면 그 씬의 시작 상태로 열립니다.
- **타이핑 씬:** 입력창을 탭해 키보드를 올리고 **아무 키나** 누르면 정해진 문장이 한 글자씩 써집니다.
  백스페이스는 한 글자 지움. 끝까지 쓰고 Send(또는 키보드의 보내기 키)를 누르면 질문이 올라갑니다.
- **음성 씬:** 마이크 버튼을 탭하면 질문이 올라갑니다. (음성 모드 화면은 3단계에서 추가)
- **답변 출력 중** 말풍선을 탭하면 남은 글자가 즉시 전부 표시됩니다.
- 개발용: 주소 뒤에 `?scene=S08`을 붙이면 그 씬으로 바로 시작합니다.

---

## 6. scenes.json 고치기

한 단계가 한 줄입니다. 고쳐서 push하면 앱을 다시 열 때 반영됩니다 (`CACHE_VERSION` 올릴 필요 없음).
문법이 틀리면 앱 화면 전체에 주황색 오류와 줄 번호가 뜹니다. JSON에는 주석을 쓸 수 없습니다.

씬: `id`, `title`(씬 메뉴에 표시), `start`, `plan`, `profile`, `textScale`, `history`(즉시 표시), `steps`(순서대로 재생)

| 단계 | 형식 |
|---|---|
| 시간 구분선 | `{"type":"divider","time":"now"}` |
| 타이핑 질문 | `{"type":"user","input":"typing","text":"...","sendDisabled":false}` |
| 음성 질문 | `{"type":"user","input":"voice","text":"..."}` |
| 맵쳐 답변 | `{"type":"mapture", ...}` 아래 항목을 필요한 것만 |

맵쳐 답변 항목:

- `loading`: `{"seconds":2,"text":"One moment, please…","progressBar":false}`. 생략하면 2초 기본 로딩.
- `headline`: `{"label":"...","value":"71.13%","delta":"0.08","up":false,"size":"normal"}`.
  `size`는 `normal`/`huge`. `up`이 `true`면 ▲(파랑), `false`면 ▼(주황), `up`과 `delta`를 둘 다 빼면 화살표 없음.
- `body`: 본문. 빈 줄(`\n\n`)로 문단을 나눌 수 있음.
- `list`: `[{"title":"Recommended","items":["...","..."]}, ...]`
- `disclaimer`, `button`(`{"label":"...","action":"paywall"}`), `report`
- `typingSpeed`: 초당 글자 수 (기본 18)
- `delay`: 아무것도 표시하지 않고 기다리는 초
- `note`: 화면에 나오지 않는 메모 (작가 확인용 `[TODO]`를 여기에 적어 둠)

**Progress Update** = `headline`만 있고 `body`·`list`가 없는 답변. 로딩 없이 0.8초 뒤(또는 `delay`초 뒤) 도착합니다.

**시간 구분선**은 바로 뜨지 않고 다음 메시지가 올라오는 순간 함께 뜹니다.
그래서 씬이 구분선으로 시작해도 첫 질문 전까지는 인사 화면이 유지됩니다.

시각 값: `"now"`(표시되는 순간), `"-5m"` `"-2h"` `"-1d"`(씬 시작 기준 과거), `"+17m"`(미래), 그 외 글자는 그대로 표시.

아직 정해지지 않은 내용은 `scenes.json`에서 `TODO`를 검색하세요.

---

## 7. 아이콘 다시 만들기

```bash
python3 tools/make-icons.py
```
얼굴 구체만 흰 배경 위에 그려 `icons/`에 PNG(192, 512)와 SVG를 생성합니다. 외부 라이브러리 불필요.
아이콘을 바꿨다면 `CACHE_VERSION`도 올리세요. 이미 설치한 폰은 홈 화면 아이콘이 늦게 바뀌거나
안 바뀔 수 있으니, 그때는 아이콘 삭제 후 재설치하세요.

---

## 8. 자동 확인 (Playwright)

모바일 크기(360/390/430px)의 Chromium으로 앱을 실제로 조작해 PASS/FAIL을 출력하고,
스크린샷을 `tools/shots/`에 남깁니다 (고스트 타이핑, 키보드가 열린 높이, 씬 메뉴, 오프라인 실행 등).

```bash
python3 -m http.server 8000                      # 다른 터미널에서
~/mapture-venv/bin/python tools/check.py         # 전체
~/mapture-venv/bin/python tools/check.py --only typing,menu
~/mapture-venv/bin/python tools/check.py --base https://<계정>.github.io/mapture/   # 배포본 확인
```

실제 Gboard의 동작과 진짜 키보드 애니메이션은 흉내만 내므로, 최종 확인은 폰에서 해야 합니다.
