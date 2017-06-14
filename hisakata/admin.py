from django.contrib import admin
from . import models


class RoundInline(admin.TabularInline):
    model = models.Round


class MatchInline(admin.TabularInline):
    model = models.Match


class PlayingInline(admin.TabularInline):
    model = models.Playing


class DateAdmin(admin.ModelAdmin):
    inlines = [RoundInline, ]


class RoundAdmin(admin.ModelAdmin):
    inlines = [MatchInline, ]
    list_display = ('round', 'admin_date',)


class MatchAdmin(admin.ModelAdmin):
    inlines = [PlayingInline, ]
    list_display = ('admin_date', 'round', 'player1', 'player2', 'winner', 'result',)


class PlayerAdmin(admin.ModelAdmin):
    inlines = [PlayingInline, ]


admin.site.register(models.Date, DateAdmin)
admin.site.register(models.Round, RoundAdmin)
admin.site.register(models.Player)
admin.site.register(models.Match, MatchAdmin)
