
# built-ins
import sys
import os
import time

# internal packages
from . import textformat
from .objects import Prompt, Command


class Engine:

    """
    Runs, stores and remember nodes of CliObjects
    
    Attributes
    ----------
    current_node : cli.Node
        The current selection of a node by the user

    node_selection : list    
        Stores node selection and remembers the node selected
    
    hideout_menu : cli.objects.Prompt
        A menu that presents the options for the user to traverse back to a node, 
        restart the application or quit the application
    
    restart_menu : cli.objects.Prompt
        A menu that presents the options for the user to restart or quit the application
    """

    def __init__(self, start_node, loop=False):

        """
        Parameters
        ----------
        start_node : cli.Node
            Starting node of the engine that contains other child nodes

        loop : bool
            If True, the engine will restart to the first node clearing all selected nodes 
            else the while loop breaks and exits the applciation
        """

        self.__current_node = start_node
        self.__node_selection = [start_node]

        # will trigger restart menu if set to True
        self.loop = loop

        self.hideout_menu = Prompt(textformat.apply("Hideout Menu", emphases=['bold'], text_color='cyan'))
        self.hideout_menu.options = {
            '1': "Return",
            '2': Command(self.go_back, value="Go back", respond=True,
                                 command=Command(lambda: time.sleep(0.3))),
            'R': Command(self.restart, value="Restart", respond=True,
                                 command=Command(lambda: time.sleep(0.3))),
            'Q': Command(self.quit, value="Quit")
            }

        self.restart_menu = Prompt("You have reached the end, what would you like to do?")
        self.restart_menu.options = {
            '1': Command(self.restart, value="Restart", respond=True,
                                 command=Command(lambda: time.sleep(0.3))),
            '2': Command(self.quit, value="Quit")}

    def clear_terminal(self):

        """Clears any existing output on the terminal"""

        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def go_back(self):

        """Set the current node to the previous node"""

        self.__current_node = self.__node_selection[-1]
        if len(self.__node_selection) > 1: 
            self.__node_selection.pop()

        return textformat.apply("Going Back...", emphases=['italic'], text_color='magenta')

    def restart(self):

        """Set the current node to the first node and clears all selection"""

        self.__current_node = self.__node_selection[0]
        self.__node_selection.clear()
        self.__node_selection.append(self.__current_node)

        return textformat.apply("Restarting...", emphases=['italic'], text_color='magenta')

    def quit(self):

        """Quits the application"""

        print(textformat.apply("\nQuitting...", emphases=['italic'], text_color='magenta'))
        time.sleep(0.5)
        self.clear_terminal()
        sys.exit()

    def run(self):
        
        """Traverses and executes nodes while triggering events pertaining to each node attributes"""

        while True:

            if self.__current_node:
                self.__current_node.engine = self
                print()

                if self.__current_node.clear_screen:
                    self.clear_terminal()

                if self.__current_node.show_hideout:
                    print(textformat.apply("To open hideout menu, press Ctrl + C\n", emphases=['italic'], text_color='cyan'))

                # CTRL + C will trigger the hideout menu
                try:
                    self.__current_node.execute()

                    if self.__current_node.acknowledge:
                        _ = input(textformat.apply("\nPress ENTER to continue.", emphases=['blink'], text_color='magenta'))

                    # automatically set next node to the only child
                    if len(self.__current_node.children) == 1:
                        self.__current_node.set_next(next(iter(self.__current_node.children.values())))
                    
                    if self.__current_node.store and self.__current_node.id != self.__node_selection[-1].id:
                            self.__node_selection.append(self.__current_node)

                    self.__current_node = self.__current_node.next

                except KeyboardInterrupt:
                    # Loop to prevent user from further triggering another KeyboardInterrupt
                    while True:
                        try:
                            self.clear_terminal()
                            self.hideout_menu.draw()
                            break
                        except KeyboardInterrupt:
                            pass
            else:
                if self.loop:
                    self.clear_terminal()
                    self.restart_menu.draw()
                else:
                    break

        self.quit()


class Node:

    """
    To encapsulate and traverse CliObjects via Engine
    
    Attributes
    ----------
    id : int
        Unique id is given to each node during runtime

    next : cli.Node
        Child node that is set to be traverse next
    
    children : dict
        Contains child nodes where each child node is identified with their id
    
    engine : cli.Engine
        A 'backdoor' for node-to-engine interaction
    """

    def __init__(self, cliobject, parent=None, name='node', 
                 show_hideout=False, clear_screen=False, acknowledge=False, store=True):
        """
        Parameters
        ----------
        cliobject : CliObject
            Can hold a cliobject

        parent : cli.Node
            Parent node that adopts this instance

        name : str
            Name for human-readable identification
        
        show_hideout : bool
            If True, will inform/remind user of using hideout menu feature
    
        clear_screen : bool
            If True, terminal will be cleared before drawing or executing the object
    
        acknowledge : bool
            If True, engine will prompt user to acknowledge a node with an input

        store : bool
            If True, engine will store it in node selections otherwise disregarded
        """

        self.cliobject = cliobject
        self.__name = name

        self.__next = None
        self.__children = {}
        self.__engine = None

        self.show_hideout = show_hideout
        self.clear_screen = clear_screen
        self.acknowledge = acknowledge
        self.store = store

        self.__id = id(self)

        if parent:
            parent.adopt(self)

    def adopt(self, node):
        
        """Store and reference the potential next node"""

        assert isinstance(node, Node)
        self.__children[node.id] = node

    def set_next(self, node):

        """Selects the next node from existing node children"""

        try:
            self.__next = self.__children[node.id] if node else None

        except KeyError:
            raise Exception(f"NODE={node.name} is not adopted by NODE={self.name}")

    def execute(self):
        
        """Draw and/or executes the CliObject that the node holds"""

        if self.cliobject.exe_seq == 'before':
            self.cliobject.execute()
            self.cliobject.draw()
        elif self.cliobject.exe_seq == 'after':
            self.cliobject.draw()
            self.cliobject.execute()
        else:
            self.cliobject.draw()

    @property
    def id(self):
        return self.__id
    
    @property
    def name(self):
        # returns the cliobject name for better identificaiton
        return self.cliobject.name + self.__name
    
    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def children(self):
        return self.__children

    @property
    def next(self):
        return self.__next

    @property
    def engine(self):
        return

    @engine.setter
    def engine(self, e):
        assert isinstance(e, Engine)
        self.__engine = e

    def engine_call(self, method):

        """Allow nodes to call the methods of an engine's instance"""

        if method == 'quit':
            self.__engine.quit()
        elif method == 'go_back':
            self.__engine.go_back()
        elif method == 'restart':
            self.__engine.restart()
        elif method == 'clear_terminal':
            self.__engine.clear_terminal()
        else:
            return


class NodeBundle:

    """To contain a group of Nodes such that each bundle can perform a specific task"""

    def __init__(self, entry_node, exit_node, parent=None, name='bundle'):

        """
        Parameters
        ----------    
        entry_node : cli.Node
            Node of a bundle where other nodes or bundle can gain access to

        exit_node : cli.Node
            Node of a bundle where it adopts other nodes or bundle

        parent : cli.Node or cli.NodeBundle
            Node as parent will adopt the entry_node. NodeBundle as parent will have 
            exit_node of the parent to adopt entry_node

        name : str
            Name for human-readable identification
        """

        self.__name = name
        self.__entry_node = entry_node
        self.__exit_node = exit_node

        if isinstance(parent, Node):
            parent.adopt(self.__entry_node)
            
        elif isinstance(parent, NodeBundle):
            parent.adopt(self)

    def adopt(self, bundle):
        self.adopt_node(bundle.entry_node)

    def adopt_node(self, node):
        self.__exit_node.adopt(node)
    
    def set_next(self, bundle):
        self.set_next_node(bundle.entry_node)
    
    def set_next_node(self, node):
        self.__exit_node.set_next(node)
    
    @property
    def name(self):
        return self.__name + '_node-bundle'

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def entry_node(self):
        return self.__entry_node

    @property
    def exit_node(self):
        return self.__exit_node


class DecoyNode(Node):

    """The DecoyNode is an extension of Node that acts as a placeholder"""

    def __init__(self, name='decoy-node', parent=None):
        # CliObject Command is used to replace the need of declaring another object
        _object = Command(lambda: None)
        _object.name = 'decoy'
        super().__init__(_object, parent=parent, name=name, show_hideout=False, store=False)
