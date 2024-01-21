import inspect
import importlib
from pathlib import Path
from enum import EnumType
from termcolor import colored
from typing import Callable, Dict, List, Union, cast

from openai import audio, chat
from openai.types.chat.chat_completion_tool_message_param import ChatCompletionToolMessageParam
from openai.types.chat import (ChatCompletion,
                               ChatCompletionMessageParam,
                               ChatCompletionMessageToolCall,
                               ChatCompletionToolParam)

from pydub import AudioSegment
from pydub.playback import play
from pydub.utils import json


class AbilityArgument:
    def __init__(self,
                 name: str, type: str, description: str, is_required: bool,
                 enum: Union[List[str], None] = None):
        self._name = name
        self._type = type
        self._description = description
        self._is_required = is_required
        self._enum = enum

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._type

    @property
    def description(self) -> str:
        return self._description

    @property
    def is_required(self) -> bool:
        return self._is_required

    @property
    def enum(self) -> List[str]:
        return cast(List[str], self._enum)

    @property
    def has_enum(self) -> bool:
        return self._enum is not None

    def generate_object(self):
        obj: Dict[str, object] = {
            "type": self._type,
            "description": self._description,
        }

        if self.has_enum:
            obj["enum"] = self.enum
        return obj


class AssistantAbility:
    def __init__(self, name: str, description: str, action: Callable):
        self._name = name
        self._description = description
        self._action = action
        self._arguments: Dict[str, AbilityArgument] = {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def arguments(self) -> Dict[str, Dict[str, object]]:
        return {
            arg.name: arg.generate_object() for arg in self._arguments.values()
        }

    def is_argument_required(self, name: str) -> bool:
        return self._arguments[name].is_required

    def add_argument(self,
                     name: str,
                     type: str,
                     description: str,
                     is_required: bool,
                     enums: Union[List[str], None] = None):
        self._arguments[name] = AbilityArgument(
            name, type, description, is_required, enums)

    def add_argument_object(self, argument: AbilityArgument):
        self._arguments[argument.name] = argument

    def generate_ability_description(self) -> ChatCompletionToolParam:
        return {
            "type": "function",
            "function": {
                "name": self._name,
                "description": self._description,
                "parameters": self.generate_parameters_description(),
            }
        }

    def generate_parameters_description(self) -> Dict[str, object]:
        args = self._arguments.values()
        return {
            "type": "object",
            "properties": {
                arg.name: arg.generate_object() for arg in args
            },
            "required": [arg.name for arg in args if arg.is_required],
        }

    def __call__(self, *args, **kwargs):
        return self._action(*args, **kwargs)

    @staticmethod
    def generate_from_function(
            **descriptions: str) -> Callable[[Callable], "AssistantAbility"]:
        def wrapper(func: Callable[..., str]) -> AssistantAbility:
            if func.__doc__ is None:
                raise ValueError("Ability function must has docstring")

            ability = AssistantAbility(func.__name__, func.__doc__, func)
            ability_signature = inspect.signature(func)
            params = ability_signature.parameters

            for param in params:
                obj = params[param]

                if obj.name not in descriptions:
                    raise ValueError(
                        f"Missing description for argument: {obj.name}")

                if obj.annotation == inspect.Parameter.empty:
                    raise ValueError(
                        f"Missing type annotation for argument: {obj.name}")

                is_required = obj.default is inspect.Parameter.empty
                enum = None

                if isinstance(obj.annotation, EnumType):
                    enum = list(obj.annotation.__members__.keys())

                ability.add_argument(obj.name,
                                     type_to_text(obj.annotation),
                                     descriptions[obj.name],
                                     is_required,
                                     enum,
                                     )

            return ability
        return wrapper


class Assistant:
    def __init__(self, instructions: str):
        self._instructions = instructions
        self._history: List[ChatCompletionMessageParam] = []
        self._abilities: Dict[str, AssistantAbility] = {}
        self.reset()

    @property
    def instructions(self) -> str:
        return self._instructions

    @property
    def history(self) -> List[ChatCompletionMessageParam]:
        return [*self._history]

    def reset(self):
        self._history = [
            {"role": "system", "content": self.instructions},
        ]

    def generate_audio(self, text: str, path: Path):
        response = audio.speech.create(
            model="tts-1-hd",
            voice="nova",
            input=text,
        )

        response.stream_to_file(path)

    def use_gpt(self,
                messages: List[ChatCompletionMessageParam]) -> ChatCompletion:
        args = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
        }

        if len(self._abilities) > 0:
            args["tools"] = [
                ability.generate_ability_description()
                for ability in self._abilities.values()
            ]
        return chat.completions.create(**args)

    def say(self, text: str):
        audio_file = Path(__file__).parent / "speech.mp3"
        self.generate_audio(text, audio_file)
        sound = AudioSegment.from_mp3(audio_file)

        try:
            play(sound)
        except KeyboardInterrupt:
            print("System: Speech Interrupted!")

    def add_ability(self, ability: Union[AssistantAbility, object]):
        ability = Assistant.get_injected_ability(ability)
        self._abilities[ability.name] = ability
        return ability

    def use(self, **descriptions: str):
        """Generate assistant ability from a function and inject inside
        then add it."""
        def wrapper(func: Callable[..., str]):
            Assistant.ability(**descriptions)(func)
            self.add_ability(func)
            return func
        return wrapper

    @staticmethod
    def ability(**descriptions: str):
        """Generate assistant ability from a function and inject inside"""
        def wrapper(func: Callable[..., str]):
            ability = AssistantAbility.generate_from_function(
                **descriptions)(func)
            setattr(func, "__assistant_ability__", ability)
            return func
        return wrapper

    @staticmethod
    def get_injected_ability(obj: object) -> AssistantAbility:
        """Get the injected AssistantAbility from an object"""
        if not Assistant.has_injected_ability(obj):
            raise ValueError("Object is not an AssistantAbility")
        if isinstance(obj, AssistantAbility):
            return obj
        obj = getattr(obj, "__assistant_ability__")
        return cast(AssistantAbility, obj)

    @staticmethod
    def has_injected_ability(obj: object) -> bool:
        """Check if an object is an AssistantAbility"""
        if isinstance(obj, AssistantAbility):
            return True
        obj = getattr(obj, "__assistant_ability__", None)
        return obj is not None and isinstance(obj, AssistantAbility)

    def import_abilities_module(self, path: str):
        module = importlib.import_module(path)
        members = inspect.getmembers(module)
        abilities = [
            member[1] for member in members
            if Assistant.has_injected_ability(member[1])
        ]
        for ability in abilities:
            self.add_ability(ability)

    def _execute_abilities(self, call: ChatCompletionMessageToolCall):
        ability_call = call.function

        print(
            colored(
                f"Use Ability: {ability_call.name}: {ability_call.arguments}",
                "green"))

        def response(content: str) -> ChatCompletionToolMessageParam:
            return {
                "role": "tool",
                "tool_call_id": call.id,
                "content": content,
            }

        if ability_call.name not in self._abilities:
            return response(
                f"Error: function {ability_call.name} does not exist"
            )

        args = json.loads(ability_call.arguments)
        ability = self._abilities[ability_call.name]
        try:
            results = ability(**args)
        except Exception as e:
            return response(f"Error: {e}")
        return response(results)

    def __call__(self, input: str,
                 with_output: bool = True,
                 assistant_name="Assistant",
                 with_speech: bool = True) -> str:

        self._history.append({"role": "user", "content": input})

        while True:
            response = self.use_gpt(self._history)
            message = response.choices[0].message
            self._history.append(message)

            calls = message.tool_calls
            if calls is not None:
                response = self._execute_abilities(calls[0])
                self._history.append(response)
                continue

            text = cast(str, response.choices[0].message.content)

            if with_output:
                print(f"{assistant_name}: {text}")

            if with_speech:
                self.say(text)

            return text


def type_to_text(obj: object) -> str:
    if obj is str:
        return "string"
    elif obj is float or obj is int:
        return "number"
    elif obj is bool:
        return "boolean"
    elif obj is dict:
        return "object"
    elif issubclass(type(obj), EnumType):
        return "string"
    elif obj is list:
        return "array"
    elif obj is None:
        return "null"
    else:
        raise ValueError(f"Unsupported type: {type(obj)}")
