import re
import sys
import pprint
import collections

def file_to_string(fname):
    handle = open(fname, 'r')
    content = handle.read()
    handle.close()
    content = re.sub('\n', '\t', content)
    return content

def parse(in_string, pattern):
    retval = None
    match = pattern.match(in_string)
    if match:
        retval=match.groups() 
    return retval

def parse_all(in_string, pattern):
    match = pattern.findall(in_string)
    return match

def split_lines(in_string):
    lines = re.split('\t', in_string)
    return lines

def tabs_to_spaces(in_string):
    return re.sub('\t', ' ', in_string) 

def header_to_list(in_string):
    result = {}
    header_pattern = re.compile(r'.+HEADER;\s+(.+)\s+ENDSEC;\s+DATA;')
    header_property_pattern = re.compile(r'\s?\(?([A-Z0-9_]+) (\(.*?\));')
    header_args_pattern = re.compile(r".*?'(.*?)',?")
    header_str = parse(in_string, header_pattern)
    header_str = tabs_to_spaces(header_str[0])

    header_propval = parse_all(header_str, header_property_pattern)
    if header_propval:
        result = [] 
        for i,prop in enumerate(header_propval):
            args = parse_all(prop[1], header_args_pattern)
            args = [x.strip("'") for x in args]
            result.append((prop[0], args)) 

    return result

def data_to_dict(in_string):
    result = collections.OrderedDict() 
    data_pattern = re.compile(r'.+\s+DATA;\s+(.+)\s+ENDSEC;')
    enum_pattern = re.compile(r'\s?(#[0-9]+) =(.+);')
    property_pattern = re.compile(r'\s?\(?([A-Z0-9_]+) (\(.*?\))\s?\)?')
    args_pattern = re.compile(r'\(?([^\s\(]+?)[,|\s]\)?')
    data = parse(in_string, data_pattern)
    datalines = split_lines(data[0])
    for line in datalines:
        directive  = parse(line, enum_pattern)
        propval = parse_all(directive[1], property_pattern)
        if propval:
            result[directive[0]] = [] 
            for i,prop in enumerate(propval):
                args = parse_all(prop[1], args_pattern)
                args = [x.strip("'") for x in args]
                result[directive[0]].append((prop[0], args)) 
    return result

def step_to_dict(filename):
    result = {}
    content = file_to_string(filename)
    result['header'] = header_to_list(content)
    result['data'] = data_to_dict(content) 
                   
           
   
    return result


if __name__ == "__main__":
    content = step_to_dict(sys.argv[1])
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(content)
