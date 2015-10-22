__author__ = 'michel'
# -*- coding: utf-8 -*-
from django.conf import settings
from . import CombaApiView
from rest_framework.response import Response
from werkzeug import secure_filename
import tempfile
from django.http import Http404
from comba_web.models import ModelBroadcastEventOverride
from comba_lib.database.broadcasts import *



#------------------------------------------------------------------------------------------#

class BroadcastPrearrangeList(CombaApiView):
    """
    List prearranged tracks for a given broadcast event
    @api {post} /prearrange             2. List prearranged tracks of a given broadcast event
    @apiName prearrange
    @apiGroup Prearrange
    @apiDescription     <p>Get the tracklist in order to get track ids (trackid) for further use.</p>

    @apiExample {curl} Curl example:
        curl --user user:pass -H "Content-type: application/json" \
        -X POST http://my.combaserver.tld/api/v1.0/prearrange \
        -d '{"identifier": "102-2015-01-02-19-00-00"}'


    @apiExample {python} Python example:
        import requests

        def addTrack(identifier, file):
            files = {'audio': open(file, 'rb')}
            data = {'identifier': identifier}
            url = "http://my.combaserver.tld/api/v1.0/prearrange"
            r = requests.post(url, files=files, data=data, auth=('user', 'pass'))
            return r.json()

        addTrack('102-2015-01-02-19-00-00', /path/to/mp3/interview-angela-merkel.mp3)

    @apiParam {String} identifier       Broadcast event unique ID.
    @apiParam {String} programme_id     find events with <programme_id>.
    @apiParam {String} station_id       find events with <station_id>.
    @apiParam {String} start            Start date of the event (format %Y-%m-%dT%H:%M)
    @apiParam {String} end              End date of the event (format %Y-%m-%dT%H:%M)
    @apiSuccess {Object[]} tracks       Track list of Prearrangement
    @apiSuccessExample {json} Success-Response:
     HTTP/1.1 200 OK
      {
        'totalLength': 2557.0, # total lenght in seconds
        'success': True,
        'completed': 35, # 35% completed, still missing 65% audio data
        'error': '',
        'message': ''
        'tracks':
            [
                {
                    'trackid' : '55aa3d0048ea2b3a973b74c8',
                    'mimetype': 'mpeg',
                    'ordering': 1,
                    'start': '2015-07-08T09:00',
                    'filename': 'interview-barack-obama-2013-05-14.mp3',
                    'identifier': 'replay--294-10-2015-07-07-16-00-00',
                    'bitrate': 128000
                },
                {
                    'trackid' : '55aa44b348ea2b3dbd2ea813',
                    'mimetype': 'mpeg',
                    'ordering': 2,
                    'start': '2015-07-08T09:00',
                    'location': 'comment-2013-05-14.mp3',
                    'identifier': 'replay--294-10-2015-07-07-16-00-00',
                    'bitrate': 128000
                }, ...
      }
    """

    def getResponse(self, request, args):
        """
        Get the Post
        """
        queries = Q()
        

        if args.get('identifier'):
            queries = queries & Q(identifier=args.get('identifier'))

        if args.get('programme_id'):
            queries = queries & Q(programme_id=args.get('programme_id'))

        if args.get('station_id'):
            queries = queries & Q(station_id=args.get('station_id'))

        if args.get('start'):
            t = datetime.datetime.strptime(args.get('start'), '%Y-%m-%dT%H:%M')
            queries = queries & Q(start=t)

        if args.get('end'):
            t = datetime.datetime.strptime(args.get('end'), '%Y-%m-%dT%H:%M')
            queries = queries & Q(end=t)

        events = BroadcastEvent.objects(queries)

        if len(events) == 0:
            raise Http404

        event = events[0]

        result = {'message':'', 'success': False, 'error': ''}

        if event:
            overrides = BroadcastEventOverride.objects(broadcast_event=event)
        else:
            result['error'] = 'Could not find a valid event'

        if overrides:
            overrideslist = []
            result['success'] = True
            result['totalLength'] = round(overrides[0].totalLength())
            result['completed'] = overrides[0].filled()
            for override in overrides:
                ov = {}
                ov['identifier'] = override.identifier
                ov['trackid'] = str(override.id)
                ov['filename'] = os.path.basename(str(override.location).replace('file://',''))
                ov['ordering'] = override.ordering
                ov['mimetype'] = override.mimetype
                ov['bitrate'] = override.bitrate
                ov['start'] = override.start.strftime('%Y-%m-%dT%H:%M')
                overrideslist.append(ov)
            result['tracks'] = overrideslist


        if result['error']:
            result['success'] = False
            result['message'] = result['error']
        else:
            result['success'] = True

        return Response(result)


#------------------------------------------------------------------------------------------#

class BroadcastPrearrangeAdd(CombaApiView):
    """
    Upload  audiofile and add it to the track list
    @api {post} /prearrange/add             2. Upload  audiofile and add it to the track list
    @apiName add
    @apiGroup Prearrange

    @apiDescription     <p>You can upload audio files in order to prearrange a program . Before of course you have to determine the identifier of the broadcast event via API, </p>

    @apiExample {curl} Curl example:
        curl --user user:pass -H "Content-type: application/json" \
        -X POST http://my.combaserver.tld/api/v1.0/prearrange/add \
        -F audio=@/path/to/mp3/interview-angela-merkel.mp3
        -d '{"identifier": "102-2015-01-02-19-00-00"}'


    @apiExample {python} Python example:
        import requests

        def addTrack(identifier, file):
            files = {'audio': open(file, 'rb')}
            data = {'identifier': identifier}
            url = "http://my.combaserver.tld/api/v1.0/prearrange/add"
            r = requests.post(url, files=files, data=data, auth=('user', 'pass'))
            return r.json()

        addTrack('102-2015-01-02-19-00-00', '/path/to/mp3/interview-angela-merkel.mp3')

    @apiParam {String} identifier       Prearrangement belongs to event with unique ID.
    @apiParam {String} programme_id     Prearrangement belongs to event with  with <programme_id>.
    @apiParam {String} station_id       Prearrangement belongs to event with <station_id>.
    @apiParam {String} start            Prearrangement belongs to event with start date of (format %Y-%m-%dT%H:%M)
    @apiParam {String} end              Prearrangement belongs to event with end date of (format %Y-%m-%dT%H:%M)
    @apiParam {Fileobject} audio        File Upload

    @apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
      {
        'success': True,
        'error': '',
        'identifier': 'replay--294-10-2015-07-07-16-00-00',
        'ordering':'3',
        'trackid': '55aa72c448ea2b524efaf178',
        'message': '',
        'filename': 'interview-angela-merkel-2013-05-14-34.mp3'
      }
    """

    def getResponse(self, request, args):

        def save_file(f, path):
            with open(path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
                    
        response = {'success': False, 'response': ''}
        queries = Q()

        if args.get('identifier'):
            queries = queries & Q(identifier=args.get('identifier'))

        if args.get('programme_id'):
            queries = queries & Q(programme_id=args.get('programme_id'))

        if args.get('station_id'):
            queries = queries & Q(station_id=args.get('station_id'))

        if args.get('start'):
            t = datetime.datetime.strptime(args.get('start'), '%Y-%m-%dT%H:%M')
            queries = queries & Q(start=t)

        if args.get('end'):
            t = datetime.datetime.strptime(args.get('end'), '%Y-%m-%dT%H:%M')
            queries = queries & Q(end=t)


        events = BroadcastEvent.objects(queries)

        if len(events) == 0:
            raise Http404

        event = events[0]

        if args.get('audio'):
            file_object = request.FILES['audio']
            fileName = secure_filename(file_object.name)
            fid, path = tempfile.mkstemp()

            try:
                save_file(file_object, path)
            except:
                response['response'] = "Upload Error"
                return Response(response)
            result = ModelBroadcastEventOverride.add(event, settings.COMBA.get('upload_folder', '/var/audio/preprod/'), fileName, path)
        else:
            result = {'error': "Upload empty"}


        if result['error']:
            response['response'] = result['error']
        else:
            response['identifier'] = event.identifier
            if result['preprod_id']:
                response['trackid'] = str(result['preprod_id'])
            if result['ordering']:
                response['ordering'] = result['ordering']
            if result['location']:
                response['filename'] = os.path.basename(str(result['location']).replace('file://',''))
            response['success'] = True

        return Response(response)


#------------------------------------------------------------------------------------------#

class BroadcastPrearrangeOrder(CombaApiView):
    """
    Define position of a track in the track list
    @api {post} /prearrange/order             3. Change the sort order of the track list
    @apiDescription  Define the position of a track in the track list of a broadcast event
    @apiName order
    @apiGroup Prearrange

    @apiExample {curl} Curl example:
        curl --user user:pass -H "Content-type: application/json" \
        -X POST http://my.combaserver.tld/api/v1.0/prearrange/order \
        -d '{'trackid': '55a257e848ea2b25d71980gh', 'position': 2}'

    @apiExample {python} Python example:
        import requests

        def setTrackPosition(trackid, position):
            data = {'trackid': trackid, 'position': position}
            url = "http://my.combaserver.tld/api/v1.0/prearrange/order"
            r = requests.post(url, data=data, auth=('user', 'pass'))
            return r.json()

        // will be the 3. track, because first pos is zero
        setTrackPosition('55a257e848ea2b25d71980gh', 2)

    @apiParam {String} trackid          track Database ID.
    @apiParam {Int} position            new position in track list

    @apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
      {
        'eventid': '55a257e848ea2b25d719803e',
        'position': 5,
        'message': 'Success!',
        'success': True,
        'trackid': '55aa814948ea2b584c838700'
      }
    """
    def getResponse(self, request, args):

        response = {'success': False, 'response': ''}
        args = self.reqparse.parse_args()
        result = ModelBroadcastEventOverride.updateordering(args.get('trackid'), int(args.get('position')))

        if result['error']:
            response['response'] = 'Could not reorder track'
        else:
            response['response'] = 'Success!'
            response['eventid'] = str(result['event_id'])
            response['trackid'] = str(result['track_id'])
            response['position'] = result['position']
            response['success'] = True

        return Response(response)

#------------------------------------------------------------------------------------------#

class BroadcastPrearrangeRemove(CombaApiView):
    """
    Remove a track from track list
    @api {post} /prearrange/remove       4. Remove tracks

    @apiName remove
    @apiGroup Prearrange

    @apiDescription    <p>Remove tracks from the tracklist of a prearranged program</p>
    @apiParam {String} trackid          track Database ID.

    @apiExample {curl} Curl example:
        curl --user user:pass -H "Content-type: application/json" \
        -X POST http://my.combaserver.tld/api/v1.0/prearrange/remove \
        -d '{'trackid': '55a257e848ea2b25d71980gh'}'

    @apiExample {python} Python example:
        import requests

        def removeTrack(trackid):
            data = {'trackid': trackid}
            url = "http://my.combaserver.tld/api/v1.0/prearrange/remove"
            r = requests.post(url, data=data, auth=('user', 'pass'))
            return r.json()


        removeTrack('55a257e848ea2b25d71980gh')

    @apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
      {
        'eventid': '55a257e848ea2b25d719803e',
        'position': 5,
        'message': 'Success!',
        'success': True,
        'trackid': '55aa814948ea2b584c838700'
      }
    """

    def getResponse(self, request, args):

        response = {'success': False, 'response': ''}
        args = self.reqparse.parse_args()
        result = ModelBroadcastEventOverride.remove(args.get('trackid'))

        if result['error']:
            if result['error'] == 1:
                response['response'] = 'Track not found'
            if result['error'] == 2:
                response['response'] = 'Could not remove track'
        else:
            response['response'] = 'Success!'
            response['trackid'] = str(result['preprod_id'])
            response['filename'] = os.path.basename(str(result['location']).replace('file://',''))
            response['success'] = True

        return Response(response)
