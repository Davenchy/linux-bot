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

### Define Ability

An ability is a function that takes arguments and returns a string.

- Ability function is decorated using `@assistant.ability` decorator.
  where the **assistant** is the instance of the `Assistant` class you want
  to register this ability to.
- The ability function is required to add a description in the ability decorator for each argument.
- The ability function is required to add type annotations for each argument, so the system can determine the correct type to pass.
- The ability function is required to add a DocString for the ability function that describes the need of the function.
- The ability function is required to return a string which contains the described output of the function.

Here's an example for the `get_files_list` ability:

```python
import os
from assistant import Assistant


# Create a new assistant instance with some instructions
assistant = Assistant("You are a helpful assistant")


@assistant.ability(path="the path where you want to list the files")
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
   - Use the `@assistant.ability` decorator
   - Add a description in the ability decorator for each argument
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
