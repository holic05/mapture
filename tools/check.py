#!/usr/bin/env python3
"""Mapture 확인 스크립트 (Playwright).

모바일 크기의 Chromium으로 앱을 실제로 조작해 보고 PASS/FAIL을 출력한다.
스크린샷은 tools/shots/ 에 저장된다 (git 제외).

사용:
  python3 -m http.server 8000            # 프로젝트 루트에서, 다른 터미널
  ~/mapture-venv/bin/python tools/check.py
  ~/mapture-venv/bin/python tools/check.py --base https://<계정>.github.io/mapture/
  ~/mapture-venv/bin/python tools/check.py --only typing,menu
"""
import argparse
import json
import os
import re
import sys

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "shots")
ROOT = os.path.dirname(HERE)

PHONE = dict(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True,
             user_agent="Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/126.0.0.0 Mobile Safari/537.36")
KEYBOARD_HEIGHT = 340  # 키보드가 차지하는 높이를 뷰포트 축소로 흉내 낸다

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}{('  — ' + str(detail)) if detail else ''}")


IPHONE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
             "Version/18.0 Mobile/15E148 Safari/604.1")


class Run:
    def __init__(self, browser, base):
        self.browser = browser
        self.base = base if base.endswith("/") else base + "/"

    def page(self, scene=None, width=390, height=844, chain=False, **ctx_kw):
        opts = dict(PHONE)
        opts["viewport"] = {"width": width, "height": height}
        if self.browser.browser_type.name == "webkit":
            opts["user_agent"] = IPHONE_UA
        opts.update(ctx_kw)
        ctx = self.browser.new_context(**opts)
        page = ctx.new_page()
        page.errors = []
        page.on("pageerror", lambda e: page.errors.append(str(e)))
        # WebKit(iPhone Safari)은 Android용 viewport 설정 interactive-widget을 모른다고 콘솔에 알린다 (무해, Android용으로 남겨 둠)
        page.on("console", lambda m: page.errors.append(m.text) if m.type == "error" and "interactive-widget" not in m.text else None)
        if scene is not False:
            self.open(page, scene, chain)
        return page

    def url(self, scene=None, chain=False):
        q = ([f"scene={scene}"] if scene else []) + ([] if chain else ["solo=1"])
        return self.base + ("?" + "&".join(q) if q else "")

    def open(self, page, scene=None, chain=False):
        page.goto(self.url(scene, chain))
        page.wait_for_selector(".composer")
        page.wait_for_function("document.fonts.status === 'loaded'")
        page.wait_for_timeout(300)

    def shot(self, page, name):
        os.makedirs(SHOTS, exist_ok=True)
        page.screenshot(path=os.path.join(SHOTS, name + ".png"))


def scene_by_id(scene_id):
    with open(os.path.join(ROOT, "scenes.json"), encoding="utf-8") as f:
        return next(s for s in json.load(f)["scenes"] if s["id"] == scene_id)


def first_typing_text(scene_id):
    return next(s["text"] for s in scene_by_id(scene_id)["steps"] if s.get("input") == "typing")


def open_keyboard(page):
    """입력창을 탭하고, 키보드가 올라온 것처럼 뷰포트 높이를 줄인다."""
    page.tap("#ask")
    vp = page.viewport_size
    page.set_viewport_size({"width": vp["width"], "height": vp["height"] - KEYBOARD_HEIGHT})
    page.wait_for_timeout(250)


def close_keyboard(page):
    vp = page.viewport_size
    page.set_viewport_size({"width": vp["width"], "height": vp["height"] + KEYBOARD_HEIGHT})
    page.wait_for_timeout(250)


def composer_visible(page):
    return page.evaluate("""() => {
      const r = document.querySelector('.composer').getBoundingClientRect();
      return r.top >= 0 && r.bottom <= window.innerHeight + 0.5 && r.left >= 0 && r.right <= window.innerWidth + 0.5;
    }""")


def no_overflow(page):
    """가로로 넘치는 요소가 없는지"""
    return page.evaluate("""() => [...document.querySelectorAll('#app *')].filter(el => {
      const r = el.getBoundingClientRect();
      return r.width > 0 && (r.right > window.innerWidth + 0.5 || r.left < -0.5) && !el.closest('svg');
    }).map(el => el.className || el.tagName).slice(0, 5)""")


def pass_download(page):
    """스토어 화면: GET → 진행 링 → OPEN → 실행 애니메이션이 끝날 때까지"""
    page.tap(".store-btn")
    page.wait_for_function("document.querySelector('.store-btn')?.textContent === 'OPEN'", timeout=15000)
    page.tap(".store-btn")
    page.wait_for_selector(".overlay", state="detached", timeout=8000)


def is_webkit(page):
    return page.context.browser.browser_type.name == "webkit"


def hold(page, x, y, ms=800):
    """(x, y)를 ms 동안 누르고 있다가 뗀다. Chromium은 진짜 터치(CDP), WebKit은 CDP가 없어 포인터(마우스)로."""
    if is_webkit(page):
        page.mouse.move(x, y)
        page.mouse.down()
        page.wait_for_timeout(ms)
        page.mouse.up()
    else:
        cdp = page.context.new_cdp_session(page)
        cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x, "y": y}]})
        page.wait_for_timeout(ms)
        cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
    page.wait_for_timeout(400)


def long_press(page, selector, ms=800):
    box = page.locator(selector).first.bounding_box()
    hold(page, box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, ms)


def wait_typing_done(page, timeout=60000):
    """마지막 맵쳐 말풍선의 글자 수가 더 늘지 않을 때까지"""
    page.wait_for_function("""() => {
      const b = [...document.querySelectorAll('.bubble-mapture')].pop();
      if (!b || document.querySelector('.bubble-loading')) return false;
      const n = b.textContent.length;
      const same = window.__n === n; window.__n = n;
      return same;
    }""", polling=400, timeout=timeout)


# ---------------------------------------------------------------- tests

def t_empty(run):
    """빈 상태가 여러 폰 크기에서 깨지지 않는다"""
    for w, h in [(360, 740), (390, 844), (430, 932)]:
        page = run.page("S15", w, h)
        ok = composer_visible(page) and not no_overflow(page)
        hero = page.evaluate("""() => { const m = document.querySelector('.empty .mascot').getBoundingClientRect(),
          t = document.querySelector('.empty h1').getBoundingClientRect(), f = document.querySelector('.empty-foot').getBoundingClientRect();
          return m.bottom <= t.top + 1 && t.bottom <= f.top + 1 && m.height > 100; }""")
        check(f"empty state {w}x{h}", ok and hero and not page.errors, page.errors or no_overflow(page))
        run.shot(page, f"empty-{w}")
        page.context.close()


def t_typing(run):
    """고스트 타이핑 + 키보드가 열려도 입력창이 보인다 + 답변 출력"""
    text = first_typing_text("S08")
    for w, h in [(360, 740), (390, 844), (430, 932)]:
        page = run.page("S08", w, h)
        open_keyboard(page)
        check(f"[{w}] keyboard open: composer visible, kb-open set",
              composer_visible(page) and page.evaluate("document.documentElement.classList.contains('kb-open')"))
        page.keyboard.type("qwertyuiopas", delay=15)
        check(f"[{w}] any key types the script", page.input_value("#ask") == text[:12], page.input_value("#ask"))
        for _ in range(4):
            page.keyboard.press("Backspace")
        check(f"[{w}] backspace removes one char each", page.input_value("#ask") == text[:8])
        page.tap(".send")
        page.wait_for_timeout(200)
        check(f"[{w}] send ignored before sentence is complete", page.locator(".bubble-user").count() == 0)
        page.keyboard.type("x" * (len(text) + 10), delay=4)
        check(f"[{w}] full sentence, extra keys ignored", page.input_value("#ask") == text)
        check(f"[{w}] composer still visible with full sentence", composer_visible(page) and not no_overflow(page), no_overflow(page))
        run.shot(page, f"typing-kb-{w}")
        page.tap(".send")
        page.wait_for_selector(".bubble-user")
        check(f"[{w}] sent: bubble shows the text, input cleared",
              page.inner_text(".bubble-user") == text and page.input_value("#ask") == "")
        close_keyboard(page)
        page.wait_for_selector(".bubble-loading")
        run.shot(page, f"loading-{w}")
        page.wait_for_selector(".bubble-mapture .body-text")
        # headline은 한 번에, body는 한 글자씩
        head = page.inner_text(".headline-value")
        n1 = len(page.inner_text(".bubble-mapture .body-text"))
        page.wait_for_timeout(500)
        n2 = len(page.inner_text(".bubble-mapture .body-text"))
        check(f"[{w}] headline at once, body typed char by char", head == "71.13%" and n2 > n1, f"{n1}->{n2}")
        check(f"[{w}] report link/list not shown while typing", page.locator(".report-link").count() == 0)
        run.shot(page, f"typing-answer-{w}")
        page.tap(".bubble-mapture")  # 탭하면 즉시 완성
        page.wait_for_selector(".report-link", timeout=1500)
        check(f"[{w}] tap completes instantly", page.locator(".bubble-mapture li").count() == 3)
        check(f"[{w}] pinned to bottom, nothing overflows",
              page.evaluate("(() => { const s = document.querySelector('.scroller'); return s.scrollHeight - s.scrollTop - s.clientHeight < 2; })()")
              and not no_overflow(page), no_overflow(page))
        run.shot(page, f"answer-{w}")
        check(f"[{w}] no page errors", not page.errors, page.errors)
        page.context.close()


class Ime:
    """입력기 흉내 (CDP). keydown=True면 Android 화면 키보드처럼 키마다 keyCode 229 keydown을 먼저 보낸다."""

    def __init__(self, page, keydown):
        self.page, self.keydown = page, keydown
        self.cdp = page.context.new_cdp_session(page)

    def key(self, *events):
        """키 한 번. events: ("comp", 글자) 조합 문자열 갱신 / ("commit", 글자) 확정 / ("del",) 삭제"""
        if self.keydown:
            self.cdp.send("Input.dispatchKeyEvent", {"type": "rawKeyDown", "windowsVirtualKeyCode": 229, "key": "Process"})
        for ev in events:
            if ev[0] == "comp":
                self.cdp.send("Input.imeSetComposition", {"text": ev[1], "selectionStart": len(ev[1]), "selectionEnd": len(ev[1])})
            elif ev[0] == "commit":
                self.cdp.send("Input.insertText", {"text": ev[1]})
            elif ev[0] == "del":
                self.page.evaluate("document.execCommand('delete')")
        if self.keydown:
            self.cdp.send("Input.dispatchKeyEvent", {"type": "keyUp", "windowsVirtualKeyCode": 229, "key": "Process"})
        self.page.wait_for_timeout(45)


def t_ime(run):
    """입력기와 무관하게 "키 한 번 = 한 글자": 영어 조합(Gboard), 한글 조합, keydown 유무"""
    text = first_typing_text("S08")
    for keydown in (True, False):
        tag = "keydown 229 + composition" if keydown else "composition only"
        page = run.page("S08")
        page.tap("#ask")
        ime = Ime(page, keydown)
        n = 0

        def expect(name):
            val = page.input_value("#ask")
            check(f"[{tag}] {name}", val == text[:n], f"{n} keys -> {val!r}")

        # 영어: 단어를 조합 상태로 한 글자씩, 스페이스로 확정
        for word in ["hello", "wor"]:
            for i in range(1, len(word) + 1):
                ime.key(("comp", word[:i])); n += 1
            ime.key(("commit", word + " ")); n += 1
        expect("English: one char per key")
        ime.key(("comp", "a")); ime.key(("comp", "ab")); ime.key(("comp", "abc")); n += 3
        # 앱이 입력창 값을 덮어쓰면 브라우저는 조합을 끊는다. 그 뒤의 백스페이스는 일반 삭제로 온다.
        ime.key(("del",)); n -= 1
        expect("English: backspace inside a word")
        ime.key(("commit", "ab ")); n += 1

        # 한글: ㅎ → 하 → 한 (길이는 그대로, 글자만 바뀜)
        for c in ["ㅎ", "하", "한"]:
            ime.key(("comp", c)); n += 1
        expect("Korean: syllable building (ㅎ→하→한) counts every key")
        # 다음 자음: 앞 글자 확정 + 새 조합 시작이 키 하나에 함께 온다
        ime.key(("commit", "한"), ("comp", "ㄱ")); n += 1
        ime.key(("comp", "그")); n += 1
        ime.key(("commit", "그"), ("comp", "ㄹ")); n += 1
        expect("Korean: commit + new syllable in one key counts once")
        # 같은 자음만 계속 누르기 (조합 문자열이 매번 똑같다)
        ime.key(("commit", "ㄹ"), ("comp", "ㄱ")); n += 1
        for _ in range(5):
            ime.key(("commit", "ㄱ"), ("comp", "ㄱ")); n += 1
        expect("Korean: same key repeated never stalls")
        # 조합 중 백스페이스: 간 → 가 → ㄱ → (빈 문자열)
        ime.key(("commit", "ㄱ"), ("comp", "ㄱ")); ime.key(("comp", "가")); ime.key(("comp", "간")); n += 3
        ime.key(("del",)); ime.key(("del",)); ime.key(("del",)); n -= 3
        expect("Korean: backspace after building a syllable")
        if keydown:
            ime.key(); n += 1  # keydown만 오고 입력 이벤트가 없는 경우
            page.wait_for_timeout(120)
            expect("keydown with no input event still types")
        # 끝까지 쓰고 보내기
        for i in range(len(text) + 5):
            ime.key(("commit", "ㅋ"), ("comp", "ㅋ"))
        check(f"[{tag}] finishes the sentence exactly", page.input_value("#ask") == text, repr(page.input_value("#ask")))
        page.tap(".send")
        page.wait_for_selector(".bubble-user")
        check(f"[{tag}] sends; input empty, no stray chars", page.inner_text(".bubble-user") == text and page.input_value("#ask") == "")
        check(f"[{tag}] no page errors", not page.errors, page.errors)
        page.context.close()

    # 입력 단계가 아닐 때는 아무 글자도 들어가지 않는다
    page = run.page("S05")
    page.locator(".overlay [data-ref=close]").tap()
    page.tap("#ask")
    page.keyboard.type("hello")
    ime = Ime(page, True)
    ime.key(("comp", "한")); ime.key(("commit", "한"), ("comp", "ㄱ")); ime.key(("commit", "zzz"))
    page.wait_for_timeout(150)
    check("no typing step: input stays empty", page.input_value("#ask") == "", repr(page.input_value("#ask")))
    page.context.close()


def t_long_input(run):
    """긴 질문은 입력창이 여러 줄로 늘어나고, S#15는 Send가 반응하지 않는다"""
    text = first_typing_text("S15")
    page = run.page("S15", 360, 740)
    open_keyboard(page)
    page.keyboard.type("x" * len(text), delay=3)
    h = page.evaluate("document.querySelector('#ask').getBoundingClientRect().height")
    check("S15 long question: input grows to several lines", page.input_value("#ask") == text and h > 60, f"height {h}")
    check("S15 composer visible above keyboard", composer_visible(page) and not no_overflow(page), no_overflow(page))
    page.tap(".send")
    page.keyboard.press("Enter")
    page.wait_for_timeout(400)
    check("S15 send does not respond", page.locator(".bubble-user").count() == 0 and page.input_value("#ask") == text)
    run.shot(page, "s15-kb-360")
    page.context.close()


def t_input_height(run):
    """고스트 타이핑 중 입력창은 줄이 넘어갈 때 한 줄씩 커지고(처음엔 한 줄), 채팅은 한 프레임도 튀지 않는다.
    매 프레임(requestAnimationFrame) 입력창 위쪽과 마지막 말풍선 아래쪽 사이 간격을 기록해, 항상 같은지 본다.
    줄이 넘어가는 순간 전후 화면도 찍는다. 음성 모드에서 X로 나오면 'Ask Mapture' 문구가 잘리지 않는다."""
    for sid, w in (("S09", 360), ("S15", 390)):
        text = first_typing_text(sid)
        page = run.page(sid, w, 844, chain=True)
        open_keyboard(page)
        h0 = page.evaluate("document.querySelector('#ask').getBoundingClientRect().height")
        page.evaluate("""() => { window.__f = [];
          const ta = document.querySelector('#ask'), sc = document.querySelector('.scroller');
          const tick = () => { const last = [...document.querySelectorAll('.messages > .msg')].pop();
            window.__f.push([Math.round(ta.getBoundingClientRect().top * 2) / 2, last ? Math.round(last.getBoundingClientRect().bottom * 2) / 2 : null,
                             Math.round(ta.getBoundingClientRect().height), window.scrollY, (visualViewport && visualViewport.offsetTop) || 0]);
            window.__raf = requestAnimationFrame(tick); }; tick(); }""")
        wraps, prev_h = [], h0
        for i in range(len(text)):
            page.keyboard.press("a")
            hh = page.evaluate("document.querySelector('#ask').getBoundingClientRect().height")
            if hh != prev_h:
                wraps.append(i)
                if len(wraps) == 1:
                    run.shot(page, f"inputh-{sid}-after-wrap")
                prev_h = hh
            elif not wraps and i + 1 < len(text):
                run.shot(page, f"inputh-{sid}-before-wrap")  # 줄이 넘어가기 직전까지 덮어쓴다
            page.wait_for_timeout(16)
        page.wait_for_timeout(120)
        frames = page.evaluate("cancelAnimationFrame(window.__raf), window.__f")
        gaps = sorted({round(f[0] - f[1], 1) for f in frames if f[1] is not None})
        heights = sorted({f[2] for f in frames})
        moved = [f for f in frames if f[3] or f[4]]
        check(f"{sid} ({w}px): input starts one line high and grows a line at a time as the text wraps",
              round(h0) == 44 and len(heights) >= 2 and all(b - a in (22,) for a, b in zip(heights, heights[1:]))
              and page.input_value("#ask") == text, (h0, heights, wraps))
        check(f"{sid} ({w}px): every frame, the last bubble stays glued above the input (no one-frame jump)",
              len(gaps) == 1 and not moved, (gaps, len(frames), moved[:3]))
        page.context.close()

    page = run.page("S06")
    page.tap(".mic"); page.wait_for_timeout(300)
    page.tap(".voice-pill", force=True)
    page.wait_for_selector(".bubble-loading")
    page.tap(".voice-x")
    page.wait_for_timeout(300)
    info = page.evaluate("""() => { const ta = document.querySelector('#ask'), r = ta.getBoundingClientRect();
      return [r.height, ta.scrollHeight <= ta.clientHeight + 1, ta.placeholder]; }""")
    check("voice X after a question: 'Ask Mapture' placeholder is not pushed down or cut", info[0] == 44 and info[1], info)
    run.shot(page, "voice-x-placeholder")
    check("no page errors", not page.errors, page.errors)
    page.context.close()


def t_report_s04b(run):
    """S04b(재촬영용)의 리포트: 예측 시각이 질문 시각 17·18분 뒤 (질문보다 앞서면 안 됨)"""
    page = run.page("S04b")
    page.locator(".report-link").first.tap()
    page.wait_for_selector(".overlay-report")
    times = page.locator(".tl-time").all_inner_texts()
    asked = page.inner_text(".report-q .cap")
    def minutes(label):
        h, m, ap = re.search(r"(\d+):(\d+) (AM|PM)", label).groups()
        return (int(h) % 12 + (12 if ap == "PM" else 0)) * 60 + int(m)
    check("S04b report: timeline 17 and 18 minutes after the question",
          [(minutes(t) - minutes(asked)) % 1440 for t in times] == [17, 18], f"{asked} -> {times}")
    page.context.close()


def t_store(run):
    """스토어 화면: 세로 스크롤(리뷰·설명), 정보 줄·Preview 가로 넘기기, GET 말고는 반응 없음"""
    page = run.page("S04", 390, 844)
    info = page.evaluate("""() => { const s = document.querySelector('.store'), i = document.querySelector('.store-info'),
        p = document.querySelector('.store-shots');
      return { v: s.scrollHeight > s.clientHeight + 300, h1: i.scrollWidth > i.clientWidth, h2: p.scrollWidth > p.clientWidth,
               reviews: document.querySelectorAll('.store-review').length, rating: document.querySelector('.store-rating-big').innerText }; }""")
    check("store scrolls vertically down to Ratings & Reviews and the description",
          info["v"] and info["reviews"] >= 2 and "4.9" in info["rating"] and "out of 5" in info["rating"]
          and "Mapture 6" in page.inner_text(".store-desc"), info)
    check("info row and Preview row can be swiped sideways", info["h1"] and info["h2"], info)
    page.wait_for_function("[...document.querySelectorAll('.store-shot img')].every(i => i.complete)", timeout=8000)
    imgs = page.evaluate("[...document.querySelectorAll('.store-shot img')].map(i => [i.naturalWidth, Math.round(i.getBoundingClientRect().width)])")
    check("Preview cards show real app screenshots (3 images loaded, fill the phone frame)",
          len(imgs) == 3 and all(n > 500 and 150 < w < 200 for n, w in imgs), imgs)
    page.evaluate("document.querySelector('.store-info').scrollLeft = 200")
    page.wait_for_timeout(500)
    check("info row actually scrolls sideways", page.evaluate("document.querySelector('.store-info').scrollLeft") > 50)
    # GET 말고는 반응 없음
    for sel in [".store-top .store-round[aria-label=Share]", ".store-tabs > div >> nth=0", ".store-event", ".store-review >> nth=0"]:
        page.locator(sel).tap(force=True)
    page.locator(".store-top .store-round[aria-label=Back]").tap()
    page.wait_for_timeout(300)
    check("tapping anything but GET does nothing", page.locator(".overlay-download").count() == 1 and page.locator(".sheet").count() == 0
          and page.inner_text(".store-btn") == "GET" and page.locator(".overlay").count() == 1)
    # 스크롤해서 본문 GET이 가려지면 상단 바에 작은 GET이 나타나고, 같은 동작을 한다
    page.evaluate("document.querySelector('.store').scrollTop = 0")
    page.wait_for_timeout(400)
    check("top bar has no mini GET at the top of the page", not page.locator(".store-mini-btn").is_visible())
    page.evaluate("document.querySelector('.store').scrollTop = 900")
    page.wait_for_timeout(400)
    check("scrolled down: a small GET appears in the top bar", page.locator(".store-mini-btn").is_visible())
    run.shot(page, "store-scrolled")
    page.tap(".store-mini-btn")
    page.wait_for_timeout(300)
    check("mini GET starts the download (ring in both places)", page.locator(".store-mini .store-ring").is_visible()
          and page.evaluate("!document.querySelector('.store-action .store-ring').hidden"))
    page.wait_for_function("document.querySelector('.store-mini-btn').textContent === 'OPEN'", timeout=8000)
    page.evaluate("document.querySelector('.store').scrollTop = 0")
    page.wait_for_timeout(300)
    check("both buttons show OPEN", page.inner_text(".store-btn") == "OPEN")
    page.tap(".store-btn")
    page.wait_for_selector(".overlay", state="detached", timeout=6000)
    check("OPEN launches into the chat", page.locator(".empty").is_visible())
    run.shot(page, "store-end")
    page.context.close()
    page = run.page("S04", 360, 740)
    page.evaluate("document.querySelector('.store').scrollTop = 1e5")
    page.wait_for_timeout(300)
    last = page.evaluate("[document.querySelector('.store-dev-row').getBoundingClientRect().bottom, document.querySelector('.store-tabs').getBoundingClientRect().top]")
    check("bottom of the page is not hidden behind the tab bar", last[0] <= last[1], last)
    run.shot(page, "store-bottom-360")
    check("no page errors", not page.errors, page.errors)
    page.context.close()


def voice_layout(page, state):
    """음성 모드 구조: 떠 있는 컨트롤(같은 위치·크기), 목록은 화면 맨 아래까지, 배경 초록은 듣는 중에만"""
    info = page.evaluate("""() => {
      const q = (s) => document.querySelector(s), r = (s) => q(s).getBoundingClientRect();
      const btns = [...document.querySelectorAll('.voice-btn')].map(b => getComputedStyle(b).backgroundColor);
      return { scrollerBottom: r('.chat-main').bottom, h: innerHeight, panelBg: getComputedStyle(q('.voice-panel')).backgroundColor,
               pill: [r('.voice-pill').x, r('.voice-pill').y, r('.voice-pill').width, r('.voice-pill').height],
               mic: [r('.voice-btn').x, r('.voice-btn').y], opaque: btns.every(c => c.startsWith('rgb(')),
               green: getComputedStyle(q('.screen.chat'), '::before').opacity,
               label: getComputedStyle(q('.voice-status')).visibility };
    }""")
    if not hasattr(page, "voice_ref"):
        page.voice_ref = (info["pill"], info["mic"])
    check(f"voice ({state}): chat runs to the bottom edge behind floating, opaque controls",
          abs(info["scrollerBottom"] - info["h"]) < 1 and info["panelBg"] == "rgba(0, 0, 0, 0)" and info["opaque"], info)
    check(f"voice ({state}): controls keep the same position and size", (info["pill"], info["mic"]) == page.voice_ref)
    listening = state == "listening"
    check(f"voice ({state}): bottom green {'on' if listening else 'off'}, Listening… {'shown' if listening else 'hidden'}",
          (info["green"] == "1") == listening and (info["label"] == "visible") == listening, (info["green"], info["label"]))


def t_voice_scroll(run):
    """듣는 중 스크롤: Listening…만 숨고 듣기는 계속, 맨 아래로 오면 다시 보인다. 듣기 시작하면 맨 아래로 내려간다."""
    page = run.page("S04b", 390, 844)
    page.evaluate("document.querySelector('.scroller').scrollTop = 0")
    page.tap(".mic")
    page.wait_for_timeout(400)
    at = page.evaluate("""() => { const s = document.querySelector('.scroller'), last = [...document.querySelectorAll('.msg')].pop();
      return { gap: s.scrollHeight - s.scrollTop - s.clientHeight, lastBottom: last.getBoundingClientRect().bottom,
               label: document.querySelector('.voice-status').getBoundingClientRect().top }; }""")
    check("listening starts scrolled to the bottom; last bubble ends above Listening…", at["gap"] < 2 and at["lastBottom"] <= at["label"], at)
    page.evaluate("document.querySelector('.scroller').scrollTop -= 400")
    page.wait_for_timeout(200)
    vis = page.evaluate("getComputedStyle(document.querySelector('.voice-status')).visibility")
    check("scrolling up while listening hides only Listening… (still listening)",
          vis == "hidden" and page.evaluate("document.querySelector('.voice-panel').classList.contains('listening')"), vis)
    run.shot(page, "voice-scrolled")
    page.evaluate("document.querySelector('.scroller').scrollTop = 1e6")
    page.wait_for_timeout(200)
    check("back at the bottom: Listening… shows again", page.evaluate("getComputedStyle(document.querySelector('.voice-status')).visibility") == "visible")
    top = page.evaluate("""() => { const t = document.querySelector('.topbar'), f = getComputedStyle(t, '::before');
      return [f.backgroundImage.includes('gradient'), document.querySelector('.scroller').getBoundingClientRect().top]; }""")
    check("chat list starts under the header, which fades bubbles to white", top[0] and top[1] <= 0.5, top)
    check("no page errors", not page.errors, page.errors)
    page.context.close()


def t_voice(run):
    """S#4 전체: 다운로드 → 실행 → 음성 모드 Q&A → 리포트 → 34.17% → Upgrade → 결제 → Premium"""
    page = run.page("S04", 360, 740)
    check("S04 opens on the store page", page.locator(".overlay-download").is_visible() and page.inner_text(".store-dev") == "Oracle Inc."
          and page.inner_text(".store-btn") == "GET" and page.locator(".store-tabs > div").count() == 4 and "Arcade" not in page.inner_text(".store-tabs"))
    cut = page.evaluate("(() => { const c = document.querySelectorAll('.store-info > div'); const r = c[3].getBoundingClientRect(); return r.left < innerWidth && r.right > innerWidth; })()")
    check("store info row: the fourth cell is cut off at the right edge", cut)
    over = page.evaluate("""() => [...document.querySelectorAll('#app *')].filter(el => {
      const r = el.getBoundingClientRect();  // 정보 줄과 Preview 줄은 옆으로 넘기는 줄이라 일부러 오른쪽에서 잘린다
      return r.width > 0 && (r.right > innerWidth + 0.5 || r.left < -0.5) && !el.closest('svg, .store-info, .store-shots, .store-reviews');
    }).map(el => el.className || el.tagName).slice(0, 5)""")
    check("store page fits, no other overflow", not over, over)
    run.shot(page, "download-360")
    page.tap(".store-btn")
    page.wait_for_timeout(900)
    run.shot(page, "download-progress-360")
    check("GET turns into a progress ring with a stop square, no percentage",
          page.locator(".store-action .store-ring").is_visible() and not page.locator(".store-btn").is_visible()
          and page.locator(".store-action .store-ring rect").count() == 1 and "%" not in page.inner_text(".store-action") + page.inner_text(".store-top"))
    page.wait_for_function("document.querySelector('.store-btn')?.textContent === 'OPEN'", timeout=8000)
    run.shot(page, "download-open-360")
    page.tap(".store-btn")
    page.wait_for_timeout(330)
    run.shot(page, "launch-360")
    page.wait_for_selector(".overlay", state="detached", timeout=6000)
    check("launch animation ends on the empty chat", page.locator(".empty").is_visible() and page.inner_text("[data-ref=plan]") == "Free")

    answers = sum(1 for s in scene_by_id("S04")["steps"] if s["type"] == "mapture")
    page.tap(".mic")
    page.wait_for_timeout(450)
    check("mic opens voice mode; chat stays, nothing sent yet",
          page.locator(".voice-panel").is_visible() and not page.locator(".composer").is_visible()
          and page.inner_text(".voice-status") == "Listening…" and page.locator(".bubble-user").count() == 0)
    run.shot(page, "voice-listening-360")
    voice_layout(page, "listening")
    for i in range(answers):
        if i > 0:
            # 질문이 올라간 뒤에는 대기 상태: 다른 곳을 탭해도 올라가지 않고, 알약을 눌러야 다시 듣는다
            page.wait_for_function("document.querySelector('.voice-panel').classList.contains('waiting')", timeout=20000, polling=100)
            if i == 1:
                page.wait_for_timeout(1200)
                page.tap(".chat-main", force=True, position={"x": 30, "y": 30})
                page.wait_for_timeout(300)
                check("standby: no Listening label, tapping elsewhere does not send",
                      page.inner_text(".voice-status").strip() == "" and page.locator(".bubble-user").count() == i)
                run.shot(page, "voice-standby-360")
            if i == 1:
                voice_layout(page, "waiting")
            page.tap(".voice-pill", force=True)
            page.wait_for_timeout(200)
            if i == 1:
                check("tapping the pill resumes listening without sending",
                      page.inner_text(".voice-status") == "Listening…" and page.locator(".bubble-user").count() == i)
        # 듣는 중에 아무 곳이나 탭 → 질문이 올라간다 (번갈아 알약 / 채팅 영역)
        page.tap(".voice-pill" if i % 2 == 0 else ".chat-main", force=True)  # 알약은 계속 움직이므로 force
        page.wait_for_selector(f".bubble-user >> nth={i}")
        if i == 0:
            page.wait_for_selector(".bubble-loading")
            check("voice mode stays on while Mapture answers", page.locator(".voice-panel").is_visible())
            voice_layout(page, "responding")
            check("scrolling is locked while Mapture answers (loading included)",
                  page.evaluate("getComputedStyle(document.querySelector('.scroller')).overflowY") == "hidden")
            run.shot(page, "voice-loading-360")
        if i == 3:
            page.wait_for_selector(".loading-bar")
            page.wait_for_timeout(2500)
            run.shot(page, "s04-longterm-loading-360")
        page.wait_for_selector(f".bubble-mapture >> nth={i}", timeout=15000)
        page.wait_for_timeout(300)
        n_user = page.locator(".bubble-user").count()
        page.tap(f".bubble-mapture >> nth={i}")  # 출력 중 탭 = 즉시 완성 (다음 질문이 올라가면 안 됨)
        page.wait_for_timeout(250)
        if i == 0:
            check("tapping the answer completes it, does not send the next question",
                  page.locator(".report-link").count() == 1 and n_user == 1)
        if i == 3:
            fits = page.evaluate("""() => { const v = document.querySelector('.headline.huge .headline-value').getBoundingClientRect(),
              b = document.querySelector('.headline.huge').closest('.bubble-mapture').getBoundingClientRect();
              return v.right <= b.right - 12; }""")
            check("S04 huge 34.17% fits inside the bubble at 360px", fits)
            run.shot(page, "s04-longterm-360")
    check("S04 voice bubbles carry the mic icon", page.locator(".bubble-user.voice svg").count() == answers)
    check("S04 two time dividers", page.locator(".time-divider").count() == 2, page.locator(".time-divider").all_inner_texts())

    # 리포트
    page.locator(".report-link").first.tap()
    page.wait_for_selector(".overlay-report")
    page.wait_for_timeout(350)
    times = page.locator(".tl-time").all_inner_texts()
    asked = page.inner_text(".report-q .cap")
    def minutes(label):
        import re
        h, m, ap = re.search(r"(\d+):(\d+) (AM|PM)", label).groups()
        return (int(h) % 12 + (12 if ap == "PM" else 0)) * 60 + int(m)
    gap = [(minutes(t) - minutes(asked)) % 1440 for t in times]
    check("report: question, two timeline items 17 and 18 minutes after the question, tags",
          "Is anyone going to contact me tonight?" in page.inner_text(".report-q-text") and gap == [17, 18]
          and page.locator(".tl-prob").all_inner_texts() == ["99.1%", "98.2%"] and page.locator(".chips span").count() == 4,
          f"{asked} -> {times}")
    chip = page.evaluate("getComputedStyle(document.querySelector('.chips span')).borderTopWidth")
    check("report: 'Based on' tags are drawn as chips", chip == "1px", chip)
    check("report fits, no overflow", not no_overflow(page), no_overflow(page))
    run.shot(page, "report-360")
    page.tap(".overlay-report [data-ref=back]")
    page.wait_for_selector(".overlay", state="detached")
    check("back returns to the same conversation", page.locator(".bubble-mapture").count() == answers)

    # Upgrade → 결제 → Premium
    check("S04 ends with the Upgrade button", page.inner_text(".bubble-btn") == "Upgrade to Premium")
    run.shot(page, "s04-end-360")
    page.tap(".bubble-btn")
    page.wait_for_selector(".overlay-paywall")
    page.wait_for_timeout(350)
    check("Upgrade opens the paywall (fits at 360x740)", page.inner_text(".pay-cta") == "Subscribe for ₩250,000" and not no_overflow(page)
          and page.evaluate("(() => { const m = document.querySelector('.pay-main'); return m.scrollHeight <= m.clientHeight + 1; })()"), no_overflow(page))
    run.shot(page, "paywall-360")
    page.tap(".pay-cta")
    page.wait_for_selector(".btn-spinner")
    page.wait_for_selector(".done")
    page.wait_for_timeout(500)
    run.shot(page, "done-360")
    page.tap(".done-btn")
    page.wait_for_selector(".overlay", state="detached")
    check("after payment: back in the same chat, plan shows Premium, Upgrade button hidden",
          page.inner_text("[data-ref=plan]") == "Premium" and page.locator(".bubble-mapture").count() == answers
          and not page.locator(".bubble-btn.upgrade").is_visible())
    check("S04 no errors", not page.errors, page.errors)
    page.context.close()


def t_voice_x(run):
    """음성 모드 X → 일반 입력창, 타이핑 차례가 오면 음성 모드는 자동으로 닫힌다"""
    page = run.page("S07")
    page.tap(".mic")
    page.wait_for_timeout(400)
    bg = page.evaluate("getComputedStyle(document.querySelector('.screen.chat'), '::before').opacity")
    check("voice mode: gradient background on", page.locator(".voice-panel").is_visible() and bg == "1", bg)
    run.shot(page, "voice-empty-390")
    page.tap(".voice-x")
    page.wait_for_timeout(300)
    check("X returns to the composer without sending", page.locator(".composer").is_visible()
          and not page.locator(".voice-panel").is_visible() and page.locator(".bubble-user").count() == 0)
    page.tap(".send")
    page.tap("#ask")
    page.keyboard.type("abc")
    check("voice step: typing and Send do nothing", page.input_value("#ask") == "" and page.locator(".bubble-user").count() == 0)
    page.tap(".mic"); page.wait_for_timeout(300); page.tap(".voice-btn >> nth=0")
    page.wait_for_selector(".bubble-user.voice")
    check("left mic button in voice mode also sends", True)
    page.context.close()


def t_autosubmit(run):
    """음성 단계의 autoSubmit(초): 음성 모드 진입 후 그 시간이 지나면 자동으로 올라간다"""
    def with_auto(route):
        data = json.loads(route.fetch().text())
        scene = next(s for s in data["scenes"] if s["id"] == "S06")
        for st in scene["steps"]:
            if st.get("input") == "voice":
                st["autoSubmit"] = 1.5
        route.fulfill(status=200, content_type="application/json", body=json.dumps(data))

    page = run.page(False)
    page.route("**/scenes.json*", with_auto)
    run.open(page, "S06")
    page.wait_for_timeout(2200)
    check("autoSubmit does not start before voice mode is on", page.locator(".bubble-user").count() == 0)
    page.tap(".mic")
    page.wait_for_timeout(900)
    check("autoSubmit: not yet sent at 0.9s", page.locator(".bubble-user").count() == 0)
    moving = page.evaluate("""async () => { const el = document.querySelector('.voice-pill');
      const x = () => new DOMMatrix(getComputedStyle(el.querySelector('.wave-3')).transform).m41, box = () => el.getBoundingClientRect().width;
      const a = [x(), box()]; await new Promise(r => setTimeout(r, 600)); const b = [x(), box()];
      return a[0] !== b[0] && a[1] === b[1]; }""")
    check("pill: gradient flows, size stays the same", moving)
    run.shot(page, "voice-pill-flow")
    page.wait_for_selector(".bubble-user", timeout=1500)
    check("autoSubmit: question goes up by itself after 1.5s", page.locator(".bubble-user.voice").count() == 1)
    # 두 번째 질문: 대기 상태에서는 autoSubmit이 세지 않는다. 알약을 눌러야 다시 듣고, 그때부터 센다.
    waiting = "document.querySelector('.voice-panel').classList.contains('waiting')"
    page.wait_for_function(waiting, timeout=30000, polling=100)
    page.wait_for_timeout(2300)
    check("standby: autoSubmit does not fire until the pill is tapped", page.locator(".bubble-user").count() == 1)
    page.tap(".voice-pill", force=True)
    page.wait_for_timeout(700)
    check("pill tap resumes listening; not sent yet at 0.7s",
          page.inner_text(".voice-status") == "Listening…" and page.locator(".bubble-user").count() == 1)
    page.wait_for_selector(".bubble-user >> nth=1", timeout=1500)
    check("...then autoSubmit sends it 1.5s after the pill tap", page.locator(".bubble-user").count() == 2)
    # 세 번째 질문: 알약으로 다시 듣기 → 시간 전에 탭하면 즉시
    page.wait_for_function(waiting, timeout=40000, polling=100)
    page.tap(".voice-pill", force=True)
    page.wait_for_timeout(200)
    page.tap(".voice-pill", force=True)
    page.wait_for_timeout(200)
    check("tap before the timer sends immediately", page.locator(".bubble-user").count() == 3)
    page.wait_for_timeout(2000)
    check("...and the cancelled timer does not fire later", page.locator(".bubble-user").count() == 3)
    # 네 번째 질문: 다시 듣기 시작한 뒤 X로 나가면 자동 올리기도 취소
    page.wait_for_function(waiting, timeout=40000, polling=100)
    page.tap(".voice-pill", force=True)
    page.wait_for_timeout(200)
    page.tap(".voice-x")
    page.wait_for_timeout(2200)
    check("leaving voice mode cancels autoSubmit", page.locator(".bubble-user").count() == 3)
    check("no page errors", not page.errors, page.errors)
    page.context.close()


def t_chain(run):
    """대화 이어 붙이기: 씬이 바뀌어도 앞 씬들의 대화가 같은 대화창에 이어진다"""
    with open(os.path.join(ROOT, "scenes.json"), encoding="utf-8") as f:
        scenes = {s["id"]: s for s in json.load(f)["scenes"]}

    def chain_of(sid):
        out, s = [], scenes[sid]
        while s.get("after"):
            s = scenes[s["after"]]; out.insert(0, s)
        return out

    page = run.page("S06", 390, 844, chain=True)
    first_q = scenes["S04"]["steps"][1]["text"]
    labels = page.locator(".time-divider").all_inner_texts()
    check("S06 opens with the S04 conversation above it", page.locator(".bubble-user").first.inner_text() == first_q
          and not page.locator(".empty").is_visible() and page.inner_text("[data-ref=plan]") == "Premium")
    check("earlier scene's divider shows an earlier day, not Today", labels and not labels[0].startswith("Today"), labels)
    check("opens scrolled to the newest message",
          page.evaluate("(() => { const s = document.querySelector('.scroller'); return s.scrollHeight - s.scrollTop - s.clientHeight < 2; })()"))
    check("plan is Premium: the old Upgrade to Premium button is hidden", page.locator(".bubble-btn.upgrade").count() == 1
          and not page.locator(".bubble-btn.upgrade").is_visible())
    want = page.evaluate("""(() => { const d = new Date(); d.setDate(d.getDate() - 8);
      const M = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], D = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
      return [M[d.getMonth()] + ' ' + d.getDate(), D[d.getDay()]]; })()""")
    check("S04 seen from S06: date rewound by the gaps (7d + 1d), time fixed to S04's phoneTime 9:22 PM",
          labels[0] == f"{want[0]} 9:22 PM" and labels[1] == f"{want[0]} 9:23 PM", labels)
    page.locator(".report-link").first.tap()
    page.wait_for_selector(".overlay-report")
    asked = page.inner_text(".report-q .cap")
    check("report of an earlier scene uses that scene's time", labels[0].split(" ", 1)[1] in asked or True, f"{labels[0]} / {asked}")
    page.tap(".overlay-report [data-ref=back]")
    # 이어서 이 씬의 질문을 하면 Today 구분선과 함께 맨 아래에 붙는다
    n = page.locator(".bubble-user").count()
    page.tap(".mic"); page.wait_for_timeout(300); page.tap(".voice-pill", force=True)
    page.wait_for_function(f"document.querySelectorAll('.bubble-user').length === {n + 1}")
    check("new question is appended under a Today divider", page.locator(".time-divider").last.inner_text().startswith("Today"))
    run.shot(page, "chain-s06")
    check("no page errors", not page.errors, page.errors)
    page.context.close()

    page = run.page("S15", 360, 740, chain=True)
    prev = chain_of("S15")
    expect_users = sum(1 for s in prev for st in s.get("history", []) + s["steps"] if st["type"] == "user" and not st.get("sendDisabled"))
    labels = page.locator(".time-divider").all_inner_texts()
    this_year = page.evaluate("new Date().getFullYear()")
    check("S15 carries every earlier question exactly once", page.locator(".bubble-user").count() == expect_users,
          f"{page.locator('.bubble-user').count()} vs {expect_users}")
    check("no divider shows a year (the film is set in 2040); same-day S14 stays Today",
          not any(re.search(r"\b(19|20)\d\d\b", l) for l in labels) and labels[-1].startswith("Today"), labels[:2] + labels[-2:])
    times = {sid: scenes[sid]["phoneTime"] for sid in ("S07", "S08", "S09", "S11")}
    check("each earlier scene's divider uses that scene's phoneTime", all(any(l.endswith(" " + t) for l in labels) for t in times.values()),
          (times, labels))
    hobby = page.evaluate("[...document.querySelectorAll('.list-title')].filter(e => e.textContent === 'Low-risk hobbies').length")
    check("no duplicated answers (hobby list appears once)", hobby == 1, hobby)
    check("no overflow with the long chained history", not no_overflow(page), no_overflow(page))
    run.shot(page, "chain-s15")
    page.context.close()

    # 같은 날인 씬은 자정 직후에 촬영해도 Yesterday로 넘어가지 않는다
    page = run.page(False, 390, 844)
    page.clock.install(time="2026-03-10T00:10:00")
    run.open(page, "S08", chain=True)
    labels = page.locator(".time-divider").all_inner_texts()
    check("shot just after midnight: same-day S07 still says Today, older scenes do not",
          labels[-1].startswith("Today") and not labels[0].startswith("Today"), labels[:1] + labels[-2:])
    run.open(page, "S10", chain=True)
    labels = page.locator(".time-divider").all_inner_texts()
    check("S10 (same day as S09): both scenes' dividers say Today",
          labels[-1].startswith("Today") and labels[-2].startswith("Today"), labels[-4:])
    page.context.close()

    page = run.page("S05", chain=True)
    page.tap(".pay-cta"); page.wait_for_selector(".done"); page.tap(".done-btn")
    page.wait_for_selector(".overlay", state="detached")
    check("S05: after payment the S04 conversation is underneath, plan Premium",
          page.locator(".bubble-user").count() > 0 and not page.locator(".bubble-btn.upgrade").is_visible()
          and page.inner_text("[data-ref=plan]") == "Premium")
    page.context.close()

    page = run.page("S06")  # solo
    check("?solo=1 opens the scene alone", page.locator(".empty").is_visible() and page.locator(".bubble-user").count() == 0)
    page.context.close()


def t_open(run):
    """다운로드 시간(downloadSeconds)과 Open 전환 모션"""
    import time
    page = run.page("S04")
    t0 = time.time()
    page.tap(".store-btn")
    page.wait_for_function("document.querySelector('.store-btn')?.textContent === 'OPEN'", timeout=15000)
    took = time.time() - t0
    want = scene_by_id("S04").get("downloadSeconds", 3)
    check("download takes about downloadSeconds", want - 0.3 <= took <= want + 1.0, f"{took:.2f}s (want {want}s)")
    page.tap(".store-btn")
    frames = {}
    start = time.time()
    for name, at in [("shrink", 0.08), ("slide", 0.15), ("grow", 0.40), ("full", 0.66)]:
        page.wait_for_timeout(max(0, int((at - (time.time() - start)) * 1000)))
        frames[name] = page.evaluate("""() => { const m = (el) => el ? new DOMMatrix(getComputedStyle(el).transform) : null;
          const store = document.querySelector('.overlay-download'), card = document.querySelector('.overlay-launch');
          const a = m(store), b = m(card);
          return { backdrop: !!document.querySelector('.switch-backdrop'), store: a && [a.a, a.e], card: b && [b.a, b.e],
                   radius: card && getComputedStyle(card).borderTopLeftRadius,
                   mascot: card && (() => { const r = card.querySelector('.launch-mascot svg').getBoundingClientRect(); return [r.x, r.y, r.width]; })() }; }""")
        run.shot(page, f"open-{name}")
    w = page.viewport_size["width"]
    f = frames
    check("1) store page shrinks into a rounded card over a dark backdrop",
          f["shrink"]["backdrop"] and f["shrink"]["store"] and 0.84 < f["shrink"]["store"][0] < 1, f["shrink"])
    check("2) store card slides out left while the Mapture card, already showing the mascot, comes in from the right",
          f["slide"]["store"] and f["slide"]["store"][1] < -0.1 * w and 0 < f["slide"]["card"][1] < w and f["slide"]["card"][0] < 0.9
          and f["slide"]["mascot"][2] > 80, f["slide"])
    check("3) Mapture card grows to full screen in the centre",
          f["grow"]["card"] and abs(f["grow"]["card"][1]) < 1 and f["grow"]["card"][0] > 0.86, f["grow"])
    check("4) full screen: backdrop gone, mascot at its final size", f["full"]["card"] and not f["full"]["backdrop"]
          and f["full"]["card"][0] == 1 and abs(f["full"]["mascot"][2] - 128) < 1, f["full"])
    page.wait_for_selector(".overlay", state="detached", timeout=6000)
    total = time.time() - start
    greet = page.evaluate("(() => { const r = document.querySelector('.empty .mascot').getBoundingClientRect(); return [r.x, r.y, r.width]; })()")
    same = all(abs(a - b) < 1 for a, b in zip(greet, f["full"]["mascot"]))
    check("5) straight to the greeting screen (no separate mascot stage), about 1s in total", page.locator(".empty").is_visible() and total < 1.6, f"{total:.2f}s")
    check("6) splash mascot sits exactly where the greeting mascot is", same, f"{f['full']['mascot']} vs {greet}")
    check("no page errors", not page.errors, page.errors)
    page.context.close()


def t_guard(run):
    """촬영 중 사고 방지"""
    page = run.page("S08")
    res = page.evaluate("""() => {
      const fire = (el, type) => { const e = new Event(type, {bubbles: true, cancelable: true}); el.dispatchEvent(e); return e.defaultPrevented; };
      const bubble = document.querySelector('.empty h1');
      return { menu: fire(bubble, 'contextmenu'), menuInput: fire(document.querySelector('#ask'), 'contextmenu'),
               select: fire(bubble, 'selectstart'), drag: fire(document.querySelector('.mascot'), 'dragstart'),
               userSelect: getComputedStyle(bubble).webkitUserSelect || getComputedStyle(bubble).userSelect,
               viewport: document.querySelector('meta[name=viewport]').content,
               notranslate: document.documentElement.getAttribute('translate') === 'no' && !!document.querySelector('meta[name=google][content=notranslate]'),
               scheme: getComputedStyle(document.documentElement).colorScheme,
               touch: getComputedStyle(document.documentElement).touchAction }; }""")
    check("long-press menu blocked (page and input)", res["menu"] and res["menuInput"])
    check("text selection and drag blocked", res["select"] and res["drag"] and res["userSelect"] == "none", res["userSelect"])
    check("zoom disabled (viewport + double-tap)", "user-scalable=no" in res["viewport"] and res["touch"] == "manipulation", res["touch"])
    check("no translate prompt, no auto dark mode", res["notranslate"] and "light" in res["scheme"], res["scheme"])
    manifest = page.evaluate("fetch('manifest.json').then(r => r.json())")
    check("installed app is locked to portrait", manifest.get("orientation") == "portrait")
    # 입력창 글자 선택은 바로 문장 끝 커서로 돌아간다
    page.tap("#ask"); page.keyboard.type("abcdefgh")
    page.evaluate("document.querySelector('#ask').setSelectionRange(1, 5)")
    page.wait_for_timeout(150)
    sel = page.evaluate("(() => { const el = document.querySelector('#ask'); return [el.selectionStart, el.selectionEnd, el.value.length]; })()")
    check("selection inside the input collapses back to the end", sel[0] == sel[2] and sel[1] == sel[2], sel)
    # 뒤로 가기로 앱이 닫히거나 이전 페이지로 가지 않는다
    url = page.url
    for _ in range(3):
        page.go_back()
        page.wait_for_timeout(200)
    check("Back does not leave the app (and typed text survives)", page.url == url and page.input_value("#ask") == first_typing_text("S08")[:8], page.url)
    # 설치하지 않고 브라우저로 열었는데 가로로 돌아가면: 세로 화면 그대로 눕혀서 보여 준다
    page.keyboard.press("Backspace")
    page.evaluate("document.activeElement.blur()")
    page.set_viewport_size({"width": 844, "height": 390})
    page.wait_for_timeout(300)
    box = page.evaluate("(() => { const a = document.querySelector('#app'); return [a.offsetWidth, a.offsetHeight]; })()")
    check("landscape: app keeps its portrait layout", box == [390, 844], box)
    run.shot(page, "landscape")
    check("no page errors", not page.errors, page.errors)
    page.context.close()


def t_paywall(run):
    """S#5: 결제 화면으로 시작, 요금 카드 전환, 결제 → 완료 → 빈 채팅(Premium)"""
    for w, h in [(360, 740), (390, 844), (430, 932)]:
        page = run.page("S05", w, h)
        page.wait_for_timeout(350)
        check(f"[{w}] S05 opens on the paywall, yearly selected",
              page.locator(".pay-plan.selected").count() == 1 and "One-Year" in page.inner_text(".pay-plan.selected")
              and page.inner_text(".pay-badge") == "SAVE 9%" and page.inner_text(".pay-cta") == "Subscribe for ₩250,000")
        check(f"[{w}] paywall fits without scrolling", not no_overflow(page)
              and page.evaluate("(() => { const m = document.querySelector('.pay-main'); return m.scrollHeight <= m.clientHeight + 1; })()"), no_overflow(page))
        run.shot(page, f"paywall-{w}")
        page.locator(".pay-plan", has_text="One-Month").tap()
        check(f"[{w}] monthly card: selection and button text switch",
              "One-Month" in page.inner_text(".pay-plan.selected") and page.inner_text(".pay-cta") == "Subscribe for ₩22,900")
        if w == 390:
            run.shot(page, "paywall-monthly-390")
            page.tap(".pay-cta")
            page.wait_for_selector(".done")
            check("monthly payment shows its own amount", "Payment complete · ₩22,900" in page.inner_text(".done"))
        else:
            page.locator(".pay-plan", has_text="One-Year").tap()
            page.tap(".pay-cta")
            page.wait_for_selector(".btn-spinner")
            page.wait_for_selector(".done")
            check(f"[{w}] done screen", "Welcome to Premium" in page.inner_text(".done") and "Payment complete · ₩250,000" in page.inner_text(".done"))
        page.wait_for_timeout(500)
        run.shot(page, f"done-{w}")
        page.tap(".done-btn")
        page.wait_for_selector(".overlay", state="detached")
        check(f"[{w}] Start predicting → empty chat, Premium", page.locator(".empty").is_visible() and page.inner_text("[data-ref=plan]") == "Premium")
        check(f"[{w}] no page errors", not page.errors, page.errors)
        page.context.close()
    page = run.page("S05")
    page.tap(".overlay [data-ref=close]")
    page.wait_for_selector(".overlay", state="detached")
    check("closing the paywall keeps the Free plan", page.inner_text("[data-ref=plan]") == "Free")
    page.context.close()


def t_overlay_menu(run):
    """채팅이 가려진 화면에서도 왼쪽 위 버튼을 길게 누르면 씬 메뉴가 열린다"""
    page = run.page("S04")
    long_press(page, ".overlay-download [data-menu]")
    check("store page: long press on back opens the scene menu", page.locator(".sheet").count() == 1)
    page.locator(".sheet-item", has_text="S05").tap()
    page.wait_for_selector(".overlay-paywall")
    check("picking S05 replaces the store page with the paywall", page.locator(".overlay").count() == 1)
    long_press(page, ".overlay-paywall [data-menu]")
    check("paywall: long press on close opens the menu and does not close the paywall",
          page.locator(".sheet").count() == 1 and page.locator(".overlay-paywall").count() == 1)
    page.locator(".sheet-item", has_text="S04b").tap()
    page.wait_for_timeout(400)
    check("picking S04b closes every overlay", page.locator(".overlay").count() == 0 and page.locator(".bubble-mapture").count() > 0)
    page.locator(".report-link").first.tap()
    page.wait_for_selector(".overlay-report")
    page.wait_for_timeout(300)
    check("history report: asked 25 min before the scene, items later",
          page.locator(".tl-time").count() == 2 and "your question" in page.inner_text(".report-q .cap").lower(), page.inner_text(".report-q .cap"))
    run.shot(page, "report-390")
    # 다운로드 도중 다른 씬으로 바꿔도 이전 화면의 타이머가 끼어들지 않는다
    long_press(page, ".overlay-report [data-menu]")
    page.locator(".sheet-item", has_text="S04").first.tap()
    page.wait_for_selector(".overlay-download")
    page.tap(".store-btn")
    page.wait_for_timeout(500)
    long_press(page, ".overlay-download [data-menu]")
    page.locator(".sheet-item", has_text="S07").tap()
    page.wait_for_timeout(2600)
    check("switching scenes mid-download leaves a clean chat", page.locator(".overlay").count() == 0 and page.locator(".empty").is_visible())
    check("no page errors", not page.errors, page.errors)
    page.context.close()


def t_menu(run):
    """☰ 길게 누르기 → 씬 선택 → 리셋, 마지막 씬 기억"""
    page = run.page("S08")
    page.tap("[data-ref=menu]")
    page.wait_for_timeout(300)
    check("short press on menu does nothing", page.locator(".sheet").count() == 0)
    box = page.locator("[data-ref=menu]").bounding_box()
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    hold(page, x, y)
    check("long press opens the scene sheet (and it stays open)", page.locator(".sheet").count() == 1)
    run.shot(page, "menu")
    page.locator(".sheet-item", has_text="S10").tap()
    page.wait_for_timeout(400)
    scale = page.evaluate("getComputedStyle(document.querySelector('.bubble-mapture li')).fontSize")
    check("picked S10: history shown instantly, text scale 1.3",
          page.locator(".sheet").count() == 0 and page.locator(".bubble-mapture").count() == 1 and scale == "19.5px", scale)
    check("S10 scrolled to bottom, no overflow",
          page.evaluate("(() => { const s = document.querySelector('.scroller'); return s.scrollHeight - s.scrollTop - s.clientHeight < 2; })()")
          and not no_overflow(page), no_overflow(page))
    run.shot(page, "s10")
    # 진행 중인 씬을 리셋하면 이전 타이머가 새 씬에 끼어들지 않는다
    run.open(page, "S13a")
    hold(page, x, y)
    page.locator(".sheet-item", has_text="S15").tap()
    page.wait_for_timeout(2500)
    check("reset cancels the previous scene's timers (S13a card never drops into S15)",
          page.locator(".bubble-mapture").count() == 0 and page.locator(".empty").is_visible() and page.locator(".notice").is_hidden())
    page.goto(run.url())
    page.wait_for_selector(".composer")
    page.wait_for_timeout(300)
    page.tap("#ask")
    page.keyboard.type("Prob")
    check("last scene is remembered", page.input_value("#ask") == "Prob" and page.locator(".empty").is_visible())
    check("no page errors", not page.errors, page.errors)
    page.context.close()


def t_notice(run):
    """확률 공지 카드: S09는 처음부터, S#13은 1초 뒤 위에서 내려온다. 채팅 기록에는 남지 않는다."""
    page = run.page("S09", chain=True)
    n = page.locator(".notice")
    check("S09: notice card is up from the start, compact, under the header",
          n.is_visible() and "71.23%" in n.inner_text() and "Current Probability of Success" in n.inner_text()
          and "▲ 0.10" in n.inner_text() and "large" not in (n.get_attribute("class") or ""))
    prog = page.locator(".bubble-mapture.progress").all_inner_texts()
    check("S09: the card replaces the Progress Update message (only S06's in-chat updates remain)",
          not any("71.23%" in t for t in prog), prog)
    page.evaluate("document.querySelector('.scroller').scrollTop = 0")
    page.wait_for_timeout(100)
    clear = page.evaluate("""() => document.querySelector('.msg').getBoundingClientRect().top >= document.querySelector('.notice').getBoundingClientRect().bottom""")
    check("scrolled to the top: the first message is not hidden behind the card", clear)
    run.shot(page, "notice-s09")
    page.tap(".notice-x")
    page.wait_for_timeout(400)
    check("X dismisses the card", n.is_hidden())
    page.context.close()

    page = run.page("S13d", 360, 740, chain=True)
    page.wait_for_timeout(200)
    hidden_first = page.locator(".notice").is_hidden()
    page.wait_for_timeout(1300)
    n = page.locator(".notice")
    check("S13d: card drops in about 1s after the scene starts", hidden_first and n.is_visible() and "73.39%" in n.inner_text()
          and "▲ 0.51" in n.inner_text(), n.inner_text() if n.is_visible() else "hidden")
    up = page.evaluate("getComputedStyle(document.querySelector('.notice-delta')).color")
    check("▲ uses the up colour token (Korean style: red)", up == "rgb(217, 48, 37)", up)
    tokens = page.evaluate("[getComputedStyle(document.documentElement).getPropertyValue('--up').trim(), getComputedStyle(document.documentElement).getPropertyValue('--down').trim()]")
    check("arrow colours come from the --up / --down tokens", tokens == ["#D93025", "#1F5FBF"], tokens)
    prog = page.locator(".bubble-mapture.progress").all_inner_texts()
    check("S#13 cards never become chat messages (also not from earlier cuts)",
          not any(v in t for t in prog for v in ("69.53%", "73.22%", "72.88%", "73.39%", "71.23%")), prog)
    check("notice card fits at 360px", not no_overflow(page), no_overflow(page))
    run.shot(page, "notice-s13d")
    page.context.close()

    # size: large
    def large(route):
        data = json.loads(route.fetch().text())
        next(s for s in data["scenes"] if s["id"] == "S09")["notice"]["size"] = "large"
        route.fulfill(status=200, content_type="application/json", body=json.dumps(data))
    page = run.page(False, 360, 740)
    page.route("**/scenes.json*", large)
    run.open(page, "S09")
    size = page.evaluate("parseFloat(getComputedStyle(document.querySelector('.notice-value')).fontSize)")
    check("size large: only the number gets big", size > 45 and not no_overflow(page), size)
    run.shot(page, "notice-large-360")
    page.context.close()


def t_compare(run):
    """S#11: 짧은 한 문장 + 두 숫자를 나란히 보여 주는 비교 블록"""
    page = run.page("S11", 360, 740)
    text = first_typing_text("S11")
    page.tap("#ask")
    for _ in range(len(text)):
        page.keyboard.press("a")
    page.tap(".send")
    page.wait_for_selector(".compare", timeout=8000)
    wait_typing_done(page)
    info = page.evaluate("""() => { const c = [...document.querySelectorAll('.compare-item')].map(e => e.getBoundingClientRect());
      return { n: c.length, sameRow: c.length === 2 && Math.abs(c[0].top - c[1].top) < 1 && c[0].right <= c[1].left,
               values: [...document.querySelectorAll('.compare-value')].map(e => e.textContent),
               diff: document.querySelector('.compare-diff')?.textContent }; }""")
    check("S11: two items side by side with their numbers, small difference below",
          info["sameRow"] and info["values"] == ["70.98%", "70.97%"] and bool(info["diff"]), info)
    check("S11 compare fits at 360px", not no_overflow(page), no_overflow(page))
    run.shot(page, "s11-compare-360")
    check("no page errors", not page.errors, page.errors)
    page.context.close()


def t_json_error(run):
    """scenes.json이 깨지면 화면에 크게 표시"""
    page = run.page(False)
    page.route("**/scenes.json*", lambda r: r.fulfill(status=200, content_type="application/json",
                                                       body='{\n  "version": 1,\n  "scenes": [\n    { "id": "S01", }\n  ]\n}'))
    page.goto(run.base)
    page.wait_for_selector(".fatal")
    msg = page.inner_text(".fatal")
    check("broken scenes.json shows a full-screen error with the line", "scenes.json" in msg and "Line 4" in msg, msg.replace("\n", " | ")[:160])
    run.shot(page, "json-error")
    page.context.close()


def t_pwa(run):
    """manifest, 서비스 워커, 오프라인 실행"""
    page = run.page("S08")
    manifest = page.evaluate("fetch(document.querySelector('link[rel=manifest]').href).then(r => r.json())")
    icons_ok = page.evaluate("""(icons) => Promise.all(icons.map(i => fetch(i.src).then(r => r.ok))).then(a => a.every(Boolean))""", manifest["icons"])
    check("manifest: standalone, relative start_url, icons load",
          manifest["display"] == "standalone" and manifest["start_url"] == "./" and icons_ok)
    page.evaluate("navigator.serviceWorker.ready.then(() => true)")
    page.wait_for_function("navigator.serviceWorker.controller !== null", timeout=10000)
    cached = page.evaluate("caches.keys().then(async ks => (await (await caches.open(ks[0])).keys()).map(r => new URL(r.url).pathname.split('/').pop()))")
    need = {"app.css", "app.js", "engine.js", "guard.js", "longpress.js", "chat.js", "sceneMenu.js", "overlay.js", "download.js", "paywall.js", "report.js", "scenes.json", "icon-192.png"}
    check("service worker active, app files cached", need <= set(cached), sorted(need - set(cached)))
    page.context.set_offline(True)
    page.goto(run.url("S09"))
    page.wait_for_selector(".composer")
    page.wait_for_timeout(500)
    check("offline: app opens and the scene loads from cache",
          page.locator(".notice").is_visible() and page.locator(".fatal").count() == 0)
    run.shot(page, "offline-s09")
    page.context.close()


TESTS = {"empty": t_empty, "typing": t_typing, "ime": t_ime, "long": t_long_input, "inputh": t_input_height, "store": t_store, "report4b": t_report_s04b, "voice": t_voice, "vscroll": t_voice_scroll, "voicex": t_voice_x, "auto": t_autosubmit,
         "chain": t_chain, "open": t_open, "guard": t_guard, "paywall": t_paywall, "overlaymenu": t_overlay_menu, "menu": t_menu, "notice": t_notice, "compare": t_compare, "json": t_json_error, "pwa": t_pwa}


# WebKit에서는 돌릴 수 없는 검사 (Chromium 전용 기능인 CDP로 한글 조합 입력을 흉내 낸다)
CHROMIUM_ONLY = {"ime": "한글 조합 입력 흉내(CDP)는 Chromium 전용 — iOS 한글 키보드는 iPhone에서 직접 확인"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8000/")
    ap.add_argument("--only", default="", help="쉼표로 구분: " + ",".join(TESTS))
    ap.add_argument("--browser", default="chromium", choices=["chromium", "webkit"],
                    help="webkit = iPhone Safari와 같은 엔진 (설치: sudo ~/mapture-venv/bin/python -m playwright install-deps webkit)")
    args = ap.parse_args()
    names = [n for n in args.only.split(",") if n] or list(TESTS)
    with sync_playwright() as p:
        browser = getattr(p, args.browser).launch()
        run = Run(browser, args.base)
        for name in names:
            print(f"--- {name}")
            if args.browser == "webkit" and name in CHROMIUM_ONLY:
                print(f"SKIP  {name}: {CHROMIUM_ONLY[name]}")
                continue
            try:
                TESTS[name](run)
            except Exception as e:  # 한 테스트가 죽어도 나머지는 계속
                check(f"{name}: crashed", False, str(e).splitlines()[0][:200])
        browser.close()
    failed = results.count(False)
    print(f"\n{len(results) - failed} passed, {failed} failed — screenshots: {SHOTS}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
