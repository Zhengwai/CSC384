#Look for #IMPLEMENT tags in this file.
'''
All models need to return a CSP object, and a list of lists of Variable objects 
representing the board. The returned list of lists is used to access the 
solution. 

For example, after these three lines of code

    csp, var_array = futoshiki_csp_model_1(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the Futoshiki puzzle.

1. futoshiki_csp_model_1 (worth 20/100 marks)
    - A model of a Futoshiki grid built using only 
      binary not-equal constraints for both the row and column constraints.

2. futoshiki_csp_model_2 (worth 20/100 marks)
    - A model of a Futoshiki grid built using only n-ary 
      all-different constraints for both the row and column constraints. 

'''
from cspbase import *
import itertools

def futoshiki_csp_model_1(futo_grid):
    ##IMPLEMENT
    n = len(futo_grid)
    vars = []
    var_array = []
    ops = [[futo_grid[i][2*j+1] for j in range(n-1)] for i in range(n)]
    vals = [[futo_grid[i][2*j] for j in range(n)] for i in range(n)]
    all_dom = [i + 1 for i in range(n)]

    for i in range(n):
        row_vars = []
        for j in range(n):    
            if vals[i][j]  == 0:
                var = Variable("{}{}".format(i, j), all_dom)
            else:
                var = Variable("{}{}".format(i, j), [vals[i][j]])      
            row_vars.append(var)
            var_array.append(var)
        
        vars.append(row_vars)
    csp = CSP("{}x{} model 1 csp".format(n, n), var_array)
    for i in range(n):
        for j in range(n):
            for k in range(j+1, n):
                var1 = vars[i][j]
                var2 = vars[i][k]
                con = Constraint("{}{}{}{})".format(i,j,i,k), [var1, var2])

                dom1 = var1.cur_domain()
                dom2 = var2.cur_domain()
                tuples = []
                if k == j+1 and ops[i][j] == '>':
                    for item in itertools.product(dom1, dom2):
                        if item[0] > item[1]:
                            tuples.append(item)
                elif k == j+1 and ops[i][j] == '<':
                    for item in itertools.product(dom1, dom2):
                        if item[0] < item[1]:
                            tuples.append(item)
                else:
                    for item in itertools.product(dom1, dom2):
                        if item[0] != item[1]:
                            tuples.append(item)

                con.add_satisfying_tuples(tuples)
                csp.add_constraint(con)

                var1 = vars[j][i]
                var2 = vars[k][i]
                con = Constraint("{}{}{}{}".format(j,i,k,i), [var1, var2])
                dom1 = var1.cur_domain()
                dom2 = var2.cur_domain()
                tuples = []
                for item in itertools.product(dom1, dom2):
                        if item[0] != item[1]:
                            tuples.append(item)
                con.add_satisfying_tuples(tuples)
                csp.add_constraint(con)
    return csp, vars

def futoshiki_csp_model_2(futo_grid):
    ##IMPLEMENT 
    n = len(futo_grid)
    vars = []
    var_array = []
    ops = [[futo_grid[i][2*j+1] for j in range(n-1)] for i in range(n)]
    vals = [[futo_grid[i][2*j] for j in range(n)] for i in range(n)]
    all_dom = [i + 1 for i in range(n)]

    for i in range(n):
        row_vars = []
        for j in range(n):    
            if vals[i][j]  == 0:
                var = Variable("{}{}".format(i, j), all_dom)
            else:
                var = Variable("{}{}".format(i, j), [vals[i][j]])      
            row_vars.append(var)
            var_array.append(var)
        
        vars.append(row_vars)
    csp = CSP("{}x{} model 2 csp".format(n,n), var_array)

    for i in range(n):
        for j in range(n-1):
            if ops[i][j] == '>':
                var1 = vars[i][j]
                var2 = vars[i][j+1]
                con = Constraint("{}{}{}{})".format(i,j,i,j+1), [var1, var2])

                dom1 = var1.cur_domain()
                dom2 = var2.cur_domain()
                tuples = []
                for item in itertools.product(dom1, dom2):
                    if item[0] > item[1]:
                        tuples.append(item)
                con.add_satisfying_tuples(tuples)
                csp.add_constraint(con)
            if ops[i][j] == '<':
                var1 = vars[i][j]
                var2 = vars[i][j+1]
                con = Constraint("{}{}{}{})".format(i,j,i,j+1), [var1, var2])

                dom1 = var1.cur_domain()
                dom2 = var2.cur_domain()
                tuples = []
                for item in itertools.product(dom1, dom2):
                    if item[0] < item[1]:
                        tuples.append(item)
                con.add_satisfying_tuples(tuples)
                csp.add_constraint(con)


    for i in range(n):
        row_vars = vars[i]
        row_doms = []
        col_vars = []
        col_doms = []

        for j in range(n):
            row_doms.append(row_vars[j].cur_domain())
            col_vars.append(vars[j][i])
            col_doms.append(vars[j][i].cur_domain())
        
        
        col_con = Constraint("col{})".format(i), col_vars)

        col_tuples = []
        for item in itertools.product(*row_doms):
            if len(item) == len(set(item)):
                col_tuples.append(item)
        col_con.add_satisfying_tuples(col_tuples)
        csp.add_constraint(col_con)

        row_con = Constraint("row{})".format(i), row_vars)
        row_tuples = []
        for item in itertools.product(*row_doms):
            if not any(item.count(e) > 1 for e in item):
                row_tuples.append(item)
        row_con.add_satisfying_tuples(row_tuples)
        csp.add_constraint(row_con)

    return csp, vars

