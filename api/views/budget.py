from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.budget import BudgetSerializer
from api.models import Budget, Transaction
from api.serializers.transaction import TransactionSerialzer


class BudgetView(APIView):
    authentication_classes = [BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    """
    
    For performing CRUD operations on budgets 
    ------------------------------------------
    
    At this moment, I want to prevent any potential
    destructive actions. Therefor I have chosen not
    to allow the modification of budgets through the API.
    
    That can be done in the admin interface... just to be safe
    
    """

    def get(self, request):
        """
        Returns all budgets and their values according to the
        budget serializer
        example:
        [
            {
                "id": 1,
                "name": "housing",
                "percentage": 0.3257300697,
                "initial_balance": 0.0,
                "balance": "0.00"
            },
            {
                "id": 2,
                "name": "food",
                "percentage": 0.1954380418,
                "initial_balance": 0.0,
                "balance": "0.00"
            }
        ]
        """
        budgets = Budget.objects.all()

        serializer = BudgetSerializer(budgets, many=True)

        return Response(serializer.data, status=200, content_type="application/json")


class BudgetTransactionView(APIView):
    authentication_classes = [BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    """
    For viewing transactions on a specific budget
    """

    def get(self, request, budget_id):
        """
        QUERY PARAM: <max: int> the maximum number of transactions to return
            -> if it isnt included it will default to 10

        Getting all
        [
            {
                "id": 1,
                "amount": 3.2573006970000002,
                "description": "add_money: Total amount added 10.00",
                "budget": 1,
                "date": "2021-03-15"
            }
        ]

        :param budget_id:
        """
        try:
            max = int(request.GET['max'])
        except:
            return Response({'error': 'query parameter "max" invalid, must be an int'}, status=400, content_type="application/json")

        trans = Transaction.objects.filter(
            budget_id=budget_id,
        ).order_by('-date')[:max]

        serializer = TransactionSerialzer(trans, many=True)

        return Response(serializer.data, status=200, content_type="application/json")
