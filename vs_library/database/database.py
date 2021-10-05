
# built-ins
import os
import time
import configparser
from dataclasses import dataclass, field

# external packages
import pandas
import pg8000
from pg8000.dbapi import ProgrammingError

from ..tools import pandas_functions


@dataclass
class ConnectionInfo:
    
    """A dataclass that contains the necessary information for a database adapter to connect to a host."""
    
    connection_id: int = None
    host: str = None
    database: str = None
    port: int = None
    user: str = None
    password: str = field(default=None, repr=False)


class ConnectionManager:

    def __init__(self, filepath=None):

        self.filename = 'connections.ini' if not filepath else os.path.basename(filepath)
        self.parser = configparser.ConfigParser()
        self.parser.read(self.filename)
        
    def create(self, connection_info):
        initial_id = 1 if not self.parser.sections() else max(list(map(int, self.parser.sections()))) + 1

        self.parser[initial_id] = {
            'host': str(connection_info.host),
            'database': str(connection_info.database),
            'port': str(connection_info.port),
            'user': str(connection_info.user),
            'password': str(connection_info.password)
            }

        self._write()

    def read(self, connection_id=None):
        if connection_id == None:
            connections = []
            for section in self.parser.sections():
                connection_info = ConnectionInfo()
                connection_info.connection_id = section
                connection_info.host = self.parser[section]['host']
                connection_info.database = self.parser[section]['database']
                connection_info.port = self.parser[section]['port']
                connection_info.user = self.parser[section]['user']
                connection_info.password = self.parser[section]['password']
                connections.append(connection_info)
                
            return connections, f"Total of {len(connections)} connections found."

        else:
            if str(connection_id) in self.parser.sections(): 
                connection_info = ConnectionInfo()
                connection_info.connection_id = int(connection_id)
                connection_info.host = self.parser[str(connection_id)]['host']
                connection_info.database = self.parser[str(connection_id)]['database']
                connection_info.port = int(self.parser[str(connection_id)]['port'])
                connection_info.user = self.parser[str(connection_id)]['user']
                connection_info.password = self.parser[str(connection_id)]['password']

                return connection_info
            else:
                return None
                
    def _write(self):
        with open(self.filename, 'w') as f:
            self.parser.write(f)

    def update(self, connection_info):
        connection_id = str(connection_info.connection_id)

        if connection_id in self.parser.sections():
            self.parser[connection_id] = {
                'host': connection_info.host,
                'database': connection_info.database,
                'port': connection_info.port,
                'user': connection_info.user,
                'password': connection_info.password
                }

            self._write()
            return True, f"connection_id={connection_info.connection_id} updated."
        else:
            return False, f"connection_id={connection_info.connection_id} not found."

    def delete(self, connection_id):

        if str(connection_id) in self.parser.sections():
            self.parser.remove_section(str(connection_id))
            self._write()
            return True, f"connection_id={connection_id} removed."
        else:
            return False, f"connection_id={connection_id} not found"

    @property
    def existing_connection(self):
        return True if self.parser.sections() else False


class PostgreSQL:

    def __init__(self, connection_info, paramstyle='named'):

        pg8000.paramstyle = paramstyle

        self.__connection_info = connection_info
        self.__connection = None

    @property
    def connected(self):
        return True if self.__connection else False

    @property
    def connection_info(self):
        return self.__connection_info

    @connection_info.setter
    def connection_info(self, c):
        if not self.__connection:
            self.__connection_info = c

    def connect(self, autocommit=True):

        connect_args = {'host': self.__connection_info.host,
                        'database': self.__connection_info.database,
                        'port': self.__connection_info.port,
                        'user': self.__connection_info.user,
                        'password': self.__connection_info.password
                        }

        if self.__connection_info:
            try:
                self.__connection = pg8000.connect(**connect_args, timeout=10)
                self.__connection.autocommit = autocommit
                return True, f"Successfully established connection to {connect_args['host']}."

            except ProgrammingError as e:
                error_dict = eval(str(e))
                return False, f"{error_dict['M']}"

            except Exception as e:
                return False, f"{str(e)}"
        else:
            return False, "Invalid connection info"

    def disconnect(self):
        self.__connection.close()
        self.__connection = None

    def execute(self, statement, values=None):
        cursor = self.__connection.cursor()
        cursor.execute(statement, values or {})
        return cursor

    def status(self):
        return True if self.__connection else False

    def __del__(self):
        if self.__connection:
            self.__connection.close()


class QueryTool:

    def __init__(self, adapter):

        self.connection_adapter = adapter

        self.__query_statement = None
        self.__query_params = None

        self.__results = None
        self.__number_of_rows = 0
        self.__number_of_columns = 0
        self.__time_taken = 0

    @property
    def query(self):
        return self.__query_statement, self.__query_params

    @query.setter
    def query(self, query):
        statement, *params = query

        self.__query_statement = statement if statement else None
        self.__query_params = next(iter(params)) if params else None

    def results(self, as_format='tuple'):

        if as_format == 'tuple':
            return self.__results if self.__results else ()

        elif as_format == 'records':
            rows, header = self.__results if self.__results else ([], [])
            return [dict(zip(header, row)) for row in rows]

        elif as_format == 'pandas_df':
            rows, header = self.__results if self.__results else ([], [])

            return pandas.DataFrame(list(rows), columns=header)

        else:
            return None

    @property
    def query_message(self):
        return f"Query returns {self.__number_of_rows} rows, " \
               f"{self.__number_of_columns} columns.\n" \
               f"Time taken: {self.__time_taken}s"

    def run(self):

        start_time = time.process_time()

        try:
            if not self.connection_adapter.connected:
                success, message = self.connection_adapter.connect()
                if not success:
                    return False, message
                    
            cursor = self.connection_adapter.execute(self.__query_statement, self.__query_params)
            end_time = time.process_time()

            header = [str(k[0]) for k in cursor.description]
            rows = list(cursor.fetchall()) if cursor else []

            self.__results = (rows, header)
            self.__number_of_columns = len(header)
            self.__number_of_rows = cursor.rowcount
            self.__time_taken = end_time - start_time

            cursor.close()

            return True, "Successfully executed query."
        
        except ProgrammingError as e:
            error_dict = eval(str(e))

            end_time = time.process_time()
            self.__results = None
            self.__number_of_rows = 0
            self.__number_of_columns = 0
            self.__time_taken = end_time - start_time

            if self.connection_adapter.connected:
                self.connection_adapter.disconnect()

            return False, f"{error_dict['M']}.{' ' + error_dict['H'] if 'H' in error_dict.keys() else ''}"

        except Exception as e:

            end_time = time.process_time()
            self.__results = None
            self.__number_of_rows = 0
            self.__number_of_columns = 0
            self.__time_taken = end_time - start_time

            if self.connection_adapter.connected:
                self.connection_adapter.disconnect()

            return False, f"{str(e)}"
    
    def export(self, filepath):

        try:
            df = self.results(as_format='pandas_df')
            success, message = pandas_functions.to_spreadsheet(df, filepath=filepath)
            
            return success, message
            
        except Exception as e:
            return False, str(e)
