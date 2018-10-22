# coding: utf-8
from game import Rules
from things import Zombie


class DeliveryRules(Rules):
    """A kind of game where players must deliver pizza"""
    def __init__(self, game):
        super().__init__(game)
        self.pizza_delivery_points = set(self.game.map.objectives)

    def game_ended(self):
        """Has the game ended?"""
        for player in self.game.players:
            self.pizza_delivery_points.discard(player.position)
        return not self.players_alive() or not self.pizza_delivery_points  # all delivery points were reached

    def game_won(self):
        """Was the game won?"""
        if self.players_alive():
            return True, 'you delivered pizza! :)'
        else:
            return False, 'pizza has been eaten by zombies... :('


def create(game):
    return DeliveryRules(game)
