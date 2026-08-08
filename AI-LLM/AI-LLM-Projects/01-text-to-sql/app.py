import os
import re
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
import sqlglot
from sqlglot import exp

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
DB_PATH = Path(__file__).with_name("sales.db")


def create_database():
    """Create a small demo database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS customers;

    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        customer_name TEXT NOT NULL,
        city TEXT NOT NULL
    );

    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        amount REAL NOT NULL,
        FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
    );

    INSERT INTO customers VALUES
        (1, 'Alice', 'Hyderabad'),
        (2, 'Bob', 'Bengaluru'),
        (3, 'Charlie', 'Chennai'),
        (4, 'Diana', 'Mumbai');

    INSERT INTO orders VALUES
        (101, 1, '2025-01-15', 4500),
        (102, 1, '2025-05-20', 7800),
        (103, 2, '2025-02-10', 12000),
        (104, 2, '2025-09-18', 6900),
        (105, 3, '2025-03-02', 3200),
        (106, 4, '2025-11-05', 15000);
    """)

    conn.commit()
    conn.close()


def get_schema():
    """Return database schema and relationships."""
    return """
TABLE customers
- customer_id INTEGER PRIMARY KEY
- customer_name TEXT
- city TEXT

TABLE orders
- order_id INTEGER PRIMARY KEY
- customer_id INTEGER
- order_date TEXT
- amount REAL

RELATIONSHIP
orders.customer_id = customers.customer_id
""".strip()


def retrieve_schema(question):
    """Simple schema retrieval layer for this demo."""
    q = question.lower()
    relevant = []

    if any(word in q for word in ["customer", "customers", "city"]):
        relevant.append("customers")
    if any(word in q for word in ["order", "orders", "sales", "spent", "amount", "purchase"]):
        relevant.append("orders")

    if not relevant:
        relevant = ["customers", "orders"]

    schema = get_schema()
    lines = schema.splitlines()

    # Keep the complete relationship plus selected tables.
    output = []
    current_table = None
    for line in lines:
        if line.startswith("TABLE "):
            current_table = line.split()[1]
            if current_table in relevant:
                output.append(line)
        elif line.startswith("RELATIONSHIP"):
            output.append(line)
        elif current_table in relevant and line.startswith("- "):
            output.append(line)

    return "\n".join(output)


def get_client():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Copy .env.example to .env and add your key."
        )
    return OpenAI(api_key=key)


def generate_sql(question, schema):
    client = get_client()

    prompt = f"""
You are a careful SQLite Text-to-SQL assistant.

Generate exactly ONE read-only SQL query.
Use only tables and columns present in the schema.
Do not use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, ATTACH, PRAGMA,
or multiple statements.
Return SQL only, with no Markdown fences.

SCHEMA:
{schema}

QUESTION:
{question}
""".strip()

    response = client.responses.create(model=MODEL, input=prompt)
    return response.output_text.strip().strip("`").strip()


def validate_sql(sql):
    """Validate that the generated SQL is one safe SELECT statement."""
    cleaned = sql.strip().rstrip(";")

    if ";" in cleaned:
        raise ValueError("Multiple SQL statements are not allowed.")

    forbidden = re.compile(
        r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|ATTACH|DETACH|PRAGMA|VACUUM)\b",
        re.IGNORECASE,
    )
    if forbidden.search(cleaned):
        raise ValueError("Only read-only SELECT queries are allowed.")

    parsed = sqlglot.parse(cleaned, read="sqlite")
    if len(parsed) != 1:
        raise ValueError("Exactly one SQL statement is required.")

    if not isinstance(parsed[0], exp.Select):
        raise ValueError("The query must be a SELECT statement.")

    return cleaned


def execute_sql(sql):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(sql).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def explain_results(question, sql, rows):
    client = get_client()

    prompt = f"""
Answer the user's question using the SQL result below.
Be concise and do not invent facts.

QUESTION:
{question}

SQL:
{sql}

RESULT:
{rows}
""".strip()

    response = client.responses.create(model=MODEL, input=prompt)
    return response.output_text.strip()


def main():
    create_database()

    print("=" * 60)
    print("TEXT-TO-SQL WORKFLOW")
    print("=" * 60)
    question = input(
        "Ask a question about the sales database "
        "(or press Enter for the demo question): "
    ).strip()

    if not question:
        question = "Which customers spent more than 10000 in 2025?"

    try:
        schema = retrieve_schema(question)
        sql = generate_sql(question, schema)
        sql = validate_sql(sql)
        rows = execute_sql(sql)

        print("\nRetrieved schema:\n")
        print(schema)

        print("\nGenerated SQL:\n")
        print(sql)

        print("\nDatabase result:\n")
        for row in rows:
            print(row)

        print("\nAnswer:\n")
        print(explain_results(question, sql, rows))

    except Exception as exc:
        print(f"\nError: {exc}")


if __name__ == "__main__":
    main()
