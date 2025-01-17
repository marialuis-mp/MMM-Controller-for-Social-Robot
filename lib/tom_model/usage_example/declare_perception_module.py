import lib.tom_model.model_elements.variables.perception_variables
from lib.tom_model.model_elements.processes import perceptual_access, rational_reasoning


class FoodData:
    def __init__(self):
        self.there_is = None
        self.not_expired = None

    def set_data(self, there_is, not_expired):
        self.there_is = there_is
        self.not_expired = not_expired


# Variables
class FoodRLD(lib.tom_model.model_elements.variables.perception_variables.RealLifeData):
    def __init__(self, name: str, data: FoodData):
        super().__init__(name, data)


class FoodPerceivedData(lib.tom_model.model_elements.variables.perception_variables.PerceivedData):
    def __init__(self, name: str, data: FoodData):
        super().__init__(name, data)


class FoodPerceivedKnowledge(lib.tom_model.model_elements.variables.perception_variables.PerceivedKnowledgeSet):
    def __init__(self, name: str, raw_data, knowledge):
        super().__init__(name, raw_data, knowledge)


# Processes
class FoodPerceptualAccess(perceptual_access.PerceptualAccess):
    def __init__(self, inputs, outputs):
        super().__init__(inputs, outputs, function=self.run_perceptual_access,
                         input_type=FoodRLD, output_type=FoodPerceivedData)

    def run_perceptual_access(self):
        pass    # define here what happens in your perceptual access


class FoodRationalReasoning(rational_reasoning.RationalReasoning):
    def __init__(self, inputs, outputs):
        super().__init__(inputs, outputs, function=self.run_rational_reasoning,
                         input_type=FoodPerceivedData, output_type=FoodPerceivedKnowledge)

    def run_rational_reasoning(self):
        for output in self.outputs.knowledge:
            pass  # define here what happens in your rational reasoning
