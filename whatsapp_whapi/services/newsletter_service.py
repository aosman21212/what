# -*- coding: utf-8 -*-
from .whapi_client import WhapiClient


class NewsletterService:
    def __init__(self, channel):
        self.client = WhapiClient(channel)

    def list_newsletters(self):
        return self.client.get('/newsletters')

    def create(self, payload):
        return self.client.post('/newsletters', json_data=payload)

    def find(self, **params):
        return self.client.get('/newsletters/find', params=params)

    def recommended(self, country):
        return self.client.get('/newsletters/recommended', params={'country': country})

    def get(self, newsletter_id):
        return self.client.get(f'/newsletters/{newsletter_id}')

    def delete(self, newsletter_id):
        return self.client.delete(f'/newsletters/{newsletter_id}')

    def edit(self, newsletter_id, payload):
        return self.client.patch(f'/newsletters/{newsletter_id}', json_data=payload)

    def subscribe(self, newsletter_id):
        return self.client.post(f'/newsletters/{newsletter_id}/subscription')

    def unsubscribe(self, newsletter_id):
        return self.client.delete(f'/newsletters/{newsletter_id}/subscription')

    def subscribe_invite(self, invite_code):
        return self.client.post(f'/newsletters/invite/{invite_code}/subscription')

    def unsubscribe_invite(self, invite_code):
        return self.client.delete(f'/newsletters/invite/{invite_code}/subscription')

    def track(self, newsletter_id):
        return self.client.post(f'/newsletters/{newsletter_id}/tracking')

    def messages(self, newsletter_id, count=100):
        return self.client.get(f'/newsletters/{newsletter_id}/messages', params={'count': count})

    def create_admin_invite(self, newsletter_id, contact_id):
        return self.client.post(f'/newsletters/{newsletter_id}/invite/{contact_id}')

    def revoke_admin_invite(self, newsletter_id, contact_id):
        return self.client.delete(f'/newsletters/{newsletter_id}/invite/{contact_id}')

    def accept_admin(self, newsletter_id, contact_id):
        return self.client.put(f'/newsletters/{newsletter_id}/admins/{contact_id}')

    def demote_admin(self, newsletter_id, contact_id):
        return self.client.delete(f'/newsletters/{newsletter_id}/admins/{contact_id}')
