from collections import deque, Counter
from itertools import combinations
from time import monotonic
from datetime import timedelta
from classes import *
from random import choice
from operator import methodcaller, itemgetter
##################################################################################
def REVISE (ctr, xj, xi, depth, heuristic, DELETE = 0, symbol = {'=' : '==', '>' : '>', '<' : '<', '<>' : '!='}) :
    for valj in xj.getDomain() :
        if not any(eval(str(abs(valj.value - vali.value)) + symbol[ctr[2]] + ctr[3]) for vali in xi.getDomain()) : DELETE = not (xj.domain.remove(valj) if depth < 0 else xj.DeleteValue(valj, depth, heuristic))
    return DELETE
##################################################################################
def AC3 (X, depth, Solution, heuristic, Q = None, var = None, result  = 1) :
    pop, append = Q.popleft, Q.appendleft
    while Q and result:
        xi = pop()
        for constraint, xj in xi.getConstraints(Solution, X) :
            if REVISE (constraint.constraint, xj, xi, depth, heuristic) :
                if not xj.getDomain() : constraint.weight, result = constraint.weight + 1, 0
                elif xj not in set(Q) : append(xj)
    if var and heuristic >= 5 : var.assign.impacts.append(1-var.GetP(X)/var.Pbefore)
    return result
##################################################################################
def READ_FILE(dom_file, var_file, ctr_file, dom_list = None, var_list = None, con_list = None):
    with open(dom_file, 'r') as DOM,  open(var_file, 'r') as VAR, open(ctr_file, 'r') as CON:
        dom_list = [list(map(int,domain.split())) for domain in DOM][1:]
        var_list = [list(map(int,variable.split())) for variable in VAR][1:]
        con_list = [CONSTRAINT(constraint.split()) for constraint in CON][1:]
    return [VARIABLE(var, dom_list[var[1]], con_list) for var in var_list]

def DOMAIN(Free, Vars, depth, r = 1, k = 1, counter_heuristic = {}, counter_times = {}, counter_choice = {}, ALL = 0):
    if Free :
        Free.sort(key=methodcaller('getDomainSize'))
        return Free[:k] if ALL else [choice(Free[:k]), depth + 1]
    else : return [] if ALL else [0, depth + 1]

def DOM_DDEG(Free, Vars, depth, r = 1, k = 1, counter_heuristic = {}, counter_times = {}, counter_choice = {}, ALL = 0) :
    if Free :
        Free.sort(key=methodcaller('FindDDeg', Vars))
        return Free[:k] if ALL else [choice(Free[:k]), depth + 1]
    else : return [] if ALL else [0, depth + 1]

def DOM_WDEG(Free, Vars, depth, r = 1, k = 1, counter_heuristic = {}, counter_times = {}, counter_choice = {}, ALL = 0) :
    from random import choice
    from operator import methodcaller
    if Free :
        Free.sort(key=methodcaller('FindWDeg', Vars))
        return Free[:k] if ALL else [choice(Free[:k]), depth + 1]
    else : return [] if ALL else [0, depth + 1]

def ACTIVITY(Free, Vars, depth, r = 1, k = 1, counter_heuristic = {}, counter_times = {}, counter_choice = {}, ALL = 0) :
    if Free :
        if r < 1 :
            for var in Free :
                if var.getDomainSize() > 1 : var.activity *= r
        Free.sort(key=methodcaller('GetActivity'), reverse = True)
        return Free[:k] if ALL else [choice(Free[:k]), depth + 1]
    else : return [] if ALL else [0, depth + 1]        

def IMPACT(Free, Vars, depth, r = 1, k = 1, counter_heuristic = {}, counter_times = {}, counter_choice = {}, ALL = 0) :
    if Free :
        Free.sort(key=methodcaller('getOrder'), reverse = True)
        return Free[:k] if ALL else [choice(Free[:k]), depth + 1]
    else : return [] if ALL else [0, depth + 1]

def Probing(Vars : list, depth : int, heuristic : int, probes : int = 0) :
    for i in range(probes) :
        choosen, depth, Solution = choice(Vars), depth + 1, set()
        while choosen :
            if choosen.RandomAssign(depth, heuristic) :
                if AC3(Vars, depth, Solution, 4, deque([choosen])) :
                    Solution.add(choosen)
                    free = set(Vars) - Solution
                    if free : choosen, depth = choice([*free]), depth + 1
                    else : return 1   
                else :
                    if depth == 0 : choosen.domain.remove(choosen.assign)
                    [v.Reset(depth) for v in set(Vars) - Solution if depth in v.depth]
            else : break
        for v in Vars : v.ALLReset()
    return 0

def ImpactInit(Vars, s = 0) :
    for var in Vars:
        DOMAIN = var.getDomain()
        size, s = len(DOMAIN), 1
        for i in range(0,size) :
            if 2 <= size/(2 ** i) : s = int(size/(2 ** i)) if s <= size/(2 ** i) < (s + 0.5) else int(round(size/(2 ** i))) 
            else : break
        for index in range(0, size, s):
            var.Pbefore = var.GetP(Vars)
            if not var.Pbefore : return 0
            var.assign = DOMAIN[index]
            var.assign.checked = 1
            [var.DeleteValue(val, 0, 5) for val in var.domain if val != var.assign and val.state]
            if not AC3(Vars, 0, set(), 5, deque([var]), var) : var.domain.remove(var.assign)
            for value in DOMAIN[index + 1 : index+s] : value.impacts.append(var.assign.impacts[0])
            for v in Vars : v.ALLReset()
    return 1

def COMMON_CHOICE(Free, Vars, depth, r = 1, k = 1, counter_heuristic = {}, counter_times = {}, counter_choice = {}) :
    Best_Vars, HEURISTICS_VARS, sign, SAME_CHOICE, flag = [], [], [], 0, 0
    for heuristic in [DOM_DDEG, DOM_WDEG, ACTIVITY, IMPACT] :
        HEURISTICS_VARS.append(heuristic(Free, Vars, depth, r, k, ALL = 1))
        Best_Vars += HEURISTICS_VARS[-1]
    if Best_Vars :
        Best_Vars = sorted(Counter(Best_Vars).items(), key=itemgetter(1), reverse = True)
        counter_times[max(dict(Best_Vars).values())] += 1
        max_times = Best_Vars[0][1]
        Best_Vars = sorted([var for var, times in Best_Vars if Best_Vars[0][1] == times], key = methodcaller('getWDEGOrder'))
        choosen = choice([var for var in Best_Vars if Best_Vars[0].wdeg == var.wdeg]) if max_times == 1 else choice(Best_Vars)
        for index, HEURISTIC in enumerate(HEURISTICS_VARS, 2) :
            if choosen in HEURISTIC :
                sign.append(index)
                if not SAME_CHOICE :
                    SAME_CHOICE = HEURISTIC.index(choosen)
                    flag = 1
                elif SAME_CHOICE != HEURISTIC.index(choosen) and flag:
                    counter_choice["NSR"] += 1
                    flag = 0
        if flag : counter_choice[SAME_CHOICE + 1] += 1
        counter_heuristic[tuple(sign)] += 1
        return choosen, depth + 1
    else : return 0, depth + 1

heuristics = {1 : DOMAIN, 2 : DOM_DDEG, 3 : DOM_WDEG, 4 : ACTIVITY, 5 : IMPACT, 6 : COMMON_CHOICE}
##################################################################################
def MAC(heuristic = 0, Vars = [], depth = -1, Solution = [], choosen = None, r = 1, nodes = 0, probes = 0, function = None, k = 1) :
    counter_times = {1 : 0, 2 : 0, 3 : 0, 4 : 0}
    counter_heuristic = dict(zip(list(combinations(range(2,6), 1)) + list(combinations(range(2,6), 2)) + list(combinations(range(2,6), 3)) + list(combinations(range(2,6), 4)), [0]*15))
    counter_choice = dict(zip(list(range(1,(k + 1))) + ["NSR"], [0]*(k + 1)))
    if AC3(Vars, depth, set(), heuristic, deque(Vars)) :
        if heuristic == 4 or heuristic == 6:
            if Probing(Vars, depth, heuristic, probes) : return [len(Vars), "SUCCESS (Probing)", 0, {}, {}, {}]
        if heuristic == 5 or heuristic == 6:
            if not ImpactInit(Vars) : return [0, "FAIL (Impact Init.)", 0, {}, {}, {}]
        INIT = monotonic()
        choosen, depth = function(list(set(Vars) - set(Solution)), Vars, depth, r, k, counter_heuristic, counter_times, counter_choice)
        while choosen :
            if choosen.Assign(depth, heuristic, Vars = Vars) :
                nodes += 1
                if AC3(Vars, depth, Solution, heuristic, deque([choosen]), choosen) :
                    Solution.append(choosen)
                    choosen, depth = function(list(set(Vars) - set(Solution)), Vars, depth, r, k, counter_heuristic, counter_times, counter_choice)
                    continue
            else :
                if monotonic() - INIT >= 3600 : return [nodes, None, monotonic() - INIT, counter_times, counter_heuristic, counter_choice]
                if Solution : choosen, depth = Solution.pop(), depth - 1
                else : return [nodes, "FAIL", monotonic() - INIT, counter_times, counter_heuristic, counter_choice]
            [v.Reset(depth) for v in set(Vars) - set(Solution) if depth in v.depth]
        return [nodes, "SUCCESS", monotonic() - INIT, counter_times, counter_heuristic, counter_choice]
    else : return [nodes, "FAIL", 0, counter_times, counter_heuristic, counter_choice]
