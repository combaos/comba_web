__author__ = 'michel'
# -*- coding: utf-8 -*-
from . import CombaApiView
from rest_framework.response import Response
from django.http import Http404
from comba_web.models import ModelBroadcastEvent


#------------------------------------------------------------------------------------------#

class BroadcastOverride(CombaApiView):

    """
    Replace broadcast event by another one
    @api {post} /broadcasts/overwrite 3. Replace a broadcast event by another program
    @apiName overwrite
    @apiGroup Broadcasts
    @apiDescription     <p>Replace broadcast event by another</p>
        <p>You can replace a broadcast event  by another. This will be played instead of the original.</p>
        <p>The original event won't be lost. You can reset it by using /broadcasts/reset (see below)</p>

    @apiExample {curl} Curl example:
        curl --user user:pass -H "Content-type: application/json" \
        -X POST http://my.combaserver.tld/api/v1.0/broadcast/owerride \
        -d '{'orig_id': '55a257e848ea2b25d719803e', 'replace_id' : '55a257e848ea2b25d719803b'}'

    @apiExample {python} Python example:
        import requests
        def replaceProgramme(orig_id, replace_id):
            data = {'orig_id': orig_id, 'replace_id' : replace_id}
            url = "http://my.combaserver.tld/api/v1.0/broadcast/owerride"
            r = requests.post(url, data=data, auth=('user', 'pass'))
            return r.json()

        replaceProgramme('55a257e848ea2b25d719803e', '55a257e848ea2b25d719803b')


    @apiSuccessExample {json} Success-Response:
         HTTP/1.1 200 OK
         {
            'orig_id': '55a257e848ea2b25d719803e',
            'replace_id': '55a257e848ea2b25d719803b',
            'success': 'true',
            'error': 0
        }

    @apiParam {String} orig_id      Original Broadcast event ID.
    @apiParam {String} replace_id   Broadcast event replacement ID.
    """


    def getResponse(self, request, args):
        """
        Get the Post
        """
        if args.get('orig_id') and args.get('replace_id'):
            result = ModelBroadcastEvent.replace(args.get('orig_id'), args.get('replace_id'))
            return Response(result)
        else:
            raise Http404

