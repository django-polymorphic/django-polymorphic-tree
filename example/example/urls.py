from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'example.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', admin.site.urls),
]
