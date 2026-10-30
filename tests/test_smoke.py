"""TC-001..005, TC-048: сайт живий, базові метадані."""
import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.smoke


def test_tc001_page_loads_with_title_and_h1(page: Page, home):
    expect(page).to_have_title(re.compile(r"Підбір сиру та вина: каталог і рекомендації \| Гурман-Інфо"))
    expect(home.h1).to_have_text("Ідеальна гастрономічна пара для вашого вечора")


def test_tc002_no_console_errors_or_failed_own_requests(page: Page):
    errors, failed = [], []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("response", lambda r: failed.append(f"{r.status} {r.url}")
            if r.status >= 400 and r.url.startswith("https://gourmet-info.netlify.app") else None)
    page.goto("/", wait_until="load")
    assert errors == [], f"Помилки в консолі: {errors}"
    assert failed == [], f"Невдалі запити до власного домену: {failed}"


def test_tc003_all_images_load(page: Page, home):
    # ліниві зображення (loading=lazy) підвантажуються лише після прокрутки
    page.evaluate("""async () => {
        for (let y = 0; y < document.body.scrollHeight; y += 600) {
            window.scrollTo(0, y);
            await new Promise(r => setTimeout(r, 120));
        }
        window.scrollTo(0, 0);
    }""")
    page.wait_for_function("[...document.images].every(i => i.complete)")
    broken = page.evaluate("[...document.images].filter(i => i.naturalWidth === 0).map(i => i.src)")
    assert broken == [], f"Зламані зображення: {broken}"


def test_tc004_unknown_page_returns_404(page: Page):
    response = page.goto("/no-such-page")
    assert response is not None and response.status == 404


def test_tc005_http_redirects_to_https_and_hsts_present(page: Page):
    response = page.request.get("http://gourmet-info.netlify.app/", max_redirects=0)
    assert response.status in (301, 302, 307, 308)
    assert response.headers["location"].startswith("https://")
    https = page.request.get("https://gourmet-info.netlify.app/")
    assert "strict-transport-security" in https.headers


def test_tc048_meta_description_and_favicon(page: Page, home):
    description = page.locator('meta[name="description"]')
    expect(description).to_have_attribute("content", re.compile(r".{50,}"))
    favicon = page.locator('link[rel="icon"]')
    href = favicon.get_attribute("href")
    assert page.request.get(f"/{href}").ok, "favicon не завантажується"
