import json

data = {'信息获取': '', '历史命令': [], '文件操作': {'filetree': {'/': {}, 'children': {}}, 'filelist': {}}}


def getJsonData(jsonl_file):
    with open(jsonl_file, 'r') as f:
        data_json = f.readlines()
    for item in data_json:
        item_json = json.loads(item)
        operation = item_json['request']['format']['operation']
        if operation == '信息获取':
            data['信息获取'] = item_json['response']['format']['msg']
        elif operation == '命令执行':
            data['历史命令'].append([item_json['request']['format']['path'], item_json['request']['format']['cmd'],
                                     item_json['response']['format']['msg']])
        elif operation == '文件操作':
            path = item_json['request']['format']['path']
            data['文件操作']['filelist'][path] = item_json['response']['format']['msg']
            if path == '/' and item_json['request']['format']['mode'] == 'list':
                pass
            else:
                if path[-1] == '/':
                    path_list = path.split('/')[:-1]
                else:
                    path_list = path.split('/')
                print(path_list)
                path_list.pop(0)
                temp = data['文件操作']['filetree']
                for p in path_list:
                    if 'children' not in temp:
                        temp['children'] = {}
                    if p not in temp['children']:
                        temp['children'][p] = {}
                    temp = temp['children'][p]
    return data

# a = getJsonData("../webshell.pcap_decrypted.jsonl")
# print(a['文件操作'])
