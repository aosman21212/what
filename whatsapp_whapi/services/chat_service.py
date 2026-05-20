# -*- coding: utf-8 -*-
from .whapi_client import WhapiClient


class ChatService:
    def __init__(self, channel):
        self.client = WhapiClient(channel)

    def list_chats(self, count=100, offset=0):
        return self.client.get('/chats', params={'count': count, 'offset': offset})

    def get_chat(self, chat_id):
        return self.client.get(f'/chats/{chat_id}')

    def delete_chat(self, chat_id):
        return self.client.delete(f'/chats/{chat_id}')

    def archive_chat(self, chat_id, archive=True):
        return self.client.post(f'/chats/{chat_id}', json_data={'archive': archive})

    def update_settings(self, chat_id, payload):
        return self.client.patch(f'/chats/{chat_id}', json_data=payload)
