# 콘텐츠 초안 목록 (작가 확인 필요)

`scenes.json`의 `[TODO]` 자리를 대본 톤에 맞춰 초안으로 채운 목록입니다. 전부 **확정이 아닌 초안**이고,
`scenes.json`에서는 해당 단계의 `note`에 `[TODO: 작가 확인]`으로 표시되어 있습니다 (`작가 확인`으로 검색).
확정되면 문장을 고치고 `note`를 지우면 됩니다. `note`는 화면에 나오지 않습니다.

## 1. 채운 대사·내용

| 씬 | 위치 | 이전 | 초안 |
|---|---|---|---|
| S03 | 이전 대화 2개 (history) | [TODO 내용] | Will it rain this afternoon? / How crowded is the café near the station right now? + 답변 |
| S03 | 재성의 질문 | [TODO: Jaeseong's question, e.g. "When will Jasmine arrive?"] | When will Jasmine arrive? |
| S04 | 1분 뒤 예측 답변 (카페 버전) | In one minute, there is a 99.98% probability that a delivery rider bringing fried chicken to the apartment upstairs will pass by your front door! | In one minute, there is a 99.98% probability that a delivery rider picking up fried chicken for the office upstairs will walk right past your table! |
| S04 | 창문 질문 (카페 버전) | Mapture, what will I see if I open my window right now? | Mapture, what will I see if I look out the window right now? |
| S04 | 창문 답변 (카페 버전) | If you open your window right now, there is a 99.97% probability that you'll make eye contact with a neighbor illegally dumping trash! | If you look out the window right now, there is a 99.97% probability that you'll make eye contact with a passerby illegally dumping trash! |
| S04b | 1분 뒤 예측 답변 (카페 버전) | In one minute, there is a 99.98% probability that a delivery rider bringing fried chicken to the apartment upstairs will pass by your front door! | In one minute, there is a 99.98% probability that a delivery rider picking up fried chicken for the office upstairs will walk right past your table! |
| S04b | 창문 질문 (카페 버전) | Mapture, what will I see if I open my window right now? | Mapture, what will I see if I look out the window right now? |
| S04b | 창문 답변 (카페 버전) | If you open your window right now, there is a 99.97% probability that you'll make eye contact with a neighbor illegally dumping trash! | If you look out the window right now, there is a 99.97% probability that you'll make eye contact with a passerby illegally dumping trash! |
| S04b | 추가 Q&A 1 (질문) | [TODO: additional question 1] | Mapture, will it rain on my way home? |
| S04b | 추가 Q&A 1 (답변) | [TODO: additional answer 1] | Based on an analysis of weather data and your usual route, there is a 3.2% probability that it will rain before you get home at 10:41 p.m.! |
| S04b | 추가 Q&A 2 (질문) | [TODO: additional question 2] | Mapture, am I going to pass tomorrow's quiz? |
| S04b | 추가 Q&A 2 (답변) | [TODO: additional answer 2] | Based on an analysis of your study records and your professor's past quizzes, there is an 88.4% probability that you will pass tomorrow's quiz! |
| S06 | Probability of Success 시작값 | [TODO: 시작값] | 35.87% ▲ 1.70 |
| S08 | Recommended instead 목록 2·3번 | [TODO] / [TODO] | TOEIC Speaking mock test / Résumé clinic at the Career Development Center |
| S08 | Detailed Analysis Report 내용 | [TODO] | 타임라인 3개 (Sun 6:00 PM / Sun 11:30 PM / Mon 9:00 AM) |
| S09 | Low-risk hobbies 4·5번 | [TODO] / [TODO] | Solving sudoku puzzles / Walking for under 20 minutes |
| S10 | Recommended 4~6번 | [TODO] ×3 | The Little Prince / Jonathan Livingston Seagull / Who Moved My Cheese? |
| S10 | Not Recommended 2~4번 | [TODO] ×3 | The Stranger / No Longer Human / Bartleby, the Scrivener |
| S13e | 74.11% 화살표 | 대본: ▼ | ▲ 0.72 (숫자 기준, 미확정) |
| S14 | 질문 | [TODO: e.g. "What's my probability of success if I join Oracle Group?"] | What's my probability of success if I join Oracle Group? |
| S14 | 답변 한 문장 | [TODO 한 문장] | Based on an analysis of your records, joining Oracle Group would raise your probability of success ten years from now to 87%! |

메모:
- **S04 / S04b 카페 버전:** 대본 원문(집 배경: 윗집 치킨 배달, 창문을 열면 쓰레기 무단 투기 이웃)을 카페 배경으로 옮겼습니다. 질문 문장도 `open my window` → `look out the window`로 바꿨습니다. 원문은 각 단계의 `note`에 남겨 두었습니다.
- **S06 시작값 35.87%:** S04의 34.17%에 첫 답변의 +1.7%p를 더한 값입니다. 뒤의 Progress Update(41.72 → 53.19 → 63.03)와 이어집니다.
- **S13e:** 대본은 ▼인데 숫자는 73.39 → 74.11로 오릅니다. 지금은 숫자를 따라 ▲ 0.72로 표시합니다. 화살표와 숫자 중 어느 쪽이 맞는지 확인이 필요합니다.
- **S03 이전 대화:** 화면 위쪽에 깔리는 예시 대화 2개는 임시 내용입니다.

## 2. 임의로 정한 설정값 (확인 필요)

### 씬 사이의 시간 간격 (`gap`)

앞 씬 대화가 이어 붙을 때, 앞 씬의 시간 구분선이 얼마나 과거로 표시될지 정합니다. 대본 기준으로 맞췄고, 대본에 없는 값은 임의입니다.
분·시간 단위(`30m`, `3h`)는 **같은 날**을 뜻해서 구분선이 항상 `Today`로 남습니다. 날짜를 넘기려면 `d`·`w`·`y`를 씁니다.

| 씬 | 앞 씬 (`after`) | 지난 시간 (`gap`) | 근거 |
|---|---|---|---|
| S05 | S04 | 7d | 대본 "One Week Later" |
| S06 | S05 | 1d | 임의 (미확정) |
| S07 | S06 | 3d | 임의 (미확정) |
| S08 | S07 | 30m | S07에서 바로 이동, 같은 날 |
| S09 | S08 | 4d | 콘서트 당일인 일요일, S08 며칠 뒤 (4일은 임의) |
| S10 | S09 | 30m | S09 직후, 같은 날 |
| S11 | S10 | 20w | 벚꽃·다음 학기 수강신청, 수개월 뒤 (20주는 임의) |
| S13a | S11 | 3w | 한 학기에 걸쳐 (컷마다 3주는 임의) |
| S13b | S13a | 3w | 〃 |
| S13c | S13b | 3w | 〃 |
| S13d | S13c | 3w | 〃 |
| S13e | S13d | 3w | 〃 |
| S14 | S13e | 2y | 대본 "TWO YEARS LATER" |
| S15 | S14 | 30m | S14 직후, 같은 날 |

S03(재성의 폰)과 S04b(S04 재촬영용)는 다른 씬에 이어 붙지 않습니다.

### 음성 질문 자동 올리기 (`autoSubmit`)

`Listening…`이 뜬 뒤 이 시간이 지나면 질문이 저절로 올라갑니다. 단어 수 ÷ 2 + 1.5초(0.5초 단위 올림)로 넉넉하게 잡았습니다.
배우의 말 속도에 맞춰 조절하세요. 그 전에 화면을 탭하면 즉시 올라갑니다.

| 씬 | 질문 | 단어 수 | autoSubmit |
|---|---|---|---|
| S04 | Is anyone going to contact me tonight? | 7 | 5초 |
| S04 | What's going to happen in one minute? | 7 | 5초 |
| S04 | Mapture, what will I see if I look out the window right now? | 13 | 8초 |
| S04 | …What's the probability that, ten years from now, I'll be living the life I want? | 15 | 9초 |
| S04 | Mapture, how do I avoid that—?! | 6 | 4.5초 |
| S04b | …What's the probability that, ten years from now, I'll be living the life I want? | 15 | 9초 |
| S04b | Mapture, how do I avoid that—?! | 6 | 4.5초 |
| S06 | Mapture, what should I start studying now if I want to succeed? | 12 | 7.5초 |
| S06 | Mapture, what should I choose as my presentation topic in my Human Resource Management class if I want to succeed? | 20 | 11.5초 |
| S06 | Mapture, are there any events I can attend right now that would help me succeed? | 15 | 9초 |
| S06 | Mapture, what certification should I get if I want to succeed? | 11 | 7초 |
| S07 | Mapture, what should I have for dinner tonight? | 8 | 5.5초 |

### 기타

- **다운로드 시간:** S04 `downloadSeconds: 4` (원형 진행 링, 2026-11-17 요청으로 3초 → 4초). 촬영하며 조절.
- **맞출 폰 시각 (`phoneTime`, 큐시트 표시용):** S03 `3:30 PM` (대사의 `Estimated arrival: 3:32 p.m.`, 2분 뒤), S04 `9:22 PM` (대사의 `in 17 minutes, at 9:39 p.m.`), S04b `9:47 PM` (목업 기준 임의).
- **스토어 화면 문구:** iPhone 앱 스토어 구조로 바꾸면서 Store-1~3 목업 문구를 그대로 씁니다
  (7.2M Ratings · 4.9 · Age 12+ · Chart #1 Productivity · Developer Oracle Inc. · Events `Meet Mapture 6` · Preview 문구 2개). `js/views/download.js`.
- **S11 답변 (비교 블록):** 대본의 "두 숫자가 화면에 나란히"에 맞춰 짧은 한 문장 + 비교 블록으로 바꿨습니다.
  문장 `Here's how your probability of success compares for this semester!`와 차이 표시 `Difference: 0.01 percentage points`는 초안입니다.
  원래 문장은 `note`에 보존.
- **S09 공지 카드의 증감:** `▲ 0.10` (S08의 71.13% → 71.23%, 목업 S09-Notice-Compact와 같음).
