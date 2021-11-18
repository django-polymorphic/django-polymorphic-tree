from django.contrib import admin
from django.urls import path

urlpatterns = [
    # Examples:
    # url(r'^$', 'example.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    path("admin/", admin.site.urls),
]
