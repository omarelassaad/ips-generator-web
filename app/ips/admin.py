from django.contrib import admin
from django.utils.html import format_html
from django.core.cache import cache
from .models import Profile, QuestionnaireResponse, ChooseMyselfData, LetPmChooseData, ReturnsUpload

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('user__username', 'user__email')

class QuestionnaireResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'answer', 'score')
    search_fields = ('user__username', 'question', 'answer')

class ChooseMyselfDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_owner', 'account_type', 'amount', 'strategy', 'version_number')
    search_fields = ('user__username', 'account_owner', 'account_type', 'strategy')

class LetPmChooseDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_owner', 'account_type', 'amount', 'timestamp', 'additional_info')
    search_fields = ('user__username', 'account_owner', 'account_type', 'additional_info')
    ordering = ('-timestamp',)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(QuestionnaireResponse, QuestionnaireResponseAdmin)
admin.site.register(ChooseMyselfData, ChooseMyselfDataAdmin)
admin.site.register(LetPmChooseData, LetPmChooseDataAdmin)


@admin.register(ReturnsUpload)
class ReturnsUploadAdmin(admin.ModelAdmin):
    list_display  = ('as_of_date', 'uploaded_at', 'is_active', 'file_link')
    list_filter   = ('is_active',)
    readonly_fields = ('uploaded_at',)
    ordering      = ('-uploaded_at',)

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Download</a>', obj.file.url)
        return "—"
    file_link.short_description = "File"

    def save_model(self, request, obj, form, change):
        if obj.is_active:
            ReturnsUpload.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)
        cache.delete('performance_data')
