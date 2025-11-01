from .core import QueryBuilder
from contextlib import contextmanager
from db.executor import connect_to_oracle_with_default_confs
import logging


OPERATORS = {
    "eq": "=",      # default
    "gt": ">", 
    "lt": "<",
    "gte": ">=",
    "lte": "<=",
    "ne": "!=",
    "like": "LIKE",
    "in": "IN"
}


logger = logging.getLogger(__name__)
class OracleDAO:
    def __init__(self, confs=None):
        self.confs = confs

    @contextmanager
    def get_cursor(self):
        conn = None
        cursor = None
        try:
            conn    = connect_to_oracle_with_default_confs(self.confs)
            cursor  = conn.cursor()
            yield cursor
            conn.commit()
        except Exception as e:
            logger.error(f"Oracle DAO error: {e}")
            raise
        finally:
            if cursor is not None:
                try:
                    cursor.close()
                except Exception:
                    pass
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    # 🔥 New method
    def table(self, table_name):
        """Return a LINQ-like QueryBuilder for a given table."""
        return QueryBuilder(self, table_name)
    
        

    # --- keep your existing helpers for QueryBuilder ---
    def _build_where_clause(self, where: dict):
        if not where:
            return "", {}

        conditions = []
        params = {}

        for idx, (key, value) in enumerate(where.items()):
            if "__" in key:
                field, op_key = key.split("__", 1)
                operator = OPERATORS.get(op_key, "=")
            else:
                field, operator = key, "="

            param_name = f"param_{idx}"

            if operator == "IN":
                placeholders = []
                for j, val in enumerate(value):
                    p_name = f"{param_name}_{j}"
                    placeholders.append(f":{p_name}")
                    params[p_name] = val
                conditions.append(f"{field} IN ({', '.join(placeholders)})")
            else:
                conditions.append(f"{field} {operator} :{param_name}")
                params[param_name] = value

        return " WHERE " + " AND ".join(conditions), params
    
    def _build_row_where_clause(self, where: str, params: dict = None):
        """
        Build a WHERE clause from raw SQL with bind parameters.

        Example:
            where = "age > :min_age AND status = :status"
            params = {"min_age": 18, "status": "active"}
        """
        if not where or not where.strip():
            return "", {}

        return f" WHERE {where.strip()}", params or {}
    
    
    def _build_order_clause(self, order_by):
        if not order_by:
            return ""
        clauses = []
        for field in order_by:
            if field.startswith('-'):
                clauses.append(f"{field[1:]} DESC")
            else:
                clauses.append(f"{field} ASC")
        return " ORDER BY " + ", ".join(clauses)

    def _build_pagination_clause(self, page, page_size):
        if page is None or page_size is None:
            return ""
        offset = (max(page, 1) - 1) * page_size
        return f" OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY"


