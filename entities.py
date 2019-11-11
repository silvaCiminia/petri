#!/usr/bin/env python

import mongoengine as m


def __init__(self):
    pass


class Session(m.Document):
    name = m.StringField(required=True)


class Entity(m.Document):
    # Basic entity class from which all db objects must inherit.
    # Provides cohesion among sessions
    session = m.ReferenceField(Session, required=True)
    meta = {'allow_inheritance': True}


# Define db classes here
# class SampleClass(m.Document):
#
# Fields whose names match exactly with the properties of thir python
# equivalents will be matched automatically, unless another name is
# specified for that property in the metadata
#    matching_field0 = m.StringField(required=True, max_length=50)
#    matching_field1 = m.IntField(required=True)

# These names have been switched from their python equivalents, in
# order to demonstrate metadata mapping
#    non_matching_field0 = m.FloatField(required=True)
#    non_matching_field1 = m.StringField(required=True, max_length=50)
