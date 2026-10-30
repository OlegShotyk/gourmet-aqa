"""TC-017..019, TC-037: відео, YouTube-фасад, карта. Сторонні домени заблоковані заглушками."""
import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.media


def test_tc017_background_video_pause_and_resume(page: Page, home):
    home.video_toggle.scroll_into_view_if_needed()
    # автозапуск (muted) має спрацювати, і підпис кнопки відображає стан
    expect(home.video_toggle).to_contain_text("Пауза відео", timeout=10_000)
    assert page.evaluate("!document.querySelector('[data-bg-video]').paused")

    home.video_toggle.click()
    expect(home.video_toggle).to_contain_text("Відтворити відео")
    assert page.evaluate("document.querySelector('[data-bg-video]').paused")

    home.video_toggle.click()
    expect(home.video_toggle).to_contain_text("Пауза відео")
    assert page.evaluate("!document.querySelector('[data-bg-video]').paused")


def test_tc018_youtube_loads_only_after_click(page: Page, home, block_third_party):
    home.youtube_facade.scroll_into_view_if_needed()
    expect(home.youtube_iframe).to_have_count(0)  # до кліку жодних сторонніх завантажень

    home.youtube_facade.click()
    expect(home.youtube_iframe).to_have_count(1)
    expect(home.youtube_iframe).to_have_attribute(
        "src", re.compile(r"^https://www\.youtube-nocookie\.com/embed/yJN7VsXCfqc"))
    expect(home.youtube_facade).to_have_count(0)


def test_tc019_video_hidden_with_reduced_motion(page: Page):
    page.emulate_media(reduced_motion="reduce")
    page.goto("/")
    expect(page.locator("[data-bg-video]")).to_be_hidden()
    expect(page.locator("[data-video-toggle]")).to_be_hidden()


def test_tc037_map_loads_lazily(page: Page, home, block_third_party):
    expect(home.map_iframe).not_to_have_attribute("src", re.compile(r".+"))
    home.map_iframe.scroll_into_view_if_needed()
    expect(home.map_iframe).to_have_attribute("src", re.compile(r"maps\.google\.com"))
