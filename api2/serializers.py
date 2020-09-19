from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api2.models import Budget, Transaction


class BudgetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        max_length=20, validators=[UniqueValidator(queryset=Budget.objects.all())]
    )
    percentage = serializers.IntegerField(max_value=100)
    initial_balance = serializers.IntegerField(required=False)
    balance = serializers.SerializerMethodField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(many=False, queryset=User.objects.all())

    class Meta:
        model = Budget
        fields = "__all__"

    def get_balance(self, obj):
        return obj.balance()


class TransactionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    amount = serializers.IntegerField(
        max_value=Transaction.MAX_TRANSACTION_SUPPORTED,
        min_value=Transaction.MIN_TRANSACTION_SUPPORTED,
    )
    description = serializers.CharField(max_length=300)
    budget = serializers.PrimaryKeyRelatedField(
        many=False, queryset=Budget.objects.all()
    )
    date = serializers.DateField()

    class Meta:
        model = Transaction
        fields = "__all__"


class AddMoneySerializer(serializers.Serializer):
    amount = serializers.IntegerField(max_value=Transaction.MAX_TRANSACTION_SUPPORTED, min_value=Transaction.MIN_TRANSACTION_SUPPORTED)
    description = serializers.CharField(max_length=300)
    date = serializers.DateField()


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20, min_length=3, required=True)
    password = serializers.CharField(max_length=20, min_length=3, required=True)

    class Meta:
        model = User
        fields = ["username", "password"]

    def validate_username(self, value):
        # we shouldn't create duplicate users with this
        if len(User.objects.filter(username=value)) != 0:
            raise serializers.ValidationError("user already exists")
