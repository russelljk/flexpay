from urllib import quote

def make_enum(base, **enums):
    class _ENUM(base):
        instances = []
        def __init__(self, *args, **kwargs):
            self.__class__.instances.append(self)
            base.__init__(self, *args, **kwargs)
        
        @classmethod
        def reverse_lookup(cls, value):
            if isinstance(value, base):
                for v in cls.instances:
                    if v == value:
                        return v
            raise TypeError('Reverse lookup for enumerated value {0} failed.'.format(value))
        
        def __setattr__(self, name, value):
            raise NotImplementedError
    
    for e in enums:
        setattr(_ENUM, e, _ENUM(enums[e]))
    
    return _ENUM

def make_amount(amt):
    '''
    Turn amt into a string for use in the REST API.
    '''
    return str(amt) # All decimal and floating point classes will convert to string properly.

def signature_quote(thing): 
    x = quote(str(thing), '~')
    return x