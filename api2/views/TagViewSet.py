from rest_framework.permissions import IsAuthenticated

from ..filters import TagFilterset
from ..models import Tag
from ..serializers import TagSerializer
from .UserRelatedModelViewSet import UserRelatedModelViewSet


class TagViewset(UserRelatedModelViewSet):
    model = Tag
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TagFilterset

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)
