# Linux Bot - Beta

Linux Bot is a virtual assistant for Linux powered by ChatGPT.

## Installation

Make sure to install all the necessary components by running:

```bash
pip install -r requirements.txt
```

Additionally, you'll need to provide your OpenAI API key:

```bash
export OPENAI_API_KEY="YOUR_API_KEY"
```

## Usage

To start using Linux Bot, run the following command:

```bash
python main.py
```

## Abilities

Linux Bot still in beta but it comes with the following abilities for testing:

- Awareness of the current working directory.
- Awareness of the current date and time.
- Capability to list files in any specified path.
- Ability to read files and analyze their content.
- Ability to get file type and size.
- Awareness of the installed package managers.
- Ability to check if a package is installed or not.
- Ability to install packages using a package manager.
- Ability to execute general shell commands and analyze their output and errors.
- Awareness of the environment variables.
- Connected disks and partitions, their information and usage.
- System CPU and Memory usage.

### Define Ability

> An ability is a function that takes arguments and returns a string.

1. Decorate The Ability Function

   - Use the `@assistant.use` decorator to define an ability.
   - The `assistant` here is the instance of the `Assistant` class you want to
     add the ability to.

2. Add Argument Descriptions

   - Add a description to the decorator for each argument describing
     the purpose of the argument.

3. Provide Type Annotations

   - Type annotations are required for each argument as it helps the system to
     understand the type of the argument.

4. Write a DocString

   - Add a DocString for the ability function to describe why the assistant
     should use this ability.

5. Return a String

   - Make sure your ability function returns a string, which contains
     the described output.

Here's an example for the `get_files_list` ability:

```python
import os
from assistant import Assistant


# Create a new assistant instance with some instructions
assistant = Assistant("You are a helpful assistant")


@assistant.use(path="the path where you want to list the files")
def get_files_list(path: str) -> str:
    """Get a list of files in the specified path"""
    files = os.listdir(os.path.expanduser(path))
    return ", ".join(files)
```

1. Import necessary modules
   The `assistant` module is required for the `Assistant` class.
   Which is used to create a new assistant instance.
2. Create a new assistant instance with some instructions
   The assistant needs some instructions to describe its behavior.
3. Define an ability function
   - Use the `@assistant.use` decorator
   - Add a description in the decorator for each argument
   - Add type annotations for each argument
   - Add a DocString for the ability function
   - Return a string which contains the described output of the function

You can catch exceptions in the following way:

```python
try:
    files = os.listdir(os.path.expanduser(path))
    return ", ".join(files)
except Exception as err:
    return f"Error: failed to get the files list: {err}"
```

## Assistant Abilities In Deep

> **AssistantAbility** is the object that contains the definition of an ability.

```python
from assistant import AssistantAbility


def get_files_list(path: str) -> str:
   ...

ability = AssistantAbility(
   name="get_files_list",
   description="Get a list of files in the specified path",
   action=get_files_list
)
ability.add_argument(
   "path",
   type=string,
   description="The path where you want to list the files",
   is_required=True,
)
```

then you can assign the ability to an assistant instance:

```python
assistant_instance.add_ability(ability)
```

To ease the process you can use `AssistantAbility.generate_from_function`
but you need to do some modifications.

1. Move the ability description to the function itself as a docstring.
2. Add type annotations to the argument and a description inside the decorator.
3. Required arguments are arguments that do not have a default value.

After modifications:

```python
from assistant import AssistantAbility


def get_files_list(path: str) -> str:
   """Get a list of files in the specified path"""
   ...


ability = AssistantAbility.generate_from_function(
   path="The path where you want to list the files"
)(func)
```

Now it is much easier to define an ability but you could also use
`Assistant.ability` function decorator to generate the ability object and
**inject it into the function itself**.

```python
from assistant import Assistant


@Assistant.ability(path="The path where you want to list the files")
def get_files_list(path: str) -> str:
   """Get a list of files in the specified path"""
   ...
```

- To check if the function or any object has an ability object injected inside
  use the `Assistant.has_injected_ability` function

- To get the injected ability object use the `Assistant.get_injected_ability`
  function, if the object does not have an ability object injected inside use
  it will raise **ValueError**

> Note: `assistant.add_ability` can detect and use the injected ability object
> So you don't need to do any extra work

```python
@Assistant.ability(path="The path where you want to list the files")
def get_files_list(path: str) -> str:
   """Get a list of files in the specified path"""
   ...

assistant_instance.add_ability(get_files_list)
```

### Load Abilities From Modules

Now let's clean up our code and move the abilities to another file and just
import the ability objects or the functions itself into our main file.

Let's say you defined many ability objects in file called `abilities.py`
instead of loading them one by one you can load all of them at once:

```python
assistant_instance.import_abilities_module("abilities")
```

### Quick Notes

`assistant.use` uses `Assistant.ability` under the hood to generate
**AssistantAbility** and inject it into the function then uses
`assistant.add_ability` to load it.

`Assistant.ability` uses `AssistantAbility.generate_from_function` under
the hood to generate **AssistantAbility** to generate ability object.

`assistant.import_abilities_module` loads all functions from the module then
loads all functions with ability object injected into it at once, means that
any python code in `abilities.py` like in example will be executed.
