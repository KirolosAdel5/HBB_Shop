from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re

username_validator = RegexValidator(
    r'^[\w.@+\- ]+$',
    'Enter a valid username. This value may contain only letters, numbers, and @/./+/-/ space/_ characters.',
    'invalid'
)

def validate_password_complexity(value):
    # Define a regular expression pattern to enforce password complexity
    pattern = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[\W_])[\w\W_]+$'

    if not re.match(pattern, value):
        raise ValidationError(
            "Password must contain at least one digit, one uppercase letter, one lowercase letter, and one special symbol."
        )