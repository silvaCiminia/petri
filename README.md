# Petri

A metadata-based connector for mongoengine. Define mongoengine Document subclasses in `entities.py` and define mappings from regular python classes to those classes in `metadata/mappings.yaml`. This library will intelligently handle the logic of storing, retrieving, and cross-referencing these objects.

## Usage

Create a contact object with a list of python classes to build mapping logic for:

`contact = petri.MongoContact([str, int, MyClass, MyClass2, ...])`

To store instances of those classes:

`new_obj = contact.update(obj)`

This will return an updated instance. In most cases it will be identical, but if this is the instance's first time being stored to the database it will be fitted with an id. You can use that id later to retrieve an object from the database by python class and id. For example:

`ret_obj = contact.retrieve(type(obj), obj.id)`

There is some very bare-bones session logic for unifying classes and instances, but as it stands this doesn't do much yet.
