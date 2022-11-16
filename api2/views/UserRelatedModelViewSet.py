from typing import Type

from django.db.models import Model
from rest_framework.viewsets import ModelViewSet


class UserRelatedModelViewSet(ModelViewSet):
    model: Type[Model]

    def create(self, request, *args, **kwargs):
        request.data.update({**request.data, "user": request.user.pk})
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        request.data.update({**request.data, "user": request.user.pk})
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

