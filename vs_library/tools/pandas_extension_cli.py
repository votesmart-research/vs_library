
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
        self.__display_0 = Display(
            "Opening File Dialog...", command=Command(self._filedialog)
        )
        self.__command_0 = Command(self._execute)
        self.__prompt_0 = Prompt(
            "Error reading file: {error}. What would you like to do?"
        )
        self.__prompt_1 = Prompt("{message}\nWould you like to continue?")

        # NODES
        self.__entry_node = Node(
            self.__display_0, name=f"{name}_file-dialog", show_hideout=True
        )

        self.__node_0 = Node(
            self.__command_0,
            name=f"{name}_read-file",
            parent=self.__entry_node,
            store=False,
        )
        self.__node_1 = Node(
            self.__prompt_0, name=f"{name}_error", parent=self.__node_0, store=False
        )
        self.__node_2 = Node(
            self.__prompt_1, name=f"{name}_continue", parent=self.__node_0, store=False
        )

        self.__exit_node = DecoyNode(name=f"{name}_last-node", parent=self.__node_2)

        self.__entry_node.adopt(self.__entry_node)
        self.__node_1.adopt(self.__entry_node)
        self.__node_1.adopt(self.__node_0)
        self.__node_2.adopt(self.__entry_node)

        # CONFIGURATIONS
        self.__prompt_0.options = {
            "1": Command(
                lambda: self.__node_1.set_next(self.__node_0), value="Try Again"
            ),
            "2": Command(
                lambda: self.__node_1.set_next(self.__entry_node),
                value="Select a different file",
            ),
            "3": Command(
                lambda: self.__node_1.engine_call("quit"), value="Exit Application"
            ),
        }

        self.__prompt_1.options = {
            "1": Command(lambda: self.__node_2.set_next(self.__exit_node), value="Yes"),
            "2": Command(
                lambda: self.__node_2.set_next(self.__entry_node),
                value="Select a different file",
            ),
        }

        self.__command_0.exe_seq = "before"

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
            self.__prompt_1.question.format_dict = {"message": "\n".join(messages)}
            self.__node_0.set_next(self.__node_2)
        else:
            self.__prompt_0.question.format_dict = {"error": "\n".join(messages)}
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
        self.__filepaths = dialog.getOpenFileNames(
            filter="Spreadsheet files (*.xls *.xlsx *.xlsm *.xlsb *.ods *.csv *.tsv"
        )
        app.shutdown()

        if not self.__filepaths[0]:
            self.__display_0.command.respond = True
            self.__entry_node.acknowledge = True
            self.__entry_node.set_next(self.__entry_node)
            return textformat.apply(
                "Filepath is not set. Please try again.",
                emphases=["italic"],
                text_color="red",
            )
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
        self.__display_0 = Display(
            "Opening File Dialog...", command=Command(self._filedialog)
        )
        self.__command_0 = Command(self._execute)
        self.__prompt_1 = Prompt(
            "Error exporting file: {error}. What would you like to do?"
        )

        # NODES
        self.__entry_node = Node(
            self.__display_0,
            name=f"{name}_file-dialog",
            clear_screen=True,
            show_hideout=True,
        )
        self.__node_0 = Node(
            self.__command_0,
            name=f"{name}_export-file",
            parent=self.__entry_node,
            acknowledge=True,
            store=False,
        )
        self.__node_1 = Node(
            self.__prompt_1, name=f"{name}_error", parent=self.__node_0, store=False
        )
        self.__exit_node = DecoyNode(name=f"{name}_last-node", parent=self.__node_0)

        self.__entry_node.adopt(self.__entry_node)
        self.__entry_node.adopt(self.__exit_node)
        self.__node_1.adopt(self.__entry_node)
        self.__node_1.adopt(self.__node_0)

        # CONFIGURATIONS
        self.__prompt_1.options = {
            "1": Command(
                lambda: self.__node_1.set_next(self.__node_0), value="Try Again"
            ),
            "2": Command(
                lambda: self.__node_1.set_next(self.__entry_node),
                value="Pick another location or name",
            ),
            "3": Command(
                lambda: self.__node_1.engine_call("quit"),
                value="Do not export and exit",
            ),
        }

        self.__command_0.exe_seq = "before"

        super().__init__(self.__entry_node, self.__exit_node, name=name, parent=parent)

    def _execute(self, function=None, df=None):
        if function:
            success, message = function(self.__filepath[0])
        else:
            success, message = pandas_extension.to_spreadsheet(df, self.__filepath[0])

        if success:
            self.__node_0.set_next(self.__exit_node)
            self.__command_0.respond = True
            return textformat.apply(message, emphases=["italic"], text_color="green")

        else:
            self.__node_0.set_next(self.__node_1)
            self.__prompt_1.question.format_dict = {"error": message}
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
        self.__filepath = dialog.getSaveFileName(
            filter="Spreadsheet files (*.xls *.xlsx *.xlsm *.xlsb *.ods *.csv *.tsv"
        )
        app.shutdown()

        if not self.__filepath[0]:
            self.__display_0.command.respond = True
            self.__entry_node.acknowledge = True
            self.__entry_node.set_next(self.__entry_node)
            return textformat.apply(
                "Filepath is not set. Please try again.",
                emphases=["italic"],
                text_color="red",
            )
        else:
            self.__display_0.command.respond = False
            self.__entry_node.acknowledge = False
            self.__entry_node.set_next(self.__node_0)


def _verify_threshold(t):
    try:
        if float(t) >= 0 and float(t) <= 100:
            return True
        else:
            return False, "Enter a percetange number between 0 to 100."
    except ValueError:
        return False, "Enter a percetange number between 0 to 100."


class TBSettings(NodeBundle):
    def __init__(self, tb_matcher, parent=None):
        name = "tabular-matcher-settings"
        self.tb_matcher = tb_matcher

        # OBJECTS
        self.__display_0 = Display(
            textformat.apply("Tabular Matcher Settings", emphases=["bold", "underline"])
        )
        self.__prompt_0 = Prompt(
            textformat.apply("Tabular Matcher Settings", emphases=["bold", "underline"])
        )
        self.__prompt_1 = Prompt(
            "Enter new threshold between 0 to 100",
            verification=_verify_threshold,
            command=Command(self._set_threshold),
        )

        # NODES
        self.__entry_node = Node(
            self.__prompt_0,
            name=f"{name}_choose",
            show_hideout=True,
            clear_screen=True,
        )
        self.__node_1 = Node(self.__prompt_1, parent=self.__entry_node, store=False)

        self.__bundle_0 = TBSetColumnsToGet(tb_matcher.config, parent=self.__entry_node)
        self.__bundle_1 = TBSetColumnsToMatch(tb_matcher.config, parent=self.__entry_node) 
        self.__bundle_2 = TBSetColumnsToGroup(tb_matcher.config, parent=self.__entry_node)
        self.__bundle_3 = TBSetColumnThreshold(tb_matcher.config, parent=self.__entry_node)
        self.__bundle_4 = TBSetColumnScorers(tb_matcher.config, parent=self.__entry_node)
        self.__bundle_5 = TBSetColumnCutoffs(tb_matcher.config, parent=self.__entry_node)
        self.__exit_node = DecoyNode(name=f"{name}_last-node")

        self.__entry_node.adopt(self.__entry_node)
        self.__entry_node.adopt(self.__bundle_0.entry_node)
        self.__entry_node.adopt(self.__bundle_1.entry_node)
        self.__entry_node.adopt(self.__bundle_2.entry_node)
        self.__entry_node.adopt(self.__bundle_3.entry_node)
        self.__entry_node.adopt(self.__bundle_4.entry_node)
        self.__entry_node.adopt(self.__bundle_5.entry_node)
        self.__node_1.adopt(self.__entry_node)

        # CONFIGURATION
        format_threshold = textformat.apply(
            str(self.tb_matcher.required_threshold), emphases=["bold", "underline"]
        )

        self.__prompt_0.options = {
            "1": Command(
                lambda: self.__entry_node.set_next(self.__bundle_0.entry_node),
                value="Set Columns To Get",
            ),
            "2": Command(
                lambda: self.__entry_node.set_next(self.__bundle_1.entry_node),
                value="Set Columns To Match",
            ),
            "3": Command(
                lambda: self.__entry_node.set_next(self.__bundle_2.entry_node),
                value="Set Columns To Group",
            ),
            "4": Command(
                lambda: self.__entry_node.set_next(self.__bundle_3.entry_node),
                value="Set Column Thresholds",
            ),
            "5": Command(
                lambda: self.__entry_node.set_next(self.__bundle_4.entry_node),
                value="Set Column Scorers",
            ),
            "6": Command(
                lambda: self.__entry_node.set_next(self.__bundle_5.entry_node),
                value="Set Column Cutoffs"
            ),
            "7": Display(
                "Required Threshold: {value}",
                format_dict={"value": format_threshold},
                command=Command(lambda: self.__entry_node.set_next(self.__node_1)),
            ),
        }

        if isinstance(parent, Node):
            self.__entry_node.adopt(parent)
            self.__prompt_0.options["R"] = Command(
                lambda: self.__entry_node.set_next(parent), value="Return"
            )
        elif isinstance(parent, NodeBundle):
            self.__entry_node.adopt(parent.entry_node)
            self.__prompt_0.options["R"] = Command(
                lambda: self.__entry_node.set_next(parent.entry_node), value="Return"
            )

        super().__init__(self.__entry_node, self.__exit_node, name=name, parent=parent)

    def _set_threshold(self):
        self.tb_matcher.required_threshold = float(self.__prompt_1.responses)
        format_threshold = textformat.apply(
            str(self.tb_matcher.required_threshold), emphases=["bold", "underline"]
        )
        self.__prompt_0.options["7"].format_dict = {"value": format_threshold}


class TBSetColumnsToGet(NodeBundle):
    def __init__(self, tb_config, parent=None):
        name = "tabular-matcher_set-columns-get"
        self.tb_config = tb_config

        # OBJECTS
        self.__table_0 = Table(
            [["Columns to Get"]], command=Command(self._populate_table)
        )
        self.__prompt_0 = Prompt("What would you like to do?")
        self.__prompt_1 = Prompt(
            "What column would you like to add?",
            multiple_selection=True,
            command=Command(self._populate_prompt_add),
        )
        self.__prompt_2 = Prompt(
            "What column would you like to remove?",
            multiple_selection=True,
            command=Command(self._populate_prompt_remove),
        )

        self.__format_yes = textformat.apply(
            "YES", emphases=["bold", "italic"], text_color="bright_red"
        )
        self.__format_no = textformat.apply(
            "NO", emphases=["bold", "italic"], text_color="bright_green"
        )

        # NODES
        self.__entry_node = Node(
            self.__table_0, name=f"{name}_columns", clear_screen=True, store=False
        )
        self.__node_0 = Node(
            self.__prompt_0, name=f"{name}_select-action", parent=self.__entry_node, store=False
        )
        self.__node_1 = Node(
            self.__prompt_1, name=f"{name}_add-column", parent=self.__node_0
        )
        self.__node_2 = Node(
            self.__prompt_2, name=f"{name}_remove-column", parent=self.__node_0
        )
        self.__exit_node = DecoyNode()

        self.__node_0.adopt(self.__entry_node)
        self.__node_1.adopt(self.__entry_node)
        self.__node_2.adopt(self.__entry_node)

        # CONFIGURATIONS
        self.__table_0.table_header = "Set Columns To Get"
        self.__table_0.description = (
            "Shows the columns that are to be obtained"
        )

        self.__prompt_1.exe_seq = "before"
        self.__prompt_2.exe_seq = "before"

        self.__prompt_0.options = {
            "1": Command(
                lambda: self.__node_0.set_next(self.__node_1), value="Add columns"
            ),
            "2": Command(
                lambda: self.__node_0.set_next(self.__node_2), value="Remove columns"
            ),
            "3": Display(
                "Allow Overwrite: {status}",
                format_dict={
                    "status": self.__format_yes
                    if tb_config.columns_to_get.allow_overwrite
                    else self.__format_no
                },
                command=Command(
                    self._toggle_overwrite,
                    command=Command(lambda: self.__node_0.set_next(self.__entry_node))
                )
            )
        }

        if isinstance(parent, Node):
            self.__node_0.adopt(parent)
            self.__prompt_0.options["R"] = Command(
                lambda: self.__node_0.set_next(parent), value="Return"
            )
        elif isinstance(parent, NodeBundle):
            self.__node_0.adopt(parent.entry_node)
            self.__prompt_0.options["R"] = Command(
                lambda: self.__node_0.set_next(parent.entry_node), value="Return"
            )

        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)

    def _populate_table(self):
        self.__table_0.clear()
        for column in self.tb_config.columns_to_get:
            self.__table_0.table.append([column])
            self.__node_0.acknowledge = False

    def _populate_prompt_add(self):
        self.__prompt_1.options.clear()
        
        if self.tb_config.columns_to_get.allow_overwrite:
            columns_not_added = [
                c for c in self.tb_config.y_columns if c not in self.tb_config.columns_to_get
            ]
        else:
            columns_not_added = [
                c for c in self.tb_config.y_columns if c not in self.tb_config.columns_to_get and \
                c not in self.tb_config.x_columns
            ]

        def _add(self, y):
            self.tb_config.columns_to_get[y] = y

        for index, y in enumerate(columns_not_added, 1):
            self.__prompt_1.options[str(index)] = Command(
                lambda column=y: _add(self, column), value=y
            )

        self.__prompt_1.options["R"] = Command(
            lambda: self.__node_1.set_next(self.__entry_node), value="Return"
        )

    def _populate_prompt_remove(self):
        self.__prompt_2.options.clear()

        for index, y in enumerate(self.tb_config.columns_to_get, 1):
            self.__prompt_2.options[str(index)] = Command(
                lambda column=y: self.tb_config.columns_to_get.pop(column), value=y
            )

        self.__prompt_2.options["R"] = Command(
            lambda: self.__node_2.set_next(self.__entry_node), value="Return"
        )

    def _toggle_overwrite(self):

        self.__prompt_0.options['3'].command.respond = False
        self.__node_0.acknowledge = False

        if self.tb_config.columns_to_get.allow_overwrite:
            intersected = set(self.tb_config.columns_to_get).intersection(set(self.tb_config.x_columns))
            if not intersected:
                self.tb_config.columns_to_get.allow_overwrite = False
            else:
                self.__prompt_0.options['3'].command.respond = True
                self.__node_0.acknowledge = True
                return textformat.apply(f"Please remove these columns before toggling: {','.join(intersected)} ", 
                                        text_color='bright_red')
        else:
            self.tb_config.columns_to_get.allow_overwrite = True

        if self.tb_config.columns_to_get.allow_overwrite :
            self.__prompt_0.options["3"].format_dict["status"] = self.__format_yes
        else:
            self.__prompt_0.options["3"].format_dict["status"] = self.__format_no


class TBSetColumnsToMatch(NodeBundle):
    def __init__(self, tb_config, parent=None):
        name = "tabular-matcher_set-column-match"
        self.tb_config = tb_config

        # OBJECTS
        self.__table_0 = Table(
            [["Columns to Match", "Match With"]], command=Command(self._populate_table)
        )
        self.__prompt_0 = Prompt("What would you like to change?")

        # NODES
        self.__entry_node = Node(
            self.__table_0, name=name, store=False
        )
        self.__node_0 = Node(
            self.__prompt_0, name=f"{name}_select-change", parent=self.__entry_node, store=False,
        )
        self.__exit_node = DecoyNode(name=f"{name}_last-node", parent=self.__node_0)

        self.__bundle_0 = _TBToMatch(
            tb_config, self.__table_0, self.__entry_node, parent=self.__node_0
        )
        self.__bundle_1 = _TBMatchWith(
            tb_config, self.__table_0, self.__entry_node, parent=self.__node_0
        )

        # CONFIGURATIONS
        self.__prompt_0.options = {
            "1": Command(
                lambda: self.__node_0.set_next(self.__bundle_0.entry_node),
                value="Columns to Match",
            ),
            "2": Command(
                lambda: self.__node_0.set_next(self.__bundle_1.entry_node),
                value="Match With",
            ),
        }

        self.__table_0.table_header = "Set Columns to Match"
        self.__table_0.description = (
            "Shows the columns to match and columns to be match with"
        )

        if isinstance(parent, Node):
            self.__node_0.adopt(parent)
            self.__prompt_0.options["R"] = Command(
                lambda: self.__node_0.set_next(parent), value="Return"
            )
        elif isinstance(parent, NodeBundle):
            self.__node_0.adopt(parent.entry_node)
            self.__prompt_0.options["R"] = Command(
                lambda: self.__node_0.set_next(parent.entry_node), value="Return"
            )

        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)

    def _populate_table(self):
        self.__table_0.clear()
        for column, match_with in self.tb_config.columns_to_match.items():
            self.__table_0.table.append([column, ", ".join(match_with)])


class _TBToMatch(NodeBundle):
    def __init__(self, tb_config, full_table, return_node, parent=None):
        name = "tabular-matcher_to-match"
        self.tb_config = tb_config

        # OBJECTS
        self.__prompt_0 = Prompt("Select the following action:")
        self.__prompt_1 = Prompt(
            "Which column would you like to add?",
            multiple_selection=True,
            command=Command(self._populate_prompt_add),
        )
        self.__prompt_2 = Prompt(
            "Which column would you like to remove?",
            multiple_selection=True,
            command=Command(self._populate_prompt_remove),
        )

        # NODES
        self.__entry_node = Node(
            full_table, name=name
        )
        self.__node_0 = Node(
            self.__prompt_0, name=f"{name}_select-action", parent=self.__entry_node, store=False
        )
        self.__node_1 = Node(
            self.__prompt_1, name=f"{name}_add-col", parent=self.__node_0, store=False
        )
        self.__node_2 = Node(
            self.__prompt_2, name=f"{name}_remove-col", parent=self.__node_0, store=False
        )
        self.__exit_node = DecoyNode(name=f"{name}_not-an-exit")

        self.__node_0.adopt(return_node)
        self.__node_1.adopt(self.__entry_node)
        self.__node_2.adopt(self.__entry_node)

        # CONFIGURATIONS
        self.__prompt_0.options = {
            "1": Command(
                lambda: self.__node_0.set_next(self.__node_1), value="Add columns"
            ),
            "2": Command(
                lambda: self.__node_0.set_next(self.__node_2), value="Remove columns"
            ),
            "R": Command(lambda: self.__node_0.set_next(return_node), value="Return"),
        }

        self.__prompt_1.exe_seq = "before"
        self.__prompt_2.exe_seq = "before"

        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)

    def _populate_prompt_add(self):
        self.__prompt_1.options.clear()

        columns_not_added = [
            c for c in self.tb_config.x_columns if c not in self.tb_config.columns_to_match
        ]

        def _add(self, x):
            self.tb_config.columns_to_match[x] = \
            (x, ) if x in self.tb_config.x_columns else (None, )

        for index, x in enumerate(columns_not_added, 1):
            self.__prompt_1.options[str(index)] = Command(
                lambda column=x: _add(self, column), value=x
            )

        self.__prompt_1.options["R"] = Command(
            lambda: self.__node_1.set_next(self.__entry_node), value="Return"
        )

    def _populate_prompt_remove(self):
        self.__prompt_2.options.clear()

        def _remove(self, x):
            del self.tb_config.columns_to_match[x]

        for index, x in enumerate(self.tb_config.columns_to_match, 1):
            self.__prompt_2.options[str(index)] = Command(
                lambda column=x: _remove(self, column), value=x
            )

        self.__prompt_2.options["R"] = Command(
            lambda: self.__node_2.set_next(self.__entry_node), value="Return"
        )


class _TBMatchWith(NodeBundle):
    def __init__(self, tb_config, full_table, return_node, parent=None):
        name = "tabular-matcher_match-with"
        self.tb_config = tb_config

        # OBJECTS
        self.__prompt_0 = Prompt(
            "Select a column in 'Columns to Match'",
            command=Command(lambda: self._populate_prompt(return_node)),
        )
        self.__table_0 = Table(
            [["Columns to Match", "Match With"]], command=Command(self._populate_table)
        )
        self.__prompt_1 = Prompt("Select the following action:")
        self.__prompt_2 = Prompt(
            "Which column would you like to add?",
            multiple_selection=True,
            command=Command(self._populate_prompt_add),
        )
        self.__prompt_3 = Prompt(
            "Which column would you like to remove?",
            multiple_selection=True,
            command=Command(self._populate_prompt_remove),
        )

        # NODES
        self.__entry_node = Node(
            full_table
        )
        self.__node_0 = Node(
            self.__prompt_0, name=f"{name}_select-column", parent=self.__entry_node, store=False
        )
        self.__node_1 = Node(
            self.__table_0, name=f"{name}_match-with", parent=self.__node_0,
        )
        self.__node_2 = Node(
            self.__prompt_1, name=f"{name}_select-action", parent=self.__node_1, store=False
        )
        self.__node_3 = Node(
            self.__prompt_2, name=f"{name}_add-col", parent=self.__node_2, store=False
        )
        self.__node_4 = Node(
            self.__prompt_3, name=f"{name}_remove-col", parent=self.__node_2, store=False
        )
        self.__exit_node = DecoyNode()

        self.__node_0.adopt(return_node)
        self.__node_2.adopt(self.__entry_node)
        self.__node_3.adopt(self.__node_1)
        self.__node_4.adopt(self.__node_1)

        # CONFIGURATIONS
        self.__prompt_0.exe_seq = "before"

        self.__prompt_1.options = {
            "1": Command(
                lambda: self.__node_2.set_next(self.__node_3), value="Add columns"
            ),
            "2": Command(
                lambda: self.__node_2.set_next(self.__node_4), value="Remove columns"
            ),
            "R": Command(
                lambda: self.__node_2.set_next(self.__entry_node), value="Return"
            ),
        }

        self.__prompt_2.exe_seq = "before"
        self.__prompt_3.exe_seq = "before"

        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)

    def _populate_table(self):
        self.__table_0.clear()
        chosen_column = self.__prompt_0.option_responses()

        self.__table_0.table += [
            [
                chosen_column,
                ", ".join(self.tb_config.columns_to_match[chosen_column]),
            ]
        ]

    def _populate_prompt(self, return_node):
        self.__prompt_0.options.clear()

        for index, x in enumerate(self.tb_config.columns_to_match, 1):
            self.__prompt_0.options[str(index)] = Command(
                lambda: self.__node_0.set_next(self.__node_1), value=x
            )

        self.__prompt_0.options["R"] = Command(
            lambda: self.__node_0.set_next(return_node), value="Return"
        )

    def _populate_prompt_add(self):
        self.__prompt_2.options.clear()

        chosen_column = self.__prompt_0.option_responses()
        columns = self.tb_config.columns_to_match[chosen_column]

        columns_not_added = [
            c for c in self.tb_config.y_columns if c not in columns
        ]

        def _add(self, y):
            chosen_column = self.__prompt_0.option_responses()
            self.tb_config.columns_to_match[chosen_column] = (y,)

        for index, y in enumerate(columns_not_added, 1):
            self.__prompt_2.options[str(index)] = Command(
                lambda column=y: _add(self, column), value=y
            )

        self.__prompt_2.options["R"] = Command(
            lambda: self.__node_3.set_next(self.__node_1), value="Return"
        )

    def _populate_prompt_remove(self):
        self.__prompt_3.options.clear()

        chosen_column = self.__prompt_0.option_responses()
        columns = self.tb_config.columns_to_match[chosen_column]

        def _remove(self, y):
            chosen_column = self.__prompt_0.option_responses()
            self.tb_config.columns_to_match[chosen_column].remove(y)

        for index, y in enumerate(columns, 1):
            self.__prompt_3.options[str(index)] = Command(
                lambda column=y: _remove(self, column), value=y
            )

        self.__prompt_3.options["R"] = Command(
            lambda: self.__node_4.set_next(self.__node_1), value="Return"
        )


class TBSetColumnsToGroup(NodeBundle):

    def __init__(self, tb_config, parent=None):
        name = "tabular-matcher_set-column-groups"
        self.tb_config = tb_config

        # OBJECTS
        self.__table_0 = Table(
            [["Columns to Group", "Group With"]], command=Command(self._populate_table)
        )
        self.__prompt_0 = Prompt("What would you like to do?")
        self.__prompt_1 = Prompt(
            "Select a Y column to group:",
            multiple_selection=True,
            command=Command(self._populate_prompt_add_y),
        )
        self.__prompt_2 = Prompt(
            "Select a Y column to remove from groups:",
            multiple_selection=True,
            command=Command(self._populate_prompt_remove_y),
        )
        self.__prompt_3 = Prompt(
            "Select a X column to group with:",
            command=Command(self._populate_prompt_add_x),
        )

        # NODES
        self.__entry_node = Node(
            self.__table_0, name=f"{name}_columns", clear_screen=True, store=False
        )
        self.__node_0 = Node(
            self.__prompt_0, name=f"{name}_select-action", parent=self.__entry_node, store=False
        )
        self.__node_1 = Node(
            self.__prompt_1, name=f"{name}_add-column-y", parent=self.__node_0, store=False
        )
        self.__node_2 = Node(
            self.__prompt_2, name=f"{name}_remove-column-y", parent=self.__node_0, store=False
        )
        self.__node_3 = Node(
            self.__prompt_3, name=f"{name}_add-column-x", parent=self.__node_1, store=False
        )
        self.__exit_node = DecoyNode()

        self.__node_1.adopt(self.__entry_node)
        self.__node_2.adopt(self.__entry_node)
        self.__node_3.adopt(self.__entry_node)
        self.__node_3.adopt(self.__node_1)

        # CONFIGURATIONS
        self.__table_0.table_header = "Set Columns To Group"
        self.__table_0.description = (
            "Shows the columns and the columns to group with"
        )
        self.__prompt_1.exe_seq = "before"
        self.__prompt_2.exe_seq = "before"
        self.__prompt_3.exe_seq = "before"
        
        self.__prompt_0.options = {
            "1": Command(
                lambda: self.__node_0.set_next(self.__node_1), value="Add columns"
            ),
            "2": Command(
                lambda: self.__node_0.set_next(self.__node_2), value="Remove columns"
            ),
        }

        if isinstance(parent, Node):
            self.__node_0.adopt(parent)
            self.__prompt_0.options["R"] = Command(
                lambda: self.__node_0.set_next(parent), value="Return"
            )
        elif isinstance(parent, NodeBundle):
            self.__node_0.adopt(parent.entry_node)
            self.__prompt_0.options["R"] = Command(
                lambda: self.__node_0.set_next(parent.entry_node), value="Return"
            )

        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)

    def _populate_table(self):
        self.__table_0.clear()
        for column, group_with in self.tb_config.columns_to_group.items():
            self.__table_0.table.append([column, group_with])

    def _populate_prompt_add_y(self):
        self.__prompt_1.options.clear()

        columns_not_added = [
            c for c in self.tb_config.y_columns if c not in self.tb_config.columns_to_group
        ]

        for index, y in enumerate(columns_not_added, 1):
            self.__prompt_1.options[str(index)] = Command(
                lambda: self.__node_1.set_next(self.__node_3), value=y
            )

        self.__prompt_1.options["R"] = Command(
            lambda: self.__node_1.set_next(self.__entry_node), value="Return"
        )

    def _populate_prompt_remove_y(self):
        self.__prompt_2.options.clear()

        for index, y in enumerate(self.tb_config.columns_to_group, 1):
            self.__prompt_2.options[str(index)] = Command(
                lambda column=y: self.tb_config.columns_to_group.pop(column), value=y
            )

        self.__prompt_2.options["R"] = Command(
            lambda: self.__node_2.set_next(self.__entry_node), value="Return"
        )

    def _populate_prompt_add_x(self):
        self.__prompt_3.options.clear()

        def _add(self, x):
            chosen_column = self.__prompt_1.option_responses()
            self.tb_config.columns_to_group[chosen_column] = x

        for index, x in enumerate(self.tb_config.x_columns, 1):
            self.__prompt_3.options[str(index)] = Command(
                lambda column=x: _add(self, column), value=x,
                command=Command(lambda: self.__node_3.set_next(self.__entry_node))
            )

        self.__prompt_3.options["R"] = Command(
            lambda: self.__node_3.set_next(self.__node_1), value="Return"
        )


class TBSetColumnThreshold(NodeBundle):
    def __init__(self, tb_config, parent=None):
        name = "tabular-matcher_set-column-threshold"
        self.tb_config = tb_config

        # OBJECTS
        self.__table_0 = Table(
            [["Option", "Column", "Threshold"]], command=Command(self._populate_table)
        )
        self.__prompt_0 = Prompt(
            "Choose an option from the table above", 
            verification=self._verify_selection,
            command=Command(lambda: self.__node_0.set_next(self.__node_1)),
            show_opt_msg=False
        )
        self.__prompt_1 = Prompt(
            "What is the threshold you would like to change to?",
            verification=_verify_threshold,
            command=Command(self._execute),
        )

        # NODES
        self.__entry_node = Node(
            self.__table_0, name=name, clear_screen=True,store=False,
        )
        self.__node_0 = Node(
            self.__prompt_0, name=f"{name}_select", parent=self.__entry_node, store=False,
        )
        self.__node_1 = Node(
            self.__prompt_1, name=f"{name}_change", parent=self.__node_0, store=False
        )

        self.__exit_node = DecoyNode()

        self.__node_1.adopt(self.__entry_node)

        # CONFIGURATIONS
        self.__prompt_0.exe_seq = 'before'

        self.__table_0.table_header = "Set Threshold By Columns"
        self.__table_0.description = (
            "Shows the columns and the threshold associated with it"
        )

        if isinstance(parent, Node):
            self.__node_0.adopt(parent)
            self.__node_1.adopt(parent)
            self.__prompt_0.options["R"] = Command(
                lambda: self.__node_0.set_next(parent), value="Return"
            )
        elif isinstance(parent, NodeBundle):
            self.__node_0.adopt(parent.entry_node)
            self.__node_1.adopt(parent.entry_node)
            self.__prompt_0.options["R"] = Command(
                lambda: self.__node_0.set_next(parent.entry_node), value="Return"
            )

        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)

    def _execute(self):
        r = self.__prompt_0.responses
        if r not in self.__prompt_0.options:
            new_threshold = float(self.__prompt_1.responses)
            column = dict(enumerate(self.tb_config.thresholds_by_column, 1))[int(r)]
            self.tb_config.thresholds_by_column[column] = new_threshold
            self.__node_1.set_next(self.__entry_node)

    def _verify_selection(self, s):
        try:
            if (s in self.__prompt_0.options or 
                int(s) in dict(enumerate(self.tb_config.thresholds_by_column, 1))):
                return True
            else:
                return False, "Selection is not available."
            
        except ValueError:
            return False, "Selection should be one of the options or 'R'."

    def _populate_table(self):
        self.__table_0.clear()
        for option, (column, threshold) in list(enumerate(self.tb_config.thresholds_by_column.items(), 1)):
            self.__table_0.table.append([option, column, threshold])


class TBSetColumnScorers(NodeBundle):
    def __init__(self, tb_config, parent=None):
        name = "tabular-matcher_set-column-scorers"
        self.tb_config = tb_config

        # OBJECTS
        self.__table_0 = Table(
            [["Option", "Column", "Scorer"]], command=Command(self._populate_table)
        )
        self.__prompt_0 = Prompt(
            "Select a column by the options in the table", 
            verification=self._verify_selection,
            command=Command(self._populate_next_prompt),
            show_opt_msg=False
        )
        self.__prompt_1 = Prompt(
            "What is the scorer you would like to change to?",
        )

        # NODES
        self.__entry_node = Node(
            self.__table_0, name=name, clear_screen=True, store=False, 
        )
        self.__node_0 = Node(
            self.__prompt_0, name=f"{name}_select", parent=self.__entry_node, store=False,
        )
        self.__node_1 = Node(
            self.__prompt_1, name=f"{name}_change", parent=self.__node_0, store=False
        )

        self.__exit_node = DecoyNode()

        self.__node_1.adopt(self.__entry_node)

        # CONFIGURATIONS
        self.__prompt_0.exe_seq = 'before'

        self.__table_0.table_header = "Set Scorer By Columns"
        self.__table_0.description = (
            "Shows the columns and the scorer associated with it"
        )

        if isinstance(parent, Node):
            self.__node_0.adopt(parent)
            self.__node_1.adopt(parent)
            self.__prompt_0.options["R"] = Command(
                lambda: self.__node_0.set_next(parent), value="Return"
            )
        elif isinstance(parent, NodeBundle):
            self.__node_0.adopt(parent.entry_node)
            self.__node_1.adopt(parent.entry_node)
            self.__prompt_0.options["R"] = Command(
                lambda: self.__node_0.set_next(parent.entry_node), value="Return"
            )

        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)

    def _execute(self):
        r = self.__prompt_0.responses
        if r not in self.__prompt_0.options:
            column = dict(enumerate(self.tb_config.scorers_by_column, 1))[int(r)]
            self.tb_config.scorers_by_column[column] = self.__prompt_1.option_responses()
            self.__node_1.set_next(self.__entry_node)

    def _verify_selection(self, s):
        try:
            if (s in self.__prompt_0.options or 
                int(s) in dict(enumerate(self.tb_config.scorers_by_column, 1))):
                return True
            else:
                return False, "Selection is not available."
            
        except ValueError:
            return False, "Selection should be one of the options or 'R'."

    def _populate_table(self):
        self.__table_0.clear()
        for option, (column, scorer) in list(enumerate(self.tb_config.scorers_by_column.items(), 1)):
            self.__table_0.table.append([option, column, scorer])

    def _populate_next_prompt(self):
        self.__prompt_1.options.clear()

        for index, scorer in enumerate(self.tb_config.scorers_by_column.SCORERS, 1):
            self.__prompt_1.options[str(index)] = Command(self._execute, value=scorer)

        self.__prompt_1.options['R'] = Command(
            lambda: self.__node_1.set_next(self.__entry_node), value='Return'
        )
        self.__node_0.set_next(self.__node_1)


class TBSetColumnCutoffs(NodeBundle):
    def __init__(self, tb_config, parent=None):
        name = "tabular-matcher_set-cutoffs-by-column"
        self.tb_config = tb_config

        # OBJECTS
        self.__table_0 = Table(
            [["Option", "Column", "Cutoffs"]], command=Command(self._populate_table)
        )
        self.__prompt_0 = Prompt(
            "Select a column you would like to toggle", 
            verification=self._verify_selection,
            command=Command(self._toggle_cutoff),
            show_opt_msg=False,
        )

        # NODES
        self.__entry_node = Node(
            self.__table_0, name=name, clear_screen=True, store=False, 
        )
        self.__node_0 = Node(
            self.__prompt_0, name=f"{name}_toggle", parent=self.__entry_node, store=False,
        )
        self.__exit_node = DecoyNode()

        self.__node_0.adopt(self.__entry_node)

        # CONFIGURATIONS
        self.__table_0.table_header = "Set Cutoffs By Column"
        self.__table_0.description = (
            "Shows the columns where cutoff is applied"
        )

        self.__prompt_0.options = {
            "R": Command(lambda: self.__node_0.set_next(self.__exit_node), value="Return"),
        }

        if isinstance(parent, Node):
            self.__node_0.adopt(parent)
            self.__prompt_0.options['R'] = Command(
                lambda: self.__node_0.set_next(parent), value="Return",
            )
        elif isinstance(parent, NodeBundle):
            self.__node_0.adopt(parent.entry_node)
            self.__prompt_0.options['R'] = Command(
                lambda: self.__node_0.set_next(parent.entry_node), value="Return",
            )

        super().__init__(self.__entry_node, self.__exit_node, parent=parent, name=name)

    def _toggle_cutoff(self):
        r = self.__prompt_0.responses
        if r not in self.__prompt_0.options:
            c = dict(enumerate(self.tb_config.cutoffs_by_column, 1))[int(r)]
            self.tb_config.cutoffs_by_column[c] = not self.tb_config.cutoffs_by_column[c]
            self.__node_0.set_next(self.__entry_node)

    def _verify_selection(self, s):
        try:
            if (s in self.__prompt_0.options or 
                int(s) in dict(enumerate(self.tb_config.cutoffs_by_column, 1))):
                return True
            else:
                return False, "Selection is not available."
            
        except ValueError:
            return False, "Selection should be one of the options or 'R'."

    def _populate_table(self):
        self.__table_0.clear()
        for option, (column, cutoff) in list(enumerate(self.tb_config.cutoffs_by_column.items(), 1)):
            self.__table_0.table.append([option, column, "Yes" if cutoff else "No"])
