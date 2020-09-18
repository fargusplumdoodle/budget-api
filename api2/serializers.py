from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api2.models import Budget, Transaction


class BudgetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        max_length=20, validators=[UniqueValidator(queryset=Budget.objects.all())]
    )
    percentage = serializers.FloatField(max_value=100)
    initial_balance = serializers.FloatField(required=False)
    balance = serializers.SerializerMethodField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(many=False, queryset=User.objects.all())

    class Meta:
        model = Budget
        fields = "__all__"

    def get_balance(self, obj):
        return obj.balance()


class TransactionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    amount = serializers.IntegerField(max_value=4000)
    description = serializers.CharField(max_length=300)
    budget = serializers.PrimaryKeyRelatedField(
        many=False, queryset=Budget.objects.all()
    )
    date = serializers.DateField()

    class Meta:
        model = Transaction
        fields = "__all__"


class AddMoneySerializer(serializers.Serializer):
    amount = serializers.IntegerField()
