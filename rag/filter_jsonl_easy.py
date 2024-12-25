import json
import os
import mmap
from typing import Dict, Set, Tuple
from tqdm import tqdm
import orjson
from huggingface_hub import hf_hub_download
import shutil
import gzip

def process_chunk(chunk: list, keywords: Set[str]) -> list:
    """处理数据块"""
    valid_lines = []
    keywords_set = set(keywords)
    
    for line in chunk:
        try:
            if not line.strip():
                continue
            data = orjson.loads(line)
            found_keywords = set()
            
            text_values = ' '.join(str(v) for v in data.values() if isinstance(v, str))
            for keyword in keywords_set:
                if keyword in text_values:
                    found_keywords.add(keyword)
            
            if found_keywords:
                data['matched_keywords'] = list(found_keywords)
                valid_lines.append(data)
                
        except Exception as e:
            continue
    
    return valid_lines

def process_file(input_file: str, output_file: str, keywords: Set[str]) -> Tuple[int, Dict[str, int]]:
    """处理单个文件"""
    kept_lines = 0
    keyword_stats = {keyword: 0 for keyword in keywords}
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(input_file, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        chunk_size = 1024 * 1024  # 1MB chunks
        
        with open(output_file, 'w', encoding='utf-8', buffering=8*1024*1024) as fout:
            current_pos = 0
            
            while current_pos < mm.size():
                mm.seek(current_pos)
                chunk_end = min(current_pos + chunk_size, mm.size())
                chunk_data = mm.read(chunk_end - current_pos)
                
                try:
                    chunk = chunk_data.decode('utf-8').split('\n')
                except UnicodeDecodeError:
                    chunk = chunk_data.decode('utf-8', errors='ignore').split('\n')
                
                valid_lines = process_chunk(chunk, keywords)
                
                for data in valid_lines:
                    kept_lines += 1
                    data['line_number'] = kept_lines
                    fout.write(orjson.dumps(data).decode('utf-8') + '\n')
                    
                    for keyword in data['matched_keywords']:
                        keyword_stats[keyword] += 1
                
                current_pos = chunk_end
        
        mm.close()
    
    return kept_lines, keyword_stats

def download_and_extract(repo_id: str, filename: str, local_dir: str) -> str:
    """从Huggingface下载并解压文件"""
    output_path = os.path.join(local_dir, os.path.dirname(filename))
    os.makedirs(output_path, exist_ok=True)
    
    output_filename = os.path.join(local_dir, filename[:-3] if filename.endswith('.gz') else filename)
    
    print(f"正在从 {repo_id} 下载文件 {filename}")
    compressed_file = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        repo_type="dataset"
    )
    
    if filename.endswith('.gz'):
        print(f"解压文件到 {output_filename}")
        with gzip.open(compressed_file, 'rb') as f_in:
            with open(output_filename, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    return output_filename, compressed_file

def cleanup_files(uncompressed_file: str, compressed_file: str):
    """清理处理完的文件"""
    if os.path.exists(uncompressed_file):
        os.remove(uncompressed_file)
    if os.path.exists(compressed_file):
        os.remove(compressed_file)
    print("已清理临时文件")

def main():
    repo_id = "BAAI/IndustryCorpus_finance"
    files_to_process = [
        "zh/rank_1207.jsonl.gz",
        "zh/rank_1208.jsonl.gz",
        "zh/rank_1209.jsonl.gz",
        "zh/rank_1210.jsonl.gz",
        "zh/rank_1211.jsonl.gz",
        "zh/rank_1212.jsonl.gz",
        "zh/rank_1213.jsonl.gz",
        "zh/rank_1214.jsonl.gz",
        "zh/rank_1215.jsonl.gz",
        "zh/rank_1216.jsonl.gz",
        "zh/rank_1217.jsonl.gz",
        "zh/rank_1218.jsonl.gz",
        "zh/rank_1219.jsonl.gz",
        "zh/rank_1220.jsonl.gz",
        "zh/rank_1221.jsonl.gz",
        "zh/rank_1222.jsonl.gz",
        "zh/rank_1223.jsonl.gz",
        "zh/rank_1224.jsonl.gz",
        "zh/rank_1225.jsonl.gz",
        "zh/rank_1226.jsonl.gz",
        "zh/rank_1227.jsonl.gz",
        "zh/rank_1228.jsonl.gz",
        "zh/rank_1229.jsonl.gz",
        "zh/rank_1230.jsonl.gz",
        "zh/rank_1231.jsonl.gz",
        "zh/rank_1232.jsonl.gz",
        "zh/rank_1233.jsonl.gz",
        "zh/rank_1234.jsonl.gz",
        "zh/rank_1235.jsonl.gz",
        "zh/rank_1236.jsonl.gz",
        "zh/rank_1237.jsonl.gz",
        "zh/rank_1238.jsonl.gz",
        "zh/rank_1239.jsonl.gz",
        "zh/rank_1240.jsonl.gz",
        "zh/rank_1241.jsonl.gz"
    ]
    
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_directory = os.path.join(current_dir, "pingan")
    
    keywords = {"平安"}
    
    print(f"当前启用的关键词: {', '.join(keywords)}")
    
    try:
        for current_file in files_to_process:
            print(f"\n开始处理文件: {current_file}")
            
            # 下载并解压
            uncompressed_file, compressed_file = download_and_extract(repo_id, current_file, current_dir)
            
            # 处理文件
            output_file = os.path.join(output_directory, f"{os.path.basename(current_file)[:-3]}_filtered.jsonl")
            kept_lines, keyword_stats = process_file(uncompressed_file, output_file, keywords)
            
            # 输出统计信息
            print(f"\n处理完成统计:")
            print(f"保留行数: {kept_lines}")
            print("\n关键词匹配统计:")
            for keyword, count in keyword_stats.items():
                print(f"  - {keyword}: {count}行")
            
            # 清理文件
            cleanup_files(uncompressed_file, compressed_file)
            
            print(f"完成处理文件: {current_file}\n")
            
    except Exception as e:
        print(f"程序执行失败: {str(e)}")

if __name__ == "__main__":
    main()
