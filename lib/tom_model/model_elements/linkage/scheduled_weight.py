class ScheduledWeight:
    def __init__(self, weights=None, changing_points=(0,), boundary_values=(-1, 1)):
        if weights is None:
            weights = [0.0, 0.0]
        assert len(weights) == len(changing_points) + 1
        self.weights = weights
        self.changing_points = changing_points
        self.boundary_values = boundary_values

    def get_active_weight(self, value_of_influencer: float):   # return weight whose domain contains value_of_inf...
        index = next((i for i, limit_value in enumerate(self.changing_points) if value_of_influencer < limit_value), -1)
        return self.weights[index], index
