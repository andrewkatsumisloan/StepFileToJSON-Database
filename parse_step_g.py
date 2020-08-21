"""
Parse a STEP file into a dictionary
"""
import os
import re
import sys
import pprint
import collections
import json

def file_to_string(fname):
    """
    return the contents of a file as a string
    :param fname: full path to input file
    """
    handle = open(fname, 'r')
    content = handle.read()
    handle.close()
    content = re.sub(r'\s', '', content)
    return content

def parse(in_string, pattern):
    """
    parse a string into meaningful parts
    :param in_string: input string
    :param pattern:   regex
    """
    retval = None
    match = pattern.match(in_string)
    if match:
        retval = match.groups()
    return retval

def split_lines(in_string):
    """
    return a list of lines
    :param in_string:
    """
    lines = re.split(';', in_string)
    return lines


def to_type(instr):
    try:
        return int(instr)
    except ValueError:
        try:
            return float(instr)
        except ValueError:
            return instr.strip("'")

def parse_line(line):
    """
    each line consists of one or more directives of the form
    <property>( <arg1>, <arg2>...). The arg lists may be empty
    or contain nested lists of args
    """
    token = ""
    result = []
    stack = []
    stack.append(result)
    for x in line:
        if x in '(),':
            arg = token.strip()
            if arg:
                stack[-1].append(to_type(arg))
            token = ''
            if x == '(':
                stack.append([])
            elif x == ')':
                top = stack.pop()
                stack[-1].append(top)
        else:
            token += x
    return result


def header_to_list(in_string):
    """
    return a list of the header fields
    :param in_string:
    """
    result = {}
    header_pattern = re.compile(r'.+HEADER;(.+)ENDSEC;DATA;')
    header_str = parse(in_string, header_pattern)
    header_str = header_str[0]

    result = parse_line(header_str)

    return result


def data_to_dict(in_string):
    """
    return a dictionary of the file's data
    :param in_string:
    """
    result = collections.OrderedDict()
    data_pattern = re.compile(r'.+DATA;(.+)ENDSEC;')
    enum_pattern = re.compile(r'(#[0-9]+)=(.+)')
    data = parse(in_string, data_pattern)
    datalines = split_lines(data[0])
    for line in datalines:
        if line:
            #print(line)
            directive = parse(line, enum_pattern)
            result[directive[0]] = parse_line(directive[1])
    return result

def step_to_dict(filename):
    """
    return a dictionary containing header and data branches
    :param filename:
    """
    result = {}
    content = file_to_string(filename)
    result['header'] = header_to_list(content)
    result['data'] = data_to_dict(content)
    return result


def to_json(stepdict, filename):
    handle = open(filename, 'w')
    json.dump(stepdict, handle)
    handle.close()

def iter_args(in_list, data, result):
    """
    :param in_list: list of args and lists
    :param data: the dict-ified data fork of a step file
    :param result: list that will contain nested lists of expanded # labels
    """
    for arg in in_list:
        if isinstance(arg, list):
            result.append([])
            iter_args(arg, data, result[-1])
        elif isinstance(arg, str) and arg.startswith('#'):
            newlist = data[arg]
            iter_args(newlist, data, result)
        else:
            result.append(arg)

if __name__ == "__main__":
    step_dict = step_to_dict(sys.argv[1])
    to_json(step_dict, ".".join([os.path.splitext(sys.argv[1])[0], "json"]))

    line21 = step_dict['data']['#21']
    print("Requested line:", "#21:", line21)
    expanded = []
    iter_args(line21, step_dict['data'], expanded )

    print("Expanded structure:", expanded)

    pp = pprint.PrettyPrinter()
    pp.pprint(step_dict)