from django import forms

class TaskEditForm(forms.Form):
	name = forms.CharField(label = 'name', max_length = 256)


