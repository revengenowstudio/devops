import os


class Env:
    # github action
    GITHUB_ACTIONS = "GITHUB_ACTIONS"
    REPOSITORY_TOKEN = "REPOSITORY_TOKEN"
    VERSION_START = "VERSION_START"
    VERSION_END = "VERSION_END"


def should_run_in_github_action() -> bool:
    return os.environ.get(Env.GITHUB_ACTIONS) == "true"


def should_run_in_local() -> bool:
    return not should_run_in_github_action()
