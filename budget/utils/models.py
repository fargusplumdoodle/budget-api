from enum import Enum

from django.db.models import CharField


class ChoiceEnum(Enum):
    """
    For use with Django fields. Allows you to define a class with a given
    set of values, then associate a field on a model/filter/serializer with
    those set of values.
    """

    @classmethod
    def choices(cls):
        return tuple((x.value, x.name) for x in cls)

    @classmethod
    def max_length(cls):
        return max(len(str(x.value)) for x in cls)

    @classmethod
    def values(cls):
        return tuple(x.value for x in cls)

    @classmethod
    def char_field(cls, *args, **kwargs):
        return CharField(
            choices=cls.choices(),
            max_length=cls.max_length(),
            *args,
            **kwargs,
        )
