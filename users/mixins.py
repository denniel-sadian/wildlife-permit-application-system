from django.urls import reverse_lazy


class ModelMixin:

    @property
    def admin_url(self):
        path = f'admin:{self._meta.app_label}_{self._meta.model_name}_change'
        return reverse_lazy(path, args=[self.id])
