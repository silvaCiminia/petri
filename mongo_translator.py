#!/usr/bin/env python3

import yaml
import re
from mongoengine import Document, ReferenceField

from . import entities


class MongoTranslator:
    """Translates between python models and mongoDB models"""

    def __init__(self,
                 types: list
                 ):
        # Parse mappings from .yaml
        with open('metadata/mappings.yaml') as file:
            self._mappings = yaml.load(file, Loader=yaml.FullLoader)

        # Map python object names to classes
        self._mappings['objects'] = {self.string_from_type(type_): type_
                                     for type_ in types}

        # Add reverse lookup tables
        self._mappings['reverse'] = {}
        for item in [mapping for mapping
                     in self._mappings
                     if mapping != 'reverse' and mapping != 'objects']:

            if item == 'db_name':
                self.db = self._mappings[item]
                continue

            if type(self._mappings[item]) is dict and \
               'db_class' in self._mappings[item].keys():
                # Map based on metadata
                self._mappings['reverse'][
                    self._mappings[item]['db_class']] = item

            else:
                self._mappings['reverse'][item] = item
                self._mappings[item] = {}

                # Set db class
                self._mappings[item]['db_class'] = item

                # Map properties based on name
                if item not in self._mappings['objects'].keys() or True:
                    raise ValueError(f'No db object found for {item}: \
Check that it exists and is mapped correctly')

                for prop in self._mappings['objects'][item].__dict__.keys():
                    if not re.match(r'__\S+__', prop) and prop != 'id':
                        self._mappings[item][prop] = prop

    @staticmethod
    def string_from_type(type_: type
                         ) -> str:
        return str(type_).split('.')[1].split('\'')[0]

    def skip(self,
             obj,
             attr: str
             ) -> bool:
        # Should this property be skipped?
        _py_type_str = self.string_from_type(type(obj))
        if 'skip' not in self._mappings[_py_type_str].keys():
            return False
        return attr in self._mappings[_py_type_str]['skip']

    def to_mongo_class(self,
                       class_: type
                       ) -> (type, dict):
        # Get tuple of db class and property mapping dict
        _py_cls_str = self.string_from_type(class_)
        obj_map = self._mappings[_py_cls_str]

        if not hasattr(entities, obj_map['db_class']):
            raise ValueError(f'No matching db class for {obj_map["db_class"]} \
found in entities file. Please check your mappings and try again')

        db_cls = (getattr(entities, obj_map['db_class'])
                  if obj_map['db_class'] is not None
                  else getattr(entities, _py_cls_str))
        return (db_cls, obj_map)

    def ref_check(self,
                  db_class: type,
                  attr: str,
                  value: object,
                  ) -> object:
        # Convert to db object if we need a reference
        db_type = type(getattr(db_class, attr))
        return self.to_mongo(value) if db_type == ReferenceField else value

    def to_mongo(self,
                 obj,
                 ) -> Document:
        # Get DB object
        (_db_cls, _obj_map) = self.to_mongo_class(type(obj))

        # Create new DB entity
        db_entity = _db_cls()

        # Map attributes from python entity
        for attr, value in obj.__dict__.items():

            if (attr == 'id' and value is None) or self.skip(obj, attr):
                continue

            if attr in _obj_map.keys():
                setattr(db_entity, _obj_map[attr], self.ref_check(_db_cls,
                                                                  attr,
                                                                  value))
            elif attr in _db_cls.__dict__.keys():
                setattr(db_entity, attr, self.ref_check(_db_cls,
                                                        attr,
                                                        value))

            else:
                raise ValueError(f'Problem converting property \
{type(obj)}.{attr} to db property')

        return db_entity

    def from_mongo(self,
                   db_entity: Document,
                   ) -> object:
        # Get python object
        _db_cls_str = self.string_from_type(type(db_entity))
        _py_cls_str = self._mappings['reverse'][_db_cls_str]
        _py_cls = self._mappings['objects'][_py_cls_str]
        _obj_map = self._mappings[_py_cls_str]

        # Create new python entity
        py_entity = _py_cls()
        # Map attributes from DB entity
        for attr, value in py_entity.__dict__.items():

            if self.skip(py_entity, attr):
                continue

            if attr == 'id':
                setattr(py_entity, attr, db_entity.id)

            elif attr in _obj_map.keys():
                setattr(py_entity, attr, getattr(db_entity, attr))

            else:
                try:
                    setattr(py_entity, attr, getattr(db_entity, attr))
                except Exception:
                    raise Exception(f'Problem getting property \
{_py_cls}.{attr} from db')

        return py_entity
