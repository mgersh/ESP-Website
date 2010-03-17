from django.db.models import ForeignKey, Field
from django.conf import settings
from esp.db.forms import AjaxForeignKeyNewformField


class AjaxForeignKey(ForeignKey):

    def __init__(self, *args, **kwargs):
        if 'queryset' in kwargs:
            self.queryset = kwargs['queryset']
        else:
            self.queryset = None

        ForeignKey.__init__(self, *args, **kwargs)


    def get_newform_field(self):
        return AjaxForeignKeyNewformField(field=self)

    def formfield(self, **kwargs):
        defaults = {'form_class': AjaxForeignKeyNewformField,
                    'field': self}
        
        defaults.update(kwargs)
        return super(AjaxForeignKey, self).formfield(**defaults)

    def south_field_triple(self):
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.related.ForeignKey"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)
