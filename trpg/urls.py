from django.conf.urls import include, url
from django.views.generic.base import TemplateView

from . import views
from .registration import views as registration_views

urlpatterns = [
    # register and auth
    url(r'^register/$',
        registration_views.RegistrationViewOverride.as_view(),
        name='registration_register'),
    url(r'^register/closed/$',
        TemplateView.as_view(template_name='registration/registration_closed.html'),
        name='registration_disallowed'),
    url(r'^login/$',
        views.LoginView.as_view(),
        name='login'),
    url(r'^logout/$',
        views.LogoutView.as_view(),
        name='logout'),
    # rooms
    url(r'^room/(?P<room_name>\w+)/character_import/$',
        views.ImportCharacterView.as_view(),
        name='character_import'),
    url(r'^room/(?P<room_name>\w+)/$',
        views.RoomView.as_view(),
        name='room'),
    url(r'^room/(?P<room_name>\w+)/pull/$',
        views.PullRecordsView.as_view(),
        name='pull_msg'),
    url('^room/(?P<room_name>\w+)/send/$',
        views.SendMsgView.as_view(),
        name='send_msg'),
    url('^room/(?P<room_name>\w+)/mode_change/$',
        views.RoomModeMsgView.as_view(),
        name='room_mode_change'),
    url(r'^room/(?P<room_name>\w+)/roll/$',
        views.RollView.as_view(),
        name='roll'),

    # site
    url(r'^$',
        views.HallView.as_view(),
        name='hall'),
]
