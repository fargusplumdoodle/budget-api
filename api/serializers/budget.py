from api.models import Transaction, Budget
from rest_framework import serializers
from django.contrib.auth.models import User


class TransactionSerialzer(serializers.ModelSerializer):
    amount = serializers.IntegerField(max_value=40000)
    description = serializers.CharField(max_length=300)
    budget = serializers.PrimaryKeyRelatedField(
        many=False, queryset=Budget.objects.all()
    )
    date = serializers.DateField()

    class Meta:
        model = Transaction
        fields = "__all__"


class AddMoneySerializer(serializers.Serializer):
    amount = serializers.IntegerField(max_value=40000)


class BudgetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=20)
    percentage = serializers.IntegerField(max_value=100, min_value=0)
    initial_balance = serializers.IntegerField(required=False, default=0)
    balance = serializers.SerializerMethodField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        many=False, queryset=User.objects.all()
    )

    class Meta:
        model = Budget
        fields = "__all__"

    @staticmethod
    def get_balance(obj):
        return obj.balance()
