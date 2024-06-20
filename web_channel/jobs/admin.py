from django.contrib import admin

from .models import User, Job, Agent, UserProfile, Category, FollowUp



class LeadAdmin(admin.ModelAdmin):
    # fields = (
    #     'first_name',
    #     'last_name',
    # )




    list_display = [ 'kra_pin']
    list_display_links = ['kra_pin']
    list_editable = []
    list_filter = ['channel_id']
    search_fields = [ 'channel_id', 'kra_pin']



admin.site.register(Category)
admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Job, LeadAdmin)
admin.site.register(Agent)
admin.site.register(FollowUp)
