import random
import string

__all__ = ['roll', 'call']


class Operator:
    def __init__(self, op, precedence, arity, operation=None, cajole='lr'):
        # op: string
        # precedence: integer
        # arity: integer; 1 or 2 for unary/binary operators
        #   unary are necessarily prefix and binary are necessarily infix
        # operation: function
        # cajole: string; contains 'l', 'r' to convert that argument to a
        #   number
        self.op = op
        self.precedence = precedence
        self.arity = arity
        self.operation = operation
        self.cajole = cajole

    def __ge__(self, other):
        if (isinstance(other, str)):
            return True
        return self.precedence >= other.precedence

    def __le__(self, other):
        if (isinstance(other, str)):
            return False
        return self.precedence <= other.precedence

    def __lt__(self, other):
        if (isinstance(other, str)):
            return False
        return self.precedence < other.precedence

    def __eq__(self, other):
        if (isinstance(other, Operator)):
            return self.op == other.op
        if(isinstance(other, str)):
            return self.op == other
        return False

    def __repr__(self):
        return '{}:{} {}'.format(self.op, self.arity, self.precedence)

    def __str__(self):
        return self.op

    def __call__(self, nums):
        operands = nums[-self.arity:]
        del nums[-self.arity:]
        # index of the left and right arguments to the operator
        l = 0 if self.arity == 2 else None
        r = 1 if self.arity == 2 else 0
        if ('l' in self.cajole):
            try:
                operands[l] = sum(operands[l])
            except(TypeError):
                pass
        if ('r' in self.cajole):
            try:
                operands[r] = sum(operands[r])
            except(TypeError):
                pass
        nums.append(self.operation(*operands))
        return nums


class Roll(list):
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        self.die = 0
        self.discards = []

    def __str__(self):
        rolls = ', '.join([str(item) for item in self])
        discards = ', '.join([str(item) for item in self.discards])
        formatstr = '[d{die}: {rolls}; ({discards})]' if discards else '[d{die}: {rolls}]'
        return formatstr.format(die=str(self.die), rolls=rolls, discards=discards)

    def __repr__(self):
        return self.__str__()

    # def __add__(self, other):
    #     return Result(rolls=[self]) + other
    #
    # def __sub__(self, other):
    #     return Result(rolls=[self]) - other


# class Result:
#     def __init__(self, initial=0, rolls=[]):
#         # self.tokens = tokens
#         self.rolls = rolls
#         self.value = initial
#         self.constants = 0
#
#     def __str__(self):
#         rolls = '+'.join([str(item) for item in self.rolls])
#         # mod = self.constants
#         # return '{} + {}'.format(rolls, mod)
#         return '{}+{}={}'.format(rolls, self.constants, self.value)
#
#     def __add__(self, other):
#         # print(self, other)
#         if (isinstance(other, Roll)):
#             self.rolls.append(other)
#             self.value += sum(other)
#         elif (isinstance(other, list)):
#             self.value += sum(other)
#             self.constants += other.constants
#         elif (isinstance(other, Result)):
#             self.rolls.extend(other.rolls)
#             self.constants += other.constants
#             self.value += other.value
#         else:
#             self.constants += other
#             self.value += other
#         return self
#
#     def __radd__(self, other):
#         return self.__add__(other)
#
#     def __sub__(self, other):
#         if (isinstance(other, Roll))
#
#     def __repr__(self):
#         return self.__str__()
#
#     def __int__(self):
#         return self.value


def roll(s, modifiers=0, option='execute'):
    """Roll dice and do arithmetic."""
    # global operators

    operators = (Operator('d', 7, 2, roll_basic, 'l'),
                 Operator('da', 7, 2, roll_average, 'l'),
                 Operator('dc', 7, 2, roll_critical, 'l'),
                 Operator('dm', 7, 2, roll_max, 'l'),
                 Operator('h', 6, 2, take_high, 'r'),
                 Operator('l', 6, 2, take_low, 'r'),
                 Operator('f', 6, 2, floor_val, 'r'),
                 Operator('c', 6, 2, ceil_val, 'r'),
                 Operator('r', 6, 2, reroll_once_on, 'r'),
                 Operator('R', 6, 2, reroll_unconditional_on, 'r'),
                 Operator('r<', 6, 2, reroll_once_lower, 'r'),
                 Operator('R<', 6, 2, reroll_unconditional_lower, 'r'),
                 Operator('rl', 6, 2, reroll_once_lower, 'r'),
                 Operator('Rl', 6, 2, reroll_unconditional_lower, 'r'),
                 Operator('r>', 6, 2, reroll_once_higher, 'r'),
                 Operator('R>', 6, 2, reroll_unconditional_higher, 'r'),
                 Operator('rh', 6, 2, reroll_once_higher, 'r'),
                 Operator('Rh', 6, 2, reroll_unconditional_higher, 'r'),
                 Operator('^', 5, 2, lambda x, y: x ** y, 'lr'),
                 Operator('m', 4, 1, lambda x: -x, 'r'),
                 Operator('p', 4, 1, lambda x: x, 'r'),
                 Operator('*', 3, 2, lambda x, y: x * y, 'lr'),
                 Operator('/', 3, 2, lambda x, y: x / y, 'lr'),
                 Operator('%', 3, 2, lambda x, y: x % y, 'lr'),
                 Operator('-', 2, 2, lambda x, y: x - y, 'lr'),
                 Operator('+', 2, 2, lambda x, y: x + y, 'lr'),
                 Operator('>', 1, 2, lambda x, y: x > y, 'lr'),
                 Operator('gt', 1, 2, lambda x, y: x > y, 'lr'),
                 Operator('>=', 1, 2, lambda x, y: x >= y, 'lr'),
                 Operator('ge', 1, 2, lambda x, y: x >= y, 'lr'),
                 Operator('<', 1, 2, lambda x, y: x < y, 'lr'),
                 Operator('lt', 1, 2, lambda x, y: x < y, 'lr'),
                 Operator('<=', 1, 2, lambda x, y: x <= y, 'lr'),
                 Operator('le', 1, 2, lambda x, y: x <= y, 'lr'),
                 Operator('=', 1, 2, lambda x, y: x == y, 'lr'),
                 Operator('|', 1, 2, lambda x, y: x or y, 'lr'),
                 Operator('&', 1, 2, lambda x, y: x and y, 'lr'),
                 )

    if (isinstance(s, (float, int))):
        # If you're naughty and pass a number in...
        # it really doesn't matter.
        return s + modifiers
    elif (s == ''):
        return 0 + modifiers
    elif (option == 'execute'):
        return execute(tokens(s, operators), operators) + modifiers
    elif (option == 'critical'):
        T = tokens(s, operators)
        T = critify(T, operators)
        return execute(T, operators) + modifiers
    elif (option == 'average'):
        T = tokens(s, operators)
        T = averageify(T, operators)
        return execute(T, operators) + modifiers
    elif (option == 'multipass'):
        import re
        pattern = '\(.*\)'
        rep = lambda m: str(roll(m.group(0)))
        new = re.sub(pattern, rep, s)
        T = tokens(new, operators)
        if (modifiers):
            T.append(string_to_operator('+', operators))
            T.append(modifiers)
        return display_multipass(T, operators)
    elif (option == 'multipass_critical'):
        # TODO: add modifiers into the passes
        import re
        pattern = '\(.*\)'
        rep = lambda m: str(roll(m.group(0)))
        new = re.sub(pattern, rep, s)
        T = tokens(s, operators)
        T = critify(T, operators)
        if (modifiers):
            T.append(string_to_operator('+'))
            T.append(modifiers)
        return display_multipass(T, operators)
    elif (option == 'tokenize'):
        return tokens(s)
    elif (option == 'from_tokens'):
        return execute(s)
    elif (option == 'zero'):
        return 0


call = roll  # A hacky workaround for backwards compatibility


def tokens(s, operators):
    """Split a string into tokens for use with execute()"""
    # Every character that could be part of an operator
    possibilities = ''.join([str(item) for item in operators])
    curr_num = []
    curr_op = []
    T = []
    i = 0
    while (i < len(s)):
        char = s[i]
        if (char in string.digits):
            if (curr_op):
                op = string_to_operator(''.join(curr_op), operators)
                T.append(op)
                curr_op = []
            curr_num.append(char)
        elif (char in possibilities or char in '()'):
            # Things that will end up on the operators stack
            # elif (char in operators or char == '(' or char == ')'):
            if (curr_num):
                T.append(int(''.join(curr_num)))
                curr_num = []
            if(char == '+' and (i == 0 or s[i - 1] in possibilities + '(')):
                T.append(string_to_operator('p', operators))
                curr_op = []
            elif(char == '-' and (i == 0 or s[i - 1] in possibilities + '(')):
                T.append(string_to_operator('m', operators))
                curr_op = []
            else:
                if (len(curr_op) == 0):
                    # This is the first time you see an operator since last
                    # time the list was cleared
                    curr_op.append(char)
                elif (''.join(curr_op + [char]) in operators):
                    # This means that the current char is part of a
                    # multicharacter operation like <=
                    curr_op.append(char)
                else:
                    # Two separate operators; push out the old one and start
                    # collecting the new one
                    op = string_to_operator(''.join(curr_op), operators)
                    T.append(op)
                    curr_op = [char]
        elif (char == '['):
            if (curr_op):
                T.append(string_to_operator(''.join(curr_op), operators))
                curr_op = []
            # Start a list of floats
            sidelist = []
            while (s[i] != ']'):
                sidelist.append(s[i])
                i += 1
            sidelist.append(s[i])
            T.append(read_list(''.join(sidelist)))
        elif (char == 'F'):
            if (curr_op):
                T.append(string_to_operator(''.join(curr_op), operators))
                curr_op = []
            # Fudge die
            T.append([-1, 0, 1])
        i += 1
    if (curr_num):
        T.append(int(''.join(curr_num)))
    elif (curr_op):
        T.append(''.join(curr_op))
    return T


def execute(T, operators):
    oper = []
    # nums = [Result()]
    nums = []
    while (len(T) > 0):
        current = T.pop(0)
        if (isinstance(current, (int, list))):
            nums.append(current)
        elif (current == '('):
            oper.append(current)
        elif (current == ')'):
            while (oper[-1] != '('):
                # Evaluate all extant expressions down to the open paren
                oper[-1](nums)
                oper.pop()
            oper.pop()  # Get rid of that last open paren
        elif (current in operators):
            try:
                # Evaluate all higher-precedence operations first
                while (oper[-1] >= current):
                    oper[-1](nums)
                    oper.pop()
            except (IndexError):
                # Operators stack is empty
                pass
            # Then push the current operator to the stack
            oper.append(current)
    while (len(oper) > 0):
        # Empty the operators stack
        oper[-1](nums)
        oper.pop()
    return deep_sum(nums)


def deep_sum(l, starting=0):
    s = starting
    for item in l:
        try:
            s += item
        except (TypeError):
            s += deep_sum(item)
    return s


def string_to_operator(s, operators):
    for op in operators:
        if (op == s):
            return op
    return s


def read_list(s, mode='float'):
    """Read a list defined in a string."""
    if (mode == 'float'):
        return list(eval(s))
    elif (mode == 'int'):
        a = list(eval(s))
        return [int(item) for item in a]


def critify(T, operators):
    # Note: crit is superseded by maximum
    # Though why you're using roll_max anyway is a mystery
    for (i, item) in enumerate(T):
        if (item == 'd' or item == 'da'):
            T[i] = string_to_operator('dc', operators)
    return T

def averageify(T, operators):
    # Note: average is superseded by crit or max
    for (i, item) in enumerate(T):
        if (item == 'd'):
            T[i] = string_to_operator('da', operators)
    return T

def maxify(T, operators):
    # Max supersedes all
    for (i, item) in enumerate(T):
        if (item == 'd' or item == 'da' or item == 'dc'):
            T[i] = string_to_operator('dm', operators)
    return T


#### Rolling functions ####


def take_low(roll, number):
    if (len(roll) > number):
        n = len(roll) - number
        roll.discards.extend(roll[-n:])
        del roll[-n:]
    return roll


def take_high(roll, number):
    if (len(roll) > number):
        n = len(roll) - number
        roll.discards.extend(roll[:n])
        del roll[:n]
    return roll


def roll_basic(number, sides):
    """Roll a single set of dice."""
    # Returns a sorted (ascending) list of all the numbers rolled
    result = Roll()
    result.die = sides
    # result.discards = [[] for all in range(number)]
    rollList = []
    for all in range(number):
        result.append(single_die(sides))
    result.sort()
    return result


def single_die(sides):
    """Roll a single die."""
    if (type(sides) is int):
        return random.randint(1, sides)
    elif (type(sides) is list):
        return sides[random.randint(0, len(sides) - 1)]


def roll_critical(number, sides):
    """Roll double the normal number of dice."""
    # Returns a sorted (ascending) list of all the numbers rolled
    result = Roll()
    result.die = sides
    # result.discards = [[] for all in range(number)]
    rollList = []
    for all in range(2*number):
        result.append(single_die(sides))
    result.sort()
    return result


def roll_max(number, sides):
    """Roll double the normal number of dice."""
    # Returns a sorted (ascending) list of all the numbers rolled
    result = Roll()
    result.die = sides
    # result.discards = [[] for all in range(number)]
    rollList = []
    if (isinstance(sides, list)):
        result.extend([max(sides) for all in range(number)])
    else:
        result.extend([sides for all in range(number)])
    return result


def roll_average(number, sides):
    val = Roll()
    val.die = sides
    # val.discards = [[] for all in range(number)]
    if (isinstance(sides, list)):
        val.extend([sum(sides)/len(sides)]*number)
        # return (sum(sides) * number) / len(sides)
    else:
        val.extend([(sides+1)/2]*number)
        # return (1 + sides) * number / 2
    return val


def reroll_once(original, target, comp):
    modified = original
    i = 0
    while i < len(original):
        if (comp(modified[i], target)):
            modified.discards.append(modified[i])
            modified[i] = single_die(modified.die)
        i += 1
    modified.sort()
    return modified


def reroll_unconditional(original, target, comp):
    modified = original
    i = 0
    while i < len(original):
        while (comp(modified[i], target)):
            modified.discards.append(modified[i])
            modified[i] = single_die(modified.die)
        i += 1
    modified.sort()
    return modified


def reroll_once_on(original, target):
    return reroll_once(original, target, lambda x, y: x == y)


def reroll_once_higher(original, target):
    return reroll_once(original, target, lambda x, y: x > y)


def reroll_once_lower(original, target):
    return reroll_once(original, target, lambda x, y: x < y)


def reroll_unconditional_on(original, target):
    return reroll_unconditional(original, target, lambda x, y: x == y)


def reroll_unconditional_higher(original, target):
    return reroll_unconditional(original, target, lambda x, y: x > y)


def reroll_unconditional_lower(original, target):
    return reroll_unconditional(original, target, lambda x, y: x < y)


def floor_val(original, bottom):
    modified = original
    i = 0
    while i < len(original):
        if (modified[i] < bottom):
            modified.discards[i].append(modified[i])
            modified[i] = bottom
        i += 1
    modified.sort()
    return modified


def ceil_val(original, top):
    modified = original
    i = 0
    while i < len(original):
        if (modified[i] > top):
            modified.discards[i].append(modified[i])
            modified[i] = top
        i += 1
    modified.sort()
    return modified


### Multipass ###

def multipass(T, operators):
    out = [T]
    working = T.copy()
    pmax = max(operators).precedence
    pmin = min(operators).precedence
    for p in range(max(operators).precedence, min(operators).precedence-1, -1):
        i = 0
        while (i < len(working)):
            if (isinstance(working[i], Operator) and working[i].precedence == p):
                # Take the operator and adjacent numbers according to the arity
                if (working[i].arity == 1):
                    # perform the operation
                    # push back into the correct location within the token list
                    working[i] = working[i]([working.pop(i+1)])
                elif (working[i].arity == 2):
                    # perform the operation
                    # push back into the correct location within the token list
                    op = working[i]
                    nums = [working.pop(i-1), working.pop(i)]
                    r = op(nums)
                    working[i-1] = r[0]
                    i -= 1
            i += 1
        out.append(working.copy())
    out.append(deep_sum(out[-1], 0))
    return out


class MultipassResult:
    def __init__(self, passes, ops):
        self.ops = ops
        self.postrolls = passes[2]
        self.final = passes[-1]

    def __str__(self):
        r = ''.join([str(item) for item in self.postrolls])
        t = str(self.final)
        return r + ' = ' + t

    def __int__(self):
        return self.passes[-1]

    def __eq__(self, other):
        if (isinstance(other, int)):
            return self.final == other
        else:
            return self is other

    def __add__(self, other):
        if (isinstance(other, MultipassResult)):
            self.postrolls.append(string_to_operator('+', self.ops))
            self.postrolls.extend(other.postrolls)
            self.final += other.final
            return self
        elif (isinstance(other, int)):
            self.postrolls.append(string_to_operator('+', self.ops))
            self.postrolls.append(other)
            self.final += other
            return self

    def __format__(self, arg):
        # does not respond to format specification yet
        return str(self)


def display_multipass(T, operators):
    result = multipass(T, operators)
    # selections = (2, -1)
    # out = []
    # for i in selections[:-1]:
    #     out.append(''.join([str(item) for item in result[i]]))
    # out.append(str(result[selections[-1]]))
    # return '\n'.join(out)
    return MultipassResult(result, operators)


### Tests ###

if __name__ == '__main__':
    print(roll('3d4', option='multipass'))
    print(roll('1d4+2', option='multipass'))
    print(roll('8d4ro1+2', modifiers=5, option='multipass'))
    print(roll('1d4+2'))
    print(roll('2d20h1+1'))
    print(roll('2d20h1+1d4'))
    print(roll('1d4+(4+3)*2'))
    print(roll('1d4+4+3*2'))
    print(roll('1+3*2^1d4'))
    print(roll('4d6'))
    print(roll('1d2ro1'))
    print(roll('1d2Ro1'))
    print(roll('2da6'))
    print(roll('1d[1,1,1,1,1,6]'))
    print(roll('1da[1,1,1,1,1,6]'))
    print(roll('1da[2,2,3,4,5,6]-1da6'))
    print(roll('-1d4'))
