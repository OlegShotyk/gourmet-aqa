"""TC-006..011, TC-013: якорна навігація (десктоп, 1280 px)."""
import re

import pytest
from playwright.sync_api import Page, expect

from pages.home_page import MENU_LINKS

pytestmark = pytest.mark.nav


def assert_scrolled_to(page: Page, anchor: str):
    expect(page).to_have_url(re.compile(re.escape(anchor) + r"$"))
    expect(page.locator(anchor)).to_be_in_viewport()


@pytest.mark.parametrize("text,anchor", MENU_LINKS.items(), ids=list(MENU_LINKS))
def test_tc006_menu_link_scrolls_to_section(page: Page, home, text, anchor):
    home.nav_link(text).click()
    assert_scrolled_to(page, anchor)


def test_tc007_logo_scrolls_to_top(page: Page, home):
    home.nav_link("Контакти").click()
    page.wait_for_function("window.scrollY > 500")
    home.logo.click()
    expect(page).to_have_url(re.compile(r"#top$"))
    page.wait_for_function("window.scrollY < 5")


def test_tc008_header_cta_goes_to_form(page: Page, home):
    home.header_cta.click()
    assert_scrolled_to(page, "#contact")
    expect(home.form).to_be_in_viewport()


def test_tc009_hero_cta_goes_to_form(page: Page, home):
    home.hero_cta_pair.click()
    assert_scrolled_to(page, "#contact")


def test_tc010_hero_cta_goes_to_services(page: Page, home):
    home.hero_cta_services.click()
    assert_scrolled_to(page, "#services")


@pytest.mark.parametrize("service_id", ["service-1-cta", "service-2-cta", "service-3-cta"])
def test_tc011_choose_format_buttons_go_to_form(page: Page, home, service_id):
    page.locator(f"#{service_id}").click()
    assert_scrolled_to(page, "#contact")


@pytest.mark.parametrize("link,anchor", [
    ("Залишити запит", "#contact"),
    ("Персональна консультація", "#contact"),
    ("Дегустація для компанії", "#contact"),
    ("Підбір до вашого меню", "#contact"),
])
def test_tc013_footer_links(page: Page, home, link, anchor):
    home.footer.get_by_role("link", name=link, exact=True).click()
    assert_scrolled_to(page, anchor)
