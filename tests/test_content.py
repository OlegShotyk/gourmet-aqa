"""TC-040: типографіка та орфографія українського тексту."""
from pathlib import Path
import re

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.content

REPORT = Path("reports/languagetool.txt")


@pytest.mark.parametrize("rule,pattern", [
    ("прямий апостроф замість ’", r"[а-яїєґі]'[а-яїєґі]"),
    ("прямі лапки замість «»", r'"'),
    ("дефіс замість тире", r"\s-\s"),
], ids=["apostrophe", "quotes", "dash"])
def test_tc040_typography(page: Page, home, rule, pattern):
    found = re.findall(rf".{{0,15}}{pattern}.{{0,15}}", home.page.locator("body").inner_text(), re.I)
    assert found == [], f"{rule}: {found}"


def test_tc040_spelling_report(page: Page, home):
    """Лише звіт: LanguageTool хибно спрацьовує на власних назвах, тому тест не падає через знахідки."""
    response = page.request.post("https://api.languagetool.org/v2/check", form={
        "language": "uk",
        "text": home.page.locator("body").inner_text(),
    })
    if not response.ok:
        pytest.skip(f"LanguageTool недоступний: HTTP {response.status}")

    lines = [f"{m['rule']['id']}: {m['context']['text']} -> {m['message']}"
             for m in response.json()["matches"]]
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
