import json
from datetime import datetime
from playwright.sync_api import sync_playwright, expect, Playwright

now = datetime.now().strftime("%Y%m%d")


# 获取巨潮资讯网 限售解禁的数据
def get_xsjj_info(playwright: Playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={"width": 1900, "height": 1000}
    )
    page = context.new_page()
    page.goto("http://www.cninfo.com.cn/new/commonUrl?url=data/person-stock-data-tables#xsjj")
    page.wait_for_timeout(2000)

    trade_type = "限售解禁"
    data_dict = {}
    entity_info_dict = {
        "resource": "巨潮资讯",
        "type": trade_type,
    }
    data_dict["entity_info"] = entity_info_dict

    content_list = []
    table_element = page.get_by_role("table").nth(1)
    pagination_element = page.locator(".personalstock-item.oneItem.jc-layout").locator(".el-pager").get_by_role(
        "listitem")
    pagination_count = pagination_element.count()
    for p in range(pagination_count):
        pagination_element.nth(p).click()
        expect(pagination_element.nth(p)).to_have_attribute("class", "number active")
        row_count = table_element.get_by_role("row").count()
        for row in range(row_count):
            row_data = table_element.get_by_role("row").nth(row)
            stock_code = row_data.get_by_role("cell").nth(0).text_content()
            stock_name = row_data.get_by_role("cell").nth(1).text_content()
            announce_date = row_data.get_by_role("cell").nth(2).text_content()
            xsjj_date = row_data.get_by_role("cell").nth(3).text_content()
            xsjj_amount = row_data.get_by_role("cell").nth(4).text_content()
            xsjj_rate = row_data.get_by_role("cell").nth(5).text_content()
            stock_amount = row_data.get_by_role("cell").nth(6).text_content()

            row_dict = {
                "股票代码": stock_code,
                "股票简称": stock_name,
                "公告日期": announce_date,
                "实际解除限售日期": xsjj_date,
                "实际解除限售数量": xsjj_amount,
                "实际解除限售比例": xsjj_rate,
                "实际可流通数量": stock_amount
            }
            content_list.append(row_dict)

    data_dict["data"] = content_list
    file_path = f"../data/finance_event/巨潮资讯_" + str(now) + f"_{trade_type}.json"
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data_dict, file, ensure_ascii=False, indent=4)

    print(f"数据已成功写入 {file_path}")

    context.close()
    browser.close()


# 获取巨潮资讯网 股东增持的数据
def get_gdzc_info(playwright: Playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={"width": 1900, "height": 1000}
    )
    page = context.new_page()
    page.goto("http://www.cninfo.com.cn/new/commonUrl?url=data/person-stock-data-tables#gdzjc")
    page.wait_for_timeout(2000)

    trade_type = "股东增持"
    data_dict = {}
    entity_info_dict = {
        "resource": "巨潮资讯",
        "type": trade_type,
    }
    data_dict["entity_info"] = entity_info_dict

    content_list = []
    table_element = page.get_by_role("table").nth(1)
    pagination_element = page.locator(".personalstock-item.oneItem.jc-layout").locator(".el-pager").get_by_role(
        "listitem")
    pagination_count = pagination_element.count()
    for p in range(pagination_count):
        pagination_element.nth(p).click()
        expect(pagination_element.nth(p)).to_have_attribute("class", "number active")
        row_count = table_element.get_by_role("row").count()
        for row in range(row_count):
            row_data = table_element.get_by_role("row").nth(row)
            announce_date = row_data.get_by_role("cell").nth(0).text_content()
            stock_code = row_data.get_by_role("cell").nth(1).text_content()
            stock_name = row_data.get_by_role("cell").nth(2).text_content()
            increase_date = row_data.get_by_role("cell").nth(3).text_content()
            holder_name = row_data.get_by_role("cell").nth(4).text_content()
            increase_amount = row_data.get_by_role("cell").nth(5).text_content()
            increase_rate = row_data.get_by_role("cell").nth(6).text_content()
            increase_price = row_data.get_by_role("cell").nth(7).text_content()

            row_dict = {
                "公告日期": announce_date,
                "证券代码": stock_code,
                "证券简称": stock_name,
                "增持日期": increase_date,
                "股东名称": holder_name,
                "增持数量": increase_amount,
                "增持比例": increase_rate,
                "增持价格": increase_price
            }
            content_list.append(row_dict)

    data_dict["data"] = content_list
    file_path = f"../data/finance_event/巨潮资讯_" + str(now) + f"_{trade_type}.json"
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data_dict, file, ensure_ascii=False, indent=4)

    print(f"数据已成功写入 {file_path}")

    context.close()
    browser.close()


# 获取巨潮资讯网 股东减持的数据
def get_gdjc_info(playwright: Playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={"width": 1900, "height": 1000}
    )
    page = context.new_page()
    page.goto("http://www.cninfo.com.cn/new/commonUrl?url=data/person-stock-data-tables#gdzjc")
    page.wait_for_timeout(2000)

    trade_type = "股东减持"
    data_dict = {}
    entity_info_dict = {
        "resource": "巨潮资讯",
        "type": trade_type,
    }
    data_dict["entity_info"] = entity_info_dict

    content_list = []
    table_element = page.get_by_role("table").nth(3)
    pagination_element = page.locator(".personalstock-item.twoItem.jc-layout").locator(".el-pager").get_by_role(
        "listitem")
    pagination_count = pagination_element.count()
    for p in range(pagination_count):
        pagination_element.nth(p).click()
        expect(pagination_element.nth(p)).to_have_attribute("class", "number active")
        row_count = table_element.get_by_role("row").count()
        for row in range(row_count):
            row_data = table_element.get_by_role("row").nth(row)
            announce_date = row_data.get_by_role("cell").nth(0).text_content()
            stock_code = row_data.get_by_role("cell").nth(1).text_content()
            stock_name = row_data.get_by_role("cell").nth(2).text_content()
            decrease_date = row_data.get_by_role("cell").nth(3).text_content()
            holder_name = row_data.get_by_role("cell").nth(4).text_content()
            decrease_amount = row_data.get_by_role("cell").nth(5).text_content()
            decrease_rate = row_data.get_by_role("cell").nth(6).text_content()
            decrease_price = row_data.get_by_role("cell").nth(7).text_content()

            row_dict = {
                "公告日期": announce_date,
                "证券代码": stock_code,
                "证券简称": stock_name,
                "减持日期": decrease_date,
                "股东名称": holder_name,
                "减持数量": decrease_amount,
                "减持比例": decrease_rate,
                "减持价格": decrease_price
            }
            content_list.append(row_dict)

    data_dict["data"] = content_list
    file_path = f"../data/finance_event/巨潮资讯_" + str(now) + f"_{trade_type}.json"
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data_dict, file, ensure_ascii=False, indent=4)

    print(f"数据已成功写入 {file_path}")

    context.close()
    browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        get_xsjj_info(playwright)
        get_gdzc_info(playwright)
        get_gdjc_info(playwright)
