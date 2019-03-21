from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_flight_task, name='index'),
    path('goods_task', views.view_goods_task, name='goods_task'),
    path('get_airline_preview', views.get_airline_preview, name='get_airline_preview'),
    path('get_ebook_preview', views.get_ebook_preview, name='get_ebook_preview'),
    path('start_schedule', views.start_schedule, name='start_schedule'),
    path('stop_schedule', views.stop_schedule, name='stop_schedule'),
    # path('export/<int:clipping_id>', views.export_clipping, name='export'),
]