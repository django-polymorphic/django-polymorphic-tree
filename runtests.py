#!/usr/bin/env python -Wd
import sys
import warnings
from os import path

import django
from django.conf import global_settings as default_settings
from django.conf import settings
from django.core.management import execute_from_command_line

# python -Wd, or run via coverage:
warnings.simplefilter("always", DeprecationWarning)

# Give feedback on used versions
sys.stderr.write(f"Using Python version {sys.version[:5]} from {sys.executable}\n")
sys.stderr.write(
    "Using Django version {} from {}\n".format(django.get_version(), path.dirname(path.abspath(django.__file__)))
)

if not settings.configured:
    module_root = path.dirname(path.realpath(__file__))

    sys.path.insert(0, path.join(module_root, "example"))

    settings.configure(
        DEBUG=False,  # will be False anyway by DjangoTestRunner.
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        DEFAULT_AUTO_FIELD="django.db.models.AutoField",
        CACHES={
            # By explicit since many tests also need the caching support
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "unique-snowflake",
            }
        },
        SECRET_KEY="testtest",
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": (),
                "OPTIONS": {
                    "debug": True,
                    "loaders": (
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ),
                    "context_processors": (
                        "django.template.context_processors.debug",
                        "django.template.context_processors.i18n",
                        "django.template.context_processors.media",
                        "django.template.context_processors.request",
                        "django.template.context_processors.static",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ),
                },
            },
        ],
        INSTALLED_APPS=(
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.messages",
            "django.contrib.sites",
            "mptt",
            "polymorphic",
            "polymorphic_tree",
            "polymorphic_tree.tests",
        ),
        # we define MIDDLEWARE_CLASSES explicitly, the default were changed in django 1.7
        MIDDLEWARE=(
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.locale.LocaleMiddleware",  # / will be redirected to /<locale>/
        ),
        ROOT_URLCONF="example.urls",
        TEST_RUNNER="django.test.runner.DiscoverRunner",
    )


DEFAULT_TEST_APPS = [
    "polymorphic_tree",
]


def runtests():
    other_args = list(filter(lambda arg: arg.startswith("-"), sys.argv[1:]))
    test_apps = list(filter(lambda arg: not arg.startswith("-"), sys.argv[1:])) or DEFAULT_TEST_APPS
    argv = sys.argv[:1] + ["test", "--traceback"] + other_args + test_apps
    execute_from_command_line(argv)


if __name__ == "__main__":
    runtests()
