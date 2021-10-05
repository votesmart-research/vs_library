
# built-ins
from tkinter import Tk, filedialog

# internal packages
from . import pandas_functions
from ..cli import Node, NodeBundle, DecoyNode, textformat
from ..cli.objects import Command, Display, Prompt


class ImportSpreadsheet(NodeBundle):

    def __init__(self, name, parent=None):

        name = name
        self.__filepath = None

        # OBJECTS
        self.__display_0 = Display("Opening File Dialog...", command=Command(self._filedialog))
        self.__command_0 = Command(self._execute)
        self.__prompt_0 = Prompt("Error reading file: {error}. What would you like to do?")
        self.__prompt_1 = Prompt("{message}. Would you like to continue?")
        
        # NODES
        self.__entry_node = Node(self.__display_0, name=f'{name}_file-dialog', 
                             show_instructions=True)

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

    def _execute(self, method=None):
        if method:
            success, message = method(self.__filepath)
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

    def __init__(self, name, parent=None):

        name = name
        self.__filepath = None
        
        # OBJECTS
        self.__display_0 = Display("Opening File Dialog...", command=Command(self._filedialog))
        self.__command_0 = Command(self._execute)
        self.__prompt_1 = Prompt("Error exporting file: {error}. What would you like to do?")

        # NODES
        self.__entry_node = Node(self.__display_0, name=f'{name}_file-dialog',
                             clear_screen=True, show_instructions=True)
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

    def _execute(self, controller=None, df=None):
        if controller:
            success, message = controller(self.__filepath)
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

        self.__filepath = filedialog.asksaveasfilename(filetypes=[('Spreadsheet files', ".ods .xlsx .xlsm \
                                                                                         .xlsb .ods .csv .tsv")])
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
