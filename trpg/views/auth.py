from .base import JSONView
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from ..registration.utility import decrypt as password_decrypt


class LoginView(JSONView):
    def get_context_data(self, **kwargs):
        username = self.request.POST['username']
        password = self.request.POST['password']
        password = password_decrypt(password)
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)
            return {'succ': True}
        else:
            return {'succ': False}


class LogoutView(JSONView):
    def get_context_data(self, **kwargs):
        logout(self.request)
        return {
            'succ': True,
            'redirect': reverse('hall'),
        }
