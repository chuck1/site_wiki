from django import forms

class SearchForm(forms.Form):
    pattern = forms.CharField(max_length=1024)

class CreateFolderForm(forms.Form):
    relpath = forms.CharField(max_length=1024)

class CreateFileForm(forms.Form):
    relpath = forms.CharField(max_length=1024)

