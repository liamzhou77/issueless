"""All custom exceptions.

  Typical usage example:

  raise FormValidationError('error_message');
"""


class FormValidationError(Exception):
    def __init__(self, message):
        self.message = message
