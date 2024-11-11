from django.shortcuts import render
from rest_framework.exceptions import ValidationError


def email_validator(email):
    """
    This function validates an email address
    """
    if email.endswith('@gmail.com'):
        return True

    if email.count('@') > 1:
        raise ValidationError("Email address must have only one @")

    return None