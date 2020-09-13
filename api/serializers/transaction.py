from rest_framework import serializers

from api.models import Transaction, Budget


class TransactionSerialzer(serializers.ModelSerializer):
    amount = serializers.FloatField(max_value=4000)
    description = serializers.CharField(max_length=300, allow_null=True, allow_blank=True)
    budget = serializers.PrimaryKeyRelatedField(many=False, queryset=Budget.objects.all())
    date = serializers.DateField()

    class Meta:
        model = Transaction
        fields = '__all__'

class AddMoneySerializer(serializers.Serializer):
    amount = serializers.FloatField(max_value=4000)
