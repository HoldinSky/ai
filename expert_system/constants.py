import structures as st

FONT = ("Arial", 17)

COOKING_TIME_OPTIONS = st.CookingTime.values()
COOKING_SKILL_OPTIONS = st.CookingSkill.values()
MEAL_OPTIONS = st.Meal.values()

DATA_COL_INGREDIENTS = "ingredients"
DATA_COL_SKILL = "cooking_skill"
DATA_COL_MEAL = "best_for(meal)"
DATA_COL_COOKING_TIME = "time_to_cook"
DATA_COL_NAME = "dish_name"
DATA_COL_DESCRIPTION = "dish_description"
DATA_COL_RECIPE = "dish_recipe"

MINIMUM_INGREDIENTS_MATCH = 0.7
MAXIMUM_TIME_OVERHEAD = 1.3