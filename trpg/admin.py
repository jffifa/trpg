from django.contrib import admin

# Register your models here.
from .models import Room, Character, Record

admin.site.register(Room)
admin.site.register(Character)
admin.site.register(Record)
