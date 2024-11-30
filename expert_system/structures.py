from enum import Enum
import tkinter as tk
from tkinter import ttk

class ExtendedEnum(Enum):
    @classmethod
    def values(cls):
        return tuple(map(lambda x: x.value, cls))

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
    FAST = "< 30хв"
    MEDIUM = "30хв - 1год"
    MEDIUM_LONG = "1-2 год"
    LONG = "2+ години"

class Meal(ExtendedEnum):
    UNIMPORTANT = "Не важливо"
    BREAKFAST = "Сніданок"
    DINNER = "Обід"
    SUPPER = "Вечеря"

class CookingSkill(ExtendedEnum):
    BEGINNER = "Початківець"
    INTERMEDIATE = "Любитель"
    ADVANCED = "Просунутий"
    CHEF = "Шеф"

class InputForm:
    def __init__(self):
        self.ingredients: tk.Text = tk.Text()
        self.cooking_skills: tk.StringVar = tk.StringVar()
        self.meal: ttk.Combobox = ttk.Combobox()
        self.cooking_time: tk.StringVar = tk.StringVar()
        self.suggestions_field: tk.Text = tk.Text()
