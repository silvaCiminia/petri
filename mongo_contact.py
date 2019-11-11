#!/usr/bin/env python3

import logging
import logging.handlers as handlers
import time
import sys

from .mongo_translator import MongoTranslator
from .mongo_connector import MongoConnector
from .util.decorators import singleton
from .base_classes import PetriClass


@singleton
class MongoContact:

    def __init__(self,
                 types: list,
                 ):
        self.logger = self.create_logger()
        self.logger.info('Instantiating MongoContact...')

        self._translator = MongoTranslator(types)
        self._connector = MongoConnector(self._translator.db)

        self.logger.info('MongoContact instantiated.')

    def update(self,
               obj: PetriClass
               ) -> PetriClass:
        # Add/Update db item
        self.logger.info(f'Updating {obj}...')

        try:
            _mongo_obj = self._translator.to_mongo(obj)

            if not _mongo_obj:
                self.logger.error('Conversion failed!')
                return None

            _id = self._connector.store(_mongo_obj)
            if _id is None:
                self.logger.error(f'Unable to store {obj} in the db!')
                return None

            self.logger.info(f'Updated {obj} successfully.')
            obj.id = _id
            return obj

        except Exception as e:
            self.logger.error(f'Update failed with exception: {e}')

    def retrieve_doc(self,
                     id: str,
                     class_: type
                     ) -> PetriClass:
        # Retrieve db item
        self.logger.info(f'Retrieving {class_} {id}...')
        (_db_cls, _) = self._translator.to_mongo_class(class_)
        _db_entities = self._connector.retrieve(id, _db_cls)

        # We shouldn't have more than one entry in this list
        if len(_db_entities) != 1:
            self.logger.error(f'Retrieval of {class_} {id} failed!')

        self.logger.info(f'{class_} {id} retrieved successfully.')
        return _db_entities[0]

    def retrieve(self,
                 id: str,
                 class_: type
                 ) -> PetriClass:
        # Retrieve full python item
        try:
            _db_entity = self.retrieve_doc(id, class_)

            self.logger.info(f'Mapping {_db_entity} to python object...')

            py_entity = self._translator.from_mongo(_db_entity)

            if py_entity is None:
                self.error(f'Mapping {_db_entity} to python object failed!')
                return

            self.logger.info(f'{_db_entity} mapped to {py_entity} \
sucessfully.')
            return py_entity

        except Exception as e:
            self.logger.error(f'Retrieval failed with exception: {e}')

    def create_logger(self
                      ) -> logging.Logger:
        logger = logging.getLogger('petri')
        logger.setLevel(logging.DEBUG)

        fileHandler = handlers.TimedRotatingFileHandler(
            f'/tmp/petri-{time.time()}.log', when='M',
            interval=1, backupCount=2)
        fileHandler.setFormatter(logging.Formatter(
         '%(asctime)s | %(name)s [%(levelname)s] %(message)s'))
        logger.addHandler(fileHandler)

        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setLevel(logging.WARNING)
        consoleHandler.setFormatter(logging.Formatter('[*] %(message)s'))
        logger.addHandler(consoleHandler)

        logger.info('Logger created.')
        return logger
