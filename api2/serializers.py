from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from api2.constants import DefaultTags, ROOT_BUDGET_NAME
from api2.models import Budget, Transaction, Tag, UserInfo


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"

    def update(self, instance, validated_data):
        if instance.name in DefaultTags.values():
            raise ValidationError("You cannot update default tags")

        return super().update(instance, validated_data)


class BudgetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        max_length=20, validators=[UniqueValidator(queryset=Budget.objects.all())]
    )
    balance = serializers.SerializerMethodField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        many=False, queryset=User.objects.all(), required=False
    )

    class Meta:
        model = Budget
        fields = "__all__"

    def get_balance(self, obj):
        return obj.balance()

    def update(self, instance, validated_data):
        if instance.name == ROOT_BUDGET_NAME:
            raise ValidationError("You cannot update root budget")

        return super().update(instance, validated_data)


class TransactionTagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=30)
    id = serializers.IntegerField(read_only=True)
    rank = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tag
        exclude = ("user",)


class TransactionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    amount = serializers.IntegerField(
        max_value=Transaction.MAX_TRANSACTION_SUPPORTED,
        min_value=Transaction.MIN_TRANSACTION_SUPPORTED,
    )
    description = serializers.CharField(max_length=300, allow_blank=True)
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

        if budget.is_node:
            raise ValidationError("You cannot assign a transaction to a node budget")

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


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        exclude = ["id", "user"]
