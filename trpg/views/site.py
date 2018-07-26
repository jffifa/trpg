from django.views.generic.edit import FormView
from django.urls import reverse
from ..forms import EnterRoomForm


class HallView(FormView):
    template_name = "trpg/hall.html"
    form_class = EnterRoomForm
    room_name = ''

    def get_success_url(self):
        return reverse('room', kwargs={'room_name': self.room_name})

    def form_valid(self, form):
        self.room_name = form.cleaned_data['room_name']
        return super(HallView, self).form_valid(form)
