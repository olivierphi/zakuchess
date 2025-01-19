from django.apps import AppConfig


class WebUIAppConfig(AppConfig):
    name = "apps.webui"

    def ready(self):
        # TODO: Django 5.2: remove this ugly monkey-patching when Django 5.2's
        #  built-in `simple_block_tag`is released

        from django import template

        from .template_django_extensions import simple_block_tag

        # Monkey-patch `register` to add `simple_block_tag` method
        template.Library.simple_block_tag = simple_block_tag
