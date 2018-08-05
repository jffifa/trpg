from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView
from django.urls import reverse
from ..models import Character, Room
from ..forms import ImportCharacterForm, ImportCharacterFormPlayer


@method_decorator(login_required, name='dispatch')
class ImportCharacterView(FormView):
    template_name = 'trpg/import_character.html'
    form_class = ImportCharacterFormPlayer

    def get_form_class(self):
        if Room.objects.filter(
                name=self.kwargs['room_name'],
                admin=self.request.user).exists():
            return ImportCharacterForm
        else:
            return ImportCharacterFormPlayer

    def get_initial(self):
        initial = super(ImportCharacterView, self).get_initial()
        initial['room_name'] = self.kwargs['room_name']
        initial['char_type'] = 'pc'
        return initial

    def get_success_url(self):
        room_name = self.kwargs['room_name']
        return reverse('room', kwargs={'room_name':room_name})

    def form_valid(self, form):
        room = Room.objects.get(name=form.cleaned_data['room_name'])
        character_data = {
            'details': form.cleaned_data['character_detail'],
        }
        Character.objects.update_or_create(
            defaults=character_data,
            room=room,
            name=form.cleaned_data['character_detail']['name'],
            char_type=form.cleaned_data['char_type'],
            user=self.request.user)
        return super(ImportCharacterView, self).form_valid(form)
