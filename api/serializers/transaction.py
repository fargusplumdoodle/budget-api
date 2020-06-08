from rest_framework import serializers

from web.models import Transaction


class TransactionSerialzer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.FloatField(max_value=4000)
    description = serializers.CharField(max_length=300, allow_null=True, allow_blank=True)
    budget = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    date = serializers.DateField()

    class Meta:
        model = Transaction
        fields = '__all__'
