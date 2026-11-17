#!/usr/bin/env python3
"""스토어 화면 Preview 스크린샷(img/preview-*.jpg)을 실제 앱 화면에서 캡처해 다시 만든다.

사용:
  python3 -m http.server 8000                    # 프로젝트 루트에서, 다른 터미널
  ~/mapture-venv/bin/python tools/make-previews.py
  ~/mapture-venv/bin/python tools/make-previews.py --base http://localhost:8000/

  1. preview-1.jpg  'Know what happens next'  : S04 10년 뒤 질문 → 34.17% 답변 (S04b로 재생, 음성 모드는 X로 닫음)
  2. preview-2.jpg  'Every decision, analyzed': S08 콘서트 질문 → 71.13% 답변
  3. preview-3.jpg  세 번째                    : S04 Detailed Analysis Report

화면 비율은 스토어 Preview 카드 속 폰 화면(약 190 × 373)에 맞춘 390 × 766.
시각은 각 씬의 phoneTime으로 고정한다 (구분선·리포트 시각이 대본과 맞게).
다시 만든 뒤에는 sw.js의 CACHE_VERSION을 올릴 것 (이미지도 오프라인 캐시에 들어 있다).
"""
import argparse
import os

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "img")
VIEW = {"width": 390, "height": 766}
SCALE = 1.5  # 390 × 1.5 = 585px 폭: 카드 안 190px를 iPhone(3배)에서 선명하게


def open_scene(browser, base, scene, clock):
    ctx = browser.new_context(viewport=VIEW, device_scale_factor=SCALE, is_mobile=True, has_touch=True)
    page = ctx.new_page()
    page.clock.set_fixed_time(clock)  # Date만 고정. 타이머·애니메이션은 그대로 흐른다
    page.goto(f"{base}?scene={scene}&solo=1")
    page.wait_for_selector(".composer")
    page.wait_for_function("document.fonts.status === 'loaded'")
    page.wait_for_timeout(400)
    return page


def finish_answer(page, n):
    """n번째 맵쳐 말풍선이 뜨면 탭해서 글자를 즉시 완성"""
    page.wait_for_selector(f".bubble-mapture >> nth={n}", timeout=20000)
    page.wait_for_timeout(200)
    page.locator(".bubble-mapture").nth(n).tap()
    page.wait_for_timeout(500)


def save(page, name):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    page.screenshot(path=path, type="jpeg", quality=82)
    print("wrote", os.path.relpath(path, ROOT), f"({os.path.getsize(path) // 1024} KB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8000/")
    args = ap.parse_args()
    base = args.base if args.base.endswith("/") else args.base + "/"
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # 1) S04: 10년 뒤 질문 → 34.17%
        page = open_scene(browser, base, "S04b", "2026-03-10T21:47:00")
        n = page.locator(".bubble-mapture").count()
        page.tap(".mic")
        page.wait_for_timeout(400)
        page.tap(".voice-pill", force=True)
        finish_answer(page, n)
        page.tap(".voice-x")
        page.wait_for_timeout(500)
        page.evaluate("document.querySelector('.scroller').scrollTop = 1e6")
        page.wait_for_timeout(200)
        save(page, "preview-1.jpg")
        page.context.close()

        # 2) S08: 콘서트 질문 → 71.13% 답변
        page = open_scene(browser, base, "S08", "2026-03-13T19:40:00")
        text = page.evaluate("fetch('scenes.json').then(r => r.json()).then(d => d.scenes.find(s => s.id === 'S08').steps.find(s => s.type === 'user').text)")
        page.tap("#ask")
        for _ in range(len(text)):
            page.keyboard.press("a")
        page.tap(".send")
        finish_answer(page, 0)
        page.evaluate("document.activeElement.blur(); document.querySelector('.scroller').scrollTop = 1e6")
        page.wait_for_timeout(300)
        save(page, "preview-2.jpg")
        page.context.close()

        # 3) S04 Detailed Analysis Report
        page = open_scene(browser, base, "S04b", "2026-03-10T21:47:00")
        page.locator(".report-link").first.tap()
        page.wait_for_selector(".overlay-report")
        page.wait_for_timeout(500)
        save(page, "preview-3.jpg")
        page.context.close()

        browser.close()


if __name__ == "__main__":
    main()
