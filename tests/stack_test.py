from tfm.stack import stack

from random import randint


def test_empty():
    test_stack = stack()

    assert(test_stack.empty())

    test_stack.push(1)
    assert(not test_stack.empty())


def test_size():
    test_stack = stack()

    assert(test_stack.size() == 0)

    pushed_numbers = randint(1, 20)
    for i in range(pushed_numbers):
        test_stack.push(i)
    assert(test_stack.size() == pushed_numbers)


def test_top():
    test_stack = stack()

    # assert(test_stack.top())
    test_stack.push(1)
    assert(test_stack.top() == 1)

    test_stack.push(2)
    assert(test_stack.top() == 2)


def test_push():
    test_stack = stack()

    test_stack.push(0)
    assert(test_stack.top() == 0)
    assert(test_stack.size() == 1)

    test_stack.push(1)
    assert(test_stack.top() == 1)
    assert(test_stack.size() == 2)


def test_pop():
    test_stack = stack()

    #test_stack.pop()

    test_stack.push(1)
    test_stack.push(5)
    assert(test_stack.pop() == 5)
    assert(test_stack.size() == 1)


def test_drop():
    test_stack = stack()

    test_stack.drop()
    assert(test_stack.empty())

    pushed_numbers = randint(10, 20)
    for i in range(pushed_numbers):
        test_stack.push(i)
    test_stack.drop()
    assert(test_stack.empty())
