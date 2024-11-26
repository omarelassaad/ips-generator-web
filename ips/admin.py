from django.contrib import admin
from .models import Profile, QuestionnaireResponse, ChooseMyselfData, LetPmChooseData

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
