from django.db                  import models
from django.contrib.auth.models import User
from datetime                   import datetime
from django.db.models.signals   import post_save

import time
import re
import logging

class profile_sc(models.Model):
    user              = models.ForeignKey(User, unique=True)
    soundcloud_id     = models.IntegerField(unique=True, null=True)
    sc_avatar         = models.URLField(blank=True, null=True)
    access_token_sc   = models.CharField(max_length=255, blank=True, null=True, editable=False)
    sc_username       = models.CharField(max_length=75)
    sc_name           = models.CharField(max_length=255)

    def __str__(self):
        return "%s's profile" % self.user

## METHOD 1: this method is for automatically creating the profile
def create_user_profile(sender, instance, created,**kwargs):
    if created:
        prof, created = profile_sc.objects.get_or_create(user=instance)

## ... This is the trigger for the previous one
post_save.connect(create_user_profile, sender=User)

