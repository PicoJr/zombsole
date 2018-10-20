# coding: utf-8
from game import Rules
from things import Zombie

TICKS = 200

class SurvivalRules(Rules):
    """A kind of game where players must kill at least TICKS ticks.
    """
    def game_ended(self):
        """Has the game ended?"""
        return not self.players_alive() or self.game.world.t > TICKS

    def game_won(self):
        """Was the game won?"""
        if self.players_alive():
            return True, 'you survived long enough :)'
        else:
            return False, 'players exterminated! :('


def create(game):
    return SurvivalRules(game)
