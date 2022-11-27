from django.urls import path

from . import views

urlpatterns = [path("", views.hello_chess_board)]
