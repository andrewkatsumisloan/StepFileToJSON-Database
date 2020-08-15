import re
import sys


def file_to_string(fname):
    handle = open(fname, 'r')
    content = handle.read()
    handle.close()
    # Replace new line with tab
    content = re.sub('\n', '\t', content)
    return content

# Generalized parse function which takes string and pattern type.
def parse(in_string, pattern):
    retval = None
    match = pattern.match(in_string)
    if match:
        retval = match.groups()
    return retval


def parse_all(in_string, pattern):
    match = pattern.findall(in_string)
    return match

def split_lines(in_string):
    lines = re.split('\t', in_string)
    return lines

def step_to_dict(filename):
    # Gets everything in between HEADER; and the first ENDSEC;
    header_pattern = re.compile(r'.+HEADER;\s+(.+)\s+ENDSEC;\s+DATA;')

    # Gets everything between DATA; and ENDSEC;
    data_pattern = re.compile(r'.+\s+DATA;\s+(.+)\s+ENDSEC;')
    enum_pattern = re.compile(r'\s?(#[0-9]+) =(.+);')
    # property_pattern = re.compile(r'\s?\(?\s([A-Z0-9_]+) (\(.*?\))\s?\)?')
    property_pattern = re.compile(r'\s?\(?([A-Z0-9_]+) (\(.*?\))\s?\)?')

    content = file_to_string(filename)

    header = parse(content, header_pattern)
    print('header=', header)

    data = parse(content, data_pattern)
    # print('data=', data)
    datalines = split_lines(data[0])
    for line in datalines:
        directive = parse(line, enum_pattern)
        propval = parse_all(directive[1], property_pattern)
        if propval:
            # print("{0:5} {1:25} {2}".format(directive[0], propval[0], propval[1]))
            print("{0:5} {1}".format(directive[0], propval))

if __name__ == "__main__":
    content = step_to_dict(sys.argv[1])


