# coding: utf-8
import random

import core
from things import Player, Zombie, Wall, Box
from utils import closest, distance, adjacent_positions, astar_path
from weapons import Gun, Rifle, Shotgun


class John(Player):
    """The man you send to kill the Boogeyman"""
    def next_step(self, things, data):
        if self.rules == 'extermination':
            return self.extermination_ai(things, data)
        elif self.rules == 'safehouse':
            return self.safehouse_ai(things, data)
        elif self.rules == 'evacuation':
            return self.evacuation_ai(things, data)
        elif self.rules == 'delivery':
            return self.safehouse_ai(things, data)
        return 'heal', self

    def extermination_ai(self, things, data):
        zombies, players, walls, boxes = self.filter_things(things)
        action, target = self.self_preservation()
        if action and target:
            return action, target
        action, target = self.help_critical_teammates(things, players)
        if action and target:
            return action, target
        if zombies:
            action, target = self.shoot_zombies(zombies)
            if action and target:
                return action, target
        if len(zombies) > 10:
            action, target = self.regroup(things, zombies, players, walls, boxes, data)
        else:
            action, target = self.track_zombies(things, zombies, players, walls, boxes, data)
        if action and target:
            return action, target

    def safehouse_ai(self, things, data):
        zombies, players, walls, boxes = self.filter_things(things)
        action, target = self.self_preservation()
        if action and target:
            return action, target
        action, target = self.help_critical_teammates(things, players)
        if action and target:
            return action, target
        if self.objectives and data['t'] % 4 == 0:
            action, target = self.reach_objective(things, zombies, players, walls, boxes, data)
            return action, target
        if zombies:
            action, target = self.shoot_zombies(zombies)
            if action and target:
                return action, target

    def evacuation_ai(self, things, data):
        zombies, players, walls, boxes = self.filter_things(things)
        action, target = self.self_preservation()
        if action and target:
            return action, target
        action, target = self.regroup(things, zombies, players, walls, boxes, data)
        if action and target and data['t'] % 4 == 0:
            return action, target
        if zombies:
            action, target = self.shoot_zombies(zombies)
            if action and target:
                return action, target

    def self_preservation(self):
        if self.life < 40:
            self.status = u'critical'
        elif self.life < 80:
            self.status = u'need_support'
        if self.life < 80:
            return 'heal', self
        return None, None

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

    def track_zombies(self, things, zombies, players, walls, boxes, data):
        closest_zombie = closest(self, zombies)
        if closest_zombie:
            self.status = u'tracking zombies'
            return self.go_to(closest_zombie.position, things, zombies, players, walls, boxes, data)
        return None, None

    def regroup(self, things, zombies, players, walls, boxes, data):
        x, y = self.position[0], self.position[1]
        n = 1 # self
        for player in players:
            if player.life > 0:
                n += 1
                x += player.position[0]
                y += player.position[1]
        barycenter = (int(x / n), int(y / n))
        self.status = u'regrouping at' + str(barycenter)
        return self.go_to(barycenter, things, zombies, players, walls, boxes, data)

    def reach_objective(self, things, zombies, players, walls, boxes, data):
        available = set(self.objectives)
        for player in players:
            available.discard(player.position)
        destination = closest(self, available)
        return self.go_to(destination, things, zombies, players, walls, boxes, data)

    def shoot_zombies(self, zombies):
        target = closest(self, zombies)
        in_range = distance(self, target) < self.weapon.max_range
        if in_range:
            self.status = u'need_support'
            return 'attack', target
        return None, None

    def help_critical_teammates(self, things, players):
        critical = [player for player in players if player.life > 0 and player.status == 'critical']
        if critical:
            closest_critical = closest(self, critical)
            if distance(self, closest_critical) < core.HEALING_RANGE:
                self.status = u'heal ' + closest_critical.name
                return 'heal', closest_critical
        return None, None

    def go_to(self, destination, things, zombies, players, walls, boxes, data):
        obstacles = [(players, 10), (walls, 5), (zombies, 3), (boxes, 2)]
        best_move = astar_path(self.position, destination, data['size'], obstacles)
        obstacle = things.get(best_move)
        if obstacle:
            if (not isinstance(obstacle, Player)):
                self.status = u'shoot at obstacle'
                return 'attack', obstacle
        return 'move', best_move


def create(rules, objectives=None):
    w = Shotgun()
    if rules == 'extermination':
        w = Rifle()
    return John('john', 'white', weapon=w, rules=rules,
                  objectives=objectives)
