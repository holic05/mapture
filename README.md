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
js/guard.js           촬영 중 사고 방지 (확대·길게 누르기 메뉴·글자 선택·뒤로 가기)
js/mascot.js          마스코트 SVG
js/longpress.js       길게 누르기 (숨은 씬 메뉴용)
js/views/chat.js      채팅 화면 (말풍선, 타이핑 출력, 고스트 타이핑, 음성 모드)
js/views/overlay.js   채팅 위를 덮는 전체 화면의 공통 틀
js/views/download.js  다운로드 페이지 + Open 전환 모션 (마스코트 시작 화면 카드)
js/views/paywall.js   결제 화면 + 결제 완료
js/views/report.js    Detailed Analysis Report
js/views/sceneMenu.js 숨은 씬 메뉴
scenes.json           씬 내용 ← 대사·숫자는 여기만 고치면 됨
manifest.json         PWA 설치 정보 (이름, 아이콘, 주소창 없는 실행)
sw.js                 서비스 워커 (오프라인 캐시)
icons/                앱 아이콘 (192, 512, svg)
tools/make-icons.py   아이콘 재생성 스크립트 (python3 tools/make-icons.py)
tools/check.py        Playwright 자동 확인 스크립트 (아래 8장)
tools/cue-sheet.py    scenes.json → docs/cue-sheet.md (촬영 큐시트)
tools/make-previews.py 스토어 Preview 스크린샷(img/preview-*.jpg)을 실제 앱 화면에서 다시 캡처
img/                  스토어 Preview 캡처 이미지
tools/format-scenes.py scenes.json을 "한 단계 = 한 줄"로 다시 정렬
docs/cue-sheet.md     씬별 촬영 큐시트 (자동 생성)
docs/content-drafts.md 작가 확인이 필요한 초안 목록
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
   - **Application → Cache storage**: `mapture-v11`(현재 `CACHE_VERSION`)에 파일들이 들어 있는지
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
| html / css / js / 아이콘 | `sw.js` 맨 위의 `CACHE_VERSION`을 올리고(`'v10'` → `'v11'`) push. |

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
  - 다운로드·결제·리포트 화면에서는 **왼쪽 위 버튼(뒤로 가기 / 닫기)** 을, 결제 완료 화면에서는 **체크 원**을 길게 누르면 됩니다.
- 마지막으로 고른 씬은 기억되어, 앱을 다시 열면 그 씬의 시작 상태로 열립니다.
- **타이핑 씬:** 입력창을 탭해 키보드를 올리고 **아무 키나** 누르면 정해진 문장이 한 글자씩 써집니다.
  백스페이스는 한 글자 지움. 끝까지 쓰고 Send(또는 키보드의 보내기 키)를 누르면 질문이 올라갑니다.
  - 키보드가 **한글이든 영어든** 상관없습니다. 키를 한 번 누르면 한 글자가 써집니다.
- **음성 씬:** 마이크 버튼을 탭하면 음성 모드가 됩니다. 입력창 대신 마이크·알약·X가 채팅 위에 떠 있고,
  듣는 중에는 화면 맨 아래가 은은한 초록빛이 되며 알약 바로 위에 `Listening…`이 뜹니다 (맨 아래로 자동 스크롤).
  듣는 중에 위로 스크롤하면 `Listening…`만 숨고 듣기는 계속됩니다. 맵쳐가 답하는 동안은 스크롤이 잠깁니다.
  그 상태에서 **화면 아무 곳이나 한 번 더 탭**하면 질문이 올라가고 답변이 이어집니다.
  `scenes.json`에서 그 질문에 `autoSubmit`(초)을 적어 두면 탭하지 않아도 그 시간 뒤에 저절로 올라갑니다.
  - 질문이 올라간 뒤에는 음성 모드가 **대기 상태**(알약이 멈추고 `Listening…`이 사라짐)가 됩니다.
    다음 질문은 **알약을 탭**해야 다시 듣기 시작합니다. 그 뒤는 같습니다 (탭하거나 `autoSubmit` 시간 뒤 올라감).
  - X를 누르면 일반 입력창으로 돌아갑니다.
- **답변 출력 중** 말풍선을 탭하면 남은 글자가 즉시 전부 표시됩니다.
- **S#4:** iPhone 앱 스토어 구조의 스토어 화면 → `GET` → 원형 진행 링(4초, `downloadSeconds`로 조절) → `OPEN` → 스토어 카드가 왼쪽으로 밀려 나가고, 마스코트가 보이는 맵쳐 카드가 들어와 전체 화면으로 커짐 → 바로 인사 화면 (약 1초). 마지막 `Upgrade to Premium`을 누르면 결제 화면으로 이어집니다.
  스토어 화면은 세로로 스크롤되고(평점·리뷰·설명까지), 정보 줄과 Preview 줄은 옆으로 넘길 수 있습니다. GET 말고는 눌러도 반응이 없습니다.
  아래로 스크롤해 GET이 가려지면 상단 바에 작은 GET이 나타나서, 스크롤한 채로 바로 누를 수 있습니다.
- **Upgrade 버튼:** 플랜이 Premium이면 보이지 않습니다 (결제 직후, 이후 씬에 이어 붙은 대화 모두).
- **결제:** 요금 카드를 탭해 고르고 `Subscribe for …` → 완료 화면 → `Start predicting`. 이후 상단 플랜이 `Premium`으로 바뀝니다.
- **리포트:** 답변 아래 `Detailed Analysis Report ›`를 탭. 왼쪽 위 뒤로 가기로 같은 대화로 돌아옵니다.
- **확률 공지 카드:** S#9는 처음부터, S#13은 씬 시작 1초 뒤 상단 바 아래에 카드가 내려옵니다. X로 닫을 수 있고 채팅 기록에는 남지 않습니다.
- **이어지는 대화:** 씬을 고르면 앞 씬들의 대화가 위에 이어 붙은 채로 열립니다 (같은 대화창처럼). 날짜가 다른 씬은 시간 구분선으로 구분됩니다.
- 씬별 동작 순서와 맞출 폰 시각은 **`docs/cue-sheet.md`** 에 있습니다.
- 개발용: 주소 뒤에 `?scene=S08`을 붙이면 그 씬으로 바로 시작합니다. `&solo=1`을 더하면 앞 씬 대화 없이 그 씬만 엽니다.

### 촬영 중 사고 방지로 막아 둔 것
길게 눌러 뜨는 복사·붙여넣기 메뉴, 글자 선택, 두 손가락·두 번 탭 확대, 가로 회전, 당겨서 새로고침,
Android 뒤로 가기로 앱이 닫히는 것, 번역 제안, 자동 다크 모드, 화면 꺼짐.
알림·전화처럼 앱 밖에서 오는 것은 막을 수 없으니 **방해 금지 모드**를 켜세요.

---

## 6. scenes.json 고치기

한 단계가 한 줄입니다. 고쳐서 push하면 앱을 다시 열 때 반영됩니다 (`CACHE_VERSION` 올릴 필요 없음).
문법이 틀리면 앱 화면 전체에 주황색 오류와 줄 번호가 뜹니다. JSON에는 주석을 쓸 수 없습니다.

씬 항목:

- `id`, `title`(씬 메뉴에 표시), `start`(`chat` / `download` / `paywall`: 첫 화면), `plan`, `profile`, `textScale`
- `after`: 앞 씬의 id. 그 씬(과 그 앞 씬들)의 대화가 이 씬 위에 이어 붙습니다. 없으면 이 씬만 열립니다.
- `gap`: 앞 씬으로부터 지난 시간 (`"30m"`, `"3h"`, `"2d"`, `"1w"`, `"2y"`). 앞 씬 대화의 시간 구분선이 그만큼 과거로 표시됩니다
  (`Yesterday 9:22 PM` → `Mon 9:22 PM` → `Nov 3 9:22 PM`, 연도는 표시하지 않음 — 영화 배경이 2040년).
  **이어 붙은 앞 씬의 구분선:** 날짜는 gap만큼 되감고, 시각은 그 씬의 `phoneTime`으로 고정합니다 (예: S06에서 본 S04 = 8일 전 9:22 PM).
  지금 씬의 구분선은 기기 시각(상태바 시계와 같음)이라, 촬영 때 폰 시각을 그 씬의 `phoneTime`에 맞추면 전부 자연스럽습니다.
  분·시간 단위는 **같은 날**이라는 뜻이라 자정 직후에 촬영해도 `Today`로 남습니다. 날짜를 넘기려면 `d`·`w`·`y`를 쓰세요.
- `downloadSeconds`: 스토어 화면의 다운로드 진행 링이 차는 시간 (기본 4초)
- `notice`: 상단 바 아래에 떠 있는 확률 공지 카드. 있을 때만 표시되고 채팅 기록에는 남지 않습니다.
  `{"value":"71.23%","delta":"0.10","up":true,"size":"compact","appear":"start"}`.
  `size`는 `compact`(기본) / `large`(숫자만 크게), `appear`는 `start`(씬 시작부터, 기본) / `drop`(씬 시작 1초 뒤 위에서 내려옴, `delay`초로 조절).
  `label`(기본 `Current Probability of Success`), `sub`(large에서 문구 아래 작은 글, 예: `Updated 2 min ago`)도 쓸 수 있습니다.
- `phoneTime`: 그 씬의 대본 시각(`"9:22 PM"`). 촬영 때 폰 시각을 여기에 맞춥니다(큐시트에 표시).
  앱은 이 씬이 다른 씬에 이어 붙을 때 구분선 시각으로 씁니다.
- `history`: 이 씬에만 미리 깔아 둘 메시지 (앞 씬 대화 다음에 즉시 표시)
- `steps`: 순서대로 재생

| 단계 | 형식 |
|---|---|
| 시간 구분선 | `{"type":"divider","time":"now"}` |
| 타이핑 질문 | `{"type":"user","input":"typing","text":"...","sendDisabled":false}` |
| 음성 질문 | `{"type":"user","input":"voice","text":"...","autoSubmit":3}` |
| 맵쳐 답변 | `{"type":"mapture", ...}` 아래 항목을 필요한 것만 |

음성 질문의 `autoSubmit`(초, 생략 가능): `Listening…`이 뜬 뒤 그 시간이 지나면 질문이 저절로 올라갑니다.
그 전에 탭하면 즉시 올라갑니다. 값이 없으면 탭으로만 올라갑니다.
`Listening…`은 첫 질문에서는 마이크를 탭할 때, 그다음 질문부터는 알약을 탭할 때 시작됩니다 (저절로 다시 듣지 않음).

맵쳐 답변 항목:

- `loading`: `{"seconds":2,"text":"One moment, please…","progressBar":false}`. 생략하면 2초 기본 로딩.
- `headline`: `{"label":"...","value":"71.13%","delta":"0.08","up":false,"size":"normal"}`.
  `size`는 `normal`/`huge`. `up`이 `true`면 ▲(빨강), `false`면 ▼(파랑) — 한국식. 색은 `css/app.css` 맨 위의 `--up`/`--down` 두 줄에서 바꿉니다. `up`과 `delta`를 둘 다 빼면 화살표 없음.
- `body`: 본문. 빈 줄(`\n\n`)로 문단을 나눌 수 있음.
- `compare`: 두 항목을 한 줄에 나란히 보여 주는 비교 블록 (본문 바로 아래).
  `{"items":[{"label":"AI Workflow Development","value":"70.98%"},{"label":"Introduction to New Media","value":"70.97%"}],"diff":"Difference: 0.01 percentage points"}`
- `list`: `[{"title":"Recommended","items":["...","..."]}, ...]`
- `disclaimer`, `button`(`{"label":"...","action":"paywall"}`: 누르면 결제 화면)
- `report`: `{"question":"...","askedAt":"now","items":[{"time":"+17m","event":"...","prob":"99.1%"}],"basedOn":["..."]}`.
  있으면 답변 아래에 리포트 링크가 생깁니다. `askedAt`이 `"now"`면 그 답변이 뜬 시각이고,
  `items`의 `"+17m"`은 **그 질문 시각으로부터** 17분 뒤입니다 (대사의 "in 17 minutes"와 항상 맞도록).
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
~/mapture-venv/bin/python tools/check.py --browser webkit   # iPhone Safari와 같은 엔진(WebKit)으로
~/mapture-venv/bin/python tools/make-previews.py            # 스토어 Preview 이미지 다시 만들기 (그 뒤 CACHE_VERSION 올리기)
```

WebKit은 처음 한 번 설치가 필요합니다: `~/mapture-venv/bin/python -m playwright install webkit` 그리고
`sudo ~/mapture-venv/bin/python -m playwright install-deps webkit` (시스템 라이브러리).

실제 Gboard의 동작과 진짜 키보드 애니메이션은 흉내만 내므로, 최종 확인은 폰에서 해야 합니다.

---

## 9. 큐시트와 초안 문서

```bash
python3 tools/cue-sheet.py       # scenes.json → docs/cue-sheet.md
python3 tools/format-scenes.py   # scenes.json 줄 정리 (내용은 그대로)
```

- `docs/cue-sheet.md`: 씬별 시작 화면, 배우 동작, 화면 대사, 걸리는 시간, 맞출 폰 시각. `scenes.json`을 고치면 다시 만드세요.
- `docs/content-drafts.md`: 대본에 없어 초안으로 채운 내용과 임의로 정한 설정값 목록. `scenes.json`에서는 `작가 확인`으로 검색.
