from django.urls import path

from apps.crm import views

urlpatterns = [
    path('', views.crm_index, name="crm_index"),
    path('login/', views.crm_login, name="crm_login"),
]
