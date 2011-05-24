from django.contrib.sites.models        import Site
from django.contrib.auth.models         import User
from django.conf                        import settings
from soundcloud.models                  import *

import urllib, cgi, simplejson, random, unicodedata
import logging
import socket

class ScBackend:
    def authenticate(self, sctoken=None, access_token=None):
        if not access_token:
            args = dict(
                    client_id     = settings.SC_CONSUMER,
                    client_secret = settings.SC_CONSUMER_SECRET,
                    redirect_uri  = settings.SC_CALLBACK_HOST + 'sc_login/',
                    grant_type    = "authorization_code",
                    code          = sctoken,
                    )
           
            resp_raw = urllib.urlopen(
                "https://api.soundcloud.com/oauth2/token",
                urllib.urlencode(args)
                )

            response = simplejson.load(resp_raw)

            logging.debug(response)

            try:
                access_token = response["access_token"]
            except:
                return None

        timeout = 10

        socket.setdefaulttimeout(timeout)

        try:
            me_json = urllib.urlopen("https://api.soundcloud.com/me.json?" + urllib.urlencode(dict(oauth_token=access_token)))
            sc_profile = simplejson.load(me_json)
        except:
            return None
        
        # For debugging
        logging.debug(sc_profile)

        # Check if the user has a username, otherwise generate one
        if not sc_profile.has_key("username"):
            sc_username = self.create_username( sc_profile["full_name"] )
        else:
            sc_username = sc_profile["username"]

        try:
            p = profile.objects.get(soundcloud_id = sc_profile["id"])
            user = p.user
        except:
            user = User()
            user.username = sc_username
            user.first_name = self.strip_accents(sc_profile["full_name"])
            user.save()

        # User profile
        userprofile                   = user.get_profile_sc()
        userprofile.sc_username       = sc_username
        userprofile.soundcloud_id     = sc_profile["id"]
        userprofile.sc_avatar         = sc_profile['avatar_url']
        userprofile.sc_name           = sc_profile['full_name']
        userprofile.access_token_sc   = access_token
        userprofile.save()

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def create_username(self, sc_name):
        ret = u""

        for letter in sc_name:
            letter = self.strip_accents(letter)
            if not ( letter.isalnum() or letter.isspace() ):
                continue
            if letter.isspace():
                ret += "_"
            else:
                ret += letter.lower()

        return ret

    def strip_accents(self, s):
        nkfd_form = unicodedata.normalize('NFKD', unicode(s))
        return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
