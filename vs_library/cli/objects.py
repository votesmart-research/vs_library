
# built-ins
from abc import ABC, abstractmethod
import time

# internal packages
from . import textformat

# external packages
from tabulate import tabulate


class CliObject(ABC):
    
    """A blueprint of a command line interface object (CliObject). CliObject allows for a user interaction on a command line. 
       It can be traversed when paired with CliNode"""

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

    """The Command class is a CliObject that allows other objects to execute a method and prints a return message."""

    def __init__(self, method=None, value='', respond=False, command=None):

        super().__init__(name='command', command=command, exe_seq=None)

        self.method = method
        self.value = value
        self.respond = respond
        self.__message = None

    def draw(self):
        if self.__message:
            print(self.__message)

    def execute(self):
        results = None

        if self.method:
            self.__message = self.method()

            if self.respond and not self.exe_seq:    
                self.draw()

        if isinstance(self.command, Command):
            self.command.execute()

        return results

    def __str__(self):
        return self.value


class Display(CliObject):

    """The Display class is a CliObject that diplays messages on the command line."""

    def __init__(self, message, command=None):
        super().__init__(name='display', command=command, exe_seq='after')

        self.message = message
        self.format_dict = None

    def draw(self):
        if self.format_dict:
            print(self.message.format(**self.format_dict))
        else:
            print(self.message)

    def execute(self):
        if isinstance(self.command, Command):
            self.command.execute()


class Prompt(CliObject):

    """The Prompt class is a CliObject that allows user inputs in response to a prompt."""

    def __init__(self, question, options=None, verification=None, multiple_selection=False, command=None):

        super().__init__(name='prompt', command=command, exe_seq='after')

        self.__question = Display(question)
        self.options = options if options else {}
        self.verification = verification
        self.multiple_selection = multiple_selection

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
    
    def option_responses(self, string=False):
        response = []

        for r in self.__responses:

            if self.options:
                if isinstance(self.options[r], Command):
                    response.append(self.options[r].value)
                else:
                    response.append(self.options[r])

        return response if not string else ', '.join(response)

    def _verify(self):

        if self.verification:
            verified = []
            error_messages = []

            for response in self.__responses:
                result = self.verification(response)

                if isinstance(result, tuple) and len(result) > 1 :
                    verified.append(result[0])
                    error_messages.append(result[1])
                else:
                    verified.append(result)

            if error_messages:
                self.__error_msg = '\n'.join(map(lambda s: textformat.apply(s, emphases=['italic'], text_color='red'), 
                                                 error_messages
                                                 )
                                            )
            return all(verified)

        elif not self.verification and self.options:
            return all(r.strip() in self.options.keys() for r in self.__responses)

        else:
            return True

    def draw(self):

        def _single(self):
            self.question.draw()
            self.__responses = [input(f"{str(self)}>> ")]

        def _multiple(self):
            self.question.draw()
            self.__responses = input(f"{str(self)}>> ").split(',')
            if '**' in self.options.keys() and self.__responses == ['**']:
                self.__responses = [o for o in self.options.keys() if o!='**']
        
        if self.multiple_selection:
            _multiple(self)
        else:
            _single(self)

        while not self._verify():
            print(f"{self.__error_msg}\n")
            time.sleep(0.75)

            if self.multiple_selection:
                _multiple(self)
            else:
                _single(self)

        if self.options:
            for r in set(self.__responses):
                cleaned_r = r.strip()
                if isinstance(self.options[cleaned_r], Command):
                    self.options[cleaned_r].execute()

    def execute(self):
        if isinstance(self.command, Command):
            self.command.execute()

    def clear(self):
        if self.__responses:
            self.__responses.clear()

    def __str__(self):
        if self.multiple_selection:
            options_msg = textformat.apply("Please enter one or more of the options above separated by a comma", emphases=['italic'])
        else:
            options_msg = textformat.apply("Please enter one of the options above", emphases=['italic'])
            
        options_str = '\n'.join([f'\t[{str(k)}] {str(v)}' for k, v in self.options.items()]) if self.options else ''

        return f"\n{options_str}\n\n{options_msg}\n" if self.options else ''


class Table(CliObject):

    """The Table class is a CliObject that display information in a tabular format on the command line."""

    def __init__(self, table, header=True, command=None):
        super().__init__(name='table', command=command, exe_seq='before')

        self.table = table
        self.header = header
        
        self.table_header = ""
        self.description = ""

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
        if self.header:
            return tabulate(self.table, headers='firstrow', tablefmt='grid')
        else:
            return tabulate(self.table, tablefmt='grid')
