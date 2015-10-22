"""comba_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
    def preprod_order(request, preprod_id, dir):
"""
from django.conf.urls import include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^preprod/(?P<eventid>[0-9a-z]+)/$', 'comba_web_programme.views.preprod', name='preprod'),
    url(r'^preprod_upload/$', 'comba_web_programme.views.preprod_upload', name='preprod_upload'),
    url(r'^preprod_download_url/$', 'comba_web_programme.views.preprod_download_url', name='preprod_download_url'),
    url(r'^preprod_delete/([0-9a-z]+)/([0-9a-z]+)/$', 'comba_web_programme.views.preprod_delete', name='preprod_delete'),
    url(r'^preprod_order/([0-9a-z]+)/([0-9a-z]+)/$', 'comba_web_programme.views.preprod_order', name='preprod_order'),
    url(r'^override/$', 'comba_web_programme.views.override', name='override'),
    url(r'^override_reset/(?P<eventid>[0-9a-z]+)/$', 'comba_web_programme.views.override_reset', name='override_reset'),
    url(r'^override_modal/(?P<eventid>[0-9a-z]+)/$', 'comba_web_programme.views.programme', name='override_modal'),
    url(r'^(?P<eventid>[0-9a-z]+)/(?P<message>\w+)/$', 'comba_web_programme.views.programme', name='programme'),
    url(r'^(?P<eventid>[0-9a-z]+)/$', 'comba_web_programme.views.programme', name='programme'),
    url(r'^$', 'comba_web_programme.views.programme', name='programme'),

]
