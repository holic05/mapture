# Mapture 촬영 큐시트

> 이 문서는 `python3 tools/cue-sheet.py`가 `scenes.json`에서 자동으로 만듭니다. 직접 고치지 말고 `scenes.json`을 고친 뒤 다시 실행하세요.

## 촬영 전 공통 준비

- 홈 화면의 **Mapture 아이콘**으로 실행 (주소창이 없어야 함). 촬영 전 Wi-Fi가 되는 곳에서 한 번 열어 최신 내용을 받아 둘 것
- **방해 금지 모드** 켜기 (알림·전화가 화면에 뜨지 않게), 화면 밝기 고정, 배터리 절약 모드 끄기
- 화면 자동 회전 끄기 (앱도 세로로 고정되어 있음)
- 키보드는 한글·영어 아무거나 가능. 타이핑 씬에서는 **아무 키나** 누르면 정해진 문장이 써짐
- **씬 고르기:** 왼쪽 위 ☰ 를 0.6초 길게 누름 → 목록에서 선택. 같은 씬을 다시 고르면 처음 상태로 리셋 (재촬영)
  - 스토어·결제·리포트 화면에서는 왼쪽 위 버튼(뒤로/닫기)을 길게 누름
- 폰 시각을 맞춰야 하는 씬은 설정 → 날짜 및 시간 → 자동 설정 끄고 직접 입력 (촬영 후 되돌리기)
- 시간 구분선과 리포트의 시각은 **촬영 순간의 폰 시각**으로 찍힘

## 씬 목록

| 씬 | 시작 화면 | 플랜 | 질문 방식 | 폰 시각 |
|---|---|---|---|---|
| S03 S#3 Café — Jaeseong's phone | 채팅 | Premium | 타이핑 | 3:30 PM |
| S04 S#4 Café — first use | 스토어 | Free | 음성 | 9:22 PM |
| S04b S#4 Café — retake from 10-year question | 채팅 | Free | 음성 | 9:47 PM |
| S05 S#5 Classroom — payment | 결제 | Free | 없음 | — |
| S06 S#6 Montage — voice Q&A | 채팅 | Premium | 음성 | — |
| S07 S#7 Daehangno — night | 채팅 | Premium | 음성 | — |
| S08 S#8 Restaurant — concert | 채팅 | Premium | 타이핑 | — |
| S09 S#9 Study room | 채팅 | Premium | 타이핑 | — |
| S10 S#10 Library — book list | 채팅 | Premium | 없음 | — |
| S11 S#11 Emily's room — course comparison | 채팅 | Premium | 타이핑 | — |
| S13a S#13 Montage — cut a (69.53%) | 채팅 | Premium | 없음 | — |
| S13b S#13 Montage — cut b (73.22%) | 채팅 | Premium | 없음 | — |
| S13c S#13 Montage — cut c (72.88%) | 채팅 | Premium | 없음 | — |
| S13d S#13 Montage — cut d (73.39%) | 채팅 | Premium | 없음 | — |
| S13e S#13 Montage — cut e (74.11%) | 채팅 | Premium | 없음 | — |
| S14 S#14 Café — two years later | 채팅 | Premium | 타이핑 | — |
| S15 S#15 Campus bench — Send does not respond | 채팅 | Premium | 타이핑 | — |

## S03 — S#3 Café — Jaeseong's phone

- **시작 화면:** 채팅 화면, 이전 메시지 4개가 깔려 있고 맨 아래로 스크롤된 상태 (이 씬의 history)
- **상단 표시:** Mapture Premium · 프로필 `J`
- **맞출 폰 시각:** **3:30 PM** (대사 속 시각과 맞추기 위해)

| # | 배우 동작 | 화면에 나오는 것 | 걸리는 시간 |
|---|---|---|---|
| 1 | 입력창 탭 → 아무 키 25번 → Send | (시간 구분선 `Today 현재 시각`) “When will Jasmine arrive?” |  |
| 2 | (자동) 탭하면 글자 즉시 완성 | Jasmine — 98.6% probability of arriving in 2 minutes. Estimated arrival: 3:32 p.m. | 로딩 1초 `One moment, please…`, 글자 출력 약 5초 (82자, 초당 18자) |

자동으로 진행되는 시간 합계: 약 6초 (배우 동작 시간 제외)

확인 필요:
- [TODO: 작가 확인] 임시 대화 (이전 대화 예시)
- [TODO: 작가 확인] 질문 문장

## S04 — S#4 Café — first use

- **시작 화면:** 스토어(다운로드) 화면 → 빈 인사 화면 (`Hello, user!`)
- **상단 표시:** Mapture Free · 프로필 `E`
- **맞출 폰 시각:** **9:22 PM** (대사 속 시각과 맞추기 위해)

| # | 배우 동작 | 화면에 나오는 것 | 걸리는 시간 |
|---|---|---|---|
| 1 | `Download` 탭 | 진행 바가 3초 동안 참 → 버튼이 `Open`으로 | 3초 |
| 2 | `Open` 탭 | 스토어 카드가 왼쪽으로 밀려 나가고 맵쳐 카드가 들어와 커짐 → 마스코트 → 인사 화면 | 약 2초 |
| 3 | 마이크 탭(음성 모드, `Listening…`) → 대사를 말함 → 화면 아무 곳 탭, 또는 5초 뒤 자동 | (시간 구분선 `Today 현재 시각`) 🎤 “Is anyone going to contact me tonight?” |  |
| 4 | (자동) 탭하면 글자 즉시 완성 | Based on an analysis of your behavioral patterns and those of the people in your contacts, there is approximately a 99.1% probability that Lee Chaeyeon will call you in 17 minutes, at 9:39 p.m., to invite you out for drinks!<br>[링크: Detailed Analysis Report ›] | 로딩 2초 `One moment, please…`, 글자 출력 약 12초 (224자, 초당 18자) |
| 5 | 대사를 말함 → 화면 아무 곳 탭, 또는 5초 뒤 자동 | (시간 구분선 `Today 현재 시각`) 🎤 “What's going to happen in one minute?” |  |
| 6 | (자동) 탭하면 글자 즉시 완성 | In one minute, there is a 99.98% probability that a delivery rider picking up fried chicken for the office upstairs will walk right past your table! | 로딩 2초 `One moment, please…`, 글자 출력 약 8초 (148자, 초당 18자) |
| 7 | 대사를 말함 → 화면 아무 곳 탭, 또는 8초 뒤 자동 | 🎤 “Mapture, what will I see if I look out the window right now?” |  |
| 8 | (자동) 탭하면 글자 즉시 완성 | If you look out the window right now, there is a 99.97% probability that you'll make eye contact with a passerby illegally dumping trash! | 로딩 2초 `One moment, please…`, 글자 출력 약 8초 (137자, 초당 18자) |
| 9 | 대사를 말함 → 화면 아무 곳 탭, 또는 9초 뒤 자동 | 🎤 “…What's the probability that, ten years from now, I'll be living the life I want?” |  |
| 10 | (자동) 탭하면 글자 즉시 완성 | **Probability · 10-year outlook: 34.17%** (큰 숫자)<br>According to my analysis, the probability that you'll be living the life you want in ten years is 34.17%!<br><sub>Estimate based on your behavioral patterns, contacts, academic records and macroeconomic data. Predictions are probabilistic and do not guarantee outcomes.</sub> | 로딩 6초 `Performing long-term analysis…` + 진행 바, 글자 출력 약 9초 (105자, 초당 12자) |
| 11 | 대사를 말함 → 화면 아무 곳 탭, 또는 4.5초 뒤 자동 | 🎤 “Mapture, how do I avoid that—?!” |  |
| 12 | (자동) 탭하면 글자 즉시 완성 | Oh! I'm sorry, but it looks like you've used up all your predictions on the Mapture Free plan. Upgrade to Premium now to receive 200 prediction tokens per day and enhanced long-term simulation features!<br>[버튼: Upgrade to Premium] | 로딩 2초 `One moment, please…`, 글자 출력 약 11초 (202자, 초당 18자) |
| 13 | `Upgrade to Premium` 탭 | 결제 화면 → 결제하면 같은 대화로 돌아오고 플랜이 `Premium` |  |

자동으로 진행되는 시간 합계: 약 69초 (배우 동작 시간 제외)

확인 필요:
- [TODO: 작가 확인] 카페 버전 초안. 대본 원문: In one minute, there is a 99.98% probability that a delivery rider bringing fried chicken to the apartment upstairs will pass by your front door!
- [TODO: 작가 확인] 카페 버전 초안. 대본 원문: Mapture, what will I see if I open my window right now?
- [TODO: 작가 확인] 카페 버전 초안. 대본 원문: If you open your window right now, there is a 99.97% probability that you'll make eye contact with a neighbor illegally dumping trash!

## S04b — S#4 Café — retake from 10-year question

- **시작 화면:** 채팅 화면, 이전 메시지 10개가 깔려 있고 맨 아래로 스크롤된 상태 (이 씬의 history)
- **상단 표시:** Mapture Free · 프로필 `E`
- **맞출 폰 시각:** **9:47 PM** (대사 속 시각과 맞추기 위해)

| # | 배우 동작 | 화면에 나오는 것 | 걸리는 시간 |
|---|---|---|---|
| 1 | 마이크 탭(음성 모드, `Listening…`) → 대사를 말함 → 화면 아무 곳 탭, 또는 9초 뒤 자동 | 🎤 “…What's the probability that, ten years from now, I'll be living the life I want?” |  |
| 2 | (자동) 탭하면 글자 즉시 완성 | **Probability · 10-year outlook: 34.17%** (큰 숫자)<br>According to my analysis, the probability that you'll be living the life you want in ten years is 34.17%!<br><sub>Estimate based on your behavioral patterns, contacts, academic records and macroeconomic data. Predictions are probabilistic and do not guarantee outcomes.</sub> | 로딩 6초 `Performing long-term analysis…` + 진행 바, 글자 출력 약 9초 (105자, 초당 12자) |
| 3 | 대사를 말함 → 화면 아무 곳 탭, 또는 4.5초 뒤 자동 | 🎤 “Mapture, how do I avoid that—?!” |  |
| 4 | (자동) 탭하면 글자 즉시 완성 | Oh! I'm sorry, but it looks like you've used up all your predictions on the Mapture Free plan. Upgrade to Premium now to receive 200 prediction tokens per day and enhanced long-term simulation features!<br>[버튼: Upgrade to Premium] | 로딩 2초 `One moment, please…`, 글자 출력 약 11초 (202자, 초당 18자) |
| 5 | `Upgrade to Premium` 탭 | 결제 화면 → 결제하면 같은 대화로 돌아오고 플랜이 `Premium` |  |

자동으로 진행되는 시간 합계: 약 29초 (배우 동작 시간 제외)

확인 필요:
- [TODO: 작가 확인] 카페 버전 초안. 대본 원문: In one minute, there is a 99.98% probability that a delivery rider bringing fried chicken to the apartment upstairs will pass by your front door!
- [TODO: 작가 확인] 카페 버전 초안. 대본 원문: Mapture, what will I see if I open my window right now?
- [TODO: 작가 확인] 카페 버전 초안. 대본 원문: If you open your window right now, there is a 99.97% probability that you'll make eye contact with a neighbor illegally dumping trash!
- [TODO: 작가 확인] 겹쳐 쌓이는 질문 초안

## S05 — S#5 Classroom — payment

- **시작 화면:** 결제 화면 (닫거나 결제하면 아래의 채팅 화면) → 이전 메시지 10개가 깔려 있고 맨 아래로 스크롤된 상태 (앞 씬 대화 이어 붙음: S04)
- **상단 표시:** Mapture Free · 프로필 `E`
- **맞출 폰 시각:** 정해진 값 없음
- **앞 씬(S04)으로부터:** 7일 뒤 → 앞 씬 대화의 구분선이 그만큼 과거 날짜로 표시됨

| # | 배우 동작 | 화면에 나오는 것 | 걸리는 시간 |
|---|---|---|---|
| 1 | 요금 카드 탭해 선택 (기본: One-Year) | `Mapture Premium` 결제 화면, 버튼 `Subscribe for ₩250,000` / `₩22,900` |  |
| 2 | `Subscribe for …` 탭 | 버튼 안 스피너 → `Welcome to Premium` / `Payment complete · ₩…` | 0.8초 |
| 3 | `Start predicting` 탭 | 채팅 화면, 상단 플랜이 `Premium`으로 |  |

자동으로 진행되는 시간 합계: 약 1초 (배우 동작 시간 제외)

## S06 — S#6 Montage — voice Q&A

- **시작 화면:** 채팅 화면, 이전 메시지 10개가 깔려 있고 맨 아래로 스크롤된 상태 (앞 씬 대화 이어 붙음: S04 → S05)
- **상단 표시:** Mapture Premium · 프로필 `E`
- **맞출 폰 시각:** 정해진 값 없음 (구분선에 촬영 순간의 실제 시각이 `Today h:mm`으로 찍힘 → 극 중 시간대에 맞추면 좋음)
- **앞 씬(S05)으로부터:** 1일 뒤 → 앞 씬 대화의 구분선이 그만큼 과거 날짜로 표시됨

| # | 배우 동작 | 화면에 나오는 것 | 걸리는 시간 |
|---|---|---|---|
| 1 | 마이크 탭(음성 모드, `Listening…`) → 대사를 말함 → 화면 아무 곳 탭, 또는 7.5초 뒤 자동 | (시간 구분선 `Today 현재 시각`) 🎤 “Mapture, what should I start studying now if I want to succeed?” |  |
| 2 | (자동) 탭하면 글자 즉시 완성 | **Probability of Success: 35.87% ▲ 1.70**<br>Based on an analysis of international affairs and your personal traits, starting to learn Spanish now could increase your probability of success ten years from now by 1.7 percentage points! | 로딩 2초 `One moment, please…`, 글자 출력 약 10초 (189자, 초당 18자) |
| 3 | 대사를 말함 → 화면 아무 곳 탭, 또는 11.5초 뒤 자동 | 🎤 “Mapture, what should I choose as my presentation topic in my Human Resource Management class if I want to succeed?” |  |
| 4 | (자동) 탭하면 글자 즉시 완성 | Based on an analysis of your professor's interests and your personal traits, giving a presentation on strategic HRM would give you a 62.2% probability of making an impression on your professor and could increase your probability of success ten years from now by 0.41 percentage points! | 로딩 2초 `One moment, please…`, 글자 출력 약 16초 (285자, 초당 18자) |
| 5 | (자동) | **Progress Update: 41.72% ▲** | 0.8초 뒤 도착 (로딩 없음) |
| 6 | 대사를 말함 → 화면 아무 곳 탭, 또는 9초 뒤 자동 | 🎤 “Mapture, are there any events I can attend right now that would help me succeed?” |  |
| 7 | (자동) 탭하면 글자 즉시 완성 | Based on an analysis of the job market and your personal traits, attending the HR department's recruitment information session at Sosun Group could increase your probability of success ten years from now by 0.03 percentage points! | 로딩 2초 `One moment, please…`, 글자 출력 약 13초 (230자, 초당 18자) |
| 8 | (자동) | **Progress Update: 53.19% ▲** | 0.8초 뒤 도착 (로딩 없음) |
| 9 | 대사를 말함 → 화면 아무 곳 탭, 또는 7초 뒤 자동 | 🎤 “Mapture, what certification should I get if I want to succeed?” |  |
| 10 | (자동) 탭하면 글자 즉시 완성 | Based on an analysis of industry trends and your personal traits, earning a certification as an AI Labor Management Specialist could increase your probability of success ten years from now by 2.1 percentage points! | 로딩 2초 `One moment, please…`, 글자 출력 약 12초 (214자, 초당 18자) |
| 11 | (자동) | **Progress Update: 63.03% ▲** | 0.8초 뒤 도착 (로딩 없음) |

자동으로 진행되는 시간 합계: 약 63초 (배우 동작 시간 제외)

확인 필요:
- [TODO: 작가 확인] 시작값 초안: 34.17% + 1.7%p = 35.87%

## S07 — S#7 Daehangno — night

- **시작 화면:** 채팅 화면, 이전 메시지 21개가 깔려 있고 맨 아래로 스크롤된 상태 (앞 씬 대화 이어 붙음: S04 → S05 → S06)
- **상단 표시:** Mapture Premium · 프로필 `E`
- **맞출 폰 시각:** 정해진 값 없음 (구분선에 촬영 순간의 실제 시각이 `Today h:mm`으로 찍힘 → 극 중 시간대에 맞추면 좋음)
- **앞 씬(S06)으로부터:** 3일 뒤 → 앞 씬 대화의 구분선이 그만큼 과거 날짜로 표시됨

| # | 배우 동작 | 화면에 나오는 것 | 걸리는 시간 |
|---|---|---|---|
| 1 | 마이크 탭(음성 모드, `Listening…`) → 대사를 말함 → 화면 아무 곳 탭, 또는 5.5초 뒤 자동 | (시간 구분선 `Today 현재 시각`) 🎤 “Mapture, what should I have for dinner tonight?” |  |
| 2 | (자동) 탭하면 글자 즉시 완성 | Based on an analysis of your dining preferences and those of your friends, there's a 92.6% probability that you'll have a satisfying meal if you eat naengmyeon at Hamheung-Myeonok, near Exit 2 of Hyehwa Station! | 로딩 2초 `One moment, please…`, 글자 출력 약 12초 (211자, 초당 18자) |

자동으로 진행되는 시간 합계: 약 14초 (배우 동작 시간 제외)

## S08 — S#8 Restaurant — concert

- **시작 화면:** 채팅 화면, 이전 메시지 23개가 깔려 있고 맨 아래로 스크롤된 상태 (앞 씬 대화 이어 붙음: S04 → S05 → S06 → S07)
- **상단 표시:** Mapture Premium · 프로필 `E`
- **맞출 폰 시각:** 정해진 값 없음 (구분선에 촬영 순간의 실제 시각이 `Today h:mm`으로 찍힘 → 극 중 시간대에 맞추면 좋음)
- **앞 씬(S07)으로부터:** 30분 뒤 → 앞 씬 대화의 구분선이 그만큼 과거 날짜로 표시됨

| # | 배우 동작 | 화면에 나오는 것 | 걸리는 시간 |
|---|---|---|---|
| 1 | 입력창 탭 → 아무 키 48번 → Send | (시간 구분선 `Today 현재 시각`) “Mapture, should I go to the concert this Sunday?” |  |
| 2 | (자동) 탭하면 글자 즉시 완성 | **Probability of Success: 71.13% ▼ 0.08**<br>Based on the goals you've set, I would not recommend attending the concert this Sunday. Attending the concert this Sunday could decrease your long-term probability of success by 0.08%! Instead, I recommend the following activities.<br>*Recommended instead*: APSI Employment Fair / TOEIC Speaking mock test / Résumé clinic at the Career Development Center<br>[링크: Detailed Analysis Report ›] | 로딩 2초 `One moment, please…`, 글자 출력 약 19초 (340자, 초당 18자) |

자동으로 진행되는 시간 합계: 약 21초 (배우 동작 시간 제외)

확인 필요:
- [TODO: 작가 확인] 대체 활동 2·3번과 리포트 내용 초안

## S09 — S#9 Study room

- **시작 화면:** 채팅 화면, 이전 메시지 26개가 깔려 있고 맨 아래로 스크롤된 상태 (앞 씬 대화 이어 붙음: S04 → S05 → S06 → S07 → S08; 이 씬의 history)
- **상단 표시:** Mapture Premium · 프로필 `E`
- **맞출 폰 시각:** 정해진 값 없음 (구분선에 촬영 순간의 실제 시각이 `Today h:mm`으로 찍힘 → 극 중 시간대에 맞추면 좋음)
- **앞 씬(S08)으로부터:** 4일 뒤 → 앞 씬 대화의 구분선이 그만큼 과거 날짜로 표시됨

| # | 배우 동작 | 화면에 나오는 것 | 걸리는 시간 |
|---|---|---|---|
| 1 | 입력창 탭 → 아무 키 42번 → Send | (시간 구분선 `Today 현재 시각`) “What should I do when I can't concentrate?” |  |
| 2 | (자동) 탭하면 글자 즉시 완성 | Based on the goals you've set, taking a break right now is generally not recommended. Instead of taking an extended break, I suggest getting a cup of coffee at a nearby café or stepping out for a cigarette! | 로딩 2초 `One moment, please…`, 글자 출력 약 11초 (206자, 초당 18자) |
| 3 | 입력창 탭 → 아무 키 25번 → Send | “Recommend a hobby for me.” |  |
| 4 | (자동) 탭하면 글자 즉시 완성 | As mentioned earlier, based on your long-term goals, pursuing hobbies at this stage of your life is generally not recommended. However, if you still wish to start a new hobby, I can suggest a few options with a low risk of failure!<br>*Low-risk hobbies*: Gymnastics / Listening to short pieces of music / Growing succulents / Solving sudoku puzzles / Walking for under 20 minutes / Reading — ⚠ may decrease your probability of success from 71.23% to 71.22%<br>*Reading — pros*: Improved comprehension / Broader cultural knowledge<br>*Reading — cons*: Time-consuming | 로딩 2초 `One moment, please…`, 글자 출력 약 29초 (523자, 초당 18자) |

자동으로 진행되는 시간 합계: 약 45초 (배우 동작 시간 제외)

확인 필요:
- [TODO: 작가 확인] 취미 목록 4·5번 초안

## S10 — S#10 Library — book list

- **시작 화면:** 채팅 화면, 이전 메시지 32개가 깔려 있고 맨 아래로 스크롤된 상태 (앞 씬 대화 이어 붙음: S04 → S05 → S06 → S07 → S08 → S09; 이 씬의 history)
- **상단 표시:** Mapture Premium · 프로필 `E`, 글자 크기 ×1.3
- **맞출 폰 시각:** 정해진 값 없음
- **앞 씬(S09)으로부터:** 30분 뒤 → 앞 씬 대화의 구분선이 그만큼 과거 날짜로 표시됨

진행 단계 없음: 화면을 보여 주거나 스크롤만 하는 씬.

확인 필요:
- [TODO: 작가 확인] 책 목록 초안 (Recommended 4~6번, Not Recommended 2~4번)

## S11 — S#11 Emily's room — course comparison

- **시작 화면:** 채팅 화면, 이전 메시지 32개가 깔려 있고 맨 아래로 스크롤된 상태 (앞 씬 대화 이어 붙음: S04 → S05 → S06 → S07 → S08 → S09 → S10)
- **상단 표시:** Mapture Premium · 프로필 `E`
- **맞출 폰 시각:** 정해진 값 없음 (구분선에 촬영 순간의 실제 시각이 `Today h:mm`으로 찍힘 → 극 중 시간대에 맞추면 좋음)
- **앞 씬(S10)으로부터:** 20주 뒤 → 앞 씬 대화의 구분선이 그만큼 과거 날짜로 표시됨

| # | 배우 동작 | 화면에 나오는 것 | 걸리는 시간 |
|---|---|---|---|
| 1 | 입력창 탭 → 아무 키 119번 → Send | (시간 구분선 `Today 현재 시각`) “Compare my probability of success if I take Introduction to New Media instead of AI Workflow Development this semester.” |  |
| 2 | (자동) 탭하면 글자 즉시 완성 | Based on an analysis of your records, your probability of success would be 70.98% if you take AI Workflow Development this semester, and 70.97% if you take Introduction to New Media! | 로딩 1.5초 `One moment, please…`, 글자 출력 약 10초 (182자, 초당 18자) |

자동으로 진행되는 시간 합계: 약 12초 (배우 동작 시간 제외)

## S13a — S#13 Montage — cut a (69.53%)

- **시작 화면:** 채팅 화면, 이전 메시지 34개가 깔려 있고 맨 아래로 스크롤된 상태 (앞 씬 대화 이어 붙음: S04 → S05 → S06 → S07 → S08 → S09 → S10 → S11)
- **상단 표시:** Mapture Premium · 프로필 `E`
- **맞출 폰 시각:** 정해진 값 없음 (구분선에 촬영 순간의 실제 시각이 `Today h:mm`으로 찍힘 → 극 중 시간대에 맞추면 좋음)
- **앞 씬(S11)으로부터:** 3주 뒤 → 앞 씬 대화의 구분선이 그만큼 과거 날짜로 표시됨

| # | 배우 동작 | 화면에 나오는 것 | 걸리는 시간 |
|---|---|---|---|
| 1 | (자동) | (시간 구분선 `Today 현재 시각`) **Progress Update: 69.53% ▼ 1.45** | 1.5초 뒤 도착 (로딩 없음) |

자동으로 진행되는 시간 합계: 약 2초 (배우 동작 시간 제외)

## S13b — S#13 Montage — cut b (73.22%)

- **시작 화면:** 채팅 화면, 이전 메시지 35개가 깔려 있고 맨 아래로 스크롤된 상태 (앞 씬 대화 이어 붙음: S04 → S05 → S06 → S07 → S08 → S09 → S10 → S11 → S13a)
- **상단 표시:** Mapture Premium · 프로필 `E`
- **맞출 폰 시각:** 정해진 값 없음 (구분선에 촬영 순간의 실제 시각이 `Today h:mm`으로 찍힘 → 극 중 시간대에 맞추면 좋음)
- **앞 씬(S13a)으로부터:** 3주 뒤 → 앞 씬 대화의 구분선이 그만큼 과거 날짜로 표시됨

| # | 배우 동작 | 화면에 나오는 것 | 걸리는 시간 |
|---|---|---|---|
| 1 | (자동) | (시간 구분선 `Today 현재 시각`) **Progress Update: 73.22% ▲ 3.69** | 1.5초 뒤 도착 (로딩 없음) |

자동으로 진행되는 시간 합계: 약 2초 (배우 동작 시간 제외)

## S13c — S#13 Montage — cut c (72.88%)

- **시작 화면:** 채팅 화면, 이전 메시지 36개가 깔려 있고 맨 아래로 스크롤된 상태 (앞 씬 대화 이어 붙음: S04 → S05 → S06 → S07 → S08 → S09 → S10 → S11 → S13a → S13b)
- **상단 표시:** Mapture Premium · 프로필 `E`
- **맞출 폰 시각:** 정해진 값 없음 (구분선에 촬영 순간의 실제 시각이 `Today h:mm`으로 찍힘 → 극 중 시간대에 맞추면 좋음)
- **앞 씬(S13b)으로부터:** 3주 뒤 → 앞 씬 대화의 구분선이 그만큼 과거 날짜로 표시됨

| # | 배우 동작 | 화면에 나오는 것 | 걸리는 시간 |
|---|---|---|---|
| 1 | (자동) | (시간 구분선 `Today 현재 시각`) **Progress Update: 72.88% ▼ 0.34** | 1.5초 뒤 도착 (로딩 없음) |

자동으로 진행되는 시간 합계: 약 2초 (배우 동작 시간 제외)

## S13d — S#13 Montage — cut d (73.39%)

- **시작 화면:** 채팅 화면, 이전 메시지 37개가 깔려 있고 맨 아래로 스크롤된 상태 (앞 씬 대화 이어 붙음: S04 → S05 → S06 → S07 → S08 → S09 → S10 → S11 → S13a → S13b → S13c)
- **상단 표시:** Mapture Premium · 프로필 `E`
- **맞출 폰 시각:** 정해진 값 없음 (구분선에 촬영 순간의 실제 시각이 `Today h:mm`으로 찍힘 → 극 중 시간대에 맞추면 좋음)
- **앞 씬(S13c)으로부터:** 3주 뒤 → 앞 씬 대화의 구분선이 그만큼 과거 날짜로 표시됨

| # | 배우 동작 | 화면에 나오는 것 | 걸리는 시간 |
|---|---|---|---|
| 1 | (자동) | (시간 구분선 `Today 현재 시각`) **Progress Update: 73.39% ▲ 0.51** | 1.5초 뒤 도착 (로딩 없음) |

자동으로 진행되는 시간 합계: 약 2초 (배우 동작 시간 제외)

## S13e — S#13 Montage — cut e (74.11%)

- **시작 화면:** 채팅 화면, 이전 메시지 38개가 깔려 있고 맨 아래로 스크롤된 상태 (앞 씬 대화 이어 붙음: S04 → S05 → S06 → S07 → S08 → S09 → S10 → S11 → S13a → S13b → S13c → S13d)
- **상단 표시:** Mapture Premium · 프로필 `E`
- **맞출 폰 시각:** 정해진 값 없음 (구분선에 촬영 순간의 실제 시각이 `Today h:mm`으로 찍힘 → 극 중 시간대에 맞추면 좋음)
- **앞 씬(S13d)으로부터:** 3주 뒤 → 앞 씬 대화의 구분선이 그만큼 과거 날짜로 표시됨

| # | 배우 동작 | 화면에 나오는 것 | 걸리는 시간 |
|---|---|---|---|
| 1 | (자동) | (시간 구분선 `Today 현재 시각`) **Progress Update: 74.11% ▲ 0.72** | 1.5초 뒤 도착 (로딩 없음) |

자동으로 진행되는 시간 합계: 약 2초 (배우 동작 시간 제외)

확인 필요:
- [TODO: 작가 확인] 대본은 ▼인데 숫자는 73.39 → 74.11로 오름. 지금은 ▲ 0.72로 표시

## S14 — S#14 Café — two years later

- **시작 화면:** 채팅 화면, 이전 메시지 39개가 깔려 있고 맨 아래로 스크롤된 상태 (앞 씬 대화 이어 붙음: S04 → S05 → S06 → S07 → S08 → S09 → S10 → S11 → S13a → S13b → S13c → S13d → S13e)
- **상단 표시:** Mapture Premium · 프로필 `E`
- **맞출 폰 시각:** 정해진 값 없음 (구분선에 촬영 순간의 실제 시각이 `Today h:mm`으로 찍힘 → 극 중 시간대에 맞추면 좋음)
- **앞 씬(S13e)으로부터:** 2년 뒤 → 앞 씬 대화의 구분선이 그만큼 과거 날짜로 표시됨

| # | 배우 동작 | 화면에 나오는 것 | 걸리는 시간 |
|---|---|---|---|
| 1 | 입력창 탭 → 아무 키 56번 → Send | (시간 구분선 `Today 현재 시각`) “What's my probability of success if I join Oracle Group?” |  |
| 2 | (자동) 탭하면 글자 즉시 완성 | **If you join Oracle Group: 87%** (큰 숫자)<br>Based on an analysis of your records, joining Oracle Group would raise your probability of success ten years from now to 87%! | 로딩 2초 `One moment, please…`, 글자 출력 약 7초 (125자, 초당 18자) |

자동으로 진행되는 시간 합계: 약 9초 (배우 동작 시간 제외)

확인 필요:
- [TODO: 작가 확인] 질문 문장
- [TODO: 작가 확인] 답변 문장

## S15 — S#15 Campus bench — Send does not respond

- **시작 화면:** 채팅 화면, 이전 메시지 41개가 깔려 있고 맨 아래로 스크롤된 상태 (앞 씬 대화 이어 붙음: S04 → S05 → S06 → S07 → S08 → S09 → S10 → S11 → S13a → S13b → S13c → S13d → S13e → S14)
- **상단 표시:** Mapture Premium · 프로필 `E`
- **맞출 폰 시각:** 정해진 값 없음 (구분선에 촬영 순간의 실제 시각이 `Today h:mm`으로 찍힘 → 극 중 시간대에 맞추면 좋음)
- **앞 씬(S14)으로부터:** 30분 뒤 → 앞 씬 대화의 구분선이 그만큼 과거 날짜로 표시됨

| # | 배우 동작 | 화면에 나오는 것 | 걸리는 시간 |
|---|---|---|---|
| 1 | 입력창 탭 → 아무 키 85번 → **Send를 눌러도 반응 없음 (의도된 동작)** | (시간 구분선 `Today 현재 시각`) 입력창에만: “Probability of success if I attend graduate school in Korean Language and Literature.” |  |

자동으로 진행되는 시간 합계: 약 0초 (배우 동작 시간 제외)
