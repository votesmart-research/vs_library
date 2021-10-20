
# built-ins
from tkinter import Tk, filedialog

import pandas

# internal packages
from . import pandas_functions
from ..cli import Node, NodeBundle, DecoyNode, textformat
from ..cli.objects import Command, Display, Prompt, Table


class ImportSpreadsheet(NodeBundle):

    """User can interact with a filedialog to import and read a file"""

    def __init__(self, name, parent=None):

        # name is specified in from child class
        name = name
        self.__filepath = None

        # OBJECTS
        self.__display_0 = Display("Opening File Dialog...", command=Command(self._filedialog))
        self.__command_0 = Command(self._execute)
        self.__prompt_0 = Prompt("Error reading file: {error}. What would you like to do?")
        self.__prompt_1 = Prompt("{message}. Would you like to continue?")
        
        # NODES
        self.__entry_node = Node(self.__display_0, name=f'{name}_file-dialog', 
                             show_hideout=True)

        self.__node_0 = Node(self.__command_0, name=f'{name}_read-file', parent=self.__entry_node, 
                             store=False)
        self.__node_1 = Node(self.__prompt_0, name=f'{name}_error', parent=self.__node_0,
                             store=False)
        self.__node_2 = Node(self.__prompt_1, name=f'{name}_continue', parent=self.__node_0,
                             store=False)

        self.__exit_node = DecoyNode(name=f'{name}_last-node', parent=self.__node_2)

        self.__entry_node.adopt(self.__entry_node)
        self.__node_1.adopt(self.__entry_node)
        self.__node_1.adopt(self.__node_0)
        self.__node_2.adopt(self.__entry_node)

        # CONFIGURATIONS
        self.__prompt_0.options = {
            '1': Command(lambda: self.__node_1.set_next(self.__node_0), value="Try Again"), 
            '2': Command(lambda: self.__node_1.set_next(self.__entry_node), value="Select a different file"),
            '3': Command(lambda: self.__node_1.engine_call('quit'), value="Exit Application")
            }

        self.__prompt_1.options = {
            '1': Command(lambda: self.__node_2.set_next(self.__exit_node), value="Yes"),
            '2': Command(lambda: self.__node_2.set_next(self.__entry_node), value="Select a different file")
            }
        
        self.__command_0.exe_seq = 'before'

        super().__init__(self.__entry_node, self.__exit_node, name=name, parent=parent)

    def _execute(self, function=None):

        # child class might utilize a specific function to read a file
        if function:
            success, message = function(self.__filepath)
        else:
            df, message = pandas_functions.read_spreadsheet(self.__filepath)
            success = not df.empty

        if success:
            self.__prompt_1.question.format_dict = {'message': message}
            self.__node_0.set_next(self.__node_2)
        else:
            self.__prompt_0.question.format_dict = {'error': message}
            self.__node_0.set_next(self.__node_1)

    def _filedialog(self):
        tk = Tk()
        tk.withdraw()
        self.__filepath = filedialog.askopenfilename(filetypes=[('Spreadsheet files', 
                                                                 ".xls .xlsx .xlsm .xlsb .ods .csv .tsv")])
        # to close the file dialog window
        tk.destroy()

        if not self.__filepath:
            self.__display_0.command.respond = True
            self.__entry_node.acknowledge = True
            self.__entry_node.set_next(self.__entry_node)
            return textformat.apply("Filepath is not set. Please try again.", emphases=['italic'], text_color='red')
        else:
            self.__display_0.command.respond = False
            self.__entry_node.acknowledge = False
            self.__entry_node.set_next(self.__node_0)


class ExportSpreadsheet(NodeBundle):

    """Allow user to interact with a filedialog to export data to a spreadsheet"""

    def __init__(self, name, parent=None):
        
        # name is specified in from child class
        name = name
        self.__filepath = None
        
        # OBJECTS
        self.__display_0 = Display("Opening File Dialog...", command=Command(self._filedialog))
        self.__command_0 = Command(self._execute)
        self.__prompt_1 = Prompt("Error exporting file: {error}. What would you like to do?")

        # NODES
        self.__entry_node = Node(self.__display_0, name=f'{name}_file-dialog',
                             clear_screen=True, show_hideout=True)
        self.__node_0 = Node(self.__command_0, name=f'{name}_export-file', parent=self.__entry_node,
                             acknowledge=True, store=False)
        self.__node_1 = Node(self.__prompt_1, name=f'{name}_error', parent=self.__node_0,
                             store=False)
        self.__exit_node = DecoyNode(name=f'{name}_last-node', parent=self.__node_0)

        self.__entry_node.adopt(self.__entry_node)
        self.__entry_node.adopt(self.__exit_node)
        self.__node_1.adopt(self.__entry_node)
        self.__node_1.adopt(self.__node_0)

        # CONFIGURATIONS
        self.__prompt_1.options = {'1': Command(lambda: self.__node_1.set_next(self.__node_0), value="Try Again"), 
                                   '2': Command(lambda: self.__node_1.set_next(self.__entry_node), value="Pick another location or name"),
                                   '3': Command(lambda: self.__node_1.engine_call('quit'), value="Do not export and exit")}

        self.__command_0.exe_seq = 'before'

        super().__init__(self.__entry_node, self.__exit_node, name=name, parent=parent)

    def _execute(self, function=None, df=None):
        if function:
            success, message = function(self.__filepath)
        else:
            success, message = pandas_functions.to_spreadsheet(df, self.__filepath)

        if success:
            self.__node_0.set_next(self.__exit_node)
            self.__command_0.respond = True
            return textformat.apply(message, emphases=['italic'], text_color='green')

        else:
            self.__node_0.set_next(self.__node_1)
            self.__prompt_1.question.format_dict = {'error': message}
            self.__command_0.respond = False
        

    def _filedialog(self):
        tk = Tk()
        tk.withdraw()

        self.__filepath = filedialog.asksaveasfilename(filetypes=[('Spreadsheet files', 
                                                                   ".ods .xlsx .xlsm .xlsb .ods .csv .tsv")])
        # to close the file dialog window
        tk.destroy()

        if not self.__filepath:
            self.__display_0.command.respond = True
            self.__entry_node.acknowledge = True
            self.__entry_node.set_next(self.__entry_node)
            return textformat.apply("Filepath is not set. Please try again.", emphases=['italic'], text_color='red')
        else:
            self.__display_0.command.respond = False
            self.__entry_node.acknowledge = False
            self.__entry_node.set_next(self.__node_0)


class PMMainMenu(NodeBundle):

    def __init__(self, pandas_matcher, parent=None):

        name = "pandasmatcher_main-menu"
        
        # OBJECTS
        self.__display_0 = Display("PandasMatcher Main Menu")
        self.__prompt_0 = Prompt("Choose the following")

        # NODES
        self.__entry_node = Node(self.__display_0, name=f'{name}_first-node',
                                 show_hideout=True)
        self.__node_0 = Node(self.__prompt_0, name=f'{name}_choose', parent=self.__entry_node,
                             store=False)

        self.__bundle_0 = PMSetColumnThreshold(pandas_matcher, parent=self.__node_0)
        self.__bundle_1 = PMSetColumnsToMatch(pandas_matcher, parent=self.__node_0)
        self.__bundle_2 = PMSetColumnsToGet(pandas_matcher, parent=self.__node_0)
        self.__bundle_3 = PMAdditionalSettings(pandas_matcher, parent=self.__node_0)
        self.__bundle_4 = PMCommenceMatch(pandas_matcher, parent=self.__node_0)

        self.__exit_node = DecoyNode(name=f'{name}_last-node')

        self.__bundle_4.adopt(self.__exit_node)
    
        # CONFIGURATION

        self.__prompt_0.options = {
            '1': Command(self.__node_0.set_next(self.__bundle_0.entry_node), value="Set Column Threshold"),
            '2': Command(self.__node_0.set_next(self.__bundle_1.entry_node), value="Set Columns To Match"),
            '3': Command(self.__node_0.set_next(self.__bundle_2.entry_node), value="Set Columns to Get"),
            '4': Command(self.__node_0.set_next(self.__bundle_3.entry_node), value="Additional Settings"),
            'M': Command(self.__node_0.set_next(self.__bundle_4.entry_node), value="Commence Match"),
        }

        if isinstance(parent, Node):
            self.__node_0.adopt(parent)
            self.__prompt_0.options['R'] = Command(self.__node_0.set_next(parent), value="Return")
        elif isinstance(parent, NodeBundle):
            self.__node_0.adopt(parent.entry_node)
            self.__prompt_0.options['R'] = Command(self.__node_0.set_next(parent.entry_node), value="Return")
        

class PMSetColumnThreshold(NodeBundle):
    
    def __init__(self, pandas_matcher, parent=None):

        name = "pandasmatcher_set-column-threshold"
        self.pandas_matcher = pandas_matcher
        
        # OBJECTS
        self.__table_0 = Table([['Options', 'Column', 'Threshold']], command=self._populate_table)
        self.__prompt_0 = Prompt("Select the column to change (by the options)")
        self.__prompt_1 = Prompt("What is the threshold you would like to change to?")
        self.__prompt_2 = Prompt("Do you want to set another column's threshold?")

        # NODES
        self.__entry_node = Node(self.__table_0, name=name)
        self.__node_0 = Node(self.__prompt_0, name=f'{name}_select', parent=self.__entry_node,
                             store=False)
        self.__node_1 = Node(self.__prompt_1, name=f'{name}_change', parent=self.__node_0,
                             store=False)
        self.__node_2 = Node(self.__prompt_2, name=f'{name}_set-another', parent=self.__node_1)
        self.__exit_node = DecoyNode()

        self.__node_2.adopt(self.__entry_node)

        # CONFIGURATIONS
        self.__prompt_2.options = {
            '1': Command(lambda: self.__node_2.set_next(self.__entry_node), value='Yes'),
            '2': Command(lambda: self.__node_2.set_next(self.__exit_node), value='No')
        }

        if isinstance(parent, Node):
            self.__node_2.adopt(parent)
            self.__prompt_2.options['2'] = Command(lambda: self.__node_2.set_next(parent), value='No')
        elif isinstance(parent, NodeBundle):
            self.__node_2.adopt(parent.entry_node)
            self.__prompt_2.options['2'] = Command(lambda: self.__node_2.set_next(parent.entry_node), value='No')

        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)

    def _populate_table(self):
        pass


class PMSetColumnsToMatch(NodeBundle):
    def __init__(self, pandas_matcher, parent=None):

        name = ""
        self.pandas_matcher = pandas_matcher
        
        # OBJECTS


        # NODES
        self.__entry_node = Node()
        self.__exit_node = DecoyNode()

        # CONFIGURATIONS

        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)


class PMSetColumnsToGet(NodeBundle):
    def __init__(self, pandas_matcher, parent=None):

        name = ""
        self.pandas_matcher = pandas_matcher
        
        # OBJECTS


        # NODES
        self.__entry_node = Node()
        self.__exit_node = DecoyNode()

        # CONFIGURATIONS

        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)


class PMAdditionalSettings(NodeBundle):
    def __init__(self, pandas_matcher, parent=None):

        name = ""
        self.pandas_matcher = pandas_matcher
        
        # OBJECTS


        # NODES
        self.__entry_node = Node()
        self.__exit_node = DecoyNode()

        # CONFIGURATIONS

        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)


class PMCommenceMatch(NodeBundle):
    pass