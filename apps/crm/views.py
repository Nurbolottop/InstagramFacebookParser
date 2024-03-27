from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseForbidden, Http404
from django.contrib import messages
from django.apps import apps
from django import forms

# Create your views here.
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
    print(app_models)
    
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

    # Получаем название модели
    model_verbose_name = model._meta.verbose_name

    # Получаем объект приложения Django
    app_name = 'contacts'  # Замените 'your_app_name' на название вашего приложения
    app_config = apps.get_app_config(app_name)
    
    # Получаем название вашего приложения (verbose_name)
    app_verbose_name = app_config.verbose_name
    
    # Получаем модели, относящиеся к данному приложению
    app_models = app_config.get_models()
    print(app_models)
    
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

    # Создаем динамическую форму на основе полей модели
    class DynamicModelForm(forms.ModelForm):
        class Meta:
            dynamic_model = apps.get_model(app_label, model_name)
            model = dynamic_model
            fields = '__all__'

    model = apps.get_model(app_label, model_name)

    # Если форма была отправлена, обрабатываем данные
    if request.method == 'POST':
        form = DynamicModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            print(models_data)
            return redirect('crm_detail', model._meta.app_label, model._meta.model_name)
    else:
        form = DynamicModelForm()
    
    # Render the template with the model verbose name
    return render(request, 'crm/add_page/add-product.html', locals())

@permission_required('view', raise_exception=True)
def crm_detail(request, app_label, model_name):
    if not request.user.is_authenticated:
        return redirect('crm_login')

    # Получаем класс модели
    model = apps.get_model(app_label, model_name)
    if model is None:
        raise Http404(f"The model {model_name} in the app {app_label} does not exist.")

    # Проверяем, есть ли у пользователя разрешение на просмотр объектов этой модели
    if not request.user.has_perm(f'{app_label}.view_{model_name.lower()}'):
        return HttpResponseForbidden("You do not have permission to view objects of this model.")

    # Получаем метаданные поля модели
     # Получаем метаданные поля модели, учитывая только те, у которых есть verbose_name
    fields_info = [{
        'name': field.name,
        'verbose_name': field.verbose_name,
        'type': field.get_internal_type()
    } for field in model._meta.fields if getattr(field, 'verbose_name', None)]

    # Фильтруем поля, чтобы в список попали только необходимые
    # Это могут быть поля, которые определены в вашей модели и имеют verbose_name
    fields_info = [field for field in fields_info if field['verbose_name'] != field['name']]
    
    if not fields_info:
        messages.error(request, "There are no fields with verbose_name set for this model.")
        return redirect('some_default_route')

    # Создаем список для хранения данных о моделях
    models_data = [{'name': m._meta.verbose_name, 'app_label': app_label, 'model_name': m._meta.model_name} for m in apps.get_app_config(app_label).get_models()]

    # Получаем все объекты данной модели
    model_objects = model.objects.all()

    # Получаем объект приложения Django
    app_name = 'contacts'  # Замените 'your_app_name' на название вашего приложения
    app_config = apps.get_app_config(app_name)
    
    # Получаем название вашего приложения (verbose_name)
    app_verbose_name = app_config.verbose_name
    
    # Получаем модели, относящиеся к данному приложению
    app_models = app_config.get_models()
    print(app_models)
    
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

    # Рендерим шаблон с данными объекта и информацией о полях
    return render(request, 'crm/detail_page/detail_product.html', locals())