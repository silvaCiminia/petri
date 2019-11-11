#!/usr/bin/env python3

import mongoengine as m


class MongoConnector:
    """MongoDB Connector"""

    def __init__(self,
                 db: str):
        self.db = db

    def connect_or_throw(self) -> bool:
        try:
            m.connect(self.db)
            return True
        except Exception:
            raise Exception(f'Unable to connect to db at {self.db}')

    def store(self,
              item: m.Document
              ) -> str:
        # Store a db item
        if self.connect_or_throw():
            if(item.save()):
                return item.id

    def retrieve(self,
                 id: str,
                 class_: type
                 ) -> m.Document:
        # Get a db item matching an id and type
        if self.connect_or_throw():
            return class_.objects(id=id)
