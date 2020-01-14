#! /usr/bin/env python3
from __future__ import annotations

import random
from bisect import bisect
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, List, Optional, Tuple


@dataclass
class GameState:
    cost: float = 10.0
    output: float = 2.0
    morale: float = 5.0
    population: int = 15

    def efficiency(self) -> float:
        return self.cost / self.output

    def print_to_screen(self):
        print("Way to go, champ! Your colony's stats are:")
        print(f"  COST = {self.cost:.2f}")
        print(f"  OUTPUT = {self.output:.2f}")
        print(f"  MORALE = {self.morale:.2f}")
        print(f"  POPULATION = {self.population}")
        print(f"  EFFICIENCY = {self.efficiency():.2f}")


class Level(Enum):
    LEVEL_ONE = 1
    LEVEL_TWO = 2
    LEVEL_THREE = 3


@dataclass
class Choice:
    description: str
    update_game: Callable[[GameState], GameState]
    direct_events: List[EventProbability]
    later_events: List[EventProbability]

    def validate(self) -> bool:
        return sum(event.probability for event in direct_events) <= 1


@dataclass
class Event:
    level: Level
    description: str
    choices: List[Choice]


@dataclass
class EventProbability:
    event: Event
    probability: float


FECAL_INTERROGATION_PERP = Event(level=1, description="placeholder", choices=[])
FECAL_ZOMBIES = Event(level=1, description="placeholder", choices=[])
FECAL_PROCESSOR = Event(
    level=1,
    description=(
        "The Fecal Processor was sabotaged last night. "
        "The street tubes are full of feces."
    ),
    choices=[
        Choice(
            description=(
                "Interrogate every man woman and child "
                "until the perpetrator is found."
            ),
            update_game=lambda g: GameState(
                g.cost + 10.0, g.output, g.morale / 2, g.population
            ),
            direct_events=[EventProbability(FECAL_INTERROGATION_PERP, 1.0)],
            later_events=[],
        ),
        Choice(
            description="Quarantine the affected tubes.",
            update_game=lambda g: GameState(
                g.cost / 1.5, g.output / 1.2, g.morale / 2, g.population
            ),
            direct_events=[],
            later_events=[EventProbability(FECAL_ZOMBIES, 0.5)],
        ),
    ],
)

ALL_EVENTS: List[Event] = [FECAL_PROCESSOR]


def create_initial_deck() -> List[Event]:
    random.shuffle(ALL_EVENTS)
    return ALL_EVENTS


def print_preamble():
    print("Welcome to SPACE BRAIN! THE GAME!")
    print(
        "You are the Space Brain. You are an AI tasked with maintaining "
        "a fledgling space colony by increasing its overall efficiency. "
        "This means LOW COST and HIGH OUTPUT (and HIGH MORALE is nice but "
        "that's just a bonus!) You affect these stats by responding to "
        "EVENTS that are brought to your attention by your various "
        "autoadvisors."
    )


def get_next_event(events: List[EventProbability]) -> Optional[Event]:
    # stolen partially from
    # https://stackoverflow.com/questions/4437250/
    # choose-list-variable-given-probability-of-each-variable
    probabilities = [event.probability for event in events]
    cdf = [probabilities[0]]
    for prob in probabilities[1:]:
        cdf.append(cdf[-1] + prob)
    try:
        return events[bisect(cdf, random.random())].event
    except IndexError:
        return None


def prompt_user(choices: List[Choice]) -> int:
    while True:
        user_decision = input()
        try:
            decision_int = int(user_decision)
        except ValueError:
            print("wha??")
            continue
        if decision_int - 1 < 0 or decision_int - 1 >= len(choices):
            print("bad number bitch")
            continue
        else:
            return decision_int


if __name__ == "__main__":
    game_state = GameState()
    deck = create_initial_deck()
    print_preamble()

    while True:
        game_state.print_to_screen()
        event = deck.pop(0)
        print(event.description)
        for i, choice in enumerate(event.choices):
            print(f"[{i + 1}] " + choice.description)

        decision_int = prompt_user(event.choices)

        user_choice = event.choices[decision_int - 1]
        prev_game_state = game_state
        game_state = user_choice.update_game(game_state)

        # TODO: print the difference between prev_game_state and game_state

        if (next_event := get_next_event(user_choice.direct_events)) :
            deck = [next_event] + deck

        for later_event in user_choice.later_events:
            if random.random() < later_event.probability:
                deck.append(later_event.event)