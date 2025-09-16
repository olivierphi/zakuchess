from __future__ import annotations

from django.urls import path

from . import views

app_name = "webui"
urlpatterns = [
    path("", views.home_page, name="home_page"),
]
