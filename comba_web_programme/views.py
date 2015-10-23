# -*- coding: utf-8 -*-
__author__ = 'michel'
from django.conf import settings
from comba_web.models import *
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from comba_lib.database.broadcasts import *
import urlparse, tempfile
from django.utils.translation import ugettext as _
from werkzeug import secure_filename
from django.core.urlresolvers import reverse
import simplejson
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.translation import get_language_info

"""
Web list programmes and search
"""

@login_required()
def programme(request, eventid="", message=''):
    searchquery = Q()
    datefromquery = Q()
    search = ""
    datefrom = ""
    dateto = ""

    li = get_language_info('de')
    print(li['name'], li['name_local'], li['bidi'])
    print request.LANGUAGE_CODE
    query = {'search':'', 'from':'','to':'','page':''}

    if request.method == 'POST':
        query = request.POST
    else:
        if request.session.get('search'):
            query = request.session.get('search')
    if query.has_key('search') and query['search']:
        search = query['search']
    if query.has_key('from') and query['from']:
        datefrom = query['from']
    if query.has_key('to') and query['to']:
        dateto= query['to']

    request.session['search'] = query

    if search:
        #events = BroadcastEvent.objects.search_text( search)
        searchquery = Q(__raw__={'title': {'$regex': search, '$options': 'i' }}) \
                        | Q(__raw__={'subject': {'$regex': search, '$options': 'i' }})

    if datefrom:
        f = datetime.datetime.strptime(datefrom, '%Y-%m-%d')
        datefromquery = Q(start__gte=f)

    if dateto:
        t = datetime.datetime.strptime(dateto, '%Y-%m-%d')
    else:
        t = datetime.datetime.now()

    datetoquery = Q(start__lte=t)
    page = request.GET.get('page', 1)
    limit = 20
    forward = (int(page) * limit) - limit
    offset = forward if forward >= 0 else 0
    events = BroadcastEvent.objects(datefromquery & datetoquery & searchquery).order_by('-start').skip(offset).limit(limit)
    paginator = Paginator(events, limit)
    eventlist = []
    for event in events:
        tracks = []
        event.tracks = []
        if  event.overwrite_event:
            tracks = BroadcastEventTrack.objects(broadcast_event=event.overwrite_event)
            event.hasFile = event.overwrite_event.fileExists()
            event.filename = os.path.basename(str(event.overwrite_event.location).replace('file://','')) if event.overwrite_event.location else ""
        else:
            tracks = BroadcastEventTrack.objects(broadcast_event=event)
            event.hasFile = event.fileExists()
            event.filename = os.path.basename(str(event.location).replace('file://','')) if event.location else ""
        for track in tracks:
            track.filename = os.path.basename(str(track.location).replace('file://',''))
            event.tracks.append(track)

        event.procOverrides = 0
        overrides = BroadcastEventOverride.objects(broadcast_event=event)
        if overrides:
            event.procOverrides = overrides[0].filled()

        event.overrides = overrides
        eventlist.append(event)
    page_obj = None
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page_obj = paginator.page(paginator.num_pages)

    pages_list = []
    list_additems = 5 if page_obj.number > 5 else (10 - page_obj.number)
    list_previtems = 5 if page_obj.number > 5 else 6

    if page_obj.number > (paginator.num_pages - 6):
        list_previtems =  10 - (paginator.num_pages - page_obj.number)
    for page in paginator.page_range:
        if (page_obj.number - list_previtems) < page and not (page > (page_obj.number + list_additems)):
            pages_list.append(page)

    if eventid:
        return render(request, 'modal_override.html', {'query':query, 'orig_id':eventid,'eventlist':eventlist, 'pages_list':pages_list, 'paginator':paginator, 'page_obj':page_obj})
    else:
        return render(request, 'programme.html', {'query':query, 'eventlist':eventlist, 'pages_list':pages_list, 'paginator':paginator, 'page_obj':page_obj})

"""
Web manage preproduction
"""
@login_required()
def preprod(request, eventid):
    ##message = request.args.get('message')
    message = ""
    totalLength = 0
    filled = 0
    red = 0
    event = BroadcastEvent.objects.get(id=eventid)
    overrides = []

    if event:
        overrides = BroadcastEventOverride.objects(broadcast_event=event)
    if overrides:
        totalLength = round(overrides[0].totalLength())
        filled = overrides[0].filled()

    if int(filled) > 100:
        green= int((float(100/float(filled))) * 100)
        red = 100 - green
    else:
        green = int(filled)
        red = 0
    return render(request, 'preprod.html', {'event':event, 'message':message, 'overrides':overrides, 'red':red, 'green':green, 'procent':filled, 'totalLength':totalLength })


"""
Web upload pre-production
"""
@login_required()
def preprod_upload(request):
    def save_file(f, path):
        with open(path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
    id = request.POST['returnid']
    event = BroadcastEvent.objects.get(id=id)
    message = ""

    if request.method == 'POST' and 'audio' in request.FILES:
        file = request.FILES['audio']
        fileName = secure_filename(file.name)
        fid, path = tempfile.mkstemp()

        try:
            save_file(file, path)
        except:
            message = _("Upload Error")
            return redirect('comba_web_programme.views.preprod', eventid=id, message=message)

        result = ModelBroadcastEventOverride.add(event, settings.COMBA.get('upload_folder', '/var/audio/preprod/'), fileName, path)
        if result['error']:
            message = result['error']
    else:
        message = _("Upload empty")
    return redirect(reverse('programme') + '#li-' + id)


"""
Web upload pre-production
"""
@login_required()
def preprod_download_url(request):
    def getFileName(url,openUrl):
        if 'Content-Disposition' in openUrl.info():
            # If the response has Content-Disposition, try to get filename from it
            cd = dict(map(
                lambda x: x.strip().split('=') if '=' in x else (x.strip(),''),
                openUrl.info()['Content-Disposition'].split(';')))
            if 'filename' in cd:
                filename = cd['filename'].strip("\"'")
                if filename: return filename
        # if no filename was found above, parse it out of the final URL.
        return os.path.basename(urlparse.urlsplit(openUrl.url)[2])

    id = request.POST['returnid']
    url = request.POST['audiourl']
    req = urllib2.Request(url, headers={ 'User-Agent': 'Mozilla/5.0' })
    event = BroadcastEvent.objects.get(id=id)
    message = ""
    if request.method == 'POST' and url:
        file = urllib2.urlopen(req)
        try:
            fileName = secure_filename(getFileName(url,file))
            fid, path = tempfile.mkstemp()
            remote_file = urllib2.urlopen(req)
            with open(path, 'wb') as f:
                shutil.copyfileobj(remote_file,f)
            result = ModelBroadcastEventOverride.add(event, settings.COMBA.get('upload_folder', '/var/audio/preprod/'), fileName, path)
        finally:
            file.close()


    if result['error']:
        message = result['error']
    return redirect(reverse('programme') + '#li-' + id)



"""
Web delete pre-production item
"""
@login_required()
def preprod_delete(request, event_id, preprod_id):
    error=""
    result = ModelBroadcastEventOverride.remove(preprod_id)
    if result.has_key('error'):
        if result['error'] == 1:
            error = _("Entry doesn't exist.")
        if result['error'] == 2:
            error = _("Could not delete %(location)", location=result['location'])

    return redirect('preprod', eventid=str(event_id))

"""
Web reorder pre-production item
"""
@login_required()
def preprod_order(request, preprod_id, dir):
    result = ModelBroadcastEventOverride.reorder(preprod_id, dir)

    return redirect('preprod', eventid=str(result['event_id']))

@login_required()
def override(request):
    orig_id = request.GET['origid']
    replace_id = request.GET['replaceid']
    result = ModelBroadcastEvent.replace(orig_id, replace_id)
    return HttpResponse(simplejson.dumps(result),content_type='application/json')

@login_required()
def override_reset(request, eventid):

    result = ModelBroadcastEvent.reset(eventid)
    return HttpResponse(simplejson.dumps(result),content_type='application/json')