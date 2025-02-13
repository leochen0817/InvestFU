import pandas as pd
import traceback
import json


# 清理每个单元格内容的头尾空格和制表符
def data_clean(content):
    import re
    if isinstance(content, str):
        # 提取标签之间的内容（使用非贪婪模式）
        match = re.search(r'<[^>]+>(.*?)</[^>]+>', content)
        if match:
            # 如果找到匹配的标签内容，提取并清理空白字符
            cleaned_content = match.group(1).strip()
            # 去除制表符
            cleaned_content = cleaned_content.replace('\t', '')
            return cleaned_content
        # 如果没有找到HTML标签，则直接清理空白字符
        return content.strip().replace('\t', '')
    return content


def excel_to_xtuner_format(input_excel_file, output_jsonl_file, system_message):
    try:
        # 读取输入的Excel文件
        df = pd.read_excel(input_excel_file)
        df = df.fillna('')

        # 写入JSON Lines文件，按照指定格式
        with open(output_jsonl_file, 'w', encoding='utf-8') as outfile:
            for _, row in df.iterrows():
                _instruction = data_clean(str(row.get('instruction', '')))
                _input = data_clean(str(row.get('input', '')))
                # 组合instruction和input
                combined_input = f"{_instruction}\n{_input}" if _input else _instruction
                _output = data_clean(str(row.get('output', '')))
                # 组织conversation数据
                conversation = {
                    "conversation": [
                        {"system": system_message, "input": combined_input, "output": _output}
                    ]
                }
                json.dump(conversation, outfile, ensure_ascii=False)
                outfile.write('\n')

        print(f"Conversion completed. Output saved to {output_jsonl_file}")

    except Exception as e:
        print(f"An error occurred: {traceback.print_exc()}")


if __name__ == "__main__":
    input_file = "../data/annual_report/平安测试数据集.xlsx"
    output_path = "./finetune/data/pingan_xtuner_all.jsonl"
    system_message = "你是一个金融分析师，你根据给定的财报数据，回答用户的问题。"
    excel_to_xtuner_format(input_file, output_path, system_message)
