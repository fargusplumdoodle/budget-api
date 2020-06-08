from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from api.serializers.budget import BudgetSerializer
from web.models import Budget, Transaction
import io
from api.serializers.transaction import TransactionSerialzer


class AddTransactionView(APIView):
    authentication_classes = [BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    """
    For adding a transaction

    """

    def post(self, request):
        """
        Creates a transaction
        """
        stream = io.BytesIO(request.body)
        data = JSONParser().parse(stream)
        serializer = TransactionSerialzer(data=data, many=False)

        if serializer.is_valid():
            Transaction.objects.create(
                amount=serializer.validated_data['amount'],
                description=serializer.validated_data['description'],
                budget=serializer.validated_data['budget'],
                date=serializer.validated_data['date'],
            )
            serializer.save()

            return Response(status=201, content_type="application/json")
        else:
            return Response(serializer.errors, status=400, content_type="application/json")
