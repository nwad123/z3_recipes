import z3

def refinement(solver: z3.Solver, max_models: int = 10) -> list[z3.ModelRef] | None:
    models = []
    count = 0
    while solver.check() == z3.sat and count < max_models:
        # capture the satisfying assignments
        model = solver.model()
        models.append(model)

        # Create a new constraint that excludes the current 
        # satisfying assignments
        block = []
        for d in model.decls():
            # append a conditions saying that 
            # `var` != `previous satisfying assignment of var`
            block.append(d() != model[d])

        # Add these constraints back into the entire model
        solver.add(z3.Or(*block))
        count += 1

    if len(models) == 0:
        print("No satisfying assignments found.")
        return None

    return models