# built-ins
import re

# internal packages
from . import references, queries
from vs_library.cli import Node, NodeBundle, DecoyNode, textformat
from vs_library.cli.objects import Command, Display, Prompt, Table


def is_validyear(x):
    try:
        regex = r'(19[8-9][9]|2[0-9][0-9][0-9]|3000)'

        return re.fullmatch(regex, x), "Year must be between 1989 to 3000."

    except ValueError:
        return False, "Input must be an integer"


class IncumbentQueryForm(NodeBundle):

    def __init__(self, query_tool, parent=None):

        name = 'incumbent-query-form'
        self.query_tool = query_tool

        # OBJECTS
        self.__display_0 = Display(textformat.apply("Incumbent Query Form", 
                                                    emphases=['bold', 'underline']))
        self.__prompt_0 = Prompt("Which of the following information do you have?")
        self.__prompt_1 = Prompt("Which of the following office(s) are of these incumbents?", 
                                 multiple_selection=True)
        self.__prompt_2 = Prompt("Which of the following office type(s) are of these incumbents?", 
                                 multiple_selection=True)
        self.__prompt_3 = Prompt("Active year(s) of incumbents", 
                                 multiple_selection=True, verification=is_validyear)
        self.__prompt_4 = Prompt("Which of the following state(s) are of these incumbents", 
                                 multiple_selection=True)
        self.__prompt_5 = Prompt("Proceed with the above response?")

        self.__table_0 = Table([], header=False, command=Command(self._populate_table))


        # NODES
        self.__entry_node = Node(self.__display_0, name=f'{name}_section-header',
                             store=False, clear_screen=True)
        self.__node_0 = Node(self.__prompt_0, name=f'{name}_office-choice', parent=self.__entry_node,
                             show_instructions=True)
        self.__node_1 = Node(self.__prompt_1, name=f'{name}_office-id', parent=self.__node_0, 
                             show_instructions=True)
        self.__node_2 = Node(self.__prompt_2, name=f'{name}_office-types', parent=self.__node_0, 
                             show_instructions=True)
        self.__node_3 = Node(self.__prompt_3, name=f'{name}_year', parent=self.__node_1, 
                             show_instructions=True)
        self.__node_4 = Node(self.__prompt_4, name=f'{name}_states', parent=self.__node_3, 
                             show_instructions=True)
        self.__node_5 = Node(self.__table_0, name=f'{name}_responses', parent=self.__node_4,
                             store=False)
        self.__node_6 = Node(self.__prompt_5, name=f'{name}_confirm', parent=self.__node_5, 
                             show_instructions=True, store=False)
        self.__exit_node = DecoyNode(name=f'{name}_last-node', parent=self.__node_6)

        self.__node_2.adopt(self.__node_3)
        self.__node_6.adopt(self.__node_0)

        # CONFIGURATIONS
        self.__table_0.table_header = "Response"
        self.__table_0.description = "Shows the filled incumbent query form"

        self.__prompt_0.options = {
            '1': Command(lambda: self.__node_0.set_next(self.__node_1), value="Office ID",
                         command=Command(self.__prompt_2.clear)),
            '2': Command(lambda: self.__node_0.set_next(self.__node_2), value="Office Types",
                         command=Command(self.__prompt_1.clear))
            }

        self.__prompt_1.options = references.OFFICE
        self.__prompt_2.options = references.OFFICE_TYPE
        self.__prompt_4.options = references.STATE| {'**': 'ALL'}

        self.__prompt_5.options = {
            '1': Command(self._execute, value="Yes", 
                         command=Command(lambda: self.__node_6.set_next(self.__exit_node))),
            '2': Command(lambda: self.__node_6.set_next(self.__node_0), value="No, re-enter responses")
            }

        super().__init__(self.__entry_node, self.__exit_node, name=name, parent=parent)

    def _execute(self):
        office_ids = self.__prompt_1.responses
        office_types = self.__prompt_2.responses
        years = self.__prompt_3.responses
        states = self.__prompt_4.responses

        if int(min(years)) >= 2005:
            self.query_tool.query  = queries.Incumbents(years, office_ids, office_types, states).by_congstatus()
        else:
            self.query_tool.query  = queries.Incumbents(years, office_ids, office_types, states).by_electdates()

    def _populate_table(self):
        self.__table_0.table = [["Office(s)", self.__prompt_1.option_responses(string=True)],
                                ["Office Type(s)", self.__prompt_2.option_responses(string=True)],
                                ["Year(s)", ", ".join(self.__prompt_3.responses)],
                                ["State(s)", self.__prompt_4.option_responses(string=True)]]


class CandidateQueryForm(NodeBundle):

    def __init__(self, query_tool, parent=None):

        name = 'candidates-query-form'
        self.query_tool = query_tool

        # OBJECTS
        self.__display_0 = Display(textformat.apply("Candidate Query Form", 
                                                    emphases=['bold', 'underline']))
        self.__prompt_0 = Prompt("What are the election stage(s) of these candidates?",  
                                 multiple_selection=True)
        self.__prompt_1 = Prompt("Which of the following information do you have?")
        self.__prompt_2 = Prompt("Which of the following office(s) are of these candidates?", 
                                 multiple_selection=True)
        self.__prompt_3 = Prompt("Which of the following office types are of these candidates?", 
                                 multiple_selection=True)
        self.__prompt_4 = Prompt("What are the years of election these candidates are in?", 
                                 multiple_selection=True, verification=is_validyear)
        self.__prompt_5 = Prompt("Which of the following state(s) are these elections held?", 
                                 multiple_selection=True)
        self.__prompt_6 = Prompt("Proceed with the above response?")

        self.__table_0 = Table([], header=False, command=Command(self._populate_table))

        # NODES
        self.__entry_node = Node(self.__display_0, name=f'{name}_section-header',
                             store=False, clear_screen=True)
        self.__node_0 = Node(self.__prompt_0, name=f'{name}_election-stage', parent=self.__entry_node,
                             show_instructions=True)
        self.__node_1 = Node(self.__prompt_1, name=f'{name}_office-choice', parent=self.__node_0, 
                             show_instructions=True)
        self.__node_2 = Node(self.__prompt_2, name=f'{name}_office-id', parent=self.__node_1, 
                             show_instructions=True)
        self.__node_3 = Node(self.__prompt_3, name=f'{name}_office-types', parent=self.__node_1, 
                             show_instructions=True)
        self.__node_4 = Node(self.__prompt_4, name=f'{name}_year', parent=self.__node_2, 
                             show_instructions=True)
        self.__node_5 = Node(self.__prompt_5, name=f'{name}_state', parent=self.__node_4, 
                             show_instructions=True)
        self.__node_6 = Node(self.__table_0, name=f'{name}_response', parent=self.__node_5,
                             show_instructions=True, store=False)
        self.__node_7 = Node(self.__prompt_6, name=f'{name}_confirm', parent=self.__node_6, 
                             store=False)
        self.__exit_node = DecoyNode(name=f'{name}_last-node', parent=self.__node_7)

        self.__node_3.adopt(self.__node_4)
        self.__node_7.adopt(self.__node_0)

        # CONFIGURATIONS
        self.__table_0.table_header = "Response"
        self.__table_0.description = "Shows the filled candidate query form"

        self.__prompt_0.options = references.ELECTION_STAGE

        self.__prompt_1.options = {
            '1': Command(lambda: self.__node_1.set_next(self.__node_2), value='Office ID',
                         command=Command(self.__prompt_3.clear)),
            '2': Command(lambda: self.__node_1.set_next(self.__node_3), value='Office Types',
                         command=Command(self.__prompt_2.clear))
            }

        self.__prompt_2.options = references.OFFICE
        self.__prompt_3.options = references.OFFICE_TYPE
        self.__prompt_5.options = references.STATE | {'**': "ALL"}

        self.__prompt_6.options = {
            '1': Command(self._execute, value="Yes",
                         command=Command(self.__node_7.set_next(self.__exit_node))),
            '2': Command(lambda: self.__node_7.set_next(self.__node_0), value="No, re-enter responses")
            }

        super().__init__(self.__entry_node, self.__exit_node, name=name, parent=parent)

    def _execute(self):
        election_stages = self.__prompt_0.responses
        office_ids = self.__prompt_2.responses
        office_types = self.__prompt_3.responses
        election_years = self.__prompt_4.responses
        states = self.__prompt_5.responses

        self.query_tool.query = queries.ElectionCandidates(election_years, election_stages, office_ids,
                                                                    office_types, states).by_yoss()

    def _populate_table(self):
        self.__table_0.table = [["Election Stage(s)", self.__prompt_0.option_responses(string=True)],
                                ["Office(s)", self.__prompt_2.option_responses(string=True)],
                                ["Office Type(s)", self.__prompt_3.option_responses(string=True)],
                                ["Year(s)", ", ".join(self.__prompt_4.responses)],
                                ["State(s)", self.__prompt_5.option_responses(string=True)]]