#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports---i.e., ones that are automatically
#   available on TEACH.CS
#   You may not remove any imports.
#   You may not import or otherwise source any of your own 
import os #for time functions
from search import * #for search engines
from sokoban import SokobanState, Direction, PROBLEMS #for Sokoban specific classes and problems
import csv

def sokoban_goal_state(state):
  '''
  @return: Whether all boxes are stored.
  '''
  for box in state.boxes:
    if box not in state.storage:
      return False
  return True

def heur_manhattan_distance(state):
#IMPLEMENT
    '''admissible sokoban puzzle heuristic: manhattan distance'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    #We want an admissible heuristic, which is an optimistic heuristic.
    #It must never overestimate the cost to get from the current state to the goal.
    #The sum of the Manhattan distances between each box that has yet to be stored and the storage point nearest to it is such a heuristic.
    #When calculating distances, assume there are no obstacles on the grid.
    #You should implement this heuristic function exactly, even if it is tempting to improve it.
    #Your function should return a numeric value; this is the estimate of the distance to the goal.
    i = 0
    for box in state.boxes:
      j = float('inf')
      for area in state.storage:
        k = distance(area, box)
        if k < j:
          j = k
      i += j
    return i

#SOKOBAN HEURISTICS
def trivial_heuristic(state):
  '''trivial admissible sokoban heuristic'''
  '''INPUT: a sokoban state'''
  '''OUTPUT: a numeric value that serves as an estimate of the distance of the state (# of moves required to get) to the goal.'''
  count = 0
  for box in state.boxes:
    if box not in state.storage:
        count += 1
  return count

def unsettled_boxes(state):
  # return two sets, the unsettled boxes and unoccupied storage
  boxes = set(state.boxes)
  storage = set(state.storage)
  ints = boxes.intersection(storage)
  return boxes.difference(ints), storage.difference(ints)

def at_corner(state, box):
  #return True if the box is at one of the four corners
  return box == (0,0) or box == (state.width-1, state.height-1) or box == (state.width-1, 0) or box == (0, state.height-1)

def on_side(state, box):
  # return 0 if the box is on the left/right side
  # return 1 if the box is on the up/down side
  # return -1 otherwise
  if box[0] == 0 or box[0] ==state.width-1:
    return 0
  if box[1] == 0 or box[1] == state.height -1:
    return 1
  return -1

def is_trapped(state, box):
  if at_corner(state, box):
    return True # the box is trapped at a corner
  side = on_side(state, box)
  left = (box[0] - 1, box[1])
  right = (box[0] + 1, box[1])
  up = (box[0], box[1] - 1)
  down = (box[0], box[1] + 1)
  if side == -1: # the box is in the internal space
    if (is_obj(state, left) and is_obj(state, up)) or (is_obj(state, left) and is_obj(state, down)) or (is_obj(state, right) and is_obj(state, up)) or (is_obj(state, right) and is_obj(state, down)):
      return True # if the box is surrounded by objects on up/down and left/right, it's trapped
      # it works in most cases, but some optimal solutions may require the boxes to be clustered. Haven't figured out how to solve it
  elif side == 0: # the box is on the left/right side
    if is_obj(state, up) or is_obj(state, down):
      return True   #similar logic
    no_area = True
    for area in state.storage:
      if area[0] == box[0] and area not in state.boxes:
        no_area = False
    if no_area:
      return True #if there's no available storage place on the side the box is on, the box is trapped
  elif side == 1:
    if is_obj(state, left) or is_obj(state,right):
      return True
    no_area = True
    for area in state.storage:
      if area[1] == box[1] and area not in state.boxes:
        no_area = False
    if no_area:
      return True #if there's no available storage place on the side the box is on, the box is trapped
  return False

def is_obj(state, loc):
  #return true if the given loc is a box or an obstacle
  if loc in state.boxes or loc in state.obstacles:
    return True
  return False

def heur_alternate(state):
#IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    #heur_manhattan_distance has flaws.
    #Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    #Your function should return a numeric value for the estimate of the distance to the goal.
    boxes, storage = unsettled_boxes(state) # only consider the unsettled boxes and storage places
    i = 0
    temp = 0
    for box in boxes:
      if is_trapped(state, box): #check if the box is surrounded by objects (box, obstacles, borders)
       return float('inf')
      j = float('inf')
      for area in storage:
        d = distance(area, box)
        if d < j:
          j = d
          temp = area
      i += j
      storage.discard(temp) # once the box is assigned to a storage, the storage is discarded from the set. It makes boxes and storage
      #places 1-1.
    return i

def distance(t1, t2):
  return abs(t1[0]-t2[0]) + abs(t1[1]-t2[1])

def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def fval_function(sN, weight):
#IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.
    Use this function stub to encode the standard form of weighted A* (i.e. g + w*h)

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
  
    #Many searches will explore nodes (or states) that are ordered by their f-value.
    #For UCS, the fvalue is the same as the gval of the state. For best-first search, the fvalue is the hval of the state.
    #You can use this function to create an alternate f-value for states; this must be a function of the state and the weight.
    #The function must return a numeric f-value.
    #The value will determine your state's position on the Frontier list during a 'custom' search.
    #You must initialize your search engine object as a 'custom' search engine if you supply a custom fval function.
    return sN.gval + sN.hval * weight

def fval_function_XUP(sN, weight):
#IMPLEMENT
    """
    Another custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.
    Use this function stub to encode the XUP form of weighted A* 

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return (1/(2*weight))*(sN.gval + sN.hval + ((sN.gval+sN.hval)**2 + 4*weight*(weight-1)*(sN.hval**2))**0.5)

def fval_function_XDP(sN, weight):
#IMPLEMENT
    """
    A third custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.
    Use this function stub to encode the XDP form of weighted A* 

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return (1/(2*weight))*(sN.gval+(2*weight-1)*sN.hval+((sN.gval-sN.hval)**2+4*weight*sN.gval*sN.hval)**0.5)

def compare_weighted_astars():
#IMPLEMENT
    '''Compares various different implementations of A* that use different f-value functions'''
    '''INPUT: None'''
    '''OUTPUT: None'''
    """
    This function should generate a CSV file (comparison.csv) that contains statistics from
    4 varieties of A* search on 3 practice problems.  The four varieties of A* are as follows:
    Standard A* (Variant #1), Weighted A*  (Variant #2),  Weighted A* XUP (Variant #3) and Weighted A* XDP  (Variant #4).  
    Format each line in your your output CSV file as follows:

    A,B,C,D,E,F

    where
    A is the number of the problem being solved (0,1 or 2)
    B is the A* variant being used (1,2,3 or 4)
    C is the weight being used (2,3,4 or 5)
    D is the number of paths extracted from the Frontier (or expanded) during the search
    E is the number of paths generated by the successor function during the search
    F is the overall solution cost    

    Note that you will submit your CSV file (comparison.csv) with your code
    """
    functions = [fval_function, fval_function_XUP, fval_function_XDP]
    lines = []
    for i in range(0,3):
        se = SearchEngine('astar', 'full')
        problem = PROBLEMS[i]
        se.init_search(problem, sokoban_goal_state, heur_manhattan_distance)
        final, stats = se.search()
        if final:
          lines.append([i, 1, "N/A", stats.states_expanded, stats.states_generated, final.gval])
        se = SearchEngine('custom', 'full')
        for j in range(2,5):
          for weight in [2,3,4,5]:
            wrapped = (lambda sN: functions[j-2](sN, weight))
            se.init_search(problem, sokoban_goal_state, heur_manhattan_distance, wrapped)
            final, stats = se.search()
            if final:
              lines.append([i, j, weight, stats.states_expanded, stats.states_generated, final.gval])
    with open("comparison.csv", "w", newline='') as f:
      writer = csv.writer(f, delimiter=',')
      writer.writerow(["Problem", "A* variant", "Weight", "Expanded", "Generated", "Overall Solution Cost"])
      for line in lines:
        writer.writerow(line)    

def anytime_weighted_astar(initial_state, heur_fn, weight=1., timebound = 10):
#IMPLEMENT
  '''Provides an implementation of anytime weighted a-star, as described in the HW1 handout'''
  '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
  '''OUTPUT: A goal state (if a goal is found), else False'''
  '''implementation of weighted astar algorithm'''
  ti = os.times()[0]
  w = 5
  costbound = float('inf')
  state = None
  while os.times()[0] - ti < timebound-0.01:
    se = SearchEngine("custom", "full")
    wrapped = (lambda sN: fval_function(sN, w))
    se.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped)
    final, stats = se.search(timebound - (os.times()[0]-ti)-0.01, (costbound, costbound, costbound))
    if final:
      if final.gval < costbound:
        costbound = final.gval
        state = final
    w += 0.1
  if state:
    return state
  return False

def anytime_gbfs(initial_state, heur_fn, timebound = 10):
#IMPLEMENT
  '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
  '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
  '''OUTPUT: A goal state (if a goal is found), else False'''
  '''implementation of anytime greedy best-first search'''
  ti = os.times()[0]
  costbound = float('inf')
  state = None
  while os.times()[0] - ti < timebound-0.01:
    se = SearchEngine("best_first", "full")
    se.init_search(initial_state, sokoban_goal_state, heur_fn)
    final, stats = se.search(timebound - (os.times()[0]-ti)-0.01, (costbound, costbound, costbound))
    if final:
      if final.gval < costbound:
        costbound = final.gval
        state = final
  if state:
    return state
  return False
                        