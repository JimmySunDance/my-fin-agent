def load_prompt(file_path:str) ->str:
    with open(file_path, 'r') as f:
        sys_p = f.read()
    f.close()
    return sys_p