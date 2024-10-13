from abc import ABC, abstractmethod
from jinja2 import Environment, FileSystemLoader

class PromptRenderer(ABC):
    @abstractmethod
    def render_prompt(self, template_name: str, context: dict) -> str:
        pass

class JinjaPromptRenderer(PromptRenderer):
    def __init__(self, template_folder: str):
        self.env = Environment(loader=FileSystemLoader(template_folder))

    def render_prompt(self, template_name: str, context: dict) -> str:
        template = self.env.get_template(template_name)
        return template.render(context)
