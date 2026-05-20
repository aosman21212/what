# -*- coding: utf-8 -*-
from .whapi_client import WhapiClient


class BusinessService:
    def __init__(self, channel):
        self.client = WhapiClient(channel)

    def get_profile(self):
        return self.client.get('/business')

    def edit_profile(self, payload):
        return self.client.post('/business', json_data=payload)

    def list_products(self):
        return self.client.get('/business/products')

    def create_product(self, payload):
        return self.client.post('/business/products', json_data=payload)

    def products_by_contact(self, contact_id):
        return self.client.get(f'/business/{contact_id}/products')

    def get_product(self, product_id):
        return self.client.get(f'/business/products/{product_id}')

    def send_product(self, product_id, to):
        return self.client.post(f'/business/products/{product_id}', json_data={'to': to})

    def update_product(self, product_id, payload):
        return self.client.patch(f'/business/products/{product_id}', json_data=payload)

    def delete_product(self, product_id):
        return self.client.delete(f'/business/products/{product_id}')

    def get_order(self, order_id):
        return self.client.get(f'/business/orders/{order_id}')

    def create_collection(self, payload):
        return self.client.post('/business/collections', json_data=payload)

    def list_collections(self):
        return self.client.get('/business/collections')

    def get_collection(self, collection_id):
        return self.client.get(f'/business/collections/{collection_id}')

    def edit_collection(self, collection_id, payload):
        return self.client.patch(f'/business/collections/{collection_id}', json_data=payload)

    def delete_collection(self, collection_id):
        return self.client.delete(f'/business/collections/{collection_id}')
