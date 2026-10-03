import re
from os.path import isfile, join
from typing import cast
from fastapi.responses import HTMLResponse



class dotdict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__

render_config = dotdict({
    "static_path": "",
    "template_path": "",
})
# for intellisense:
cast(str, render_config.static_path)
cast(str, render_config.template_path)


def space_remove(text: str) -> str:
    while "  " in text:
        text = text.replace("  ", " ")
    return text


def render_tag(tag: str) -> str:
    if tag.startswith("static"):
        filepath = tag.split(" ", maxsplit=1)[-1].strip()
        with open(join(render_config.static_path, filepath), "r", encoding="utf-8") as f:
            file = f.read()
        if tag.startswith("static_script"):
            return f"<script>{file}</script>"
        if tag.startswith("static_style"):
            return f"<style>{file}</style>"
        else:
            return file
    return ""

def render_to_str(template: str, context: dict | None = None) -> str:
    if context is None:
        context = {}

    def tag(match) -> str:
        command = match.group(1).strip()
        return render_tag(command)

    template = re.sub(r"\{%(.*?)%}", tag, template, flags=re.DOTALL)

    def var(match) -> str:
        var = match.group(1).strip()
        return context.get(var, "")

    template = re.sub(r"\{\{(.*?)}}", var, template, flags=re.DOTALL)

    return template

def render(filepath: str, context: dict | None = None) -> HTMLResponse:
    if not isfile(join(render_config.template_path, filepath)):
        raise FileNotFoundError(f"File {filepath} not found")

    with open(join(render_config.template_path, filepath), "r", encoding="utf-8") as f:
        template = f.read()

    return HTMLResponse(render_to_str(template, context))
