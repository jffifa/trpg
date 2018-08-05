import re
from django import forms
from django.core.exceptions import ObjectDoesNotExist

from .models import Room
from .char_parser.coc6e import Coc6eCharParser


class ImportCharacterForm(forms.Form):
    room_name = forms.CharField(widget=forms.HiddenInput())
    char_type = forms.ChoiceField(
        choices=(
            ('pc', 'PC'),
            ('npc', 'NPC'),
        ),
        label='角色类型')
    character_detail = forms.CharField(
        help_text='进入<a target="_blank" href="%(link)s">%(link)s</a>，找到并复制你的txt卡' % {
            'link': 'https://hina.moe/coc/card-gallery.php'},
        widget=forms.Textarea(attrs={
            'class': 'form-control',
        }),
        label='导入角色')

    line_regex = re.compile(r'^(.+):  (.+)$')

    def clean_character_detail(self):
        detail = self.cleaned_data['character_detail']
        parser = Coc6eCharParser()
        try:
            return parser.parse(detail)
        except ValueError as e:
            raise forms.ValidationError(str(e))

    def clean_room_name(self):
        room_name = self.cleaned_data['room_name']
        try:
            Room.objects.get(name=room_name)
        except ObjectDoesNotExist:
            raise forms.ValidationError('房间不存在')

        return room_name


class ImportCharacterFormPlayer(ImportCharacterForm):
    char_type = forms.CharField(widget=forms.HiddenInput())


class EnterRoomForm(forms.Form):
    room_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-2 mr-sm-2',
            'placeholder': '请输入房间名',
        }),
        label='请输入房间名')

    def clean_room_name(self):
        room_name = self.cleaned_data['room_name']
        try:
            Room.objects.get(name=room_name)
        except ObjectDoesNotExist:
            raise forms.ValidationError('房间不存在')

        return room_name
