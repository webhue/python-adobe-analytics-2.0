import inspect
import inflection
import json


class DynamicObject(object):
    def __init__(self, *args, **kwargs):
        if kwargs is not None and len(kwargs) > 0:
            for k in kwargs:
                self.__dict__[k] = kwargs[k]

    def __iter__(self):
        return self.__dict__.iteritems()

    def __str__(self):
        return json.dumps(dict(self), indent=4)

    def __repr__(self):
        return "<DynamicObject: %s>" % str([attr for attr in self.__dict__])


def to_dynamic_object(obj):
    if not isinstance(obj, dict):
        raise ValueError('Function expects a dictionary!')
    _obj = DynamicObject()
    for k, v in obj.items():
        _obj.__dict__[inflection.underscore(k)] = to_dynamic_object(
            v) if isinstance(v, dict) else v
    return _obj


def create_instance(cls):
    init_args = inspect.getargspec(cls.__init__)
    args = ()
    defaults = init_args.defaults if init_args.defaults is not None else ()
    if len(init_args.args) - 1 > len(defaults):
        for _ in range(1, len(init_args.args) - len(defaults)):
            args += (None,)

    if len(defaults) > 0:
        args += defaults
    return cls(*args)
