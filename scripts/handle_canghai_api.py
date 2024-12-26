import requests
import json

from scripts.utils.date_utils import get_previous_workday_with_holidays


def invoke_remote_api(token, stock_code, start_date, end_date, api_type):
    entity_info_dict = {
        "stock_code": stock_code,
        "api_type": "历史行情",
        "start_date": start_date,
        "end_date": end_date
    }

    # 调用沧海数据接口获取历史日线行情数据
    url = f"https://tsanghi.com/api/fin/stock/XSHG/daily?token={token}&ticker={stock_code}&start_date={start_date}&end_date={end_date}&order=1"
    reponse_dict = requests.get(url).json()
    reponse_dict["entity_info"] = entity_info_dict

    file_path = f"../data/market_data/{stock_code}_{api_type}.json"
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(reponse_dict, file, ensure_ascii=False, indent=4)

    print(f"数据已成功写入 {file_path}")


if __name__ == "__main__":
    # 请到 https://tsanghi.com/ 注册账号，并复制token
    token = ""
    stock_code = "601318"
    start_date = "2024-01-01"
    end_date = get_previous_workday_with_holidays()
    api_type = "history_daily_data"
    invoke_remote_api(token, stock_code, start_date, end_date, api_type)
