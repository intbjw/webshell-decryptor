import pyshark
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
import binascii


def decrypt(data, key, script_type, encode_type):
    if isinstance(data, pyshark.packet.fields.LayerFieldsContainer):
        data = str(data)
    # 移除可能存在的冒号
    data = data.replace(':', '')
    try:
        # 尝试将十六进制字符串转换为字节
        decoded_data = binascii.unhexlify(data)
        # console.print(f"[green]十六进制解码成功[/green]")
    except binascii.Error:
        print(f"[red]十六进制解码失败[/red]")
        return None
    if encode_type == "xor":
        return xor_decrypt(decoded_data, key, script_type)
    if encode_type == "aes":
        return aes_decrypt(decoded_data, key, script_type)


def xor_decrypt(data, key, script_type):
    try:
        base64_decoded = base64.b64decode(data, validate=True)
    # console.print(f"[green]Base64解码成功[/green]")
    except:
        return data
    key_bytes = key.encode('utf-8')
    decrypted = bytearray()
    if script_type == "php":
        for i, byte in enumerate(base64_decoded):
            key_index = ((i & 15) + 1) % len(key_bytes)
            decrypted.append(byte ^ key_bytes[key_index])
        return bytes(decrypted)
    if script_type == "asp":
        for i, byte in enumerate(data):
            key_index = ((i & 15) + 1) % len(key_bytes)  # 使用与原ASP代码相同的索引逻辑
            decrypted.append(byte ^ key_bytes[key_index])
        return decrypted.decode('utf-8', errors='ignore')


def aes_decrypt(data, key, script_type):
    try:
        base64_decoded = base64.b64decode(data, validate=True)
    except:

        return data
    if script_type == "php":
        key_bytes = key.encode('utf-8')[:16].ljust(16, b'\0')
        iv = b'\x00' * 16
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        try:
            decrypted = unpad(cipher.decrypt(base64_decoded), AES.block_size)
        except ValueError:
            # 如果解密后的数据没有正确的填充，尝试不进行去填充
            decrypted = cipher.decrypt(base64_decoded)
        return decrypted
    if script_type == "aspx":
        try:
            # 按照 ASP 的行为，将 key 使用系统默认编码进行转换
            key = key.encode('UTF-8')

            # 确保密钥长度为 16 字节（128 位），ASP 中是这样处理的
            key = key[:16].ljust(16, b'\0')

            # 创建 AES 解密器，使用 CBC 模式，并使用相同的 key 作为 IV
            cipher = AES.new(key, AES.MODE_CBC, iv=key)

            # 解密数据
            decrypted_data = cipher.decrypt(data)

            # 移除 PKCS7 填充
            padding_length = decrypted_data[-1]
            if 1 <= padding_length <= 16:
                return decrypted_data[:-padding_length]
            else:
                return decrypted_data  # 如果填充长度异常，返回未去除填充的结果
        except Exception as e:
            # 捕获错误信息，方便调试
            return data
    if script_type == "jsp":
        try:
            key_bytes = key.encode('utf-8')[:16].ljust(16, b'\0')  # 确保密钥长度为16字节
            cipher = AES.new(key_bytes, AES.MODE_ECB)
            decrypted_data = cipher.decrypt(base64_decoded)
            # 移 PKCS7 填充
            padding_length = decrypted_data[-1]
            if 1 <= padding_length <= 16:
                return decrypted_data[:-padding_length]
            else:
                return decrypted_data
        except Exception as e:
            return data
