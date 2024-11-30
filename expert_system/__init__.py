import pandas as pd
import tkinter as tk
from tkinter import ttk

from constants import FONT, COOKING_TIME_OPTIONS, COOKING_SKILL_OPTIONS, MEAL_OPTIONS
import structures as st

DATA = pd.read_csv("../data/es/dishes.csv")

def set_text_value(widget: tk.Text, value: str) -> None:
    widget.config(state="normal")

    widget.delete("1.0", tk.END)
    widget.insert(tk.END, value)

    widget.config(state="disabled")

def suggest_the_dishes(form: st.InputForm):
    pass

# UI
def create_input_frame(container, form: st.InputForm):
    frame = ttk.Frame(container)

    # розміщення елементів вводу в grid
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(0, weight=2)

    # Введення наявних продуктів
    ttk.Label(frame, text="Продукти в наявності *", font=FONT).grid(column=0, row=0, sticky=tk.W)
    form.ingredients = tk.Text(frame, height=3, width=30, font=FONT, wrap="word")  # Wrap text by word
    form.ingredients.grid(column=1, row=0, sticky=tk.EW)
    form.ingredients.focus()

    ttk.Label(frame, text="Вміння кулінарії *", font=FONT).grid(column=0, row=1, sticky=tk.W)
    form.cooking_skills = tk.StringVar()
    complexity_dropdown = ttk.Combobox(frame, values=COOKING_SKILL_OPTIONS, textvariable=form.cooking_skills, font=FONT, state="readonly")
    complexity_dropdown.grid(column=1, row=2, sticky=tk.EW)
    form.cooking_skills.set(COOKING_SKILL_OPTIONS[0])

    ttk.Label(frame, text="Прийом їжі *", font=FONT).grid(column=0, row=2, sticky=tk.W)
    form.meal = tk.StringVar()
    meal_dropdown = ttk.Combobox(frame, values=MEAL_OPTIONS, textvariable=form.meal, font=FONT, state="readonly")
    meal_dropdown.grid(column=1, row=3, sticky=tk.EW)
    form.meal.set(MEAL_OPTIONS[0])

    # Вибір часу, який готові витратити на приготування
    ttk.Label(frame, text="Час на приготування", font=FONT).grid(column=0, row=3, sticky=tk.W)
    form.cooking_time = tk.StringVar()
    cooking_time_dropdown = ttk.Combobox(frame, values=COOKING_TIME_OPTIONS, textvariable=form.cooking_time, font=FONT, state="readonly")
    cooking_time_dropdown.grid(column=1, row=1, sticky=tk.EW)
    form.cooking_time.set(COOKING_TIME_OPTIONS[0])

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

    form.suggestions_field = tk.Text(window, font=("Arial", 14), wrap="word", state="disabled")
    form.suggestions_field.grid(column=0, row=2, sticky=tk.EW, pady=10, padx=5)

    search_button = tk.Button(window, text="Пошук", font=FONT, background="lightgreen", command=lambda: suggest_the_dishes(form))
    search_button.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

    window.mainloop()

def main():
    init_main_window()

if __name__ == "__main__":
    main()
