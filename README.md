# gourmet-aqa: автотести для «Гурман-Інфо»

E2E-тести для https://gourmet-info.netlify.app/ на **Python + pytest + Playwright** (патерн Page Object).

## Що всередині
```
gourmet-aqa/
├─ docs/
│  ├─ test-plan.md          # Test Plan
│  ├─ test-cases.xlsx       # 51 тест-кейс + аркуш Summary (формули)
│  ├─ bug-reports.md        # BUG-001..003 і питання до вимог
│  └─ site-snapshot.html    # знімок HTML, за яким писались локатори
├─ pages/home_page.py       # Page Object (локатори: role/label/aria/data-*)
├─ tests/                   # smoke, navigation, responsive, media, form, accessibility
├─ conftest.py              # фікстури: home, capture (mock POST), block_third_party
├─ pytest.ini               # base_url, HTML-звіт, скриншоти при падінні, маркери
└─ .github/workflows/tests.yml
```

## Запуск
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install                                     # Chromium, Firefox, WebKit

pytest                                                 # Chromium за замовчуванням
pytest --browser chromium --browser firefox --browser webkit
pytest -m form                                         # лише форма
pytest -m "smoke or nav"
pytest --headed --slowmo 300                           # дивитись очима
```
Звіт: `reports/report.html`; скриншоти падінь: `reports/artifacts/`.

## Важливі принципи
- **Реальні відправки форми не робляться.** Фікстура `capture` перехоплює POST і відповідає заглушкою, тож у ваш Netlify Forms нічого не потрапляє.
- **Сторонні сервіси** (YouTube, Google Maps, віджет погоди) у тестах блокуються: вони поза межами тестування.
- **Відомі баги** позначені `@pytest.mark.xfail(reason="BUG-00X …")`: тест «червоніє» як xfail, а коли дефект виправлять, `strict=True` повідомить про це (XPASS → FAIL).
- Нумерація `test_tcNNN_*` збігається з ID у `docs/test-cases.xlsx`.

## Результат прогону (2026-10-30)
Chromium 156 + WebKit 27.2: **116 passed, 5 xfailed (відомі баги), 1 xpassed, 0 failed.**
Firefox у середовищі розробки не запускався (TLS-проксі пісочниці); його перевіряє CI.
Перший запуск CI: зелений у Chromium, Firefox і WebKit.
Цифри вище отримано до закриття BUG-001: TC-033 тепер звичайний тест, а не xfail.
TC-034 виконано вручну: заявка дійшла в Netlify Forms, BUG-001 закрито як не баг.
Ручні кейси (TC-035, 038, 039, 040, 046, 049, 050) ще не виконані: див. `docs/test-cases.xlsx`.
