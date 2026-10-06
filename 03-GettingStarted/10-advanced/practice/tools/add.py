from .schema import AddInputModel


async def add_handler(input_model: AddInputModel) -> float:
    """Add two validated numbers."""
    return input_model.a + input_model.b


tool_add = {
    "name": "add",
    "description": "Add two numbers",
    "input_model": AddInputModel,
    "handler": add_handler
}