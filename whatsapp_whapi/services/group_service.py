# -*- coding: utf-8 -*-
from .whapi_client import WhapiClient


class GroupService:
    def __init__(self, channel):
        self.client = WhapiClient(channel)

    def list_groups(self):
        return self.client.get('/groups')

    def create(self, subject, participants):
        return self.client.post('/groups', json_data={
            'subject': subject,
            'participants': participants,
        })

    def accept_invite(self, invite_code):
        return self.client.put('/groups', json_data={'invite_code': invite_code})

    def get(self, group_id):
        return self.client.get(f'/groups/{group_id}')

    def update_info(self, group_id, payload):
        return self.client.put(f'/groups/{group_id}', json_data=payload)

    def leave(self, group_id):
        return self.client.delete(f'/groups/{group_id}')

    def update_setting(self, group_id, payload):
        return self.client.patch(f'/groups/{group_id}', json_data=payload)

    def get_invite(self, group_id):
        return self.client.get(f'/groups/{group_id}/invite')

    def revoke_invite(self, group_id):
        return self.client.delete(f'/groups/{group_id}/invite')

    def add_participants(self, group_id, participants):
        return self.client.post(f'/groups/{group_id}/participants', json_data={
            'participants': participants,
        })

    def remove_participants(self, group_id, participants):
        return self.client.delete(f'/groups/{group_id}/participants', json_data={
            'participants': participants,
        })

    def get_icon(self, group_id):
        return self.client.get(f'/groups/{group_id}/icon')

    def set_icon(self, group_id, media):
        return self.client.put(f'/groups/{group_id}/icon', json_data={'media': media})

    def delete_icon(self, group_id):
        return self.client.delete(f'/groups/{group_id}/icon')

    def demote_admins(self, group_id, participants):
        return self.client.delete(f'/groups/{group_id}/admins', json_data={
            'participants': participants,
        })

    def promote_admins(self, group_id, participants):
        return self.client.patch(f'/groups/{group_id}/admins', json_data={
            'participants': participants,
        })

    def get_applications(self, group_id):
        return self.client.get(f'/groups/{group_id}/applications')

    def accept_application(self, group_id, participants):
        return self.client.post(f'/groups/{group_id}/applications', json_data={
            'participants': participants,
        })

    def reject_applications(self, group_id, participants):
        return self.client.delete(f'/groups/{group_id}/applications', json_data={
            'participants': participants,
        })
