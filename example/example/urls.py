import django
from django.conf.urls import include, url
from django.contrib import admin

if django.VERSION < (1,7):
    admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'example.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
]
