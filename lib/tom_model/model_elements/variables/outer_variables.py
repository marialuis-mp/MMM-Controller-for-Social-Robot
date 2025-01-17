from abc import ABCMeta, abstractmethod


class OuterElement:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, name, verbal_terms=()):
        """ General class for the outer elements, which are the processes of the modules module or of the
        decision-making module.

        Parameters
        ----------
        name : str
            Name that identifies the process.
        verbal_terms: tuple
            List of verbal terms associated with the process. It is optional
        """
        self.name = name
        self.terms = verbal_terms
