from enum import Enum
import tkinter as tk
from tkinter import ttk

SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = SECONDS_IN_MINUTE * 60


# ENUMS
class ExtendedEnum(Enum):
    @classmethod
    def values(cls):
        return tuple(map(lambda x: x.value, cls))

    @classmethod
    def names(cls):
        return tuple(map(lambda x: x.name, cls))

    @classmethod
    def from_str(cls, value):
        for item in cls:
            if item.value.lower() == value.lower():
                return item
        raise ValueError(f"'{value.name}' is not a valid {cls} value")

    def __gt__(self, other):
        return self.values().index(self.value) > self.values().index(other.value)

    def __ge__(self, other):
        return self.values().index(self.value) >= self.values().index(other.value)

    def __lt__(self, other):
        return self.values().index(self.value) < self.values().index(other.value)

    def __le__(self, other):
        return self.values().index(self.value) <= self.values().index(other.value)


class CookingTime(ExtendedEnum):
    UNIMPORTANT = "Не важливо"
    FAST = "< 20 хвилин"
    MEDIUM = "20 хвилин - 1 година"
    MEDIUM_LONG = "1-2 години"
    LONG = "2+ години"

    def to_seconds(self) -> int:
        if self == CookingTime.FAST:
            return 20 * 60
        elif self == CookingTime.MEDIUM:
            return 1 * SECONDS_IN_HOUR
        elif self == CookingTime.MEDIUM_LONG:
            return 2 * SECONDS_IN_HOUR
        else:
            return 2 * SECONDS_IN_HOUR + 1


class Meal(ExtendedEnum):
    UNIMPORTANT = "Не важливо"
    BREAKFAST = "Сніданок"
    DINNER = "Обід"
    SUPPER = "Вечеря"


class CookingSkill(ExtendedEnum):
    BEGINNER = "Початківець"
    INTERMEDIATE = "Любитель"
    ADVANCED = "Профі"
    CHEF = "Шеф"


class PartialMatchReason(ExtendedEnum):
    INSUFFICIENT_INGREDIENTS = "Не вистачає інгредієнтів"
    INSUFFICIENT_TIME = "Не вистачає часу"
    INSUFFICIENT_SKILL = "Може бути надто складно"

class TextStyleTag(ExtendedEnum):
    INSUFFICIENT_INGREDIENTS = 0
    INSUFFICIENT_TIME = 1
    INSUFFICIENT_SKILL = 2
    FULL_MATCH = 3
    PARTIAL_MATCH = 4
    DELIMITER = 5

    @classmethod
    def from_match_reason(cls, reason: PartialMatchReason):
        for item in cls:
            if item.name == reason.name:
                return item
        raise ValueError(f"'{reason.name}' is not a valid {cls} value")


# STRUCTURES and CLASSES
class InputForm:
    def __init__(self):
        self.ingredients: tk.Text = tk.Text()
        self.cooking_skills: tk.StringVar = tk.StringVar()
        self.meal: ttk.Combobox = ttk.Combobox()
        self.cooking_time: tk.StringVar = tk.StringVar()
        self.suggestions_field: tk.Text = tk.Text()


class Dish:
    def __init__(self,
                 ingredients: [str],
                 skill: CookingSkill,
                 meal: Meal,
                 time_to_cook: int,
                 name: str,
                 description: str,
                 recipe: str):
        self.ingredients = ingredients
        self.skill = skill
        self.meal = meal
        self.time_to_cook = time_to_cook
        self.name = name
        self.description = description
        self.recipe = recipe

    def __str__(self):
        return f"""\"{self.name}\" ({self.meal.value})
{self.description}
Інгредієнти: {", ".join(self.ingredients)}.
Рецепт: {self.recipe}
Час приготування: {(self.time_to_cook / SECONDS_IN_MINUTE):.1f} хвилин
Рівень: {self.skill.value}"""

class FullMatch:
    def __init__(self, dish: Dish):
        self.dish = dish


class PartialMatch:
    def __init__(self, dish: Dish):
        self.reasons: set[PartialMatchReason] = set()

        self.dish = dish
        self.absent_ingredients = []

    def insufficient_ingredients(self, absent_ingredients: [str]):
        self.absent_ingredients = absent_ingredients
        self.reasons.add(PartialMatchReason.INSUFFICIENT_INGREDIENTS)

    def insufficient_time(self):
        self.reasons.add(PartialMatchReason.INSUFFICIENT_TIME)

    def insufficient_skill(self):
        self.reasons.add(PartialMatchReason.INSUFFICIENT_SKILL)