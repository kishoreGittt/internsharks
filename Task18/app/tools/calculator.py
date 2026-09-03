def calculator(operation: str, a: float, b: float) -> dict:
    """
    Perform basic arithmetic operations.
    """

    operation = operation.lower().strip()

    if operation == "add":
        result = a + b

    elif operation == "subtract":
        result = a - b

    elif operation == "multiply":
        result = a * b

    elif operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero.")

        result = a / b

    else:
        raise ValueError(
            f"Unsupported operation: {operation}"
        )

    return {
        "operation": operation,
        "a": a,
        "b": b,
        "result": result
    }