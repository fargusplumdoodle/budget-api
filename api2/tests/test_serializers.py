from api2.serializers import TransactionSerializer
from budget.utils.test import BudgetTestCase


class TransactionSerializerTestCase(BudgetTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.budget = cls.generate_budget()

    def setUp(self):
        self.trans = self.generate_transaction(self.budget)

    def get_list_of_tag_names(self):
        """Returns a list of tag objects that only contain names"""
        tags = []
        for _ in range(3):
            tag = self.generate_tag()
            tags.append({"name": tag.name})
        return tags

    def test_create_tags(self):
        tags = self.get_list_of_tag_names()
        trans_data = TransactionSerializer(self.trans, many=False).data
        trans_data["tags"] = tags

        serializer = TransactionSerializer(data=trans_data, many=False)
        self.assertTrue(serializer.is_valid())
        created_transaction = serializer.save()

        self.assertEqual(created_transaction.tags.all().count(), 3)
        for tag in tags:
            self.assertTrue(created_transaction.tags.filter(name=tag["name"]).exists())

    def test_tag_doesnt_exist(self):
        trans_data = TransactionSerializer(self.trans, many=False).data
        trans_data["tags"] = [{"name": "this certainly does not exist"}]
        serializer = TransactionSerializer(data=trans_data, many=False)
        self.assertFalse(serializer.is_valid())

        tag_for_other_user = self.generate_tag(user=self.generate_user())
        trans_data = TransactionSerializer(self.trans, many=False).data
        trans_data["tags"] = [{"name": tag_for_other_user.name}]
        serializer = TransactionSerializer(data=trans_data, many=False)
        self.assertFalse(serializer.is_valid())
