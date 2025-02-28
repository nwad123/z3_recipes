import z3
import itertools as it


class MacroTriple:
    """
    Represents a food item with its macro-nutrient composition.

    Attributes:
        name (str): The name of the food item.
        fat (float): The fat content per gram.
        carbs (float): The carbohydrate content per gram.
        protien (float): The protein content per gram.
    """

    def __init__(
        self,
        name: str,
        fat: float,
        carbs: float,
        protien: float,
        gramsPerServing: float,
    ):
        self.name = name
        self.fat = fat / gramsPerServing
        self.carbs = carbs / gramsPerServing
        self.protien = protien / gramsPerServing

    def __iter__(self):
        fat, carbs, protien, coefficient = self.with_coef()
        yield fat
        yield carbs
        yield protien
        yield coefficient

    def with_coef(self):
        """
        Returns the macro-nutrient composition and a coefficient for the food item.

        Returns:
            tuple: A tuple containing the fat, carbs, protein content per gram, and a Z3 Real coefficient.
        """

        coefficient = z3.Real(f"K_{self.name}")

        return self.fat, self.carbs, self.protien, coefficient


def recipeFormula(
    ingredients: list[MacroTriple],
    target: MacroTriple,
    *,
    min_bound: float = 1.0,
    max_bound: float = 8.0,
) -> z3.Solver:
    """
    Generates a Z3 solver with constraints based on the given ingredients and target.

    Args:
        ingredients: A list of MacroTriple objects representing the ingredients.
        target: A MacroTriple object representing the target macro-nutrient composition.
        min_bound: The minimum value for the coefficient of each ingredient. Must
            be greater than 0.
        max_bound: The maximum value for the coefficient of each ingredient. Must be
            greater than `min_bound`.

    Returns:
        A Z3 solver with the added recipe constraints.
    """

    s = z3.Solver()

    # Initialize equations with the first ingredient
    fat, carbs, protien, coefficient = ingredients[0]

    # Add bounds for the initial coefficient
    s.add(coefficient > min_bound)
    s.add(coefficient < max_bound)

    # Initialize equations for fat, carbs, and protein
    f_eq = coefficient * fat
    c_eq = coefficient * carbs
    p_eq = coefficient * protien

    # Iterate through the rest of the ingredients
    for fat, carbs, protien, coefficient in ingredients[1::]:
        s.add(coefficient > min_bound)
        s.add(coefficient < max_bound)
        # Accumulate the equations
        f_eq += coefficient * fat
        c_eq += coefficient * carbs
        p_eq += coefficient * protien

    # Add the constraint that each ingredient must be greater than
    # or equal to the next as specified by the FDA
    for (_, _, _, coef1), (_, _, _, coef2) in it.pairwise(ingredients):
        s.add(coef1 >= coef2)

    # Add the target constraints
    s.add(f_eq == target.fat)
    s.add(c_eq == target.carbs)
    s.add(p_eq == target.protien)

    return s


def getMultipleRecipeModels(solver, max_models=10):
    """
    Generates multiple recipes (satisfying assignments) for a given Z3 solver.
    Each model is refined from the previous set of generated models.

    Args:
        solver: The Z3 solver with the constraints added.
        max_models: The maximum number of models to generate.

    Returns:
        A list of Z3 models.
    """
    models = []
    count = 0
    while solver.check() == z3.sat and count < max_models:
        model = solver.model()
        models.append(model)

        # Create a new constraint that excludes the current model
        block = []
        for d in model.decls():
            # Create a constraint that is the negation of the current model
            block.append(d() != model[d])
        solver.add(z3.Or(*block))
        count += 1

    if len(models) == 0:
        print("No recipes found.")

    return models


if __name__ == "__main__":
    # List of ingredients for protay bites
    Ingredients = [
        MacroTriple("Pb", 46.9, 25.0, 21.9, 100),
        MacroTriple("Honey", 0, 82.4, 0.3, 100),
        MacroTriple("Oats", 5.9, 68.7, 13.5, 100),
        MacroTriple("Protien", 0, 8, 20, 34),
        MacroTriple("ChocChips", 29.2, 66.7, 4.2, 100),
    ]

    # Target macros for protay bites
    Target = MacroTriple("Bites", 5, 11, 4, 1)

    # Set of formulas to check for protay bites
    formula = recipeFormula(Ingredients, Target, min_bound=2, max_bound=9)

    # Get all the models within some max_models limit
    all_models = getMultipleRecipeModels(formula, max_models=3)
    z3.set_option(rational_to_decimal=True, precision=3)

    # Print out each model
    for i, model in enumerate(all_models):
        print(f"\nRecipe {i+1}:")
        print(model)
