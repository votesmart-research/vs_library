
# internal packages
import re
from . import database
from ..tools import pandas_functions_cli
from ..cli import Node, NodeBundle, DecoyNode, textformat
from ..cli.objects import Command, Display, Prompt, Table


def will_it_int(response):
    try:
        int(response)
        return True
    except ValueError:
        return False, "Input must be an integer"


class AddConnection(NodeBundle):


    def __init__(self, connection_manager, parent=None):

        """
        Prompts user to enter necessary information for a connection to be stored.

        Parameters
        ----------
        connection_manager : database.ConnectionManager
            the controller of this bundle
        """

        name = 'add-connection'
        self.connection_manager = connection_manager

        # OBJECTS
        self.__prompt_0 = Prompt(textformat.apply("Host Name", emphases=['bold']))
        self.__prompt_1 = Prompt(textformat.apply("Database Name", emphases=['bold']))
        self.__prompt_2 = Prompt(textformat.apply("Port Number", emphases=['bold']), 
                                 verification=will_it_int)
        self.__prompt_3 = Prompt(textformat.apply("Username", emphases=['bold']))
        self.__prompt_4 = Prompt(textformat.apply("Password", emphases=['bold']))
        self.__prompt_5 = Prompt("Proceed with the changes?")

        self.__table_0 = Table([], header=False, command=Command(self._populate_table))

        # NODES
        self.__entry_node = Node(self.__prompt_0, name=f'{name}_hostname', 
                                 show_hideout=True)

        self.__node_0 = Node(self.__prompt_1, name=f'{name}_database', parent=self.__entry_node, 
                             show_hideout=True)
        self.__node_1 = Node(self.__prompt_2, name=f'{name}_port', parent=self.__node_0, 
                             show_hideout=True)
        self.__node_2 = Node(self.__prompt_3, name=f'{name}_username', parent=self.__node_1, 
                             show_hideout=True)
        self.__node_3 = Node(self.__prompt_4, name=f'{name}_password', parent=self.__node_2, 
                             show_hideout=True)
        self.__node_4 = Node(self.__table_0, name=f'{name}_responses', parent=self.__node_3,
                             show_hideout=True, store=False, clear_screen=True)

        self.__node_5 = Node(self.__prompt_5, name=f'{name}_confirm', parent=self.__node_4, 
                             show_hideout=True, store=False, acknowledge=True)

        self.__exit_node = DecoyNode(name=f'{name}_last-node', parent=self.__node_5)

        self.__node_5.adopt(self.__entry_node)

        # CONFIGURATIONS
        self.__table_0.table_header = "Connection Info"

        self.__prompt_5.options = {
            '1': Command(self._execute, value='Yes', respond=True,
                         command=Command(lambda: self.__node_5.set_next(self.__exit_node))),
            '2': Command(lambda: self.__node_5.set_next(self.__entry_node), value="Re-enter responses",
                         command=Command(self.clear_all, respond=True)),
            '3': Command(lambda: self.__node_5.set_next(self.__exit_node), value="Discard Changes",
                         command=Command(self.clear_all, respond=True))
            }

        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)

    def _execute(self):
        new_connection = database.ConnectionInfo()

        new_connection.host = self.__prompt_0.responses
        new_connection.database = self.__prompt_1.responses
        new_connection.port = self.__prompt_2.responses
        new_connection.user = self.__prompt_3.responses
        new_connection.password = self.__prompt_4.responses

        msg = self.connection_manager.create(new_connection)

        return textformat.apply(msg, emphases=['italic'], text_color='green')

    def clear_all(self):
        # must clear results to prevent from uninteded edits
        self.__prompt_0.clear()
        self.__prompt_1.clear()
        self.__prompt_2.clear()
        self.__prompt_3.clear()
        self.__prompt_4.clear()

        return textformat.apply("All responses are cleared.", emphases=['italic'], bg_color='bright_yellow')

    def _populate_table(self):
        self.__table_0.table = [[textformat.apply("Host", emphases=['bold']), self.__prompt_0.responses],
                                [textformat.apply("Database Name", emphases=['bold']), self.__prompt_1.responses],
                                [textformat.apply("Port Number", emphases=['bold']), self.__prompt_2.responses],
                                [textformat.apply("Username", emphases=['bold']), self.__prompt_3.responses],
                                [textformat.apply("Password", emphases=['bold']), self.__prompt_4.responses]]


class SelectConnection(NodeBundle):

    def __init__(self, connection_manager, parent=None):

        """
        Prompts user to select a connection from a table of stored connection

        Parameters
        ----------
        connection_manager : database.ConnectionManager
            the controller of this bundle
        """

        name = 'select-connection'

        self.connection_manager = connection_manager
        # list is a memory location such that it can be referenced
        self.__selected_connection = []

        # OBJECTS
        self.__table_0 = Table([[]], header=True, 
                               command=Command(self._populate_table))

        self.__prompt_0 = Prompt("Select a connection by connection_id", 
                                 command=Command(self._execute, respond=True))
        
        # NODES
        self.__entry_node = Node(self.__table_0, name=f'{name}_connection-list', 
                                 store=False)

        self.__node_0 = Node(self.__prompt_0, name=f'{name}_select-connection', parent=self.__entry_node, 
                             store=False)

        self.__exit_node = DecoyNode(name=f'{name}_lastnode', parent=self.__node_0)

        self.__node_0.adopt(self.__entry_node)

        # CONFIGURATIONS
        self.__table_0.table_header = "Stored Connections"
        self.__table_0.description = "Shows all connections stored locally"

        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)
    
    def _execute(self):
        
        # clears the list in order to append newly selected connection
        self.__selected_connection.clear()

        # ConnectionManager.read() requires a str or an int
        # prompt.responses returns an empty list instead of a str or int
        response = self.__prompt_0.responses if self.__prompt_0.responses else 0
        connection_info, msg = self.connection_manager.read(response)

        if connection_info:
            self.selected_connection.append(connection_info)
            self.__node_0.set_next(self.__exit_node)
        else:
            self.__node_0.set_next(self.__entry_node)
            return textformat.apply(msg, emphases=['italic'], text_color='red')

    def _populate_table(self):
        connections, msg = self.connection_manager.read()

        self.__table_0.table = [['connection_id','host', 'database', 'port', 'user']]
        self.__table_0.description = msg

        for connection in connections:
            self.__table_0.table.append([connection.connection_id, connection.host, connection.database, connection.port, connection.user])

    @property
    def selected_connection(self):
        return self.__selected_connection


class EditConnection(NodeBundle):
    
    def __init__(self, connection_manager, selected_connection, parent=None):

        """
        Edit and update an existing connection

        Parameters
        ----------
        connection_manager : database.ConnectionManager
            the controller of this bundle

        selected_connection: list
            may refer to the list in SelectConnection bundle
        """
        
        name = 'edit-connection'
        
        self.connection_manager = connection_manager
        self.connection_to_edit = selected_connection

        # OBJECTS
        self.__prompt_0 = Prompt("Which of the following would you like to change?")
        self.__prompt_1 = Prompt(textformat.apply("Host Name", emphases=['bold']), 
                                 command=Command(self._update_host))
        self.__prompt_2 = Prompt(textformat.apply("Database Name", emphases=['bold']), 
                                 command=Command(self._update_database))
        self.__prompt_3 = Prompt(textformat.apply("Port Number", emphases=['bold']), 
                                 command=Command(self._update_port), verification=will_it_int)
        self.__prompt_4 = Prompt(textformat.apply("Username", emphases=['bold']), 
                                 command=Command(self._update_user))
        self.__prompt_5 = Prompt(textformat.apply("Password", emphases=['bold']), 
                                 command=Command(self._update_password))
        self.__prompt_6 = Prompt("Done Editing?")
        self.__prompt_7 = Prompt("Are you sure you want to delete this connection?")

        # NODES
        self.__entry_node = Node(self.__prompt_0, name=f'{name}_selection',
                                 show_hideout=True)

        self.__node_0 = Node(self.__prompt_1, name=f'{name}_host', parent=self.__entry_node, 
                             store=False)
        self.__node_1 = Node(self.__prompt_2, name=f'{name}_database', parent=self.__entry_node, 
                             store=False)
        self.__node_2 = Node(self.__prompt_3, name=f'{name}_port', parent=self.__entry_node, 
                             store=False)
        self.__node_3 = Node(self.__prompt_4, name=f'{name}_username', parent=self.__entry_node, 
                             store=False)
        self.__node_4 = Node(self.__prompt_5, name=f'{name}_password', parent=self.__entry_node, 
                             store=False)
        self.__node_5 = Node(self.__prompt_6, name=f'{name}_confirm', parent=self.__entry_node, 
                             store=False)
        self.__node_6 = Node(self.__prompt_7, name=f'{name}_delete', parent=self.__entry_node)

        self.__exit_node = DecoyNode(name=f'{name}_lastnode', parent=self.__node_5)

        self.__entry_node.adopt(self.__exit_node)
        self.__node_0.adopt(self.__node_5)
        self.__node_1.adopt(self.__node_5)
        self.__node_2.adopt(self.__node_5)
        self.__node_3.adopt(self.__node_5)
        self.__node_4.adopt(self.__node_5)
        self.__node_5.adopt(self.__entry_node)
        self.__node_6.adopt(self.__exit_node)
        self.__node_6.adopt(self.__entry_node)

        # CONFIGURATIONS
        self.__prompt_0.options = {
            '1': Command(lambda: self.__entry_node.set_next(self.__node_0), value="Host Name"), 
            '2': Command(lambda: self.__entry_node.set_next(self.__node_1), value="Database Name"), 
            '3': Command(lambda: self.__entry_node.set_next(self.__node_2), value="Port Number"), 
            '4': Command(lambda: self.__entry_node.set_next(self.__node_3), value="Username"), 
            '5': Command(lambda: self.__entry_node.set_next(self.__node_4), value="Password"),
            '6': Command(lambda: self.__entry_node.set_next(self.__exit_node), value="Change Nothing"),
            'D': Command(lambda: self.__entry_node.set_next(self.__node_6), value="Delete Connection")
            }

        self.__prompt_6.options = {
            '1': Command(self._save_changes, value='Save Changes',
                         command=Command(lambda: self.__node_5.set_next(self.__exit_node))),
            '2': Command(lambda: self.__node_5.set_next(self.__exit_node), value='Discard Changes'),
            '3': Command(lambda: self.__node_5.set_next(self.__entry_node), value='Return to Editing')
            }
        
        self.__prompt_7.options = {
            '1': Command(self._delete_connection, value='Yes',
                         command=Command(lambda: self.__node_6.set_next(self.__exit_node))),
            '2': Command(lambda: self.__node_6.set_next(self.__entry_node), value='No')
            }

        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)

    def _save_changes(self):
        connection_info = next(iter(self.connection_to_edit))
        self.connection_manager.update(connection_info)

    def _delete_connection(self):
        connection_info = next(iter(self.connection_to_edit))
        self.connection_manager.delete(connection_info.connection_id)

    def _update_host(self):
        connection_info = next(iter(self.connection_to_edit))
        connection_info.host = self.__prompt_1.responses

    def _update_database(self):
        connection_info = next(iter(self.connection_to_edit))
        connection_info.database = self.__prompt_2.responses

    def _update_port(self):
        connection_info = next(iter(self.connection_to_edit))
        connection_info.port = int(self.__prompt_3.responses)

    def _update_user(self):
        connection_info = next(iter(self.connection_to_edit))
        connection_info.user = self.__prompt_4.responses
    
    def _update_password(self):
        connection_info = next(iter(self.connection_to_edit))
        connection_info.password = self.__prompt_5.responses


class EstablishConnection(NodeBundle):

    def __init__(self, connection_adapter, selected_connection, selection_bundle=None, parent=None):

        """
        Display and shows a successful or a failed connection and allows user for more than one 
        attempts to establish database connection

        Parameters
        ----------
        connection_adapter : database.PostgreSQL or any connection adapter
            the controller of this bundle
        
        selected_connection : list
            may refer to the list in SelectConnection bundle

        selection_bundle : SelectConnection
            any bundle that selects a connection
        """

        name = 'establish-connection'
        self.connection_adapter = connection_adapter

        # OBJECTS
        self.__display_0 = Display("Connecting to \'{database}\' on \'{host}\'...", 
                                                command=Command(lambda: self._format_message(selected_connection)))

        self.__command_0 = Command(lambda: self._execute(selected_connection))
        self.__prompt_0 = Prompt("Connection to database failed. What would you like to do?")
        
        # NODES
        self.__entry_node = Node(self.__display_0, name=f'{name}_connecting-msg',
                                 show_hideout=True, store=False)

        self.__node_0 = Node(self.__command_0, name=f'{name}_connecting', parent=self.__entry_node, 
                             acknowledge=True, store=False)
        self.__node_1 = Node(self.__prompt_0, name=f'{name}_failed', parent=self.__node_0)

        self.__exit_node = DecoyNode(f'{name}_last-node', parent=self.__node_0)

        self.__node_1.adopt(self.__entry_node)

        # CONFIGURATIONS
        self.__prompt_0.options = {
            '1': Command(lambda: self.__node_1.set_next(self.__entry_node), value="Try Again"),
            '2': Command(lambda: self.__node_1.engine_call('quit'), value="Exit application and try again later")
            }

        self.__display_0.exe_seq = 'before'
        self.__command_0.exe_seq = 'before'

        # adds another option for returning to selection
        if selection_bundle:
            self.__node_1.adopt(selection_bundle.entry_node)
            self.__prompt_0.options['R'] = Command(lambda: self.__node_1.set_next(selection_bundle.entry_node), 
                                                   value="Return to selection.")
            
        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)

    def _execute(self, selected_connection):

        connection_info = next(iter(selected_connection))
        self.connection_adapter.connection_info = connection_info

        success, message = self.connection_adapter.connect()

        if success:
            self.__node_0.set_next(self.__exit_node)
            return textformat.apply(message, emphases=['italic'], text_color='green')
        else:
            self.__node_0.set_next(self.__node_1)
            return textformat.apply(f"ERROR: {message}", emphases=['italic'], text_color='red')

    def _format_message(self, selected_connection):

        connection_info = next(iter(selected_connection))
        self.__display_0.format_dict = {'host': connection_info.host, 
                                        'database': connection_info.database}


class QueryExecution(NodeBundle):

    def __init__(self, query_tool, query_edit_bundle=None, parent=None):

        """
        Displays and show the user the process and results of executing query,
        allows for more than one attempts to execute a query

        Parameters
        ----------
        query_tool : database.QueryTool
            the controller of this bundle

        query_edit_bundle : (any bundle that edits a query)
            Refer to classes in vsdb.queries_cli
        """

        name = 'query-execution'
        self.query_tool = query_tool
        
        self.__display_0 = Display("Executing Query...", command=Command(self._execute, respond=True))
        self.__display_1 = Display("Results:\n{message}")
        self.__prompt_0 = Prompt("Failed to run query. What do you want to do?")
        
        self.__entry_node = Node(self.__display_0, name=f'{name}_executing', 
                                 show_hideout=True)

        self.__node_0 = Node(self.__display_1, name=f'{name}_query-results', parent=self.__entry_node)
        self.__node_1 = Node(self.__prompt_0, name=f'{name}_query-failed', parent=self.__entry_node)

        self.__exit_node = DecoyNode(name=f'{name}_last', parent=self.__node_0)
        
        self.__prompt_0.options = {
            '1': Command(lambda: self.__node_1.set_next(self.__entry_node), value="Try Again"),
            '2': Command(lambda: self.__node_1.engine_call('quit'), value="Exit and try again later.")
            }
        
        self.__node_1.adopt(self.__entry_node)

        # adds another option for returning to editing the query params
        if query_edit_bundle:
            self.__node_1.adopt(query_edit_bundle.entry_node)
            self.__prompt_0.options['R'] = Command(lambda: self.__node_1.set_next(query_edit_bundle.entry_node), 
                                                   value='Return to Query Edit')


        super().__init__(self.__entry_node, self.__exit_node, name=name, parent=parent)

    def _execute(self):
        success, message = self.query_tool.run()

        if success:
            self.__display_1.format_dict = {'message': self.query_tool.query_message}
            self.__entry_node.set_next(self.__node_0)
            return textformat.apply(message, emphases=['italic'], text_color='green')
        else:
            self.__entry_node.set_next(self.__node_1)
            return textformat.apply(f"ERROR: {message}", emphases=['italic'], text_color='red')


class ExportQueryResults(pandas_functions_cli.ExportSpreadsheet):

    def __init__(self, query_tool, parent=None):
        
        """
        Asks user where to save the query results

        Parameters
        ----------
        query_tool : database.QueryTool
            the controller of this bundle
        """

        name = 'export-query-results'
        self.query_tool = query_tool

        super().__init__(name, parent)

    def _execute(self):
        return super()._execute(self.query_tool.export)

