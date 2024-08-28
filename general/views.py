from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm
from django.contrib import messages
from django.http import HttpResponseRedirect
from general.models import Reserve, Menu, Employee, Food, Feedback
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from jalali_date import datetime2jalali, date2jalali
import jdatetime
from django.urls import reverse_lazy
import urllib
from dateutil import parser
from jdatetime import datetime as jalali_datetime
from datetime import datetime, timedelta
from django.db.models import Q
from django.shortcuts import HttpResponse
from django.db.models import Count
from django.views.generic import View
from django.utils import timezone
import os
from django.template.loader import get_template
from io import BytesIO
import xhtml2pdf.pisa as pisa
from django.template.loader import get_template
from django.template import Context
import pdfkit
from django.http import Http404
import re
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


"""

    user accounting functions that consist login and logout
    
"""


def login_user(request):
    try:
        if request.user.is_authenticated:
            return redirect('general:home')

        next = request.GET.get('next')
        form = UserLoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            if next:
                return redirect(next)
            return redirect('general:home')

        context = {
            'form': form,
        }

        return render(request, 'login.html', context)

    except:
        return render(request, 'login.html')


def logout_user(request):
    try:
        logout(request)
        return redirect('login')
    except:
        return render(request, 'login.html')


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'رمز عبور شما با موفقیت تغییر یافت !')
            return redirect('general:login')
        else:
            messages.error(request, 'لطفا در وارد کردن اطلاعات صحیح دقت کنید')
    else:
        if request.user.is_authenticated:
            form = PasswordChangeForm(request.user)
            employe = Employee.objects.get(user=request.user)
            context = {
                'employe': employe,
                'form': form
            }
            return render(request, 'change_password.html', context)

    form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


@login_required(login_url='general:login')
def dashboard(request):
    try:
        if request.user.is_authenticated:
            menus = Menu.objects.all().order_by('date')
            count = Menu.objects.count()
            paginator = Paginator(menus, 7)

            # current_page = int(request.GET.get('page') or 1)
            # Find the page number containing today's date
            today_date = jdatetime.datetime.now().strftime("%Y-%m-%d")  # Today's date in '%Y-%m-%d' format
            page_number_with_today = 1  # Default to first page

            for index, menu in enumerate(menus):
                menu_date = menu.date.strftime("%Y-%m-%d")
                if menu_date in today_date:
                    page_number_with_today = index // 7 + 1  # Assuming 7 items per page
                    break

            current_page = int(request.GET.get('page') or page_number_with_today)
            page = paginator.page(current_page)
            all_menu = page.object_list

            user = get_object_or_404(User, username=request.user)
            user_reserved = Reserve.objects.filter(employee__user=user)
            user_feedback = Feedback.objects.filter(reserve__employee__user=user)
            employe = Employee.objects.get(user=request.user)

            today1 = jdatetime.datetime.now().strftime("%d %B %Y")  # '1399 01 05'
            today2 = jdatetime.datetime.now().strftime("%Y-%m-%d")  # '1399 01 05'
            today3 = jdatetime.datetime.now().strftime("%B")  # '1399 01 05'

            reserves_total_price = ''
            start_gregorian_date = jdatetime.date(int(jdatetime.datetime.now().strftime("%Y")), int(jdatetime.datetime.now().strftime("%m")), 1).togregorian()
            end_gregorian_date = jdatetime.date(int(jdatetime.datetime.now().strftime("%Y")), int(jdatetime.datetime.now().strftime("%m")), 29).togregorian()
            reserves_sum = Reserve.objects.filter(employee__user=request.user, menu__date__range=[start_gregorian_date, end_gregorian_date], serve=True).order_by('employee__fullname').count()
            reserves_nights = Reserve.objects.filter(employee__user=request.user, menu__date__range=[start_gregorian_date, end_gregorian_date], night=True).order_by('employee__fullname').count()


            if employe.type == '1':
                reserves_total_price = (reserves_sum + reserves_nights) * int(employe.price)
            elif employe.type == '2':
                reserves_total_price = (reserves_sum + reserves_nights) * int(employe.price)

            this_year = jdatetime.datetime.now().strftime("%Y")
            this_month = jdatetime.datetime.now().strftime("%m")

            # Convert to integers for arithmetic operations
            this_year = int(this_year)
            this_month = int(this_month)

            # Calculate next month
            next_month = this_month + 1
            # next_month = this_month

            if next_month <= 12:
                start_gregorian_date = jdatetime.date(this_year, next_month, 1).togregorian()
                # Handle days in the month
                if next_month == 12:
                    # If next month is December, set end day to 29 (or 30 if applicable)
                    end_day = 29 if jdatetime.jdatetime.isleap(this_year) else 31
                else:
                    end_day = 31
                end_gregorian_date = jdatetime.date(this_year, next_month, end_day).togregorian()
            else:
                # If next month is January of next year
                start_gregorian_date = jdatetime.date(this_year + 1, 1, 1).togregorian()
                end_gregorian_date = jdatetime.date(this_year + 1, 1, 29).togregorian()  # Assuming 29 days in January

            # Filter menus for the current month
            menus_filter_this_month = Menu.objects.filter(date__range=[start_gregorian_date, end_gregorian_date]).order_by('date')


            menu_not = []
            for m in menus_filter_this_month:
                if not Reserve.objects.filter(menu=m, employee__user=user).exists():
                    menu_not.append(m)

            context = {
                'menu_not': menu_not,
                'user_reserved': user_reserved,
                'user_feedback': user_feedback,
                'menus': menus,
                'page': page,
                'today1': today1,
                'today2': today2,
                'today3': today3,
                'employe': employe,
                'reserves_total_price': reserves_total_price,
            }
            return render(request, 'index.html', context)
    except:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='general:login')
def food_reserve(request):
    try:
        if request.method == 'POST':
            menu_list = request.POST.getlist('menu')

            for i in menu_list:
                menu = re.split("@", i)[0]
                typee = re.split("@", i)[1]
                menu_select = get_object_or_404(Menu, pk=menu)
                user = get_object_or_404(User, username=request.user)
                employe = Employee.objects.get(user=request.user)

                if not Reserve.objects.filter(menu=menu_select, employee__user=user).exists():
                    if menu_select.date.strftime("%A") == 'پنج‌شنبه':
                        food_name = menu_select.type_1.name
                        Reserve.objects.create(menu=menu_select, type='1', employee=employe, date=jdatetime.datetime.now(),
                                               food_name=food_name)
                    else:
                        if typee == '1':
                            food_name = menu_select.type_1.name
                            Reserve.objects.create(menu=menu_select, type='1', employee=employe,
                                                   date=jdatetime.datetime.now(), food_name=food_name)
                        elif typee == '2':
                            food_name = menu_select.type_2.name
                            Reserve.objects.create(menu=menu_select, type='2', employee=employe,
                                                   date=jdatetime.datetime.now(), food_name=food_name)

                    # messages.success(request, "Thank you dear", 'success')
                else:
                    # messages.success(request, "Don't add !", 'danger')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    except:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='admin:login')
def food_define(request):
    try:
        menus = Menu.objects.all().order_by('-date')
        foods = Food.objects.all()

        context = {
            'menus': menus,
            'foods': foods,
        }
        return render(request, 'food-define.html', context)
    except:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='admin:login')
def add_menu(request):
    try:
        if request.method == 'POST':
            type1 = request.POST.get('type1')
            type2 = request.POST.get('type2')
            _date = request.POST.get('_date')
            _holiday = request.POST.get('_holiday')

            original_date = parser.parse(_date)
            original_date_ = original_date.strftime('%Y-%m-%d')

            if not Menu.objects.filter(date=original_date_).exists():
                if _holiday == 'on':
                    Menu.objects.create(date=original_date_, holiday=True)
                elif _holiday == None:
                    food1 = Food.objects.get(name=type1)
                    food2 = Food.objects.get(name=type2)
                    Menu.objects.create(type_1=food1, type_2=food2, date=original_date_)

                    messages.success(request, "Thank you dear", 'success')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
                else:
                    messages.success(request, "Don't add !", 'danger')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            else:
                # messages.success(request, "Don't add !", 'danger')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    except:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='admin:login')
def food_delivery(request):
    try:
        percentage_1 = ''
        percentage_2 = ''
        menu = Menu.objects.get(date=jdatetime.datetime.now())
        today1 = jdatetime.datetime.now().strftime("%A")
        today2 = jdatetime.datetime.now().strftime("%d %B %Y")
        reserves_1 = Reserve.objects.filter(type='1', menu__date=jdatetime.datetime.now()).count()
        reserves_1_serve = Reserve.objects.filter(type='1', serve=True, menu__date=jdatetime.datetime.now()).count()
        if reserves_1 > 0 and reserves_1_serve > 0:
            percentage_1 = get_percentage(reserves_1, reserves_1_serve)
        reserves_2 = Reserve.objects.filter(type='2', menu__date=jdatetime.datetime.now()).count()
        reserves_2_serve = Reserve.objects.filter(type='2', serve=True, menu__date=jdatetime.datetime.now()).count()
        if reserves_2 > 0 and reserves_2_serve > 0:
            percentage_2 = get_percentage(reserves_2, reserves_2_serve)

        context = {
            'menu': menu,
            'reserves_1': reserves_1,
            'reserves_1_serve': reserves_1_serve,
            'percentage_1': percentage_1,
            'reserves_2': reserves_2,
            'reserves_2_serve': reserves_2_serve,
            'percentage_2': percentage_2,
            'today1': today1,
            'today2': today2,
        }
        return render(request, 'food-delivery.html', context)
    except:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='admin:login')
def food_delivery_search(request):
    try:
        menus = Menu.objects.all()
        today1 = jdatetime.datetime.now().strftime("%A")
        today2 = jdatetime.datetime.now().strftime("%d %B %Y")

        context = {
            'menus': menus,
            'today1': today1,
            'today2': today2,
        }
        return render(request, 'food-delivery.html', context)
    except:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='admin:login')
def autocompleteModel(request):
    try:
        q = request.GET.get('user_code')
        today1 = jdatetime.datetime.now().strftime("%A")
        today2 = jdatetime.datetime.now().strftime("%d %B %Y")

        menu = Menu.objects.get(date=jdatetime.datetime.now())
        reserves_1 = Reserve.objects.filter(type='1', menu__date=jdatetime.datetime.now()).count()
        reserves_1_serve = Reserve.objects.filter(type='1', serve=True, menu__date=jdatetime.datetime.now()).count()
        percentage_1 = ''

        if reserves_1 > 0 and reserves_1_serve > 0:
            percentage_1 = get_percentage(reserves_1, reserves_1_serve)
        reserves_2 = Reserve.objects.filter(type='2', menu__date=jdatetime.datetime.now()).count()
        reserves_2_serve = Reserve.objects.filter(type='2', serve=True, menu__date=jdatetime.datetime.now()).count()
        percentage_2 = ''


        if reserves_2 > 0 and reserves_2_serve > 0:
            percentage_2 = get_percentage(reserves_2, reserves_2_serve)

        try:
            search_qs = Reserve.objects.get(Q(employee__fullname__icontains=q, menu__date=jdatetime.datetime.now()) | Q(employee__personal_code__icontains=q, menu__date=jdatetime.datetime.now()))

            context = {
                'search_qs': search_qs,
                'menu': menu,
                'today1': today1,
                'today2': today2,
                'reserves_1': reserves_1,
                'reserves_1_serve': reserves_1_serve,
                'percentage_1': percentage_1,
                'reserves_2': reserves_2,
                'reserves_2_serve': reserves_2_serve,
                'percentage_2': percentage_2,
            }
            return render(request, 'food-delivery.html', context)

        except:
            context = {
                'fail_search': q,
                'menu': menu,
                'today1': today1,
                'today2': today2,
                'reserves_1': reserves_1,
                'reserves_1_serve': reserves_1_serve,
                'percentage_1': percentage_1,
                'reserves_2': reserves_2,
                'reserves_2_serve': reserves_2_serve,
                'percentage_2': percentage_2,
            }
            return render(request, 'food-delivery.html', context)


    except:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='admin:login')
def delivery_control_all(request):
    try:
        employees = Employee.objects.all()
        reserves = Reserve.objects.filter(menu__date=jdatetime.datetime.now())
        one_week_ago = datetime.today() - timedelta(days=7)
        menus = Menu.objects.filter(date__gte=one_week_ago).order_by('date')
        today_menu = Menu.objects.get(date=jdatetime.datetime.now())

        reserves_1 = Reserve.objects.filter(type='1', menu__date=jdatetime.datetime.now()).count()
        reserves_1_serve = Reserve.objects.filter(type='1', serve=True, menu__date=jdatetime.datetime.now()).count()
        reserves_2 = Reserve.objects.filter(type='2', menu__date=jdatetime.datetime.now()).count()
        reserves_2_serve = Reserve.objects.filter(type='2', serve=True, menu__date=jdatetime.datetime.now()).count()

        today2 = jdatetime.datetime.now().strftime("%Y-%m-%d")  # '1399 01 05'

        context = {
            'employees': employees,
            'menus': menus,
            'today2': today2,
            'reserves': reserves,
            'today_menu': today_menu,
            'reserves_1': reserves_1,
            'reserves_1_serve': reserves_1_serve,
            'reserves_2': reserves_2,
            'reserves_2_serve': reserves_2_serve,
        }
        return render(request, 'delivery-control.html', context)
    except:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def delivery_control(request, fid):
    try:
        employees = Employee.objects.all()
        reserves = Reserve.objects.filter(menu__pk=fid)
        one_week_ago = datetime.today() - timedelta(days=7)
        menus = Menu.objects.filter(date__gte=one_week_ago)
        today_menu = Menu.objects.get(pk=fid)

        reserves_1 = Reserve.objects.filter(type='1', menu__pk=fid).count()
        reserves_1_serve = Reserve.objects.filter(type='1', serve=True, menu__pk=fid).count()
        reserves_2 = Reserve.objects.filter(type='2', menu__pk=fid).count()
        reserves_2_serve = Reserve.objects.filter(type='2', serve=True, menu__pk=fid).count()

        today2 = jdatetime.datetime.now().strftime("%Y-%m-%d")  # '1399 01 05'

        context = {
            'employees': employees,
            'menus': menus,
            'today2': today2,
            'reserves': reserves,
            'today_menu': today_menu,
            'reserves_1': reserves_1,
            'reserves_1_serve': reserves_1_serve,
            'reserves_2': reserves_2,
            'reserves_2_serve': reserves_2_serve,
        }
        return render(request, 'delivery-control.html', context)
    except:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='admin:login')
def delivery_control_filter(request):
    try:
        pid_user_code = request.GET.get('user_code')

        employees = Employee.objects.all()

        if pid_user_code.isdigit():
            employee = get_object_or_404(Employee, personal_code=pid_user_code)
            reserve = Reserve.objects.filter(employee=employee, menu__date=jdatetime.datetime.now())
            one_week_ago = datetime.today() - timedelta(days=7)
            menus = Menu.objects.filter(date__gte=one_week_ago)

            context = {
                'employees': employees,
                'employee': employee,
                'reserves': reserve,
                'menus': menus,
            }

            return render(request, 'delivery-control.html', context)

        else:
            employee = get_object_or_404(Employee, fullname__icontains=pid_user_code)
            reserve = Reserve.objects.filter(employee=employee, menu__date=jdatetime.datetime.now())
            one_week_ago = datetime.today() - timedelta(days=7)
            menus = Menu.objects.filter(date__gte=one_week_ago)

            context = {
                'employees': employees,
                'employee': employee,
                'reserves': reserve,
                'menus': menus,
            }

            return render(request, 'delivery-control.html', context)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    except:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='admin:login')
def delivery_control_serve(request):
    # try:
        if request.method == 'POST':
            user_code = request.POST.get('user_code')
            menu_code = request.POST.get('menu_code')
            menu = get_object_or_404(Menu, pk=menu_code)
            if Reserve.objects.filter(employee__personal_code=user_code, menu=menu, transfer=False, serve=False):
                Reserve.objects.filter(employee__personal_code=user_code, menu=menu).update(serve=True)
            elif Reserve.objects.filter(employee__personal_code=user_code, menu=menu, transfer=False, serve=True):
                Reserve.objects.filter(employee__personal_code=user_code, menu=menu).update(serve=False)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    # except:
    #     return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='admin:login')
def delivery_control_transfer(request):
    # try:
        if request.method == 'POST':
            user_code_of = request.POST.get('user_code_of')
            user_code_to = request.POST.get('user_code_to')

            employee_to = get_object_or_404(Employee, personal_code=user_code_to)

            if not Reserve.objects.filter(employee__personal_code=user_code_to, menu__date=jdatetime.datetime.now()).exists():
                reserve = Reserve.objects.get(employee__personal_code=user_code_of, menu__date=jdatetime.datetime.now())
                Reserve.objects.create(menu=reserve.menu, type=reserve.type, employee=employee_to, date=jdatetime.datetime.now(), food_name=reserve.food_name, serve=True)
                Reserve.objects.filter(employee__personal_code=user_code_of, menu__date=jdatetime.datetime.now()).update(transfer=True, transfer_to=employee_to)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    # except:
    #     return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='admin:login')
def delivery_user_info(request):
    try:
        employees = Employee.objects.all()
        # reserves = Reserve.objects.all()

        # Get the current Gregorian date
        current_gregorian_date = datetime.now().date()

        # # Convert the current date to Gregorian
        # current_date = jdatetime.date.fromgregorian(date=current_gregorian_date)

        # Get the current month and year using jdatetime
        current_day = current_gregorian_date.day
        current_month = current_gregorian_date.month
        current_year = current_gregorian_date.year

        # Filter reserves for the current month
        reserves = Reserve.objects.filter(menu__date__day=current_day, menu__date__month=current_month, menu__date__year=current_year)

        serve_count = Reserve.objects.filter(serve=True).count()
        deserve_count = Reserve.objects.filter(serve=False).count()
        transfer_count = Reserve.objects.values('transfer_to').order_by('transfer_to').annotate(the_count=Count('transfer_to')).count()

        context = {
            'employees': employees,
            'reserves': reserves,
            'serve_count': serve_count,
            'deserve_count': deserve_count,
            'transfer_count': transfer_count,
        }
        return render(request, 'food-userinfo.html', context)
    except:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='admin:login')
def delivery_user_info_filter(request):
    try:
        pid_user = request.GET.get('user')
        pid_month = request.GET.get('month')

        employees = Employee.objects.all()

        if pid_user:
            employee = get_object_or_404(Employee, pk=pid_user)
            reserve = Reserve.objects.filter(employee=employee)

            serve_count = Reserve.objects.filter(employee=employee, serve=True).count()
            deserve_count = Reserve.objects.filter(employee=employee, serve=False).count()


            context = {
                'employees': employees,
                'employee': employee,
                'reserves': reserve,
                'serve_count': serve_count,
                'deserve_count': deserve_count,
            }

            return render(request, 'food-userinfo.html', context)

        elif pid_month:
            this_year = jdatetime.datetime.now().strftime("%Y")
            gregorian_date = jdatetime.date(int(this_year), int(pid_month), 1).togregorian()
            filter_monthe_gregorian = gregorian_date.month

            reserve = Reserve.objects.filter(menu__date__month=filter_monthe_gregorian)

            context = {
                'employees': employees,
                'reserves': reserve,
            }

            return render(request, 'food-userinfo.html', context)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    except:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


##############

def get_percentage(total_count, cnt):
    perc = cnt * 100 / total_count
    return perc


# Create your pdf here.
@login_required(login_url='admin:login')
def pdf(request, mid):
    try:
        if request.user.is_superuser:
            this_year = jdatetime.datetime.now().strftime("%Y")

            if int(mid) <= 12:
                start_gregorian_date = jdatetime.date(int(this_year), int(mid), 1).togregorian()
                # Handle days in the month
                if int(mid) == 12:
                    # If next month is December, set end day to 29 (or 30 if applicable)
                    end_gregorian_date = jdatetime.date(int(this_year), int(mid), 29).togregorian() 
                else:
                    end_gregorian_date = jdatetime.date(int(this_year), int(mid), 31).togregorian()
                # end_gregorian_date = jdatetime.date(this_year, next_month, end_day).togregorian()
            else:
                # If next month is January of next year
                start_gregorian_date = jdatetime.date(this_year + 1, 1, 1).togregorian()
                end_gregorian_date = jdatetime.date(this_year + 1, 1, 29).togregorian()  # Assuming 29 days in January


            
            # end_gregorian_date = jdatetime.date(int(this_year), int(mid), 30).togregorian()
            # filter_monthe_gregorian = gregorian_date.month

            menus = Menu.objects.filter(date__range=[start_gregorian_date, end_gregorian_date]).order_by('date')

            month = []


            for menu in menus:
                day = {}
                day_menu = menu.date
                day['day'] = str(day_menu)
                menu_food_1 = menu.type_1
                day['food1'] = str(menu_food_1)
                reserve_1 = Reserve.objects.filter(menu=menu, type='1').count()
                day['reserve1'] = str(reserve_1)
                menu_food_2 = menu.type_2
                day['food2'] = str(menu_food_2)
                reserve_2 = Reserve.objects.filter(menu=menu, type='2').count()
                day['reserve2'] = str(reserve_2)

                month.append(day)

                # month['day'+str(menu.id)] = day

            context = {'month': month}

            # return render(request, 'pdf/index.html', {'month': json.dumps(month)})
            return render(request, 'pdf/index.html', context)
    except:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='admin:login')
def internal(request, pid, uid):
    try:
        if request.user.is_superuser:
            reserves_total_price = ''
            employee = get_object_or_404(Employee, pk=pid)
            this_year = jdatetime.datetime.now().strftime("%Y")
            # this_month = jdatetime.datetime.now().strftime("%m")
            # start_gregorian_date = jdatetime.date(int(this_year), int(uid), 1).togregorian()
            # end_gregorian_date = jdatetime.date(int(this_year), int(uid), 30).togregorian()
            if int(uid) <= 12:
                start_gregorian_date = jdatetime.date(int(this_year), int(uid), 1).togregorian()
                # Handle days in the month
                if int(uid) == 12:
                    # If next month is December, set end day to 29 (or 30 if applicable)
                    end_gregorian_date = jdatetime.date(int(this_year), int(uid), 29).togregorian() 
                else:
                    end_gregorian_date = jdatetime.date(int(this_year), int(uid), 31).togregorian()
                # end_gregorian_date = jdatetime.date(this_year, next_month, end_day).togregorian()
            else:
                # If next month is January of next year
                start_gregorian_date = jdatetime.date(this_year + 1, 1, 1).togregorian()
                end_gregorian_date = jdatetime.date(this_year + 1, 1, 29).togregorian()  # Assuming 29 days in January

            reserves = Reserve.objects.filter(employee__pk=pid, menu__date__range=[start_gregorian_date, end_gregorian_date], serve=True).order_by('employee__fullname')
            reserves_sum = Reserve.objects.filter(employee__pk=pid, menu__date__range=[start_gregorian_date, end_gregorian_date], serve=True).order_by('employee__fullname').count()
            reserves_nights = Reserve.objects.filter(employee__pk=pid, menu__date__range=[start_gregorian_date, end_gregorian_date], night=True).order_by('employee__fullname').count()

            if employee.type == '1':
                reserves_total_price = (reserves_sum + reserves_nights) * int(employee.price)
            elif employee.type == '2':
                reserves_total_price = (reserves_sum + reserves_nights) * int(employee.price)

            context = {
                'reserves': reserves,
                'reserves_sum': reserves_sum,
                'reserves_nights': reserves_nights,
                'reserves_total_price': reserves_total_price,
            }

            return render(request, 'pdf/index2.html', context)
        else:
            raise Http404("شما مجاز به دسترسی به این صفحه نیستید")
    except:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='general:login')
def done_popup(request):
    if request.method == 'GET':
        Employee.objects.filter(user=request.user).update(popup=True)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='general:login')
def feedback_reserve(request):
    try:
        if request.method == 'POST':
            user_rate = request.POST.get('rating')
            user_comment = request.POST.get('comments')


            # Filter reservations from today
            employe = Employee.objects.get(user=request.user)
            user_reserve = Reserve.objects.get(employee=employe, menu__date=jdatetime.datetime.now())

            # Check if feedback already exists for the reservation
            existing_feedback = Feedback.objects.filter(reserve=user_reserve).exists()

            # Create feedback if a reservation exists for today
            if user_reserve and not existing_feedback:
                Feedback.objects.create(reserve=user_reserve, rate=user_rate, comment=user_comment)

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    except:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='admin:login')
def feedback_reserve_list(request):
    try:
        employees = Employee.objects.all()
        feedback = Feedback.objects.filter(reserve__menu__date=jdatetime.datetime.now())
        reserves = Reserve.objects.filter(menu__date=jdatetime.datetime.now())
        one_week_ago = datetime.today() - timedelta(days=7)
        menus = Menu.objects.filter(date__gte=one_week_ago).order_by('date')
        today_menu = Menu.objects.get(date=jdatetime.datetime.now())

        reserves_1 = Reserve.objects.filter(type='1', menu__date=jdatetime.datetime.now()).count()
        reserves_1_serve = Reserve.objects.filter(type='1', serve=True, menu__date=jdatetime.datetime.now()).count()
        reserves_2 = Reserve.objects.filter(type='2', menu__date=jdatetime.datetime.now()).count()
        reserves_2_serve = Reserve.objects.filter(type='2', serve=True, menu__date=jdatetime.datetime.now()).count()

        today2 = jdatetime.datetime.now().strftime("%Y-%m-%d")  # '1399 01 05'

        context = {
            'employees': employees,
            'feedback': feedback,
            'menus': menus,
            'today2': today2,
            'reserves': reserves,
            'today_menu': today_menu,
            'reserves_1': reserves_1,
            'reserves_1_serve': reserves_1_serve,
            'reserves_2': reserves_2,
            'reserves_2_serve': reserves_2_serve,
        }
        return render(request, 'feedback-list.html', context)
    except:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def feedback_day(request, feedid):
    # try:
        employees = Employee.objects.all()
        feedback = Feedback.objects.filter(reserve__menu__date=feedid)
        one_week_ago = datetime.today() - timedelta(days=7)
        menus = Menu.objects.filter(date__gte=one_week_ago)
        today_menu = Menu.objects.get(date=feedid)
        #
        # reserves_1 = Reserve.objects.filter(type='1', menu__pk=fid).count()
        # reserves_1_serve = Reserve.objects.filter(type='1', serve=True, menu__pk=fid).count()
        # reserves_2 = Reserve.objects.filter(type='2', menu__pk=fid).count()
        # reserves_2_serve = Reserve.objects.filter(type='2', serve=True, menu__pk=fid).count()

        today2 = jdatetime.datetime.now().strftime("%Y-%m-%d")  # '1399 01 05'

        context = {
            'employees': employees,
            'feedback': feedback,
            'menus': menus,
            'today_menu': today_menu,
        }
        return render(request, 'feedback-list.html', context)
    # except:
    #     return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))