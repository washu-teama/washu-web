from django import forms


class SignupForm(forms.Form):
    uid = forms.CharField(max_length=10)
    pwd = forms.CharField(max_length=30)
    repwd = forms.CharField(max_length=30)
