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
        return self.precedence >= other.precedence

    def __eq__(self, other):
        if (isinstance(other, Operator)):
            return self.op == other.op
        if(isinstance(other, str)):
            return self.op == other
        return False

    def __repr__(self):
        return '{}:{} {}'.format(self.op, self.arity, self.precedence)

    def __str__(self):
        return '{}'.format(self.op)

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


def roll(s, modifiers=0, option='execute'):
    """Roll dice and do arithmetic."""
    # global operators

    operators = (Operator('d', 7, 2, roll_basic, 'l'),
                 Operator('da', 7, 2, roll_average, 'l'),
                 Operator('h', 6, 2, lambda x, y: x[-y:], 'r'),
                 Operator('l', 6, 2, lambda x, y: x[:y], 'r'),
                 Operator('r', 6, 2, reroll_once, 'r'),
                 Operator('R', 6, 2, reroll_unconditional, 'r'),
                 Operator('^', 5, 2, lambda x, y: x ** y, 'lr'),
                 Operator('m', 4, 1, lambda x: -x, 'r'),
                 Operator('p', 4, 1, lambda x: x, 'r'),
                 Operator('*', 3, 2, lambda x, y: x * y, 'lr'),
                 Operator('/', 3, 2, lambda x, y: x / y, 'lr'),
                 Operator('-', 2, 2, lambda x, y: x - y, 'lr'),
                 Operator('+', 2, 2, lambda x, y: x + y, 'lr'),
                 Operator('>', 1, 2, lambda x, y: x > y, 'lr'),
                 Operator('<', 1, 2, lambda x, y: x < y, 'lr'),
                 Operator('=', 1, 2, lambda x, y: x == y, 'lr'),
                 )

    if (isinstance(s, (float, int))):
        # If you're naughty and pass a number in...
        # it really doesn't matter.
        return s + modifiers
    elif (s == ''):
        return 0 + modifiers
    elif (option == 'execute'):
        return (execute(tokens(s, operators), operators) + modifiers)
    elif (option == 'max'):
        T = tokens(s, operators)
        for (i, item) in enumerate(T):
            if (item == 'd' or item == 'da'):
                if (len(T) >= i + 3 and (T[i + 2] == 'h' or T[i + 2] == 'l')):
                    T[i - 1:i + 4] = [T[i + 3], '*', T[i + 1]]
                else:
                    T[i] = '*'
        return execute(T, operators)
    elif (option == 'critical'):
        T = tokens(s, operators)
        for i in range(len(T)):
            if (T[i] == 'd'):
                T[i - 1] *= 2
        return (execute(T, operators) + modifiers)
    # elif (option == 'average'):
    #     return (execute(tokens(s, operators), av=True) + modifiers)
    elif (option == 'zero'):
        return 0
    # elif (option == 'multipass'):
    #     return displayMultipass(multipass(tokens(s), modifiers))
    elif (option == 'tokenize'):
        return tokens(s)


call = roll  # A hacky workaround for backwards compatibility


# def tokens(s, operators):
#     """Splt a string into rolling tokens"""
#     curr_num = []
#     curr_op = []
#     T = []
#     i = 0
#     numflag = s[0] in string.digits
#     opflag = s[0] in operators
#     while i < len(s):
#         char = s[i]
#


def tokens(s, operators):
    """Split a string into tokens for use with execute()"""
    curr_num = []
    curr_op = []
    T = []
    i = 0
    # booleans; whether a number or an operator is currently being processed
    numflag = s[0] in string.digits
    opflag = s[0] in operators
    while (i < len(s)):
        char = s[i]
        if (char in string.digits):
            if (opflag):
                op = string_to_operator(''.join(curr_op), operators)
                T.append(op)
                curr_op = []
                numflag = not numflag
                opflag = not opflag
            curr_num.append(char)
        elif (char in 'dahlrR^mp*/+-<>='):
            # This should definitely be more refined; it should filter to just valid characters while being straight up
            # elif (char in operators or char == '(' or char == ')'):
            if (numflag):
                T.append(int(''.join(curr_num)))
                curr_num = []
                numflag = not numflag
                opflag = not opflag
            if(char == '+' and (i == 0 or s[i - 1] in operators)):
                T.append(string_to_operator('p', operators))
            elif(char == '-' and (i == 0 or s[i - 1] in operators)):
                T.append(string_to_operator('m', operators))
            else:
                if (len(curr_op) == 0):
                    # This is the first time you see an operator since last time the list was cleared
                    curr_op.append(char)
                elif (''.join(curr_op + [char]) in operators):
                    # This means that the current char is part of a multicharacter operation like <=
                    curr_op.append(char)
                else:
                    # Two separate operators; push out the old one and start collecting the new one
                    op = string_to_operator(''.join(curr_op), operators)
                    T.append(op)
                    curr_op = [char]
        elif (char == '['):
            # Start a list of floats
            sidelist = []
            while (s[i] != ']'):
                sidelist.append(s[i])
                i += 1
            i += 1
            sidelist.append(s[i])
            T.append(read_list(''.join(sidelist)))
        elif (char == 'F'):
            # Fudge die
            T.append([-1, 0, 1])
        i += 1
    if (numflag):
        T.append(int(''.join(curr_num)))
    elif (opflag):
        T.append(''.join(operator))
    return T


def execute(T, operators):
    oper = []
    nums = []
    while (len(T) > 0):
        current = T.pop(0)
        if (type(current) is int or type(current) is list):
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


def deep_sum(l):
    s = 0
    for item in l:
        try:
            s += sum(item)
        except(TypeError):
            s += item
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


def roll_basic(number, sides):
    """Roll a single set of dice."""
    # Returns a sorted (ascending) list of all the numbers rolled
    result = Roll()
    result.die = sides
    result.discards = [[] for all in range(number)]
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
        return sides[random.randint(0, len(rollList) - 1)]


def roll_average(number, sides):
    val = Roll()
    val.die = sides
    val.discards = [[] for all in range(number)]
    if (isinstance(sides, list)):
        val.extend([sum(sides)/len(sides)]*number)
        # return (sum(sides) * number) / len(sides)
    else:
        val.extend([(sides+1)/2]*number)
        # return (1 + sides) * number / 2
    return val


def reroll_once(original, target):
    modified = original
    i = 0
    while i < len(original):
        if (modified[i] == target):
            modified.discards[i].append(modified[i])
            modified[i] = single_die(modified.die)
        i += 1
    modified.sort()
    return modified


def reroll_unconditional(original, target):
    modified = original
    i = 0
    while i < len(original):
        while (modified[i] == target):
            modified.discards[i].append(modified[i])
            modified[i] = single_die(modified.die)
        i += 1
    modified.sort()
    return modified

# def execute(T, av=False):
#     """Calculate a result from a list of tokens."""
#     oper = []
#     nums = []
#     while (len(T) > 0):
#         current = T.pop(0)
#         if (type(current) is int or type(current) is list):
#             nums.append(current)
#         elif (current == '('):
#             oper.append(current)
#         elif (current == ')'):
#             while (oper[-1] != '('):
#                 # Evaluate all extant expressions down to the open paren
#                 if (arity(oper[-1]) == 2):
#                     nums.append(evaluate(
#                         [nums.pop(-2), nums.pop()], oper.pop(), av))
#                 else:
#                     nums.append(unary(nums.pop(), oper.pop()))
#             oper.pop()  # Get rid of that last open paren
#         elif (current in operators):
#             try:
#                 while (oper[-1] >= current):
#                     if (arity(oper[-1]) == 2):
#                         nums.append(evaluate(
#                             [nums.pop(-2), nums.pop()], oper.pop(), av))
#                     else:
#                         nums.append(unary(nums.pop(), oper.pop()))
#             except (IndexError):
#                 pass
#             oper.append(current)
#             # or add a higher-precedence operator to the stack
#     while (len(oper) > 0):
#         # empty the operator stack
#         if (arity(oper[-1]) == 2):
#             nums.append(evaluate([nums.pop(-2), nums.pop()], oper.pop(), av))
#         else:
#             nums.append(unary(nums.pop(), oper.pop()))
#     try:
#         # collapse list of rolls if able
#         nums[0] = sum(nums[0])
#     except (TypeError):
#         pass
#     return sum(nums)


# def make_roll(lhs, rhs, average):
#     if (average):
#         if (isinstance(rhs, list)):
#             return (sum(rhs) * lhs) // len(rhs)
#         else:
#             return (1 + rhs) * lhs // 2
#     else:
#         return roll_basic(lhs, rhs)


# def evaluate(nums, op, av=False):
#     """Evaluate expressions."""
#     if (any(op == c for c in 'd^*/%+-><=')):
#         # collapse any lists in preparation for operation
#         try:
#             nums[0] = sum(nums[0])
#         except (TypeError):
#             pass
#
#     if (any(operators[3] == c for c in 'hl^*/%+-><=&|')):
#         try:
#             nums[1] = sum(nums[1])
#         except (TypeError):
#             pass
#
#     if (op == 'd'):
#         if (av):
#             if (type(nums[1]) is list):
#                 return (sum(nums[1]) * nums[0]) // len(nums[1])
#             else:
#                 return (1 + nums[1]) * nums[0] // 2
#         else:
#             return roll_basic(nums[0], nums[1])
#     elif (op == 'h'):
#         return nums[0][-nums[1]:]
#     elif (op == 'l'):
#         return nums[0][:nums[1]]
#     elif (op == '^'):
#         return nums[0]**nums[1]
#     elif (op == '*'):
#         return nums[0] * nums[1]
#     elif (op == '/'):
#         return nums[0] / nums[1]
#     elif (op == '%'):
#         return nums[0] % nums[1]
#     elif (op == '+'):
#         return nums[0] + nums[1]
#     elif (op == '-'):
#         return nums[0] - nums[1]
#     elif (op == '>'):
#         return nums[0] > nums[1]
#     elif (op == '<'):
#         return nums[0] < nums[1]
#     elif (op == '='):
#         return nums[0] == nums[1]
#     elif (op == '&'):
#         return nums[0] and nums[1]
#     elif (op == '|'):
#         return nums[0] or nums[1]


# def unary(num, op):
#     """Evaluate unary expressions."""
#     try:
#         num = sum(num)
#     except (TypeError):
#         pass
#     if (op == 'm'):
#         return -num
#     elif (op == 'p'):
#         return num


# def execute(T, av=False):
#     """Calculate a result from a list of tokens."""
#     oper = []
#     nums = []
#     while (len(T) > 0):
#         current = T.pop(0)
#         if (type(current) is int or type(current) is list):
#             nums.append(current)
#         elif (current == '('):
#             oper.append(current)
#         elif (current == ')'):
#             while (oper[-1] != '('):
#                 # Evaluate all extant expressions down to the open paren
#                 if (arity(oper[-1]) == 2):
#                     nums.append(evaluate(
#                         [nums.pop(-2), nums.pop()], oper.pop(), av))
#                 else:
#                     nums.append(unary(nums.pop(), oper.pop()))
#             oper.pop()  # Get rid of that last open paren
#         elif (current in operators):
#             try:
#                 while (oper[-1] >= current):
#                     if (arity(oper[-1]) == 2):
#                         nums.append(evaluate(
#                             [nums.pop(-2), nums.pop()], oper.pop(), av))
#                     else:
#                         nums.append(unary(nums.pop(), oper.pop()))
#             except (IndexError):
#                 pass
#             oper.append(current)
#             # or add a higher-precedence operator to the stack
#     while (len(oper) > 0):
#         # empty the operator stack
#         if (arity(oper[-1]) == 2):
#             nums.append(evaluate([nums.pop(-2), nums.pop()], oper.pop(), av))
#         else:
#             nums.append(unary(nums.pop(), oper.pop()))
#     try:
#         # collapse list of rolls if able
#         nums[0] = sum(nums[0])
#     except (TypeError):
#         pass
#     return sum(nums)


# def arity(op):
#     """Determine the arity of an operator."""
#     for this in operators:
#         if (this == op):
#             return this.arity
#     raise NotFoundError('Operator not valid')


# def multipass(T, modifiers=0):
#     # note: this does not yet support parentheses
#     passes = ["d", "hl", "^mp*/%+-", "><=&|"]
#     for run in passes:
#         for op in run:
#             while (T.count(op)):
#                 loc = T.index(op)
#                 if (arity[operators.index(op)] == 2):
#                     val = evaluate([T[loc - 1], T[loc + 1]], op)
#                     T[loc - 1:loc + 2] = [val]
#                     # this assignment only works when RHS is iterable
#                 else:
#                     val = unary(T[loc + 1], op)
#                     T[loc:loc + 2] = [val]
#             out.extend(['+' if modifiers >= 0 else '', modifiers])
#         out.append(T)
#     out.append(T[0])
#     # out should be of the form
#     # [[rolls have been made],
#     # [selected rolls have been discarded],
#     # [arithmetic but not boolean operators have been evaluated],
#     # final result]
#     return out


# def displayMultipass(l):
#     out = ['', '', '', '']
#     for (i, sec) in enumerate(l):
#         for token in sec:
#             out[i] += str(token)
#         out[i] += '\n'
#     return out


# class NotFoundError(Exception):
#     pass


if __name__ == '__main__':
    print(roll('1d4+(4+3)*2'))
    print(roll('1d4+4+3*2'))
    print(roll('1+3*2^1d4'))
    print(roll('4d6'))
    print(roll('1d2r1'))
    print(roll('1d2R1'))
    print(roll('2da6'))
