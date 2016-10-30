#!/usr/bin/env python3
#
# unique_bot.py
#   Given input via stdin, return unique lines.
#

import sys


class UniqueBot():
    """
    Given input, returns unique lines.
    """

    def __init__(self, input, count=False):
        self.count = count
        self.input = input
        self.unique_lines = dict()

    def _find_unique_lines(self):
        """
        Loop through input, count unique lines.
        """

        for line in self.input:
            clean_line = line.strip()

            if clean_line:
                if clean_line in self.unique_lines:
                    self.unique_lines[clean_line] += 1
                else:
                    self.unique_lines[clean_line] = 1

    def print_lines(self):
        """
        Print lines to stdout, optionally including unique counts.
        """
        self._find_unique_lines()

        for line, count in self.unique_lines.items():
            if self.count:
                formatted_line = "{count} {line}".format(count=count, line=line)
            else:
                formatted_line = line

            print(formatted_line)


def run():
    """
    Populate UniqueBot with stdin input, and print unique lines.
    """
    input = sys.stdin
    unique_bot = UniqueBot(input)
    unique_bot.print_lines()


# Here goes nothing!
run()
