import re
from dataclasses import dataclass


skill_pattern = re.compile(r"(\w+)\((`[^`]+`(?:, `[^`]+`)*)?\)")
argument_pattern = re.compile(r"`([^`]+)`")


class SkillManager:

    def __init__(self):
        self.skills = {}

    def register_skill(self, name: str, handler: callable):
        self.skills[name] = handler

    def execute_command(self, command):
        return self.skills[command.name](*command.arguments)

    def parse_skill_commands(self, message: str):
        return [self.parse_skill_match(match) for match in skill_pattern.finditer(message)]
            
    def parse_skill_match(self, skill_match):
        skill_name = skill_match.group(1)
        arguments_str = skill_match.group(2)

        if arguments_str:
            arguments = [match.group(1) for match in argument_pattern.finditer(arguments_str)]
        else:
            arguments = []
        
        return Command(
            name=skill_name,
            arguments=arguments,
        )

@dataclass
class Command:

    name: str
    arguments: list[str]

    def to_dict(self):
        return {
            "name": self.name,
            "arguments": self.arguments,
        }
