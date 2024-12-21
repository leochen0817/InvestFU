from playwright.sync_api import Playwright, sync_playwright, expect
import re


def get_ssc_pdf(playwright: Playwright, code_list, period_list):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={"width": 1900, "height": 1000}
    )
    page = context.new_page()

    page.goto("http://www.sse.com.cn/disclosure/listedinfo/announcement/")
    page.wait_for_timeout(2000)
    for code in code_list:
        page.get_by_placeholder("6位代码 / 简称").fill(code)
        page.get_by_placeholder("6位代码 / 简称").press("Enter")
        # 选择 定期报告-年报
        page.get_by_role("listitem").filter(has_text=re.compile(r"^年报$")).locator("span").click()
        page.wait_for_timeout(1000)
        # 勾选 只看公告正文，过滤无效报告
        page.locator(".big-type-title > .iconfont").first.click()
        page.wait_for_timeout(1000)
        # 目前官方是默认三年时间，如需要拉取更早的，需要调整时间控件
        for period in period_list:
            with page.expect_download() as download_info:
                page.locator(".table-responsive").locator(".table_titlewrap").filter(has_text=period).locator(
                    "xpath=../..").locator(".iconfont.iconxiazai").click(button="left")
                download = download_info.value
                suggested_filename = download.suggested_filename
                parts = suggested_filename.split('_')
                final_filename = '_'.join([parts[0], '_'.join(parts[2:])])
                save_path = f"../data/annual_report/{final_filename}"
                print("保存成功，路径为：", save_path)
                download.save_as(save_path)

        page.get_by_text("重置").click()

    context.close()
    browser.close()


if __name__ == "__main__":
    stock_code_list = ["601318"]
    period_list = ["2023", "2022"]
    with sync_playwright() as p:
        get_ssc_pdf(p, stock_code_list, period_list)
