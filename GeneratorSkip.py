"""
This file hosts an algorithm for skipping entries at the beginning or the end of a iterable.
The iterable definition also includes generators, which is useful in our case.
I'm including this in a separate module because this way we can load it in everywhere without the copying and pasting.

This algorithm is made by Group AB-3 of the Faculty of Aerospace Engineering at TUD, 2018-2019
"""

# Import system modules:
import itertools as it
import collections as co


def skip(Arr, start=0, end=0):
	"""
	This function takes care of skipping a number of entries at the beginning or at the end of a generator.
	The normal [:] does not work because it is an generator after all.
	"""
	# Make the iterable ready to iterate:
	iterable = iter(Arr)

	# Iterate through the iterable for the first, unneeded entries.
	for x in it.islice(iterable, start):
		pass

	# Create a deque, because of speed and memory, to store the variables in.
	queque = co.deque(it.islice(iterable, end))

	# For every variable left in the iterable, after skipping the first few:
	for x in iterable:
		# Append it to the deque:
		queque.append(x)

		# Delete and yield the first value of the iterable:
		yield queque.popleft()
