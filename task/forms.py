from django import forms

class TaskEditForm(forms.Form):
	name = forms.CharField(label = 'name', max_length = 256)
        priority = forms.IntegerField(label = "priority")

class TaskCreateForm(forms.Form):
	name = forms.CharField(label = 'name', max_length = 256)
        priority = forms.IntegerField(label = "priority")

