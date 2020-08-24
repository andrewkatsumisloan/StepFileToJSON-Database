"""
Parse a STEP file into a JSON file that can be queried in any way.

To use program, run via command line: python3 parse_args.py <name of step file>.STEP <key>
Where <key> is either a string or integer value by which you want to query, or a quoted label number preceded by a pound key (i.e '#18')

There are two different types of arguments this program accepts
    1. a "label number" (i.e '#39'), which will return a nested list of the line and the references (expanded) that each line contains
    2. a string (not case sensitive), int, or float, which will return every line in which it appears.

Examples:
LINUX TERMINAL
    python3 parse_step_final.py step_test_1.STEP '#33'
        - Returns a nested list containing line #33 and its expanded references.

    python3 parse_step_final.py step_test_1.STEP VECTOR
        - Returns every line that contains the string of characters VECTOR in the properties or values fields.

    python3 parse_step_final.py step_test_1.STEP 39
        - Returns every line that contains '39' in the properties or values fields
"""

import os
import re
import sys
import pprint
import collections
import json
import argparse

def file_to_string(fname):
    """
    return the contents of a .STEP file as a string
    :param fname: full path to input file
    """
    handle = open(fname, 'r')
    content = handle.read()
    handle.close()
    content = re.sub(r'\s', '', content)
    return content


def parse(in_string, pattern):
    """
    parse a string into meaningful parts, return a tuple
    :param in_string: input string
    :param pattern: regex for relevant string
    """
    retval = None
    match = pattern.match(in_string)
    if match:
        retval = match.groups()
        # print('this is retval: ', retval)
    return retval

def split_lines(in_string):
    """
    return a list of lines separated by semicolons.
    :param in_string:
    """
    lines = re.split(';', in_string)
    return lines

def to_type(instr):
    """
    This function converts strings to ints or floats, or string (strip is for 'NONE')
    :param instr:
    :return:
    """
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
    Returns result, a list that contains the properties and values in correct nested form.
    """
    token = ""
    result = []
    stack = []
    stack.append(result)
    for x in line:
        # If x is a ( ) or , ...
        if x in '(),':
            arg = token.strip()
            if arg:
                # adding arg to the list at the 'top' of the stack
                stack[-1].append(to_type(arg))
            token = ''
            # Append a list to the top of the stack if you encounter an open parenthesis
            if x == '(':
                stack.append([])
            # Pop off the top of the stack, store it in var top.
            # Append top to list on top of stack.
            elif x == ')':
                top = stack.pop()
                stack[-1].append(top)
        else:
            token += x
    # print('this is the return value of result', result)
    return result


def parse_header(in_string):
    """
    return a list of the header
    :param in_string:
    """
    # result = {}
    header_pattern = re.compile(r'.+HEADER;(.+)ENDSEC;DATA;')
    header_str = parse(in_string, header_pattern)
    header_str = header_str[0]

    result = parse_line(header_str)
    return result


def data_to_dict(in_string):
    """
    return an ordered dictionary of the file's data segment
    :param in_string: Pass in a string containing the data segment
    """
    result = collections.OrderedDict()
    # data_pattern Extracts everything in file between 'DATA; and 'ENDSEC;'
    data_pattern = re.compile(r'.+DATA;(.+)ENDSEC;')
    # enum_pattern captures the label # and everything after the = sign...
    enum_pattern = re.compile(r'(#[0-9]+)=(.+)')
    data = parse(in_string, data_pattern)
    # datalines is a list of comma separated lines (demarcated by ';'), data[0] is the entire data field in string form
    datalines = split_lines(data[0])
    for line in datalines:
        if line:
            directive = parse(line, enum_pattern)
            result[directive[0]] = parse_line(directive[1])
    return result


def step_to_dict(filename):
    """
    return a dictionary containing header and data as key values. data is comprised of another dictionary, an ordered dictionary.
    :param filename:
    """
    result = {}
    content = file_to_string(filename)
    result['header'] = parse_header(content)
    result['data'] = data_to_dict(content)
    return result


def to_json(stepdict, filename):
    handle = open(filename, 'w')
    json.dump(stepdict, handle)
    handle.close()


def from_json(filename):
    """
    :param filename:
    :return: dictionary
    """
    handle = open(filename, 'r')
    step_dict = json.load(handle)
    handle.close()
    return step_dict


def iter_args(in_list, data, result):
    """
    Recursively handle creation of list containing nested lists (to show expanded list)
    :param in_list: line to be expanded
    :param data: the dict-ified data seg of a step file
    :param result: list that will contain nested lists of expanded # labels
    """
    for arg in in_list:
        if isinstance(arg, list):
            result.append([])
            iter_args(arg, data, result[-1])
        # If its a label starting with #, then create a new list containing
        elif isinstance(arg, str) and arg.startswith('#'):
            newlist = data[arg]
            iter_args(newlist, data, result)
        else:
            result.append(arg)

def contains_query(line, string):
    """
    This function checks whether the requested string is in the given line by converting the list (line) into a string.
    :param line: list of properties and values for one "line" (i.e a line as defined by #xx in STEP file)
    :param string: the query, the string that the user wants to find in the given line.
    :return: boolean, True if in line, False if not in line
    """
    return string in str(line)


def query(data_dict, string):
    """
    Append the line to the list called result IFF string is in that line (call contains_query to check).
    :param data_dict: the dictionary passed in by user
    :param string: the string that the user is querying by
    :return: a list containing all of the instances of the lines that contain the string
    """
    result = []
    # Iterates through keys in data_dict['data']
    for label in data_dict['data'].keys():
        if contains_query(data_dict['data'][label], string):
            result.append((label, data_dict['data'][label]))

    return result
    # Call contains_query on every line
    # Append line to results if match is found.

def usage():
    """
    Command line help/Error message if < 3 arguments entered.
    """
    print()
    print('parse_step')
    print('SYNTAX:')
    print('python3 parse_step.py <stepfile> <key>')
    print()
    print('EXAMPLE:')
    print('python3 parse_step_h.py step_test_1.STEP "#21"')
    print('(Note: labels containing special character "#" must be quoted)')
    

if __name__ == "__main__":
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    filename = sys.argv[1]
    label = sys.argv[2]
    label = label.upper()

    json_filename = ".".join([os.path.splitext(filename)[0], "json"])
    # Convert STEP file to python structure
    step_dict = step_to_dict(filename)

    # save to json file
    to_json(step_dict, json_filename)

    # load from json file
    new_dict = from_json(json_filename)

    # Either prints expanded dictionary (if) or returns every line containing given string, int, float value (else)
    if label.startswith('#'):
        # grab the data associated with a label
        line = new_dict['data'][label]
        print("Requested line:", label, line)
        expanded = []
        iter_args(line, step_dict['data'], expanded)
        pp = pprint.PrettyPrinter()
        pp.pprint(expanded)
        # print("Expanded structure:", expanded)
    else:
        matches = query(new_dict, label)
        for match in matches:
            print(match)

    # pp = pprint.PrettyPrinter()
    # pp.pprint(expanded)

    #pp = pprint.PrettyPrinter()
    #pp.pprint(step_dict)
