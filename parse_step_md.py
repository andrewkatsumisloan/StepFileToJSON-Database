"""
Parse a STEP file into a dictionary
"""

import re
import sys
import pprint
import copy
import collections
import pyparsing


def parse_args(string):
    return re.split(',', string)

def to_type(string):
        try:
            return int(string)
        except ValueError:
            try:
                return float(string)
            except ValueError:
                return string

def parse_line(string):
    # Strip outer parenthesis
    if string[0] == '(' and string[-1] == ')':
        string = string[1:-1]
    result = {}
    p_tracker = []
    level = 0
    property = ''
    value = ''
    for x in string:
        if x == '(':
            p_tracker.append('(')
            # if len(p_tracker) > 1:
            #     value += x
        elif x == ')':
            p_tracker.pop()
            # if len(p_tracker) > 1:
            #     value += x
            if not p_tracker:
                temp = parse_args(value)
                realVal = []
                for item in temp:
                    item = to_type(item)
                    realVal.append(item)
                result[property] = realVal
                property = ''
                value = ''
        else:
            if p_tracker and p_tracker[-1] == '(':
                value += x
            else:
                property += x
    return result

def file_to_string(fname):
    """
    return the contents of a file as a string
    :param fname: full path to input file (replacing new line character with tab)
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

def parse_all(in_string, pattern):
    """
    return a list of all matches
    :param in_string: input string
    :param pattern: regex
    """
    match = pattern.findall(in_string)
    return match


def split_lines(in_string):
    """
    return a list of lines
    :param in_string:
    """
    lines = re.split(';', in_string)
    return lines


# def tabs_to_spaces(in_string):
#     """
#     return a mutated form of in_string where spaces are converted to tabs
#     :param in_string:
#     """
#     return re.sub('\t', ' ', in_string)

def expand_line(dictionary, label):
    """
    This function should accept a filename, dictionary, and a label.
    It should return a nested dictionary where the labels are replaced by the values they correspond to.
    :param dictionary:
    :param label:
    :return nest_dict
    """
    # This should take a filename as well.
    result = {}
    result[label] = copy.copy(dictionary['data'][label])

    for pair in result[label]:
        for arg in pair[1]:
            if arg.startswith('#'):
                arg = expand_line(dictionary, arg)

    # How to check if # in argument list.
    return result

# def header_to_list(in_string):
#     """
#     return a list of the header fields
#     :param in_string:
#     """
#     result = {}
#     header_pattern = re.compile(r'.+HEADER;(.+)ENDSEC;DATA;')
#     header_property_pattern = re.compile(r'\(?([A-Z0-9_]+) (\(.*?\));')
#     header_args_pattern = re.compile(r".*?'(.*?)',?")
#     header_str = parse(in_string, header_pattern)
#     header_str = tabs_to_spaces(header_str[0])
#
#     header_propval = parse_all(header_str, header_property_pattern)
#     if header_propval:
#         result = []
#         for prop in header_propval:
#             args = parse_all(prop[1], header_args_pattern)
#             args = [x.strip("'") for x in args]
#             result.append((prop[0], args))
#
#     return result


def data_to_dict(in_string):
    """
    return a dictionary of the file's data
    :param in_string:
    """
    result = {}
    result['data'] = collections.OrderedDict()
    # data_pattern extracts all of the contents between DATA; and ENDSEC;
    data_pattern = re.compile(r'.+DATA;(.+)ENDSEC;')

    # enum_pattern extracts two groups, the label# and everything that comes after the = sign
    enum_pattern = re.compile(r'(#[0-9]+)=(.+)')

    # property_pattern extracts two groups, the property name and the
    property_pattern = re.compile(r'\(?([A-Z0-9_]+)(\(.*?\))\)?')

    # args_pattern extracts
    args_pattern = re.compile(r'\(?([^\(]+?)[,]\)?')
    data = parse(in_string, data_pattern)
    datalines = split_lines(data[0]) #data[0] contains the data field

    for line in datalines[:-1]:
        # print('LINE: ', line)
        directive = parse(line, enum_pattern)
        # print('Print dir: ', directive)
        # directive is a match object, where directive[1] is equal to the second group

        line_dict = parse_line(directive[1])
        result['data'][directive[0]] = line_dict

        # directive[1] will be all the content after the = sign, so the property name and the values
            # propval holds list containing all matching groups
            # propval = parse_all(directive[1], property_pattern)
            # print(propval)
            # if propval:
            #     result[directive[0]] = []
            #     for prop in propval:
            #         args = parse_all(prop[1], args_pattern)
            #         args = [x.strip("'") for x in args]
            #         result[directive[0]].append((prop[0], args))
            #         print(directive[0], prop[0], args)
    return result


def step_to_dict(filename):
    """
    return a dictionary containing header and data branches
    :param filename:
    """
    result = {}
    content = file_to_string(filename)
    # result['header'] = header_to_list(content)
    result['data'] = data_to_dict(content)
    return result


if __name__ == "__main__":
    step_dict = step_to_dict(sys.argv[1])
    pp = pprint.PrettyPrinter()
    pp.pprint(step_dict)
    # print(expand_line(step_dict, '#11'))
    # expand_line(step_dict, '#12')


