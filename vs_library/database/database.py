
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
    
    """
    Holds the necessary information for a database adapter to establish a connection
    
    Attributes
    ----------
    connection_id : int
        A unique ID given to each connection info

    host : str
        Name of the host to connect

    port : int
        Port number of the connection
    
    user : str
        Name of the user recognized by the host
    """
    
    connection_id: int = None
    host: str = ''
    database: str = ''
    port: int = None
    user: str = ''
    password: str = field(default=None, repr=False)


class ConnectionManager:

    """
    Creates, Read, Update and Delete connection info using configparser
    
    See more on configparser at:
    https://docs.python.org/3/library/configparser.html
    
    """

    def __init__(self, filepath):

        """
        Parameters
        ----------

        filepath : str
            A path to a directory or a file
        """
        
        self.__filepath = filepath if os.path.isdir(filepath) else os.path.dirname(filepath)
        self.__filename = 'connections.ini'

        self.__parser = configparser.ConfigParser()
        self.__parser.read(f"{self.__filepath}/{self.__filename}")

    def _write(self):

        """Creates or use an existing file"""

        with open(f"{self.__filepath}/{self.__filename}", 'w') as f:
            self.__parser.write(f)
        
    def create(self, connection_info):

        """Unwraps connection info and writes it to a new or existing file"""

        # auto increment id
        initial_id = 1 if not self.__parser.sections() else max(list(map(int, self.__parser.sections()))) + 1

        self.__parser[initial_id] = {
            'host': str(connection_info.host),
            'database': str(connection_info.database),
            'port': str(connection_info.port),
            'user': str(connection_info.user),
            'password': str(connection_info.password)
            }

        self._write()

        return f"A new connection info is added and assigned connection_id={initial_id}"

    def read(self, connection_id=None):

        """
        Return a single or an array of connection info from the parser

        Parameters
        ----------
        connection_id : str or int
            ID corresponding to what is found in parser

        Returns
        -------
        (ConnectionInfo or array, str)
        """

        # prevents 0 or an empty string as an input to return all connections
        if connection_id == None:
            connections = []
            for section in self.__parser.sections():
                connection_info = ConnectionInfo()
                connection_info.connection_id = section
                connection_info.host = self.__parser[section]['host']
                connection_info.database = self.__parser[section]['database']
                connection_info.port = self.__parser[section]['port']
                connection_info.user = self.__parser[section]['user']
                connection_info.password = self.__parser[section]['password']
                connections.append(connection_info)
                
            return connections, f"Total of {len(connections)} connections found."

        else:
            if str(connection_id) in self.__parser.sections(): 
                connection_info = ConnectionInfo()
                connection_info.connection_id = int(connection_id)
                connection_info.host = self.__parser[str(connection_id)]['host']
                connection_info.database = self.__parser[str(connection_id)]['database']
                # ConnectionInfo dataclass requires port to be int
                connection_info.port = int(self.__parser[str(connection_id)]['port'])
                connection_info.user = self.__parser[str(connection_id)]['user']
                connection_info.password = self.__parser[str(connection_id)]['password']

                return connection_info, f"connection_id={connection_id} is selected"
            else:
                return None, f"Selected connection connection_id={connection_id}" +\
                              " is not found"

    def update(self, connection_info):
        
        """Update existing connection info or create one if it is not an existing one"""

        connection_id = str(connection_info.connection_id)

        if connection_id in self.__parser.sections():
            self.__parser[connection_id] = {
                'host': connection_info.host,
                'database': connection_info.database,
                'port': connection_info.port,
                'user': connection_info.user,
                'password': connection_info.password
                }

            self._write()

    def delete(self, connection_id):

        """Delete connection info by connection_id"""

        if str(connection_id) in self.__parser.sections():
            self.__parser.remove_section(str(connection_id))
            self._write()

    @property
    def existing_connection(self):
        return True if self.__parser.sections() else False


class PostgreSQL:

    """A PostgreSQL connection adapter"""

    def __init__(self, connection_info, paramstyle='named'):

        """
        This connection adapter utilizes the pg8000 package, see here:
        https://pypi.org/project/pg8000/

        Parameters
        ----------
        paramstyle : 'named', 'qmark', 'numeric', 'format' or 'pyformat', default='named'
            This will depend on how query parameters are appended
            See here for more details: https://www.python.org/dev/peps/pep-0249/#paramstyle
        """

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

    def connect(self, autocommit=False):
        
        """
        Establishes connection and changes connection to a pg8000 connection object

        Parameters
        ----------
        autocommit : bool
            if True, each execution is a complete transaction, useful for executing multiple
            query statements
        """

        connect_args = {'host': self.__connection_info.host,
                        'database': self.__connection_info.database,
                        'port': self.__connection_info.port,
                        'user': self.__connection_info.user,
                        'password': self.__connection_info.password
                        }

        if self.__connection_info:
            try:
                self.__connection = pg8000.connect(**connect_args, timeout=10) # default timeout is longer
                self.__connection.autocommit = autocommit # autocommit is False by default on pg8000
                return True, f"Successfully established connection to {connect_args['host']}."

            except ProgrammingError as e:
                # ProgrammingError returns a dict-like string
                error_dict = eval(str(e))
                return False, f"ERROR: {error_dict['M']}"

            except Exception as e:
                return False, f"ERROR: {str(e)}"
        else:
            return False, "Invalid connection info"

    def disconnect(self):
        self.__connection.close()
        self.__connection = None

    def execute(self, statement, values=None):
        """Use a database cursor to execute a SQL statement"""
        cursor = self.__connection.cursor()
        cursor.execute(statement, values or {})
        return cursor

    def status(self):
        return True if self.__connection else False

    # close connection safely when exiting python
    def __del__(self):
        if self.__connection:
            self.__connection.close()


class QueryTool:

    """Perform SQL querying on database and stores query results
    
    Attributes
    ----------
    query : tuple
        The first element in the tuple is the query string
        The second element in the tuple are the parameters of the query string
    """

    def __init__(self, connection_adapter):

        """
        Parameters
        ----------
        connection_adapter : (PostgreSQL or other)
            an extension of a database adapter
        """

        self.connection_adapter = connection_adapter

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

        """
        Returns query results in a specific format

        Parameters
        ----------
        as_format : 'tuple', 'records', or 'pandas_df'
            'tuple' is the direct result of a query execution
            'records' is a list of dictionaries
            'pandas_df' is a pandas DataFrame object

        Returns
        -------
        tuple, [dict_1, dict_2...] or pandas.DataFrame()
        """
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

        """Excecutes query statement using a database cursor"""

        # calculates the total time taken to execute query
        start_time = time.process_time()

        try:
            # make sure connection is established
            if not self.connection_adapter.connected:
                success, message = self.connection_adapter.connect()
                if not success:
                    return False, message
            
            cursor = self.connection_adapter.execute(self.__query_statement, self.__query_params)
            end_time = time.process_time()

            header = [str(k[0]) for k in cursor.description]
            # fetchall will empty cursor contents, list to store it somewhere else
            rows = list(cursor.fetchall()) if cursor else [] 

            self.__results = (rows, header)
            self.__number_of_columns = len(header)
            self.__number_of_rows = cursor.rowcount
            self.__time_taken = end_time - start_time

            cursor.close()

            return True, "Successfully executed query."
        
        except ProgrammingError as e:
            end_time = time.process_time()

            # ProgrammingError returns a dict-like string
            error_dict = eval(str(e))

            self.__results = None
            self.__number_of_rows = 0
            self.__number_of_columns = 0
            self.__time_taken = end_time - start_time

            # error can be due to a connection error
            if self.connection_adapter.connected:
                self.connection_adapter.disconnect()

            return False, f"ERROR: {error_dict['M']}.{' ' + error_dict['H'] if 'H' in error_dict.keys() else ''}"

        except Exception as e:

            end_time = time.process_time()

            self.__results = None
            self.__number_of_rows = 0
            self.__number_of_columns = 0
            self.__time_taken = end_time - start_time

            # error can be due to a connection error
            if self.connection_adapter.connected:
                self.connection_adapter.disconnect()

            return False, f"ERROR: {str(e)}"
    
    def export(self, filepath):

        try:
            df = self.results(as_format='pandas_df')
            success, message = pandas_functions.to_spreadsheet(df, filepath=filepath)
            
            return success, message
            
        except Exception as e:
            return False, f"ERROR: {str(e)}"
