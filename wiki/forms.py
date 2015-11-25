from django import forms

class SearchForm(forms.Form):
    pattern = forms.CharField(max_length=1024)


