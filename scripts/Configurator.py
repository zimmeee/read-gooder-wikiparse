import os
import sys
import inspect


def configure_stanford_parser(directory="../resources"):
    # Set os environment vars to find Stanford Parser
    stanford_parser_directory = directory
    stanford_parser_models_directory = directory
    os.environ['STANFORD_PARSER'] = stanford_parser_directory
    os.environ['STANFORD_MODELS'] = stanford_parser_models_directory


def runnable_from_command_line():
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(
        inspect.getfile(inspect.currentframe()))[0], "../format")))

    print(cmd_subfolder)
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)

