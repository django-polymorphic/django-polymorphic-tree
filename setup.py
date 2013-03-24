#!/usr/bin/env python
from setuptools import setup, find_packages
from os.path import dirname, join
import sys, os

# When creating the sdist, make sure the django.mo file also exists:
if 'sdist' in sys.argv:
    try:
        os.chdir('polymorphic_tree')
        from django.core.management.commands.compilemessages import compile_messages
        compile_messages(sys.stderr)
    finally:
        os.chdir('..')


setup(
    name='django-polymorphic-tree',
    version='0.8.7',
    license='Apache License, Version 2.0',

    install_requires=[
        'django-polymorphic>=0.3.1',
        'django-mptt>=0.5.1',
        'django-tag-parser>=1.0.0',
    ],
    requires=[
        'Django (>=1.3)',   # Using staticfiles
    ],
    description="A polymorphic mptt structure to display content in a tree.",
    long_description=open(join(dirname(__file__), 'README.rst')).read(),

    author='Diederik van der Boor',
    author_email='opensource@edoburu.nl',

    url='https://github.com/edoburu/django-polymorphic-tree',
    download_url='https://github.com/edoburu/django-polymorphic-tree/zipball/master',

    packages=find_packages(),
    include_package_data=True,

    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ]
)
