import constants as c
import structures as st
import tkinter as tk

def set_text_value(widget: tk.Text, value: str) -> None:
    widget.config(state="normal")

    widget.delete("1.0", tk.END)
    widget.insert(tk.END, value)

    widget.config(state="disabled")

def sufficient_skill(needed, actual) -> bool:
    return actual >= needed

def extract_ingredients(row) -> [str]:
    return row[c.DATA_COL_INGREDIENTS]

def extract_skill(row) -> st.CookingSkill:
    return st.CookingSkill.from_str(row[c.DATA_COL_SKILL])

def extract_meal(row) -> st.Meal:
    return st.Meal.from_str(row[c.DATA_COL_MEAL])

def extract_time(row) -> int:
    return row[c.DATA_COL_COOKING_TIME]

def extract_name(row) -> str:
    return row[c.DATA_COL_NAME]

def extract_description(row) -> str:
    return row[c.DATA_COL_DESCRIPTION]

def extract_recipe(row) -> str:
    return row[c.DATA_COL_RECIPE]

def dish_from_row(row) -> st.Dish:
    return st.Dish(
        extract_ingredients(row),
        extract_skill(row),
        extract_meal(row),
        extract_time(row),
        extract_name(row),
        extract_description(row),
        extract_recipe(row)
    )