from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils import timezone
import calendar
import os
import uuid
import re
from django.conf import settings
from django.core.files.storage import default_storage


def validate_founded_year(value):
    current_year = timezone.now().year
    if value < 1900 or value > current_year:
        raise ValidationError(f"Год основания должен быть между 1900 и {current_year}.")

class SpaceCompany(models.Model):
    id = models.AutoField(primary_key=True)
    short_name = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255)
    type_of_organization = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    head_title_and_name = models.CharField(max_length=255, null=True, blank=True)
    founded_year = models.IntegerField(validators=[validate_founded_year], null=True, blank=True)

    class Meta:
        db_table = 'space_companies'
        indexes = [
            models.Index(fields=['short_name'], name='idx_sc_sname'),
            models.Index(fields=['full_name'], name='idx_sc_fname'),
            models.Index(fields=['country'], name='idx_sc_country'),
        ]

    def get_images(self):
        return Image.objects.filter(object_id=self.id, object_type='space_companies')

    def __str__(self):
        return self.short_name

class Manufacturer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'manufacturers'

    def __str__(self):
        return self.name


class RocketFamily(models.Model):
    id = models.AutoField(primary_key=True)
    family_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    wiki_url = models.TextField(null=True, blank=True)
    company = models.ForeignKey(SpaceCompany, on_delete=models.SET_NULL, null=True, blank=True, related_name='rocket_families')

    class Meta:
        db_table = 'rocket_families'
        indexes = [models.Index(fields=['company'], name='idx_rf_company_id')]

    def get_images(self):
        return Image.objects.filter(object_id=self.id, object_type='rocket_families')

    def __str__(self):
        return self.family_name


class Vehicle(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    vehicle_type = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'vehicles'

    def get_images(self):
        return Image.objects.filter(object_id=self.id, object_type='vehicles')
    
    def __str__(self):
        return self.name


class VehicleRecoveryMethod(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=50)
    short_name = models.CharField(max_length=50, null=True, blank=True)
    full_name = models.CharField(max_length=255, unique=True, null=True, blank=True)

    class Meta:
        db_table = 'vehicle_recovery_methods'
    
    def get_images(self):
        return Image.objects.filter(object_id=self.id, object_type='vehicle_recovery_methods')
    
    def __str__(self):
        return self.full_name


class LaunchPad(models.Model):
    STATUS_CHOICES = [('Active', 'Active'), ('Under Construction', 'Under Construction'), ('Abandoned', 'Abandoned')]

    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, validators=[MinValueValidator(-90), MaxValueValidator(90)], null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, validators=[MinValueValidator(-180), MaxValueValidator(180)], null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, null=True, blank=True)

    class Meta:
        db_table = 'launch_pads'
        indexes = [models.Index(fields=['status'], name='idx_lp_status')]

    def get_images(self):
        return Image.objects.filter(object_id=self.id, object_type='launch_pads')
    
    def __str__(self):
        return self.full_name


class CompanyInternetResource(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(SpaceCompany, on_delete=models.CASCADE, related_name='internet_resources')
    resource_type = models.CharField(max_length=50)
    url = models.TextField()

    class Meta:
        db_table = 'company_internet_resources'
        unique_together = ('company', 'resource_type')
        indexes = [models.Index(fields=['company'], name='idx_cir_company_id')]

    def __str__(self):
        return self.url


class RocketConfiguration(models.Model):
    STATUS_CHOICES = [('Active', 'Active'), ('Retired', 'Retired'), ('Planned', 'Planned')]

    id = models.AutoField(primary_key=True)
    modification_name = models.CharField(max_length=255)
    vehicle_family = models.ForeignKey(RocketFamily, on_delete=models.CASCADE, related_name='configurations')
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, null=True, blank=True, related_name='rocket_configurations')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    price = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    reusable = models.BooleanField(null=True, blank=True)
    launch_thrust = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(0.0001)], null=True, blank=True)
    payload_mass_leo = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    payload_mass_gto = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    stages = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    side_boosters = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    rocket_height = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(0.0001)], null=True, blank=True)
    fairing_diameter = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(0.0001)], null=True, blank=True)
    fairing_height = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(0.0001)], null=True, blank=True)
    wiki_url = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'rocket_configurations'
        unique_together = ('modification_name', 'vehicle_family')
        indexes = [
            models.Index(fields=['manufacturer'], name='idx_rc_manufacturer_id'),
            models.Index(fields=['status'], name='idx_rc_status'),
            models.Index(fields=['vehicle_family'], name='idx_rc_vf_id'),
        ]

    def get_images(self):
        return Image.objects.filter(object_id=self.id, object_type='rocket_configurations')
    
    def __str__(self):
        return self.modification_name


class LaunchMission(models.Model):
    FLIGHT_STATUS_CHOICES = [('Success', 'Success'), ('Partial Failure', 'Partial Failure'), ('Failure', 'Failure')]

    id = models.AutoField(primary_key=True)
    rocket_config = models.ForeignKey(RocketConfiguration, on_delete=models.CASCADE, related_name='launch_missions')
    year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2100)], null=True, blank=True)
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], null=True, blank=True)
    day = models.IntegerField(null=True, blank=True)
    hour = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(23)], null=True, blank=True)
    minute = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(59)], null=True, blank=True)
    launch_pad = models.ForeignKey(LaunchPad, on_delete=models.SET_NULL, null=True, blank=True, related_name='launch_missions')
    flight_status = models.CharField(max_length=50, choices=FLIGHT_STATUS_CHOICES, null=True, blank=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)  # Новое поле для слага
    description = models.TextField(null=True, blank=True)
    video_url = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'launches_missions'
        indexes = [
            models.Index(fields=['rocket_config'], name='idx_lm_rc_id'),
            models.Index(fields=['launch_pad'], name='idx_lm_lp_id'),
        ]

    def clean(self):
        if (self.hour is None) != (self.minute is None):
            raise ValidationError("Hour and minute must both be set or both be null.")
        
        combinations = [
            all(v is None for v in [self.minute, self.hour, self.day, self.month, self.year]),
            self.year is not None and all(v is None for v in [self.minute, self.hour, self.day, self.month]),
            all(v is not None for v in [self.year, self.month]) and all(v is None for v in [self.minute, self.hour, self.day]),
            all(v is not None for v in [self.year, self.month, self.day]) and all(v is None for v in [self.minute, self.hour]),
            all(v is not None for v in [self.year, self.month, self.day, self.hour, self.minute]),
        ]
        if not any(combinations):
            raise ValidationError("Invalid combination of date and time fields.")
        
        if self.month is not None:
            if self.month < 1 or self.month > 12:
                raise ValidationError("Month must be between 1 and 12.")

        if self.day is not None:
            if self.month is None or self.year is None:
                raise ValidationError("Day cannot be set without month and year.")
            max_day = calendar.monthrange(self.year, self.month)[1]
            if not (1 <= self.day <= max_day):
                raise ValidationError(f"Invalid day for the given month and year: {self.day}")
    
    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)
        
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = f"{base_slug}-{self.id}"
            if len(unique_slug) > 255:
                unique_slug = unique_slug[:252] + '-' + str(self.id)
            self.slug = unique_slug
        
        super().save(*args, **kwargs)


    def get_images(self):
        return Image.objects.filter(object_id=self.id, object_type='launches_missions')
    
    def __str__(self):
        return self.name


class PayloadGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    orbit_type = models.CharField(max_length=255, null=True, blank=True)
    payload_count = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    mass = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    mission = models.ForeignKey(LaunchMission, on_delete=models.CASCADE, null=True, blank=True, related_name='payload_groups')

    class Meta:
        db_table = 'payload_groups'
        indexes = [
            models.Index(fields=['mission'], name='idx_pg_mission_id'),
        ]

    def get_images(self):
        return Image.objects.filter(object_id=self.id, object_type='payload_groups')
    
    def __str__(self):
        return self.name


class LaunchVehicle(models.Model):
    RECOVERY_RESULT_CHOICES = [('Success', 'Success'), ('Partial Failure', 'Partial Failure'), ('Failure', 'Failure'), ('Pending', 'Pending')]

    launch = models.ForeignKey(LaunchMission, on_delete=models.CASCADE, related_name='launch_vehicles')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='launch_vehicles')
    attempted_recovery = models.BooleanField()
    recovery_method = models.ForeignKey(VehicleRecoveryMethod, on_delete=models.SET_NULL, null=True, blank=True, related_name='launch_vehicles')
    recovery_result = models.CharField(max_length=50, choices=RECOVERY_RESULT_CHOICES, null=True, blank=True)

    class Meta:
        db_table = 'launch_vehicle'
        unique_together = ('launch', 'vehicle')
        indexes = [
            models.Index(fields=['launch'], name='idx_lv_launch_id'),
            models.Index(fields=['vehicle'], name='idx_lv_vehicle_id'),
            models.Index(fields=['recovery_method'], name='idx_lv_rm_id'),
        ]



def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*\s]', '_', filename)

def get_unique_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]

    object_name = instance.get_object_name()
    if not object_name:
        sanitized_name = "unknown"
    else:
        sanitized_name = sanitize_filename(object_name)
    
    unique_name = f"{sanitized_name}_{uuid.uuid4().hex}.{ext}"
    
    return os.path.join(instance.object_type, unique_name)

class Image(models.Model):
    OBJECT_TYPE_CHOICES = [
        ('space_companies', 'Space Companies'),
        ('vehicles', 'Vehicles'),
        ('launches_missions', 'Launches Missions'),
        ('payload_groups', 'Payload Groups'),
        ('vehicle_recovery_methods', 'Vehicle Recovery Methods'),
        ('rocket_configurations', 'Rocket Configurations'),
        ('launch_pads', 'Launch Pads'),
        ('rocket_families', 'Rocket Families')
    ]

    id = models.AutoField(primary_key=True)
    url = models.ImageField(upload_to=get_unique_image_upload_path)
    object_id = models.PositiveIntegerField()
    object_type = models.CharField(max_length=50, choices=OBJECT_TYPE_CHOICES)

    class Meta:
        db_table = 'images'
        indexes = [
            models.Index(fields=['object_id'], name='idx_img_obj_id'),
            models.Index(fields=['object_type'], name='idx_img_obj_type'),
        ]

    def save(self, *args, **kwargs):
        """Переопределение метода save для обработки старого файла."""
        # Проверка на наличие существующего объекта в базе данных
        if self.pk:
            old_instance = Image.objects.filter(pk=self.pk).first()
            if old_instance and old_instance.url != self.url:
                if default_storage.exists(old_instance.url.name):
                    default_storage.delete(old_instance.url.name)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Переопределение метода delete для удаления файла."""
        if self.url and default_storage.exists(self.url.name):
            default_storage.delete(self.url.name)
        super().delete(*args, **kwargs)

    def get_object_name(self):
        """Получаем имя объекта в зависимости от object_type."""
        if self.object_type == 'space_companies':
            return SpaceCompany.objects.filter(id=self.object_id).values_list('full_name', flat=True).first()
        elif self.object_type == 'rocket_families':
            return RocketFamily.objects.filter(id=self.object_id).values_list('family_name', flat=True).first()
        elif self.object_type == 'vehicles':
            return Vehicle.objects.filter(id=self.object_id).values_list('name', flat=True).first()
        elif self.object_type == 'vehicle_recovery_methods':
            return VehicleRecoveryMethod.objects.filter(id=self.object_id).values_list('full_name', flat=True).first()
        elif self.object_type == 'launch_pads':
            return LaunchPad.objects.filter(id=self.object_id).values_list('full_name', flat=True).first()
        elif self.object_type == 'rocket_configurations':
            return RocketConfiguration.objects.filter(id=self.object_id).values_list('modification_name', flat=True).first()
        elif self.object_type == 'launches_missions':
            return LaunchMission.objects.filter(id=self.object_id).values_list('name', flat=True).first()
        elif self.object_type == 'payload_groups':
            return PayloadGroup.objects.filter(id=self.object_id).values_list('name', flat=True).first()
        return None