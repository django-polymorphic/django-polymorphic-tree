#!/usr/bin/env python
from setuptools import setup, find_packages
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
    version='0.8.3',
    license='Apache License, Version 2.0',

    install_requires=[
        'Django>=1.3.0',
        'django-polymorphic>=0.2',
        'django-mptt>=0.5.1',
    ],
    description="A polymorphic mptt structure to display content in a tree.",
    long_description=open('README.rst').read(),

    author='Diederik van der Boor',
    author_email='opensource@edoburu.nl',

    url='https://github.com/edoburu/django-polymorphic-tree',
    download_url='https://github.com/edoburu/django-polymorphic-tree/zipball/master',

    packages=find_packages(),
    include_package_data=True,

    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
