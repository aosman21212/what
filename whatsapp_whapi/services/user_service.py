# -*- coding: utf-8 -*-
from .whapi_client import WhapiClient


class UserService:
    def __init__(self, channel):
        self.client = WhapiClient(channel)

    def login_qr_base64(self):
        return self.client.get('/users/login')

    def login_qr_image(self):
        return self.client.get('/users/login/image')

    def login_qr_rowdata(self):
        return self.client.get('/users/login/rowdata')

    def login_phone_code(self, phone_number):
        return self.client.get(f'/users/login/{phone_number}')

    def logout(self):
        return self.client.post('/users/logout')

    def profile(self):
        return self.client.get('/users/profile')

    def update_profile(self, payload):
        return self.client.patch('/users/profile', json_data=payload)

    def update_status(self, text):
        return self.client.put('/status', json_data={'text': text})
