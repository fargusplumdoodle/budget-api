ROOT_BUDGET_NAME = "root"


class DefaultTags:
    INCOME = "income"
    TRANSFER = "transfer"
    PAYCHEQUE = "paycheque"

    @classmethod
    def values(cls):
        return [
            cls.__dict__[member]
            for member in cls.__dict__
            if (member[:2] != "__" and member != "values")
        ]
