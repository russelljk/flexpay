__all__ = ["RestAPIException"]

class RestAPIException(StandardError):
    def __init__(self, *args):
        StandardError.__init__(self, *args)
    
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return 'FPS REST API Exception: {0} {1}\n\n{2}'.format(self.args[0],
                                          self.args[1],
                                          self.args[2])