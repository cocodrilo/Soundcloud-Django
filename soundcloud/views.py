from django.shortcuts               import render_to_response
from django.http                    import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers       import reverse
from django.conf                    import settings
from django.contrib.sites.models    import Site
from django.contrib.auth            import login, logout, authenticate
from django.template                import Context, loader
from django.core.cache              import cache
from soundcloud.models              import *

import urllib, cgi, simplejson
		
def authenticate_view(request):
    
    code = request.GET.get("code",None)
    
    args = dict(
            client_id       = settings.SC_CONSUMER,
            redirect_uri    = settings.SC_CALLBACK_HOST + 'sc_login/',
            response_type   = "code",
            )
    
    if code != None:

        user = authenticate(sctoken=code, request=request)

        if user != None:

            redir = request.session.get('after_login_redir','/')
            login(request, user)
            return HttpResponseRedirect(redir)

        else:

            request.session['message'] = "Soundcloud is not responding. Try again later!"
            redir = request.session.get('after_login_redir','/')
            return HttpResponseRedirect(redir)

    else:
        return HttpResponseRedirect("https://soundcloud.com/connect?" + urllib.urlencode(args))


def register(request):
	if request.method == "POST":
		user = User.objects.create_user(request.POST["username"], request.POST["email"])
		return HttpResponseRedirect('/sc_login/')
	else:
		return render_to_response("register.html")
	
def logout_view(request):
	logout(request)
	return HttpResponseRedirect('/')

