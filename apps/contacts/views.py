from django.shortcuts import render
from django.http import JsonResponse
from apps.contacts.models import InstagramProfile

# Create your views here.
def profile_data(request):
    data = list(InstagramProfile.objects.values())  # Получите данные, которые вам нужны
    return JsonResponse(data, safe=False)