from django.apps import AppConfig

class DatasetManagerConfig(AppConfig):
    name = 'dataset_manager'
    ready_run = False

    def ready(self):
        if self.ready_run:
            return
        self.ready_run = True

        # Import signals
        import dataset_manager.signals
