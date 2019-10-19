from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render
import json


from .serializers import CategorySerializer, TransactionSerializer
from .models import Category, Transaction

def test_budget_is_balanced(request):
    """
    POST  apit/v1/check_balanced
    :param request:
    :return:
    """

    data = json.loads(request.body)

    return Response(data=data, status=200)


class CategoryView(APIView):
    def post(self, request):
        """
        Sets all the budgets
        Input:
            {
                'categories': [category objects]
            }
        """
        # 0. validation, could be better
        try:
            data = json.loads(request.body)

            # validation
            if 'categories' not in data:
                return Response(status=400)
            if not isinstance(data['categories'], list):
                return Response(status=400)
        except:
            return Response(status=400)

        # 2. Doing a little bit more checking
        valid_data = []
        for category in data['categories']:

            serial = CategorySerializer(data=category, many=False)

            if serial.is_valid():
                valid_data.append(serial)
            else:
                return Response(status=400)

        # saving data if its valid
        for serial in valid_data:
            serial.save()

        return Response(status=201)

    def get(self, request):
        """
        Returns everything, what is security
        """
        return Response(CategorySerializer(Category.objects.all(), many=True).data, status=200)


def get_budget_summary(request):
    # api/v1/summary

    # 1. getting data and serializidng
    data = Category.objects.all()

    serial = CategorySerializer(data=data, many=True)

    return Response(serial.data, status=200)



def dashboard(request):
    context = {}

    context['categories'] = Category.objects.all()

    return render(request, 'api/index.html', context=context)
