"""TC-012, TC-044, TC-045, TC-047: доступність."""
import re

import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.a11y


def test_tc012_skip_link_jumps_to_main(page: Page, home):
    page.keyboard.press("Tab")
    expect(home.skip_link).to_be_focused()
    page.keyboard.press("Enter")
    expect(page).to_have_url(re.compile(r"#main$"))


def test_tc044_single_h1_and_no_skipped_heading_levels(page: Page, home):
    levels = page.evaluate(
        "[...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h => +h.tagName[1])")
    assert levels.count(1) == 1, "На сторінці має бути рівно один h1"
    assert levels[0] == 1
    for prev, cur in zip(levels, levels[1:]):
        assert cur <= prev + 1, f"Пропущено рівень заголовка: h{prev} → h{cur}"


def test_tc045_axe_no_critical_or_serious_violations(page: Page, home):
    results = Axe().run(page)
    bad = [v for v in results.response["violations"] if v["impact"] in ("critical", "serious")]
    summary = [(v["id"], v["impact"], len(v["nodes"])) for v in bad]
    assert bad == [], f"axe-порушення: {summary}"


def test_tc047_lang_and_logo_alt(page: Page, home):
    expect(page.locator("html")).to_have_attribute("lang", "uk")
    expect(home.header.locator("img").first).to_have_attribute("alt", re.compile(r".+"))
