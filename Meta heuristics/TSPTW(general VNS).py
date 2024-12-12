
import random
import time

def TSPTW_cost(input:tuple, path:list, return_to_0=False):
    N, e, l, d, t = input
    total_time = 0
    path = [0] + [item for item in path]
    e = [None] + e
    l = [None] + l
    d = [0] + d
    travel_cost = 0
    for i in range(N):
        total_time += d[path[i]] + t[path[i]][path[i+1]]
        total_time = max(total_time, e[path[i+1]])
        travel_cost += t[path[i]][path[i+1]]
        if total_time > l[path[i+1]]:
            return None
        
    if return_to_0:
        travel_cost += t[path[-1]][0]
    return travel_cost

def inp():
    N = int(input()) # number of customers, not including starting point 
    e = []
    l = []
    d = []
    for _ in range(N):
        a,b,c = map(int,input().split())
        e.append(a)
        l.append(b)
        d.append(c)
    t = []
    for _ in range(N+1):
        t.append(list(map(int,input().split())))
    return N, e, l, d, t


class Solver:
  def __init__(self, N, e, l, d, t):
      self.N = N
      self.e = [0] + e
      self.l = [0] + l
      self.d = [0] + d
      self.t = t
      self.compatible = self.check_compatible()

  def check_compatible(self):
    compatible = [[True] * (self.N + 1) for _ in range(self.N + 1)]
    for i in range(self.N + 1):
        for j in range(self.N + 1):
            if i == j or (self.e[i] + self.d[i] + self.t[i][j]) > self.l[j]:
                compatible[i][j] = False
    return compatible

  def CheckFeasible(self, x: list): # x: a solution
    if x == None:
        return False
    y={0:0,} # y: arrival time
    s = 0
    for i in x:
        y_i = max(y[s], self.e[s])+ self.d[s]+ self.t[s][i]
        if y_i> self.l[i]:
            return False
        else:
            s=i
            y[i] = y_i
    return True

  def CheckViolation(self, x):
    e = self.e
    d = self.d
    t = self.t
    l = self.l
    violated_nodes = []
    unviolated_nodes = []
    y={0:0,}
    s=0
    for i in x:
        y_i = max(y[s],e[s])+d[s]+t[s][i]
        s=i
        y[i]=y_i
        if y_i > l[i]:
          violated_nodes.append(i)
        else:
          unviolated_nodes.append(i)
    return violated_nodes, unviolated_nodes

  def FeasibleFunc(self, x: list):
      e = self.e
      d = self.d
      t = self.t
      l = self.l
      y={0:0,} # y: arrival time
      i = 0
      s=0
      for j in x:
          y[j] = max(y[i],e[i])+d[i]+t[i][j]
          s += max(0,y[j]-l[j])
          i=j
      return s

  def Local1Shift(self, x: list, current_obj):
      violated_nodes, unviolated_nodes = self.CheckViolation(x)
      for i in violated_nodes:
          i_pos = x.index(i)
          for position in list(range(0, i_pos)): # backward movements of violated customers
              if not self.compatible[i][x[position]]:
                continue
              neighbor = x.copy()
              neighbor.remove(i)
              neighbor.insert(position,i)
              if self.FeasibleFunc(neighbor) < current_obj:
                  return neighbor
      for i in unviolated_nodes:
          for position in list(range(x.index(i)+1,len(x)+1)): # forward movements of non-violated customers
              if not self.compatible[x[position-1]][i]:
                continue
              neighbor = x.copy()
              neighbor.remove(i)
              neighbor.insert(position,i)
              if self.FeasibleFunc(neighbor) < current_obj:
                  return neighbor
      for i in unviolated_nodes:
          for position in list(range(0,x.index(i))): # backward movements of non-violated customers
              if not self.compatible[i][x[position]]:
                continue
              neighbor = x.copy()
              neighbor.remove(i)
              neighbor.insert(position,i)
              if self.FeasibleFunc(neighbor) < current_obj:
                  return neighbor
      for i in violated_nodes:
          for position in list(range(x.index(i)+1,len(x)+1)): # forward movements of violated customers
              if not self.compatible[x[position-1]][i]:
                continue
              neighbor = x.copy()
              neighbor.remove(i)
              neighbor.insert(position,i)
              if self.FeasibleFunc(neighbor) < current_obj:
                  return neighbor
      return x

  def Pertubation(self, x, level):
      new_sol = x.copy()
      for _ in range(level):
          i,j = random.sample(range(len(new_sol)),2)
          new_sol[i], new_sol[j] = new_sol[j], new_sol[i]
      return new_sol

  def Solve_VNS(self, level_max, itermax):
    level = 1
    iter = 0
    x = random.sample(list(range(1,N+1)),N) # random initial solution
    x_cost = self.FeasibleFunc(x)
    while (level <= level_max):
        x1 = self.Pertubation(x, level)
        x1_cost = self.FeasibleFunc(x1)
        x1 = self.Local1Shift(x1, x1_cost)
        if  x1_cost < x_cost:
            x=x1
            x_cost = x1_cost
            level=1
        else:
            if iter > itermax:
                level+=1
                iter = 0
        iter += 1
    return x

  def VNS(self, level_max, iterMax):
    x = sorted(list(range(1,self.N+1)), key = lambda i: self.l[i])
    iter = 0
    while not (self.CheckFeasible(x) or iter > iterMax):   
      x = self.Solve_VNS(level_max, iterMax)
      iter += 1
    if not self.CheckFeasible(x):
      x = sorted(list(range(1,N+1)), key = lambda i: self.e[i])
      iter = 0
      while not (self.CheckFeasible(x) or iter > iterMax):   
        x = self.Solve_VNS(level_max, iterMax)
        iter += 1
    return x

  def GVNS(self, x, levelMax, iterMax, maxTime):
    ''' x: a feasible solution'''
    start = time.time()
    level = 1
    best_cost = self.ObjFunc(x)
    x = self.VND(x, iterMax)
    iter = 0
    while level <= levelMax and iter <= iterMax:
      iter += 1
      x0 = self.Pertubation(x, level)
      x0 = self.VND(x0, iterMax)
      x0_cost = self.ObjFunc(x0)
      if x0_cost != None:
        if x0_cost < best_cost:
          level = 1
          best_cost = x0_cost
          x = x0
      else:
          level+=1
    return x

  def ObjFunc(self, x: list):
    value = TSPTW_cost((self.N, self.e[1:], self.l[1:], self.d[1:], self.t), x)
    return value

  def VND(self, x, iterMax):
    x1 = None
    iter = 0
    while x != x1 and iter <= iterMax:
      x = self.Local1ShiftOpti(x)
      x1 = x.copy()
      x = self.Local2Opt(x)
      iter += 1
    return x.copy()

  def Local1ShiftOpti(self, x):
      violated_nodes, unviolated_nodes = self.CheckViolation(x)
      t = self.t
      compatible = self.compatible
      for i in violated_nodes:
          i_pos = x.index(i)
          if i_pos == 0:
            continue
          for position in list(range(0, i_pos)): # backward movements of violated customers
              if position != 0:
                if i_pos == N-1:
                  delta = - t[x[position-1]][x[position]] - t[x[i_pos-1]][i] + t[x[position-1]][i] + t[i][x[position]]
                  check = (compatible[x[position-1]][i]  and compatible[i][x[position]])
                else:
                  delta = - t[x[position-1]][x[position]] - t[x[i_pos-1]][i] - t[i][x[i_pos+1]] + t[x[position-1]][i] + t[i][x[position]] + t[x[i_pos -1]][x[i_pos+1]]
                  check = (compatible[x[position-1]][i]  and compatible[i][x[position]] and compatible[x[i_pos -1]][x[i_pos+1]])
              else:
                if i_pos == N-1:
                  delta = - t[x[i_pos-1]][i] + t[i][x[position]] 
                  check = compatible[i][x[position]]
                else:
                  delta = - t[x[i_pos-1]][i] - t[i][x[i_pos+1]] + t[i][x[position]] + t[x[i_pos -1]][x[i_pos+1]]
                  check = (compatible[i][x[position]] and compatible[x[i_pos -1]][x[i_pos+1]])
              if not (check and delta < 0):
                continue
              neighbor = x.copy()
              neighbor.remove(i)
              neighbor.insert(position,i)
              if self.CheckFeasible(neighbor):
                  return neighbor
      for i in unviolated_nodes:
          i_pos = x.index(i)
          if i_pos == N-1:
            continue
          for position in list(range(i_pos+1,N+1)): # forward movements of non-violated customers
              if position != N:
                if i_pos == 0:
                  delta =  - t[i][x[i_pos+1]] - t[x[position-1]][x[position]] + t[x[position-1]][i] + t[i][x[position]]
                  check = (compatible[x[position-1]][i] and compatible[i][x[position]])
                else:
                  delta =  - t[x[i_pos-1]][i] - t[i][x[i_pos+1]] - t[x[position-1]][x[position]] + t[x[i_pos-1]][x[i_pos+1]] + t[x[position-1]][i] + t[i][x[position]]
                  check = (compatible[x[i_pos-1]][x[i_pos+1]] and compatible[x[position-1]][i] and compatible[i][x[position]])
              else:
                if i_pos == 0:
                  delta =  - t[i][x[i_pos+1]] + t[x[position-1]][i]
                  check = compatible[x[position-1]][i]
                else:
                  delta =  - t[x[i_pos-1]][i] - t[i][x[i_pos+1]] + t[x[i_pos-1]][x[i_pos+1]] + t[x[position-1]][i]
                  check = (compatible[x[i_pos-1]][x[i_pos+1]] and compatible[x[position-1]][i])
              if not (check and delta < 0):
                continue
              neighbor = x.copy()
              neighbor.remove(i)
              neighbor.insert(position,i)
              if self.CheckFeasible(neighbor):
                  return neighbor
      for i in unviolated_nodes:
          i_pos = x.index(i)
          if i_pos == 0:
            continue
          for position in list(range(0, i_pos)): # backward movements of unviolated customers
              if position != 0:
                if i_pos == N-1:
                  delta = 0 - t[x[position-1]][x[position]] - t[x[i_pos-1]][i] + t[x[position-1]][i] + t[i][x[position]]
                  check = (compatible[x[position-1]][i]  and compatible[i][x[position]])
                else:
                  delta = 0 - t[x[position-1]][x[position]] - t[x[i_pos-1]][i] - t[i][x[i_pos+1]] + t[x[position-1]][i] + t[i][x[position]] + t[x[i_pos -1]][x[i_pos+1]]
                  check = (compatible[x[position-1]][i]  and compatible[i][x[position]] and compatible[x[i_pos -1]][x[i_pos+1]])
              else:
                if i_pos == N-1:
                  delta = 0 - t[x[i_pos-1]][i] + t[i][x[position]] 
                  check = compatible[i][x[position]]
                else:
                  delta = 0 - t[x[i_pos-1]][i] - t[i][x[i_pos+1]] + t[i][x[position]] + t[x[i_pos -1]][x[i_pos+1]]
                  check = (compatible[i][x[position]] and compatible[x[i_pos -1]][x[i_pos+1]])
              if not (check and delta < 0):
                continue
              neighbor = x.copy()
              neighbor.remove(i)
              neighbor.insert(position,i)

              if self.CheckFeasible(neighbor):
                  return neighbor
      for i in violated_nodes:
          i_pos = x.index(i)
          if i_pos == N-1:
            continue
          for position in list(range(i_pos+1,N+1)): # forward movements of violated customers
              if position != N:
                if i_pos == 0:
                  delta =  - t[i][x[i_pos+1]] - t[x[position-1]][x[position]] + t[x[position-1]][i] + t[i][x[position]]
                  check = (compatible[x[position-1]][i] and compatible[i][x[position]])
                else:
                  delta =  - t[x[i_pos-1]][i] - t[i][x[i_pos+1]] - t[x[position-1]][x[position]] + t[x[i_pos-1]][x[i_pos+1]] + t[x[position-1]][i] + t[i][x[position]]
                  check = (compatible[x[i_pos-1]][x[i_pos+1]] and compatible[x[position-1]][i] and compatible[i][x[position]])
              else:
                if i_pos == 0:
                  delta =  - t[i][x[i_pos+1]] + t[x[position-1]][i]
                  check = compatible[x[position-1]][i]
                else:
                  delta =  - t[x[i_pos-1]][i] - t[i][x[i_pos+1]] + t[x[i_pos-1]][x[i_pos+1]] + t[x[position-1]][i]
                  check = (compatible[x[i_pos-1]][x[i_pos+1]] and compatible[x[position-1]][i])
              if not (check and delta < 0):
                continue
              neighbor = x.copy()
              neighbor.remove(i)
              neighbor.insert(position,i)
              if self.CheckFeasible(neighbor):
                  return neighbor
      return x.copy()
              
  def Local2Opt(self, x):
      x_copy = x.copy()
      n = self.N  
      compatible = self.compatible
      t = self.t
      for i in range(n - 1):
          for j in range(i + 2, n):
              if j != n - 1:
                  Delta = -t[x_copy[i]][x_copy[i + 1]] - t[x_copy[j]][x_copy[j + 1]] + t[x_copy[i]][x_copy[j]] + t[x_copy[i + 1]][x_copy[j + 1]]
                  check = compatible[x_copy[i]][x_copy[j]] and compatible[x_copy[i + 1]][x_copy[j + 1]]
              else:
                  Delta = -t[x_copy[i]][x_copy[i + 1]] + t[x_copy[i]][x_copy[j]]
                  check = compatible[x_copy[i]][x_copy[j]]

              if not (check and Delta >= 0):
                  continue

              path = self.do2Opt(x_copy, i, j)
              if self.CheckFeasible(path):
                return path
      return x_copy

  def do2Opt(self, x, i, j):
      path = x.copy()
      path[i + 1:j + 1] = reversed(path[i + 1:j + 1])
      return path

  def Solve(self, levelMax, iterMax, maxTime):
    start = time.time()
    iter = 0
    x_best = None
    min_cost = float('inf')
    while iter <= iterMax and time.time() - start <= maxTime:
      x = self.VNS(levelMax, iterMax)
      x_cost = self.ObjFunc(x)
      x0 = self.GVNS(x, levelMax, iterMax, maxTime)
      x0_cost = self.ObjFunc(x0)
      if x0_cost < x_cost:
        x_best = x0
        min_cost = x0_cost
      else:
        x_best = x
        min_cost = x_cost
      iter += 1
    runtime = time.time() - start
    if x_best != None:
      return x_best, min_cost, runtime
    else:
      if x == None:
        return 'None', 'None', 'None'
      else:
        return x, self.ObjFunc(x), runtime

if __name__ == '__main__':
  N, e, l, d, t =inp()
  s = Solver(N, e, l, d, t)
  if N < 300:
    levelMax, iterMax, maxTime = 8, 30, 180
  elif N >= 300 and N < 500:
    levelMax, iterMax, maxTime = 10, 10, 180
  elif N >= 500 and N < 1000:
    levelMax, iterMax, maxTime = 3, 3, 120
  else:
    levelMax, iterMax, maxTime = 3, 3, 60
  path, cost, runtime = s.Solve(levelMax, iterMax, maxTime)
  print(N)
  print(*path)
