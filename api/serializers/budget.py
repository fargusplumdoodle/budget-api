from rest_framework import serializers

from api.models import Budget


class BudgetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=20)
    percentage = serializers.FloatField(max_value=100)
    initial_balance = serializers.FloatField(required=False)

    balance = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Budget
        fields = '__all__'

    def get_balance(self, obj):
        return obj.balance()
