from django.contrib import admin, messages
from django.urls import reverse, path
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.utils.html import format_html
from .models import (
    SpaceCompany, Manufacturer, RocketFamily, Vehicle, VehicleRecoveryMethod,
    LaunchPad, CompanyInternetResource, RocketConfiguration, LaunchMission,
    PayloadGroup, LaunchVehicle, Image
)
from django import forms

# Универсальная форма для загрузки изображений
class BaseImageForm(forms.ModelForm):
    new_images = forms.FileField(
        required=False,
        label="Upload new photos"
    )

    class Meta:
        fields = '__all__'


# Форма для модели SpaceCompany
class SpaceCompanyAdminForm(BaseImageForm):
    class Meta(BaseImageForm.Meta):
        model = SpaceCompany


# Форма для модели RocketFamily
class RocketFamilyAdminForm(BaseImageForm):
    class Meta(BaseImageForm.Meta):
        model = RocketFamily


# Форма для модели Vehicle
class VehicleAdminForm(BaseImageForm):
    class Meta(BaseImageForm.Meta):
        model = Vehicle


# Форма для модели VehicleRecoveryMethod
class VehicleRecoveryMethodAdminForm(BaseImageForm):
    class Meta(BaseImageForm.Meta):
        model = VehicleRecoveryMethod


# Форма для модели LaunchPad
class LaunchPadAdminForm(BaseImageForm):
    class Meta(BaseImageForm.Meta):
        model = LaunchPad


# Форма для модели RocketConfiguration
class RocketConfigurationAdminForm(BaseImageForm):
    class Meta(BaseImageForm.Meta):
        model = RocketConfiguration


# Форма для модели LaunchMission
class LaunchMissionAdminForm(BaseImageForm):
    class Meta(BaseImageForm.Meta):
        model = LaunchMission


# Форма для модели PayloadGroup
class PayloadGroupAdminForm(BaseImageForm):
    class Meta(BaseImageForm.Meta):
        model = PayloadGroup


class BaseImageAdmin(admin.ModelAdmin):
    image_object_type = None
    image_object_short = None

    def related_images(self, obj):
        if not self.image_object_type or not self.image_object_short:
            raise ValueError("Необходимо указать image_object_type в наследуемом классе")

        images = Image.objects.filter(object_type=self.image_object_type, object_id=obj.id)
        if images.exists():
            image_tags = ''.join(
                f'''
                <div style="position: relative; display: inline-block; margin: 5px;">
                    <img src="{settings.MEDIA_URL}{image.url}" height="130" style="display: block;" />
                    <a href="{reverse(f'admin:{self.image_object_short}_delete_image', args=[image.id])}" 
                    style="
                        position: absolute;
                        top: 0;
                        right: 0;
                        transform: translate(50%, -50%);
                        background-color: red;
                        color: white;
                        border-radius: 50%;
                        width: 20px;
                        height: 20px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        text-decoration: none;
                        font-weight: bold;
                        font-size: 14px;
                    "
                    title="Удалить"
                    onclick="return confirm('Вы уверены, что хотите удалить это изображение?');"
                    >×</a>
                </div>
                ''' for image in images
            )
            return format_html(image_tags)
        return "-"
    related_images.short_description = 'Images'

    def save_model(self, request, obj, form, change):
        """Сохранение объекта и связанных изображений."""
        super().save_model(request, obj, form, change)
        if form.cleaned_data.get('new_images'):
            for image_file in request.FILES.getlist('new_images'):
                Image.objects.create(
                    object_type=self.image_object_type,
                    object_id=obj.id,
                    url=image_file
                )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('delete-image/<int:image_id>/', self.admin_site.admin_view(self.delete_image), name=f'{self.image_object_short}_delete_image'),
        ]
        return custom_urls + urls

    def delete_image(self, request, image_id):
        """Удаление изображения и перенаправление на страницу объекта."""
        image = get_object_or_404(Image, id=image_id)
        image.delete()
        messages.success(request, "Изображение успешно удалено.")
        return redirect(request.META.get('HTTP_REFERER', f'admin:app_{self.image_object_short}_changelist'))
    
    class Media:
        js = ('js\image_paste.js',) 


class CompanyInternetResourceInline(admin.TabularInline):
    model = CompanyInternetResource
    extra = 1

@admin.register(SpaceCompany)
class SpaceCompanyAdmin(BaseImageAdmin):
    form = SpaceCompanyAdminForm
    image_object_type = 'space_companies'
    image_object_short = 'spacecompany'
    list_display = ('id', 'short_name', 'full_name', 'type_of_organization', 'country', 'founded_year', 'head_title_and_name', 'related_images')
    readonly_fields = ('related_images',)
    search_fields = ('short_name', 'full_name', 'country')
    list_filter = ('type_of_organization', 'country')
    inlines = [CompanyInternetResourceInline]
    ordering = ('id',)
    fieldsets = (
        ('Name', {
            'fields': ('short_name', 'full_name')
        }),
        ('Addition info', {
            'fields': ('type_of_organization', 'country', 'head_title_and_name', 'founded_year', 'new_images', 'related_images')
        }),
        ('Resources', {
            'fields': ('resources_comment',),
        }),
    )
    list_per_page = 40

    def resources_comment(self, obj):
        return format_html(
            '<div style="padding: 8px; font-size: 15px; background-color: #000000; border: 1px solid #ff0000;">'
            '<strong>Main internet resources:</strong> instagram | twitter | website'
            '</div>'
        )
    resources_comment.short_description = 'Comment'


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)
    ordering = ('id',)


@admin.register(RocketFamily)
class RocketFamilyAdmin(BaseImageAdmin):
    form = RocketFamilyAdminForm
    image_object_type = 'rocket_families'
    image_object_short = 'rocketfamily'
    list_display = ('id', 'family_name', 'company', 'related_images')
    readonly_fields = ('related_images',)
    search_fields = ('family_name', 'company__short_name')
    ordering = ('id',)
    autocomplete_fields = ['company']
    list_per_page = 40


@admin.register(Vehicle)
class VehicleAdmin(BaseImageAdmin):
    form = VehicleAdminForm
    image_object_type = 'vehicles'
    image_object_short = 'vehicle'
    list_display = ('id', 'name', 'vehicle_type', 'related_images')
    search_fields = ('name', 'vehicle_type')
    list_filter = ('vehicle_type',)
    ordering = ('id',)
    readonly_fields = ('related_images',)
    list_per_page = 40


@admin.register(VehicleRecoveryMethod)
class VehicleRecoveryMethodAdmin(BaseImageAdmin):
    form = VehicleRecoveryMethodAdminForm
    image_object_type = 'vehicle_recovery_methods'
    image_object_short = 'vehiclerecoverymethod'
    list_display = ('id', 'type', 'short_name', 'full_name', 'related_images')
    search_fields = ('type', 'short_name', 'full_name')
    list_filter = ('type',)
    ordering = ('id',)
    readonly_fields = ('related_images',)
    list_per_page = 40


@admin.register(LaunchPad)
class LaunchPadAdmin(BaseImageAdmin):
    form = LaunchPadAdminForm
    image_object_type = 'launch_pads'
    image_object_short = 'launchpad'
    list_display = ('id', 'full_name', 'status', 'latitude', 'longitude', 'related_images')
    list_editable = ('status', 'latitude', 'longitude')
    readonly_fields = ('related_images',)
    search_fields = ('full_name', 'status')
    list_filter = ('status',)
    ordering = ('id',)
    list_per_page = 40


@admin.register(RocketConfiguration)
class RocketConfigurationAdmin(BaseImageAdmin):
    form = RocketConfigurationAdminForm
    image_object_type = 'rocket_configurations'
    image_object_short = 'rocketconfiguration'
    list_display = ('id', 'modification_name', 'vehicle_family', 'manufacturer', 'status', 'reusable', 'related_images')
    readonly_fields = ('related_images',)
    search_fields = ('modification_name', 'vehicle_family__family_name', 'manufacturer__name')
    autocomplete_fields = ['vehicle_family', 'manufacturer']
    list_filter = ('status', 'reusable')
    ordering = ('modification_name',)
    fieldsets = (
        ('Main', {
            'fields': ('modification_name', 'vehicle_family', 'manufacturer', 'status', 'reusable', 'new_images', 'related_images')
        }),
        ('Addition info', {
            'fields': (
                'price', 'launch_thrust', 'payload_mass_leo', 'payload_mass_gto',
                'stages', 'side_boosters', 'rocket_height', 'fairing_diameter', 'fairing_height', 'wiki_url'
            )
        }),
    )
    list_per_page = 40

    # class Media:
    #     js = ('js\image_paste.js',) 


class LaunchVehicleInline(admin.StackedInline):
    model = LaunchVehicle
    extra = 1
    autocomplete_fields = ['vehicle', 'recovery_method']
    readonly_fields = ('related_images',)

    def related_images(self, obj):
        if obj.id:
            images = Image.objects.filter(object_type='launch_vehicles', object_id=obj.id)
            if images.exists():
                return format_html(''.join(
                    f'<img src="{settings.MEDIA_URL}{image.url}" height="100" style="margin: 5px;" />' 
                    for image in images
                ))
        return "-"
    related_images.short_description = 'Images'

class PayloadGroupInline(admin.StackedInline):
    model = PayloadGroup
    form = PayloadGroupAdminForm
    extra = 1
    readonly_fields = ('related_images',)
    fields = ('name', 'description', 'orbit_type', 'payload_count', 'mass', 'new_images', 'related_images')

    def related_images(self, obj):
        if obj.id:
            images = Image.objects.filter(object_type='payload_groups', object_id=obj.id)
            if images.exists():
                return format_html(''.join(
                    f'<img src="{settings.MEDIA_URL}{image.url}" height="100" style="margin: 5px;" />' 
                    for image in images
                ))
        return "-"
    related_images.short_description = 'Images'


@admin.register(LaunchMission)
class LaunchMissionAdmin(BaseImageAdmin):
    form = LaunchMissionAdminForm
    image_object_type = 'launches_missions'
    image_object_short = 'launchmission'
    list_display = ('id', 'name', 'day', 'month', 'year', 'hour', 'minute', 'rocket_config', 'launch_pad', 'flight_status', 'related_images')
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ('related_images',)
    search_fields = ('name', 'rocket_config__modification_name', 'launch_pad__full_name')
    # list_filter = ('flight_status',)
    ordering = ('-year', '-month', '-day', '-hour', '-minute')
    fieldsets = (
        ('Main info', {
            'fields': ('name', 'slug', 'day', 'month', 'year', 'hour', 'minute', 'new_images', 'related_images')
        }),
        ('Details', {
            'fields': ('rocket_config', 'launch_pad', 'flight_status', 'video_url', 'description')
        }),
    )
    inlines = [LaunchVehicleInline, PayloadGroupInline]
    autocomplete_fields = ['rocket_config', 'launch_pad']
    list_per_page = 40


@admin.register(PayloadGroup)
class PayloadGroupAdmin(BaseImageAdmin):
    form = PayloadGroupAdminForm
    image_object_type = 'payload_groups'
    image_object_short = 'payloadgroup'
    list_display = ('id', 'name', 'mission', 'orbit_type', 'related_images')
    readonly_fields = ('related_images',)
    search_fields = ('name', 'mission__name', 'orbit_type')
    # list_filter = ('orbit_type',)
    ordering = ('id',)
    list_per_page = 40
    autocomplete_fields = ['mission']


@admin.register(LaunchVehicle)
class LaunchVehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'launch', 'vehicle', 'attempted_recovery', 'recovery_method', 'recovery_result')
    search_fields = ('launch__name', 'vehicle__name', 'recovery_method__type')
    # list_filter = ('attempted_recovery',)
    ordering = ('launch', 'vehicle')
    autocomplete_fields = ['launch', 'vehicle', 'recovery_method']


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'object_type', 'object_id', 'url', 'image_tag')
    readonly_fields = ('id', 'object_type', 'object_id', 'url', 'image_tag',)
    search_fields = ('object_type', 'object_id', 'url')
    list_filter = ('object_type',)
    ordering = ('id',)
    list_per_page = 40
    save_on_top = True

    def image_tag(self, obj):
        """Отображение миниатюры изображения в админке."""
        if obj.url:
            full_url = f"{settings.MEDIA_URL}{obj.url}"
            return format_html('<img src="{}" height="150" />', full_url)
        return "-"
    image_tag.short_description = 'Image'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False