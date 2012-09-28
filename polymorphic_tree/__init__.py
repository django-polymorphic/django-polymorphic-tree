VERSION = (0,8,3)

# Do some sane version checking
import django
import mptt

if django.VERSION < (1,3,0):
    raise ImportError("At least Django 1.3.0 is required to run this application")

if mptt.VERSION < (0,5,1):
    raise ImportError("At least django-mptt 0.5.1 is required to run this application")
