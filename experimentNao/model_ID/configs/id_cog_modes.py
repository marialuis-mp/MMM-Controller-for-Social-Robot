from enum import Enum


class IdCogModes(Enum):
    """ Modes to identify the cognition and perception modules of the theory of mind model

    """
    VAR_BY_VAR = 1  # Identifying variables of the cognitive model one by one
    ALL = 2         # Identifying variables of the cognitive model all at once
    # SEP_PER_X: identifies the perception and cognition separately, using different methods
    # SEP_PER_1: Identifies the perception using only the time steps where the emotions are not very extreme (i.e.,
    # are close to 0). In these time steps, the bias is negligible, and the approximation of the bias being null can be
    # made. This allows identifying the perception under the assumption that the bias is null and the rationally
    # perceived knowledge is the same as the belief.
    SEP_PER_1 = 3   # 1: perception; 2: cognition
    SEP_PER_2 = 4   # 1: perception; 2: both
    SEP_PER_3 = 5   # 1: perception; 2: cognition; 3: both
