from django.shortcuts import render
from space_data.models import LaunchMission
from django.db.models import Q
from django.conf import settings
from django.utils import timezone as django_timezone
from datetime import datetime
import pytz


def home(request):
    # Получаем текущее время в UTC с использованием Django
    utc_current_time = django_timezone.now()

    # Переименуем временную зону для пользователя, чтобы избежать конфликта
    user_timezone = pytz.timezone(settings.TIME_ZONE)
    current_time = utc_current_time.astimezone(user_timezone)

    # Фильтрация для прошлых запусков
    past_launches = LaunchMission.objects.filter(
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
    ).order_by('-year', '-month', '-day', '-hour', '-minute')[:4]

    # Фильтрация для будущих запусков
    future_launches = LaunchMission.objects.filter(
        Q(year__gt=utc_current_time.year) |
        (Q(year=utc_current_time.year) & Q(month__gt=utc_current_time.month)) |
        (Q(year=utc_current_time.year) & Q(month=utc_current_time.month) & (Q(day__gt=utc_current_time.day) | Q(day__isnull=True))) |
        (Q(year=utc_current_time.year) & Q(month=utc_current_time.month) & Q(day=utc_current_time.day) & (Q(hour__gt=utc_current_time.hour) | Q(hour__isnull=True))) |
        (Q(year=utc_current_time.year) & Q(month=utc_current_time.month) & Q(day=utc_current_time.day) & Q(hour=utc_current_time.hour) & (Q(minute__gte=utc_current_time.minute) | Q(minute__isnull=True)))
    ).select_related(
        'rocket_config',
        'rocket_config__vehicle_family',
        'rocket_config__vehicle_family__company',
        'launch_pad'
    ).order_by('year', 'month', 'day', 'hour', 'minute')[:4]

    # Обработка прошедших запусков (перевод в локальное время)
    for launch in past_launches:
        if all(getattr(launch, field) is not None for field in ['year', 'month', 'day', 'hour', 'minute']):
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
                launch_local_time = launch_datetime.astimezone(user_timezone)

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

    # Обработка будущих запусков (перевод в локальное время)
    for launch in future_launches:
        if all(getattr(launch, field) is not None for field in ['year', 'month', 'day', 'hour', 'minute']):
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
                launch_local_time = launch_datetime.astimezone(user_timezone)

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

    tz_offset = int(current_time.utcoffset().total_seconds() / 3600)

    context = {
        'past_launches': past_launches,
        'future_launches': future_launches,
        'tz_offset': "+" + str(tz_offset) if tz_offset > 0 else str(tz_offset),
    }

    return render(request, 'home.html', context)
