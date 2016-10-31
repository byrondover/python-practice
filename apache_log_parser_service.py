#!/usr/bin/env python3
#
# (c) 2016, Byron Dover <byrondover@gmail.com>
#
# apache_log_parser.py
#   Counts 404s in Apache log passed into stdin.
#
# Authors:
#   Byron Dover <byrondover@gmail.com>
#
# License:
#   MIT
#

import json
import sys

from flask import Flask, request

app = Flask(__name__)

class ApacheLogParser:
    """
    Given Apache log lines, count 404s.
    """

    def __init__(self, _input):
        self.input = _input

    def count_response_codes(self, code=404):
        """
        Count number of given response codes.
        """
        count = 0

        for i, line in enumerate(self.input):
            substrings = line.split()
            try:
                response_code = substrings[6]
                if response_code == str(code):
                    count += 1
            except IndexError:
                print('Line {line_number} appears to be invalid.'.format(
                    line_number=i + 1), file=sys.stderr)

        return count


def count_by_code(_input, code):
    """
    Print number of given response codes via ApacheLogParser.
    """
    log_parser = ApacheLogParser(_input)
    count = log_parser.count_response_codes(code)
    return count


def run():
    """
    Print number of 404s found in stdin via ApacheLogParser.
    """
    _input = sys.stdin
    count = count_by_code(_input, 404)
    print(count)


@app.route("/count")
def count_response_codes():
    """
    Expects ?code=200&log_lines=["line1", "line2"], for example.
    """
    code = request.args.get('code', 200)
    log_lines = request.args.get('log_lines')

    if log_lines:
        lines_list = json.loads(log_lines)
        count = count_by_code(lines_list, code)
    else:
        count = 0

    response = str(count)
    return response


# Here goes nothing!
if __name__ == '__main__':
    run()
