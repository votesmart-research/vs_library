
# built-ins
from abc import ABC, abstractmethod
import time

# internal packages
from . import textformat

# external packages
from tabulate import tabulate


class CliObject(ABC):
    
    """
    A blueprint of a command line interface object (CliObject)

    CliObjects is to provide user interaction with the application on the command line
    
    Attributes
    ----------
    name : str
        Name associated with the type of object

    command : cli.objects.Command
        A Command object that is used in the execute() method

    exe_seq : str
        'before' to denote command is executed before object is drawn
        'after' to denote command is executed after object is drawn.
    """

    def __init__(self, name, command, exe_seq):

        self.name = name
        self.command = command
        self.exe_seq = exe_seq

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def execute(self):
        pass


class Command(CliObject):

    """The Command class is a CliObject that allows other objects to execute a method and prints a return message"""

    def __init__(self, method, value='', respond=False, command=None):

        """
        Parameters
        ----------
        method : function
            Can be any python functions and can return a message

        value : str, optional
            A string representation of object when printed to terminal

        respond : bool, default=False
            If True, the return message from method will be drawn
        """

        super().__init__(name='command', command=command, exe_seq=None)

        self.method = method
        self.value = value
        self.respond = respond
        self.__message = None

    def draw(self):
        if self.__message:
            print(self.__message)

    def execute(self):

        if self.method:
            self.__message = self.method()
            
            if self.respond and not self.exe_seq:
                self.draw()

        # useful for creating a chained Command
        if isinstance(self.command, Command):
            self.command.execute()

    def __str__(self):
        return str(self.value)


class Display(CliObject):

    """The Display class is a CliObject that diplays messages on the command line"""

    def __init__(self, message, format_dict=None, command=None):
        
        """
        Parameters
        ----------
        message : str
            A string to be printed on the terminal when object is drawn

        format_dict : dict, default=None
            A dictionary containing parameters to format a string variable utilizing
            the str.format() method
        """

        super().__init__(name='display', command=command, exe_seq='after')

        self.message = message
        self.format_dict = format_dict if format_dict else dict()

    def draw(self):

        print(str(self))

    def execute(self):
        if isinstance(self.command, Command):
            self.command.execute()

    def __str__(self):
        if self.format_dict:
            return self.message.format(**self.format_dict)
        else:
            return self.message


class Prompt(CliObject):

    def __init__(self, 
                 question, 
                 options=None, 
                 verification=None, 
                 multiple_selection=False, 
                 command=None,
                 show_opt_msg=True):


        super().__init__(name='prompt', command=command, exe_seq='after')

        self.__question = Display(question)
        self.options = options if options else dict()
        self.verification = verification
        self.multiple_selection = multiple_selection
        self.show_opt_msg = show_opt_msg

        self.__responses = []
        self.__error_msg = textformat.apply("Your input(s) are not recognizable, please try again.", 
                                            emphases=['italic'], text_color='red')

    @property
    def question(self):
        return self.__question

    @question.setter
    def question(self, question):
        self.__question = Display(question)

    @property
    def responses(self):
        return self.__responses if self.multiple_selection else next(iter(self.__responses))
    
    def option_responses(self, string=True):


        responses = []

        for r in self.__responses:

            if self.options:
                responses.append(str(self.options[r]))

        return ", ".join(responses) if string else responses

    def _verify(self):


        # the presence of verification will take precedence over verifying against option given
        if self.verification:
            verified = []
            error_messages = []

            for response in self.__responses:
                result = self.verification(response)
                
                # some returns from verification function can be a boolean and a string
                if isinstance(result, tuple) and len(result) > 1 :
                    verified.append(result[0])
                    error_messages.append(result[1])
                else:
                    verified.append(result)

            if error_messages:
                self.__error_msg = '\n'.join(map(lambda s: textformat.apply(s, emphases=['italic'], text_color='red'), 
                                                 error_messages))
            return all(verified)

        # verifying against option will only take place if no verification is given
        elif not self.verification and self.options:
            return all(r.strip() in self.options.keys() for r in self.__responses)

        else:
            return True

    def draw(self):

        # to receive a response
        def _single(self):
            self.question.draw()
            self.__responses = [input(f"{str(self)}>: ")]

        # to receive multiple responses
        def _multiple(self):
            self.question.draw()
            self.__responses = input(f"{str(self)}>: ").split(',')

            # ** is a unique option that allows user to select all of the option
            if '**' in self.options.keys() and self.__responses == ['**']:
                self.__responses = [o for o in self.options.keys() if o!='**']
        
        if self.multiple_selection:
            _multiple(self)
        else:
            _single(self)

        while not self._verify():
            print(f"{self.__error_msg}\n")
            time.sleep(0.75) # to provide user acknowledgement if something went wrong

            if self.multiple_selection:
                _multiple(self)
            else:
                _single(self)

        # executes the selected option if it is a Command
        if self.options:
            for r in set(self.__responses):
                r = r.strip()
                if r in self.options:
                    if isinstance(self.options[r], CliObject):
                        self.options[r].execute()

    def execute(self):
        if isinstance(self.command, Command):
            self.command.execute()

    def clear(self):

        if self.__responses:
            self.__responses.clear()

    def __str__(self):

        if self.show_opt_msg:
            if self.multiple_selection:
                options_msg = textformat.apply("Please enter one or more of the options above separated by a comma\n", 
                                            emphases=['italic'])
            else:
                options_msg = textformat.apply("Please enter one of the options above\n", emphases=['italic'])
        else:
            options_msg = ""
            
        options_str = '\n'.join([f'\t[{str(k)}] {str(v)}' for k, v in self.options.items()]) if self.options else ''

        combined = "\n".join((f"{options_str}\n", options_msg))

        return f"\n{combined}" if self.options else ''


class Table(CliObject):

    """
    The Table class is a CliObject that display information in a tabular format on the command line
    
    This is dependent on 'tabulate' python package see here:
    https://pypi.org/project/tabulate/

    Attributes
    ----------
    table_header : str, optional
        String bolded and centered at the top of the table to provide intro to the table

    description : str, optional
        String italicized and left justified at the bottom of the table to provide 
        a description of the table
    """

    def __init__(self, table, header=True, command=None):

        """
        Parameters
        ----------
        table : list
            List within the list will be a row of the table

        header : bool, default=True
            If true, table emphasize the first row as header
        """

        super().__init__(name='table', command=command, exe_seq='before')

        self.table = table
        self.header = header
        
        self.table_header = ""
        self.description = ""

    def clear(self):
        
        """Clears the table"""
        
        if self.header:
            del self.table[1:]
        else:
            self.table.clear()

    def draw(self):
        table_str = str(self)
        table_length = max(map(len, table_str.split('\n')))

        if self.table_header:
            center_header = self.table_header.center(table_length)
            print(textformat.apply(center_header, emphases=['bold']))

        print(table_str)
        
        if self.description:
            ljust_desc = self.description.ljust(table_length)
            print(textformat.apply(ljust_desc, emphases=['italic']))

    def execute(self):
        if isinstance(self.command, Command):
            self.command.execute()

    def __str__(self):

        """Returns a tabulated string"""

        if self.header:
            return tabulate(self.table, headers='firstrow', tablefmt='grid')
        else:
            return tabulate(self.table, tablefmt='grid')
