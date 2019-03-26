from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_flight_task, name='index'),
    path('get_airline_preview', views.get_airline_preview, name='get_airline_preview'),
    path('add_flight_task', views.add_flight_task, name='add_flight_task'),
    path('del_flight_task', views.del_flight_task, name='del_flight_task'),

    path('goods_task', views.view_goods_task, name='goods_task'),
    path('get_ebook_preview', views.get_ebook_preview, name='get_ebook_preview'),
    path('add_goods_task', views.add_goods_task, name='add_goods_task'),
    path('edit_goods_task', views.edit_goods_task, name='edit_goods_task'),
    path('del_goods_task', views.del_goods_task, name='del_goods_task'),
    path('get_goods_task_info', views.get_goods_task_info, name='get_goods_task_info'),

    path('register/', views.register, name='register'),
    path('setting/', views.setting, name='setting'),
    path('start_schedule', views.start_schedule, name='start_schedule'),
    path('stop_schedule', views.stop_schedule, name='stop_schedule'),
    # path('export/<int:clipping_id>', views.export_clipping, name='export'),
]