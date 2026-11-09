from langchain.tools import tool
import sqlglot


@tool
def validate_sql(sql: str) -> str:
    """
    Validate PostgreSQL SQL syntax.
    Use this before presenting generated SQL to the user.
    """

    try:
        sqlglot.parse(
            sql,
            read="postgres",
            error_level="RAISE"
        )

        return "SQL syntax is valid."

    except Exception as e:
        return f"SQL validation failed: {str(e)}"