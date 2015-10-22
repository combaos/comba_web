"""comba_web URL Configuration
"""
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from views.broadcasts import *
from views.override import *
from views.prearrange import *
from django.core.urlresolvers import reverse_lazy


admin.autodiscover()

urlpatterns = [
    url(r'^broadcast$', BroadcastItem.as_view(), name='broadcast'),
    url(r'^broadcast/$', BroadcastItem.as_view(), name='broadcast'),
    url(r'^broadcast/reset/$', BroadcastReset.as_view(), name='reset'),
    url(r'^broadcast/override/$', BroadcastOverride.as_view(), name='override'),
    url(r'^broadcasts$', BroadcastList.as_view(), name='broadcasts'),
    url(r'^broadcasts/$', BroadcastList.as_view(), name='broadcasts'),
    url(r'^broadcasts/download$', BroadcastItem.as_view(), name='download'),
    url(r'^broadcasts/download/$', BroadcastItem.as_view(), name='download'),
    url(r'^prearrange/$', BroadcastPrearrangeList.as_view(), name='prearrange'),
    url(r'^prearrange/add/$', BroadcastPrearrangeAdd.as_view(), name='prearrange_add'),
    url(r'^prearrange/order/$', BroadcastPrearrangeOrder.as_view(), name='prearrange_order'),
    url(r'^prearrange/remove/$', BroadcastPrearrangeRemove.as_view(), name='prearrange_remove'),
]
