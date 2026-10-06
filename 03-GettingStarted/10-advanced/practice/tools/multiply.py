from .schema import AddInputModel


async def multiply_handler(input_model: AddInputModel) -> float:
    """Multiply two validated numbers."""
    return input_model.a * input_model.b


tool_multiply = {
    "name": "multiply",
    "description": "Multiply two numbers",
    "input_model": AddInputModel,
    "handler": multiply_handler
}