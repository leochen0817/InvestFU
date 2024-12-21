import json
import concurrent.futures


def process_line(line, keyword):
    try:
        data = json.loads(line)
        if keyword in data.get('text', ''):
            return line
    except json.JSONDecodeError:
        print(f"Warning: Could not decode line: {line}")
    return None


def filter_jsonl(input_file, output_file, keyword, batch_size=1000, max_workers=4):
    filtered_lines = []
    with open(input_file, 'r', encoding='utf-8') as infile, \
            open(output_file, 'w', encoding='utf-8') as outfile, \
            concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for line in infile:
            futures.append(executor.submit(process_line, line, keyword))
            # When the number of submitted tasks reaches the batch size, wait for them to complete and write results.
            if len(futures) >= batch_size:
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result is not None:
                        filtered_lines.append(result)
                # Write all filtered lines from this batch to the output file at once.
                outfile.writelines(filtered_lines)
                # Clear the list of filtered lines after writing.
                filtered_lines.clear()
                # Clear the list of futures.
                futures.clear()

        # Process any remaining tasks that were not part of a full batch.
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result is not None:
                filtered_lines.append(result)
        # Write any remaining filtered lines to the output file.
        if filtered_lines:
            outfile.writelines(filtered_lines)
    print("数据处理完成。")


if __name__ == "__main__":
    input_file = "../data/finance_domain/rank_1207.jsonl"  # Replace with your input file path
    output_file = "../data/finance_domain/601318.jsonl"  # Replace with your desired output file path
    keyword = "中国平安"
    batch_size = 1000  # Adjust based on memory constraints and performance needs
    max_workers = 4  # Adjust based on CPU cores available

    filter_jsonl(input_file, output_file, keyword, batch_size, max_workers)
