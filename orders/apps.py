from django.apps import AppConfig

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        import orders.signals  # Importa el archivo de señales de tu aplicación
        from orders.signals import show_me_the_money  # Importa la señal específica