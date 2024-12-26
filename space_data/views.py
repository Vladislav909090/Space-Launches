from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .models import SpaceCompany, LaunchPad, RocketFamily, RocketConfiguration, LaunchMission, LaunchVehicle, Vehicle, VehicleRecoveryMethod, PayloadGroup
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
import pytz
from django.conf import settings
from datetime import datetime
from django.utils import timezone as django_timezone 


 
def home(request):
    return redirect('users:register')


@login_required
def rocket_family_list(request):
    # Используем select_related для загрузки данных компании в одном запросе
    rocket_families = RocketFamily.objects.select_related('company').all()

    return render(request, 'space_data/rocket_family_list.html', {
        'rocket_families': rocket_families,
    })

@login_required
def rocket_config_list(request):
    # Загружаем данные с related объектом manufacturer
    rocket_configs = RocketConfiguration.objects.select_related('manufacturer').all()

    return render(request, 'space_data/rocket_config_list.html', {
        'rocket_configs': rocket_configs,
    })

@login_required
def company_list(request):
    # Загружаем все объекты SpaceCompany без сортировки
    companies = SpaceCompany.objects.all()

    return render(request, 'space_data/company_list.html', {
        'companies': companies,
    })

@login_required
def launch_pad_list(request):
    # Поскольку LaunchPad не имеет внешних ключей, select_related не требуется
    launch_pads = LaunchPad.objects.all()
    
    return render(request, 'space_data/launch_pad_list.html', {
        'launch_pads': launch_pads,
    })

@login_required
def vehicle_list(request):
    # Получаем все объекты транспортных средств
    vehicles = Vehicle.objects.all()
    
    return render(request, 'space_data/vehicle_list.html', {
        'vehicles': vehicles,
    })

@login_required
def vehicle_recovery_method_list(request):
    # Получаем все объекты средств спасения
    recovery_methods = VehicleRecoveryMethod.objects.all()
    
    return render(request, 'space_data/vehicle_recovery_method_list.html', {
        'vehicle_recovery_methods': recovery_methods,
    })

@login_required
def payload_group_list(request):
    # Используем select_related для предварительной загрузки связанных данных
    payload_groups = PayloadGroup.objects.select_related('company', 'mission').all()
    
    return render(request, 'space_data/payload_group_list.html', {
        'payload_groups': payload_groups,
    })

@login_required
def launch_mission_list(request):
    # Используем select_related для предварительной загрузки связанных данных
    launch_missions = LaunchMission.objects.select_related('rocket_config', 'launch_pad').all()
    
    return render(request, 'space_data/launch_mission_list.html', {
        'launch_missions': launch_missions,
    })


@login_required
def map_view(request):
    launch_pads = LaunchPad.objects.all()

    launch_pads_data = [
        {
            'name': pad.full_name,
            'description': pad.description,
            'latitude': float(pad.latitude) if pad.latitude is not None else None,
            'longitude': float(pad.longitude) if pad.longitude is not None else None,
            'status': pad.status
        }
        for pad in launch_pads if pad.latitude and pad.longitude
    ]

    return render(request, 'space_data/map.html', {'launch_pads': launch_pads_data})


@login_required
def launch_cards(request):
    utc_current_time = django_timezone.now()

    # Используем временную зону пользователя из настроек
    local_timezone = pytz.timezone(settings.TIME_ZONE)

    # Фильтрация только для прошедших запусков (по времени UTC)
    launches = LaunchMission.objects.filter(
        Q(year__lt=utc_current_time.year) |
        (Q(year=utc_current_time.year) & Q(month__lt=utc_current_time.month)) |
        (Q(year=utc_current_time.year) & Q(month=utc_current_time.month) & Q(day__lt=utc_current_time.day)) |
        (Q(year=utc_current_time.year) & Q(month=utc_current_time.month) & Q(day=utc_current_time.day) & Q(hour__lt=utc_current_time.hour)) |
        (Q(year=utc_current_time.year) & Q(month=utc_current_time.month) & Q(day=utc_current_time.day) & Q(hour=utc_current_time.hour) & Q(minute__lt=utc_current_time.minute))
    ).select_related(
        'rocket_config',
        'rocket_config__vehicle_family',
        'rocket_config__vehicle_family__company',
        'launch_pad'
    ).order_by('-year', '-month', '-day', '-hour', '-minute')

    # Пагинация
    paginator = Paginator(launches, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Обработка прошедших запусков: преобразуем в локальное время
    for launch in page_obj:
        if (launch.year is not None) and (launch.month is not None) and (launch.day is not None) and (launch.hour is not None) and (launch.minute is not None):

            try:
                launch_datetime = datetime(
                    launch.year, 
                    launch.month, 
                    launch.day, 
                    launch.hour, 
                    launch.minute, 
                    tzinfo=pytz.utc
                )

                # Преобразуем UTC-время в локальное время
                launch_local_time = launch_datetime.astimezone(local_timezone)

                # Сохраняем локальные значения обратно в поля
                launch.year = launch_local_time.year
                launch.month = launch_local_time.month
                launch.day = launch_local_time.day
                launch.hour = launch_local_time.hour
                launch.minute = launch_local_time.minute
            except ValueError:
                launch.year = launch.month = launch.day = launch.hour = launch.minute = None
        
        # Изображение ракеты
        rocket_image = launch.rocket_config.get_images().first()
        launch.rocket_image_url = rocket_image.url if rocket_image else 'default_rocket_configurations.png'

        # Логотип компании
        company_image = launch.rocket_config.vehicle_family.company.get_images().first()
        launch.company_logo_url = company_image.url if company_image else None

    local_current_time = utc_current_time.astimezone(local_timezone)
    tz_offset = int(local_current_time.utcoffset().total_seconds() / 3600)

    context = {
        'page_obj': page_obj,
        'tz_offset': "+" + str(tz_offset) if tz_offset >= 0 else str(tz_offset),  # передаем смещение в контекст
    }

    return render(request, 'space_data/launches.html', context)


@login_required
def launch_detail(request, slug):
    mission = get_object_or_404(LaunchMission, slug=slug)
    rocket_config = mission.rocket_config
    company = rocket_config.vehicle_family.company if rocket_config and rocket_config.vehicle_family and rocket_config.vehicle_family.company else None
    recovery_methods = LaunchVehicle.objects.filter(launch=mission).select_related('recovery_method', 'vehicle')
    payloads = mission.payload_groups.all()
    launch_pad = mission.launch_pad

    # Получение текущего времени и часового пояса
    timezone = pytz.timezone(settings.TIME_ZONE)
    current_time = timezone.localize(datetime.now())  # Текущее время с учетом часового пояса
    tz_offset = int(current_time.utcoffset().total_seconds() / 3600)  # Смещение для отображения в GMT+X

    # Форматирование даты запуска в обратном порядке (день-месяц-год)
    launch_date = ''
    if mission.year:
        date_parts = []
        if mission.day:
            date_parts.append(str(mission.day).zfill(2))
        if mission.month:
            date_parts.append(str(mission.month).zfill(2))
        date_parts.append(str(mission.year))

        if mission.hour is not None and mission.minute is not None:
            # Создание datetime для перевода в часовой пояс
            try:
                launch_datetime = datetime(
                    mission.year, 
                    mission.month, 
                    mission.day, 
                    mission.hour, 
                    mission.minute, 
                    tzinfo=pytz.utc
                )

                # Преобразуем в локальное время
                launch_local_time = launch_datetime.astimezone(timezone)

                # Форматируем время в строку
                time_str = f"{launch_local_time.strftime('%H:%M')}"
                launch_date = '-'.join(date_parts) + ' ' + time_str
            except ValueError:
                launch_date = '-'.join(date_parts)  # если ошибка в данных
        else:
            launch_date = '-'.join(date_parts)
    else:
        launch_date = 'Дата неизвестна'

    # Получение изображений
    rocket_images = rocket_config.get_images() if rocket_config else None
    launch_pad_images = launch_pad.get_images() if launch_pad else None

    context = {
        'mission': mission,
        'rocket_config': rocket_config,
        'company': company,
        'recovery_methods': recovery_methods,
        'payloads': payloads,
        'launch_pad': launch_pad,
        'launch_date': launch_date,
        'rocket_images': rocket_images,
        'launch_pad_images': launch_pad_images,
        'tz_offset': "+" + str(tz_offset) if tz_offset > 0 else str(tz_offset),
    }
    
    return render(request, 'space_data/launch_detail.html', context)