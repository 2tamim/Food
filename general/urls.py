from django.urls import path, include, re_path
from .views import *


app_name = 'general'

urlpatterns = [
    path('', dashboard, name='home'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('password/', change_password, name='change_password'),

    #add_food
    path('food/add/user/', food_reserve, name='food-add'),
    path('food/add/all/', food_define, name='food-add-all'),
    path('food/delivery/', food_delivery, name='food-delivery'),
    path('food/delivery/search/', autocompleteModel, name='search'),
    path('food/delivery/control/today/', delivery_control_all, name='delivery-control-all'),
    path('food/delivery/control/day/<str:fid>/', delivery_control, name='delivery-control'),
    path('food/delivery/control/filter/', delivery_control_filter, name='delivery-control-filter'),
    path('food/delivery/control/serve/', delivery_control_serve, name='delivery-control-serve'),
    path('food/delivery/control/transfer/', delivery_control_transfer, name='delivery-control-transfer'),
    path('food/user/info/', delivery_user_info, name='delivery-userinfo'),
    path('food/user/info/filter/', delivery_user_info_filter, name='delivery-userinfo-filter'),
    path('food/menu/add/', add_menu, name='menu-add'),
    path('food/list/pdf/<str:mid>/', pdf, name='month-info'),
    path('food/list/pdf/internal/<str:pid>/<str:uid>/', internal, name='user-info'),

    #
    path('popup/', done_popup, name='popup'),
    path('feedback/', feedback_reserve, name='feedback'),
    path('feedback/list/', feedback_reserve_list, name='feedback-list'),
    path('feedback/day/<str:feedid>/', feedback_day, name='feedback-day'),
]
