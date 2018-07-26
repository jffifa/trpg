from django import forms
from registration.forms import RegistrationForm


class RegistrationFormOverride(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        fields = RegistrationForm.Meta.fields + [
            'first_name',
        ]

    first_name = forms.CharField(
        label='昵称',
        required=False)

    def __init__(self, *args, **kwargs):
        super(RegistrationFormOverride, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
