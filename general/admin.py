from general.models import Employee, Reserve, Menu, Food, Feedback
from django.contrib import admin

from django_jalali.admin.filters import JDateFieldListFilter

# you need import this for adding jalali calander widget
import django_jalali.admin as jadmin  # noqa


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('fullname',)
admin.site.register(Employee, EmployeeAdmin)


class ReserveAdmin(admin.ModelAdmin):
    list_display = ('employee', 'menu', 'food_name')
    list_filter = (
        ('date', JDateFieldListFilter),
    )

admin.site.register(Reserve, ReserveAdmin)


class MenuAdmin(admin.ModelAdmin):
    list_display = ('date',)

admin.site.register(Menu, MenuAdmin)


class FoodAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Food, FoodAdmin)


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('reserve',)

admin.site.register(Feedback, FeedbackAdmin)