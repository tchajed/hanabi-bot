from __future__ import print_function

# A card is "3B", where the first char is 1-5 and the second char is the color
# (RGBYW)

import random
random.seed(0)

def assert_is_upper(*possibles):
  for s in possibles:
    assert(s.upper() == s)

COLOR_LETTERS = "RGBYW"

def make_deck():
  deck = [n + c for n in "12345" for c in COLOR_LETTERS]
  random.shuffle(deck)
  return deck

NUM_CARDS_IN_HAND = {
  2: 5,
  3: 5,
  4: 4,
  5: 4
}

def is_color(char):
  assert_is_upper(char)
  return char in COLOR_LETTERS

def get_color(card):
  return card[1]

def get_number(card):
  return int(card[0])

class Hints:
  @classmethod
  def empty(cls):
    return cls([], [])

  def __init__(self, known, impossibles):
    self.known = known
    self.impossibles = impossibles

  def add_hint(self, card, hint):
    assert_is_upper(card, hint)
    if hint in card:
      self.known.append(hint)
    else:
      self.impossibles.append(hint)

  def __repr__(self):
    knowns = "".join([str(k) for k in self.known])
    impossibles = "".join([str(i) for i in self.impossibles])
    # TODO: sort knowns into number then color
    # TODO: don't print redundant impossibles
    return "is {}, not {}".format(knowns, impossibles)


class GameState:

  @classmethod
  def start_game(cls, num_players = 3):
    deck = make_deck()
    cards_in_hand = NUM_CARDS_IN_HAND[num_players]
    hands = []
    for i in range(num_players):
      hand = [(d, Hints.empty()) for d in deck[:cards_in_hand]]
      hands.append(hand)
      del deck[:cards_in_hand]

    played = dict([(i, 0) for i in COLOR_LETTERS])
    return GameState(deck, hands, played, [], 0, 8, 0)

  def __init__(self, deck, hands, played, discarded, num_mistakes, num_tokens, current_player):
    self.deck = deck
    self.hands = hands
    self.played = played
    self.discarded = discarded
    self.num_mistakes = num_mistakes
    self.num_tokens = num_tokens
    self.current_player = 0

  def print_state(self, player_index = None):
    if player_index is None:
      player_index = self.current_player
    for other_player in range(self.num_players):
      hand = self.hands[other_player]
      if other_player == player_index:
        print("{} (your) hand".format(other_player))
        for _, hints in hand:
          print(hints)
      else:
        print("{} hand".format(other_player))
        for card, hint in hand:
          print("{} [{}]".format(card, hint))

    print("discarded {}".format(" ".join(self.discarded)))
    played = []
    for color in COLOR_LETTERS:
      played.append("{}{}".format(self.played[color], color))

    print("played {}".format(" ".join(played)))
    print("{} hints left".format(self.num_tokens))
    print("{} mistakes made".format(self.num_mistakes))

  @property
  def current_hand(self):
    return self.hands[self.current_player]

  @property
  def num_players(self):
    return len(self.hands)

  @property
  def hand_size(self):
    return NUM_CARDS_IN_HAND[self.num_players]

  def are_plays_remaining(self):
    return len(self.current_hand) == self.hand_size

  def is_complete(self):
    return (all([v == 5 for v in self.played.values()]) or
            self.num_mistakes >= 3 or
            (len(self.deck) == 0 and
             all([len(h) < self.hand_size for h in self.hands])))


  # game actions

  def hint(self, player_index, hint):
    if player_index == self.current_player:
      assert('TODO - self-hint...')

    if self.num_tokens <= 0:
      assert('TODO - no hint tokens')

    self.num_tokens -= 1
    for c in self.hands[player_index]:
      c[1].add_hint(c[0], hint)

    self.next_player()

  def play(self, card_index):
    if not self.are_plays_remaining():
      assert('TODO - no more plays')

    hand = self.current_hand
    card = hand.pop(card_index)[0]
    self.draw()

    if not self.is_playable(card):
      self.num_mistakes += 1
      self.discarded.append(card)
      self.next_player()
      return

    self.played[get_color(card)] += 1
    self.next_player()

  def discard(self, card_index):
    if not self.are_plays_remaining():
      assert('TODO - no more plays')

    if self.num_tokens >= 8:
      assert('TODO - full hint tokens')

    hand = self.current_hand
    card = hand.pop(card_index)
    self.discarded.append(card[0])
    self.draw()
    self.num_tokens += 1
    self.next_player()

  # internal
  def draw(self):
    hand = self.current_hand
    card = self.deck.pop()
    hand.append((card, Hints.empty()))

  def next_player(self):
    self.current_player = (self.current_player + 1) % self.num_players

  def is_playable(self, card):
    highest_played = self.played[get_color(card)]
    return get_number(card) == highest_played + 1
