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

import sys


class ApacheLogParser:
    """
    Given Apache log lines, count 404s.
    """

    def __init__(self, _input):
        self.input = _input
        self.count = 0

    def count_404s(self):
        """
        Count number of 404 response codes.
        """
        for i, line in enumerate(self.input):
            substrings = line.split()
            try:
                response_code = substrings[6]
                if response_code == '404':
                    self.count += 1
            except IndexError:
                print('Line {line_number} appears to be invalid.'.format(
                    line_number=i + 1), file=sys.stderr)

        return self.count


def run():
    """
    Print number of 404s found in stdin via ApacheLogParser.
    """
    _input = sys.stdin
    log_parser = ApacheLogParser(_input)
    count = log_parser.count_404s()
    print(count)


# Here goes nothing!
if __name__ == '__main__':
    run()
