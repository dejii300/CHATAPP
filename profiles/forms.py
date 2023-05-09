from django import forms
from .models import *
from django.forms import ModelForm


class ChatMessageForm(ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={"class":"forms", "rows":3, "placeholder": "Type message here"}))
    class Meta:
        model = ChatMessage
        fields = ["body",]

class userForm(ModelForm):
    class Meta:
        model = Profile
        
        fields = ['first_name', 'last_name','email', 'pic', 'country']