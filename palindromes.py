#!/usr/bin/env python3
#
# palindromes.py
#   Given string input, return all possible palindromes.
#

DEFAULT_TEXT = "racecarenterelephantmalayalam"


def is_palindrome(word):
    return all(word[i] == word[-1 * (i + 1)] for i in range(len(word) // 2))


def substrings(string):
    for i in range(len(string)):
        for j in range(i, len(string)):
            substring = string[i:j + 1]
            if len(substring) > 1:
                yield substring


def palindrome_substrings(string):
    return (i for i in substrings(string) if is_palindrome(i))


if __name__ == '__main__':
    palindromes = palindrome_substrings(DEFAULT_TEXT)

    for palindrome in palindromes:
        print(palindrome)
