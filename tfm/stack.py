# This Python file uses the following encoding: utf-8
from collections import deque


class stack:
    """
    Provides a classic stack using a deque() data structure.
    """

    def __init__(self):
        """
        Initializes the stack.
        """
        self.stack = deque()

    def empty(self) -> bool:
        """
        Returns True if stack is emtpy and False if it isn't.

        :return: Emptyness of the stack.
        :rtype: bool
        """
        return len(self.stack) == 0

    def size(self) -> int:
        """
        Returns the size of the stack.

        :return: Number of elements in the stack.
        :rtype: int
        """
        return len(self.stack)

    def top(self):
        """
        Returns the top element of the stack.

        :return: Top element of the stack.
        """
        return self.stack[-1]

    def push(self, stack_element):
        """
        Adds an element to the top of the stack.

        :param stack_element: The element which will be added to the stack.
        """
        self.stack.append(stack_element)

    def pop(self):
        """
        Removes and returns the top element of the stack.

        :return: Top element of the stack.
        """
        return self.stack.pop()

    def drop(self):
        """
        Resets the entire stack by removing all of its elements.
        """
        while (self.size() != 0):
            self.stack.pop()
