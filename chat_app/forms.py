from django import forms

class MessageForm(forms.Form):
    message = forms.CharField(
        max_length= 100,
        required= True,
        widget= forms.TextInput(attrs= {'placeholder': 'Type your message'})
    )