from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from collections import OrderedDict

from .base import JSONView
from ..roll.dice import Coc6eDice
from ..models import Character, Room, Record


@method_decorator(login_required, name='dispatch')
class RoomView(TemplateView):
    template_name = 'trpg/room.html'

    def get_context_data(self, **kwargs):
        room_name = kwargs['room_name']
        room = Room.objects.get(name=room_name)

        is_admin = False
        characters = Character.objects.filter(room=room)
        if room.admin == self.request.user:
            is_admin = True

        first_controlable_char_id = None
        for character in characters:
            if character.user == self.request.user:
                character.control_by_user = True
                if first_controlable_char_id is None:
                    first_controlable_char_id = character.id
            else:
                character.control_by_user = False
            if character.char_type != 'admin':
                character.details = self.process_character_detail(character.details)

        return {
            'is_admin': is_admin,
            'room': room,
            'room_mode': {
                'silent': bool(room.mode_flag & Room.ModeFlag.SILENT),
            },
            'characters': characters,
            'first_controlable_char_id': first_controlable_char_id,
        }

    @classmethod
    def process_character_detail(cls, details):
        for k, v in details.items():
            if type(v) is dict:
                # make it as ordered dict
                details[k] = OrderedDict(sorted(v.items(), key=lambda x: x[1]['show_order']))

        return details


@method_decorator(login_required, name='dispatch')
class PullRecordsView(JSONView):
    MAX_PULL_COUNT = 100

    def get_context_data(self, **kwargs):
        room = Room.objects.get(name=kwargs['room_name'])
        last_record_id = self.request.GET.get(
            'last_record_id', self.request.POST.get('last_record_id'))

        records = Record.objects.order_by('-id').filter(room=room)
        if last_record_id != '':
            records = records.filter(pk__gt=int(last_record_id))
        records = list(records[:self.MAX_PULL_COUNT])
        records.reverse()
        return {
            'records': records,
        }

    def get_json_object(self, context):
        record_list = []
        for record in context['records']:
            record_list.append(record.clean_for_room(user=self.request.user))
        return {
            'succ': True,
            'records': record_list,
        }


@method_decorator(login_required, name='dispatch')
class SendMsgView(JSONView):
    http_method_names = ['post']

    def get_context_data(self, **kwargs):
        msg = self.request.POST.get('msg')
        if not msg:
            return {'succ': True}
        char_id = int(self.request.POST.get('cur_char_id'))
        room_name = kwargs.get('room_name')

        # TODO: permission check
        room = Room.objects.get(name=room_name)
        char = Character.objects.get(room=room, id=char_id)

        if room.mode_flag & Room.ModeFlag.SILENT:
            if char.char_type != 'admin':
                return {'succ': False, 'msg': 'room under silent mode'}

        record_detail = {'message': msg}
        Record.objects.create(
            room=room,
            character=char,
            record_type='talk',
            details=record_detail,
            pure_text=msg)

        return {'succ': True}


@method_decorator(login_required, name='dispatch')
class RoomModeMsgView(JSONView):
    http_method_names = ['post']

    def get_context_data(self, **kwargs):
        mode_name = self.request.POST.get('mode_name')
        mode_value = self.request.POST.get('mode_value')
        if not mode_name or not mode_value:
            return {'succ': False, 'msg': 'invalid params'}
        room = Room.objects.get(name=kwargs.get('room_name'))
        if room.admin != self.request.user:
            return {'succ': False, 'msg': 'permission error'}
        char = Character.get_room_admin_character(room=room)

        mode_value = (mode_value == '1')
        if mode_name == 'silent':
            mode_flag = Room.ModeFlag.SILENT
            if mode_value:
                pure_text = '%s 开启了叙述模式，请聆听' % char.name
            else:
                pure_text = '%s 关闭了叙述模式，所有人正常发言' % char.name
        else:
            return {'succ': False, 'msg': 'unknown mode name'}

        if mode_value:
            room.mode_flag |= mode_flag
        else:
            room.mode_flag &= (~mode_flag)
        room.save()

        details = {
            'type': 'mode_change',
            'mode_flag': room.mode_flag,
        }
        Record.objects.create(
            room=room,
            character=char,
            record_type='sys',
            details=details,
            pure_text=pure_text
        )
        return {'succ': True}


@method_decorator(login_required, name='dispatch')
class RollView(JSONView):
    http_method_names = ['post']

    def get_context_data(self, **kwargs):
        roll_cmd = self.request.POST.get('roll_cmd', '')
        roll_against = self.request.POST.get('roll_against', '')
        roll_hidden = self.request.POST.get('roll_hidden', '')
        char_id = self.request.POST.get('cur_char_id')
        room_name = kwargs.get('room_name')

        if roll_hidden == 'true':
            roll_hidden = True
        else:
            roll_hidden = False

        # TODO: permission check
        room = Room.objects.get(name=room_name)
        if roll_hidden:
            # force character to admin
            char = Character.objects.get(room=room, char_type='admin')
        else:
            char = Character.objects.get(room=room, id=char_id)
        if (room.mode_flag & Room.ModeFlag.SILENT) and char.char_type != 'admin':
            return {'succ': False, 'msg': 'room under silent mode'}

        def get_char_details(char_name):
            try:
                char = Character.objects.get(room=room, name=char_name)
                if char.char_type == 'admin':
                    return None
                else:
                    return char.details
            except ObjectDoesNotExist:
                return None

        dice = Coc6eDice(get_char_details=get_char_details)
        dice.roll(roll_cmd=roll_cmd, roll_against=roll_against, char_name=char.name)
        Record.create_roll_record(
            room=room, character=char,
            raw_roll_cmd=roll_cmd, raw_roll_against=roll_against,
            dice=dice, roll_hidden=roll_hidden)
        return {'succ': True}
