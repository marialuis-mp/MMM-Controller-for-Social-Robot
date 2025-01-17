import time
from enum import Enum

from experimentNao.interaction import verbose
from experimentNao.interaction.nao_behaviour.nao_requests import NaoClient
from experimentNao.interaction.nao_behaviour.requests_enums import ComplexMovements


class RewardSystemSimple:
    def __init__(self, nao_client, output_command, random_, nao_offering_rewards=True):
        """ System that manages giving the rewarding movements to the participants (simplified version)

        Parameters
        ----------
        nao_client : Union[experimentNao.interaction.nao_behaviour.nao_requests.NaoClient, None]
        output_command : function
        random_ : random.Random
        nao_offering_rewards : bool
        """
        # nao related
        self.nao_client = nao_client
        self.output_command = output_command
        self.nao_offering_rewards = nao_offering_rewards
        self.random = random_
        self.reward_list = []
        self.set_reward_list()

    def set_reward_list(self):
        """ list of rewards given to the participants

        """
        # self.reward_list = [Reward(ComplexMovements.TAI_CHI, 'I will practice some tai chi for you')]
        self.reward_list = [Reward(ComplexMovements.PICTURE, 'I will take a picture of this moment!'),
                            Reward(ComplexMovements.TAI_CHI, 'I will practice some tai chi for you'),        # move left
                            Reward(ComplexMovements.PLAY_GUITAR, 'I will show you how I play the guitar!'),  # move left
                            Reward(ComplexMovements.ELEPHANT, 'I will show you my favourite animal'),
                            Reward(ComplexMovements.DANCE, 'I will dance for you!')]

    def update_and_run(self, puzzle_was_skipped: bool, current_puzzle: int):
        """ updates the system (flags and variables) and gives the reward if needed

        Parameters
        ----------
        puzzle_was_skipped : bool
            whether the current puzzle was skipped (or alternatively, complete)
        current_puzzle : int
            number of the current puzzle in the session
        """
        if self.check_if_reward_to_be_given_in_puzzle(puzzle_was_skipped, current_puzzle):
            self.give_random_reward()

    def check_if_reward_to_be_given_in_puzzle(self, puzzle_was_skipped: bool, current_puzzle: int):
        """ checks whether the current puzzle is the correct moment for a reward to be given

        Parameters
        ----------
        puzzle_was_skipped : bool
            whether the current puzzle was skipped (or alternatively, complete)
        current_puzzle : int
            number of the current puzzle in the session

        Returns
        -------

        """
        return False if puzzle_was_skipped else True

    def give_random_reward(self):
        """ gives a random reward to the participant

        Returns
        -------

        """
        if self.nao_offering_rewards:
            # Minimum times that any reward was given
            min_times_selected = min(reward.n_times_reward_was_given for reward in self.reward_list)
            # Filter rewards to include only those with the minimum selection count
            eligible_rewards = [r for r in self.reward_list if r.n_times_reward_was_given == min_times_selected]
            reward = self.random.choice(eligible_rewards)   # Randomly select one reward from the eligible ones
            reward.give_reward(self.output_command, self.nao_client, self.random, give_reason_of_reward=False)
            return True
        return False


class RewardSystemScheduled(RewardSystemSimple):
    def __init__(self, nao_client, output_command, random_, n_puzzles_per_group, max_n_of_puzzles,
                 nao_offering_rewards=True):
        """ System that manages giving the rewarding movements to the participants (scheduled version)

        Parameters
        ----------
        nao_client : Union[experimentNao.interaction.nao_behaviour.nao_requests.NaoClient, None]
        output_command : function
        random_ : random.Random
        n_puzzles_per_group : int
        max_n_of_puzzles : int
        nao_offering_rewards : bool
        """
        super().__init__(nao_client, output_command, random_, nao_offering_rewards)
        self.n_puzzles_per_group = n_puzzles_per_group
        self.max_number_of_puzzles = max_n_of_puzzles
        self.times_per_group_nao_helping = 1
        self.reward_given_in_puzzle = []

    def update_and_run(self, puzzle_was_skipped: bool, current_puzzle: int):
        """ updates the system (flags and variables) and gives the reward if needed

        Parameters
        ----------
        puzzle_was_skipped : bool
            whether the current puzzle was skipped (or alternatively, complete)
        current_puzzle : int
            number of the current puzzle in the session
        """
        give_reward = self.check_if_reward_to_be_given_in_puzzle(puzzle_was_skipped, current_puzzle)
        if give_reward:
            self.give_random_reward()
        self.reward_given_in_puzzle.append(give_reward)

    def check_if_reward_to_be_given_in_puzzle(self, puzzle_was_skipped: bool, current_puzzle: int):
        """ checks whether the current puzzle is the correct moment for a reward to be given

        Parameters
        ----------
        puzzle_was_skipped : bool
            whether the current puzzle was skipped (or alternatively, complete)
        current_puzzle : int
            number of the current puzzle in the session

        Returns
        -------

        """
        if puzzle_was_skipped:    # if puzzle not completed: don't give reward
            return False
        if self.times_per_group_nao_helping == self.n_puzzles_per_group:     # if always give reward
            return True
        pos_of_puzzle_in_group = current_puzzle % self.n_puzzles_per_group  # 1st, 2nd, etc..
        first_of_group = current_puzzle - pos_of_puzzle_in_group            # 1st of this group
        if self.reward_given_in_puzzle[first_of_group:].count(True) >= self.times_per_group_nao_helping:
            return False         # if reward was already given in this group as many times as allowed
        probability_of_reward = 1 / (self.n_puzzles_per_group - pos_of_puzzle_in_group)
        return self.random.uniform(0, 1) < probability_of_reward


class Reward:
    def __init__(self, reward_movement: ComplexMovements, reward_txt):
        """ Achievements that can be reached by the participants, their requirements and rewards.

        Parameters
        ----------
        reward_movement : reward given to the participant if achievement is fulfilled
        """
        self.reward = reward_movement
        self.reward_txt = reward_txt
        self.n_times_reward_was_given = 0

    def give_reward(self, output_command, nao_client: NaoClient, random, give_reason_of_reward=False):
        """ Give this reward to the participant, by making Noa speak out which movement it will do,
        and by performing the movement corresponding to this reward.

        Parameters
        ----------
        output_command : function
        nao_client : Union[experimentNao.interaction.nao_behaviour.nao_requests.NaoClient, None]
        random : random.Random
        give_reason_of_reward : bool
        """
        output_command(self.generate_reward_txt(random, give_reason_of_reward))
        self.make_nao_give_reward(output_command, nao_client)
        self.n_times_reward_was_given += 1

    def generate_reward_txt(self, random, give_reason_of_reward=False):
        """ generates the text that Nao speaks before giving the reward

        Parameters
        ----------
        random : random.Random
        give_reason_of_reward : bool

        Returns
        -------

        """
        intro_txt = random.choice(['Since you are doing a great job, ', 'You are doing some progress. So, '])
        return intro_txt + ' ' + self.generate_reward_description_txt(random)

    def generate_reward_description_txt(self, random):
        """ generates the text that describes the reward

        Parameters
        ----------
        random : random.Random

        Returns
        -------

        """
        return random.choice(['I will give you a reward.', 'I will do something for you.',
                              'I am going to give you a reward.']) + ' ' + self.reward_txt

    def make_nao_give_reward(self, output_command, nao_client):
        """ creates the sequence that needs to be sent to the Nao client in order to give the reward to the participant

        Parameters
        ----------
        output_command : function
        nao_client : Union[experimentNao.interaction.nao_behaviour.nao_requests.NaoClient, None]
        """
        if nao_client is not None:
            time.sleep(1)
            nao_client.make_a_coordinated_movement(self.reward)
            time.sleep(1)
            print('Movement finished')
        else:
            output_command('I cannot give the reward now, sorry.')
