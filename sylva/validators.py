from . import errors


# pylint: disable=unused-argument
def dict_not_empty(instance, attribute, value):
    if value is not None and not len(list(value.keys())):
        raise errors.LocationError(instance.location, 'Cannot be empty')


# pylint: disable=unused-argument
def list_not_empty(instance, attribute, value):
    if value is not None and len(value) <= 0:
        raise errors.LocationError(instance.location, 'Cannot be empty')


def positive(instance, attribute, value):
    if value is not None and value <= 0:
        raise errors.LocationError(instance.location, 'Must be > 0')
