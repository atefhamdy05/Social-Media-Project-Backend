from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='api_post_list'),
    path('<str:id>/', views.post_detail, name='api_post_detail'),
]
