"""All custom exceptions.

  Typical usage example:

  raise ValidationError('error_message');
"""


class ValidationError(Exception):
    def __init__(self, error):
        self.error = error
