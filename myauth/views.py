from django.shortcuts import render
#from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.conf import settings

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
                print 'register failure',e
                pass
            else:
                print 'register success'

                return HttpResponse('A confirmation link has been sent to your email.'
                        '<br><a href="/accounts/login/?next={}">'
                        'return to login</a>'.format(nxt))
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

def address_next(request):
    try:
        n = request.GET['next']
    except:
        n = '/'

def logout(request):
    django.contrib.auth.logout(request)
    
    HttpResponseRedirect('/accounts/login?next={}'.format(address_next(request)))



