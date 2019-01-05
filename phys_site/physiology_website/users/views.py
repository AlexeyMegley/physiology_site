from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User

from .forms import StudentCreationForm, LoginForm


def signup(request):
    if request.method == 'POST':
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            new_student = form.save()
            login(request, new_student.user)
            return HttpResponseRedirect('/home')
    else:
        form = StudentCreationForm()
    return render(request, 'users/register.html', {'form': form})


def log_in(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = User.objects.get(email=email)
            authenticate(username=user.username, password=password)
            login(request, user)
            return HttpResponseRedirect('/home')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def log_out(request):
    logout(request)
    return HttpResponseRedirect('/')

@login_required
def home(request):
    return render(request, 'users/pers_info.html')
