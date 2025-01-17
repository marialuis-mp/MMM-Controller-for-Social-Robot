class Parameter2Optimise:
    def __init__(self, minimum_value, maximum_value, var_or_linkage_represented=None, value=None, name=None):
        self.value = value
        self.minimum_value = minimum_value
        self.maximum_value = maximum_value
        self.number_of_discrete_values = None
        self.var_or_linkage_represented = var_or_linkage_represented
        self.step = None
        self.name = name

    def set_value_of_parameter(self, value):
        self.value = self.bound_value(value)

    def get_value_of_parameter(self):
        return self.value

    def generate_random_value(self, random):
        self.value = random.uniform(self.minimum_value, self.maximum_value)

    def set_step_and_number_of_discrete_values(self, step: float):
        self.number_of_discrete_values = round((self.maximum_value - self.minimum_value) / step + 1)
        self.step = step

    def bound_value(self, value):
        return min(max(value, self.minimum_value), self.maximum_value)