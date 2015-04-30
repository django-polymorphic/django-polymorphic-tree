import django

# allow test runners in Django < 1.7 to find the tests
if django.VERSION[:2] < (1, 7):
    from .test_models import *
