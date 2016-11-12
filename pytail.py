#!/usr/bin/env python3
#
# Copyright 2016, Acme Corp. All rights reserved.
#
# pytail.py
#   A pure Python implementation of tail.
#
# Authors:
#   Byron Dover <byrondover@gmail.com>
#
# License:
#   BSD
#


import argparse
import sys


class Tailer:
    """
    Given input as a positional argument or via stdin, limit output according
    to arguments.
    """

    def __init__(self, _input):
        self.input = _input

    def tail(self, lines=10):
        reversed_lines = list(reversed(self.input.readlines()))
        tail_lines = []

        for line in range(lines):
            try:
                one_line = reversed_lines[line]
                tail_lines.append(one_line)
            except IndexError:
                break

        return list(reversed(tail_lines))


def run():
    tailer = Tailer(open('wiredrive_devtest.py', 'r'))
    lines = tailer.tail()
    for line in lines:
        print(line, end=str())


if __name__ == '__main__':
    run()
