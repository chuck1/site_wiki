
from django import forms

class Register(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    email = forms.EmailField(label='email')
    pass0 = forms.CharField(label='password', max_length=100)
    pass1 = forms.CharField(label='confirm password', max_length=100)

    def clean(self):
        cleaned_data = super(Register, self).clean()
        pass0 = cleaned_data.get("pass0")
        pass1 = cleaned_data.get("pass1")

        if not (pass0 == pass1):
            raise forms.ValidationError("passwords did not match")

