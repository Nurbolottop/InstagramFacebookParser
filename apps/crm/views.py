from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.contrib.auth.models import User

# Create your views here.
from django.apps import apps

def crm_index(request):
    # Проверяем, аутентифицирован ли пользователь
    if not request.user.is_authenticated:
        return redirect('crm_login')
    
    # Получаем объект приложения Django
    app_name = 'contacts'  # Замените 'your_app_name' на название вашего приложения
    app_config = apps.get_app_config(app_name)
    
    # Получаем название вашего приложения (verbose_name)
    app_verbose_name = app_config.verbose_name
    
    # Получаем модели, относящиеся к данному приложению
    app_models = app_config.get_models()
    
    # Создаем список для хранения данных о моделях
    models_data = []
    
    # Проходимся по всем моделям и собираем информацию о них
    for model in app_models:
        model_data = {
            'name': model._meta.verbose_name,  # Получаем название модели
            'app_label': app_name,
            'model_name': model._meta.model_name,
        }
        models_data.append(model_data)
    
    # Отображаем шаблон с передачей данных о названии приложения и его моделях
    return render(request, 'crm/dashboard/index.html', locals())


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

from django.contrib.auth.decorators import permission_required
from django.forms.models import modelform_factory
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.apps import apps

from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.apps import apps

@permission_required('add', raise_exception=True)
def crm_add(request, app_label, model_name):
    
    # Проверяем, аутентифицирован ли пользователь
    if not request.user.is_authenticated:
        return redirect('crm_login')
    
    # Получаем объект приложения Django
    app_name = 'contacts'  # Замените 'your_app_name' на название вашего приложения
    app_config = apps.get_app_config(app_name)
    
    # Получаем название вашего приложения (verbose_name)
    app_verbose_name = app_config.verbose_name
    
    # Получаем модели, относящиеся к данному приложению
    app_models = app_config.get_models()
    
    # Создаем список для хранения данных о моделях
    models_data = []
    
    # Проходимся по всем моделям и собираем информацию о них
    for model in app_models:
        model_data = {
            'name': model._meta.verbose_name,  # Получаем название модели
            'app_label': app_name,
            'model_name': model._meta.model_name,
        }
        models_data.append(model_data)
    # Get the model object
    model = apps.get_model(app_label, model_name)
    
    # Check if the user has permission to add objects to this model
    if not model or not request.user.has_perm(f'{app_label}.add_{model_name.lower()}'):
        return HttpResponseForbidden("You do not have permission to add objects to this model.")

    # Get the verbose name of the model
    model_verbose_name = model._meta.verbose_name

    # If the user submitted the form, process the data
    if request.method == 'POST':
        # Create a new instance of the model with the submitted data
        instance = model()
        for field in model._meta.fields:
            if field.name in request.POST:
                setattr(instance, field.name, request.POST[field.name])
        instance.save()
        
        # Redirect the user to a success page
        return redirect('success_page')
    
    # Render the template with the model verbose name
    return render(request, 'crm/add_page/add-product.html', locals())

