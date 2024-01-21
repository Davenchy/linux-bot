from datetime import datetime
import os

from assistant import Assistant, json

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


@assistant.ability()
def get_date_and_time():
    """Get date and time"""
    now = datetime.now()

    return "hour: {}, minute: {}, second: {}, day: {}, month: {}, year: {}".format(
        now.hour, now.minute, now.second, now.day, now.month, now.year
    )


@assistant.ability()
def get_current_working_directory():
    """Get current working directory"""
    try:
        return os.getcwd()
    except Exception:
        return "Error: Failed to get current working directory"


@assistant.ability(path="the path to list its file names")
def get_files(path: str) -> str:
    """return a list of files in specific path"""
    try:
        files = os.listdir(os.path.expanduser(path))
        return json.dumps(", ".join([file for file in files]))
    except Exception:
        return "Error: Failed to get files list"


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
