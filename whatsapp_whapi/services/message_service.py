# -*- coding: utf-8 -*-
from .whapi_client import WhapiClient


class MessageService:
    def __init__(self, channel):
        self.client = WhapiClient(channel)

    def list_messages(self, count=100, offset=0, chat_id=None):
        params = {'count': count, 'offset': offset}
        path = '/messages/list'
        if chat_id:
            path = f'/messages/list/{chat_id}'
        return self.client.get(path, params=params)

    def get_message(self, message_id):
        return self.client.get(f'/messages/{message_id}')

    def send_text(self, to, body, **kwargs):
        payload = {'to': to, 'body': body, **kwargs}
        return self.client.post('/messages/text', json_data=payload)

    def send_image(self, to, media, caption=None, **kwargs):
        payload = {'to': to, 'media': media, **kwargs}
        if caption:
            payload['caption'] = caption
        return self.client.post('/messages/image', json_data=payload)

    def send_video(self, to, media, **kwargs):
        return self.client.post('/messages/video', json_data={'to': to, 'media': media, **kwargs})

    def send_short(self, to, media, **kwargs):
        return self.client.post('/messages/short', json_data={'to': to, 'media': media, **kwargs})

    def send_gif(self, to, media, **kwargs):
        return self.client.post('/messages/gif', json_data={'to': to, 'media': media, **kwargs})

    def send_audio(self, to, media, **kwargs):
        return self.client.post('/messages/audio', json_data={'to': to, 'media': media, **kwargs})

    def send_voice(self, to, media, **kwargs):
        return self.client.post('/messages/voice', json_data={'to': to, 'media': media, **kwargs})

    def send_document(self, to, media, filename=None, **kwargs):
        payload = {'to': to, 'media': media, **kwargs}
        if filename:
            payload['filename'] = filename
        return self.client.post('/messages/document', json_data=payload)

    def send_link_preview(self, to, body, **kwargs):
        return self.client.post('/messages/link_preview', json_data={'to': to, 'body': body, **kwargs})

    def send_location(self, to, latitude, longitude, **kwargs):
        return self.client.post('/messages/location', json_data={
            'to': to, 'latitude': latitude, 'longitude': longitude, **kwargs
        })

    def send_live_location(self, to, latitude, longitude, **kwargs):
        return self.client.post('/messages/live_location', json_data={
            'to': to, 'latitude': latitude, 'longitude': longitude, **kwargs
        })

    def send_contact(self, to, contact_id, **kwargs):
        return self.client.post('/messages/contact', json_data={'to': to, 'contact': contact_id, **kwargs})

    def send_contact_list(self, to, contacts, **kwargs):
        return self.client.post('/messages/contact_list', json_data={'to': to, 'contacts': contacts, **kwargs})

    def send_poll(self, to, title, options, **kwargs):
        return self.client.post('/messages/poll', json_data={
            'to': to, 'title': title, 'options': options, **kwargs
        })

    def send_interactive(self, to, payload):
        payload = dict(payload)
        payload['to'] = to
        return self.client.post('/messages/interactive', json_data=payload)

    def send_carousel(self, to, payload):
        payload = dict(payload)
        payload['to'] = to
        return self.client.post('/messages/carousel', json_data=payload)

    def send_sticker(self, to, media, **kwargs):
        return self.client.post('/messages/sticker', json_data={'to': to, 'media': media, **kwargs})

    def send_story(self, payload):
        return self.client.post('/messages/story', json_data=payload)

    def send_story_text(self, payload):
        return self.client.post('/messages/story/text', json_data=payload)

    def send_story_media(self, payload):
        return self.client.post('/messages/story/media', json_data=payload)

    def send_story_audio(self, payload):
        return self.client.post('/messages/story/audio', json_data=payload)

    def forward(self, message_id, to):
        return self.client.post(f'/messages/{message_id}', json_data={'to': to})

    def mark_read(self, message_id):
        return self.client.put(f'/messages/{message_id}')

    def delete(self, message_id):
        return self.client.delete(f'/messages/{message_id}')

    def react(self, message_id, emoji):
        return self.client.put(f'/messages/{message_id}/reaction', json_data={'emoji': emoji})

    def remove_reaction(self, message_id):
        return self.client.delete(f'/messages/{message_id}/reaction')

    def star(self, message_id):
        return self.client.put(f'/messages/{message_id}/star')

    def pin(self, message_id):
        return self.client.post(f'/messages/{message_id}/pin')

    def unpin(self, message_id):
        return self.client.delete(f'/messages/{message_id}/pin')
