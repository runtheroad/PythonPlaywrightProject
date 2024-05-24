import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import datetime
import os
import allure
from allure_commons.types import AttachmentType

TARGET_URL = os.getenv('TARGET_URL', 'https://news.ycombinator.com')
REPORT_DIR = os.getenv('REPORT_DIR', 'reports')


async def save_hacker_news_articles():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        with allure.step("Go to target URL"):
            await page.goto(TARGET_URL)

        with allure.step("Extract article titles and URLs"):
            articles = []
            items = await page.query_selector_all('.athing')

            for item in items:

                title_element = await item.query_selector('.titleline a')
                title_text = await title_element.inner_text()
                title_href = await title_element.get_property('href')
                articles.append({'title': title_text, 'url': title_href})

                if len(articles) >= 10:
                    break

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(REPORT_DIR, f'hacker_news_articles_{timestamp}.csv')

        os.makedirs(REPORT_DIR, exist_ok=True)

        with allure.step("Save articles to CSV"):
            df = pd.DataFrame(articles)
            df.to_csv(filename, index=False)
            allure.attach.file(filename, name="10 Latest Hacker News Articles", attachment_type=AttachmentType.CSV)

        await browser.close()


if __name__ == "__main__":
    os.makedirs(REPORT_DIR, exist_ok=True)
    asyncio.run(save_hacker_news_articles())
