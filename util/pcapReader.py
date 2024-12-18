import time

import binascii
import pyshark

from util.jsonl2html import save_to_html
from webshell.Behinder import Behinder
from util.formater import format_request_data, format_response_data
import jsonlines


class StreamingJSONLWriter:
    def __init__(self, file_path):
        self.file_path = file_path
        self.writer = jsonlines.open(file_path, mode='w')

    def write_item(self, item):
        self.writer.write(item)

    def close(self):
        self.writer.close()

    @staticmethod
    def _default(obj):
        if isinstance(obj, bytes):
            return obj.decode('utf-8', errors='ignore')
        return str(obj)


def pcapRead(pcapFile, url_path, key, script_type, encode_type):
    global obj
    json_file_path = f'{pcapFile}_decrypted.jsonl'
    if script_type == "jsp":
        obj = Behinder()
        obj.set_url(url_path)
        obj.set_key(key)

    pcapData = pyshark.FileCapture(
        pcapFile,
        display_filter=f'http.request.uri contains "{url_path}"',
        use_json=True,
        include_raw=True
    )
    packet_count = 0
    json_writer = StreamingJSONLWriter(json_file_path)
    sessions = {}

    for packet in pcapData:
        packet_count += 1
        try:
            http_layer = packet.http
            tcp_layer = packet.tcp
            tcp_stream = packet.tcp.stream
            req_num = int(tcp_layer.nxtseq)
            resp_num = int(tcp_layer.ack)
            full_http_data = packet.http_raw.value + http_layer.file_data_raw[0]
            # 处理HTTP请求
            if not hasattr(http_layer, 'response'):
                # console.print(f"[yellow]发现请求[/yellow]: TCP流: {tcp_stream}, Req_Num: {req_num}")

                if req_num not in sessions.keys():
                    sessions[req_num] = {}

                if hasattr(http_layer, 'full_uri'):
                    sessions[req_num]['url'] = http_layer.full_uri

                # 从 full_http_data 中获取请求方法
                http_data_first_line = binascii.unhexlify(full_http_data[:20])
                method = http_data_first_line.split(b' ', 1)[0].decode('utf-8', errors='ignore')

                sessions[req_num]['method'] = method
                request_data = None
                if hasattr(http_layer, 'file_data_raw'):
                    request_data = http_layer.file_data_raw[0]
                if request_data:
                    obj.set_data(request_data)
                    obj.set_script_type(script_type)
                    obj.set_encode_type(encode_type)
                    decrypted_request = obj.decrypted_data()
                    if decrypted_request:
                        formatted_request = format_request_data(decrypted_request, script_type)
                        sessions[req_num]['request'] = {
                            'raw_data_hex': full_http_data,
                            'decrypted_data_hex': decrypted_request.hex(),
                            'format': formatted_request
                        }
                        # print(sessions)
                        # console.print("[green]格式化后的请求:[/green]")
                        # console.print(truncate_long_values(formatted_request, max_length=50, max_items=10))
                    else:
                        # console.print(f"[red]无法解密请求数据[/red]: TCP流: {tcp_stream}, Req_Num: {req_num}")
                        pass
                else:
                    pass

            elif hasattr(http_layer, 'response'):
                if resp_num not in sessions.keys():
                    sessions[resp_num] = {}

                    # 从 full_http_data 中获取请求方法
                http_data_first_line = binascii.unhexlify(full_http_data[:50])
                if len(http_data_first_line.split(b' ', 1)) > 1:
                    method = http_data_first_line.split(b' ')[1].decode('utf-8', errors='ignore')
                else:
                    method = "未知方法"
                sessions[resp_num]['code'] = method
                response_data = None
                if hasattr(http_layer, 'file_data_raw'):
                    response_data = http_layer.file_data_raw[0]

                if response_data:
                    obj.set_data(response_data)
                    decrypted_response = obj.decrypted_data()
                    if decrypted_response:
                        formatted_response = format_response_data(decrypted_response)
                        sessions[resp_num]['response'] = {
                            'raw_data_hex': full_http_data,
                            'decrypted_data_hex': response_data if formatted_response == decrypted_response else decrypted_response.hex(),
                            'format': formatted_response
                        }
                        # console.print("[green]格式化后的响应:[/green]")
                        # console.print(truncate_long_values(formatted_response))
                    else:
                        # console.print(f"[red]无法解密响应数据[/red]: Resp_Num {resp_num}")
                        pass
                else:
                    # console.print(f"[red]无法获取响应数据, 响应中没有数据.[/red]: Resp_Num {resp_num}")
                    pass

                # 检查是否存在对应的请求
                if 'request' in sessions[resp_num]:
                    # 写入完整的会话数据
                    json_writer.write_item(sessions[resp_num])
                    del sessions[resp_num]  # 从sessions字典中删除已写入的会话
                else:
                    # console.print(f"[yellow]警告: 响应 {resp_num} 没有对应的请求，暂不写入[/yellow]")
                    pass
        except Exception as e:
            # console.print(f"[bold red]处理数据包时出错[/bold red]: {e}")
            continue

        # console.print(f"-" * 50)

        # 每处理 5 个数据包更新一次状态
        if packet_count % 5 == 0:
            # status.update(f"[bold green]已分析 {packet_count} 个数据包...")
            time.sleep(0.1)

    # console.print(f"\n总共分析了 [bold]{packet_count}[/bold] 个数据包")

    # 处理未匹配的请求和响应
    for session_key, session in sessions.items():
        # console.print(f"[yellow]警告: 找到未匹配的会话[/yellow]: {session_key}")
        json_writer.write_item(session)

    # 关闭文件
    json_writer.close()
    save_to_html(json_file_path)

# console.print(f"[bold green]解密结果已保存到文件: {json_file_path}[/bold green]")
