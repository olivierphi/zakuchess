"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path, register_converter

from apps.chess.url_converters import ChessSquareConverter

register_converter(ChessSquareConverter, "square")

urlpatterns = [
    path("", include("apps.webui.urls")),
    path("", include("apps.daily_challenge.urls")),
    path("lichess/", include("apps.lichess_bridge.urls")),
    path("-/", include("django_alive.urls")),
    path("admin/", admin.site.urls),
]
