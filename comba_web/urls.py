"""comba_web URL Configuration

"""
from django.conf.urls import include, url
from django.contrib import admin

admin.autodiscover()
import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^monitor/', include('comba_web_monitor.urls')),
    url(r'^programme/', include('comba_web_programme.urls')),
    url(r'^api/v1.0/', include('comba_web_api.urls')),
    url(r'^', 'comba_web.views.index.home', name='index'),
]
