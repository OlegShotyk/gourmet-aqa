"""TC-050: заголовки безпеки у відповіді сайту."""
import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.security


def test_tc050_hsts_header_present(page: Page):
    assert "strict-transport-security" in page.request.get("/").headers


@pytest.mark.bug
@pytest.mark.xfail(strict=True, reason="Q3: заголовка немає; рекомендація для _headers / netlify.toml")
@pytest.mark.parametrize("header", [
    "content-security-policy",
    "x-content-type-options",
    "x-frame-options",
])
def test_tc050_recommended_header_present(page: Page, header):
    assert header in page.request.get("/").headers
