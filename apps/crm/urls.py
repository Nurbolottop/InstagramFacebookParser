from django.urls import path

from apps.crm import views

urlpatterns = [
    path('', views.crm_index, name="crm_index"),
    path('login/', views.crm_login, name="crm_login"),
    path('add/<str:app_label>/<str:model_name>/', views.crm_add, name='add_model'),
    path('detail/<str:app_label>/<str:model_name>/', views.crm_detail, name='crm_detail'),
]