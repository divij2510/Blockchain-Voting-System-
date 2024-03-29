from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Vote)
admin.site.register(Voter)

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'vote_count', 'w3id')