from api2.models import Budget


def get_all_children(budget: Budget):
    budget_table = Budget.objects.model._meta.db_table
    return Budget.objects.raw(f"""
        WITH RECURSIVE search_tree(id, parent_id) AS (
                SELECT id, parent_id
                FROM {budget_table}
                WHERE parent_id = {budget.id}
             UNION ALL
                 SELECT b.id, b.parent_id
                 FROM {budget_table} as b, search_tree as t
                 WHERE b.parent_id = t.id
        )
    SELECT * FROM search_tree;
    """)