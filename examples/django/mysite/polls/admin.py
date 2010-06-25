from mysite.polls.models import Poll
from django.contrib import admin
from mysite.polls.models import Choice

class ChoiceInline(admin.TabularInline):

    model = Choice
    extra = 3

class PollAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]

admin.site.register(Poll, PollAdmin)