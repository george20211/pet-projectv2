from django.contrib import admin

from .models import Group, Post


class Administrator(admin.ModelAdmin):
    list_display = ('text', 'pub_date', 'author', 'group', 'id')
    list_filter = ('text', 'pub_date')
    search_fields = ("text",)
    empty_value_display = "-пусто-"


admin.site.register(Post, Administrator)
admin.site.register(Group)
