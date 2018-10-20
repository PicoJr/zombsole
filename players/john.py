# coding: utf-8
import random

import core
from things import Player, Zombie, Wall, Box
from utils import closest, distance, adjacent_positions, astar_path
from weapons import Gun


class John(Player):
    """The man you send to kill the Boogeyman"""
    def next_step(self, things, data):
        zombies, players, walls, boxes = self.filter_things(things)
        if self.life < 50:
            self.status = u'need_support'
            return 'heal', self
        if self.objectives and data['t'] % 4 != 0:
            action, target = self.reach_objective(things, zombies, players, walls, boxes, data)
            return action, target
        if zombies:
            action, target = self.shoot_zombies(zombies)
            if action and target:
                return action, target
        action, target = self.support_teammates(things, players)
        if action and target:
            return action, target
        return 'heal', self

    def filter_things(self, things):
        zombies, players, walls, boxes = [], [], [], []
        for thing in things.values():
            if isinstance(thing, Zombie):
                zombies.append(thing)
            elif isinstance(thing, Player) and thing.position != self.position:
                players.append(thing)
            elif isinstance(thing, Wall):
                walls.append(thing)
            elif isinstance(thing, Box):
                boxes.append(thing)
        return zombies, players, walls, boxes


    def reach_objective(self, things, zombies, players, walls, boxes, data):
        available = set(self.objectives)
        for player in players:
            available.discard(player.position)
        target = closest(self, available)
        obstacles = [(players, 10), (walls, 5), (zombies, 3), (boxes, 2)]
        best_move = astar_path(self.position, target, data['size'], obstacles)
        obstacle = things.get(best_move)
        if obstacle:
            if (isinstance(obstacle, Wall) or isinstance(obstacle, Box)):
                self.status = u'shoot at obstacle'
                return 'attack', obstacle
        return 'move', best_move

    def shoot_zombies(self, zombies):
        target = closest(self, zombies)
        in_range = distance(self, target) < self.weapon.max_range
        if in_range:
            self.status = u'need_support'
            return 'attack', target
        return None, None

    def support_teammates(self, things, players):
        support = [player for player in players if 0 < player.life and player.status == 'need_support']
        target = closest(self, support)
        if target:
            target_injured = target.life < 100
            if distance(self, target) < core.HEALING_RANGE and target_injured:
                self.status = u'heal ' + target.name
                return 'heal', target
            else:
                best_move = closest(target, adjacent_positions(self))
                obstacle = things.get(best_move)
                if obstacle and not isinstance(obstacle, Player):
                    self.status = u'shoot at obstacle'
                    return 'attack', obstacle
                return 'move', best_move
        return None, None


def create(rules, objectives=None):
    return John('john', 'white', weapon=Gun(), rules=rules,
                  objectives=objectives)
