from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheck(APIView):
    @staticmethod
    def get(request: Request):
        return Response(status=200)
