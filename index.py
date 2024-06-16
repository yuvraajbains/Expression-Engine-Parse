"""This is a parser that is used for regular expressions in which
it is changed into a structured representation which in this case is a parse tree.
"""
def re_parse(r):
    """
    Parses the regular expression string `r` into a parse tree.
    The parse tree is a structured representation of the regex.

    :param r: The regular expression string to parse.
    :return: The root node of the parse tree.
    """
    # Start parsing from the beginning of the string.
    idx, node = parse_split(r, 0)
    
    # Check if parsing reached the end of the string.
    if idx != len(r):
        # Raise an exception if there are unexpected characters.
        raise Exception('unexpected ")"')
    
    # Return the root of the parse tree.
    return node

def parse_split(r, idx):
    """
    Parses the alternation operator `|` in the regex string.

    :param r: The regular expression string.
    :param idx: The current index in the string.
    :return: A tuple (index, node) where `node` is the parse tree node.
    """
    # Start parsing a concatenation.
    idx, prev = parse_concat(r, idx)

    while idx < len(r):
        if r[idx] == ')':
            break  # Exit if closing parenthesis is encountered.
        if r[idx] != '|':
            break  # Exit if not an alternation operator.

        # Parse the right side of the alternation.
        idx, node = parse_concat(r, idx + 1)
        
        # Create a split node connecting the previous node and the new node.
        prev = ('split', prev, node)
    
    # Return the current index and the parse tree node.
    return idx, prev

def parse_concat(r, idx):
    """
    Parses concatenation in the regex string.

    :param r: The regular expression string.
    :param idx: The current index in the string.
    :return: A tuple (index, node) where `node` is the parse tree node.
    """
    prev = None  # Initialize previous node as None.

    while idx < len(r):
        if r[idx] in '|)':
            break  # Exit if an alternation or closing parenthesis is encountered.
        
        # Parse the next node.
        idx, node = parse_node(r, idx)
        
        if prev is None:
            prev = node  # Set the first node.
        else:
            prev = ('cat', prev, node)  # Create a concatenation node.

    # Return the current index and the parse tree node.
    return idx, prev

def parse_node(r, idx):
    """
    Parses a single node in the regex string. This includes characters, dots, and parenthesized expressions.

    :param r: The regular expression string.
    :param idx: The current index in the string.
    :return: A tuple (index, node) where `node` is the parse tree node.
    """
    if idx >= len(r):
        return idx, None  # Return if the string is exhausted.
    
    ch = r[idx]  # Get the current character.
    idx += 1  # Move to the next character.
    
    if ch == '(':
        idx, node = parse_split(r, idx)  # Parse a subexpression.
        if idx < len(r) and r[idx] == ')':
            idx += 1  # Skip the closing parenthesis.
        else:
            raise Exception('unbalanced parenthesis')  # Error for unbalanced parentheses.
    elif ch == '.':
        node = 'dot'  # Dot character represents any single character.
    else:
        node = ch  # Single character node.

    # Handle postfix operators.
    idx, node = parse_postfix(r, idx, node)
    
    # Return the current index and the node.
    return idx, node

def parse_postfix(r, idx, node):
    """
    Parses postfix operators `*`, `+`, `{n,m}`.

    :param r: The regular expression string.
    :param idx: The current index in the string.
    :param node: The node to apply the postfix operators to.
    :return: A tuple (index, node) where `node` is the modified parse tree node.
    """
    if idx == len(r) or r[idx] not in '*+{':
        return idx, node  # Return if no postfix operator is found.

    ch = r[idx]
    idx += 1  # Move to the next character.

    if ch == '*':
        rmin, rmax = 0, float('inf')  # Zero or more repetitions.
    elif ch == '+':
        rmin, rmax = 1, float('inf')  # One or more repetitions.
    else:
        idx, i = parse_int(r, idx)  # Parse the integer inside `{}`.
        if i is None:
            raise Exception('expect int')
        rmin = rmax = i
        
        if idx < len(r) and r[idx] == ',':
            idx, j = parse_int(r, idx + 1)
            rmax = j if j is not None else float('inf')  # Handle the optional max value.
        
        if idx < len(r) and r[idx] == '}':
            idx += 1
        else:
            raise Exception('unbalanced brace')  # Error for unbalanced braces.

    # Sanity checks for repetition range.
    if rmax < rmin:
        raise Exception('min repeat greater than max repeat')
    if rmin > 1000:  # Example limit for repetition number.
        raise Exception('the repetition number is too large')

    node = ('repeat', node, rmin, rmax)  # Create a repeat node.
    
    # Return the current index and the node.
    return idx, node

def parse_int(r, idx):
    """
    Parses an integer from the regex string.

    :param r: The regular expression string.
    :param idx: The current index in the string.
    :return: A tuple (index, integer) where `integer` is the parsed integer.
    """
    save = idx  # Save the starting index.
    while idx < len(r) and r[idx].isdigit():
        idx += 1  # Move to the next digit.
    # Return the parsed integer.
    return idx, int(r[save:idx]) if save != idx else None

# Test cases
test_cases = [
    ('', None),  # Empty string
    ('.', 'dot'),  # Single dot
    ('a', 'a'),  # Single character
    ('ab', ('cat', 'a', 'b')),  # Concatenation
    ('a|b', ('split', 'a', 'b')),  # Alternation
    ('a+', ('repeat', 'a', 1, float('inf'))),  # One or more repetitions
    ('a{3,6}', ('repeat', 'a', 3, 6)),  # Repetition with range
    ('a|bc', ('split', 'a', ('cat', 'b', 'c')))  # Alternation with concatenation
]

for expr, expected in test_cases:
    # Parse the expression and print the result.
    result = re_parse(expr)
    print(f"Expression: {expr} => Parsed: {result}")
    assert result == expected, f"Failed on {expr}"

# Print a success message if all tests pass.
print("All test cases passed.")
