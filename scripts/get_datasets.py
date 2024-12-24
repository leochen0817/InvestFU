import re
import requests
import json


def is_valid_json(data):
    # 如果数据是字符串，尝试解析为 JSON
    if isinstance(data, str):
        try:
            # 解析字符串为 Python 对象
            json.loads(data)
            return True
        except json.JSONDecodeError:
            return False
    # 如果数据已经是列表，直接返回 True
    elif isinstance(data, list):
        return True
    else:
        return False


def text_to_json(text):
    matches = re.findall(r'问题\s*(\d*)[：:](.*?),?答案[：:](.*?)(?=问题\d*|$)', text, re.DOTALL)
    # 组装成JSON数组
    json_array = []
    for match in matches:
        question_num, question, answer = match
        json_array.append(
            {"conversation":
                {
                    "input": f"问题{question_num}：{question}",
                    "output": answer.strip()
                }
            })
    return json_array


def json_to_json(data):
    # 组装成JSON数组
    json_array = []
    for d in data:
        for key, value in d.items():
            if 'entity_info' not in value.keys():
                filename = re.findall(r'\d*_?(.*)$', key)
                event = ''.join(filename)
                event = event.replace('_', '')

                json_array.append(
                    {"conversation":
                        {
                            "input": f"问题：{event}事件",
                            "output": value
                        }
                    })
            elif 'api_type' in value['entity_info'].keys():
                name = value['entity_info']['stock_code']
                event_start_time = value['entity_info']['start_date']
                event_end_time = value['entity_info']['end_date']
                event = value['entity_info']['api_type']
                json_array.append(
                    {"conversation":
                        {
                            "input": f"问题：{name}从{event_start_time}至{event_end_time}的{event}信息",
                            "output": value['data']
                        }
                    })
            else:
                event = value['entity_info']['type']
                name = ''
                event_time = ''
                for data in value['data']:
                    for k, v in data.items():
                        if '日期' in k and k != '公告日期':
                            event_time = v
                        # 检查键是否包含指定的关键词
                        if '简称' in k:
                            name = v

                    json_array.append(
                        {"conversation":
                            {
                                "input": f"问题：{name}{event_time}{event}事件",
                                "output": data
                            }
                        })
    return json_array


def write_json(json_path, content1, content2=None):
    if not is_valid_json(content1):
        # 处理为json格式
        content1 = text_to_json(content1)
    else:
        # json解析
        content1 = json_to_json(content1)

    if content2:
        if not is_valid_json(content2):
            # 处理为json格式
            content2 = text_to_json(content2)
        else:
            # json解析
            content2 = json_to_json(content2)

    content = json.dumps(content1 + content2 if content2 else content1, ensure_ascii=False, indent=4)
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"数据已写入json文件")


def pdf_split(pdf_type, pdf_md):
    """
        :param pdf_type: 年报、研报
        :param pdf_md: md
        :return: list
    """
    text_list = []
    if pdf_type == '研报':
        # 正则表达式匹配 Markdown 标题找到所有的标题
        header_pattern = re.compile(r'^(#{1,6})\s+(.*)', re.MULTILINE)
    elif pdf_type == '年报':
        # 正则表达式匹配 Markdown 标题找到所有的二级标题
        header_pattern = re.compile(r'^(#{1,2})\s+(.*)', re.MULTILINE)
    else:
        return None

    headers = header_pattern.findall(pdf_md)

    # 如果没有标题，直接返回整个文本
    if not headers:
        return [pdf_md.strip()]

    # 将文本按标题切分
    last_end = 0
    for i, (header_level, header_text) in enumerate(headers):
        # 找到标题的位置
        header_start = pdf_md.find(f"{header_level} {header_text}", last_end)
        if header_start == -1:
            continue

        # 获取标题后的内容
        header_end = header_start + len(f"{header_level} {header_text}")
        next_header_level, next_header_text = headers[i+1] if i + 1 < len(headers) else headers[-1]
        next_header = pdf_md.find(f"{next_header_level} {next_header_text}", header_end) if i + 1 < len(headers) else -1
        if next_header == -1:
            content = pdf_md[header_end:].strip()
        else:
            content = pdf_md[header_end:next_header].strip()

        # 如果是年报，拼接一级标题
        if pdf_type == '年报':
            # 找到一级标题（#）
            first_level_header_pattern = re.compile(r'^# (.*)', re.MULTILINE)
            first_level_header = first_level_header_pattern.search(pdf_md[:header_start])
            if first_level_header:
                first_level_text = first_level_header.group(1)
                text_list.append(f"{first_level_text}\n{header_text}\n{content}")
            else:
                text_list.append(f"{header_text}\n{content}")
        else:
            # 如果是研报，直接添加标题和内容
            text_list.append(f"{header_text}\n{content}")

        # 更新 last_end
        last_end = header_end

    return text_list


if __name__=="__main__":
    from scripts.data_reader import *

    file_path = '../data/finance_event'
    output_path = '../data/datasets/pretrain_data_finance_event.json'
    text1, text2 = read_data(file_path)
    write_json(output_path, text2)

    file_path = '../data/market_data'
    output_path = '../data/datasets/pretrain_data_market_data.json'
    text1, text2 = read_data(file_path)
    write_json(output_path, text2)

    file_path = '../data/public_sentiment'
    output_path = '../data/datasets/pretrain_data_public_sentiment.json'
    text1, text2 = read_data(file_path)
    write_json(output_path, text1, text2)

    file_path = '../data/finance_domain'
    output_path = '../data/datasets/pretrain_data_finance_domain.json'
    text1, text2 = read_data(file_path)
    write_json(output_path, text1)
