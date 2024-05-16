import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML


def extract_tables_and_columns(query):
    parsed = sqlparse.parse(query)
    statement = parsed[0]
    tables = []
    columns = []

    for token in statement.tokens:
        if token.ttype is Keyword and token.value.upper() == 'FROM':
            idx = statement.token_index(token)
            tables += [statement.tokens[idx + 2].get_real_name()]
        elif isinstance(token, IdentifierList):
            for identifier in token.get_identifiers():
                columns.append(identifier.get_real_name())
        elif isinstance(token, Identifier):
            columns.append(token.get_real_name())
    return tables, columns

def combine_queries(queries):
    all_tables = set()
    all_columns = set()
    where_clauses = set()
    for query in queries:
        tables, columns = extract_tables_and_columns(query)
        all_tables.update(tables)
        all_columns.update(columns)
        where_clause = query.split('WHERE')[-1].strip() if 'WHERE' in query else ''
        if where_clause:
            where_clauses.add(where_clause)

    combined_query = 'SELECT ' + ', '.join(all_columns) + ' FROM ' + ' LEFT JOIN '.join(all_tables)
    if where_clauses:
        combined_query += ' WHERE ' + ' AND '.join(where_clauses)

    return combined_query

queries = [
    "SELECT a.name, a.age FROM users a WHERE a.id = 1;",
    "SELECT b.salary FROM salaries b WHERE b.user_id = 1;",
    "SELECT c.address FROM addresses c WHERE c.user_id = 1;"
]

combined_query = combine_queries(queries)
print(combined_query)
