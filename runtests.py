#!/usr/bin/env python -Wd
import sys
import warnings
import django
from django.core.management import execute_from_command_line
from django.conf import settings, global_settings as default_settings
from os import path


# python -Wd, or run via coverage:
warnings.simplefilter('always', DeprecationWarning)

# Give feedback on used versions
sys.stderr.write('Using Python version {0} from {1}\n'.format(sys.version[:5], sys.executable))
sys.stderr.write('Using Django version {0} from {1}\n'.format(
    django.get_version(),
    path.dirname(path.abspath(django.__file__)))
)

if not settings.configured:
    module_root = path.dirname(path.realpath(__file__))

    sys.path.insert(0, path.join(module_root, 'example'))

    settings.configure(
        DEBUG = False,  # will be False anyway by DjangoTestRunner.
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        },
        CACHES = {
            # By explicit since many tests also need the caching support
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'unique-snowflake',
            }
        },
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': (),
                'OPTIONS': {
                    'debug': True,
                    'loaders': (
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    ),
                    'context_processors': (
                        'django.template.context_processors.debug',
                        'django.template.context_processors.i18n',
                        'django.template.context_processors.media',
                        'django.template.context_processors.request',
                        'django.template.context_processors.static',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                    ),
                },
            },
        ],
        INSTALLED_APPS = (
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.messages',
            'django.contrib.sites',
            'django.contrib.admin',
            'mptt',
            'polymorphic',
            'polymorphic_tree',
            'polymorphic_tree.tests',
        ),
        # we define MIDDLEWARE_CLASSES explicitly, the default were changed in django 1.7
        MIDDLEWARE_CLASSES=(
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.locale.LocaleMiddleware',  # / will be redirected to /<locale>/
        ),
        MIDDLEWARE=(
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.locale.LocaleMiddleware',  # / will be redirected to /<locale>/
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
        ),
        ROOT_URLCONF = 'example.urls',
        TEST_RUNNER = 'django.test.runner.DiscoverRunner',
    )


DEFAULT_TEST_APPS = [
    'polymorphic_tree',
]


def runtests():
    other_args = list(filter(lambda arg: arg.startswith('-'), sys.argv[1:]))
    test_apps = list(filter(lambda arg: not arg.startswith('-'), sys.argv[1:])) or DEFAULT_TEST_APPS
    argv = sys.argv[:1] + ['test', '--traceback'] + other_args + test_apps
    execute_from_command_line(argv)

if __name__ == '__main__':
    runtests()
