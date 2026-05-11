from pydantic import BaseModel

from tool_builder import tool


class Multiplication(BaseModel):
    a: float
    b: float

class Addition(BaseModel):
    a: float
    b: float

@tool
def calc_multiply(a:float, b:float) -> float:
    """Function returns the multiple of two values.
Arguments:
    a: float = the first value
    b: float = the second value
    """
    print(f"{a} x {b} = {a*b}")
    return f"{a} x {b} = {a*b}"

@tool
def calc_addition(a:float, b:float) ->float:
    """Function that returns the addition of two values
Arguments:
    a: float = the first value
    b: float = the second value
    """
    return f"{a} + {b} = {a+b}"

msd = {
    calc_multiply:Multiplication,
    calc_addition:Addition
} 