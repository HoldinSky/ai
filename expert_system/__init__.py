import pandas as pd
import tkinter as tk
from tkinter import ttk

import constants as c
import structures as st
from expert_system.utils import set_text_value
from utils import (sufficient_skill, extract_ingredients, extract_skill, extract_meal, extract_time, dish_from_row)

DATA = pd.read_csv("../data/es/dishes.csv")


def match_ingredients(stock, needed) -> (float, [str]):
    count_needed = len(needed)
    count_matched = 0
    absent = []

    for ingredient in needed:
        matched = False
        if ingredient in stock:
            count_matched += 1
            continue
        else:
            # для випадків, коли вписаний продукт не знайдено 1-1 в базі, бо там зберігається довша строка (з кількістю тощо)
            for stocked in stock:
                if stocked in ingredient:
                    count_matched += 1
                    matched = True
                    break
        if not matched:
            absent.append(ingredient)

    return count_matched / count_needed if len(absent) > 0 else 999, absent

def time_overhead(provided: st.CookingTime, needed: int) -> float:
    if provided == st.CookingTime.UNIMPORTANT:
        return -1
    return needed / provided.to_seconds()

def match_recipes(
        products_in_stock,
        skill: st.CookingSkill,
        time: st.CookingTime,
        meal: st.Meal
) -> ([st.FullMatch], [st.PartialMatch]):
    full_matches, partial_matches = [], []

    for index, row in DATA.iterrows():
        full_match, partial_match = None, None
        if not sufficient_skill(extract_skill(row), skill):
            continue
        if meal != st.Meal.UNIMPORTANT and extract_meal(row) != meal:
            continue

        match_percentage, absent = match_ingredients(products_in_stock, extract_ingredients(row))
        time_coefficient = time_overhead(time, extract_time(row))

        if time_coefficient > 1:
            if time_coefficient > c.MAXIMUM_TIME_OVERHEAD:
                continue
            partial_match = st.PartialMatch(dish_from_row(row))
            partial_match.insufficient_time()

        if 1.0 > match_percentage:
            if match_percentage > c.MINIMUM_INGREDIENTS_MATCH:
                continue
            if partial_match is None:
                partial_match = st.PartialMatch(dish_from_row(row))
            partial_match.insufficient_ingredients(absent)

        if partial_match is not None:
            partial_matches.append(partial_match)
        else:
            full_matches.append(st.FullMatch(dish_from_row(row)))

    return full_matches, partial_matches


def compose_suggestion(full_matches: [st.FullMatch], partial_matches: [st.PartialMatch]) -> str:
    suggestion_parts: [str] = []
    if len(full_matches) > 0:
        suggestion_parts.append("=== Приготуйте просто зараз ===\n")
        for m in full_matches:
            suggestion_parts.append(f"{m.dish}\n\n")

    if len(partial_matches) > 0:
        suggestion_parts.append("=== Можливо приготувати ===\n")
        for m in partial_matches:
            suggestion_parts.append(f"{m.dish}\n")

            if st.PartialMatchReason.NOT_ENOUGH_TIME in m.reasons:
                suggestion_parts.append("- ! Недостатньо часу\n")
            if st.PartialMatchReason.NOT_ENOUGH_INGREDIENTS in m.reasons:
                suggestion_parts.append(f"- ! Не вистачає інгредієнтів: {", ".join(m.absent_ingredients)}\n")
            suggestion_parts.append("\n")

    return "".join(suggestion_parts)

def suggest_the_dishes(form: st.InputForm):
    products_in_stock = form.ingredients.get("1.0", tk.END).strip().split(", ")
    skill = st.CookingSkill.from_str(form.cooking_skills.get())
    time = st.CookingTime.from_str(form.cooking_time.get())
    meal = st.Meal.from_str(form.meal.get())

    full_matches, partial_matches = match_recipes(products_in_stock, skill, time, meal)
    suggestion = compose_suggestion(full_matches, partial_matches)

    set_text_value(form.suggestions_field, suggestion)

# UI
def create_input_frame(container, form: st.InputForm):
    frame = ttk.Frame(container)

    # розміщення елементів вводу в grid
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(0, weight=2)

    # Введення наявних продуктів
    ttk.Label(frame, text="Продукти в наявності *", font=c.FONT).grid(column=0, row=0, sticky=tk.W)
    form.ingredients = tk.Text(frame, height=3, width=30, font=c.FONT, wrap="word")  # Wrap text by word
    form.ingredients.grid(column=1, row=0, sticky=tk.EW)

    ttk.Label(frame, text="Вміння кулінарії *", font=c.FONT).grid(column=0, row=1, sticky=tk.W)
    form.cooking_skills = tk.StringVar()
    skills_dropdown = ttk.Combobox(frame, values=c.COOKING_SKILL_OPTIONS, textvariable=form.cooking_skills, font=c.FONT,
                                   state="readonly")
    skills_dropdown.grid(column=1, row=1, sticky=tk.EW)
    form.cooking_skills.set(c.COOKING_SKILL_OPTIONS[0])

    ttk.Label(frame, text="Прийом їжі *", font=c.FONT).grid(column=0, row=2, sticky=tk.W)
    form.meal = tk.StringVar()
    meal_dropdown = ttk.Combobox(frame, values=c.MEAL_OPTIONS, textvariable=form.meal, font=c.FONT, state="readonly")
    meal_dropdown.grid(column=1, row=2, sticky=tk.EW)
    form.meal.set(c.MEAL_OPTIONS[0])

    # Вибір часу, який готові витратити на приготування
    ttk.Label(frame, text="Час на приготування", font=c.FONT).grid(column=0, row=3, sticky=tk.W)
    form.cooking_time = tk.StringVar()
    cooking_time_dropdown = ttk.Combobox(frame, values=c.COOKING_TIME_OPTIONS, textvariable=form.cooking_time,
                                         font=c.FONT, state="readonly")
    cooking_time_dropdown.grid(column=1, row=3, sticky=tk.EW)
    form.cooking_time.set(c.COOKING_TIME_OPTIONS[0])

    for widget in frame.winfo_children():
        widget.grid(padx=5, pady=5)

    return frame

def init_main_window():
    window = tk.Tk()
    form = st.InputForm()

    window.title("Що приготувати?")
    window.minsize(650, 400)
    window.resizable(width=False, height=False)

    input_frame = create_input_frame(window, form)
    input_frame.grid(column=0, row=0, sticky=tk.EW)

    # Bind paste event
    def paste(event=None):
        try:
            clipboard_content = window.clipboard_get()
            form.ingredients.insert(tk.INSERT, clipboard_content)
        except tk.TclError:
            print("No content in clipboard to paste.")

    # Add binding for Ctrl+V or Cmd+V
    form.ingredients.bind("<Control-v>", paste)  # For Windows/Linux
    form.ingredients.bind("<Command-v>", paste)  # For macOS

    form.suggestions_field = tk.Text(window, font=("Arial", 14), wrap="word", state="disabled")
    form.suggestions_field.grid(column=0, row=2, sticky=tk.EW, pady=10, padx=5)

    search_button = tk.Button(window, text="Пошук", font=c.FONT, background="lightgreen", command=lambda: suggest_the_dishes(form))
    search_button.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

    window.mainloop()

def main():
    init_main_window()

if __name__ == "__main__":
    main()
