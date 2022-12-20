from django.urls import path

from . import views

app_name = "webui"

urlpatterns = [
    path("", views.hello_chess_board),
]
