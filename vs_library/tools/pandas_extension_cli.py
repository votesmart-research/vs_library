
# built-ins
# from tkinter import Tk, filedialog

# internal packages
from . import pandas_extension
from ..cli import Node, NodeBundle, DecoyNode, textformat
from ..cli.objects import Command, Display, Prompt, Table

# external packages
from PySide6 import QtWidgets


class ImportSpreadsheets(NodeBundle):

    """User can interact with a filedialog to import and read a file"""

    def __init__(self, name, parent=None):

        # name is specified in from child class
        name = name
        self.__filepaths = None
        self.__dfs = []

        # OBJECTS
        self.__display_0 = Display("Opening File Dialog...", command=Command(self._filedialog))
        self.__command_0 = Command(self._execute)
        self.__prompt_0 = Prompt("Error reading file: {error}. What would you like to do?")
        self.__prompt_1 = Prompt("{message}\nWould you like to continue?")
        
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

    def _execute(self, function=None, multiple=False):

        self.__dfs.clear()

        # child class might utilize a specific function to read a file
        messages = []
        successes = []

        if function and not multiple:
            s, m = function(self.__filepaths[0])
            successes.append(s)
            messages.append(m)

        else:
            for filepath in self.__filepaths[0]:

                if function:
                    s, m = function(filepath)
                    successes.append(s)
                    messages.append(m)

                else:
                    df, m = pandas_extension.read_spreadsheet(filepath)
                    successes.append(not df.empty)
                    messages.append(m)
                    self.__dfs.append(df)               

        if all(successes):
            self.__prompt_1.question.format_dict = {'message': "\n".join(messages)}
            self.__node_0.set_next(self.__node_2)
        else:
            self.__prompt_0.question.format_dict = {'error': "\n".join(messages)}
            self.__node_0.set_next(self.__node_1)

    def _filedialog(self):

        # DEPRECATED---->
        # tk = Tk()
        # tk.withdraw()
        # self.__filepaths = filedialog.askopenfilenames(filetypes=[('Spreadsheet files', 
        #                                                          ".xls .xlsx .xlsm .xlsb .ods .csv .tsv")])
        # # to close the file dialog window
        # tk.destroy()
        # <-----

        app = QtWidgets.QApplication()
        dialog = QtWidgets.QFileDialog(parent=None)
        self.__filepaths = dialog.getOpenFileNames(filter="Spreadsheet files (*.xls *.xlsx *.xlsm *.xlsb *.ods *.csv *.tsv")
        app.shutdown()
        
        if not self.__filepaths[0]:
            self.__display_0.command.respond = True
            self.__entry_node.acknowledge = True
            self.__entry_node.set_next(self.__entry_node)
            return textformat.apply("Filepath is not set. Please try again.", emphases=['italic'], text_color='red')
        else:
            self.__display_0.command.respond = False
            self.__entry_node.acknowledge = False
            self.__entry_node.set_next(self.__node_0)
 
    @property
    def dfs(self):
        return self.__dfs


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
            success, message = function(self.__filepath[0])
        else:
            success, message = pandas_extension.to_spreadsheet(df, self.__filepath[0])

        if success:
            self.__node_0.set_next(self.__exit_node)
            self.__command_0.respond = True
            return textformat.apply(message, emphases=['italic'], text_color='green')

        else:
            self.__node_0.set_next(self.__node_1)
            self.__prompt_1.question.format_dict = {'error': message}
            self.__command_0.respond = False
        

    def _filedialog(self):

        # DEPRECATED---->
        # tk = Tk()
        # tk.withdraw()

        # self.__filepath = filedialog.asksaveasfilename(filetypes=[('Spreadsheet files', 
        #                                                            ".ods .xlsx .xlsm .xlsb .ods .csv .tsv")])
        # # to close the file dialog window
        # tk.destroy()
        # <-----

        app = QtWidgets.QApplication()
        dialog = QtWidgets.QFileDialog(parent=None)
        self.__filepath = dialog.getSaveFileName(filter="Spreadsheet files (*.xls *.xlsx *.xlsm *.xlsb *.ods *.csv *.tsv")
        app.shutdown()

        if not self.__filepath[0]:
            self.__display_0.command.respond = True
            self.__entry_node.acknowledge = True
            self.__entry_node.set_next(self.__entry_node)
            return textformat.apply("Filepath is not set. Please try again.", emphases=['italic'], text_color='red')
        else:
            self.__display_0.command.respond = False
            self.__entry_node.acknowledge = False
            self.__entry_node.set_next(self.__node_0)

def _verify_threshold(t):
    try:
        if float(t)>=0 and float(t)<=100:
            return True
        else:
            return False, "Enter a number between 0 to 100, as this denotes percentage."
    except:
        return False, "Enter a number between 0 to 100, as this denotes percentage."


class PMSettings(NodeBundle):

    def __init__(self, pandas_matcher, parent=None):

        name = "pandasmatcher-settings"
        self.pandas_matcher = pandas_matcher
        
        # OBJECTS
        self.__display_0 = Display(textformat.apply("Pandas Matcher Settings", emphases=['bold', 'underline']))
        self.__prompt_0 = Prompt("Choose the following:")
        self.__prompt_1 = Prompt("Enter new threshold between 0 to 100", verification=_verify_threshold,
                                 command=Command(self._set_threshold))

        # NODES
        self.__entry_node = Node(self.__display_0, name=f'{name}_first-node',
                                 show_hideout=True, clear_screen=True)
        self.__node_0 = Node(self.__prompt_0, name=f'{name}_choose', parent=self.__entry_node,
                             store=False)
        self.__node_1 = Node(self.__prompt_1, parent=self.__node_0,
                             store=False)

        self.__bundle_0 = PMSetColumnThreshold(pandas_matcher, parent=self.__entry_node)
        self.__bundle_1 = PMSetColumnsToMatch(pandas_matcher, parent=self.__entry_node)
        self.__bundle_2 = PMSetColumnsToGet(pandas_matcher, parent=self.__entry_node)

        self.__exit_node = DecoyNode(name=f'{name}_last-node')

        self.__node_0.adopt(self.__entry_node)
        self.__node_0.adopt(self.__bundle_0.entry_node)
        self.__node_0.adopt(self.__bundle_1.entry_node)
        self.__node_0.adopt(self.__bundle_2.entry_node)
        self.__node_1.adopt(self.__entry_node)

        self.__entry_node.set_next(self.__node_0)
    
        # CONFIGURATION
        format_threshold = textformat.apply(str(self.pandas_matcher.required_threshold), emphases=['bold', 'underline'])
        self.__format_yes = textformat.apply("YES", emphases=['bold', 'italic'], text_color='bright_red')
        self.__format_no = textformat.apply("NO", emphases=['bold', 'italic'], text_color='bright_green')

        self.__prompt_0.options = {
            '1': Command(lambda: self.__node_0.set_next(self.__bundle_0.entry_node), value="Set Column Threshold"),
            '2': Command(lambda: self.__node_0.set_next(self.__bundle_1.entry_node), value="Set Columns To Match"),
            '3': Command(lambda: self.__node_0.set_next(self.__bundle_2.entry_node), value="Set Columns to Get"),
            '4': Display("Toggle Cutoff: {status}", format_dict={'status': self.__format_yes if pandas_matcher.cutoff 
                                                                  else self.__format_no},
                                                     command=Command(self._toggle_cutoff,
                                                     command=Command(lambda: self.__node_0.set_next(self.__entry_node)))),

            '5': Display("Required Threshold: {value}", format_dict={'value': format_threshold},
                         command=Command(lambda: self.__node_0.set_next(self.__node_1)))
        }

        if isinstance(parent, Node):
            self.__node_0.adopt(parent)
            self.__prompt_0.options['R'] = Command(lambda: self.__node_0.set_next(parent), value="Return")
        elif isinstance(parent, NodeBundle):
            self.__node_0.adopt(parent.entry_node)
            self.__prompt_0.options['R'] = Command(lambda: self.__node_0.set_next(parent.entry_node), value="Return")
        
        super().__init__(self.__entry_node, self.__exit_node, name=name, parent=parent)
    
    def _toggle_cutoff(self):
        self.pandas_matcher.cutoff = not self.pandas_matcher.cutoff

        if self.pandas_matcher.cutoff:
            self.__prompt_0.options['4'].format_dict['status'] = self.__format_yes
        else:
            self.__prompt_0.options['4'].format_dict['status'] = self.__format_no

    def _set_threshold(self):
        self.pandas_matcher.required_threshold = float(self.__prompt_1.responses)
        format_threshold = textformat.apply(str(self.pandas_matcher.required_threshold), emphases=['bold', 'underline'])
        self.__prompt_0.options['5'].format_dict = {'value': format_threshold}


class PMSetColumnThreshold(NodeBundle):
    
    def __init__(self, pandas_matcher, parent=None):

        name = "pandasmatcher_set-column-threshold"
        self.pandas_matcher = pandas_matcher
        
        # OBJECTS
        self.__table_0 = Table([['Options', 'Column', 'Threshold']], command=Command(self._populate_table))
        self.__prompt_0 = Prompt("Select a column by the options", verification=self._verify_selection)
        self.__prompt_1 = Prompt("What is the threshold you would like to change to?", 
                                 verification=_verify_threshold, command=Command(self._execute))
        self.__prompt_2 = Prompt("Do you want to set another threshold?")

        # NODES
        self.__entry_node = Node(self.__table_0, name=name,
                                 store=False)
        
        self.__node_0 = Node(self.__prompt_0, name=f'{name}_select', parent=self.__entry_node,
                             store=False)
        self.__node_1 = Node(self.__prompt_1, name=f'{name}_change', parent=self.__node_0,
                             store=False)
        self.__node_2 = Node(self.__prompt_2, name=f'{name}_set-another', parent=self.__node_1,
                             store=False)

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

    def _execute(self):
        r = int(self.__prompt_0.responses)
        new_threshold = float(self.__prompt_1.responses)

        if r and new_threshold:
            column = dict(enumerate(self.pandas_matcher.column_threshold, 1))[int(r)]
            self.pandas_matcher.column_threshold[column] = new_threshold

    def _verify_selection(self, s):
        try:
            if int(s) in dict(enumerate(self.pandas_matcher.column_threshold, 1)).keys():
                return True
            else:
                return False, "Option is not available."
        except:
            return False, "Option is not available."

    def _populate_table(self):
        self.__table_0.clear()
        for option, (column, threshold) in enumerate(map(tuple,self.pandas_matcher.column_threshold.items()),1):
            self.__table_0.table.append([option, column, threshold])
        

class PMSetColumnsToMatch(NodeBundle):
    def __init__(self, pandas_matcher, parent=None):

        name = "pandas-matcher_set-column-match"
        self.pandas_matcher = pandas_matcher
        
        # OBJECTS
        self.__table_0 = Table([["Columns to Match", "Match With"]], command=Command(self._populate_table))
        self.__prompt_0 = Prompt("What would you like to change?")
        
        # NODES
        self.__entry_node = Node(self.__table_0, name=name)
        self.__node_0 = Node(self.__prompt_0, name=f"{name}_select-change", parent=self.__entry_node,
                             store=False)
        self.__exit_node = DecoyNode(name=f"{name}_last-node", parent=self.__node_0)

        self.__bundle_0 = _PMToMatch(pandas_matcher, self.__table_0, self.__entry_node, parent=self.__node_0)
        self.__bundle_1 = _PMMatchWith(pandas_matcher, self.__table_0, self.__entry_node, parent=self.__node_0)

        # CONFIGURATIONS
        self.__prompt_0.options = {
            '1': Command(lambda: self.__node_0.set_next(self.__bundle_0.entry_node), value="Columns to Match"),
            '2': Command(lambda: self.__node_0.set_next(self.__bundle_1.entry_node), value="Match With")
        }

        self.__table_0.table_header = "Set Columns to Match"
        self.__table_0.description = "Shows the columns to match and columns to be match with"
        
        if isinstance(parent, Node):
            self.__node_0.adopt(parent)
            self.__prompt_0.options['R'] = Command(lambda: self.__node_0.set_next(parent), value='Return')
        elif isinstance(parent, NodeBundle):
            self.__node_0.adopt(parent.entry_node)
            self.__prompt_0.options['R'] = Command(lambda: self.__node_0.set_next(parent.entry_node), value='Return')

        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)

    def _populate_table(self):
        self.__table_0.clear()
        for column, match_with in self.pandas_matcher.columns_to_match.items():
            self.__table_0.table.append([column, ", ".join(match_with)])


class _PMToMatch(NodeBundle):

    def __init__(self, pandas_matcher, full_table, return_node, parent=None):

        name = "pandas-matcher_to-match"
        self.pandas_matcher = pandas_matcher
        
        # OBJECTS
        self.__prompt_0 = Prompt("Select the following action:")
        self.__prompt_1 = Prompt("Which column would you like to add?", multiple_selection=True,
                                 command=Command(self._populate_prompt_add))
        self.__prompt_2 = Prompt("Which column would you like to remove?", multiple_selection=True, 
                                 command=Command(self._populate_prompt_remove))

        # NODES
        self.__entry_node = Node(full_table, name=name,
                                 store=False)
        self.__node_0 = Node(self.__prompt_0, name=f"{name}_select-action", parent=self.__entry_node)
        self.__node_1 = Node(self.__prompt_1, name=f"{name}_add-col", parent=self.__node_0)
        self.__node_2 = Node(self.__prompt_2, name=f"{name}_remove-col", parent=self.__node_0)
        self.__exit_node = DecoyNode(name=f"{name}_not-an-exit")

        self.__node_0.adopt(return_node)
        self.__node_1.adopt(self.__entry_node)
        self.__node_2.adopt(self.__entry_node)

        # CONFIGURATIONS
        self.__prompt_0.options = {
            '1': Command(lambda: self.__node_0.set_next(self.__node_1), value="Add columns"),
            '2': Command(lambda: self.__node_0.set_next(self.__node_2), value="Remove columns"),
            'R': Command(lambda: self.__node_0.set_next(return_node), value='Return')
        }

        self.__prompt_1.exe_seq = 'before'
        self.__prompt_2.exe_seq = 'before'

        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)

    def _populate_prompt_add(self):

        self.__prompt_1.options.clear()

        columns = self.pandas_matcher.columns_to_match.keys()
        columns_df_from = self.pandas_matcher.df_from.columns

        columns_not_added = [c for c in self.pandas_matcher.df_to.columns if c not in columns]

        def _add(self, column):
            self.pandas_matcher.column_threshold[column] = self.pandas_matcher.required_threshold
            self.pandas_matcher.columns_to_match[column] = [column] if column in columns_df_from else []

        for index, column in enumerate(columns_not_added, 1):
            self.__prompt_1.options[str(index)] = Command(lambda column=column: _add(self, column), value=column)

        self.__prompt_1.options['R'] = Command(lambda: self.__node_1.set_next(self.__entry_node), value="Return")
 
    def _populate_prompt_remove(self):

        self.__prompt_2.options.clear()
        
        def _remove(self, column):
            self.pandas_matcher.column_threshold.pop(column)
            self.pandas_matcher.columns_to_match.pop(column)

        columns_to = self.pandas_matcher.columns_to_match.keys()
        
        for index, column in enumerate(columns_to, 1):
            self.__prompt_2.options[str(index)] = Command(lambda column=column: _remove(self, column), value=column)

        self.__prompt_2.options['R'] = Command(lambda: self.__node_2.set_next(self.__entry_node), value="Return")


class _PMMatchWith(NodeBundle):

    def __init__(self, pandas_matcher, full_table, return_node, parent=None):

        name = "pandas-matcher_match-with"
        self.pandas_matcher = pandas_matcher

        # OBJECTS
        self.__prompt_0 = Prompt("Select a column in 'Columns to Match'", 
                                 command=Command(lambda: self._populate_prompt(return_node)))
        self.__table_0 = Table([['Columns to Match', 'Match With']],
                               command=Command(self._populate_table))
        self.__prompt_1 = Prompt("Select the following action:")
        self.__prompt_2 = Prompt("Which column would you like to add?", multiple_selection=True,
                                 command=Command(self._populate_prompt_add))
        self.__prompt_3 = Prompt("Which column would you like to remove?",multiple_selection=True,
                                 command=Command(self._populate_prompt_remove))
        
        # NODES
        self.__entry_node = Node(full_table)
        self.__node_0 = Node(self.__prompt_0, name=f"{name}_select-column", parent=self.__entry_node)
        self.__node_1 = Node(self.__table_0, name=f"{name}_match-with", parent=self.__node_0)
        self.__node_2 = Node(self.__prompt_1, name=f"{name}_select-action", parent=self.__node_1)
        self.__node_3 = Node(self.__prompt_2, name=f"{name}_add-col", parent=self.__node_2)
        self.__node_4 = Node(self.__prompt_3, name=f"{name}_remove-col", parent=self.__node_2)
        self.__exit_node = DecoyNode()

        self.__node_0.adopt(return_node)
        self.__node_2.adopt(self.__entry_node)
        self.__node_3.adopt(self.__node_1)
        self.__node_4.adopt(self.__node_1)

        # CONFIGURATIONS
        self.__prompt_0.exe_seq = 'before'

        self.__prompt_1.options = {
            '1': Command(lambda: self.__node_2.set_next(self.__node_3), value="Add columns"),
            '2': Command(lambda: self.__node_2.set_next(self.__node_4), value="Remove columns"),
            'R': Command(lambda: self.__node_2.set_next(self.__entry_node), value='Return')
        }

        self.__prompt_2.exe_seq = 'before'
        self.__prompt_3.exe_seq = 'before'

        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)

    def _populate_prompt(self, return_node):

        self.__prompt_0.options.clear()

        columns_to = self.pandas_matcher.columns_to_match.keys()

        for index, column in enumerate(columns_to, 1):
            self.__prompt_0.options[str(index)] = Command(lambda: self.__node_0.set_next(self.__node_1), value=column)

        self.__prompt_0.options['R'] = Command(lambda: self.__node_0.set_next(return_node), value="Return")

    def _populate_table(self):

        self.__table_0.clear()
        chosen_column = self.__prompt_0.option_responses()

        self.__table_0.table += [[chosen_column, ", ".join(self.pandas_matcher.columns_to_match[chosen_column])]]

    def _populate_prompt_add(self):

        self.__prompt_2.options.clear()

        chosen_column = self.__prompt_0.option_responses()

        columns = self.pandas_matcher.columns_to_match[chosen_column]
        columns_not_added = [c for c in self.pandas_matcher.df_from.columns if c not in columns]

        for index, column in enumerate(columns_not_added, 1):
            self.__prompt_2.options[str(index)] = Command(lambda column=column: columns.append(column), value=column)
        
        self.__prompt_2.options['R'] = Command(lambda: self.__node_3.set_next(self.__node_1), value="Return")

    def _populate_prompt_remove(self):

        self.__prompt_3.options.clear()

        chosen_column = self.__prompt_0.option_responses()

        columns = self.pandas_matcher.columns_to_match[chosen_column]

        for index, column in enumerate(columns, 1):
            self.__prompt_3.options[str(index)] = Command(lambda column=column: columns.remove(column), value=column)
        
        self.__prompt_3.options['R'] = Command(lambda: self.__node_4.set_next(self.__node_1), value="Return")


class PMSetColumnsToGet(NodeBundle):
    def __init__(self, pandas_matcher, parent=None):

        name = "pandas-matcher_set-columns-get"
        self.pandas_matcher = pandas_matcher
        
        # OBJECTS
        self.__table_0 = Table([['Columns to Get']],
                               command=Command(self._populate_table))
        self.__prompt_0 = Prompt("Select the following action:")
        self.__prompt_1 = Prompt("What column would you like to add?", multiple_selection=True,
                                 command=Command(self._populate_prompt_add))
        self.__prompt_2 = Prompt("What column would you like to remove?", multiple_selection=True,
                                 command=Command(self._populate_prompt_remove))

        # NODES
        self.__entry_node = Node(self.__table_0, name=f"{name}_columns",
                                 clear_screen=True)
        self.__node_0 = Node(self.__prompt_0, name=f"{name}_select-action", parent=self.__entry_node)
        self.__node_1 = Node(self.__prompt_1, name=f"{name}_add-column", parent=self.__node_0)
        self.__node_2 = Node(self.__prompt_2, name=f"{name}_remove-column", parent=self.__node_0)
        self.__exit_node = DecoyNode()

        self.__node_1.adopt(self.__entry_node)
        self.__node_2.adopt(self.__entry_node)

        # CONFIGURATIONS
        self.__prompt_1.exe_seq = 'before'
        self.__prompt_2.exe_seq = 'before'

        self.__prompt_0.options = {
            '1': Command(lambda: self.__node_0.set_next(self.__node_1), value="Add columns"),
            '2': Command(lambda: self.__node_0.set_next(self.__node_2), value="Remove columns")
        }

        if isinstance(parent, Node):
            self.__node_0.adopt(parent)
            self.__prompt_0.options ['R'] = Command(lambda: self.__node_0.set_next(parent), value="Return")
        elif isinstance(parent, NodeBundle):
            self.__node_0.adopt(parent.entry_node)
            self.__prompt_0.options ['R'] = Command(lambda: self.__node_0.set_next(parent.entry_node), value="Return")

        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)

    def _populate_table(self):
        self.__table_0.clear()
        for column in self.pandas_matcher.columns_to_get:
            self.__table_0.table.append([column])

    def _populate_prompt_add(self):
        self.__prompt_1.options.clear()

        columns = self.pandas_matcher.columns_to_get
        columns_not_added = [c for c in self.pandas_matcher.df_from.columns if c not in columns]

        for index, column in enumerate(columns_not_added, 1):
            self.__prompt_1.options[str(index)] = Command(lambda column=column: columns.append(column), value=column)

        self.__prompt_1.options['R'] = Command(lambda: self.__node_1.set_next(self.__entry_node), value="Return")

    def _populate_prompt_remove(self):
        
        self.__prompt_2.options.clear()
        columns = self.pandas_matcher.columns_to_get

        for index, column in enumerate(columns, 1):
            self.__prompt_2.options[str(index)] = Command(lambda column=column: columns.remove(column), value=column)

        self.__prompt_2.options['R'] = Command(lambda: self.__node_2.set_next(self.__entry_node), value="Return")
        