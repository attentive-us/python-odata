# -*- coding: utf-8 -*-

from .connection import OData3Connection, OAuth2Connection
from .entity import Entity as EntityBase
from .query import Query
from .exceptions import ODataError

__all__ = (
    'ODataService',
    'ODataError',
)


class ODataService(object):

    def __init__(self, url, oauth2=None):
        self.url = url
        self.metadata_url = ''
        self.collections = {}
        if oauth2 is not None:
            client_id = oauth2.get('client_id')
            token = oauth2.get('token')
            self.connection = OAuth2Connection(client_id, token=token)
        else:
            self.connection = OData3Connection()

        class Entity(EntityBase):
            __odata_url_base__ = url
            __odata_connection__ = self.connection

        self.Entity = Entity

    def __repr__(self):
        return '<ODataService at {0}>'.format(self.url)

    def query(self, entitycls):
        return Query(entitycls)

    def save(self, new_object):
        url = new_object.__odata_url__()
        pk_name, pk_prop = new_object.__odata_pk_property__()

        data = new_object.__odata__.copy()
        instance_url = new_object.__odata_instance_url__()
        data.pop(pk_prop.name)

        if instance_url is None:
            saved_data = self.connection.execute_post(url, data)
        else:
            saved_data = self.connection.execute_put(instance_url, data)

        # Received object's data in response
        if saved_data is not None:

            new_object.__odata__.update(saved_data)

        # Update object manually
        elif instance_url is not None:

            saved_data = self.connection.execute_get(instance_url)

        # Drop unnecessary values
        for key in saved_data.keys():
            if 'odata.' in key:
                saved_data.pop(key)

        new_object.__odata__.update(saved_data)
