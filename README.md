# Z3 Recipes: Optimal Macro-Nutrient Recipe Generation

This Python script uses the Z3 theorem prover to generate recipes that meet specified macro-nutrient targets, utilizing nutritional information from ingredients.

## Setup

1. Create virtual environment: `python3 -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
2. Install Z3: `pip install z3-solver`
3. Run: `python recipes.py`

The script outputs recipe combinations satisfying the target macronutrient profile. Modify Ingredients and Target in recipes.py to adjust recipes and targets.
`max_models` controls the number of solutions generated.
