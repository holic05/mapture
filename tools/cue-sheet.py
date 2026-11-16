#!/usr/bin/env python3
"""씬별 촬영 큐시트를 scenes.json에서 뽑아 docs/cue-sheet.md 로 쓴다.

scenes.json을 고친 뒤 다시 실행하면 문서가 갱신된다.
사용: python3 tools/cue-sheet.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "cue-sheet.md")

# js/engine.js, js/views/*.js 의 기본값과 맞춰 둘 것
DEFAULT_LOADING_S = 2.0
PAUSE_BEFORE_LOADING_S = 0.35
PROGRESS_DELAY_S = 0.8
DEFAULT_TYPING_CPS = 18
DEFAULT_DOWNLOAD_S = 3
OPEN_MOTION_S = 2.0   # 카드 전환 0.56 + 마스코트 1.1 + 넘어가기 0.3
PAY_PROCESSING_S = 0.8

UNITS = {"m": "분", "h": "시간", "d": "일", "w": "주", "y": "년"}


def esc(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def gap_ko(gap):
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*([mhdwy])\s*", str(gap or ""))
    return f"{m.group(1)}{UNITS[m.group(2)]}" if m else "같은 시각"


def is_progress(step):
    return bool(step.get("headline")) and not step.get("body") and not step.get("list")


def lists_of(step):
    lst = step.get("list") or []
    return lst if isinstance(lst, list) else [lst]


def typed_chars(step):
    body = step.get("body") or ""
    n = len(body if isinstance(body, str) else "".join(body))
    for lst in lists_of(step):
        n += len(lst.get("title", "")) + sum(len(str(i)) for i in lst.get("items", []))
    return n


def chain_of(scene, by_id):
    out, seen, s = [], {scene["id"]}, scene
    while s.get("after") and s["after"] in by_id and s["after"] not in seen:
        s = by_id[s["after"]]
        seen.add(s["id"])
        out.insert(0, s)
    return out


def message_count(scene):
    return sum(1 for st in (scene.get("history") or []) + (scene.get("steps") or [])
               if st["type"] != "divider" and not st.get("sendDisabled"))


def mapture_row(step):
    """(화면에 나오는 것, 걸리는 시간 초, 설명)"""
    parts, secs, how = [], 0.0, []
    if is_progress(step) and not step.get("loading"):
        delay = step.get("delay", PROGRESS_DELAY_S)
        secs += delay
        how.append(f"{delay:g}초 뒤 도착 (로딩 없음)")
    else:
        if step.get("delay"):
            secs += step["delay"]
        ld = step.get("loading") or {}
        ls = ld.get("seconds", DEFAULT_LOADING_S)
        secs += PAUSE_BEFORE_LOADING_S + ls
        how.append(f"로딩 {ls:g}초 `{ld.get('text', 'One moment, please…')}`" + (" + 진행 바" if ld.get("progressBar") else ""))
    hl = step.get("headline")
    if hl:
        arrow = ""
        if isinstance(hl.get("up"), bool) or hl.get("delta"):
            arrow = (" ▲" if hl.get("up") else " ▼") + (f" {hl['delta']}" if hl.get("delta") else "")
        size = " (큰 숫자)" if hl.get("size") == "huge" else ""
        parts.append(f"**{esc(hl.get('label') or 'Progress Update')}: {esc(hl.get('value', ''))}{arrow}**{size}")
    if step.get("body"):
        body = step["body"] if isinstance(step["body"], str) else " ".join(step["body"])
        parts.append(esc(body))
    for lst in lists_of(step):
        parts.append(f"*{esc(lst.get('title', ''))}*: " + " / ".join(esc(i) for i in lst.get("items", [])))
    if step.get("disclaimer"):
        parts.append(f"<sub>{esc(step['disclaimer'])}</sub>")
    if step.get("button"):
        parts.append(f"[버튼: {esc(step['button'].get('label', ''))}]")
    if step.get("report"):
        parts.append("[링크: Detailed Analysis Report ›]")
    chars = typed_chars(step)
    if chars:
        cps = step.get("typingSpeed") or DEFAULT_TYPING_CPS
        t = chars / cps
        secs += t
        how.append(f"글자 출력 약 {t:.0f}초 ({chars}자, 초당 {cps:g}자)")
    return "<br>".join(parts), secs, ", ".join(how)


def scene_section(scene, by_id):
    out = []
    steps = scene.get("steps") or []
    chain = chain_of(scene, by_id)
    start = scene.get("start", "chat")
    out.append(f"## {scene['id']} — {scene.get('title', '')}\n")

    # 시작 화면
    if start == "download":
        screen = "스토어(다운로드) 화면"
    elif start == "paywall":
        screen = "결제 화면 (닫거나 결제하면 아래의 채팅 화면)"
    else:
        screen = "채팅 화면"
    prior = sum(message_count(s) for s in chain) + sum(1 for st in scene.get("history") or [] if st["type"] != "divider")
    if prior:
        src = []
        if chain:
            src.append("앞 씬 대화 이어 붙음: " + " → ".join(s["id"] for s in chain))
        if scene.get("history"):
            src.append("이 씬의 history")
        under = f"이전 메시지 {prior}개가 깔려 있고 맨 아래로 스크롤된 상태 ({'; '.join(src)})"
    else:
        under = "빈 인사 화면 (`Hello, user!`)"
    out.append(f"- **시작 화면:** {screen}" + (f" → {under}" if start != "chat" else f", {under}"))
    scale = f", 글자 크기 ×{scene['textScale']:g}" if scene.get("textScale", 1) != 1 else ""
    out.append(f"- **상단 표시:** Mapture {scene.get('plan', 'Free')} · 프로필 `{scene.get('profile', 'E')}`{scale}")
    if scene.get("phoneTime"):
        out.append(f"- **맞출 폰 시각:** **{scene['phoneTime']}** (대사 속 시각과 맞추기 위해)")
    else:
        shows = any(st["type"] == "divider" and st.get("time") == "now" for st in steps)
        out.append("- **맞출 폰 시각:** 정해진 값 없음" + (" (구분선에 촬영 순간의 실제 시각이 `Today h:mm`으로 찍힘 → 극 중 시간대에 맞추면 좋음)" if shows else ""))
    if chain:
        out.append(f"- **앞 씬({chain[-1]['id']})으로부터:** {gap_ko(scene.get('gap'))} 뒤 → 앞 씬 대화의 구분선이 그만큼 과거 날짜로 표시됨")

    # 단계
    rows, total, n = [], 0.0, 0
    if start == "download":
        ds = scene.get("downloadSeconds", DEFAULT_DOWNLOAD_S)
        n += 1; rows.append((n, "`Download` 탭", f"진행 바가 {ds:g}초 동안 참 → 버튼이 `Open`으로", f"{ds:g}초"))
        n += 1; rows.append((n, "`Open` 탭", "스토어 카드가 왼쪽으로 밀려 나가고 맵쳐 카드가 들어와 커짐 → 마스코트 → 인사 화면", f"약 {OPEN_MOTION_S:g}초"))
        total += ds + OPEN_MOTION_S
    if start == "paywall":
        n += 1; rows.append((n, "요금 카드 탭해 선택 (기본: One-Year)", "`Mapture Premium` 결제 화면, 버튼 `Subscribe for ₩250,000` / `₩22,900`", ""))
        n += 1; rows.append((n, "`Subscribe for …` 탭", "버튼 안 스피너 → `Welcome to Premium` / `Payment complete · ₩…`", f"{PAY_PROCESSING_S:g}초"))
        n += 1; rows.append((n, "`Start predicting` 탭", "채팅 화면, 상단 플랜이 `Premium`으로", ""))
        total += PAY_PROCESSING_S

    divider_pending = False
    voice_on = False
    for st in steps:
        if st["type"] == "divider":
            divider_pending = True
            continue
        div = "(시간 구분선 `Today 현재 시각`) " if divider_pending else ""
        divider_pending = False
        if st["type"] == "user":
            if st.get("input") == "voice":
                auto = st.get("autoSubmit")
                enter = "알약 탭(다시 `Listening…`) → " if voice_on else "마이크 탭(음성 모드, `Listening…`) → "
                send = f"화면 아무 곳 탭, 또는 {auto:g}초 뒤 자동" if auto else "화면 아무 곳 탭"
                action = f"{enter}대사를 말함 → {send}"
                voice_on = True
            else:
                chars = len(st["text"])
                action = f"입력창 탭 → 아무 키 {chars}번 → "
                action += "**Send를 눌러도 반응 없음 (의도된 동작)**" if st.get("sendDisabled") else "Send"
                voice_on = False
            n += 1
            shown = "입력창에만: " if st.get("sendDisabled") else ("🎤 " if st.get("input") == "voice" else "")
            rows.append((n, action, f"{div}{shown}“{esc(st['text'])}”", ""))
        else:
            shown, secs, how = mapture_row(st)
            total += secs
            n += 1
            rows.append((n, "(자동) 탭하면 글자 즉시 완성" if typed_chars(st) else "(자동)", f"{div}{shown}", how))
            if (st.get("button") or {}).get("action") == "paywall":
                n += 1; rows.append((n, f"`{esc(st['button'].get('label', ''))}` 탭", "결제 화면 → 결제하면 같은 대화로 돌아오고 플랜이 `Premium`", ""))
    if rows:
        out.append("")
        out.append("| # | 배우 동작 | 화면에 나오는 것 | 걸리는 시간 |")
        out.append("|---|---|---|---|")
        out.extend(f"| {i} | {a} | {b} | {c} |" for i, a, b, c in rows)
        out.append("")
        out.append(f"자동으로 진행되는 시간 합계: 약 {total:.0f}초 (배우 동작 시간 제외)")
    else:
        out.append("\n진행 단계 없음: 화면을 보여 주거나 스크롤만 하는 씬.")

    notes = [st["note"] for st in (scene.get("history") or []) + steps if "TODO" in str(st.get("note", ""))]
    if notes:
        out.append("\n확인 필요:")
        out.extend(f"- {esc(x)}" for x in dict.fromkeys(notes))
    return "\n".join(out) + "\n"


def main():
    with open(os.path.join(ROOT, "scenes.json"), encoding="utf-8") as f:
        data = json.load(f)
    by_id = {s["id"]: s for s in data["scenes"]}
    doc = ["# Mapture 촬영 큐시트", "",
           "> 이 문서는 `python3 tools/cue-sheet.py`가 `scenes.json`에서 자동으로 만듭니다. 직접 고치지 말고 `scenes.json`을 고친 뒤 다시 실행하세요.", "",
           "## 촬영 전 공통 준비", "",
           "- 홈 화면의 **Mapture 아이콘**으로 실행 (주소창이 없어야 함). 촬영 전 Wi-Fi가 되는 곳에서 한 번 열어 최신 내용을 받아 둘 것",
           "- **방해 금지 모드** 켜기 (알림·전화가 화면에 뜨지 않게), 화면 밝기 고정, 배터리 절약 모드 끄기",
           "- 화면 자동 회전 끄기 (앱도 세로로 고정되어 있음)",
           "- 키보드는 한글·영어 아무거나 가능. 타이핑 씬에서는 **아무 키나** 누르면 정해진 문장이 써짐",
           "- **씬 고르기:** 왼쪽 위 ☰ 를 0.6초 길게 누름 → 목록에서 선택. 같은 씬을 다시 고르면 처음 상태로 리셋 (재촬영)",
           "  - 스토어·결제·리포트 화면에서는 왼쪽 위 버튼(뒤로/닫기)을 길게 누름",
           "- 폰 시각을 맞춰야 하는 씬은 설정 → 날짜 및 시간 → 자동 설정 끄고 직접 입력 (촬영 후 되돌리기)",
           "- 시간 구분선과 리포트의 시각은 **촬영 순간의 폰 시각**으로 찍힘",
           "", "## 씬 목록", "",
           "| 씬 | 시작 화면 | 플랜 | 질문 방식 | 폰 시각 |", "|---|---|---|---|---|"]
    for s in data["scenes"]:
        kinds = sorted({("음성" if st.get("input") == "voice" else "타이핑") for st in s.get("steps") or [] if st["type"] == "user"})
        start = {"download": "스토어", "paywall": "결제"}.get(s.get("start"), "채팅")
        doc.append(f"| {s['id']} {s.get('title', '')} | {start} | {s.get('plan', 'Free')} | {' + '.join(kinds) or '없음'} | {s.get('phoneTime', '—')} |")
    doc.append("")
    for s in data["scenes"]:
        doc.append(scene_section(s, by_id))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(doc))
    print("wrote", OUT, f"({len(data['scenes'])} scenes)")


if __name__ == "__main__":
    main()
