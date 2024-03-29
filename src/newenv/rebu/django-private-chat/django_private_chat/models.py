# -*- coding: utf-8 -*-
""" This file details all Chat models
"""

from django.db import models
from model_utils.models import TimeStampedModel, SoftDeletableModel
from django.conf import settings
from django.template.defaultfilters import date as dj_date
from django.utils.translation import ugettext as _
from django.utils.timezone import localtime


class Dialog(TimeStampedModel):
    """ The Dialog is a class that models any dialog between users

    Attributes:
        owner: User that owns the dialog 
        opponent: User that owner is in a dialog with 
    """
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Dialog owner"), related_name="selfDialogs",
                              on_delete=models.CASCADE)
    opponent = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Dialog opponent"), on_delete=models.CASCADE)

    def __str__(self):
        return _("Chat with ") + self.opponent.username


class Message(TimeStampedModel, SoftDeletableModel):
    """ The Message is a class that models any message between users

    Attributes:
        dialog: Dialog that message belongs to 
        sender: User that sends the message
        text: Text that is sent in message
        read: Bool that dictates whether the oppponent has read sender's message
        all_objects: renames manager for message model class 
    """
    dialog = models.ForeignKey(Dialog, verbose_name=_("Dialog"), related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Author"), related_name="messages",
                               on_delete=models.CASCADE)
    text = models.TextField(verbose_name=_("Message text"))
    read = models.BooleanField(verbose_name=_("Read"), default=False)
    all_objects = models.Manager()

    def get_formatted_create_datetime(self):
        return dj_date(localtime(self.created), settings.DATETIME_FORMAT)

    def __str__(self):
        return self.sender.username + "(" + self.get_formatted_create_datetime() + ") - '" + self.text + "'"
