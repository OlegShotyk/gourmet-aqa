"""Спільні фікстури.

Важливо: форма «Отримати підбір пари» на проді надсилає реальний POST на Netlify.
Тому в автотестах усі POST-запити ПЕРЕХОПЛЮЮТЬСЯ (mock) і нічого не потрапляє на сервер.
"""
from urllib.parse import parse_qs

import pytest

from pages.home_page import HomePage

SITE = "https://gourmet-info.netlify.app"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "locale": "uk-UA",
        "timezone_id": "Europe/Kyiv",
        "viewport": {"width": 1280, "height": 800},
    }


@pytest.fixture
def home(page) -> HomePage:
    return HomePage(page).open()


class FormCapture:
    """Збирає перехоплені POST-запити форми."""

    def __init__(self, page=None):
        self.requests = []
        self._page = page

    @property
    def count(self) -> int:
        return len(self.requests)

    def wait_for(self, n: int = 1, timeout_ms: int = 5000) -> None:
        """Чекає, поки буде перехоплено щонайменше n POST-запитів."""
        waited = 0
        while self.count < n and waited < timeout_ms:
            self._page.wait_for_timeout(50)
            waited += 50
        assert self.count >= n, f"Очікувалось ≥{n} POST, перехоплено {self.count}"

    def assert_none_sent(self, settle_ms: int = 400) -> None:
        """Негативна перевірка: даємо браузеру короткий час і переконуємось, що POST не пішов."""
        self._page.wait_for_timeout(settle_ms)
        assert self.count == 0, f"Форма відправилась, хоча не мала: {self.last_fields}"

    @property
    def last_fields(self) -> dict:
        raw = self.requests[-1].post_data or ""
        return {k: v[0] for k, v in parse_qs(raw, keep_blank_values=True).items()}


@pytest.fixture
def capture(page) -> FormCapture:
    """Перехоплює будь-який POST і відповідає заглушкою 200, не торкаючись сервера."""
    cap = FormCapture(page)

    def handler(route):
        request = route.request
        # Лише відправка САМОЇ форми: навігаційний POST на домен сайту.
        # (Сторонні POST, напр. аналітика віджета погоди, форму не стосуються.)
        is_form_post = (request.method == "POST"
                        and request.is_navigation_request()
                        and request.url.startswith(SITE))
        if is_form_post:
            cap.requests.append(request)
            route.fulfill(status=200, content_type="text/html; charset=utf-8",
                          body="<html><body><h1>mock: form accepted</h1></body></html>")
        else:
            route.continue_()

    page.route("**/*", handler)
    return cap


@pytest.fixture
def block_third_party(page):
    """Не ходимо до YouTube/Google Maps/forecast7 у тестах: вони поза межами тестування."""
    for pattern in ("**/*youtube*/**", "**/maps.google.com/**", "**/forecast7.com/**",
                    "**/weatherwidget.io/**"):
        page.route(pattern, lambda route: route.fulfill(status=200, body=""))
