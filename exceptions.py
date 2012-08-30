class ImmediateRboxResponse(Exception):
    """ Class for sending immediate error messages"""
    
    response = Exception    
    def __init__(self, response):
        self.response = response