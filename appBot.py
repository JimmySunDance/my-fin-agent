## 
import inspect

import ollama 
from pydantic import BaseModel

class Tool:
    """
    A class representing a reusable piece of code (Tool).

    Attributes:
        name (str): Name of the tool.
        description (str): A textual description of what the tool does.
        func (callable): The function this tool wraps.
        arguments (list): A list of arguments.
        outputs (str or list): The return type(s) of the wrapped function.
    """
    def __init__(self, 
                 name: str, 
                 description: str, 
                 func: callable, 
                 arguments: list, 
                 outputs: str):
        self.name = name
        self.description = description
        self.func = func
        self.arguments = arguments
        self.outputs = outputs

    def to_string(self) -> str:
        """
        Return a string representation of the tool, including its name, 
        description, arguments and outputs.
        """
        args_str = ", ".join(
            f"{arg_name}: {arg_type}" for arg_name, arg_type in self.arguments
        )
        return (
            f"Tool Name: {self.name},\n"
            f"Description: {self.description},\n"
            f"Arguments: {args_str},\n"
            f"Outputs: {self.outputs}\n"
        )


def tool(func):
    """
    A decorator that creates a Tool instance from the given function.
    """

    signature = inspect.signature(func)
    
    name = func.__name__
    description = func.__doc__ or "No description provided."

    arguments = []
    for param in signature.parameters.values():
        annotation_name = (
            param.annotation.__name__
            if hasattr(param.annotation, "__name__")
            else str(param.annotation)
        )
        arguments.append((param.name, annotation_name))

    return_annotation = signature.return_annotation
    if return_annotation is inspect._empty:
        outputs = "No return annotation"
    else:
        outputs = (
            return_annotation.__name__
            if hasattr(return_annotation, "__name__")
            else str(return_annotation)
        )


    return Tool(
        func=func, 
        name=name, 
        description=description, 
        arguments=arguments, 
        outputs=outputs
    )


class ToolChoice(BaseModel):
    tool_name: str


@tool
def calc_multiply(a:float, b:float) -> float:
    """Function returns the multiple of two values"""
    return a*b


system_prompt = """
You are a helpful AI. 
You have the following tools:

Name: "calc_multiply"
Definition: Function returns the multiple of two values
"""

tools = [t for t in globals().values() if type(t) == Tool]
for t in tools:
    print(t.to_string())

response = ollama.chat(
    model="llama3.2:latest",
    messages=[
        {
            "role": "system", 
            "content": system_prompt
        },
        {
            "role": "user", 
            "content": "what is the multiple of 5 and 10?"
        },
    ],
    format=ToolChoice.model_json_schema()
)
response = ToolChoice.model_validate_json(response.message.content)

print(response)