"""Page Object головної (і єдиної) сторінки Гурман-Інфо.

Локатори взято з реальної розмітки сайту: переважно role/label/aria та data-атрибути,
а не CSS-класи Tailwind (вони часто змінюються).
"""
from playwright.sync_api import Page, Locator

MENU_LINKS = {
    "Переваги": "#benefits",
    "Послуги": "#services",
    "Як це працює": "#how-it-works",
    "Про нас": "#about",
    "Контакти": "#contact",
}


class HomePage:
    def __init__(self, page: Page):
        self.page = page

        # Шапка
        self.header = page.locator("header")
        self.desktop_nav = page.locator('nav[aria-label="Основна навігація"]')
        self.mobile_nav = page.locator('nav[aria-label="Мобільна навігація"]')
        self.mobile_menu = page.locator("#mobile-menu")
        self.menu_toggle = page.locator("[data-menu-toggle]")
        self.logo = self.header.locator('a[href="#top"]').first
        self.header_cta = self.header.locator('a[href="#contact"]', has_text="Підібрати пару").first
        self.skip_link = page.get_by_role("link", name="Перейти до основного вмісту")

        # Hero
        self.h1 = page.locator("h1")
        self.hero_cta_pair = page.get_by_role("link", name="Підібрати смакову пару")
        self.hero_cta_services = page.get_by_role("link", name="Переглянути послуги")

        # Відео
        self.bg_video = page.locator("[data-bg-video]")
        self.video_toggle = page.locator("[data-video-toggle]")
        self.youtube_facade = page.locator("[data-youtube]")
        self.youtube_iframe = page.locator('iframe[src*="youtube"]')
        self.map_iframe = page.locator('iframe[title^="Карта"]')

        # Форма
        self.form = page.locator('form[name="pairing-request"]')
        self.name: Locator = self.form.locator("#name")
        self.email: Locator = self.form.locator("#email")
        self.message: Locator = self.form.locator("#message")
        self.honeypot: Locator = self.form.locator('input[name="bot-field"]')
        self.submit: Locator = self.form.get_by_role("button", name="Отримати підбір пари")

        # Футер
        self.footer = page.locator("footer")

    # ---- дії -------------------------------------------------------------
    def open(self) -> "HomePage":
        self.page.goto("/")
        return self

    def nav_link(self, text: str) -> Locator:
        """Посилання основної (десктопної) навігації у шапці, не у футері."""
        return self.desktop_nav.get_by_role("link", name=text, exact=True)

    def mobile_link(self, text: str) -> Locator:
        return self.mobile_nav.get_by_role("link", name=text, exact=True)

    def fill_form(self, name: str = "", email: str = "", message: str = "") -> "HomePage":
        self.name.fill(name)
        self.email.fill(email)
        self.message.fill(message)
        return self

    def submit_form(self) -> "HomePage":
        self.submit.click()
        return self

    def scroll_to_form(self) -> "HomePage":
        self.form.scroll_into_view_if_needed()
        return self
