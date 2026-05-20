# -*- coding: utf-8 -*-
from .whapi_client import WhapiClient


class StatusService:
    def __init__(self, channel):
        self.client = WhapiClient(channel)

    def get_message_statuses(self, message_id):
        return self.client.get(f'/statuses/{message_id}')

    def get_story_statuses(self, story_id):
        return self.client.get(f'/statuses/story/{story_id}')
