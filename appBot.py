## Python standard libs

## Third party libs
from ollama import chat
from pydantic import BaseModel

## Project modules
from tool_builder import Tool
from tools import *
from utils import *


class ToolChoice(BaseModel):
    tool_names: list[str]


SYSTEM_PROMPT = load_prompt('prompts/system_prompt.txt')
TOOL_SELECT_PROMPT = load_prompt('prompts/tool_select_prompt.txt')

LLM_MODEL = "qwen2.5:14b"


def get_tool_info() -> tuple[str, list[str]]:
    """
    This function gathers available 'AI Tools' (type Tool) and formats the into
    a descriptive string to be passed into the LLM system prompt.
    """

    tools = [t.name for t in globals().values() if type(t) == Tool]
    tool_con = ""
    if len(tools):
        for t in tools:
            des = globals()[t].description
            tool_con += "".join(f"Tool name: '{t}'\nDescription: {des}\n\n")
        return tool_con, tools
    else:
        return "No tools available", []
    

def ai_extraction(
        system_prompt:str, 
        user_prompt:str, 
        output_struct, 
        ai_model:str=LLM_MODEL
    ):
    """
    This function extracts the specified items form a user prompt. 
    """
    message = [
        {"role":"system", "content":system_prompt}, 
        {"role":"user", "content":user_prompt}
    ]

    response = chat(
        model=ai_model,
        messages=message, 
        format=output_struct.model_json_schema()
    )
    response = output_struct.model_validate_json(response.message.content)
    return response


def execute_tool(tool_name:str, args:dict) -> str:
    """
    This function executes the specified tool with the provided arguments and 
    returns any additional context for the master llm response.
    """
    print(f"... Executing {tool_name}")
    if len(dict(args)):
        response = globals()[tool_name](**args.__dict__)
    else:
        response = globals()[tool_name]()
    return response


def tool_use_loop(tool_list, user_prompt:str, real_tools:list[str]) -> str:
    """
    Execute the tools identified by the LLM as necessary to build enough 
    context to answer the question
    """
    
    tool_context = ""
    if len(tool_list.tool_names) > 0:
        print(f"- Tools found: {tool_list.tool_names}")

        for tool in tool_list.tool_names:
            if tool not in real_tools:
                pass
            
            print(f"-- Using: {tool}")

            if len(globals()[tool].arguments):
                args = globals()[tool].arguments
                sys_p = f"Extract the following arguments form the user prompt:\n{''.join(f'{arg[0]}: {arg[1]}\n' for arg in args)}"

                # Extract arguments for tool use
                values = ai_extraction(
                    system_prompt = sys_p,
                    user_prompt = user_prompt,
                    output_struct = msd[globals()[tool]]
                )

                response = str(execute_tool(tool, values))
            else:
                response = str(execute_tool(tool, {}))
            
            tool_context += response
    else:
        return "There is no tool designed to answer this question"    
    return tool_context


def chat_with_ai(
        user_prompt:str, 
        tool_context:str, 
        ai_model:str=LLM_MODEL
    ) -> str:

    messages=[
        {"role": "system", "content": SYSTEM_PROMPT.format(tool_context[0])},
        {"role": "user", "content":user_prompt},
    ]

    response = chat(model=ai_model, messages=messages)
    return response.message.content


def main() -> None:
    tools_=get_tool_info()

    user_input = input("Welcome to JamesBot! How can I help?\n")

    while user_input.lower() != 'q':
        ## Identify tools required to answer
        tools = ai_extraction(
            system_prompt=TOOL_SELECT_PROMPT.format(tools_),
            user_prompt=user_input, 
            output_struct=ToolChoice
        )

        ## Execute tools to develop context
        tools_context = tool_use_loop(
            tool_list=tools, 
            user_prompt=user_input, 
            real_tools=tools_[1]
        )

        # Answer user question
        answer = chat_with_ai(
            user_prompt=user_input,
            tool_context=tools_context
        )

        print("\n---\n")
        print("Response:\n", answer)

        user_input = input("\n--- --- ---\nAnything else?\nOr 'q' to quit\n")
    return 

if __name__ == "__main__":
    main()