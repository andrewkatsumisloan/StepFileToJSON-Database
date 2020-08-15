"""
Parse a STEP file into a dictionary
"""

import re
import sys
import pprint
import collections

def file_to_string(fname):
    """
    return the contents of a file as a string
    :param fname: full path to input file
    """
    handle = open(fname, 'r')
    content = handle.read()
    handle.close()
    content = re.sub('\n', '\t', content)
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
    lines = re.split('\t', in_string)
    return lines

def tabs_to_spaces(in_string):
    """
    return a mutated form of in_string where spaces are converted to tabs
    :param in_string:
    """
    return re.sub('\t', ' ', in_string)

def header_to_list(in_string):
    """
    return a list of the header fields
    :param in_string:
    """
    result = {}
    header_pattern = re.compile(r'.+HEADER;\s+(.+)\s+ENDSEC;\s+DATA;')
    header_property_pattern = re.compile(r'\s?\(?([A-Z0-9_]+) (\(.*?\));')
    header_args_pattern = re.compile(r".*?'(.*?)',?")
    header_str = parse(in_string, header_pattern)
    header_str = tabs_to_spaces(header_str[0])

    header_propval = parse_all(header_str, header_property_pattern)
    if header_propval:
        result = []
        for prop in header_propval:
            args = parse_all(prop[1], header_args_pattern)
            args = [x.strip("'") for x in args]
            result.append((prop[0], args))

    return result

def data_to_dict(in_string):
    """
    return a dictionary of the file's data
    :param in_string:
    """
    result = collections.OrderedDict()
    data_pattern = re.compile(r'.+\s+DATA;\s+(.+)\s+ENDSEC;')
    enum_pattern = re.compile(r'\s?(#[0-9]+) =(.+);')
    property_pattern = re.compile(r'\s?\(?([A-Z0-9_]+) (\(.*?\))\s?\)?')
    args_pattern = re.compile(r'\(?([^\s\(]+?)[,|\s]\)?')
    data = parse(in_string, data_pattern)
    datalines = split_lines(data[0])
    for line in datalines:
        directive = parse(line, enum_pattern)
        propval = parse_all(directive[1], property_pattern)
        if propval:
            result[directive[0]] = []
            for prop in propval:
                args = parse_all(prop[1], args_pattern)
                args = [x.strip("'") for x in args]
                result[directive[0]].append((prop[0], args))
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

if __name__ == "__main__":
    step_dict = step_to_dict(sys.argv[1])
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(step_dict)
