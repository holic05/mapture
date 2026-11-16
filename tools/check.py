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


class Run:
    def __init__(self, browser, base):
        self.browser = browser
        self.base = base if base.endswith("/") else base + "/"

    def page(self, scene=None, width=390, height=844, **ctx_kw):
        opts = dict(PHONE)
        opts["viewport"] = {"width": width, "height": height}
        opts.update(ctx_kw)
        ctx = self.browser.new_context(**opts)
        page = ctx.new_page()
        page.errors = []
        page.on("pageerror", lambda e: page.errors.append(str(e)))
        page.on("console", lambda m: page.errors.append(m.text) if m.type == "error" else None)
        if scene is not False:
            self.open(page, scene)
        return page

    def open(self, page, scene=None):
        page.goto(self.base + (f"?scene={scene}" if scene else ""))
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
        page = run.page("S05", w, h)
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


def t_ime(run):
    """Android Gboard처럼 '조합(composition)' 상태로 들어오는 입력 (취소 불가 이벤트)"""
    text = first_typing_text("S08")
    page = run.page("S08")
    page.tap("#ask")
    cdp = page.context.new_cdp_session(page)
    typed = 0
    # 단어 하나를 조합 상태로 한 글자씩 → 스페이스로 확정, 을 반복
    for word in ["hello", "wor", "abcdefg"]:
        for i in range(1, len(word) + 1):
            cdp.send("Input.imeSetComposition", {"text": word[:i], "selectionStart": i, "selectionEnd": i})
            typed += 1
            page.wait_for_timeout(15)
        cdp.send("Input.insertText", {"text": " "})
        typed += 1
        page.wait_for_timeout(15)
    val = page.input_value("#ask")
    check("IME composition: every key adds exactly one scripted char", val == text[:typed], f"{typed} keys -> {val!r}")
    # 조합 중 백스페이스 = 더 짧은 조합 문자열
    cdp.send("Input.imeSetComposition", {"text": "ab", "selectionStart": 2, "selectionEnd": 2})
    cdp.send("Input.imeSetComposition", {"text": "abc", "selectionStart": 3, "selectionEnd": 3})
    cdp.send("Input.imeSetComposition", {"text": "ab", "selectionStart": 2, "selectionEnd": 2})
    page.wait_for_timeout(50)
    val2 = page.input_value("#ask")
    check("IME composition: backspace inside a word removes one char", val2 == text[:typed + 1], repr(val2))
    page.context.close()

    # 입력 단계가 아닐 때는 아무 글자도 들어가지 않는다
    page = run.page("S05")
    page.tap("#ask")
    page.keyboard.type("hello")
    cdp = page.context.new_cdp_session(page)
    cdp.send("Input.imeSetComposition", {"text": "abc", "selectionStart": 3, "selectionEnd": 3})
    cdp.send("Input.insertText", {"text": "zzz"})
    page.wait_for_timeout(50)
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


def t_voice(run):
    """S#4: 음성 질문(2단계에서는 마이크 탭) → 리포트 링크 → 큰 숫자 → Upgrade 버튼"""
    page = run.page("S04", 360, 740)
    check("S04 starts on the empty state", page.locator(".empty").is_visible())
    answers = sum(1 for s in scene_by_id("S04")["steps"] if s["type"] == "mapture")
    for i in range(answers):
        page.tap(".mic")
        page.wait_for_selector(f".bubble-user >> nth={i}")
        if i == 3:
            page.wait_for_selector(".loading-bar")
            page.wait_for_timeout(2500)
            run.shot(page, "s04-longterm-loading-360")
        page.wait_for_selector(f".bubble-mapture >> nth={i}", timeout=15000)
        page.wait_for_timeout(300)
        page.tap(f".bubble-mapture >> nth={i}")
        page.wait_for_timeout(200)
        if i == 0:
            check("S04 first answer has the report link", page.locator(".report-link").count() == 1)
            run.shot(page, "s04-first-360")
        if i == 3:
            fits = page.evaluate("""() => { const v = document.querySelector('.headline.huge .headline-value').getBoundingClientRect(),
              b = document.querySelector('.headline.huge').closest('.bubble-mapture').getBoundingClientRect();
              return v.right <= b.right - 12; }""")
            check("S04 huge 34.17% fits inside the bubble at 360px", fits)
            run.shot(page, "s04-longterm-360")
    check("S04 voice bubbles carry the mic icon", page.locator(".bubble-user.voice svg").count() == answers)
    check("S04 ends with the Upgrade button", page.inner_text(".bubble-btn") == "Upgrade to Premium")
    check("S04 two time dividers", page.locator(".time-divider").count() == 2, page.locator(".time-divider").all_inner_texts())
    check("S04 no overflow / errors", not no_overflow(page) and not page.errors, page.errors or no_overflow(page))
    run.shot(page, "s04-end-360")
    page.context.close()


def t_menu(run):
    """☰ 길게 누르기 → 씬 선택 → 리셋, 마지막 씬 기억"""
    page = run.page("S08")
    page.tap("[data-ref=menu]")
    page.wait_for_timeout(300)
    check("short press on menu does nothing", page.locator(".sheet").count() == 0)
    box = page.locator("[data-ref=menu]").bounding_box()
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    cdp = page.context.new_cdp_session(page)
    touch = [{"x": x, "y": y}]
    cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": touch})
    page.wait_for_timeout(800)
    cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
    page.wait_for_timeout(400)
    check("long press opens the scene sheet (and it stays open)", page.locator(".sheet").count() == 1)
    run.shot(page, "menu")
    page.locator(".sheet-item", has_text="S10").tap()
    page.wait_for_timeout(400)
    scale = page.evaluate("getComputedStyle(document.querySelector('.body-text')).fontSize")
    check("picked S10: history shown instantly, text scale 1.3",
          page.locator(".sheet").count() == 0 and page.locator(".bubble-mapture").count() == 2 and scale == "19.5px", scale)
    check("S10 scrolled to bottom, no overflow",
          page.evaluate("(() => { const s = document.querySelector('.scroller'); return s.scrollHeight - s.scrollTop - s.clientHeight < 2; })()")
          and not no_overflow(page), no_overflow(page))
    run.shot(page, "s10")
    # 진행 중인 씬을 리셋하면 이전 타이머가 새 씬에 끼어들지 않는다
    run.open(page, "S13a")
    cdp = page.context.new_cdp_session(page)
    cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": touch})
    page.wait_for_timeout(800)
    cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
    page.locator(".sheet-item", has_text="S05").tap()
    page.wait_for_timeout(2500)
    check("reset cancels the previous scene's timers", page.locator(".bubble-mapture").count() == 0 and page.locator(".empty").is_visible())
    page.goto(run.base)
    page.wait_for_selector(".composer")
    page.wait_for_timeout(300)
    check("last scene is remembered", page.inner_text("[data-ref=plan]") == "Free" and page.locator(".empty").is_visible())
    check("no page errors", not page.errors, page.errors)
    page.context.close()


def t_progress(run):
    """S#13: history 위에 Progress Update 하나가 도착"""
    page = run.page("S13d")
    before = page.locator(".bubble-mapture.progress").count()
    page.wait_for_function("document.querySelectorAll('.bubble-mapture.progress').length === 4", timeout=5000)
    page.wait_for_timeout(400)
    last = page.locator(".bubble-mapture.progress").last
    check("S13d: one Progress Update arrives on top of history",
          before == 3 and "73.39%" in last.inner_text() and "▲ 0.51" in last.inner_text(), last.inner_text())
    up = page.evaluate("getComputedStyle([...document.querySelectorAll('.headline-delta')].pop()).color")
    check("▲ uses the up colour", up == "rgb(31, 95, 191)", up)
    run.shot(page, "s13d")
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
    need = {"app.css", "app.js", "engine.js", "chat.js", "sceneMenu.js", "scenes.json", "icon-192.png"}
    check("service worker active, app files cached", need <= set(cached), sorted(need - set(cached)))
    page.context.set_offline(True)
    page.goto(run.base + "?scene=S09")
    page.wait_for_selector(".composer")
    page.wait_for_timeout(500)
    check("offline: app opens and the scene loads from cache",
          page.locator(".bubble-mapture.progress").count() == 1 and page.locator(".fatal").count() == 0)
    run.shot(page, "offline-s09")
    page.context.close()


TESTS = {"empty": t_empty, "typing": t_typing, "ime": t_ime, "long": t_long_input, "voice": t_voice,
         "menu": t_menu, "progress": t_progress, "json": t_json_error, "pwa": t_pwa}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8000/")
    ap.add_argument("--only", default="", help="쉼표로 구분: " + ",".join(TESTS))
    args = ap.parse_args()
    names = [n for n in args.only.split(",") if n] or list(TESTS)
    with sync_playwright() as p:
        # Chromium 시스템 라이브러리를 sudo 없이 ~/.cache/mapture-libs 에 풀어 둔 경우 그 경로를 쓴다.
        # (`sudo ~/mapture-venv/bin/playwright install-deps chromium` 을 실행했다면 이 폴더는 필요 없음)
        env = dict(os.environ)
        libs = os.path.expanduser("~/.cache/mapture-libs")
        if os.path.isdir(libs):
            env["LD_LIBRARY_PATH"] = libs + os.pathsep + env.get("LD_LIBRARY_PATH", "")
        browser = p.chromium.launch(env=env)
        run = Run(browser, args.base)
        for name in names:
            print(f"--- {name}")
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
