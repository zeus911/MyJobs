
class BaseView(object):
    """
    Must override this in the inherited class if you need to use it.
    
    """
    def __init__(self, request, *args, **kwargs):
        raise NotImplementedError("Need to define '__init__' on this view.")
    
    def __call__(self):
        pass
    
    def __new__(cls, *args, **kwargs):
        # This helps us make all requests thread-safe, as each new request will
        # get its own instance of the view class that its using.
        view = cls.new(cls, *args, **kwargs)
        return view.create_response()
    
    @classmethod
    def new(cls, *args, **kwargs):
        # Just a factory to build the new object.
        obj = object.__new__(cls)
        obj.__init__(*args, **kwargs)
        return obj
    
    def create_response(self, request):
        """
        Must override this in the inherited class if you need to use it.
        Must return an HTTPResponse from this method.
        
        """
        raise NotImplementedError("""
                                  Need to define 'create_response' on this view.
                                  """)