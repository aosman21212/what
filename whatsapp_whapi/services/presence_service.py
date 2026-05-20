# -*- coding: utf-8 -*-
from .whapi_client import WhapiClient


class PresenceService:
    def __init__(self, channel):
        self.client = WhapiClient(channel)

    def set_me(self, online=True):
        return self.client.put('/presences/me', json_data={'online': online})

    def get(self, entry_id):
        return self.client.get(f'/presences/{entry_id}')

    def subscribe(self, entry_id):
        return self.client.post(f'/presences/{entry_id}')

    def send_typing(self, entry_id, typing=True, recording=False):
        return self.client.put(f'/presences/{entry_id}', json_data={
            'typing': typing,
            'recording': recording,
        })
