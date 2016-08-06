"""
Rolling
Version 1.0 (released 2016-01-09)
Direct all comments, suggestions, etc. at /u/the-nick-of-time
Released under the GNU General Public License version 2, as detailed within
the file LICENSE included in the same directory as this code.

This module provides the framework for evaluating roll expressions. Basically,
it adds the capability to parse the operators 'd', 'h', and 'l'.The important
thing to note is that these are simply new binary operators.
The definitions of these operators are as follows:
xdy rolls x y-sided dice and returns a sorted list of these rolls.
    xd[a,b,c,...] rolls x dice with sides a,b,c....
xdyhz rolls x y-sided dice and returns the z highest of these rolls. This
    enables the advantage mechanic.
xdylz rolls x y-sided dice and returns the z lowest of these rolls. This
    enables the disadvantage mechanic.

Any string that can be parsed by this code is called throughout all my related
code a "rollable string". These are similar to arithmetic expressions, just with the above operators added.
Examples of rollable strings:
+4                  (positive four)
-2                  (negative two)
1d6                 (roll a six-sided die with sides numbered one through six)
-1d6                (roll a d6 and take the negative)
3d6+2               (roll 3d6 and add 2 to the sum)
1d6+1d4+1           (roll a d6, add to it a d4, and add one to that)
2d20h1+3+2          (roll 2d20, take the higher of the two rolls, add a total of five to it)
3d6/2               (roll 3d6, divide the sum by 2; note that this returns an unrounded number)
Less applicable functionalities:
1d6^2               (roll a d6, square the result)
1d6^1d4             (roll a d6, raise it to a random power between 1 and 4)
1d4d4d4             (roll a d4, roll that many d4s, sum them and roll that many d4s)
1d[0,0,0,1,1,2]     (roll a six-sided die with three sides being 0, two 1, and one 2)
1d[.5,.33,.25,.20]  (roll a four-sided die with sides 0.5, 0.33, 0.25, and 0.2)
1d100>11            (roll a d100 and check whether the roll is greater than 11; returns a 1 for true and 0 for false)
3d4%5               (roll 3d4, return the remainder after division by 5)

"""

import random
import string

__all__ = ['roll', 'call']


class operator:
    def __init__(self, op, precedence, arity, operation=None, cajole='lr'):
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
        if (isinstance(other, operator)):
            return self.op == other.op
        if(isinstance(other, str)):
            return self.op == other
        return False

    def __repr__(self):
        return '{}:{} {}'.format(self.op, self.arity, self.precedence)

    def op(self, nums):
        operands = nums[-self.arity:]
        del nums[-self.arity:]
        l = 0 if self.arity == 2 else None
        r = 1 if self.arity == 2 else 0
        if ('l' in self.cajole):
            operands[l] = sum(operands[l])
        if ('r' in self.cajole):
            operands[r] = sum(operands[r])
        nums.append(self.operation(*operands))
        return nums


def roll(s, modifiers=0, option='execute'):
    """Roll dice and do arithmetic."""
    global operators

    operators = (operator('d', 7, 2, rollBasic, 'l'),
                 operator('dav', 7, 2, rollAverage, 'l'),
                 operator('h', 6, 2, lambda x, y: x[-y:], 'r'),
                 operator('l', 6, 2, lambda x, y: x[:y], 'r'),
                 operator('^', 5, 2, lambda x, y: x**y, 'lr'),
                 operator('m', 4, 1, lambda x: -x, 'r'),
                 operator('p', 4, 1, lambda x: x, 'r'),
                 operator('*', 3, 2, lambda x, y: x*y, 'lr'),
                 operator('/', 3, 2, lambda x, y: x/y, 'lr'),
                 operator('-', 2, 2, lambda x, y: x-y, 'lr'),
                 operator('+', 2, 2, lambda x, y: x+y, 'lr'),
                 operator('>', 1, 2, lambda x, y: x>y, 'lr'),
                 operator('<', 1, 2, lambda x, y: x<y, 'lr'),
                 operator('=', 1, 2, lambda x, y: x == y, 'lr'),
                 )

    if (isinstance(s, float) or isinstance(s, int)):
        # If you're naughty and pass a number in...
        # it really doesn't matter.
        return s + modifiers
    elif (s == ''):
        return 0 + modifiers
    elif (option == 'execute'):
        return (execute(tokens(s)) + modifiers)
    elif (option == 'max'):
        T = tokens(s)
        for (i, item) in enumerate(T):
            if (item == 'd'):
                if (len(T) >= i + 3 and (T[i + 2] == 'h' or T[i + 2] == 'l')):
                    T[i - 1:i + 4] = [T[i + 3], '*', T[i + 1]]
                else:
                    T[i] = '*'
        return execute(T)
    elif (option == 'critical'):
        T = tokens(s)
        for i in range(len(T)):
            if (T[i] == 'd'):
                T[i - 1] *= 2
        return (execute(T) + modifiers)
    elif (option == 'average'):
        return (execute(tokens(s), av=True) + modifiers)
    elif (option == 'zero'):
        return 0
    # elif (option == 'multipass'):
    #     return displayMultipass(multipass(tokens(s), modifiers))
    elif (option == 'tokenize'):
        return tokens(s)


call = roll  # A hacky workaround for backwards compatibility

def tokens(s, av=False):
    """Split a string into tokens for use with execute()"""
    number = []
    operator = []
    out = []
    i = 0
    numflag = s[0] in string.digits
    opflag = s[0] in operators
    while (i < len(s)):
        char = s[i]
        if (char in string.digits):
            if (opflag):
                out.extend(operator)
                operator = []
                numflag = not numflag
                opflag = not opflag
            number.append(char)
        elif (char in operators or char == '(' or char == ')'):
            if (numflag):
                out.append(int(''.join(number)))
                number = []
                numflag = not numflag
                opflag = not opflag
            if(char == '+' and (i == 0 or s[i-1] in operators)):
                out.append(string_to_operator('p'))
            elif(char == '-' and (i == 0 or s[i-1] in operators)):
                out.append(string_to_operator('m'))
            else:
                operator.append(string_to_operator(char, av))
        elif (char == '['):
            sidelist = []
            while (s[i] != ']'):
                sidelist.append(s[i])
                i += 1
            i += 1
            sidelist.append(s[i])
            out.append(readList(''.join(sidelist)))
        elif (char == 'F'):
            out.append([-1, 0, 1])
        i += 1
    if (numflag):
        out.append(int(''.join(number)))
    elif (opflag):
        out.append(''.join(operator))
    return out


def string_to_operator(s, av=False):
    if (av and s == 'd'):
        s = 'dav'
    for op in operators:
        if (op == s):
            return op
    return s


def readList(s, mode='float'):
    """Read a list defined in a string."""
    if (mode == 'float'):
        return list(eval(s))
    elif (mode == 'int'):
        a = list(eval(s))
        return [int(item) for item in a]


def rollBasic(number, sides):
    """Roll a single set of dice."""
    #Returns a sorted (ascending) list of all the numbers rolled
    result = []
    rollList = []
    if (type(sides) is int):
        rollList = list(range(1, sides + 1))
    elif (type(sides) is list):
        rollList = sides
    for all in range(number):
        result.append(rollList[random.randint(0, len(rollList) - 1)])
    result.sort()
    return result

    
def rollAverage(number, sides):
    if (isinstance(sides, list)):
        return (sum(sides) * number) / len(sides)
    else:
        return (1 + sides) * number / 2


def make_roll(lhs, rhs, average):
    if (average):
        if (isinstance(rhs, list)):
            return (sum(rhs) * lhs) // len(rhs)
        else:
            return (1 + rhs) * lhs // 2
    else:
        return rollBasic(lhs, rhs)


def evaluate(nums, op, av=False):
    """Evaluate expressions."""
    if (any(op == c for c in 'd^*/%+-><=')):
        #collapse any lists in preparation for operation
        try:
            nums[0] = sum(nums[0])
        except (TypeError):
            pass

    if (any(operators[3] == c for c in 'hl^*/%+-><=&|')):
        try:
            nums[1] = sum(nums[1])
        except (TypeError):
            pass

    if (op == 'd'):
        if (av):
            if (type(nums[1]) is list):
                return (sum(nums[1]) * nums[0]) // len(nums[1])
            else:
                return (1 + nums[1]) * nums[0] // 2
        else:
            return rollBasic(nums[0], nums[1])
    elif (op == 'h'):
        return nums[0][-nums[1]:]
    elif (op == 'l'):
        return nums[0][:nums[1]]
    elif (op == '^'):
        return nums[0]**nums[1]
    elif (op == '*'):
        return nums[0] * nums[1]
    elif (op == '/'):
        return nums[0] / nums[1]
    elif (op == '%'):
        return nums[0] % nums[1]
    elif (op == '+'):
        return nums[0] + nums[1]
    elif (op == '-'):
        return nums[0] - nums[1]
    elif (op == '>'):
        return nums[0] > nums[1]
    elif (op == '<'):
        return nums[0] < nums[1]
    elif (op == '='):
        return nums[0] == nums[1]
    elif (op == '&'):
        return nums[0] and nums[1]
    elif (op == '|'):
        return nums[0] or nums[1]


def unary(num, op):
    """Evaluate unary expressions."""
    try:
        num = sum(num)
    except (TypeError):
        pass
    if (op == 'm'):
        return -num
    elif (op == 'p'):
        return num


def execute(T, av=False):
    """Calculate a result from a list of tokens."""
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
                #Evaluate all extant expressions down to the open paren
                if (arity(oper[-1]) == 2):
                    nums.append(evaluate(
                        [nums.pop(-2), nums.pop()], oper.pop(), av))
                else:
                    nums.append(unary(nums.pop(), oper.pop()))
            oper.pop()  #Get rid of that last open paren
        elif (current in operators):
            try:
                while (oper[-1] >= current):
                    if (arity(oper[-1]) == 2):
                        nums.append(evaluate(
                            [nums.pop(-2), nums.pop()], oper.pop(), av))
                    else:
                        nums.append(unary(nums.pop(), oper.pop()))
            except (IndexError):
                pass
            oper.append(current)
            #or add a higher-precedence operator to the stack
    while (len(oper) > 0):
        #empty the operator stack
        if (arity(oper[-1]) == 2):
            nums.append(evaluate([nums.pop(-2), nums.pop()], oper.pop(), av))
        else:
            nums.append(unary(nums.pop(), oper.pop()))
    try:
        #collapse list of rolls if able
        nums[0] = sum(nums[0])
    except (TypeError):
        pass
    return sum(nums)

def arity(op):
    """Determine the arity of an operator."""
    for this in operators:
        if (this == op):
            return this.arity
    raise NotFoundError('Operator not valid')

def multipass(T, modifiers=0):
    # note: this does not yet support parentheses
    passes = ["d", "hl", "^mp*/%+-", "><=&|"]
    for run in passes:
        for op in run:
            while (T.count(op)):
                loc = T.index(op)
                if (arity[operators.index(op)] == 2):
                    val = evaluate([T[loc - 1], T[loc + 1]], op)
                    T[loc - 1:loc + 2] = [val]
                    #this assignment only works when RHS is iterable
                else:
                    val = unary(T[loc + 1], op)
                    T[loc:loc + 2] = [val]
            out.extend(['+' if modifiers >= 0 else '', modifiers])
        out.append(T)
    out.append(T[0])
    # out should be of the form
    # [[rolls have been made],
    # [selected rolls have been discarded],
    # [arithmetic but not boolean operators have been evaluated],
    # final result]
    return out


def displayMultipass(l):
    out = ['', '', '', '']
    for (i, sec) in enumerate(l):
        for token in sec:
            out[i] += str(token)
        out[i] += '\n'
    return out


class NotFoundError(Exception):
    pass


if __name__ == '__main__':
    #print(roll('1d4+(4+3)*2'))
    #print(roll('1d4+4+3*2'))
    print(roll('1+3*2^1d4'))
