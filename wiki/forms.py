import os
from django import forms

import wiki.util

class SearchForm(forms.Form):
    pattern = forms.CharField(max_length=1024)

class CreateFolderForm(forms.Form):
    relpath = forms.CharField(max_length=1024)

class CreateFileForm(forms.Form):
    relpath = forms.CharField(max_length=1024)

    def clean(self):
        cleaned_data = super(CreateFileForm, self).clean()
        relpath = cleaned_data.get("relpath")
	
        h,e = os.path.splitext(relpath)

        try:
            wiki.util.convert_ext_s2b(e)
        except:
            raise forms.ValidationError("invalid source file extension")

