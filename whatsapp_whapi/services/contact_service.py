# -*- coding: utf-8 -*-
from .whapi_client import WhapiClient


class ContactService:
    def __init__(self, channel):
        self.client = WhapiClient(channel)

    def list_contacts(self, count=100, offset=0):
        return self.client.get('/contacts', params={'count': count, 'offset': offset})

    def check_phones(self, phones):
        return self.client.post('/contacts', json_data={'contacts': phones})

    def add_contact(self, phone, name):
        return self.client.put('/contacts', json_data={'phone': phone, 'name': name})

    def get_contact(self, contact_id):
        return self.client.get(f'/contacts/{contact_id}')

    def send_contact(self, contact_id, to):
        return self.client.post(f'/contacts/{contact_id}', json_data={'to': to})

    def exists(self, contact_id):
        return self.client.head(f'/contacts/{contact_id}')

    def edit_contact(self, contact_id, payload):
        return self.client.patch(f'/contacts/{contact_id}', json_data=payload)

    def delete_contact(self, contact_id):
        return self.client.delete(f'/contacts/{contact_id}')

    def get_lids(self, ids):
        return self.client.get('/contacts/lids', params={'ids': ','.join(ids)})

    def get_lid(self, contact_id):
        return self.client.get(f'/contacts/lids/{contact_id}')
