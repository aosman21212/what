# -*- coding: utf-8 -*-
from .whapi_client import WhapiClient


class ChannelService:
    def __init__(self, channel):
        self.client = WhapiClient(channel)

    def health(self, wakeup=True, platform='web'):
        return self.client.get('/health', params={
            'wakeup': str(wakeup).lower(),
            'platform': platform,
            'channel_type': 'web',
        })

    def get_settings(self):
        return self.client.get('/settings')

    def update_settings(self, payload):
        return self.client.patch('/settings', json_data=payload)

    def reset_settings(self):
        return self.client.delete('/settings')

    def get_events(self):
        return self.client.get('/settings/events')

    def test_webhook(self):
        return self.client.post('/settings/webhook_test')

    def get_limits(self):
        return self.client.get('/limits')

    def register_webhook(self, webhook_url, events=None):
        payload = {
            'webhooks': [{
                'url': webhook_url,
                'events': events or [
                    {'type': 'messages', 'method': 'put'},
                    {'type': 'statuses', 'method': 'put'},
                    {'type': 'chats', 'method': 'put'},
                    {'type': 'contacts', 'method': 'put'},
                    {'type': 'groups', 'method': 'put'},
                    {'type': 'presences', 'method': 'put'},
                    {'type': 'channel', 'method': 'put'},
                ],
            }],
        }
        return self.update_settings(payload)
