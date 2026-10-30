"""TC-020..036: форма «Отримати підбір пари» (pairing-request).

Усі POST перехоплюються фікстурою `capture`: реальні дані на Netlify не відправляються.
"""
import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.form

VALID_NAME = "Олена"
VALID_EMAIL = "olena@example.com"


def validity(field, flag: str) -> bool:
    return field.evaluate(f"el => el.validity.{flag}")


# ---- позитивні сценарії -------------------------------------------------------
def test_tc020_submit_with_valid_data(home, capture):
    home.scroll_to_form()
    home.fill_form(VALID_NAME, VALID_EMAIL, "вечеря на шістьох, до 1500 грн").submit_form()
    capture.wait_for(1)
    assert capture.last_fields == {
        "form-name": "pairing-request",
        "bot-field": "",
        "name": VALID_NAME,
        "email": VALID_EMAIL,
        "message": "вечеря на шістьох, до 1500 грн",
    }


def test_tc021_submit_without_optional_message(home, capture):
    home.fill_form(VALID_NAME, VALID_EMAIL).submit_form()
    capture.wait_for(1)
    assert capture.last_fields["message"] == ""


def test_tc024_name_with_two_chars_is_accepted(home, capture):
    home.fill_form("Ол", VALID_EMAIL).submit_form()
    capture.wait_for(1)
    assert capture.last_fields["name"] == "Ол"


# ---- негативна валідація ------------------------------------------------------
def test_tc022_empty_name_blocks_submit(home, capture):
    home.fill_form("", VALID_EMAIL).submit_form()
    assert validity(home.name, "valueMissing")
    capture.assert_none_sent()


def test_tc023_one_char_name_is_rejected_minlength(home, capture):
    home.fill_form("А", VALID_EMAIL).submit_form()
    assert validity(home.name, "tooShort")
    capture.assert_none_sent()


def test_tc025_empty_email_blocks_submit(home, capture):
    home.fill_form(VALID_NAME, "").submit_form()
    assert validity(home.email, "valueMissing")
    capture.assert_none_sent()


@pytest.mark.parametrize("bad_email", ["abc", "abc@", "@example.com", "a b@example.com", "abc@@example.com"])
def test_tc026_invalid_email_formats_rejected(home, capture, bad_email):
    home.fill_form(VALID_NAME, bad_email).submit_form()
    assert not home.email.evaluate("el => el.checkValidity()"), f"{bad_email!r} прийнято"
    capture.assert_none_sent()


@pytest.mark.bug
@pytest.mark.xfail(strict=True, reason="BUG-002: ім'я з одних пробілів проходить валідацію (minlength без trim)")
def test_tc027_whitespace_only_name_is_rejected(home, capture):
    home.fill_form("   ", VALID_EMAIL).submit_form()
    capture.assert_none_sent()


# ---- нестандартні дані --------------------------------------------------------
def test_tc028_special_characters_are_sent_intact(home, capture):
    name = "О'Коннор Ім’я 🍷"
    message = "<b>& \"лапки\" 'апостроф' > 5"
    home.fill_form(name, VALID_EMAIL, message).submit_form()
    capture.wait_for(1)
    assert capture.last_fields["name"] == name
    assert capture.last_fields["message"] == message


def test_tc029_xss_payload_is_not_executed(page: Page, home, capture):
    dialogs = []
    page.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))
    payload = "<script>alert(1)</script><img src=x onerror=alert(2)>"
    home.fill_form(payload, VALID_EMAIL, payload).submit_form()
    capture.wait_for(1)
    page.wait_for_timeout(300)
    assert dialogs == [], f"Виконався скрипт: {dialogs}"


def test_tc030_very_long_message(home, capture):
    long_text = "сир " * 1250  # 5000 символів
    home.fill_form(VALID_NAME, VALID_EMAIL, long_text).submit_form()
    capture.wait_for(1)
    assert len(capture.last_fields["message"]) == len(long_text)


# ---- honeypot, label, Netlify ------------------------------------------------
def test_tc031_honeypot_is_hidden_from_users(home):
    expect(home.honeypot).to_be_hidden()
    expect(home.honeypot).to_have_attribute("name", "bot-field")


@pytest.mark.parametrize("label_for", ["name", "email", "message"])
def test_tc032_labels_focus_their_fields(page: Page, home, label_for):
    home.form.locator(f'label[for="{label_for}"]').click()
    expect(page.locator(f"#{label_for}")).to_be_focused()


def test_tc033_form_is_registered_in_netlify(home):
    # Netlify прибирає data-netlify під час деплою і додає hidden form-name: це ознака, що форму зареєстровано
    expect(home.form).to_have_attribute("name", "pairing-request")
    expect(home.form.locator('input[name="form-name"]')).to_have_attribute("value", "pairing-request")


@pytest.mark.bug
@pytest.mark.xfail(strict=False, reason="BUG-003: немає захисту від подвійної відправки (WebKit: 2 POST; "
                                        "у Chromium залежить від таймінгу, тому strict=False)")
def test_tc036_double_click_does_not_send_duplicates(home, capture):
    home.fill_form(VALID_NAME, VALID_EMAIL)
    home.submit.dblclick()
    capture.wait_for(1)
    home.page.wait_for_timeout(500)
    assert capture.count == 1, f"Відправлено {capture.count} запитів замість 1"
