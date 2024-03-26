from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.contrib import admin
from django.contrib.auth.models import User

# Create your views here.
def crm_index(request):
    if not request.user.is_authenticated:
        return redirect('crm_login')
    return render(request, 'crm/dashboard/index.html')


def crm_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('crm_index')
        else:
            error_message = "Неправильное имя пользователя или пароль."
            return render(request, 'crm/user/login.html', {'error_message': error_message})
    return render(request, 'crm/user/login.html')
