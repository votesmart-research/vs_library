
# built-ins
import sys
import os
import time

# internal packages
from . import objects, textformat


class Engine:

    """Runs, stores and remember nodes of CliObjects.
    
    Attributes
    ----------
    current_node: Node
        The current selection of a node by user selection

    node_selection: array    
        Stores node selection and remembers the node selected
    
    hideout_menu: Prompt CliObject
        A menu that presents the options for the user to traverse back to a node, 
        restart the application or quit the application
    
    restart_menu: Prompt CliObject
        A menu that presents the options for the user to restart or quit the application

    """

    def __init__(self, start_node, loop=False):

        """
        Parameters
        ----------
        start_node: Node
        
        """

        self.__current_node = start_node
        self.__node_selection = [start_node]

        # will trigger restart menu if set to True
        self.loop = loop

        self.hideout_menu = objects.Prompt(textformat.apply("Hideout Menu", emphases=['bold'], text_color='cyan'))
        self.hideout_menu.options = {
            '1': "Return",
            '2': objects.Command(self.go_back, value="Go back", respond=True,
                                 command=objects.Command(lambda: time.sleep(0.3))),
            'R': objects.Command(self.restart, value="Restart", respond=True,
                                 command=objects.Command(lambda: time.sleep(0.3))),
            'Q': objects.Command(self.quit, value="Quit")
            }

        self.restart_menu = objects.Prompt("You have reached the end, what would you like to do?")
        self.restart_menu.options = {
            '1': objects.Command(self.restart, value="Restart", respond=True,
                                 command=objects.Command(lambda: time.sleep(0.3))),
            '2': objects.Command(self.quit, value="Quit")}


    def clear_terminal(self):

        """Clears any existing output on the terminal"""

        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')


    def go_back(self):

        """Returns to the previous node."""

        self.__current_node = self.__node_selection[-1]
        if len(self.__node_selection) > 1: 
            self.__node_selection.pop()

        return textformat.apply("Going Back...", emphases=['italic'], text_color='magenta')


    def restart(self):

        """Returns to the first node and clears all node selection."""

        self.__current_node = self.__node_selection[0]
        self.__node_selection.clear()
        self.__node_selection.append(self.__current_node)

        return textformat.apply("Restarting...", emphases=['italic'], text_color='magenta')

    def quit(self):

        """Quits the application."""

        print(textformat.apply("\nQuitting...", emphases=['italic'], text_color='magenta'))
        time.sleep(0.5)
        self.clear_terminal()
        sys.exit()


    def run(self):
        
        """Traversed through all the nodes by setting to their next intended child while also executing each individual 
        nodes themselves"""

        while True:

            if self.__current_node:
                self.__current_node.engine = self
                print()

                if self.__current_node.clear_screen:
                    self.clear_terminal()

                if self.__current_node.show_instructions:
                    print(textformat.apply("To open hideout menu, press Ctrl + C\n", emphases=['italic'], text_color='cyan'))

                # CTRL + C will trigger the hideout menu
                try:
                    if self.__current_node.object.exe_seq == 'before':
                        self.__current_node.object.execute()
                        self.__current_node.object.draw()
                    elif self.__current_node.object.exe_seq == 'after':
                        self.__current_node.object.draw()
                        self.__current_node.object.execute()
                    # since not all current node has a command to execute, it will default to draw only
                    else:
                        self.__current_node.object.draw()

                    if self.__current_node.acknowledge:
                        _ = input(textformat.apply("\nPress ENTER to continue.", emphases=['blink'], text_color='magenta'))

                    # automatically set next of  to the only child
                    if len(self.__current_node.children) == 1:
                        self.__current_node.set_next(next(iter(self.__current_node.children.values())))
                    
                    if self.__current_node.store and self.__current_node.id != self.__node_selection[-1].id:
                            self.__node_selection.append(self.__current_node)

                    self.__current_node = self.__current_node.next

                except KeyboardInterrupt:
                    print()
                    # Loop to prevent user from further triggering another KeyboardInterrupt
                    while True:
                        try:
                            print()
                            self.clear_terminal()
                            self.hideout_menu.draw()
                            break
                        except KeyboardInterrupt:
                            pass
            else:
                if self.loop:
                    print()
                    self.restart_menu.draw()
                else:
                    break

        self.quit()


class Node:

    """An encapsulation of CliObjects, to allow for traversing between objects."""

    def __init__(self, object, parent=None, name='node', show_instructions=False, clear_screen=False, 
                 acknowledge=False, store=True):

        self.object = object
        self.__id = id(self)
        self.__name = object.name + '_' + name

        self.__next = None
        self.__children = {}
        self.__engine = None

        self.show_instructions = show_instructions
        self.clear_screen = clear_screen
        self.acknowledge = acknowledge
        self.store = store

        if parent:
            parent.adopt(self)

    def adopt(self, node):
        
        """Store and reference the potential next node"""

        assert isinstance(node, Node)
        self.__children[node.id] = node


    def set_next(self, node):

        """Selects the next node from existing node children during runtime"""

        try:
            self.__next = self.__children[node.id] if node else None

        except KeyError:
            raise Exception(f"NODE={node.name} is not adopted by NODE={self.__name}")

    @property
    def id(self):
        return self.__id
    
    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, name):
        self.__name = self.object.name + '_' + name

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
        else:
            return


class NodeBundle:

    """Can contain a group (bundle) of LinkNodes."""

    def __init__(self, entry_node, exit_node, parent=None, name='node'):

        self.__name = 'bundle' + '_' + name
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
        self.set_next(bundle.entry_node)
    
    def set_next_node(self, node):
        self.__exit_node.set_next(node)
    
    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = 'bundle' + '_' + name

    @property
    def entry_node(self):
        return self.__entry_node

    @property
    def exit_node(self):
        return self.__exit_node


class DecoyNode(Node):

    """The DecoyNode is an extension of Node that acts as a placeholder"""

    def __init__(self, name='decoy-node', parent=None):
        _object = objects.Command()
        _object.name = 'decoy'
        super().__init__(_object, parent=parent, name=name, show_instructions=False, store=False)
