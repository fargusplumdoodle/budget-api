import io

from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import UserInfo
from ..serializers import TagSerializer, UserInfoSerializer


class UserInfoView(APIView):
    model = UserInfo
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        info, _ = self.model.objects.get_or_create(user=request.user)
        return Response(data=UserInfoSerializer(info).data, status=200)

    def put(self, request: Request):
        info, _ = self.model.objects.get_or_create(user=request.user)

        stream = io.BytesIO(request.body)
        data = JSONParser().parse(stream)

        serializer = UserInfoSerializer(info, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data, status=201)
