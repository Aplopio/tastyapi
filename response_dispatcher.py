from exceptions import *
from responses import *

class CustomResponseDispatcher(object):
    def handle_cache_control(self, request, response):
        return response

    def create_response(self, content, content_type=None, **response_kwargs):
        return CustomResponse(content)

    def get_default_response_class(self):
        return CustomResponse

    def get_unauthorized_response_class(self):
        return CustomResponseUnauthorized    

    def get_unauthorized_request_response(self):
        raise CustomResponseErrorUnauthorized(response=CustomResponseUnauthorized())

    def get_created_response_class(self):
        return CustomResponseCreated

    def get_no_content_response(self):
        return CustomResponseNoContent()

    def get_accepted_response_class(self):
        return CustomResponseAccepted

    def get_bad_request_response(self, content):
        raise CustomResponseErrorBadRequest(response=CustomResponseBadRequest(content))
        
    def get_method_notallowed_response(self, content):
        raise CustomResponseErrorMethodNotAllowed(response=CustomResponseMethodNotAllowed(content))

    def get_too_many_request_response(self):
        raise CustomResponseErrorTooManyRequests(response=CustomResponseTooManyRequests())

    def get_multiple_choices_response(self, content):
        return CustomResponseMultipleChoices(content)

    def get_not_found_response(self):
        raise CustomResponseErrorNotFound(response=CustomResponseNotFound())

    def get_created_response(self, location):
        return CustomResponseCreated(location=location)

    def get_not_implemented_response(self):
        raise CustomResponseErrorNotImplemented(response = CustomResponseNotImplemented())