import constants as c
import structures as st
import tkinter as tk

def set_text_value(widget: tk.Text, value: str):
    widget.config(state="normal")

    widget.delete("1.0", tk.END)
    widget.insert("1.0", value)

    widget.config(state="disabled")

def clear_text_value(widget: tk.Text):
    widget.config(state="normal")
    widget.delete("1.0", tk.END)
    widget.config(state="disabled")

def append_text(widget: tk.Text, text: str):
    widget.config(state="normal")
    widget.insert("insert", text)
    widget.config(state="disabled")

def apply_style_to_text(widget: tk.Text, start_index: str, end_index: str, tag_name: str):
    widget.tag_add(tag_name, start_index, end_index)

def append_text_with_style(widget: tk.Text, text: str, style_tags: [str]):
    start_index = widget.index(tk.INSERT)
    append_text(widget, text)
    end_index = widget.index("insert")

    for tag in style_tags:
        apply_style_to_text(widget, start_index, end_index, tag)

def setup_tags_styles(widget: tk.Text):
    widget.tag_configure(st.TextStyleTag.FULL_MATCH.name, background="#8cf2a2")
    widget.tag_configure(st.TextStyleTag.PARTIAL_MATCH.name, background="#f2e18c")

    widget.tag_configure(st.TextStyleTag.INSUFFICIENT_SKILL.name, foreground="#b51712")
    widget.tag_configure(st.TextStyleTag.INSUFFICIENT_INGREDIENTS.name, foreground="#b51712")
    widget.tag_configure(st.TextStyleTag.INSUFFICIENT_TIME.name, foreground="#b51712")

    widget.tag_configure(st.TextStyleTag.DELIMITER.name, background="#0e5ab2")


def sufficient_skill(needed, actual) -> bool:
    return actual >= needed

def extract_ingredients(row) -> [str]:
    return tuple(row[c.DATA_COL_INGREDIENTS].split(", "))

def extract_skill(row) -> st.CookingSkill:
    return st.CookingSkill.from_str(row[c.DATA_COL_SKILL])

def extract_meal(row) -> st.Meal:
    return st.Meal.from_str(row[c.DATA_COL_MEAL])

def extract_time(row) -> int:
    return int(row[c.DATA_COL_COOKING_TIME])

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