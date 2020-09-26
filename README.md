#STEP FILE TO SEARCHABLE/QUERYABLE JSON OBJECT FOR STORAGE IN DATABASE 

This is a command line utility that enables the user to convert a .STEP to searchable JSON object.  


Parse a STEP file into a JSON file that can be queried in any way.

To use program, run via command line: python3 parse_args.py <name of step file>.STEP <key>
Where <key> is either a string or integer value by which you want to query,
or a quoted label number preceded by a pound key (i.e '#18')

There are two different types of arguments this program accepts
    1. a "label number" (i.e '#39'), which will return a nested list of the line
    and the references that each line contains
    2. a string (not case sensitive), int, or float, which will return every line
    in which that string appears.

Examples:
LINUX TERMINAL
    python3 parse_step.py step_test_1.STEP '#33'
        - Returns a nested list containing line #33 and its expanded references.

    python3 parse_step.py step_test_1.STEP VECTOR
        - Returns every line that contains the string of characters VECTOR in the
        properties or values fields.

    python3 parse_step.pu step_test_1.STEP 39
        - Returns every line that contains '39' in the properties or values fields


