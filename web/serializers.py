from rest_framework import serializers

from api.models import Budget, Transaction


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
