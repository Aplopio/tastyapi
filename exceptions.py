class CustomResponseError(Exception):
    rbox_response = None

    def __init__(self, response):
        self.rbox_response = response


class CustomResponseErrorUnauthorized(CustomResponseError):
    pass


class CustomResponseErrorBadRequest(CustomResponseError):
    pass


class CustomResponseErrorMethodNotAllowed(CustomResponseError):
    pass


class CustomResponseErrorTooManyRequests(CustomResponseError):
    pass
    

class CustomResponseErrorNotFound(CustomResponseError):
    pass


class  CustomResponseErrorNotImplemented(CustomResponseError):
    pass        
