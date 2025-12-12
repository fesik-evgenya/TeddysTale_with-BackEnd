from django.apps import AppConfig


class TeddyAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'teddy_admin'
    verbose_name = 'Администрирование'

    def ready(self):
        import teddy_admin.signals
