import re
import sys
import pprint


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

def step_to_dict(filename):
    result = {}
    header_pattern = re.compile(r'.+HEADER;\s+(.+)\s+ENDSEC;\s+DATA;')
    data_pattern = re.compile(r'.+\s+DATA;\s+(.+)\s+ENDSEC;')
    enum_pattern =  re.compile(r'\s?(#[0-9]+) =(.+);')
    property_pattern = re.compile(r'\s?\(?([A-Z0-9_]+) (\(.*?\))\s?\)?')
    args_pattern = re.compile(r'\(?([^\s\(]+?)[,|\s]\)?')

    content = file_to_string(filename)

    result['header'] = parse(content, header_pattern)

    data = parse(content, data_pattern)
    #print('data=', data)
    datalines = split_lines(data[0])
    result['data'] = {}
    for line in datalines:
        directive  = parse(line, enum_pattern)
        propval = parse_all(directive[1], property_pattern)
        if propval:
            result['data'][directive[0]] = [] 
            for i,prop in enumerate(propval):
                args = parse_all(prop[1], args_pattern)
                args = [x.strip("'") for x in args]
                result['data'][directive[0]].append((prop[0], args)) 
                   
           
   
    return result


if __name__ == "__main__":
    content = step_to_dict(sys.argv[1])

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(content)
