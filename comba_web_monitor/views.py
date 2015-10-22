__author__ = 'michel'
from django.conf import settings
from comba_lib.base.schedulerconfig import CombaSchedulerConfig
from comba_lib.service.icecast import IcecastServer
from comba_clientapi.zmqadapter import ClientZMQAdapter
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from .models import *
import simplejson, redis
from django.http import HttpResponse
from django.shortcuts import render_to_response, render as render_template
from django.contrib.auth.decorators import login_required

@login_required()
def monitor(request):
    model = ModelSysInfo()
    trackStart = model.getNextTrackstart()
    playerState = False if not trackStart else  model.getPlayerInfo()

    context =  {
                                    'trackStart': trackStart,
                                    'recordStart': model.getNextRecordstart(),
                                    'recorderState': model.getDumpInfo(),
                                    'playerState': playerState,
                                    'playlistStart': model.getNextPlayliststart(),
                                    'load': model.getLoad(),
                                    'diskfree': model.getFreeSpace(),
                                    'componentStates': model.getComponentStates()
                                }

    return render_template(request, 'monitor.html', context)

@login_required()
def scheduler(request):
    scheduler_path =  settings.SCHEDULER_PATH
    schedulerconfig = CombaSchedulerConfig(scheduler_path)
    jobs =  schedulerconfig.getJobs()
    jobs = sorted(jobs, key=lambda k: k['time'])
    html = render_to_string('scheduler.html', {'jobs':jobs})
    data = {'data': html}
    return HttpResponse(simplejson.dumps(data),content_type='application/json')

@login_required()
def channels(request):
    db = redis.Redis()
    print "hier gehtn die Kanaele"
    (username, password) = db.get('internAccess').split(':')
    adapter = ClientZMQAdapter("localhost", 9099)
    adapter.setUsername(username)
    adapter.setPassword(password)
    adapter.send('allData')
    resp = simplejson.loads(adapter.receive())
    channels = {}

    if resp.has_key('value'):
        channels = resp['value']
        channels = sorted(channels.iteritems(), key=lambda (k,v): (v,k))

    html = render_to_string('channels.html', {'channels': channels})
    data = {'data': html}
    return HttpResponse(simplejson.dumps(data),content_type='application/json')

@login_required()
def sysinfo(request):
    model = ModelSysInfo()
    trackStart = model.getNextTrackstart()
    playerState = False if not trackStart else  model.getPlayerInfo()
    html = render_to_string('sysinfo.html',
                                {
                                    'trackStart': trackStart,
                                    'recordStart': model.getNextRecordstart(),
                                    'recorderState': model.getDumpInfo(),
                                    'playerState': playerState,
                                    'playlistStart': model.getNextPlayliststart(),
                                    'load': model.getLoad(),
                                    'diskfree': model.getFreeSpace(),
                                    'componentStates': model.getComponentStates()
                                }
                           )

    data = {'data': html}
    return HttpResponse(simplejson.dumps(data),content_type='application/json')

@login_required()
def stream(request):
    message = ""
    mounts = []
    if settings.USE_ICECAST:
        mountpoint = str('/' + settings.COMBA.get('stream_mountpoint')).replace('//','/')
        icecast = IcecastServer('comba',
                            settings.COMBA.get('stream_host'),
                            settings.COMBA.get('stream_port'),
                            settings.COMBA.get('stream_admin_user'),
                            settings.COMBA.get('stream_admin_password'),
                            mountpoint)
        mounts = icecast.Mounts

    else:

        message = _("No Stream available")
    html = render_to_string('stream.html', {'mounts':mounts, 'message':message})
    data = {'data': html}
    return HttpResponse(simplejson.dumps(data),content_type='application/json')

@login_required()
def events(request,component):
    model = ModelEvents()
    events = model.getEvents(component)
    return HttpResponse(simplejson.dumps(events),content_type='application/json')

