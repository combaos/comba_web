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
"""
from django.conf.urls import include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^sysinfo/', 'comba_web_monitor.views.sysinfo', name='sysinfo'),
    url(r'^channels/', 'comba_web_monitor.views.channels', name='channels'),
    url(r'^scheduler/', 'comba_web_monitor.views.scheduler', name='scheduler'),
    url(r'^stream/', 'comba_web_monitor.views.stream', name='stream'),
    url(r'^events/([a-z]+)/$', 'comba_web_monitor.views.events', name='events'),
    url(r'^', 'comba_web_monitor.views.monitor', name='monitor'),
]
