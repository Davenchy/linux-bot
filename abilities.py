import os
import sys
import psutil
import shutil
import subprocess
from datetime import datetime
from assistant import Assistant, json


@Assistant.ability()
def get_date_and_time():
    """Get date and time"""
    now = datetime.now()

    return "hour: {}, minute: {}, second: {}, day: {}, month: {}, year: {}".format(
        now.hour, now.minute, now.second, now.day, now.month, now.year
    )


@Assistant.ability(path="the path to get its type")
def get_path_type(path: str) -> str:
    """Returns the type of the path: file, directory or link"""
    try:
        path = os.path.expanduser(path)
        if os.path.isfile(path):
            return "file"
        elif os.path.isdir(path):
            return "directory"
        elif os.path.islink(path):
            return "link"
        else:
            return "unknown"
    except Exception:
        return "Error: Failed to get path type"


@Assistant.ability(path="the path to the file or directory")
def get_path_size(path: str) -> str:
    """Returns the size in bytes of the file
    or the number of files in the directory depends on the path type"""
    try:
        path = os.path.expanduser(path)
        if os.path.isfile(path):
            return f"{os.path.getsize(path)} bytes"
        elif os.path.isdir(path):
            return f"{len(os.listdir(path))} files"
        else:
            return "unknown"
    except Exception:
        return "Error: Failed to get path size/count"


@Assistant.ability(path="the path where the files to list are located")
def get_files(path: str) -> str:
    """Get a list of files/directories in specific path each one in a new line
    each line is formatted as the following:

    filetype: file, directory or link
    filesize: the size of the file in bytes or number of files in the directory
    in case of a directory
    filename: the name of the file/directory"""
    try:
        files = os.listdir(os.path.expanduser(path))
        formatted_files = []

        for file in files:
            filepath = os.path.join(path, file)
            filetype = get_path_type(filepath)
            filesize = get_path_size(filepath)
            formatted_files.append(f"{filetype}, {filesize}, {file}")
        return "\n".join(formatted_files)
    except Exception:
        return "Error: Failed to get files list"


@Assistant.ability(path="The path of the file to read")
def read_file(path: str) -> str:
    """Read a file using its path"""
    with open(os.path.expanduser(path), "r") as f:
        return f.read()


@Assistant.ability()
def get_package_managers() -> str:
    """Get a list of known package managers and its paths on the system if
    any of them is installed on the system"""

    known_managers = ["apt", "yum", "dnf", "pacman", "zypper", "nix"]
    try:
        return json.dumps({
            manager: shutil.which(manager)
            for manager in known_managers})
    except subprocess.CalledProcessError:
        return "Error: Failed to get package managers list"


@Assistant.ability(command_name="the name of the command to check")
def is_command_installed(command_name: str) -> str:
    """Check if a command is installed on the system"""
    try:
        if shutil.which(command_name) is None:
            return "not installed"
        else:
            return "installed"
    except subprocess.CalledProcessError:
        return "Error: Failed to check if command is installed"


@Assistant.ability(command="The shell command to execute")
def execute(command: str) -> str:
    """Execute a shell command and returns the returned code, stdout and stderr
    """

    try:
        result = subprocess.run(
            command, shell=True, text=True,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if len(stderr) > 0:
            print(stderr, file=sys.stderr)

        return json.dumps({
            "return_code": result.returncode,
            "stdout": stdout,
            "stderr": stderr,
        })
    except subprocess.CalledProcessError as e:
        print(e)
        return json.dumps({
            "return_code": e.returncode,
            "stdout": e.stdout,
            "stderr": e.stderr,
        })


@Assistant.ability()
def get_environment_variables():
    """Get all environment variables"""
    return json.dumps(dict(os.environ))


@Assistant.ability()
def get_disk_partitions():
    """Get all system disks, their information and usage"""
    results = list()

    for partition in psutil.disk_partitions():
        usage = psutil.disk_usage(partition.device)

        results.append({
            "disk": partition.device,
            "usage_total": usage.total,
            "usage_used": usage.used,
            "usage_free": usage.free,
            "usage_percent": usage.percent,
            "mountpoint": partition.mountpoint,
            "fstype": partition.fstype,
            "mount_options": partition.opts,
        })

    return json.dumps(results)


@Assistant.ability()
def get_system_usage():
    """Get system usage like: cpu, memory, disk"""
    # Get CPU usage in 1 minutes
    cpu_percent_1 = psutil.cpu_percent(interval=1)
    # Get CPU usage in 5 minutes
    cpu_percent_5 = psutil.cpu_percent(interval=5)
    # Get CPU usage in 15 minutes
    cpu_percent_15 = psutil.cpu_percent(interval=15)

    # Get memory usage
    memory_info = psutil.virtual_memory()

    return json.dumps({
        "disks": get_disk_partitions(),
        "cpu_1min": cpu_percent_1,
        "cpu_5min": cpu_percent_5,
        "cpu_15min": cpu_percent_15,
        "memory_free": memory_info.free,
        "memory_used": memory_info.used,
        "memory_total": memory_info.total,
        "memory_percent": memory_info.percent,
        "memory_slab": memory_info.slab,
        "memory_active": memory_info.active,
        "memory_inactive": memory_info.inactive,
        "memory_buffers": memory_info.buffers,
        "memory_cached": memory_info.cached,
        "memory_shared": memory_info.shared,
        "memory_available": memory_info.available,
    })


# !TODO: check processes network usage
# !TODO: check listening process and their ports
# !TODO: check network connectivity
# !TODO: ping addresses
# !TODO: get network interfaces
# !TODO: scan for devices and open ports in the local network
