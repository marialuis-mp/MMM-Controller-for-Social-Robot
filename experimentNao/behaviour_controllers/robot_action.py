class RobotAction:
    def __init__(self, puzzle_difficulty_level, give_reward):
        """ action that the controller of the robot can perform

        Parameters
        ----------
        puzzle_difficulty_level : int
        give_reward : bool
        """
        self.puzzle_difficulty_level = puzzle_difficulty_level
        self.give_reward = give_reward
        self.cost = 0
        self.active_actions = None
        self.respects_soft_constraints = None
        self.respects_hard_constraints = None
        self.respects_all_constraints = None

    def reset_costs(self):
        """ resets the cost of this action

        """
        self.cost = 0

    def set_cost(self, cost: float):
        """ sets the cost of taking this action in the current time step

        Parameters
        ----------
        cost : float
        """
        self.cost = cost

    def set_respected_constraints(self, respects_hard_constraints, respects_soft_constraints):
        """ sets which constraints are respected if this action is taken in the current time step

        Parameters
        ----------
        respects_hard_constraints : bool
        respects_soft_constraints : bool
        """
        self.respects_hard_constraints = respects_hard_constraints
        self.respects_soft_constraints = respects_soft_constraints
        self.respects_all_constraints = respects_soft_constraints and respects_hard_constraints

    def get_action_info(self, simple=True):
        """ returns the basic information about this action

        Parameters
        ----------
        simple : bool

        Returns
        -------

        """
        info = 'Diff.:{}\t\tReward:{}\t\tCost:{}'.format(self.puzzle_difficulty_level, self.give_reward, self.cost)
        if not simple:
            info += '\t\tAll const.:{}\t\tHard const.:{}'.format(self.respects_all_constraints,
                                                                 self.respects_hard_constraints)
        return info
