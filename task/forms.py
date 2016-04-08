from django import forms

import task.models

class TaskEditForm(forms.Form):
	name    = forms.CharField(label = 'name', max_length = 256)
	notes   = forms.CharField(label = 'notes', widget=forms.Textarea)
        priority = forms.IntegerField(label = "priority")
        bool_wait_for_feedback = forms.BooleanField(label = "wait for feedback", required=False)
        parent = forms.ModelChoiceField(queryset=task.models.Task.objects.all(), empty_label="None", required=False)

class TaskCreateForm(forms.Form):
	name = forms.CharField(label = 'name', max_length = 256)
        priority = forms.IntegerField(label = "priority")
        bool_wait_for_feedback = forms.BooleanField(label = "wait for feedback", required=False)

