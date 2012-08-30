from tastypie.responses import ResponseHandler
from exceptions import *

class BadHeaderError(ValueError):
    pass


class CustomResponse(object):
    status_code = 200
    
    def __init__(self, content='', content_type=None, status=None, **kwargs):
        self._headers = {}
        self.content = content
        self.content_type = content_type
        if status:
            self.status_code = status

    def __setitem__(self, header, value):
        header, value = self._convert_to_ascii(header, value)
        self._headers[header.lower()] = (header, value)

    def __delitem__(self, header):
        try:
            del self._headers[header.lower()]
        except KeyError:
            pass

    def __getitem__(self, header):
        return self._headers[header.lower()][1]

    
    def _convert_to_ascii(self, *values):
        """Converts all values to ascii strings."""
        for value in values:
            if isinstance(value, unicode):
                try:
                    value = value.encode('us-ascii')
                except UnicodeError, e:
                    e.reason += ', HTTP response headers must be in US-ASCII format'
                    raise
            else:
                value = str(value)
            if '\n' in value or '\r' in value:
                raise BadHeaderError("Header values can't contain newlines (got %r)" % (value))
            yield value
        
class CustomResponseUnauthorized(CustomResponse):
    status_code = 401

class CustomResponseNoContent(CustomResponse):
    status_code = 204

class CustomResponseAccepted(CustomResponse):
    status_code = 202

class CustomResponseBadRequest(CustomResponse):
    status_code = 400

class CustomResponseMethodNotAllowed(CustomResponse):
    status_code = 405
    
class CustomResponseTooManyRequests(CustomResponse):
    status_code = 429

class CustomResponseMultipleChoices(CustomResponse):
    status_code = 300

class CustomResponseNotFound(CustomResponse):
    status_code = 404

class CustomResponseNotImplemented(CustomResponse):
    status_code = 501

class CustomResponseCreated(CustomResponse):
    status_code = 201

    def __init__(self, *args, **kwargs):
        location = ''

        if 'location' in kwargs:
            location = kwargs['location']
            del(kwargs['location'])

        super(CustomResponseCreated, self).__init__(*args, **kwargs)
        self.location = location    


class CustomResponseHandler(ResponseHandler):
    def handle_cache_control_customrequest(self, request, response):
        return response

    def create_response_customrequest(self, request, content, content_type=None, **response_kwargs):
        return CustomResponse(content)

    def get_default_response_class_customrequest(self, request):
        return CustomResponse

    def get_unauthorized_response_class_customrequest(self, request):
        return CustomResponseUnauthorized    

    def get_unauthorized_request_response_customrequest(self, request):
        raise CustomResponseErrorUnauthorized(response=CustomResponseUnauthorized())

    def get_created_response_class_customrequest(self, request):
        return CustomResponseCreated

    def get_no_content_response_customrequest(self, request):
        return CustomResponseNoContent()

    def get_accepted_response_class_customrequest(self, request):
        return CustomResponseAccepted

    def get_bad_request_response_customrequest(self, request, content):
        raise CustomResponseErrorBadRequest(response=CustomResponseBadRequest(content))
        
    def get_method_notallowed_response_customresponse(self, request, content):
        raise CustomResponseErrorMethodNotAllowed(response=CustomResponseMethodNotAllowed(content))

    def get_too_many_request_response_customrequest(self, request):
        raise CustomResponseErrorTooManyRequests(response=CustomResponseTooManyRequests())

    def get_multiple_choices_response_customrequest(self, request, content):
        return CustomResponseMultipleChoices(content)

    def get_not_found_response_customrequest(self, request):
        raise CustomResponseErrorNotFound(response=CustomResponseNotFound())

    def get_created_response_customrequest(self, request, location):
        return CustomResponseCreated(location=location)

    def get_not_implemented_response_customrequest(self, request):
        raise CustomResponseErrorNotImplemented(response = CustomResponseNotImplemented())