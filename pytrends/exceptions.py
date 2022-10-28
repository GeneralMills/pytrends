class ResponseError(Exception):
    """ Something was wrong with the response from Google. """

    def __init__(self, message, response):
        super().__init__(message)
        # pass response so it can be handled upstream
        self.response = response

    @classmethod
    def from_response(cls, response):
        message = f'The request failed: Google returned a response with code {response.status_code}'
        return cls(message, response)


class TooManyRequestsError(ResponseError):
    """ Exception raised when the backend returns a 429 error code. """
    pass
