from django.db import models
from django_jalali.db import models as jmodels
from django.contrib.auth.models import User
import jdatetime


class Employee(models.Model):
    _type1 = '1'
    _type2 = '2'
    _other = 'other'

    value_choices = [
        (_type1, 'رسمی'),
        (_type2, 'قراردادی'),
        (_other, 'سایر'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100)
    personal_code = models.CharField(max_length=100)
    type = models.CharField(choices=value_choices, max_length=50, null=True)
    price = models.CharField(max_length=100, null=True, blank=True)
    delivery = models.BooleanField(default=False)
    popup = models.BooleanField(default=False)

    def __str__(self):
        return self.fullname


class Food(models.Model):
    _type1 = '1'
    _type2 = '2'
    _type3 = '3'
    _type4 = '4'
    _type5 = '5'
    _other = 'other'

    value_choices = [
        (_type1, 'ماست'),
        (_type2, 'نوشابه'),
        (_type3, 'دلستر'),
        (_type4, 'دوغ'),
        (_type5, 'زیتون'),
        (_other, 'سایر'),
    ]

    name = models.CharField(max_length=100)
    desert = models.CharField(choices=value_choices, max_length=50, null=True)
    avatar = models.ImageField(upload_to='images')
    calorie = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name


class Menu(models.Model):
    type_1 = models.ForeignKey(Food, on_delete=models.PROTECT, null=True, blank=True, related_name='type_1')
    type_2 = models.ForeignKey(Food, on_delete=models.PROTECT, null=True, blank=True, related_name='type_2')
    date = jmodels.jDateField(null=True, blank=True)
    holiday = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % (self.date)


class Reserve(models.Model):
    _type1 = '1'
    _type2 = '2'
    _other = 'other'

    value_choices = [
        (_type1, 'نوع 1'),
        (_type2, 'نوع 2'),
        (_other, 'سایر'),
    ]

    menu = models.ForeignKey(Menu, on_delete=models.PROTECT, null=True, related_name='منو')
    type = models.CharField(choices=value_choices, max_length=50, null=True)
    food_name = models.CharField(max_length=100, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=u'کارمند', related_name='employee')
    date = jmodels.jDateField(default=jdatetime.datetime(1402, 7, 1))
    serve = models.BooleanField(default=False)
    night = models.BooleanField(default=False)
    transfer = models.BooleanField(default=False)
    transfer_to = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True, verbose_name=u'انتقال', related_name='transfer_to')

    def __str__(self):
        return "%s" % (self.date)


class Feedback(models.Model):
    _rate1 = '1'
    _rate2 = '2'
    _rate3 = '3'
    _rate4 = '4'
    _rate5 = '5'

    value_choices = [
        (_rate1, '1'),
        (_rate2, '2'),
        (_rate3, '3'),
        (_rate4, '4'),
        (_rate5, '5'),
    ]

    reserve = models.ForeignKey(Reserve,on_delete=models.CASCADE, null=True, related_name='رزرو')
    rate = models.CharField(choices=value_choices, max_length=50, null=True)
    comment = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return "%s" % (self.reserve)



