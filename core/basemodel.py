__author__ = 'xwl'

import uuid
from django.db import models


def _unique():
    return uuid.uuid4().hex


class PrimaryKeyModel(models.Model):
    class Meta:
        abstract = True

    id = models.CharField(db_column='c_id', primary_key=True,
                          default=_unique, max_length=32, editable=False)


class Serializable(object):
    class FieldNotFound(Exception):
        pass

    def serialize(self, fields=[]):
        if not fields:
            fields = [f.name for f in self._meta.get_fields()
                      if not (f.auto_created or
                              f.many_to_many or
                              f.many_to_one)]
        # print fields
        allowed = set(fields) - set(getattr(self, '_api_hidden_fields', []))
        grouped = {}
        for field in allowed:
            if '.' not in field:
                grouped[field] = False
                continue
            k, v = field.split('.', 1)
            grouped.setdefault(k, []).append(v)

        d = {}
        for field, keys in grouped.items():
            d[field] = self.get_value(field, keys)
        return d

    def get_value(self, name, keypath):
        if keypath:
            field = self._meta.get_field(name)
            if field.many_to_one:
                return getattr(self, field.name).serialize(keypath)
            if field.many_to_many:
                return [val.serialize(keypath) for val in
                        getattr(self, field.name).all()]
            raise Serializable.FieldNotFound(
                "%s is not a relation field." % name)
        else:
            field = self._meta.get_field(name)
            return getattr(self, field.name)