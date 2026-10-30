"""TC-014..016, TC-041..043, TC-051: адаптивність і мобільне меню."""
import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.responsive

WIDTHS = [320, 375, 768, 1280]


@pytest.mark.parametrize("width", WIDTHS)
def test_tc041_no_horizontal_scroll(page: Page, width):
    page.set_viewport_size({"width": width, "height": 800})
    page.goto("/")
    overflow = page.evaluate(
        "document.documentElement.scrollWidth - document.documentElement.clientWidth")
    assert overflow <= 0, f"Горизонтальний скрол {overflow}px на ширині {width}px"


def test_tc042_desktop_shows_menu_hides_burger(page: Page, home):
    expect(home.desktop_nav).to_be_visible()
    expect(home.menu_toggle).to_be_hidden()


# ---- мобільне меню (375 px) --------------------------------------------------
@pytest.fixture
def mobile(page: Page, home):
    page.set_viewport_size({"width": 375, "height": 800})
    return home


def test_tc014_mobile_menu_opens_and_closes(mobile):
    h = mobile
    expect(h.desktop_nav).to_be_hidden()
    expect(h.mobile_menu).to_be_hidden()
    expect(h.menu_toggle).to_have_attribute("aria-expanded", "false")

    h.menu_toggle.click()
    expect(h.mobile_menu).to_be_visible()
    expect(h.menu_toggle).to_have_attribute("aria-expanded", "true")
    expect(h.menu_toggle).to_have_attribute("aria-label", "Закрити меню")

    h.menu_toggle.click()
    expect(h.mobile_menu).to_be_hidden()
    expect(h.menu_toggle).to_have_attribute("aria-expanded", "false")
    expect(h.menu_toggle).to_have_attribute("aria-label", "Відкрити меню")


def test_tc015_mobile_link_scrolls_and_closes_menu(page: Page, mobile):
    h = mobile
    h.menu_toggle.click()
    h.mobile_link("Послуги").click()
    expect(page).to_have_url(re.compile(r"#services$"))
    expect(h.mobile_menu).to_be_hidden()
    expect(page.locator("#services")).to_be_in_viewport()


def test_tc016_escape_closes_menu_and_returns_focus(page: Page, mobile):
    h = mobile
    h.menu_toggle.click()
    expect(h.mobile_menu).to_be_visible()
    page.keyboard.press("Escape")
    expect(h.mobile_menu).to_be_hidden()
    expect(h.menu_toggle).to_have_attribute("aria-expanded", "false")
    expect(h.menu_toggle).to_be_focused()


def test_tc051_menu_closes_when_viewport_grows(page: Page, mobile):
    h = mobile
    h.menu_toggle.click()
    expect(h.mobile_menu).to_be_visible()
    page.set_viewport_size({"width": 1024, "height": 800})
    expect(h.mobile_menu).to_be_hidden()
    expect(h.menu_toggle).to_have_attribute("aria-expanded", "false")


def test_tc043_form_usable_on_320px(page: Page, home, capture):
    page.set_viewport_size({"width": 320, "height": 640})
    home.scroll_to_form()
    for field in (home.name, home.email, home.message, home.submit):
        expect(field).to_be_visible()
        box = field.bounding_box()
        assert box["x"] >= 0 and box["x"] + box["width"] <= 320, "Поле виходить за межі екрана"
    home.fill_form("Олена", "olena@example.com", "вечеря на шістьох").submit_form()
    capture.wait_for(1)
    assert capture.last_fields["name"] == "Олена"
