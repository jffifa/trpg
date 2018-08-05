from django import forms
from django.core.exceptions import ObjectDoesNotExist

from ..models import Room


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
