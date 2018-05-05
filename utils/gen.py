import ast
from configparser import ConfigParser, NoOptionError, NoSectionError
import json
import linecache
import logging.config
import os
import sys

import yaml


import ipdb
ipdb.set_trace()
logger = logging.getLogger(__name__)


def get_data_type(val):
    """
    Given a string, returns its corresponding data type

    ref.: https://stackoverflow.com/a/10261229

    :param val: string value
    :return: Data type of string value
    """
    try:
        # TODO: might not be safe to evaluate string
        t = ast.literal_eval(val)
    except ValueError:
        return str
    except SyntaxError:
        return str
    else:
        if type(t) is bool:
            return bool
        elif type(t) is int:
            return int
        elif type(t) is float:
            return float
        else:
            return str


def get_option_value(parser, section, option):
    value_type = get_data_type(parser.get(section, option))
    try:
        if value_type == int:
            return parser.getint(section, option)
        elif value_type == float:
            return parser.getfloat(section, option)
        elif value_type == bool:
            return parser.getboolean(section, option)
        else:
            value = parser.get(section, option)
            # Get the string before the escaping was applied by configparser
            # configparser adds an extra '\' before '\n' when it encounters a
            # newline in the configuration file config.ini
            # ref.: https://bit.ly/2HMpvng
            value = bytes(value, 'utf-8').decode('unicode_escape')
            return value
    except NoSectionError:
        print_exception()
        return None
    except NoOptionError:
        print_exception()
        return None


def print_exception(error=None):
    """
    For a given exception, print filename, line number, the line itself, and
    exception description.

    ref.: https://stackoverflow.com/a/20264059

    :return: None
    """
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    if error is None:
        err_desc = exc_obj
    else:
        err_desc = "{}: {}".format(error, exc_obj)
    # TODO: find a way to add the error description (e.g. AttributeError) without
    # having to provide the error description as input to the function
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), err_desc))


def read_config_from_ini(config_path):
    parser = ConfigParser()
    found = parser.read(config_path)
    if config_path not in found:
        print("ERROR: {} is empty".format(config_path))
        return None
    options = {}
    for section in parser.sections():
        options.setdefault(section, {})
        for option in parser.options(section):
            options[section].setdefault(option, None)
            value = get_option_value(parser, section, option)
            if value is None:
                print("ERROR: The option '{}' could not be retrieved from {}".format(option, config_path))
                return None
            options[section][option] = value
    return options


def read_config_from_yaml(config_path):
    with open(config_path, 'r') as stream:
        try:
            options = yaml.load(stream)
        except yaml.YAMLError as exc:
            print_exception(exc)
            return None
    return options


def setup_logging(log_conf_path):
    with open(log_conf_path, 'r') as f:
        config_dict = json.load(f)
        logging.config.dictConfig(config_dict)
