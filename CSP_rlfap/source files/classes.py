class VARIABLE :
    
    def __init__(self, variable, domain, constraints):
        self.id : int = variable[0]
        self.domain_id : int = variable[1]
        self.domain_size : int = domain[1]
        self.domain : list = [VALUE(value, -1, 1) for value in domain[2:]]
        self.constraints : list = [constraint for constraint in constraints if self.id in [constraint.xi, constraint.xj]]
        self.assign : VALUE = None
        self.depth : set = set()
        self.checked_values : set = set()
        self.wdeg : float = 0.0
        self.activity : float = 0.0
        self.ddeg : float = 0.0
        self.Pbefore : float = 0.0
        self.actdom : float = 0.0
        self.impact : float = 0.0

    def getDomain(self) : return [value for value in self.domain if value.state]

    def getDeletedDomain(self) : return [value for value in self.domain if not value.state]

    def getID(self) : return self.id
    
    def getConstraints(self, Solution, Vars) :
        from operator import methodcaller
        return [(constraint, Vars[constraint.xi if self.id != constraint.xi else constraint.xj]) for constraint in self.constraints if not any(x in list(map(methodcaller('getID'), Solution)) for x in [constraint.xi, constraint.xj])]
    
    def DeleteValue(self, value, depth, heuristic) :
        if depth not in self.depth and depth > -1:
            if heuristic == 4 or heuristic == 6: self.activity += 1
            self.depth.add(depth)
        value.depth, value.state = depth, 0

    def Reset(self, Depth) :
        if Depth in self.depth :
            [value.reset() for value in self.getDeletedDomain() if Depth == value.depth]
            if self.assign : self.assign.reset()
            self.depth.remove(Depth)

    def Assign(self, Depth, heuristic, choice = 0, Vars = None) :
        if heuristic == 5 or heuristic == 6 : self.Pbefore = self.GetP(Vars)
        if self.assign : choice = (self.getDomain().index(self.assign) + 1)
        self.assign = None
        for value in self.getDomain()[choice:]:
            self.assign = value
            self.assign.depth = Depth
            [self.DeleteValue(val, Depth, heuristic) for val in self.getDomain() if val != self.assign]
            break
        return self.assign

    def RandomAssign(self, Depth, heuristic) :
        free = set(self.getDomain()) - self.checked_values
        self.assign = None
        if free :
            from random import choice
            self.assign = choice([*free])
            self.assign.depth = Depth
            [self.DeleteValue(val, Depth, heuristic) for val in self.getDomain() if val != self.assign]
            self.checked_values.add(self.assign)
        return self.assign

    def ALLReset(self) :
        [value.reset() for value in self.getDeletedDomain()]
        if self.assign : self.assign.reset()
        self.depth, self.checked_values, self.assign = set(), set(), None
        
    def getDomainSize(self) :
        self.domain_size = len(self.getDomain())
        return self.domain_size

    def FindWDeg(self, Vars) :
        self.wdeg = 0
        for constraint in self.constraints :
            x = Vars[constraint.xi if self.id != constraint.xi else constraint.xj]
            if not x.assign :
                self.wdeg += constraint.weight
        self.wdeg = float('inf') if self.wdeg == 0 else len(self.getDomain())/self.wdeg
        return self.wdeg
    
    def FindDDeg(self, Vars) :
        self.ddeg = 0
        for constraint in self.constraints :
            x = Vars[constraint.xi if self.id != constraint.xi else constraint.xj]
            if not x.assign : self.ddeg += 1
        self.ddeg = float('inf') if self.ddeg == 0 else len(self.getDomain())/self.ddeg
        return self.ddeg

    def GetActivity(self) :
        size = len(self.getDomain())
        self.actdom = (self.activity/size) if size else float('inf')
        return self.actdom

    def GetP(self, Vars, P = 1) :
        for var in Vars :
            P*= var.getDomainSize()
        return P

    def GetImpact(self, I = 0) :
        for value in self.getDomain(): I+= 1 - value.meanImpact()
        self.impact = I
        return self.impact

    def getOrder(self): return (self.GetImpact(), self.getDomainSize())

    def getWDEGOrder(self) : return self.wdeg

    def __str__(self): return "x{} -> {}".format(self.id, self.assign.value)

class CONSTRAINT :

    def __init__(self, constraint) :
        self.constraint = constraint if len(constraint) == 4 else constraint + ["0"]
        self.xi : int = int(constraint[0]) if len(constraint) > 1 else None
        self.xj : int = int(constraint[1]) if len(constraint) > 1 else None
        self.weight : int = 1

    def __str__(self) :
        return "constraint : {}\nWeight : {}".format(self.constraint, self.weight)

class VALUE :

    def __init__(self, value, depth, state) :
        self.value : int = value
        self.depth : int = depth
        self.state : int = state
        self.checked : int = 0
        self.impacts : list = []

    def meanImpact(self) :
        if not self.checked and len(self.impacts) > 1:
            self.impacts.pop(0)
            self.checked = 1
        return sum(self.impacts)/len(self.impacts)

    def reset(self) :
        self.depth = -1
        self.state = 1

    def __str__(self) :
        return "value: {} - depth: {} - state: {}".format(self.value, self.depth, self.state)
