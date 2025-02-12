from django.apps import AppConfig


class LichessBridgeConfig(AppConfig):
    name = "apps.lichess_bridge"

    def ready(self):
        from .svg_icons import register_app_icons

        register_app_icons()
