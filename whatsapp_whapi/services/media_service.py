# -*- coding: utf-8 -*-
import base64

from .whapi_client import WhapiClient


class MediaService:
    def __init__(self, channel):
        self.client = WhapiClient(channel)

    def upload(self, file_content, filename, mimetype):
        files = {'file': (filename, file_content, mimetype)}
        return self.client.post('/media', files=files)

    def upload_from_attachment(self, attachment):
        content = base64.b64decode(attachment.datas)
        return self.upload(content, attachment.name, attachment.mimetype)

    def list_media(self, count=100):
        return self.client.get('/media', params={'count': count})

    def get_media(self, media_id):
        return self.client.get(f'/media/{media_id}')

    def delete_media(self, media_id):
        return self.client.delete(f'/media/{media_id}')
