from django.shortcuts import render
#from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.conf import settings
from django.core.urlresolvers import reverse
import django.contrib.auth
import django.core.urlresolvers

# Create your views here.

from .forms import Register
from .models import MyUser, Confirmation

def confirmation(request, code):
    #dt = timezone.now()
    
    c = Confirmation.objects.get(code=code)
    print c
    
    c.user.is_active = True
    c.user.save()

    return HttpResponse('confirmation success')

def register(request):

    message = None

    if request.method == 'POST':
        nxt = request.POST['next']

        form = Register(request.POST)
    
        if form.is_valid():
            try:
                user = MyUser.objects.create_user(
                    request,
                    form.cleaned_data['email'],
                    form.cleaned_data['pass0'],)
            except Exception as e:
                message = "register failure {}".format(repr(e))
            else:
                print 'register success'

                href = reverse("accounts_login")+"?next={}".format(nxt)
                return HttpResponse('A confirmation link has been sent to your email.'
                        '<br><a href="{}">'
                        'return to login</a>'.format(href))
        else:
            message = "register failure form invalid"
    else:
        print 'register start'
        form = Register()
        nxt = request.GET['next']

    c = {
            'message': message,
                'form': form,
                'next': nxt}
    return render(request, 'myauth/register.html', c)

def address_next(request):
    try:
        return request.GET['next']
    except:
        return django.core.urlresolvers.get_script_prefix()

def logout(request):
    django.contrib.auth.logout(request)
    
    n = address_next(request)
    n = django.core.urlresolvers.get_script_prefix()

    href = reverse("accounts_login") + "?next={}".format(n)
    print "redirect to",href
    return HttpResponseRedirect(href)



