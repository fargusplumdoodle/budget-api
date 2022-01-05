from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from api2.models import Budget, Transaction, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        exclude = ("rank",)


class BudgetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        max_length=20, validators=[UniqueValidator(queryset=Budget.objects.all())]
    )
    percentage = serializers.IntegerField(max_value=100)
    initial_balance = serializers.IntegerField(required=False)
    balance = serializers.SerializerMethodField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        many=False, queryset=User.objects.all(), required=False
    )

    class Meta:
        model = Budget
        fields = "__all__"

    def get_balance(self, obj):
        return obj.balance()


class TransactionTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["name"]


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
    income = serializers.BooleanField(required=False, default=False)
    transfer = serializers.BooleanField(required=False, default=False)
    tags = TransactionTagSerializer(many=True)

    class Meta:
        model = Transaction
        fields = "__all__"

    def validate(self, attrs):
        budget = attrs.get("budget")
        for tag in attrs["tags"]:
            if (
                not Tag.objects.filter(name=tag.get("name"), user=budget.user).count()
                == 1
            ):
                raise ValidationError(
                    f"Tag '{tag.get('name')}' does not exist for user {budget.user.username}"
                )
        return attrs

    @staticmethod
    def set_tags(instance, tags_json):
        if not tags_json:
            return instance

        tags = [
            Tag.objects.get(name=tag.get("name"), user=instance.budget.user)
            for tag in tags_json
        ]
        instance.tags.set(tags)
        return instance

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance = self.set_tags(instance, tags)
        instance.save()
        return instance

    def create(self, validated_data):
        tag_names = validated_data.pop("tags", None)

        trans = self.Meta.model.objects.create(**validated_data)

        trans = self.set_tags(trans, tag_names)
        trans.save()
        return trans


class AddMoneySerializer(serializers.Serializer):
    amount = serializers.IntegerField(
        max_value=Transaction.MAX_TRANSACTION_SUPPORTED,
        min_value=Transaction.MIN_TRANSACTION_SUPPORTED,
    )
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
