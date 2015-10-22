__author__ = 'michel'
# -*- coding: utf-8 -*-
from . import CombaApiView
from rest_framework.response import Response
from sendfile import sendfile
from django.http import Http404
from comba_web_api.serializers.broadcast import BroadcastEventSerializer
from comba_web.models import ModelBroadcastEvent
from comba_lib.database.broadcasts import *


class BroadcastItem(CombaApiView):
    """
    Select a single item or download a file
    @api {post} /broadcasts/download 2. Downloads of archived programs
    @apiDescription                <p>Download an archived program as mp3</p>
        <p>It's recommanded to use /api/v1.0/broadcasts to get events identifier. Combining "start" and "programme_id" should also return a unique result</p>
    @apiName download
    @apiGroup Broadcasts

    @apiExample {curl} Curl example:
        curl --user user:pass -H "Content-type: application/json" \
        -X POST http://my.combaserver.tld/api/v1.0/broadcasts/download \
        -d '{"identifier": "102-2015-01-02-19-00-00"}' > /path/to/mp3/audio.mp3

    @apiExample {python} Python example:
        import requests

        def downloadProgram(identifier):
            data = {'identifier': identifier}
            url = "http://my.combaserver.tld/api/v1.0/broadcasts/download"
            r = requests.post(url, data=data, auth=('user', 'pass'))
            storePath = '/path/to/mp3/audio.mp3'
            fp = open(storePath, "wb")
            fp.write(r.content)
            fp.close()

        downloadProgram('102-2015-01-02-19-00-00')

    @apiParam {String} identifier Broadcast event unique ID.
    @apiParam {String} programme_id Programme ID.
    @apiParam {String} station_id Station ID.
    @apiParam {String} start Start date of the event (format %Y-%m-%dT%H:%M)
    @apiParam {String} end End date of the event (format %Y-%m-%dT%H:%M)

    """

    def getResponse(self, request, args):
        """
        Get Item
        """
        queries = Q()

        if args.get('current'):
            t = datetime.datetime.now()
            events = BroadcastEvent.objects(Q(start__lte=t)).order_by('-start').limit(1)

        else:

            if args.get('id'):
                queries = queries & Q(id = args.get('id'))

            if args.get('identifier'):
                queries = queries & Q(identifier = args.get('identifier'))


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
        if request.resolver_match.url_name == 'download':
            file = str(event.location).replace('file://', '')

            if(os.path.exists(file)):
                return sendfile(request, file, attachment=True)
            else:
                raise Http404
        else:
            serializer = BroadcastEventSerializer(event)
            return Response(serializer.data)


#------------------------------------------------------------------------------------------#

class BroadcastList(CombaApiView):
    """
    Get a list of broadcast events
    @api {post} /broadcasts        1. List and search
    @apiDescription                <p>Search for broadcast events.</p>
        <p>E.g. you can use parameter "start" to get a specific event, grab the identifier and download the recorded program.</p>
        <p>Use parameter "current" to get current running program.</p>
    @apiName broadcasts
    @apiGroup Broadcasts
    @apiExample {curl} Curl example:
        curl --user user:pass -H "Content-type: application/json" \
        -X POST http://my.combaserver.tld/api/v1.0/broadcasts \
        -d '{"datefrom":"2015-02-27", "dateto":"2015-03-01", "state":"archived", "rerun":false}'

    @apiExample {python} Python example:
        import requests
        def getBroadcast(datetime, program_id)
            data = {'start': datetime, 'program_id': program_id}
            url = "http://my.combaserver.tld/api/v1.0/broadcasts"
            r = requests.post(url, data=data, auth=('user', 'pass'))
            return r.json()

        result = getBroadcast('2015-07-08T11:00', 21)
        print "Got identifier " + result['broadcasts'][0]['identifier']
        # Got identifier 294-10-2015-07-07-16-00-00
    @apiParam {String} limit        return [limit] number of items
    @apiParam {String} limitstart   start list at [limitstart]
    @apiParam {String} identifier   broadcast event unique ID.
    @apiParam {Bool} current        get the current running event only
    @apiParam {String} title        find events by title
    @apiParam {String} program_id find events by program ID.
    @apiParam {String} station_id   find events by Station ID.
    @apiParam {String} start        find events by start date and time(format %Y-%m-%dT%H:%M)
    @apiParam {String} end          find events by end date and time (format %Y-%m-%dT%H:%M)
    @apiParam {String} state        find events by its states
    @apiParam {String} search       Search for a string in events titles or subjects
    @apiParam {String} datefrom     find events starting after [datefrom] (format %Y-%m-%d)
    @apiParam {String} dateto       find events ending before [dateto] (format %Y-%m-%d)
    @apiParam {String} datetimefrom find events starting after [datetimefrom] (format %Y-%m-%dT%H:%M)
    @apiParam {String} datetimeto   find events ending before [datetimeto] (format %Y-%m-%dT%H:%M)
    @apiParam {Bool} rerun          find reruns only
    @apiSuccess {Object[]} broadcasts       List of Broadcast events
    @apiSuccessExample {json} Success-Response:
         HTTP/1.1 200 OK
         {
            [
                {
                    'id': '54ac83f448ea2b1d9d284419',
                    'identifier':'replay--294-10-2015-07-07-16-00-00',
                    'replay_of':'10-2015-07-07-16-00-00',
                    'end':2015-07-08T11:00',
                    'description':'Informationen und Berichte',
                    'title':'Stoffwechsel',
                    'state':'created',
                    'station_id':'radioz',
                    'replay_of_datetime':'2015-07-07T16:00',
                    'start':'2015-07-08T09:00',
                    'program_id':'4',
                    'reccurrence_id':'294',
                    'rerun': True,
                    'duration':'2:00:00',
                    'station_name':'Radio Z',
                    'ressource_ready': False,
                    'subject':'listen to a lot of interviews with interesting people'
                }
            ]
         }

    """

    def getResponse(self, request, args):
        """
        Get users request, return broadcast events list
        """
        limit = 1000
        offset = 0

        queries = Q()
        many = False
        events = []
        if args.get('current'):
            t = datetime.datetime.now()
            events = BroadcastEvent.objects(Q(start__lte=t)).order_by('-start').limit(1)
            events = events[0]
        else:
            many = True
            if args.get('limit'):
                limit = args.get('limit')

            if args.get('limitstart'):
                offset = args.get('limitstart')

            if args.get('identifier'):
                queries = queries & Q(identifier=args.get('identifier'))

            if args.get('title'):
                queries = queries & Q(title=args.get('title'))

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

            if args.get('state'):
                queries = queries & Q(state=args.get('state'))

            if args.get('rerun'):
                queries = queries & Q(rerun=True)

            if args.get('search'):
                queries  = Q(__raw__={'title': {'$regex': args.get('search'), '$options': 'i' }}) \
                        | Q(__raw__={'subject': {'$regex': args.get('search'), '$options': 'i' }})

            if args.get('datetimefrom'):
                t = datetime.datetime.strptime(args.get('datetimefrom'), '%Y-%m-%dT%H:%M')
                queries = queries &  Q(start__gte=t)
            else:
                if args.get('datefrom'):
                    t = datetime.datetime.strptime(args.get('datefrom'), '%Y-%m-%d')
                    queries = queries &  Q(start__gte=t)

            if args.get('datetimeto'):
                t = datetime.datetime.strptime(args.get('datetimeto'), '%Y-%m-%dT%H:%M')
                queries = queries &  Q(start__lte=t)
            else:
                if args.get('dateto'):
                    t = datetime.datetime.strptime(args.get('dateto'), '%Y-%m-%d')
                    queries = queries &  Q(start__lte=t)

            events = BroadcastEvent.objects(queries).skip(offset).limit(limit)

        serializer = BroadcastEventSerializer(events, many=many)
        return Response(serializer.data)

#------------------------------------------------------------------------------------------#

class BroadcastReset(CombaApiView):
    """
    Reset original broadcast event
    @api {post} /broadcast/reset 4. Reset a replaced program
    @apiName reset
    @apiGroup Broadcasts
    @apiDescription     <p>Reset a broadcast event</p>
        <p>Recover the original status of a broadcast event, which had previously been replaced by another program.</p>

    @apiExample {curl} Curl example:
        curl --user user:pass -H "Content-type: application/json" \
        -X POST http://my.combaserver.tld/api/v1.0/broadcast/reset \
        -d '{'orig_id': '55a257e848ea2b25d719803e'}'

    @apiExample {python} Python example:
        import requests
        def resetProgram(orig_id):
            data = {'orig_id': orig_id}
            url = "http://my.combaserver.tld/api/v1.0/broadcast/reset"
            r = requests.post(url, data=data, auth=('user', 'pass'))
            return r.json()

        resetProgram('55a257e848ea2b25d719803e')

    @apiSuccessExample {json} Success-Response:
         HTTP/1.1 200 OK
         {
            'orig_id': '55a257e848ea2b25d719803e',
            'success': 'true',
            'error': 0
        }


    @apiParam {String} orig_id      Original Broadcast event ID.

    """


    def getResponse(self, request, args):

        if args.get('orig_id'):
            result = ModelBroadcastEvent.reset(args.get('orig_id'))
            return Response(result)
        else:
            raise Http404


