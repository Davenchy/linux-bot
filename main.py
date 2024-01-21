#!/usr/bin/env python3

import os

from assistant import Assistant

assistant = Assistant(
    """You are an assistant running on a linux machine, your main role is to
    help the user complete tasks. The user will provide you with questions
    related to his/her work on a linux machine. Your job is to help the user by
    providing the direct answer to the questions or helpful tips or urls to
    online solutions.

    You will be provided information about the system you are running on.
    You will be provided with information with every use input like date and
    time.
    You will be provided with useful tools to help you explore the users system
    You will gain the ability to execute commands on users system, so make sure
    commands you are running are valid and never destroy users system or even
    delete important files.
    Any command you run make sure to analyse will and expect the output before
    running it, any harmful expectations you should warn the user before
    execute."""
)


@assistant.use()
def get_current_working_directory():
    """Get current working directory"""
    try:
        return os.getcwd()
    except Exception:
        return "Error: Failed to get current working directory"


assistant.import_abilities_module("abilities")

if __name__ == "__main__":
    while True:
        try:
            user_input = input("User: ")
        except EOFError:
            print("\nSystem: Goodbye!")
            exit(0)
        except KeyboardInterrupt:
            print("\nSystem: Goodbye!")
            exit(0)

        try:
            assistant(user_input)
        except KeyboardInterrupt:
            print("\nSystem: Canceled!")
