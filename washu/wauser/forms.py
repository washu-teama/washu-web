from django import forms

from .models import User
from django.core.exceptions import ObjectDoesNotExist

class SignupForm(forms.Form):
    uid = forms.CharField(max_length=20)
    pwd = forms.CharField(max_length=30)
    repwd = forms.CharField(max_length=30)

    def clean(self):
        form_data = self.cleaned_data
        if form_data['pwd'] != form_data['repwd']:
            self._errors["pwd"] = ["Password do not match"] # Will raise a error message
            del form_data['pwd']
        try:
            User.objects.get_by_natural_key(username=form_data["uid"])
            self._errors["uid"] = ["user already exist"]
        except ObjectDoesNotExist:
            pass

        return form_data
