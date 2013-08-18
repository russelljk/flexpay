import xml.sax

__all__ = ["Response"]

class Response(object):
    def __init__(self, name, parent):
        self._parent = parent
        self._name = name
        self._value = ''
        self._children = []
        
    def add_attribute(self, name, o):
        if isinstance(o, str) or\
           isinstance(o, unicode):
            o = o.strip()   
        elif isinstance(o, Response):
            self._children.append(o)
        setattr(self, name, o)
    
    def set_value(self, v):
        self._value = v.strip()
    
    def get_value(self):
        return self._value
    
    value = property(get_value, set_value)
    
    def get_name(self):
        return self._name
        
    def __str__(self):
        v = ''
        if (not len(self._children)) and self._value:
            return str(self._value)
        return self._name + v
        
class Handler(xml.sax.ContentHandler):
    def __init__(self, method):
        self.root_obj = None
        self.method_result = method + 'Result'
        self._text = ''
        self.resp = None
        self.request_id = None
    
    def push_layer(self, name):
        o = Response(name, self.root_obj)
        if self.root_obj:
            self.root_obj.add_attribute(name, o)            
        self.root_obj = o
    
    def pop_layer(self):
        if self.root_obj:
            self.root_obj.set_value(self._text)
            self.root_obj = self.root_obj._parent
        
    def startElement(self, name, attrs):            
        if name == self.method_result or self.root_obj != None:
            self.push_layer(name)
    
    def endElement(self, name):
        if name == 'RequestId':
            self.resp.add_attribute('RequestId', self._text)
        if self.root_obj != None:
            if name == self.method_result:
                self.resp = self.root_obj
            self.pop_layer()
        self._text = ''
        
    def characters(self, content):
        self._text += content

def make_response(x, method):
    h = Handler(method)
    xml.sax.parseString(x, h)
    resp = h.resp
    resp.add_attribute('ResponseText', x)
    return resp
