import csv
from playwright.sync_api import Playwright, sync_playwright, expect


# 获取东方财富 全球动态的新闻
def get_qqdu_info(playwright: Playwright):
    file_path = "../data/public_sentiment/舆情_东方财富_全球动态.csv"
    with open(file_path, "a", encoding="gbk", newline="") as f:
        csv_writer = csv.writer(f)
        name = ["来源", "类型", "标题", "简述", "内容"]
        csv_writer.writerow(name)

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={"width": 1900, "height": 1000}
    )
    page = context.new_page()

    # 获取前3页的你数据
    for i in range(1, 4):
        url = "https://global.eastmoney.com/a/cqqdd_" + str(i) + ".html"
        page.goto(url)
        page.wait_for_load_state()
        page.wait_for_timeout(2000)

        full_div_element = page.locator(".repeatList")
        content_div_element = full_div_element.get_by_role("listitem")
        page_size = content_div_element.count()

        for j in range(page_size):
            title = page.locator("ul#newsListContent").get_by_role("listitem").nth(j).get_by_role(
                "link").last.inner_text()
            short_summary = page.locator("ul#newsListContent").get_by_role("listitem").nth(j).locator(
                "p.info").get_attribute("title")
            print("title:", title)
            print("short_summary:", short_summary)

            with page.expect_popup() as popup_info:
                page.locator("ul#newsListContent").get_by_role("listitem").nth(j).get_by_role("link").last.click()
            pop_page = popup_info.value
            pop_page.wait_for_load_state()
            content = pop_page.locator("div#ContentBody").inner_text()
            pop_page.close()

            try:
                with open(file_path, "a", encoding="gbk", newline="") as f:
                    csv_writer = csv.writer(f)
                    list = []
                    list.append("东方财富")
                    list.append("全球导读")
                    list.append(title)
                    list.append(short_summary)
                    list.append(content)
                    csv_writer.writerow(list)
                    f.close()
            except:
                continue
    print(f"数据已成功写入 {file_path}")
    context.close()
    browser.close()


# 获取东方财富 国内经济新闻
def get_gnjj_info(playwright: Playwright):
    file_path = "../data/public_sentiment/舆情_东方财富_国内经济.csv"
    with open(file_path, "a", encoding="gbk", newline="") as f:
        csv_writer = csv.writer(f)
        name = ["来源", "类型", "标题", "简述", "内容"]
        csv_writer.writerow(name)

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={"width": 1900, "height": 1000}
    )
    page = context.new_page()

    # 获取前3页的你数据
    for i in range(1, 4):
        url = "https://finance.eastmoney.com/a/cgnjj_" + str(i) + ".html"
        page.goto(url)
        page.wait_for_load_state()
        page.wait_for_timeout(2000)

        full_div_element = page.locator(".repeatList")
        content_div_element = full_div_element.get_by_role("listitem")
        page_size = content_div_element.count()

        for j in range(page_size):
            title = page.locator("ul#newsListContent").get_by_role("listitem").nth(j).get_by_role(
                "link").last.inner_text()
            short_summary = page.locator("ul#newsListContent").get_by_role("listitem").nth(j).locator(
                "p.info").get_attribute("title")
            print("title:", title)
            print("short_summary:", short_summary)

            with page.expect_popup() as popup_info:
                page.locator("ul#newsListContent").get_by_role("listitem").nth(j).get_by_role("link").last.click()
            pop_page = popup_info.value
            pop_page.wait_for_load_state()
            content = pop_page.locator("div#ContentBody").inner_text()
            pop_page.close()

            try:
                with open(file_path, "a", encoding="gbk", newline="") as f:
                    csv_writer = csv.writer(f)
                    list = []
                    list.append("东方财富")
                    list.append("国内经济")
                    list.append(title)
                    list.append(short_summary)
                    list.append(content)
                    csv_writer.writerow(list)
                    f.close()
            except:
                continue
    print(f"数据已成功写入 {file_path}")
    context.close()
    browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        get_gnjj_info(playwright)
        get_qqdu_info(playwright)
