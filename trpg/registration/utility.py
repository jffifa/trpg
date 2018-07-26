from django.conf import settings


def decrypt(text):
    half_len = len(text)//2
    return text[half_len:]

