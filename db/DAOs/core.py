def execute_query(cursor, query, params=None, is_dict=True, fetch_size=None, cols_names=None):
    """
    Execute a query safely with bind parameters and return fetched results.
    """
    try:
        cursor.execute(query, params or {})
    except Exception as e:
        raise RuntimeError(f"Can't execute query: {e}")

    # --- unified fetch logic ---
    fetcher = cursor.fetchall if fetch_size is None else lambda: cursor.fetchmany(fetch_size)
    rows = fetcher()

    # --- format data ---
    if is_dict:
        columns = cols_names if cols_names else [col[0].lower() for col in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    return rows


class QueryBuilder:
    def __init__(self, dao, table):
        self.dao = dao
        self.table = table
        self._cols = "*"
        self._where = {}
        self._order_by = []
        self._page = None
        self._page_size = None
        self._is_dict = True
        self._fetch_size = None

        self._joins = []
        self._where_raw = None
        self._where_raw_params = {}
        self._cols_names = None

        # ✅ group by only
        self._group_by = None

    # -----------------------------
    def select(self, cols):
        self._cols = ", ".join(cols) if cols else "*"
        return self

    def join(self, table, condition, join_type="INNER"):
        join_type = join_type.upper()
        if join_type not in ("INNER", "LEFT", "RIGHT", "FULL"):
            raise ValueError(f"Invalid join type: {join_type}")

        self._joins.append(f"{join_type} JOIN {table} ON {condition}")
        return self

    def where(self, conditions):
        self._where = conditions or {}
        return self

    def row_where(self, raw_sql: str, params: dict = None):
        self._where_raw = raw_sql
        self._where_raw_params = params or {}
        return self

    def order_by(self, fields):
        self._order_by = fields or []
        return self

    def paginate(self, page, page_size):
        self._page = page
        self._page_size = page_size
        return self

    def as_tuples(self):
        """Fetch results as tuples instead of dicts."""
        self._is_dict = False
        return self

    # ✅ New method: group_by
    def group_by(self, fields):
        """
        Add GROUP BY clause.

        Example:
            .group_by(["region", "year"])
        """
        if isinstance(fields, (list, tuple)):
            self._group_by = ", ".join(fields)
        else:
            self._group_by = fields
        return self

    def fetch(self, fetch_size=None, cols_names=None):
        """Build final SQL and execute."""
        self._fetch_size = fetch_size
        self._cols_names = cols_names
        return self._execute()

    def count(self):
        """Return total number of rows matching current filters."""
        if hasattr(self, "_where_raw") and self._where_raw:
            where_clause, params = self.dao._build_row_where_clause(
                self._where_raw, getattr(self, "_where_raw_params", {})
            )
        else:
            where_clause, params = self.dao._build_where_clause(self._where)

        query = f"SELECT COUNT(*) AS total FROM {self.table}{where_clause}"

        with self.dao.get_cursor() as cursor:
            result = execute_query(cursor, query, params=params, is_dict=True)
            return result[0]["total"] if result else 0

    # ------------------------------------
    def _execute(self):
        # Build WHERE
        if self._where_raw:
            where_clause, params = self.dao._build_row_where_clause(
                self._where_raw, self._where_raw_params
            )
        else:
            where_clause, params = self.dao._build_where_clause(self._where)

        # Build JOIN / ORDER / PAGE
        join_clause = " " + " ".join(self._joins) if self._joins else ""
        order_clause = self.dao._build_order_clause(self._order_by)
        pagination_clause = self.dao._build_pagination_clause(self._page, self._page_size)

        # ✅ Build GROUP BY only
        group_clause = ""
        if self._group_by:
            group_clause = f" GROUP BY {self._group_by}"

        # ✅ Final Query
        query = f"""
        SELECT {self._cols}
        FROM {self.table}
        {join_clause}
        {where_clause}
        {group_clause}
        {order_clause}
        {pagination_clause}
        """.strip()

        with self.dao.get_cursor() as cursor:
            return execute_query(
                cursor,
                query,
                params=params,
                is_dict=self._is_dict,
                fetch_size=self._fetch_size,
                cols_names=self._cols_names
            )
