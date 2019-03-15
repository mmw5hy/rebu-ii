from django.forms import ModelForm
from .models import Consumer, Producer
from marketplace.models import Item
from django import forms

class ConsumerUserForm(ModelForm):
    """ ModelForm to create Consumer Users """
    class Meta:
        model = Consumer
        fields = ['first_name', 'last_name', 'email', 'password', 'address', 'birthday']
        widgets = {
            'password': forms.PasswordInput(),
        }

class EditConsumerForm(ModelForm):
    """ ModelForm to create Consumer Users """
    class Meta:
        model = Consumer
        fields = ['first_name', 'last_name', 'email', 'birthday', 'address']

class ProducerUserForm(ModelForm):
    """ ModelForm to create Producer Users """
    class Meta:
        model = Producer
        fields = ['first_name', 'last_name', 'email', 'password', 'address', 'store_name', 'birthday', 'image']
        widgets = {
            'password': forms.PasswordInput(),
        }

class EditProducerForm(ModelForm):
    """ ModelForm to create Producer Users """
    class Meta:
        model = Producer
        fields = ['first_name', 'last_name', 'email', 'store_name', 'address', 'birthday']

class NewItemForm(ModelForm):
    """ ModelForm to create Items """
    class Meta:
        model = Item
        fields = ['name', 'ingredients', 'description', 'price', 'image']
