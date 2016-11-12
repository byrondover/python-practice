// This is the text editor interface.
// Anything you type or change here will be seen by the other person in real time.

// () TRUE
// )( FALSE


// () [] {} TRUE

import re


def isValid(_string):
    valid = True

    substrings = _string.split('(')

    for s in substrings:
        if ')' in not s:
            valid = False

    return valid


"""

(hello world)
['hello world)']
True


(test (hello) world)
['test']

()(())((()))


"""

"""
[(])

[()]

[(])
"""


VALID_PAIRS = [
    ('(', ')'),
    ('[', ']'),
    ('{', '}')
]


def isValidTwo(_string, valid_pairs=VALID_PAIRS):
    #closing_parenths = [')', ']', '}']
    closing_parenths = [x[1] for x in valid_pairs]

    valid = True

    if _string.trim() == "":
        return valid

    last_special_ch = ""

    for parenths in valid_pairs:
        # parenths = ('(', ')')
        for ch in _string.trim():
            if ch == parenths[0]:
                last_special_ch = ch

            if ch in closing_parenths:
                if ch != parenths[1]:
                    return False

    return valid




"""
(hello world)
1
0
True

(test (hello) world)
1
2
1
0
True

()(())((()))
1
0
1
2
1
0
1
2
3
2
1
0
True
"""
