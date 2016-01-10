"""
Rolling
Version 1.0 (released 2016-01-09)
Direct all comments, suggestions, etc. at /u/the-nick-of-time

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
+4 					(positive four)
-2 					(negative two)
1d6 				(roll a six-sided die with sides numbered one through six)
-1d6				(roll a d6 and take the negative)
3d6+2				(roll 3d6 and add 2 to the sum)
1d6+1d4+1			(roll a d6, add to it a d4, and add one to that)
2d20h1+3+2			(roll 2d20, take the higher of the two rolls, add a total of five to it)
3d6/2				(roll 3d6, divide the sum by 2; note that this returns an unrounded number)
Less applicable functionalities:
1d6^2 				(roll a d6, square the result)
1d6^1d4				(roll a d6, raise it to a random power between 1 and 4)
1d4d4d4				(roll a d4, roll that many d4s, sum them and roll that many d4s)
1d[0,0,0,1,1,2]		(roll a six-sided die with three sides being 0, two 1, and one 2)
1d[.5,.33,.25,.20]	(roll a four-sided die with sides 0.5, 0.33, 0.25, and 0.2)
1d100>11			(roll a d100 and check whether the roll is greater than 11; returns a 1 for true and 0 for false)
3d4%5				(roll 3d4, return the remainder after division by 5)

"""

import random

def call(s,modifiers=0,option='execute'):
    #Merely a wrapper for the whole tokenization and parsing process
    #Defines or redefines the two reference strings so that everything will be
    #consistent
    global digits, operators, order
    digits='0123456789'
    #It is easier to have all of the operators in a single iterable for use with
    #the 'in' operator but ideally it would be organized like so:
    #HIGH   d
    #       h or l
    #       ^ (exponentiation)
    #       - or + (negative or positive sign)
    #       * or /
    #       + or -
    #LOW    > or < or = (boolean comparison operators)
    #Order is the number of inputs to the corresponding operator
    operators='dhl^mp*/%+-><=&|('
    order=[2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2]

    if(s==''):
        return 0+modifiers
    elif(option=='execute'):
        return (execute(tokens(s))+modifiers)
    elif(option=='max'):
        T=[('*' if item=='d' else item) for item in tokens(s)]
        return execute(T)
    elif(option=='critical'):
        T=tokens(s)
        for i in range(len(T)):
            if(T[i]=='d'):
                T[i-1]*=2
        return (execute(T)+modifiers)
    elif(option=='average'):
        return (execute(tokens(s),av=True)+modifiers)
    elif(option=='zero'):
        return 0
    elif(option=='multipass'):
        return displayMultipass(multipass(tokens(s),modifiers))
    elif(option=='tokenize'):
        return tokens(s)

def tokens(s):
    #Splits a string into a list of integers and operators
    #to be evaluated by execute()
    #The valid operators, in order of decreasing precedence, are defined in call()
    number=''
    out=[]
    i=0
    while(i<len(s)):
        char=s[i]
        if(char in digits):
            number+=char
        elif(char in operators or char==')'):
            if(s[i]=='-' and (i==0 or s[i-1] in operators)):
                out.append('m')
            elif(s[i]=='+' and (i==0 or s[i-1] in operators)):
                out.append('p')
            else:
                try:
                    #Turn the contents of the numbers string into an int
                    out.append(int(number))
                    number=''
                except(ValueError):
                    #often the numbers string is empty because of a leading (
                    pass
                out.append(char)
        elif(char=='['):
            i+=1
            ls=''
            while(s[i]!=']'):
                ls+=s[i]
                i+=1
            out.append(readList(ls))
        elif(char=='F'):
            out.append([-1,0,1])
        i+=1
    try:
        #push out the last number
        out.append(int(number))
    except(ValueError):
        pass
    return out

def readList(s,mode='float'):
    s=s.split(sep=',')
    out=[]
    for num in s:
        num=num.replace('[','')
        num=num.replace(']','')
        if(num):
            if(mode=='float'):
                num=float(num)
            elif(mode=='int'):
                num=int(num)
            out.append(num)
    return out

def rollBasic(number,sides):
    #Returns a sorted (ascending) list of all the numbers rolled
    result=[]
    rollList=[]
    if(type(sides) is int):
        rollList=list(range(1,sides+1))
    elif(type(sides) is list):
        rollList=sides
    for all in range(number):
        result.append(rollList[random.randint(0,len(rollList)-1)])
    result.sort()
    return result

def evaluate(nums,op,av=False):
    #Operator definitions (basically what 'nums' is allowed to be)
    #   d is defined for [int {d} int] or [int {d} [numeric list]]
    #   h and l are defined only for [[sorted numeric list] {h/l} int]
    #   the arithmetic operators can take anything, as they collapse any lists
    if(op in 'd^*/%+-><='):
        #collapse any lists in preparation for operation
        try:
            nums[0]=sum(nums[0])
        except(TypeError):
            pass

    if(op in 'hl^*/%+-><=&|'):
        try:
            nums[1]=sum(nums[1])
        except(TypeError):
            pass

    if(op=='d'):
        if(av):
            return (1+nums[1])*nums[0]//2
        else:
            return rollBasic(nums[0],nums[1])
    elif(op=='h'):
        return nums[0][-nums[1]:]
    elif(op=='l'):
        return nums[0][:nums[1]]
    elif(op=='^'):
        return nums[0]**nums[1]
    elif(op=='*'):
        return nums[0]*nums[1]
    elif(op=='/'):
        return nums[0]/nums[1]
    elif(op=='%'):
        return nums[0]%nums[1]
    elif(op=='+'):
        return nums[0]+nums[1]
    elif(op=='-'):
        return nums[0]-nums[1]
    elif(op=='>'):
        return nums[0]>nums[1]
    elif(op=='<'):
        return nums[0]<nums[1]
    elif(op=='='):
        return nums[0]==nums[1]
    elif(op=='&'):
        return nums[0] and nums[1]
    elif(op=='|'):
        return nums[0] or nums[1]

def unary(num,op):
    try:
        num=sum(num)
    except(TypeError):
        pass
    if(op=='m'):
        return -num
    elif(op=='p'):
        return num

def execute(T,av=False):
    oper=[]
    nums=[]
##    for current in T:
    while(len(T)>0):
        current=T.pop(0)
        if(type(current) is int or type(current) is list):
            nums.append(current)
        elif(current=='('):
            oper.append(current)
        elif(current==')'):
            while(oper[-1]!='('):
        #Evaluate all extant expressions down to the open paren
                if(order[operators.index(oper[-1])]==2):
                    nums.append(evaluate([nums.pop(-2),nums.pop()],oper.pop(),av))
                else:
                    nums.append(unary(nums.pop(),oper.pop()))
            oper.pop()   #Get rid of that last open paren
        elif(current in operators):
            try:
                while(operators.index(oper[-1])<=operators.index(current)):
                    #check precedence; lower index=higher precedence
                    #perform operation
                    if(order[operators.index(oper[-1])]==2):
                        nums.append(evaluate([nums.pop(-2),nums.pop()],oper.pop(),av))
                    else:
                        nums.append(unary(nums.pop(),oper.pop()))
            except(IndexError):
                pass
            oper.append(current)
            #or add a higher-precedence operator to the stack
    while(len(oper)>0):
        #empty the operator stack
        op=oper[-1]
        ind=operators.index(oper[-1])
        orde=order[ind]
        if(order[operators.index(oper[-1])]==2):
            nums.append(evaluate([nums.pop(-2),nums.pop()],oper.pop(),av))
        else:
            nums.append(unary(nums.pop(),oper.pop()))
    try:
        #collapse list of rolls if able
        nums[0]=sum(nums[0])
    except(TypeError):
        pass
    return sum(nums)

def multipass(T,modifiers=0):
    out=[]
    while True:
        try:
            #This rolls every d and overwrites the slot
            loc=T.index('d')
            T[loc]=rollBasic(T[loc-1],T[loc+1])
            del T[loc+1]
            del T[loc-1]
        except(ValueError):
            break
    out.append([T,'+',modifiers])
    while True:
        try:
            loc=T.index('h')
            T[loc]=T[loc-1][-T[loc+1]:]
            del T[loc+1]
            del T[loc-1]
        except(ValueError):
            try:
                loc=T.index('l')
                T[loc]=T[loc-1][:T[loc+1]]
                del T[loc+1]
                del T[loc-1]
            except(ValueError):
                break
    T.append(['+',modifiers])
    out.append(T)

    out.append(execute(T))
    # out should be of the form [[rolls have been made],[selected rolls have been discarded],final result]
    return out


def displayMultipass(l):
    return str(l[0])+'\n'+str(l[1])+'\n'+str(l[2])
