import base64
import json
import re
from jawa.cf import ClassFile
from io import BytesIO
from jawa.constants import String

php_patterns = {
    # 匹配供暖
    'operations': {
        'init': r'main\(\$content\);',
        'info': r'main\(\$whatever\);',
        'command': r'main\(\$cmd,\$path\);',
        'shell': r'main\(\$type,\$bashPath,\$cmd,\$whatever\);',
        'file': r'main\(\$mode,\$path,\$hash,\$blockIndex,\$blockSize,\$content,\$charset,\$newpath,\$createTimeStamp,\$accessTimeStamp,\$modifyTimeStamp\);',
        'portmap': r'main\(\$action,\$targetIP,\$targetPort,\$socketHash,\$remoteIP,\$remotePort,\$extraData\);',
        'socksproxy': r'main\(\$action,\$listenPort,\$socketHash,\$extraData\);',
        'reverseshell': r'main\(\$type,\$ip,\$port\);',
        'database': r'main\(\$type,\$host,\$port,\$user,\$pass,\$database,\$sql\);',
    },

    # 匹配参数
    'args': {
        'mode': r'\$mode="([^"]+)"',
        'path': r'\$path="([^"]+)"',
        'hash': r'\$hash="([^"]+)"',
        'blockIndex': r'\$blockIndex="([^"]+)"',
        'blockSize': r'\$blockSize="([^"]+)"',
        'content': r'\$content="([^"]+)"',
        'charset': r'\$charset="([^"]+)"',
        'newpath': r'\$newpath="([^"]+)"',
        'createTimeStamp': r'\$createTimeStamp="([^"]+)"',
        'accessTimeStamp': r'\$accessTimeStamp="([^"]+)"',
        'modifyTimeStamp': r'\$modifyTimeStamp="([^"]+)"',
        'cmd': r'\$cmd="([^"]+)"',
        'type': r'\$type="([^"]+)"',
        'bashPath': r'\$bashPath="([^"]+)"',
        'whatever': r'\$whatever="([^"]+)"',
        'action': r'\$action="([^"]+)"',
        'targetIP': r'\$targetIP="([^"]+)"',
        'targetPort': r'\$targetPort="([^"]+)"',
        'listenPort': r'\$listenPort="([^"]+)"',
        'socketHash': r'\$socketHash="([^"]+)"',
        'remoteIP': r'\$remoteIP="([^"]+)"',
        'remotePort': r'\$remotePort="([^"]+)"',
        'extraData': r'\$extraData="([^"]+)"',
        'ip': r'\$ip="([^"]+)"',
        'port': r'\$port="([^"]+)"',
        'port': r'\$port="([^"]+)"',
        'host': r'\$host="([^"]+)"',
        'user': r'\$user="([^"]+)"',
        'pass': r'\$pass="([^"]+)"',
        'database': r'\$database="([^"]+)"',
        'sql': r'\$sql="([^"]+)"'
    }
}

# 定义匹配模式
asp_patterns = {
    'init': r'Sub main\(arrArgs\).*?content=arrArgs\(0\).*?echo\(content\).*?End Sub',
    'info': r'Sub main\(arrArgs\).*?on error resume next.*?dim i,ws,Sa,sysenv,envlist,envlists,cpunum,cpuinfo,os',
    'file': r'Sub main\(arrArgs\).*?mode=arrArgs\(0\).*?path=arrArgs\(1\).*?Dim finalResult',
    'command': r'Sub main\(arrArgs\).*?cmd=arrArgs\(0\).*?runCmd\(cmd\).*?End Sub',
    'database': r'Sub main\(arrArgs\).*?on error resume next.*?dbType=arrArgs\(0\).*?host=arrArgs\(1\).*?port=arrArgs\(2\).*?username=arrArgs\(3\).*?pass=arrArgs\(4\).*?database=arrArgs\(5\).*?sql=arrArgs\(6\)'
}


def get_php_operation(category):
    operations = {
        "init": "初始化",
        "info": "信息获取",
        "shell": "虚拟终端",
        "command": "命令执行",
        "file": "文件操作",
        "database": "数据库操作",
        "portmap": "端口转发",
        "socksproxy": "远程Socks代理",
        "reverseshell": "反弹shell",
        "custom_code": "自定义代码执行"
    }
    for key, value in operations.items():
        if key in category:
            return value
    return f"未知操作: {category}"


def get_asp_operation(category):
    operations = {
        "init": "初始化",
        "info": "信息获取",
        "shell": "虚拟终端",
        "command": "命令执行",
        "file": "文件操作",
        "database": "数据库操作",
        "portmap": "端口转发",
        "ReversePortMap": "反向DMZ",
        "RemoteSocksProxy": "远程Socks代理",
        "ConnectBack": "反弹shell",
        "Loader": "DLl加载器",
        "custom_code": "自定义代码执行"
    }
    for key, value in operations.items():
        if key in category:
            return value
    return f"未知操作: {category}"


def get_aspx_operation(source_file_name):
    operations = {
        "Echo.dll": "初始化",
        "BasicInfo.dll": "信息获取",
        "RealCMD.dll": "虚拟终端",
        "Cmd.dll": "命令执行",
        "FileOperation.dll": "文件操作",
        "Database.dll": "数据库操作",
        "PortMap.dll": "端口转发",
        "ReversePortMap.dll": "反向DMZ",
        "RemoteSocksProxy.dll": "远程Socks代理",
        "ConnectBack.dll": "反弹shell",
        "Loader.dll": "DLl加载器",
        "Eval.dll": "自定义代码执行"
    }
    for key, value in operations.items():
        if key in source_file_name:
            return value
    return f"未知操作: {source_file_name}"


def get_jsp_operation(source_file_name):
    operations = {
        "Eval.java": "初始化",
        "BasicInfo.java": "信息获取",
        "RealCMD.java": "虚拟终端",
        "Cmd.java": "命令执行",
        "FileOperation.java": "文件操作",
        "Database.java": "数据库操作",
        "PortMap.java": "端口转发",
        "ReversePortMap.java": "反向DMZ",
        "RemoteSocksProxy.java": "远程Socks代理",
        "ConnectBack.java": "反弹shell",
        "Loader.java": "jar加载器",
        "Eval.java": "自定义代码执行"
    }
    for key, value in operations.items():
        if key in source_file_name:
            return value
    return f"未知操作: {source_file_name}"


def decode_json_value(value):
    if isinstance(value, str):
        try:
            # 尝试进行base64解码
            decoded = base64.b64decode(value, validate=True)
            # 检查解码后的内容是否为有效的UTF-8
            decoded_str = decoded.decode('utf-8')
            return decoded_str
        except (UnicodeDecodeError, base64.binascii.Error):
            # 如果base64解码失败或不是有的UTF-8，保留原值
            return value
    elif isinstance(value, dict):
        return {decode_json_value(k): decode_json_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [decode_json_value(item) for item in value]
    else:
        return value


def format_request_data(request_data, script_type):
    """
    格式化请求数据
    :param request_data: 请求数据
    :param script_type: 脚本类型
    :return: 格式化后的请求数据
    """
    result = {}
    if script_type == 'php':
        request_data = request_data.decode('utf-8', errors='ignore')
        # 首先匹配 base64_decode('...') 模式
        base64_pattern = r"base64_decode\('([^']+)'\)"
        match = re.search(base64_pattern, request_data)

        result = {'operation': ''}

        if match:
            base64_content = match.group(1)
            try:
                decoded_content = base64.b64decode(base64_content, validate=True).decode('utf-8', errors='ignore')
            except:
                decoded_content = f"无法解码: {base64_content[:30]}..."
            matched = False
            for key, pattern in php_patterns['operations'].items():
                match = re.search(pattern, decoded_content)
                if match:
                    matched = True
                    result['operation'] = get_php_operation(key)

            if not matched:
                result['operation'] = get_php_operation('custom_code')
                result['custom_code'] = decoded_content

            for key, pattern in php_patterns['args'].items():
                match = re.search(pattern, decoded_content)
                if match:
                    # 如果有匹配组，使用第一个匹配组，否则使用整个匹配
                    value = match.group(1) if match.groups() else match.group(0)
                    # 尝试 base64 解码
                    try:
                        result[key] = decode_json_value(value)
                    except:
                        result[key] = value
        else:
            # console.print(request_data)
            exit()
            result['operation'] = get_php_operation('custom_code')
            result['custom_code'] = request_data

    elif script_type == 'asp':
        request_data = request_data.decode('utf-8', errors='ignore')

        result = {'operation': ''}
        matched = False
        for category, pattern in asp_patterns.items():
            match = re.search(pattern, request_data, re.S)

            if match:
                matched = True
                main_match = re.search(r'main Array\((.*)\)', request_data)
                if main_match:
                    main_data = main_match.group(1)
                    args = main_data.split(',')
                    decoded_args = []
                    for arg in args:
                        chrs = re.findall(r'chrw\((\d+)\)', arg)
                        decoded_arg = ''.join(chr(int(num)) for num in chrs)
                        decoded_args.append(decoded_arg)

                    result['operation'] = get_asp_operation(category)
                    result[category] = decoded_args

        # 如果没有任何匹配，将原始请求数据保存到 custom_code
        if not matched:
            result['operation'] = get_asp_operation('custom_code')
            result['custom_code'] = request_data

        # 将非空字段添加到result中
        result.update({field: value for field, value in result.items() if value})

    elif script_type == 'aspx':

        source_file_name = ''
        module_pattern = b'\x3C\x4D\x6F\x64\x75\x6C\x65\x3E\x00'
        module_index = request_data.find(module_pattern)
        if module_index != -1:
            end_index = request_data.find(b'\x00', module_index + len(module_pattern))
            if end_index != -1:
                source_file_name = request_data[module_index + len(module_pattern):end_index].decode('utf-8',
                                                                                                     errors='ignore')

        result = {'operation': get_aspx_operation(source_file_name)}

        # 查找最后一个 7E7E7E7E 7E7E
        end_pattern = b'\x7E\x7E\x7E\x7E\x7E\x7E'
        end_index = request_data.rfind(end_pattern)
        if end_index != -1:
            end_content = request_data[end_index + len(end_pattern):].decode('utf-8', errors='ignore')

            # 解析结尾内容
            content_parts = end_content.split(',')
            for part in content_parts:
                key, value = part.split(':')
                try:
                    # 尝试进行base64解码
                    result[key] = base64.b64decode(value, validate=True).decode('utf-8', errors='ignore')
                except:
                    # 如果base64解码失败,保留原值
                    result[key] = value

    elif script_type == 'jsp':
        try:
            # 将字节数据包装成类文件对象
            class_file = BytesIO(request_data)

            # 使用包装后的类文件对象
            cf = ClassFile(class_file)

            source_file = cf.attributes.find_one(name='SourceFile')
            if source_file:
                source_file_name = source_file.source_file.value
            else:
                source_file_name = "Unknown"

            result = {'operation': get_jsp_operation(source_file_name)}

            # 添加从java.py迁移的代码
            init_method = cf.methods.find_one(name='<init>')
            if init_method and init_method.code:
                fields = {
                    'cmd': '', 'path': '', 'content': '', 'whatever': '', 'type': '',
                    'bashPath': '', 'mode': '', 'action': '', 'targetIP': '', 'targetPort': '',
                    'remoteIP': '', 'remotePort': '', 'listenPort': '', 'ip': '', 'port': '',
                    'libPath': '', 'host': '', 'user': '', 'pass': '', 'database': '', 'sql': ''
                }
                last_ldc_value = None

                for instruction in init_method.code.disassemble():
                    if instruction.mnemonic == 'ldc':
                        constant_index = instruction.operands[0].value
                        constant = cf.constants.get(constant_index)
                        if isinstance(constant, String):
                            last_ldc_value = cf.constants.get(constant.string.index).value

                    elif instruction.mnemonic == 'putstatic':
                        constant_index = instruction.operands[0].value
                        constant = cf.constants.get(constant_index)
                        field_ref = constant.name_and_type
                        if field_ref.name.value in fields and last_ldc_value is not None:
                            try:
                                # 使用严格模式进行base64解码
                                decoded_value = base64.b64decode(last_ldc_value, validate=True).decode('utf-8')
                                fields[field_ref.name.value] = decoded_value
                            except:
                                # 如果解码失败，保留原始值
                                fields[field_ref.name.value] = last_ldc_value
                        last_ldc_value = None

                # 将非空字段添加到result中
                print(result)
                result.update({field: value for field, value in fields.items() if value})
                print(result)

        except Exception as e:
            # console.print(f"[red]解析JSP请求时出错: {e}[/red]")
            pass

    return result


def format_response_data(response_data):
    try:
        response_data = response_data.decode('utf-8', errors='ignore')
        # 先尝试解析整个response_data为JSON
        json_data = json.loads(response_data)

        # 对整个json_data进行decode_json_value处理
        json_data = decode_json_value(json_data)

        # 如果存在msg字段，对其进行特殊处理
        if 'msg' in json_data.keys():
            msg = json_data['msg']
            try:
                # 尝试将msg解析JSON
                if msg[-2:] == ',]':
                    msg = msg[:-2] + ']'
                msg_json = json.loads(msg)
                json_data['msg'] = decode_json_value(msg_json)
            except Exception as e:
                pass
        return json_data
    except Exception as e:
        # console.print(f"[red]格式化响应数据时出错, 响应数据不是JSON格式: {e}[/red]")
        return response_data
