import os, shutil
from comba_lib.reporting.statestore import RedisStateStore
from comba_lib.database.broadcasts import *
from comba_lib.utils.audio import CombaAudiotools
from werkzeug import secure_filename
from django.utils.translation import ugettext as _
from bson.objectid import ObjectId

"""
Model - general information about system and component states
"""


class ModelSysInfo(object):
    # ------------------------------------------------------------------------------------------#
    def __init__(self):
        self.statestore = RedisStateStore()

    #------------------------------------------------------------------------------------------#
    def getFreeSpace(self):
        """
        get free disk space human readable
        """
        st = os.statvfs('/')
        # bytes = (st.f_blocks - st.f_bfree) * st.f_frsize
        bytes = st.f_bsize * st.f_bavail
        abbrevs = (
            (1 << 50L, 'PB'),
            (1 << 40L, 'TB'),
            (1 << 30L, 'GB'),
            (1 << 20L, 'MB'),
            (1 << 10L, 'kB'),
            (1, 'bytes')
        )
        if bytes == 1:
            return '1 byte'
        for factor, suffix in abbrevs:
            if bytes >= factor:
                break
        return '%.*f %s' % (2, bytes / factor, suffix)

    #------------------------------------------------------------------------------------------#
    def getLoad(self):
        """
        OS load average
        """
        load = os.getloadavg()
        return "{0:.2f}".format(load[0]) + ", " + "{0:.2f}".format(load[1]) + ", " + "{0:.2f}".format(load[2])

    #------------------------------------------------------------------------------------------#
    def getAliveState(self, component):
        """
        Is the component alive?
        """
        return self.statestore.getAliveState(component)

    #------------------------------------------------------------------------------------------#
    def getState(self, component, name):
        """
        Return a state of component
        """
        return self.statestore.getState(name, component)

    #------------------------------------------------------------------------------------------#
    def getEvents(self, component, name):
        """
        Return last events of component
        """
        return self.statestore.getEvents(name, component)

    #------------------------------------------------------------------------------------------#
    def getNextEvent(self, component, name):
        """
        Components announced event
        """
        return self.statestore.getNextEvent(name, component)

    #------------------------------------------------------------------------------------------#
    def getDumpInfo(self):
        """
        Recorders dumping progress
        """
        file = self.getState('record', 'dumpfile')
        info = {'file': file, 'size': 0, 'recorded': 0}
        if file and os.path.exists(file):
            result = os.stat(file)
            if result:
                info['size'] = result.st_size
                info['recorded'] = int(info['size']) / 3174777
        return info

    #------------------------------------------------------------------------------------------#
    def getPlayerInfo(self):
        """
        Info from player about current playing file
        """
        file = self.getState('playd', 'playlistcurrent')
        info = {'file': file, 'size': 0, 'recorded': 0, 'complete': False}
        if file and os.path.exists(file):
            result = os.stat(file)
            if result:
                info['size'] = result.st_size
                info['recorded'] = int(info['size']) / 3174777
                info['complete'] = True if info['recorded'] == 100 else False

        return info

    #------------------------------------------------------------------------------------------#
    def getNextTrackstart(self):
        """
        next track from playlist
        """
        event = self.getNextEvent('player', 'playtrack')
        return event if event else False

    #------------------------------------------------------------------------------------------#
    def getNextPlayliststart(self):
        """
        Next start of playlist
        """
        eventQueue = self.statestore.getEventQueue('playliststart', 'player')
        if not eventQueue or not isinstance(eventQueue, list):
            return False
        else:
            item = eventQueue[0]
            if not item.has_key('date') or not item.has_key('time'):
                return False
            return item['date'] + ' ' + item['time']

    #------------------------------------------------------------------------------------------#
    def getNextRecordstart(self):
        """
        Next start of recorder
        """
        event = self.getNextEvent('recorder', 'dumpstart')
        return event if event else False

    #------------------------------------------------------------------------------------------#
    def getComponentStates(self):
        """
        Alive states of components
        """
        componentStates = []
        componentStates.append({'title': 'Scheduler', 'name': 'scheduler', 'state': self.getAliveState('scheduler')})
        componentStates.append({'title': 'Controller', 'name': 'controller', 'state': self.getAliveState('controller')})
        componentStates.append({'title': 'Monitor', 'name': 'monitor', 'state': self.getAliveState('monitor')})
        componentStates.append({'title': 'Archiver', 'name': 'archive', 'state': self.getAliveState('archive')})
        componentStates.append({'title': 'Player', 'name': 'playd', 'state': self.getAliveState('playd')})
        componentStates.append({'title': 'Recorder', 'name': 'recorder', 'state': self.getAliveState('record')})
        componentStates.append(
            {'title': 'Preprod Recorder', 'name': 'recorder', 'state': self.getAliveState('altrecord')})
        return componentStates


"""
Model - detailled information about component messages
"""


class ModelEvents(object):
    # ------------------------------------------------------------------------------------------#
    def __init__(self):
        """
        Constructor
        """
        self.statestore = RedisStateStore()

    def getEvents(self, component):
        """
        Get entries from a components events channel
        """
        self.statestore.setChannel(component)
        self.statestore.daily = True
        entries = self.statestore.getEntries()
        self.statestore.daily = False
        return entries


"""
Model - handles events
"""


class ModelBroadcastEvent(object):
    # ------------------------------------------------------------------------------------------#
    @staticmethod
    def replace(orig_id, replace_id):
        result = {'success': False, 'error': '', 'orig_id': orig_id, 'replace_id': replace_id}
        current = BroadcastEvent.objects.get(id=orig_id)
        replace = BroadcastEvent.objects.get(id=replace_id)
        if replace:
            current.overwrite_event = replace
            current.save()
            result['success'] = True
        return result

        #------------------------------------------------------------------------------------------#

    @staticmethod
    def reset(orig_id):
        result = {"success": "false", "error": "0", "orig_id": orig_id}

        reset = BroadcastEvent.objects.get(id=orig_id)
        if reset:
            reset.overwrite_event = None
            reset.save()
            result['success'] = 'true'
        return result


"""
Model - handles preproduction
"""


class ModelBroadcastEventOverride(object):
    # ------------------------------------------------------------------------------------------#
    @staticmethod
    def remove(preprod_id):
        """
        Remove a file from pre-production file list
        :param preprod_id:
        :return:dict
        """
        result = {'error': 0, 'location': '', 'preprod_id': preprod_id}
        override = BroadcastEventOverride.objects.get(id=preprod_id)
        result['location'] = override.location

        if override:
            filepath = str(override.location).replace('file://', '')
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    result['error'] = 2
            override.delete()
        else:
            result['error'] = 1

        return result

    #------------------------------------------------------------------------------------------#
    @staticmethod
    def reorder(preprod_id, dir):
        """

        :param preprod_id: db id
        :param dir: direction - up|down
        :return:dict
        """
        result = {'error': '', 'event_id': '', 'position': 0}
        change = BroadcastEventOverride.objects.get(id=preprod_id)
        change_ordering = change.ordering
        result['event_id'] = change.broadcast_event.id

        if str(dir) == "down":
            obj = BroadcastEventOverride.objects(broadcast_event=change.broadcast_event,
                                                 ordering=(change_ordering + 1)).first()
            if (obj):
                obj.modify(dec__ordering=1)
                change.ordering = change_ordering + 1

        else:
            obj = BroadcastEventOverride.objects(broadcast_event=change.broadcast_event,
                                                 ordering=(change_ordering - 1)).first()

            if (obj):
                obj.modify(inc__ordering=1)
                change.ordering = change_ordering - 1

        result['position'] = change.ordering
        change.save()
        return result

    #------------------------------------------------------------------------------------------#
    @staticmethod
    def updateordering(preprod_id, position):
        """

        :param preprod_id: db id
        :param position: new position
        :return:dict
        """
        result = {'error': '', 'event_id': '', 'position': 0}
        change = BroadcastEventOverride.objects.get(id=preprod_id)
        change_ordering = change.ordering

        result['event_id'] = change.broadcast_event.id
        result['track_id'] = change.id
        objects = BroadcastEventOverride.objects(broadcast_event=change.broadcast_event)
        position = int(position)


        if ((len(objects) - 1) < position):
            position = len(objects) - 1

        counter = 0
        newpos = 0
        for obj in objects:
            if counter == position:
                change.ordering = position
                change.save()
                newpos = newpos + 1
            if obj.id != change.id:
                obj.ordering = newpos
                obj.save()
                newpos = newpos + 1

            counter = counter + 1

        result['position'] = change.ordering

        return result


   #------------------------------------------------------------------------------------------#
    @staticmethod
    def add(event, basefolder, filename, file):
        """

        :param event: parent event
        :param basefolder: basefolder to store files
        :param file: file object from upload
        :return:
        """
        # initiate result dict
        result = {'error': '', 'preprod_id': '', 'location':''}
        audiotools = CombaAudiotools()

        # initiate override object
        override = BroadcastEventOverride()
        override.broadcast_event = event
        override.start = event.start


        # create folders

        parentfolder = os.path.abspath(os.path.join(basefolder, os.path.pardir))

        uid = os.stat(parentfolder).st_uid
        gid = os.stat(parentfolder).st_gid

        if not os.path.exists(basefolder):
            os.mkdir(basefolder)
            try:
                os.chown(basefolder, uid, gid)
            except:
                pass


        folder = os.path.join(basefolder, override.start.strftime('%Y-%m-%d-%H-%M'))
        if not os.path.exists(folder):
            os.mkdir(folder)
            try:
                os.chown(folder, uid, gid)
            except:
                pass

        # make secure filename, create path and store file
        filename = secure_filename(filename)
        file_path = os.path.join(folder, filename)
        inc = 1
        (base, ext) = os.path.splitext(file_path)
        while os.path.exists(file_path):
            file_path = base + "-" + str(inc) + ext
            inc = inc + 1
        try:
            shutil.move(file, file_path)
        except:
            result['error'] = _("Could not store file to %(location)", location=file_path)

        # check mime type
        mimetype = audiotools.audio_mime_type(file_path)
        if mimetype:
            if mimetype.find("wav") > -1:
                info = audiotools.get_wav_info(file_path)
            elif (mimetype.find("mpeg")) > -1:
                info = audiotools.get_mp3_info(file_path)
            elif (mimetype.find("ogg")) > -1:
                info = audiotools.get_ogg_info(file_path)
            else:
                try:
                    os.remove(file_path)
                except:
                    pass
                result['error'] = _("Wrong Filetype")

            # store data
            override.mimetype = mimetype
            if info.has_key('bitrate'):
                override.bitrate = info['bitrate']
            if info.has_key('length'):
                override.length = info['length']
            if info.has_key('channels'):
                override.channels = info['channels']
            override.identifier = event.identifier
            override.ordering = override.nextOrdering()
            override.location = 'file://' + file_path
            override.save()
            result['preprod_id'] = override.id
            result['ordering'] = override.ordering
            result['location'] = override.location
        else:
            result['error'] = _("Wrong Filetype")

        return result
