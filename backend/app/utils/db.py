#  -- I can't believe it's not ORM! --
# --- Just like a real ORM but worse ---
import psycopg2 as psycopg2
import logging
import string
import random
from psycopg2 import sql, Error
from datetime import datetime
from pydantic import BaseModel
from typing import Any, List, Type, Optional, Dict, Union

def generate_random_string(length: int) -> str:
    """Generate a random string of the specified length."""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class ComplexDatabaseManager:
    """A complex database manager that provides low-level access to a PostgreSQL database."""
    def __init__(self, dbname, user, password, host='localhost'):
        self.conn = None
        self.cursor = None
        try:
            self.conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host
            )
            self.cursor = self.conn.cursor()
        except Error as e:
            logging.error(f"Error {e.pgcode}: {e.pgerror}")
            self.close()
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the database connection."""
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            self.conn.close()

    def execute_query(self, query, params=None) -> Optional[bool]:
        """Execute a SQL query and commit the changes to the database."""
        if self.conn is not None:
            try:
                print(f"Executing query: {query.as_string(self.conn)}")
                self.cursor.execute(query, params)
                self.conn.commit()
                return True
            except Error as e:
                logging.error(f"Error {e.pgcode}: {e.pgerror}")
                self.conn.rollback()
                return False

    def read_query(self, query, params=None) -> Optional[List[dict]]:
        """Execute a SQL query and return the results as a list of dictionaries."""
        if self.conn is None:
            logging.error("Database connection not established.")
            return None

        try:
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()

            if not rows:
                return []

            result = []
            for row in rows:
                dict_row = {}
                for idx, col in enumerate(self.cursor.description):
                    col_name = col.name
                    col_type = col.type_code
                    value = row[idx]

                    if col_type not in pg_to_py_types:
                        dict_row[col_name] = value
                        continue

                    convert_func = pg_to_py_types[col_type]
                    try:
                        value = convert_func(value)
                    except (TypeError, ValueError) as e:
                        logging.error(f"Error while converting {col_name}: {e}")
                        value = None

                    dict_row[col_name] = value
                result.append(dict_row)
            return result

        except Error as e:
            logging.error(f"Error {e.pgcode}: {e.pgerror}")
            return None


class Table:
    """A table in a PostgreSQL database."""
    def __init__(self, db: ComplexDatabaseManager, name: str, primary_key: str = 'id'):
        self.db = db
        self.name = name
        self.primary_key = primary_key

    def get(self, condition: str, params: tuple) -> List[dict]:
        """
        Returns a list of dicts for all records in the database that match the given condition.
        The condition should be a string, and the params should be a tuple
        """
        assert isinstance(condition, str), "condition must be a string"
        assert isinstance(params, tuple), "params must be a tuple"
        query = sql.SQL("SELECT * FROM {} WHERE {}").format(
            sql.Identifier(self.name), 
            sql.SQL(condition)
        )
        return self.db.read_query(query, params)

    def getfirst(self, condition: str, params: tuple) -> Optional[dict]:
        """Returns the first record in the database that matches the given condition."""
        results = self.get(condition, params)
        if results:
            return results[0]
        return None

    def get_pydantic(self, condition: str, params: tuple, model: Type[BaseModel]) -> List[BaseModel]:
        """Returns a list of Pydantic models for all records in the database that match the given condition."""
        results = self.get(condition, params)
        return [model(**row) for row in results]

    def get_first_pydantic(self, condition: str, params: tuple, model: Type[BaseModel]) -> Optional[BaseModel]:
        """
        Get the first row from the database and return it as a Pydantic model.

        :param condition: The condition to use in the query.
        :param params: The parameters to use in the query.
        :param model: The Pydantic model to use to represent the row.
        :return: The row as a Pydantic model, or None if no rows were returned.
        """
        result = self.getfirst(condition, params)
        if result:
            return model(**result)
        return None

    def _generate_unique_id(self, length: int) -> str:
        """ Generate a unique ID for the table
        This isn't great, but UUIDs are a bit too long for my taste
        and this probably isn't going to be popular enough to warrant it anyways lol
        """
        attempts = set()
        # this was originally recursive, but I changed it to a loop because "mumble... pythonic... mumble mumble"
        for _ in range(1000):  # Limit the number of attempts, idk this seems good enough
            id = generate_random_string(length)
            if id not in attempts:
                attempts.add(id)
                if not self.get(f"{self.primary_key} = %s", (id,)):
                    return id
        raise Exception("Unable to generate a unique ID after 1000 attempts.")

    def insert(self, data: Dict[str, Any], id_length: Optional[int] = None):
        """Insert a new record into the database."""
        if id_length is not None and self.primary_key == 'id':
            assert 'id' not in data, "When id_length is provided, 'id' should not be in data"
            unique_id = self._generate_unique_id(id_length)
            data['id'] = unique_id
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(self.name),
            sql.SQL(', ').join(map(sql.Identifier, data.keys())),
            sql.SQL(', ').join(sql.Placeholder() * len(data))
        )
        self.db.execute_query(query, list(data.values()))


    def update(self, condition: str, params: tuple, column: str, value):
        """Update a record in the database."""
        query = sql.SQL("UPDATE {} SET {} = %s WHERE {}").format(
            sql.Identifier(self.name),
            sql.Identifier(column),
            sql.SQL(condition)
        )
        self.db.execute_query(query, (value,) + params)

    def delete(self, condition: str, params: tuple):
        """Delete a record from the database."""
        query = sql.SQL("DELETE FROM {} WHERE {}").format(
            sql.Identifier(self.name),
            sql.SQL(condition)
        )
        self.db.execute_query(query, params)

    def get_item(self, condition: str, params: tuple) -> Optional['Row']:
        """Returns a Row object for the first record in the database that matches the given condition."""
        result = self.getfirst(condition, params)
        if result:
            return Row(**result, table=self)
        return None


class Row:
    """A row in a PostgreSQL database."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.table = kwargs.pop('table', None)

    def update(self, column: str, value):
        """Update a column in the row."""
        if self.table.primary_key in self.__dict__:
            self.table.update(f'{self.table.primary_key} = %s', (self.__dict__[self.table.primary_key],), column, value)
            self.__dict__[column] = value
        else:
            raise Error("Can't update row without primary key.")

    def delete(self):
        """Delete the row from the database."""
        if self.table.primary_key in self.__dict__:
            self.table.delete(f'{self.table.primary_key} = %s', (self.__dict__[self.table.primary_key],))
        else:
            raise Error("Can't delete row without primary key.")


class DatabaseManager(ComplexDatabaseManager):
    """A database manager that provides high-level access to a PostgreSQL database."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tables = {}

    def __getattr__(self, item):
        if item not in self.tables:
            self.tables[item] = Table(self, item)
        return self.tables[item]

    def create_table(self, table_name: str, columns: Dict[str, str]):
        """Create a new table in the database."""
        assert isinstance(columns, dict), "columns should be a dictionary with format {'column_name': 'data_type'}"
        columns_str = ', '.join([f'{col} {data_type}' for col, data_type in columns.items()])
        query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
            sql.Identifier(table_name),
            sql.SQL(columns_str)
        )
        self.execute_query(query)
