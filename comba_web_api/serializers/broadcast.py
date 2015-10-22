from comba_web.models import *
from comba_web_api.serializers import CombaModelSerializer
from rest_framework import serializers
class BroadcastEventSerializer(CombaModelSerializer):
    ressource_ready =  serializers.SerializerMethodField('fileexists')

    class Meta:
        model = BroadcastEvent
        fields = ('id',
                  'identifier',
                  'replay_of',
                  'end',
                  'description',
                  'title',
                  'state',
                  'station_id',
                  'replay_of_datetime',
                  'start',
                  'programme_id',
                  'reccurrence_id',
                  'rerun',
                  'duration',
                  'station_name',
                  'ressource_ready',
                  'subject',
                )

    def fileexists(self, obj):
        return obj.fileExists()


