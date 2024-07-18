# Nick Chu DeChristofaro and Prathit Kurup 
# PA5 Interpreter
from __future__ import division
import sys
import copy
from collections import namedtuple

# Using named tuples to represent Cool classes, attributes, and methods
CoolClass = namedtuple("CoolClass", "Name Inherits Features")
Attribute = namedtuple("Attribute", "Name Type Initializer") 
Method = namedtuple("Method", "Name Formals ReturnType Body")


# A Cool Identifier is a tuple (pair) of a location and a string.
ID = namedtuple("ID", "loc str") 
Formal = namedtuple("Formal", "Name Type")

# Cool Values

# Kinds of Expressions
Identifier = namedtuple("Identifier", "Var StaticType")
Integer = namedtuple("Integer", "Integer StaticType") 
String = namedtuple("String", "String StaticType")
Plus = namedtuple("Plus", "Left Right StaticType") 
While = namedtuple("While", "Predicate Body StaticType") 
Minus = namedtuple("Minus", "Left Right StaticType")
Times = namedtuple("Times", "Left Right StaticType")
Divide = namedtuple("Divide", "Left Right StaticType")
Lt = namedtuple("Lt", "Left Right StaticType")
Le = namedtuple("Le", "Left Right StaticType")
Eq = namedtuple("Eq", "Left Right StaticType")
Not = namedtuple("Not", "Exp StaticType")
Negate = namedtuple("Negate", "Exp StaticType")
IsVoid = namedtuple("IsVoid", "Exp StaticType")
New = namedtuple("New", "Type StaticType")
true = namedtuple("true", "Value StaticType")
false = namedtuple("false", "Value StaticType")
Block = namedtuple("Block", "Body StaticType")
If = namedtuple("If", "Predicate Then Else StaticType")
Dynamic_Dispatch = namedtuple("Dynamic_Dispatch", "Exp Method Args StaticType")
Static_Dispatch = namedtuple("Static_Dispatch", "Exp Type Method Args StaticType")
Self_Dispatch = namedtuple("Self_Dispatch", "Method Args StaticType")
Assign = namedtuple("Assign", "Var Exp StaticType")
Let = namedtuple("Let", "Bindings Body StaticType")
Let_No_Init = namedtuple("Let_No_Init", "Var Type")
Let_Init = namedtuple("Let_Init", "Var Type Exp")
Case = namedtuple("Case", "Exp Elements StaticType")
Case_element = namedtuple("Case_element", "Var Type Body StaticType")
# New for PA5: we need to also keep track of internals
Internal = namedtuple("Internal", "Body StaticType")

lines = [] 
act_recs = 0 # keep track of activation records

# Cool Values
class Cool_Object:
    def __init__(self, class_name):
        self.type = class_name
        self.attributes = {}
    
    def add_attr(self, attr_name, loc):
        self.attributes[attr_name] = loc

    def __str__(self):
        return (f"{self.type}({str(self.attributes)})")
    
class Cool_Int:
    def __init__(self, class_name, integer):
        self.type = class_name
        self.integer = integer
        self.attributes = {}

    def __str__(self):
        return (f"{self.type}({str(self.integer)})")

class Cool_String:
    def __init__(self, class_name, len, str):
        self.type = class_name
        self.length = len
        self.string = str
        self.attributes = {}

    def __str__(self):
        return (f"{self.type}({str(self.length)}, {self.string})")

class Cool_Bool:
    def __init__(self, class_name, bool):
        self.type = class_name
        self.bool = bool
        self.attributes = {}

    def __str__(self):
        return (f"{self.type}({str(self.bool)})")

# Structure to hold information about the Interpreter's environment
class Environment:
    def __init__(self):
        # We use a dictionary to map variable names to locations
        self.env = {}
        self.next_loc = 0

    def update(self, id, loc):
        self.env[id] = loc
    
    def extend(self):
        return copy.deepcopy(self)

    # Check whether var in environment
    def lookup(self, id):
        if id in self.env: 
            return self.env[id]
        else:
            print(f"Variable {id} not in environment")
            exit(1)

    def __str__(self) -> str:
        return str(self.env)

# Structure to hold information about the Interpreter's store
class Store:
    def __init__(self):
        # We use a dictionary to map locations to values
        self.store = {}
        self.next_loc = 0

    def newloc(self):
        loc = self.next_loc
        self.next_loc += 1
        return loc

    def update(self, loc, value):
        self.store[loc] = value

    def lookup(self, loc):
        if loc in self.store:
            return self.store[loc]
        else:
            print(f"Location {loc} not in store")
            exit(1)
    
    def lookup_val(self, val):
        for loc in self.store:
            if self.store[loc] == val: return loc
        print(f"Value not in store")
        exit(1)

    def __str__(self) -> str:
        return str(self.store)

# This follows a similar structure to the OCaml video code for PA4. 
def main(): 
    # We need to set the recursion limit higher than the default
    sys.setrecursionlimit(20000)
    global lines
    fname = sys.argv[1] 
    with open(fname) as file:
        lines = [line.rstrip("\r\n") for line in file] 

  # Each call to read() returns the next line (as a string). 
    def read(): 
        global lines
        this_line = lines[0] 
        lines = lines[1:]
        return this_line 

  # read_list is a higher-order function. You pass in a worker
  # function (like "read_exp" or "read_feature"). This first
  # reads the number of elements in the list and then calls
  # the worker function that many times in a row. It returns
  # a list made of the returns of the sequential calls to the
  # worker function.
    def read_list(worker):
        k = int(read()) 
        return [ worker () for x in range(k) ] 

    def read_id():
        loc = read () 
        name = read ()
        return ID(loc, name) 

    def read_bindings ():
        ekind = read_ekind(1)
        return ekind

    def read_case_elements():
        var = read_id()
        type = read_id()
        body = read_exp()
        return Case_element(var, type, body, None)

    # An expression starts with its location (line number) 
    # and then has a "kind" (like Plus or While). 
    def read_exp ():
        eloc = read () 
        ekind = read_ekind(0)
        return (eloc, ekind)

    def read_ekind (binding):
        if not binding: static_type = read ()
        ekind = read () 
        if ekind == "integer":
            val = read ()
            return Integer(val, static_type)
        elif ekind == "identifier":
            id = read_id()
            return Identifier(id, static_type)
        elif ekind == "string":
            val = read ()
            return String(val, static_type)
        elif ekind == "plus": 
            left = read_exp ()
            right = read_exp ()
            return Plus(left, right, static_type) 
        elif ekind == "minus": 
            left = read_exp ()
            right = read_exp ()
            return Minus(left, right, static_type) 
        elif ekind == "times": 
            left = read_exp ()
            right = read_exp ()
            return Times(left, right, static_type) 
        elif ekind == "divide": 
            left = read_exp ()
            right = read_exp ()
            return Divide(left, right, static_type) 
        elif ekind == "lt": 
            left = read_exp ()
            right = read_exp ()
            return Lt(left, right, static_type) 
        elif ekind == "le": 
            left = read_exp ()
            right = read_exp ()
            return Le(left, right, static_type) 
        elif ekind == "eq": 
            left = read_exp ()
            right = read_exp ()
            return Eq(left, right, static_type) 
        elif ekind == "not": 
            exp = read_exp ()
            return Not(exp, static_type)
        elif ekind == "negate": 
            exp = read_exp ()
            return Negate(exp, static_type)
        elif ekind == "isvoid": 
            exp = read_exp ()
            return IsVoid(exp, static_type)
        elif ekind == "new": 
            type = read_id ()
            return New(type, static_type)
        elif ekind == "true": 
            return true(True, static_type)
        elif ekind == "false": 
            return false(False, static_type)
        elif ekind == "block":
            body = read_list(read_exp)
            return Block(body, static_type)
        elif ekind == "while":
            predicate = read_exp ()
            body = read_exp ()
            return While(predicate, body, static_type) 
        elif ekind == "if":
            predicate = read_exp ()
            then_branch = read_exp ()
            else_branch = read_exp ()
            return If(predicate, then_branch, else_branch, static_type)
        elif ekind == "dynamic_dispatch":
            exp = read_exp()
            method = read_id()
            args = read_list(read_exp)
            return Dynamic_Dispatch(exp, method, args, static_type)
        elif ekind == "static_dispatch":
            exp = read_exp()
            type = read_id()
            method = read_id()
            args = read_list(read_exp)
            return Static_Dispatch(exp, type, method, args, static_type)
        elif ekind == "self_dispatch":
            method = read_id()
            args = read_list(read_exp)
            return Self_Dispatch(method, args, static_type)
        elif ekind == "assign":
            var = read_id()
            exp = read_exp()
            return Assign(var, exp, static_type)
        elif ekind == "let":
            bindings = read_list(read_bindings)
            body = read_exp()
            return Let(bindings, body, static_type)
        elif ekind == "let_binding_no_init":
            var = read_id()
            type = read_id()
            return Let_No_Init(var, type)
        elif ekind == "let_binding_init":
            var = read_id()
            type = read_id()
            exp = read_exp()
            return Let_Init(var, type, exp)
        elif ekind == "case":
            exp = read_exp()
            elements = read_list(read_case_elements)
            return Case(exp, elements, static_type)
        elif ekind == 'internal':
            body = read()
            return Internal(body, static_type)
        else: 
            raise (Exception(f"read_ekind: {ekind} unhandled"))

    # Read in the class map and store it in class_map dictionary
    def read_class_map():
        read ()
        num_classes = read ()
        for i in range(int(num_classes)):
            read_class_map_class()

    def read_class_map_class():
        class_name = read ()
        class_map[class_name] = []
        num_attrs = read()
        for i in range(int(num_attrs)):
            read_class_map_attr(class_name)

    def read_class_map_attr(class_name):
        init = read()
        attr_name = read()
        type_name = read()
        if init == "initializer": init_exp = read_exp()
        else: init_exp = None
        class_map[class_name].append(Attribute(attr_name, type_name, init_exp))

    # Read in the implementation map and store it in imp_map dictionary
    def read_imp_map():
        read() #ask weim about these
        num_classes = read()
        for i in range (int(num_classes)):
            read_imp_map_class()

    def read_imp_map_class():
        class_name = read()
        num_methods = read()
        for i in range (int(num_methods)):
            read_imp_map_method(class_name)

    def read_imp_map_method(class_name):
        method_name = read()
        num_formals = read()
        imp_map[(class_name, method_name)] = []
        for i in range(int(num_formals)):
            imp_map[(class_name, method_name)].append(read())
        read()
        body = read_exp()
        imp_map[(class_name, method_name)].append(body)

    # Read in the parent map and store it in parent_map dictionary
    def read_parent_map():
        read()
        num_relations = read()
        for i in range(int(num_relations)):
            child = read()
            parent = read()
            parent_map[child] = parent

    # Assign default values to Cool values 
    def get_default_val(c):
        match c:
            case "Int": val = Cool_Int("Int", 0)
            case "String": val = Cool_String("String", 0, "")
            case "Bool": val = Cool_Bool("Bool", False)
            case default: val = None
        return val
    
    def map_attrs(attributes):
        # Create new enviornment
        new_e = Environment()
        for attr_name in attributes:
            new_e.update(attr_name, attributes[attr_name])
        return new_e
    
    # Find closest ancestor of case variable x 
    def closest_ancestor(x, case_elems):
        while (x != "Object"):
            for elem in case_elems:
                if x == elem.Type.str: return elem
            x = parent_map[x]
        for elem in case_elems:
            if elem.Type.str == "Object": return elem
        return None
            
    # Evaluation: recursively evaluate each expression based on operational semantics rules
    # Return: cool_value, new_store
    def eval(so, s, e, exp):
        global act_recs
        line_num = exp[0]
        exp = exp[1]
        exp_kind = type(exp).__name__.lower()
        
        if exp_kind == "integer": 
            i = exp.Integer
            return Cool_Int("Int", int(i)), s
        
        elif exp_kind == "string":
            string = exp.String
            l = len(string)
            return Cool_String("String", l, string), s

        elif exp_kind == 'true':
            return Cool_Bool("Bool", True), s
        
        elif exp_kind == 'false':
            return Cool_Bool("Bool", False), s
        
        elif exp_kind in ["plus", "minus", "times", "divide"]:
            v1, s2 = eval(so, s, e, exp.Left)
            v2, s3 = eval(so, s2, e, exp.Right)
            
            match exp_kind:
                case "plus": result_val = v1.integer + v2.integer
                case "minus": result_val = v1.integer - v2.integer
                case "times": result_val = v1.integer * v2.integer
                case "divide": 
                    # Ensure no division by zero
                    if v2.integer == 0:
                        print(f"ERROR: {line_num}: Exception: division by zero")
                        exit(1)
                    result_val = int(v1.integer / v2.integer)
            
            return Cool_Int("Int", result_val), s3
        
        elif exp_kind in ["lt", "le", "eq"]:
            v1, s2 = eval(so, s, e, exp.Left)
            v2, s3 = eval(so, s2, e, exp.Right)

            if v1 == None or v2 == None: 
                if exp_kind != "lt": b = v1 == v2
                else: b = False
                return Cool_Bool("Bool", b), s
            
            t1 = type(v1).__name__
            t2 = type(v2).__name__
            
            # Comparisons for Int, String, Bool, Object
            match (t1, t2):
                case ("Cool_Int", "Cool_Int"):
                    match exp_kind:
                        case "lt": b = v1.integer < v2.integer
                        case "le": b = v1.integer <= v2.integer
                        case "eq": b = v1.integer == v2.integer
                
                case ("Cool_String", "Cool_String"):
                    match exp_kind:
                        case "lt": b = v1.string < v2.string
                        case "le": b = v1.string <= v2.string
                        case "eq": b = v1.string == v2.string
                
                case ("Cool_Bool", "Cool_Bool"):
                    match exp_kind:
                        case "lt": b = v1.bool < v2.bool
                        case "le": b = v1.bool <= v2.bool
                        case "eq": b = v1.bool == v2.bool
                
                case ("Cool_Object", "Cool_Object"):
                    if exp_kind != "lt": b = s.lookup_val(v1) == s.lookup_val(v2)
                    else: b = False
                
                case default: b = False
           
            return Cool_Bool("Bool", b), s
        
        elif exp_kind == "identifier":
            if exp.Var.str == "self": return so, s
            loc = e.lookup(exp.Var.str)
            v = s.lookup(loc)
            return v, s
        
        elif exp_kind == "block":
            for expr in exp.Body:
                v, s = eval(so, s, e, expr)
            # Return last one
            return v, s 
        
        elif exp_kind == "not":
            b, s2 = eval(so, s, e, exp.Exp)
            if b.bool == True: v1 = Cool_Bool("Bool", False)
            else: v1 = Cool_Bool("Bool", True)
            return v1, s2
        
        elif exp_kind == "negate":
            i, s2 = eval(so, s, e, exp.Exp)
            v1 = Cool_Int("Int", ~(i.integer) + 1)
            return v1, s2

        # Use variable location to update store with new value
        elif exp_kind == "assign":
            v1, s = eval(so, s, e, exp.Exp)
            var_loc = e.lookup(exp.Var.str)
            s.update(var_loc, v1)
            return v1, s
        
        elif exp_kind == "if":
            b, s2 = eval(so, s, e, exp.Predicate)
            if b.bool == True: v, s3 = eval(so, s2, e, exp.Then)
            else: v, s3 = eval(so, s2, e, exp.Else)
            return v, s3
        
        elif exp_kind == "while":
            b, s2 = eval(so, s, e, exp.Predicate)
            if b.bool == True:
                v2, s3 = eval(so, s2, e, exp.Body)
                v, s4 = eval(so,s3, e, (line_num, exp))
                return None, s4
            else: 
                return None, s2
            
        elif exp_kind == "isvoid":
            v, s2 = eval(so, s, e, exp.Exp)
            if v == None: return Cool_Bool("Bool", True), s2
            else: return Cool_Bool("Bool", False), s2

        # Loop through bindings to updates the extended environment and store
        elif exp_kind == "let":
            bindings = exp.Bindings
            ext_e = e.extend()

            for i in range(len(bindings)):
                if type(bindings[i]).__name__ == "Let_Init":
                    v1, s2 = eval(so, s, ext_e, bindings[i].Exp)
                else:
                    v1 = get_default_val(bindings[i].Type.str)
                
                loc = s.newloc()
                s.update(loc, v1)
                ext_e.update(bindings[i].Var.str, loc)
            
            # Evaluate let body with extended environment
            v2, s4 = eval(so, s, ext_e, exp.Body)
            return v2, s4
        
        # Get closest ancestor branch and evaluate its expression to update extended environment
        elif exp_kind == "case":
            v, s2 = eval(so, s, e, exp.Exp)
            # Error to have case on void
            if v == None:
                print(f"ERROR: {line_num}: Exception: case on void")
                exit(1)
            
            x = v.type
            ti_branch = closest_ancestor(x, exp.Elements)

            # Error to have case without matching branch
            if ti_branch == None:
                print(f"ERROR: {line_num}: Exception: case without matching branch: {x}(...)")
                exit(1)

            loc = s.newloc()
            s.update(loc, v)
            ext_e = e.extend()
            ext_e.update(ti_branch.Var.str, loc)

            return eval(so, s, ext_e, ti_branch.Body)
                       
        # Handle new Cool values
        elif exp_kind == "new":
            # Add to activation record count and check if exceeds limit (stack overflow)
            act_recs += 1
            if act_recs >= 1000:
                print(f"ERROR: {line_num}: Exception: stack overflow")
                exit(1)
            if exp.Type.str == "SELF_TYPE" and type(so).__name__ == "Cool_Object":
                t = so.type
            else:
                t = exp.Type.str

            # Check if needs default value
            if t in ["Int", "String", "Bool"]:
                return get_default_val(t), s

            # New environment for new object (new scope)
            new_e = Environment()
            v1 = Cool_Object(t)

            # Map new attributes to their locations in new environment
            for attr in class_map[t]:
                loc = s.newloc()
                v1.add_attr(attr.Name, loc)
                s.update(loc, get_default_val(attr.Type))
                new_e.update(attr.Name, loc)
        
            # Evaluate each attribute of the new object
            for attr in class_map[t]:
                init = attr.Initializer
                if init != None:
                    v2, s = eval(v1, s, new_e, (line_num, Assign(ID(line_num, attr.Name), init, init[1].StaticType)))
        
            # Stack frame is popped off
            act_recs -= 1
            return v1, s
        
        elif exp_kind == "dynamic_dispatch":
            act_recs += 1
            if act_recs >= 1000:
                print(f"ERROR: {line_num}: Exception: stack overflow")
                exit(1)

            # Dynamic_Dispatch = namedtuple("Dynamic_Dispatch", "Exp Method Args StaticType")
            arg_values = []

            for arg in exp.Args:
                arg_v, s = eval(so, s, e, arg)
                arg_values.append(arg_v)
        
            v0, s = eval(so, s, e, exp.Exp)

            # Error if dispatch on void
            if v0 == None:
                print(f"ERROR: {line_num}: Exception: dispatch on void")
                exit(1)

            # Grab formals and body from the imp_map using indexing
            formals = (imp_map[(v0.type, exp.Method.str)])[:-1]
            body = (imp_map[(v0.type, exp.Method.str)])[-1]

            # Map attributes to their locations in new environment
            new_e = map_attrs(v0.attributes)

            # Env updated with formal arguments mapped to loc
            # New store with evaluated arg values mapped to loc
            for i in range(len(exp.Args)):
                loc = s.newloc()
                new_e.update(formals[i], loc)
                s.update(loc, arg_values[i])

            vf, s = eval(v0, s, new_e, body)
            act_recs -= 1
            return vf, s
        
        elif exp_kind == "static_dispatch":
            act_recs += 1
            if act_recs >= 1000:
                print(f"ERROR: {line_num}: Exception: stack overflow")
                exit(1)

            # Static_Dispatch = namedtuple("Static_Dispatch", "Exp Type Method Args StaticType")
            arg_values = []

            for arg in exp.Args:
                arg_v, s = eval(so, s, e, arg)
                arg_values.append(arg_v)
        
            v0, s = eval(so, s, e, exp.Exp)

            # Error to static dispatch on void
            if v0 == None:
                print(f"ERROR: {line_num}: Exception: static dispatch on void")
                exit(1)

            formals = (imp_map[(exp.Type.str, exp.Method.str)])[:-1]
            body = (imp_map[(exp.Type.str, exp.Method.str)])[-1]

            # Map attributes to their locations in new environment
            new_e = map_attrs(v0.attributes)

            # Env updated with formal arguments mapped to loc
            # New store with evaluated arg values mapped to loc
            for i in range(len(exp.Args)):
                loc = s.newloc()
                new_e.update(formals[i], loc)
                s.update(loc, arg_values[i])

            vf, s = eval(v0, s, new_e, body)
            act_recs -= 1
            return vf, s

        elif exp_kind == "self_dispatch":
            act_recs += 1
            if act_recs >= 1000:
                print(f"ERROR: {line_num}: Exception: stack overflow")
                exit(1)
            
            # Self_Dispatch = namedtuple("Self_Dispatch", "Method Args StaticType")
            arg_values = []

            for arg in exp.Args:
                arg_v, s = eval(so, s, e, arg)
                arg_values.append(arg_v)

            formals = (imp_map[(so.type, exp.Method.str)])[:-1]
            body = (imp_map[(so.type, exp.Method.str)])[-1]

            # print(exp.Method.str, formals, body)

            # Map self's attributes to their locations in new environment
            # for attribute in so.Attributes:
            new_e = map_attrs(so.attributes)

            # Env updated with formal arguments mapped to loc
            # New store with evaluated arg values mapped to loc
            for i in range(len(exp.Args)):
                loc = s.newloc()
                new_e.update(formals[i], loc)
                s.update(loc, arg_values[i])

            vf, s = eval(so, s, new_e, body)
            act_recs -= 1
            return vf, s
        
        # Handle all internal methods 
        elif exp_kind == "internal":
            match exp.Body:
                # methods out_string and out_int print their argument, 
                # flush the standard output, and return their self parameter.
                case "IO.out_string":
                    formals = (imp_map[("IO", "out_string")])[:-1]
                    loc = e.lookup(formals[0])
                    value = s.lookup(loc)
                    # Change every \t to tab and \n to newline
                    value = value.string.replace("\\t", "\t").replace("\\n", "\n")
                    print(value, end="")
                    return so, s
                
                case "IO.out_int":
                    formals = (imp_map[("IO", "out_int")])[:-1]
                    loc = e.lookup(formals[0])
                    value = s.lookup(loc)
                    value = value.integer
                    print(value, end="")
                    return so, s
                
                case "IO.in_int":
                    # check for EOF
                    try: value = input()
                    except EOFError: value = 0

                    # Parse value
                    try: value = str(value).split()[0]
                    except: value = 0

                     # check that input is int
                    try: value = int(value)
                    except: value = 0
                   
                    # check if input value exceeds input limitations
                    if value < -2147483648 or value > 2147483647: value = 0
                    return Cool_Int("Int", value), s
               
                case "IO.in_string":
                    # check for EOF
                    try: value = input()
                    except EOFError: value = ""

                    # check for null character
                    if '\0' in value: value = ""
                    
                    return Cool_String("String", len(value), value), s
                
                case "Object.abort":
                    print("abort")
                    exit(1)

                # Return a string
                case "Object.type_name":
                    return Cool_String("String", len(so.type), so.type), s
                
                case "String.concat":
                    formals = (imp_map[("String", "concat")])[:-1]
                    loc = e.lookup(formals[0])
                    tail = s.lookup(loc)
                    # Concatenate strings:
                    full_str = so.string + tail.string
                    return Cool_String("String", len(full_str), full_str), s
                
                case "String.substr":
                    formals = (imp_map[("String", "substr")])[:-1]
                    iloc = e.lookup(formals[0])
                    lloc = e.lookup(formals[1])
                    i = s.lookup(iloc).integer
                    l = s.lookup(lloc).integer
                    # Error if the substring uses indexes out of bounds
                    if so.length < i + l:
                        print("ERROR: 0: Exception: String.substr out of range")
                        exit(1)

                    sub_str = so.string[i:i+l]
                    return Cool_String("String", len(sub_str), sub_str), s

                case "String.length":
                    return Cool_Int("Int", so.length), s

                case "Object.copy":
                    # We can use the internal copy method in Python
                    so_copy = copy.copy(so)

                    # If the object is a Cool_Object, we need to copy its attributes
                    if type(so).__name__ == "Cool_Object":
                        so_copy.attributes = {}
                        for attr in so.attributes:
                            # Map to NEW locations
                            loc = s.newloc()
                            so_copy.add_attr(attr, loc)
                            v = s.lookup(so.attributes[attr])
                            s.update(loc, v)
                    
                    return so_copy, s

            return so, s

        else:
            print("unhandled expression")
            print(exp)
            exit(1)

    # Initialize empty dictionaries
    class_map = {}
    imp_map = {}
    parent_map = {}
    # Read .cl-type input file to extract class map, implementation map, parent map, and AST
    read_class_map()
    read_imp_map()
    read_parent_map()

    # Traverse the AST to interpret the program
    def interpret():
        so = Cool_Object("Main")
        e = Environment()
        s = Store()

        # Initialize Main class attributes
        for attr in class_map["Main"]:
            loc = s.newloc()
            so.add_attr(attr.Name, loc)
            e.update(attr.Name, loc)
            s.update(loc, get_default_val(attr.Type))
            if attr.Initializer != None:
                # Evaluate!
                v, s = eval(so, s, e, attr.Initializer)
                s.update(loc, v)
        
        # Start by intepretting the main method of the Main class
        starting_main_method = imp_map[("Main","main")]
        eval(so, s, e, starting_main_method[0])
    
    interpret()

main()
