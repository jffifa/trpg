from django.db import models
from jsonfield import JSONCharField, JSONField

from django.contrib.auth.models import User

from .roll.dice import Coc6eDice
# Create your models here.


class Room(models.Model):
    class Meta:
        verbose_name = '房间'
        verbose_name_plural = '房间'

    def __str__(self):
        return self.name

    ROOM_TYPE_CHOICES = (
        ('coc6e', 'CoC(6e)'),
    )

    name = models.CharField(max_length=32, unique=True, verbose_name='房间名')
    room_type = models.CharField(max_length=32, choices=ROOM_TYPE_CHOICES, verbose_name='房间类型')
    admin = models.ForeignKey(User, on_delete=models.CASCADE)

    @classmethod
    def check_user_admin(cls, room_name, user):
        if cls.objects.filter(name=room_name, admin=user).exists():
            return True
        else:
            return False

    def get_dice_type(self):
        if self.room_type == 'coc6e':
            return Coc6eDice


class Character(models.Model):
    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'

        unique_together = (
            ('room', 'name'),
        )

    def __str__(self):
        return '[%s] %s' % (self.room.name, self.name,)

    CHAR_TYPE_CHOICES = (
        ('admin', 'DM/KP'),
        ('pc', 'PC'),
        ('npc', 'NPC'),
    )

    name = models.CharField(max_length=64, verbose_name='角色名')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name='关联房间')
    char_type = models.CharField(max_length=64, choices=CHAR_TYPE_CHOICES, verbose_name='角色类型')
    details = JSONField(verbose_name='角色细节')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='关联账号')


class Record(models.Model):
    class Meta:
        verbose_name = '记录'
        verbose_name_plural = '记录'

        index_together = (
            ('room', 'id'),
        )

    def __str__(self):
        return '房间<%s>: %s' % (self.room.name, self.pure_text,)

    RECORD_TYPE_CHOICES = (
        ('roll', 'roll'),
        ('roll_req', 'roll_req'),
        ('talk', 'talk'),
        ('sys', 'sys'),
    )

    room = models.ForeignKey(Room)  # redundant field for lookup
    character = models.ForeignKey(Character, on_delete=models.CASCADE, null=True)
    record_type = models.CharField(max_length=32, choices=RECORD_TYPE_CHOICES, verbose_name='记录类型')
    record_time = models.DateTimeField(auto_now_add=True)
    details = JSONField(max_length=65536, verbose_name='记录细节')
    pure_text = models.TextField(max_length=65536, verbose_name='纯文本')

    @classmethod
    def create_roll_record(
            cls, room, character,
            raw_roll_cmd, raw_roll_against,
            dice, roll_hidden=False):

        details = {
            'raw_roll_cmd': raw_roll_cmd,
            'raw_roll_against': raw_roll_against,
            'roll_cmd': dice.roll_cmd,
            'roll_against': dice.roll_against,
            'roll_result': dice.roll_result,
            'roll_result_desc': dice.roll_result_desc,
            'roll_hidden': roll_hidden,
        }
        cls.objects.create(
            room=room, character=character,
            record_type='roll',
            details=details,
            pure_text='ROLL: %s [ %s ]' % (raw_roll_cmd, raw_roll_against))

    def clean_for_room(self, user=None):
        result = {
            'record_id': self.id,
            'room_id': self.room.id,
            'record_type': self.record_type,
            'char': {
                'char_id': self.character.id,
                'char_type': self.character.char_type,
                'char_name': self.character.name,
            },
        }
        if self.record_type == 'talk':
            result['details'] = self.details
        elif self.record_type == 'roll':
            result['details'] = {
                'roll_hidden': self.details['roll_hidden'],
            }
            d = result['details']
            if self.details['roll_hidden'] and user != self.room.admin:
                d['roll_show'] = False
            else:
                d['roll_show'] = True
                d['raw_roll_cmd'] = self.details['raw_roll_cmd']
                d['roll_against'] = self.details['roll_against']
                d['roll_result'] = self.details['roll_result']
                dice_type = self.room.get_dice_type()
                d['roll_result_text'] = dice_type.show_result(self.details['roll_result'])
                d['roll_result_desc'] = self.details['roll_result_desc']

        return result
