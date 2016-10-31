#!/usr/bin/env python3
#
# test_unique_bot.py
#   Basic unit tests for Unique Bot.
#

import unique_bot as ub

EXAMPLE_INPUT = [
    'test', '   test  ', 'fake', 'does this work\n\n', '\ntest\n\n\n\n', 'gabe'
]


def _fixture_unique_bot(count=False):
    unique_bot = ub.UniqueBot(EXAMPLE_INPUT, count)
    return unique_bot


def test_find_unique_lines():
    expected_results = {'gabe': 1, 'does this work': 1, 'fake': 1, 'test': 3}
    unique_bot = _fixture_unique_bot(count=False)
    unique_bot._find_unique_lines()
    results = unique_bot.unique_lines
    assert results == expected_results


def test_find_unique_lines_with_count():
    expected_results = {'gabe': 1, 'does this work': 1, 'fake': 1, 'test': 3}
    unique_bot = _fixture_unique_bot(count=True)
    unique_bot._find_unique_lines()
    results = unique_bot.unique_lines
    assert results == expected_results


def run():
    """
    Run unit tests in order.
    """
    try:
        test_find_unique_lines()
        test_find_unique_lines_with_count()
        print('All tests pass.')
    except AssertionError:
        print('One or more tests failed.')


# Blast-off!
if __name__ == '__main__':
    run()
