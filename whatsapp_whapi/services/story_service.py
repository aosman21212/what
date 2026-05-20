# -*- coding: utf-8 -*-
from .message_service import MessageService


class StoryService(MessageService):
    """Stories use /messages/story* endpoints (extends MessageService)."""

    def list_stories(self, count=100):
        return self.client.get('/stories', params={'count': count})

    def get_story(self, story_id):
        return self.client.get(f'/stories/{story_id}')

    def copy_story(self, story_id, to):
        return self.client.post(f'/stories/{story_id}', json_data={'to': to})
