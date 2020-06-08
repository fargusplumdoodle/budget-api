import io

from rest_framework import parsers, renderers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.compat import coreapi, coreschema
from rest_framework.schemas import ManualSchema
from rest_framework.authtoken.models import Token
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.budget import BudgetSerializer
from web.models import Budget


class BudgetView(APIView):
    authentication_classes = [BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    """
    
    For performing CRUD operations on budgets 
    
    """

    def get(self, request):
        """
        Returns all budgets and their values according to the
        budget serializer
        """
        budgets = Budget.objects.all()

        serializer = BudgetSerializer(budgets, many=True)

        return Response(serializer.data, status=200, content_type="application/json")
