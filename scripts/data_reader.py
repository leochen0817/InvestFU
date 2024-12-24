# coding:utf-8
import os
import re
# pip install pypdf
from pypdf import PdfReader, PdfWriter
# pip install python-docx
import docx
import pandas as pd
import markdown
from bs4 import BeautifulSoup
import json


class Colors:
    end = '\033[0m'
    underline = '\033[4m'
    red = '\033[91m'
    green = '\033[92m'
    yellow = '\033[93m'
    blue = '\033[94m'
    magenta = '\033[95m'


def read_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                text = f.read()
        except Exception as e:
            text = None
    return text


# 发现pdfplubmber<=0.11.4的版本(2024.8.19更新)有bug：有些pdf无法读取到空格，
def read_pdf_pdfplumber(file_path):
    try:
        import pdfplumber
        text = None
        pdf = pdfplumber.open(file_path)
        pages = pdf.pages
        for i in range(len(pages)):
            t = pages[i].extract_text()
            text = text + t if text else t
        return text
    except Exception as e:
        print(e)
        return None


def read_pdf(file_path):
    try:
        text = None
        reader = PdfReader(file_path)
        pages_number = len(reader.pages)
        for i in range(pages_number):
            page = reader.pages[i]
            t = page.extract_text()
            text = text + t if text else t
    except Exception as e:
        print(f'{Colors.red}无法读取PDF文件：{file_path}{Colors.end}')
        text = None
    return text


def read_docx(file_path):
    try:
        file = docx.Document(file_path)
        text = None
        for para in file.paragraphs:
            para_text = para.text
            text = text + para_text if text else para_text
    except Exception as e:
        print(f'{Colors.red}无法读取WORD文件：{file_path}{Colors.end}')
        text = None
    return text


def read_excel(file_path):
    try:
        d = pd.read_excel(file_path)
        text = d.to_json(orient='records', index=None, force_ascii=False, lines=True)
        text = text.replace('\\n', '').replace('"', '').replace('{','').replace('}', '')
    except Exception as e:
        print(f'{Colors.red}无法读取EXCEL文件：{file_path}{Colors.end}')
        text = None
    return text


def read_csv(file_path):
    try:
        # 暂编码方式：utf-8
        d = pd.read_csv(file_path, header=0, encoding='utf-8')
        text = d.to_json(orient='records', index=None, force_ascii=False, lines=True)
        text = text.replace('\\n', '').replace('"', '')
    except Exception as e:
        print(f'{Colors.red}无法读取CSV文件：{file_path}{Colors.end}')
        text = None
    return text


def read_csv_to_json(file_path):
    try:
        # 尝试使用指定的编码读取 CSV 文件
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        # 如果读取失败，尝试使用 'latin1' 编码
        df = pd.read_csv(file_path, encoding='gbk')
    df = df.fillna('')
    result_dict = df.to_dict(orient='records')
    return result_dict


def read_pdf_pymupdf4llm_to_md(file_path):
    import pymupdf4llm      # pip install pymupdf4llm==0.0.17
    return pymupdf4llm.to_markdown(file_path)


def read_markdown(file_path):
    # 读取 Markdown 文件
    with open(file_path, 'r', encoding='utf-8') as file:
        markdown_text = file.read()
    # 将 Markdown 转换为 HTML
    html = markdown.markdown(markdown_text)
    # 使用BeautifulSoup提取HTML中的文本
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    # 输出纯文本
    return text.replace('\n', '')


def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        # 文件内容解析为 Python 对象（字典或列表）
        data = json.load(file)
    return data


def read_data(file_path):
    if not os.path.exists(file_path):
        return None
    data = []
    json_array = []
    for file_name in os.listdir(file_path):
        if file_name.startswith('~$') or file_name.startswith('.'):
            continue
        file_title, file_ext = os.path.splitext(file_name)
        file_ext = file_ext.lower()[1:]
        file_path_name = os.path.join(file_path, file_name)
        text = None
        json_data = None
        if file_ext == 'txt':
            text = read_txt(file_path_name)
        elif file_ext == 'pdf':
            # text = read_pdf(file_path_name)
            text = read_pdf_pymupdf4llm_to_md(file_path_name)
        elif file_ext == 'docx':
            text = read_docx(file_path_name)
        elif file_ext == 'xlsx' or file_ext == 'xls':
            text = read_excel(file_path_name)
        elif file_ext == 'md':
            text = read_markdown(file_path_name)
        elif file_ext == 'csv':
            # text = read_csv(file_path_name)
            json_data = read_csv_to_json(file_path_name)
        elif file_ext == 'json':
            json_data = read_json(file_path_name)
        if text:
            text = re.sub(r"\n{3,}", r"\n", text)
            text = re.sub("\n\n", "\n", text)
            data.append(text)
        if json_data:
            if isinstance(json_data, list):
                for dict_data in json_data:
                    json_array.append({file_title: dict_data})
            else:
                json_array.append({file_title: json_data})
    return '\n'.join(data), json_array


if __name__ == '__main__':
    # d = read_data('./data/text')
    d = read_csv_to_json('./data/eastmoney/舆情_东方财富_国内经济.csv')
    print('d = \n', d)

