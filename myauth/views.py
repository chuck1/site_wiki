from django.shortcuts import render
#from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.conf import settings

# Create your views here.

from .forms import Register
from .models import MyUser as User

def confirmation(request, code):
    dt = timezone.now()

def register(request):
    if request.method == 'POST':
        nxt = request.POST['next']

        form = Register(request.POST)
    
        if form.is_valid():
            try:
                user = User.objects.create_user(
                    #form.cleaned_data['username'],
                    form.cleaned_data['email'],
                    form.cleaned_data['pass0'],)
                user.is_active = False
                user.save()
            except Exception as e:
                print 'register failure',e
                pass
            else:
                print 'register success'

                return HttpResponse('you should receive a confirmation email')
                #return HttpResponseRedirect('/accounts/login?next={}'.format(nxt))
                #return HttpResponseRedirect(nxt)
        else:
            print 'register failure'
    else:
        print 'register start'
        form = Register()
        nxt = request.GET['next']

    c = {
                'form': form,
                'next': nxt,
                }
    return render(request, 'myauth/register.html', c)


