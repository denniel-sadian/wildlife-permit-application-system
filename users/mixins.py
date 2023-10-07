from django.urls import reverse_lazy


class ModelMixin:

    @property
    def subclass(self):
        """Return the model subclass instance."""
        try:
            return self._subclass
        except AttributeError:
            self._subclass = self.__class__.objects.get_subclass(id=self.id)
        return self._subclass

    @property
    def type(self):
        """Return the type."""
        return self.subclass.__class__.__name__

    @property
    def admin_url(self):
        path = f'admin:{self._meta.app_label}_{self._meta.model_name}_change'
        return reverse_lazy(path, args=[self.id])
