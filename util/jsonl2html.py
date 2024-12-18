import pandas as pd
import json


def save_to_html(jsonl_file_path):
    # 读取 jsonl 文件
    data = []

    with open(jsonl_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data.append(json.loads(line))

    # 转换为 DataFrame
    df = pd.DataFrame(data)

    # 提取 request 和 response 字段中的 'format' 数据
    def extract_request_format(request_data):
        try:
            # 如果 request_data 是字典，提取 format 字段
            if isinstance(request_data, dict) and 'format' in request_data:
                return request_data['format']
            # 如果 request_data 是字符串形式的 JSON
            elif isinstance(request_data, str):
                request_json = json.loads(request_data)
                return request_json.get('format', 'N/A')
        except (json.JSONDecodeError, TypeError):
            return 'N/A'

    # 仅展示 request 中的 format
    if 'request' in df.columns:
        df['request'] = df['request'].apply(extract_request_format)

    # 仅展示 response 中的 format
    if 'response' in df.columns:
        df['response'] = df['response'].apply(extract_request_format)

    # 生成 HTML，支持自动换行
    html_output = df.to_html(classes='table table-striped table-bordered', escape=False)

    # 包装 HTML 为完整文档，添加美化和搜索功能
    html_page = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JSONL Data Viewer</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <link rel="stylesheet" href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.min.css">
        <script src="https://code.jquery.com/jquery-3.5.1.js"></script>
        <script src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>
        <style>
            body {{
                padding: 20px;
                background-color: #f8f9fa;
            }}
            h1 {{
                margin-bottom: 20px;
            }}
            table {{
                margin-top: 20px;
            }}
            table td, table th {{
                word-wrap: break-word;
                max-width: 300px;
                white-space: pre-wrap;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="text-center">JSONL Data Viewer</h1>
            <div class="table-responsive">
                {html_output}
            </div>
        </div>
    
        <script>
            $(document).ready(function() {{
                $('table').DataTable();
            }});
        </script>
    </body>
    </html>
    """

    # 保存 HTML 文件
    output_path = './rendered_jsonl_wrapped_response.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_page)

    print(f"HTML 文件已保存到: {output_path}")
