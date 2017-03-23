#!/usr/bin/env python

from sopel.module import commands
import random
# from collections import Counter
from itertools import cycle


class Player():
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.pairs = 0

    def fish(self, card):
        if card not in self.hand:
            self.hand.append(card)
        else:
            self.pairs += 1
            self.hand.remove(card)

    def get_hand(self):
        return sorted(self.hand)


def setup(bot):
    bot.memory['gofish'] = {
        'active': False
    }


@commands('gofish')
def gofish(bot, trigger):
    if not bot.memory['gofish']['active']:
        start(bot, trigger)
    else:
        fish(bot, trigger)


def start(bot, trigger):
    if not trigger.group(2):
        bot.say('Error: choose a user to play against')
        bot.say('.gofish <user1> {<user2> ...}')
        return

    players = [Player(i) for i in [trigger.nick] + trigger.group(2).split()]

    if not all([i in bot.users for i in [j.name for j in players]]):
        bot.say('Not all users are online')
        return

    if len(set(players)) < 2:
        bot.say('Not enough players!')
        return

    bot.memory['gofish']['deck'] = random.sample('A23456789XJQK'*4, 52)

    if len(players) == 2:
        initcards = 7
    else:
        initcards = 5

    # deal cards
    for player in players:
        for i in range(initcards):
            player.fish(bot.memory['gofish']['deck'].pop())

    bot.say('Game started with {}'.format(', '.join(i.name for i in players)))
    bot.memory['gofish']['active'] = True

    random.shuffle(players)
    bot.memory['gofish']['players'] = cycle(players)
    bot.memory['gofish']['current'] = next(bot.memory['gofish']['players'])
    gofishscores(bot, trigger)

    bot.say('{}\'s go!'.format(bot.memory['gofish']['current'].name))
    bot.say('To play: .gofish <player> <card>')


def fish(bot, trigger):
    if not trigger.group(2) or len(trigger.group(2).split()) < 2:
        bot.say('To play: .gofish <player> <card>')
        return

    player, card = trigger.group(2).split()

    if player not in bot.users:
        bot.say('{} isn\'t in the game! Pick again'.format(player))
        return

    if card not in 'A23456789XJQK':
        bot.say('{} isn\'t a card! Pick again from A23456789JQK'.format(card))
        return


@commands('gfcards')
def gofishcards(bot, trigger):
    pass


@commands('gfend')
def gofishend(bot, trigger):
    pass


@commands('gfscores')
def gofishscores(bot, trigger):
    players = bot.memory['gofish']['players']

    bot.say('Current scores:')
    scores = {}
    player = next(players)
    while player.name not in scores:
        scores[player.name] = player.pairs
        player = next(players)
    for i in sorted(scores):
        bot.say('{}: {}'.format(i, scores[i]))
