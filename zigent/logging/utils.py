import re


def format_dict_str(dict_like, keys=None):
    pairs: list[str]
    if keys:
        pairs = [f"{k}: {dict_like[k]}" for k in keys]
    else:
        pairs = [f"{k}: {dict_like[k]}" for k in dict_like]
    return "\n".join(pairs)


def str_color_remove(color_str: str):
    ansi_escape = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")
    clean_str = ansi_escape.sub("", color_str)
    return clean_str
