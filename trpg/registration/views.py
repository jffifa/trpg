from django.urls import reverse_lazy
from registration.backends.simple.views import RegistrationView

from .forms import RegistrationFormOverride


class RegistrationViewOverride(RegistrationView):
    form_class = RegistrationFormOverride

    def get_success_url(self, user):
        return reverse_lazy('hall')
