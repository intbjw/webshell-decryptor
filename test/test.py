from jawa.cf import ClassFile
from io import BytesIO
from jawa.constants import String

json_data = {'msg': [
    {'size': '4096', 'perm': 'rwxr-xr-x', 'name': '.', 'lastModified': '2024/12/08 02:39:18', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwxr-xr-x', 'name': '..', 'lastModified': '2024/12/08 02:39:18', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwx------', 'name': 'root', 'lastModified': '2024/12/08 02:30:24', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwxr-xr-x', 'name': 'srv', 'lastModified': '2024/09/11 14:04:28', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwxr-xr-x', 'name': 'bin', 'lastModified': '2024/12/08 02:30:22', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwxr-xr-x', 'name': 'etc', 'lastModified': '2024/12/08 02:39:08', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwxr-xr-x', 'name': 'lib32', 'lastModified': '2024/09/11 14:04:28', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwxr-xr-x', 'name': 'lib64', 'lastModified': '2024/09/11 14:07:49', 'type': 'directory'},
    {'size': '340', 'perm': 'rwxr-xr-x', 'name': 'dev', 'lastModified': '2024/12/08 02:39:08', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwxrwxrwx', 'name': 'tmp', 'lastModified': '2024/12/08 02:39:08', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwxr-xr-x', 'name': 'mnt', 'lastModified': '2024/09/11 14:04:28', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwxr-xr-x', 'name': 'usr', 'lastModified': '2024/09/11 14:04:28', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwxr-xr-x', 'name': 'home', 'lastModified': '2022/04/18 10:28:59', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwxr-xr-x', 'name': 'opt', 'lastModified': '2024/09/11 14:04:28', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwxr-xr-x', 'name': 'var', 'lastModified': '2024/09/11 14:07:54', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwxr-xr-x', 'name': 'sbin', 'lastModified': '2024/12/07 09:02:18', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwxr-xr-x', 'name': 'lib', 'lastModified': '2024/12/07 09:02:18', 'type': 'directory'},
    {'size': '0', 'perm': 'r-xr-xr-x', 'name': 'proc', 'lastModified': '2024/12/08 02:39:08', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwxr-xr-x', 'name': 'run', 'lastModified': '2024/12/08 02:39:10', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwxr-xr-x', 'name': 'media', 'lastModified': '2024/09/11 14:04:28', 'type': 'directory'},
    {'size': '0', 'perm': 'r-xr-xr-x', 'name': 'sys', 'lastModified': '2024/12/08 02:39:08', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwxr-xr-x', 'name': 'boot', 'lastModified': '2022/04/18 10:28:59', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwxr-xr-x', 'name': 'libx32', 'lastModified': '2024/09/11 14:04:28', 'type': 'directory'},
    {'size': '4096', 'perm': 'rwxr-x---', 'name': 'logs', 'lastModified': '2024/12/08 02:39:13', 'type': 'directory'},
    {'size': '0', 'perm': 'rwxr-xr-x', 'name': '.dockerenv', 'lastModified': '2024/12/08 02:39:08', 'type': 'file'}],
    'status': 'success'}

for item in json_data['msg']:
    print(item['perm'], item['type'], item['size'], item['lastModified'], item['name'])

with open("test.class", "rb") as f:
    request_data = f.read()

class_file = BytesIO(request_data)

# 使用包装后的类文件对象
cf = ClassFile(class_file)

source_file = cf.attributes.find_one(name='SourceFile')
if source_file:
    source_file_name = source_file.source_file.value
else:
    source_file_name = "Unknown"

print(source_file_name)
init_method = cf.methods.find_one(name='<init>')
for instruction in init_method.code.disassemble():
    print(instruction)
# 我想打印源码
source = cf.source
print(source)
