import base64

from util.decrypter import decrypt


class Behinder:
    def __init__(self):
        self.url = ''
        self.key = ''
        self.script_type = ''
        self.data = ''
        self.encode_type = ''
        self.filedata = ''
        self.cmd_history = ''
        self.database = ''

    def set_url(self, url):
        self.url = url

    def set_key(self, key):
        self.key = key

    def set_script_type(self, script_type):
        self.script_type = script_type

    def get_url(self):
        return self.url

    def get_key(self):
        return self.key

    def get_script_type(self):
        return self.script_type

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def set_encode_type(self, encode_type):
        self.encode_type = encode_type

    def get_encode_type(self):
        return self.encode_type

    def decrypted_data(self):
        return decrypt(self.data, self.key, self.script_type, self.encode_type)
