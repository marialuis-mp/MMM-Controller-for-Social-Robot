import copy

from lib.tom_model.model_elements.variables import fst_dynamics_variables
from lib.tom_model.model_elements.variables.outer_variables import OuterElement


class RealLifeData(OuterElement):
    def __init__(self, name: str, data):
        super().__init__(name)
        self.data = data


class PerceivedData(OuterElement):
    def __init__(self, name: str, data):
        super().__init__(name)
        self.data = data


class PerceivedKnowledgeSet(OuterElement):
    def __init__(self, name: str, raw_data, knowledge):
        super().__init__(name)
        self.raw_data = raw_data            # Type of raw data
        self.knowledge = []                 # Variables of type fast dynamics (judgements about environment)
        assert isinstance(knowledge, (list, dict))
        if isinstance(knowledge, list):     # iterate through the pieces of knowledge if knowledge is a list
            for piece in knowledge:
                self.add_knowledge(piece)
            self.knowledge_dict = None
        else:
            for piece in list(knowledge.values()):  # iterate through the pieces of knowledge if knowledge is a dict
                self.add_knowledge(piece)
            self.knowledge_dict = knowledge
        self.knowledge = tuple(self.knowledge)

    def add_knowledge(self, piece_of_knowledge):
        if isinstance(piece_of_knowledge, fst_dynamics_variables.RationallyPerceivedKnowledge):
            self.knowledge.append(piece_of_knowledge)
        elif isinstance(piece_of_knowledge, list):
            for piece in piece_of_knowledge:
                self.add_knowledge(piece)
        else:
            raise TypeError('Variable of wrong type')

    def __deepcopy__(self, memo):
        raw_data = copy.deepcopy(self.raw_data)
        if self.knowledge_dict is not None:
            knowledge = dict()
            for key in self.knowledge_dict:
                knowledge[key] = copy.deepcopy(self.knowledge_dict[key])
        else:
            knowledge = []
            for piece in self.knowledge:
                knowledge.append(copy.deepcopy(piece))
        result = type(self)(copy.copy(self.name), raw_data, knowledge)
        return result
