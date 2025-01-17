from abc import ABCMeta
from lib.tom_model.model_elements.linkage import influencer
from lib.tom_model.fis_support_functions import fis_rules as rules
from lib.tom_model import config


class CognitiveVariable:
    __metaclass__ = ABCMeta
    next_tag = 0

    def __init__(self, name, initial_value=0, range_values=(-1, 1), verbal_terms=tuple(), mf_type='default',
                 update_rate=1):
        # Common Part
        if type(name) is str:
            self.name = name
        else:
            raise TypeError("Name of variable must be a string")
        if type(initial_value) in [int, float]:
            self.value = initial_value
            self.next_value = initial_value
            self.values = []
        else:
            raise TypeError("Initial value of variable must be numeric")
        if isinstance(range_values, (list, tuple)) and len(range_values) == 2:
            self.minimum_value = range_values[0]
            self.maximum_value = range_values[1]
        else:
            raise TypeError("Range values must be a tuple of 2 values")
        # Object of variable : object/entity about which the variable is about (e.g., a dog/a bottle/etc...)
        self.object_of_variable = None  # if there are multiple B,G,E about mult entities, the entity this var is about
        self.tag = CognitiveVariable.next_tag
        self.terms = verbal_terms
        self.update_rate = update_rate
        if config.FRAMEWORK == 'FIS':
            [self.consequent, self.antecedent] = rules.declare_antecedent_and_consequent(self.name, verbal_terms,
                                                                                         range_values, mf_type)
        CognitiveVariable.next_tag += 1

    def update_value(self):
        """ Updates the value of the variable for the next time step according to a value that was already computed
        and saved in self.next_value. The value of self.next_value is now useless. The update rate is how much the
        variable's value in the next time step is updated with the computed value. For example, if learning_rate is 0.9,
        the value of the variable in the next step is 90% the computed value for the next time step (self.next_value)
        and 10% the current value of the variable.

        Parameters
        ----------
        """
        self.value = self.next_value * self.update_rate + self.value * (1-self.update_rate)

    def set_object_about(self, object_):
        """ Sets the type of object the variable is about. For example, a car ('Belief that the car is blue', or
        'Goal to drive the car'). It can correspond to a person, an object, an animal, etc...

        Parameters
        ----------
        object_ :
        """
        self.object_of_variable = object_

    def print_variable(self, round_values=False, short_names=False, ident=False, get_value=True, get_type=True):
        """ Prints the information about the variable, according to the configuration parameters. The information
        printed is the type of variable (Belief, Goal, ...), the name, and the value.

        Parameters
        ----------
        get_type : If the type variable is to be printed
        get_value : If the value of the variable is to be printed
        round_values : If the value should be rounded to 3 decimal cases
        short_names : If the name of the variable must be shortened
        ident : if the strings should have a length that is the same for all the variables
        """
        print(self.get_string_with_info_about_variable(round_values, short_names, ident, get_value, get_type))

    def get_string_with_info_about_variable(self, round_values=False, short_names=False, ident=False,
                                            get_value=True, get_type=True):
        """ Generates a string with the main information about the variable, according to the configuration parameters.

        Parameters
        ----------
        get_type : If the type variable is to be printed
        get_value : If the value of the variable is to be printed
        round_values : If the value should be rounded to 3 decimal cases
        short_names : If the name of the variable must be shortened
        ident : if the strings should have a length that is the same for all the variables

        Returns
        -------

        """
        type_str_size = 12
        name_str_size = 30
        str_type = str(type(self).__name__)
        str_name = str(self.name)
        if round_values or ident:
            str_value = str(round(self.value, 3))
        else:
            str_value = str(self.value)
        if short_names:
            if len(str_type) > type_str_size:   # make all string with type to have 8
                # find upper case
                new_str_type = ''
                for character in str_type:
                    if character.isupper():
                        new_str_type = new_str_type + character + ' '
                str_type = new_str_type
        if ident:
            while len(str_type) < type_str_size:
                str_type = str_type + ' '
            while len(str_name) < name_str_size:
                str_name = str_name + ' '
            while len(str_value) < 7:
                str_value = str_value + ' '
        string2return = str()
        if get_type:
            string2return += '## ' + str_type + ' ## '
        string2return += str_name
        if get_value:
            string2return += '  Value: ' + str_value
        return string2return

    def show_membership_functions(self):
        self.antecedent.view()

    def print_mf_function(self):
        self.consequent.view(sim=self.var_fis)

    def get_name_of_type(self):
        return str(type(self).__name__)


def is_pair_variable_value(pair):
    if len(pair) == 2:
        return (isinstance(pair[0], CognitiveVariable)) and (type(pair[1]) in influencer.Influencer.connection_type)
    return False
