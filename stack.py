# This Python file uses the following encoding: utf-8
from collections import deque


class stack:
    def __init__(self):
        self.stack = deque()

    def empty(self):
        return len(self.stack) == 0

    def size(self):
        return len(self.stack)

    def top(self):
        return self.stack[-1]

    def push(self, stack_element):
        self.stack.append(stack_element)

    def pop(self):
        return self.stack.pop()

    def drop(self):
        while (self.size() != 0):
            self.stack.pop()
