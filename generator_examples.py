#!/usr/bin/env python3


def countdown():
  i=5
  while i > 0:
    yield i
    i -= 1


for i in countdown():
  print(i)


# Result:
#
# >>>
# 5
# 4
# 3
# 2
# 1


# Another example.


def numbers(x):
  for i in range(x):
    if i % 2 == 0:
      yield i


print(list(numbers(11)))


# Result:
#
# >>>
# [0, 2, 4, 6, 8, 10]
