# Prathit Kurup and Nick Chu DeChristofaro
# Based on Python starter code that covers the majority of the aspects of the PA4c OCaml video. 
import sys
import copy
from collections import namedtuple

# Where OCaml would use "algebraic datatypes", we use
# Python's "namedtuple", which is similar. 
CoolClass = namedtuple("CoolClass", "Name Inherits Features")
Attribute = namedtuple("Attribute", "Name Type Initializer") 
Method = namedtuple("Method", "Name Formals ReturnType Body")

# A Cool Identifier is a tuple (pair) of a location and a string.
ID = namedtuple("ID", "loc str") 
Formal = namedtuple("Formal", "Name Type")

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
Let_No_Init = namedtuple("Let_No_Init", "Var Type StaticType")
Let_Init = namedtuple("Let_Init", "Var Type Exp StaticType")
Case = namedtuple("Case", "Exp Elements StaticType")
Case_element = namedtuple("Case_element", "Var Type Body StaticType")

# Base Cool Classes
ObjectClass      = CoolClass("Object", None, 
                              [Method(Name=ID(loc='', str="abort"), Formals=[], ReturnType=ID(loc='', str="Object"), Body=""), 
                               Method(Name=ID(loc='', str="copy"), Formals=[], ReturnType=ID(loc='', str="SELF_TYPE"), Body=""),
                               Method(Name=ID(loc='', str="type_name"), Formals=[], ReturnType=ID(loc='', str="String"), Body="")
                              ])
IOClass      = CoolClass("IO", ID(loc='', str="Object"), 
                              [Method(Name=ID(loc='', str="in_int"), Formals=[], ReturnType=ID(loc='', str="Int"), Body=""),
                               Method(Name=ID(loc='', str="in_string"), Formals=[], ReturnType=ID(loc='', str="String"), Body=""),
                               Method(Name=ID(loc='', str="out_int"), Formals=[Formal(ID("", "x") , ID("", "Int"))], ReturnType=ID(loc='', str="SELF_TYPE"), Body=""),
                               Method(Name=ID(loc='', str="out_string"), Formals=[Formal(ID("", "x") , ID("", "String"))], ReturnType=ID(loc='0', str="SELF_TYPE"), Body="")
                              ])
IntClass      = CoolClass("Int", ID(loc='', str="Object"), [])
StringClass      = CoolClass("String", ID(loc='', str="Object"), 
                              [Method(Name=ID(loc='', str="concat"), Formals=[Formal(ID("", "s") , ID("", "String"))], ReturnType=ID(loc='', str="String"), Body=""),
                               Method(Name=ID(loc='', str="length"), Formals=[], ReturnType=ID(loc='', str="Int"), Body=""), 
                               Method(Name=ID(loc='', str="substr"), Formals=[Formal(ID("", "i") , ID("", "Int")), Formal(ID("", "l") , ID("", "Int"))], ReturnType=ID(loc='', str="String"), Body="") 
                              ])
BoolClass      = CoolClass("Bool", ID(loc='', str="Object"), [])

# The lines in the CL-AST file that we read as input.
lines = [] 

# This follows a similar structure to the OCaml video code. 
def main(): 
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

  def read_cool_program():
    return read_list(read_cool_class)

  def read_id():
    loc = read () 
    name = read ()
    return ID(loc, name) 

  def read_cool_class (): 
    cname = read_id () 
    i = read()
    if i == "no_inherits": 
      inherits = None 
    elif i == "inherits": 
      inherits = read_id()
    else:
      raise(Exception(f"read_cool_class: inherits {i}"))
    features = read_list(read_feature)
    return CoolClass(cname, inherits, features) 

  def read_feature (): 
    a = read()
    if a == "attribute_no_init":
      fname = read_id()
      ftype = read_id()
      return Attribute(fname, ftype, None) 
    elif a == "attribute_init":
      fname = read_id()
      ftype = read_id()
      finit = read_exp()
      return Attribute(fname, ftype, finit)
    elif a == "method":
      mname = read_id ()
      formals = read_list(read_formal)
      mtype = read_id ()
      mbody = read_exp ()
      return Method(mname, formals, mtype, mbody)
    else:
      raise(Exception(f"read_feature {a}"))

  def read_formal ():
    fname = read_id()
    ftype = read_id()
    return Formal(fname, ftype) 
  
  def read_bindings ():
    ekind = read_ekind()
    return ekind
  
  def read_case_elements():
    var = read_id()
    type = read_id()
    if type.str == 'SELF_TYPE':
      print(f"ERROR: {type.loc}: Type-Check: using SELF_TYPE as a case branch type is not allowed")
      exit(1)
    body = read_exp()
    return Case_element(var, type, body, None)

  # An expression starts with its location (line number) 
  # and then has a "kind" (like Plus or While). 
  def read_exp ():
    eloc = read () 
    ekind = read_ekind()
    return (eloc, ekind)
  
  def read_ekind ():
    ekind = read () 
    if ekind == "integer":
      val = read ()
      return Integer(val, None)
    elif ekind == "identifier":
      id = read_id()
      return Identifier(id, None)
    elif ekind == "string":
      val = read ()
      return String(val, None)
    elif ekind == "plus": 
      left = read_exp ()
      right = read_exp ()
      return Plus(left, right, None) 
    elif ekind == "minus": 
      left = read_exp ()
      right = read_exp ()
      return Minus(left, right, None) 
    elif ekind == "times": 
      left = read_exp ()
      right = read_exp ()
      return Times(left, right, None) 
    elif ekind == "divide": 
      left = read_exp ()
      right = read_exp ()
      return Divide(left, right, None) 
    elif ekind == "lt": 
      left = read_exp ()
      right = read_exp ()
      return Lt(left, right, None) 
    elif ekind == "le": 
      left = read_exp ()
      right = read_exp ()
      return Le(left, right, None) 
    elif ekind == "eq": 
      left = read_exp ()
      right = read_exp ()
      return Eq(left, right, None) 
    elif ekind == "not": 
      exp = read_exp ()
      return Not(exp, None)
    elif ekind == "negate": 
      exp = read_exp ()
      return Negate(exp, None)
    elif ekind == "isvoid": 
      exp = read_exp ()
      return IsVoid(exp, None)
    elif ekind == "new": 
      type = read_id ()
      return New(type, None)
    elif ekind == "true": 
      return true(True, None)
    elif ekind == "false": 
      return false(False, None)
    elif ekind == "block":
      body = read_list(read_exp)
      return Block(body, None)
    elif ekind == "while":
      predicate = read_exp ()
      body = read_exp ()
      return While(predicate, body, None) 
    elif ekind == "if":
      predicate = read_exp ()
      then_branch = read_exp ()
      else_branch = read_exp ()
      return If(predicate, then_branch, else_branch, None)
    elif ekind == "dynamic_dispatch":
      exp = read_exp()
      method = read_id()
      args = read_list(read_exp)
      return Dynamic_Dispatch(exp, method, args, None)
    elif ekind == "static_dispatch":
      exp = read_exp()
      type = read_id()
      method = read_id()
      args = read_list(read_exp)
      return Static_Dispatch(exp, type, method, args, None)
    elif ekind == "self_dispatch":
      method = read_id()
      args = read_list(read_exp)
      return Self_Dispatch(method, args, None)
    elif ekind == "assign":
      var = read_id()
      exp = read_exp()
      return Assign(var, exp, None)
    elif ekind == "let":
      bindings = read_list(read_bindings)
      body = read_exp()
      return Let(bindings, body, None)
    elif ekind == "let_binding_no_init":
      var = read_id()
      type = read_id()
      return Let_No_Init(var, type, None)
    elif ekind == "let_binding_init":
      var = read_id()
      type = read_id()
      exp = read_exp()
      return Let_Init(var, type, exp, None)
    elif ekind == "case":
      exp = read_exp()
      elements = read_list(read_case_elements)
      return Case(exp, elements, None)
    else: 
      raise (Exception(f"read_ekind: {ekind} unhandled"))

  ast = read_cool_program () 

  base_classes = [ "Int", "String", "Bool", "IO", "Object" ]
  user_classes = [ c.Name.str for c in ast ] 
  all_classes = (base_classes + user_classes)

  # Look for inheritance from Int, String and undeclared classes 
  for c in ast:
    if c.Inherits != None: 
      i = c.Inherits 
      if i.str in ["Int", "String", "Bool"]:
        print(f"ERROR: {i.loc}: Type-Check: inheriting from forbidden class {i.str}")
        exit(1) 
      elif not i[1] in all_classes:
        print(f"ERROR: {i.loc}: Type-Check: inheriting from undefined class {i.str}")
        exit(1) 

  # Example of another check. Let's look for duplicate classes. 
  for i in range(len(ast)):
    c_i = ast[i]
    for j in range(i+1, len(ast)): 
      c_j = ast[j]
      if c_i.Name.str == c_j.Name.str:
        print(f"ERROR: {c_j.Name.loc}: Type-Check: class {c_i.Name.str} redefined") 
        exit(1) 

  # Check if class main not found
  main_exists = False
  for c in ast:
    if c.Name.str == "Main": main_exists = True
  if not main_exists:
    print(f"ERROR: 0: Type-Check: class Main not found") 
    exit(1) 
    
  # Check if main method exists in Main class
  for c in ast:
    if c.Name.str == "Main":
      feature_names = [f.Name.str for f in c.Features]
      if "main" not in feature_names:
        print(f"ERROR: 0: Type-Check: class Main method main not found") 
        exit(1)

  # Check if main method has no params
  for c in ast:
    if c.Name.str == "Main":
      for f in c.Features:
        if f.Name.str == "main":
          formal_list = [formal for formal in f.Formals]
          if formal_list: 
            print(f"ERROR: 0: Type-Check: class Main method main with 0 parameters not found")
            exit(1)

  # Map the name of every class 
  mappedClassNames = {}
  for c in ast:
    mappedClassNames[c.Name.str] = c
  
  # Get top sort of inheritance graph
  topsort = []
  indeg = {}
  for c in ast:
    if c.Inherits != None and ((c.Inherits).str not in base_classes):
      indeg[c.Name.str] = 1
    else:
      indeg[c.Name.str] = 0

  to_explore = set()
  for cName in indeg:
    if indeg[cName] == 0:
        to_explore.add(cName)
  
  while len(to_explore) != 0:
    cName = sorted(list(to_explore))[0]
    to_explore.remove(cName)
    topsort.append(cName)

    for c in ast:
      if c.Inherits != None:
        if (c.Inherits).str == cName:
          indeg[c.Name.str] = 0
          to_explore.add(c.Name.str)
  
  # Check for cycles
  if len(topsort) != len(user_classes):
    print(f"ERROR: 0: Type-Check: Inheritance cycle: you have not warmed my heart")
    exit(1)

  # Check if methods/attributes repeated within class
  for c in ast:
    attribute_names = []
    method_names = []
    for f in c.Features:
      feature_name = f.Name.str
      feature_type = type(f).__name__.lower()
      if feature_type == "method" and feature_name not in method_names:
          method_names.append(feature_name)
      elif feature_type == "attribute" and feature_name not in attribute_names:
          attribute_names.append(feature_name)
      else:
        print(f"ERROR: {f.Name.loc}: Type-Check: class {c.Name.str} redefines {type(f).__name__.lower()} {feature_name}")
        exit(1)

  # Check if duplicate formal paramaters
  for c in ast:
    for f in c.Features:
      if type(f).__name__.lower() == "method":
        formal_list = []
        for formal in f.Formals:
          if formal[0].str not in formal_list:
            formal_list.append(formal[0].str)
          else:
            print(f"ERROR: {f.Name.loc}: Type-Check: class {c.Name.str} has method {f.Name.str} with duplicate formal parameter named {formal[0].str}")
            exit(1)

  # checks for invalid redfinition of methods
  def redefined_method(c, p_c):
    if p_c == None or p_c.str == "Object": 
      p_c = ObjectClass
    elif p_c.str == "IO": 
      p_c = IOClass
      redefined_method(c, p_c.Inherits)
    else:
      redefined_method(c, ast[user_classes.index(p_c.str)].Inherits)
      p_c = ast[user_classes.index(p_c.str)]
    check_methods(c, p_c)
  
  # Check for changed parameter count, changed return types, changed parameter types
  def check_methods(c, p_c):
      for f in c.Features:
          if type(f).__name__.lower() == "method":
              for p_f in p_c.Features:
                  if type(p_f).__name__.lower() == "method" and f.Name.str == p_f.Name.str:
                      check_return_type(c, f, p_f)
                      check_formals(c, f, p_f)
    
  # Check for changed return type
  def check_return_type(c, f, p_f):
      if f.ReturnType.str != p_f.ReturnType.str:
          print(f"ERROR: {f.Name.loc}: Type-Check: class {c.Name.str} redefines method {f.Name.str} and changes return type (from {p_f.ReturnType.str} to {f.ReturnType.str})")
          exit(1)

  # Check for changed parameter count and types
  def check_formals(c, f, p_f):
      c_formals = [formal for formal in f.Formals]
      p_c_formals = [formal for formal in p_f.Formals]
      if len(c_formals) != len(p_c_formals):
        print(f"ERROR: {f.Name.loc}: Type-Check: class {c.Name.str} redefines method {f.Name.str} and changes number of formals")
        exit(1)
      for i in range(len(c_formals)):
        if c_formals[i][1].str != p_c_formals[i][1].str:
          print(f"ERROR: {f.Name.loc}: Type-Check: class {c.Name.str} redefines method {f.Name.str} and changes type of formal {c_formals[i][0].str}")
          exit(1)

  # check for redefined attributes
  def redefined_attributes(c, p_c):   
    if p_c == None or p_c.str == "Object" or p_c.str == "IO": 
      return
    else:
      redefined_attributes(c, ast[user_classes.index(p_c.str)].Inherits)
      p_c = ast[user_classes.index(p_c.str)]
      check_attributes(c, p_c)


  # Helper function to check if attributes get redefined 
  def check_attributes(c, p_c):
     p_attributes = [atr.Name.str for atr in p_c.Features if type(atr).__name__.lower() == "attribute"]
     for f in c.Features:
        if f.Name.str in p_attributes:
          print(f"ERROR: {f.Name.loc}: Type-Check: class {c.Name.str} redefines attribute {f.Name.str}")
          exit(1)
  
  # Run checks on methods and attributes
  for c in ast:
    redefined_method(c, c.Inherits)
    redefined_attributes(c, c.Inherits)

  # Check that classes are not named SELF_TYPE and SELF_TYPE is not a parameter
  for c in ast:
    if c.Name.str == 'SELF_TYPE':
      print(f"ERROR: {c.Name.loc}: Type-Check: class named SELF_TYPE")
      exit(1)
    for f in c.Features:
      if type(f).__name__.lower() == "method": 
        formal_types = [formal[1].str for formal in f.Formals]
        if 'SELF_TYPE' in formal_types:
          print(f"ERROR: {f.Name.loc}: Type-Check: class {c.Name.str} has method {f.Name.str} with formal parameter of unknown type SELF_TYPE")
          exit(1)

  # Build dictionaries mapping classes with: methods (inherited and uninherited), attributes, and inherited classes (parents)
  attribute_dict = {}
  # This is the "M" dict in the type checking rules, mapping classes to methods
  # Maps classes the dictionaries mapping method names to their Method (Python object) in the ast representation
  method_dict = {"Object":{"abort":ObjectClass.Features[0], "copy":ObjectClass.Features[1], "type_name":ObjectClass.Features[2]}, 
                 "IO":{"abort":ObjectClass.Features[0], "copy":ObjectClass.Features[1], "type_name":ObjectClass.Features[2], "in_int":IOClass.Features[0], "in_string":IOClass.Features[1], "out_int":IOClass.Features[2], "out_string":IOClass.Features[3]},
                 "String":{"abort":ObjectClass.Features[0], "copy":ObjectClass.Features[1], "type_name":ObjectClass.Features[2],"concat":StringClass.Features[0], "length":StringClass.Features[1], "substr":StringClass.Features[2]},
                 "Int":{"abort":ObjectClass.Features[0], "copy":ObjectClass.Features[1], "type_name":ObjectClass.Features[2]},
                 "Bool":{"abort":ObjectClass.Features[0], "copy":ObjectClass.Features[1], "type_name":ObjectClass.Features[2]}
                }
  # Maps classes to all the methods that are not inherited
  own_methods = {"Object":["abort", "copy", "type_name"], 
                 "IO":["in_int", "in_string", "out_int", "out_string"],
                 "String":["concat", "length", "substr"],
                 "Int":[],
                 "Bool":[]
                }
  # Maps classes to a list of all their inherited parents 
  parent_dict = {"Object":[], "IO":["Object"], "Int":["Object"], "String":["Object"], "Bool":["Object"]}
  
  # Build these dictionaries by traversing the AST
  def traverse_ast(c):
    attribute_dict[c.Name.str] = {}
    method_dict[c.Name.str] = {}
    own_methods[c.Name.str] = []
    parent_dict[c.Name.str] = []
    
    # Collect information from parents
    parent = c.Inherits
    if parent != None: 
      parent_dict[c.Name.str] = parent_dict[parent.str] + [parent.str]
      if parent.str not in base_classes:
        (attribute_dict[c.Name.str]).update(attribute_dict[parent.str])
      method_dict[c.Name.str] = copy.deepcopy(method_dict[parent.str])
    # Object is a parent of all classes
    else: 
      parent_dict[c.Name.str] = ["Object"]
      method_dict[c.Name.str] = copy.deepcopy(method_dict["Object"])
    
    # Check the classes features (attributes and methods)
    for f in c.Features:
      feature_name = f.Name.str
      feature_type = type(f).__name__.lower()
      if feature_type == "attribute":
          attribute_dict[c.Name.str][feature_name] = f.Type.str
      elif feature_type == "method":
          method_dict[c.Name.str][feature_name] = f
          own_methods[c.Name.str].append(feature_name)

  # Fill dictionaries in top order
  for cName in topsort:
    traverse_ast(mappedClassNames.get(cName))
  # print("Attribute Dict:")
  # print(attribute_dict)
  # print("Parent Dict:")
  # print(parent_dict)
  # print("Method Dict:")
  # print(method_dict)
  # print("Own Method Dict:")
  # print(own_methods)
  
  # Find whether t1 is a subtype of t2
  def is_subtype(c, t1, t2):
    #TODO: check if needed
    if t1 == 'SELF_TYPE': t1 = c
    if t2 == 'SELF_TYPE': t2 = c
    if t1 == t2: return True
    if t1 == 'Object': return False
    # if t1 == t2 then true
    # if t2 == object then true
    if t2 == 'Object': return True
    # otherwise check parent map
    if parent_dict[t1][-1] == t2: return True
    else:
      return is_subtype(c, parent_dict[t1][-1], t2)
    
  def find_lub(c, t1, t2):
    if (t1 == 'SELF_TYPE') & (t2 == 'SELF_TYPE'): return 'SELF_TYPE'
    if t1 == 'SELF_TYPE': return find_lub(c, c, t2)
    if t2 == 'SElF_TYPE': return find_lub(c, c, t1)

    if t1 == t2: return t1
    if is_subtype(c, t1, t2): return t2
    if is_subtype(c, t2, t1): return t1

    lub = 'Object'
    for cls in reversed(parent_dict[t1]):
      if cls in parent_dict[t2]: return cls
    return lub
      
  # Typecheck all expressions passed in using o, m, c as the typechecking rules specify
  # Return line number and expression with filled in static type
  def typecheck (o, m, c, e):
    line_num = e[0]
    # Get the kind of expression
    exp_kind = type(e[1]).__name__.lower()
    
    if exp_kind == 'integer': 
      checked_e = e[1]._replace(StaticType="Int")
      return (line_num, checked_e)

    elif exp_kind == 'plus' or exp_kind == 'minus'  or exp_kind == 'times' or exp_kind == 'divide':
      e1 = typecheck(o, m, c, e[1].Left)
      if e1[1].StaticType != 'Int':
        print(f"ERROR: {e.Left[0]}: Type-Check: arithmetic not on type Int")
        exit(1)
      e2 = typecheck(o, m, c, e[1].Right)
      if e2[1].StaticType != 'Int':
        print(f"ERROR: {e.Right[0]}: Type-Check: arithmetic not on type Int")
        exit(1)
      checked_e = e[1]._replace(Left=e1, Right=e2, StaticType="Int")
      return (line_num, checked_e)
      
    elif exp_kind == 'identifier':
      id_name = e[1].Var.str
      if id_name not in o[c].keys():
        print(f"ERROR: {line_num}: Type-Check: unbound identifier {id_name}")
        exit(1)
      t = o[c][e[1].Var.str]
      
      # special check for turning true/false into a Bool
      if t == "true" or t == "false": t = "Bool"
      checked_e = e[1]._replace(StaticType=t)
      return (line_num, checked_e)
    
    elif exp_kind == 'true':
      return (line_num, true("true", "Bool"))
    
    elif exp_kind == 'false':
      return (line_num, false("false", "Bool"))
    
    elif exp_kind == 'string':
      checked_e = e[1]._replace(StaticType="String")
      return (line_num, checked_e)
    
    elif exp_kind == 'assign':
      if e[1].Var.str == 'self':
        print(f"ERROR: {e[1].Var.loc}: Type-Check: cannot assign to self")
        exit(1)
      t = o[c][e[1].Var.str]
      checked_e = typecheck(o, m, c, e[1].Exp)
      if not is_subtype(c, checked_e[1].StaticType, t):
        print(f"ERROR: {e[1].Exp[0]}: Type-Check: {checked_e[1].StaticType} does not conform to {t} in assignment")
        exit(1)
      checked_e = e[1]._replace(Exp=checked_e, StaticType=checked_e[1].StaticType)
      return (line_num, checked_e)
    
    elif exp_kind == 'new':
      if e[1].Type.str not in all_classes and e[1].Type.str != 'SELF_TYPE':
        print(f"ERROR: {e[0]}: Type-Check: unknown type {e[1].Type.str}")
        exit(1)
      if e[1].Type.str == "SELF_TYPE":
        checked_e = e[1]._replace(StaticType=c)
      else:
        checked_e = e[1]._replace(StaticType=e[1].Type.str)
      return (line_num, checked_e)

    elif exp_kind == 'dynamic_dispatch':
      e1 = typecheck(o, m, c, e[1].Exp)
      if e1[1].StaticType == 'SELF_TYPE': t_0_prime = c
      else: t_0_prime = e1[1].StaticType

      if e[1].Method.str not in m[t_0_prime].keys():
        print(f"ERROR: {e[1].Method.loc}: Type-Check: unknown method {e[1].Method.str} in dispatch on {e1[1].StaticType}")
        exit(1)

      m_sig = m[t_0_prime][e[1].Method.str]
      declared_args = m_sig.Formals
      checked_args = []
      
      if len(e[1].Args) != len(declared_args):
        print(f"ERROR: {e[1].Method.loc}: Type-Check: wrong number of actual arguments ({len(e[1].Args)} vs. {len(declared_args)})")
        exit(1)

      for i in range(len(e[1].Args)):
        a = typecheck(o, m, c, e[1].Args[i])
        if not is_subtype(c, a[1].StaticType, declared_args[i].Type.str):
          print(f"ERROR: {e[1].Method.loc}: Type-Check: argument #{i+1} type {a[1].StaticType} does not conform to formal type {declared_args[i].Type.str}")
          exit(1)
        checked_args.append(a)


      if m_sig.ReturnType.str == 'SELF_TYPE': static_type = e1[1].StaticType
      else: static_type = m_sig.ReturnType.str
      return(line_num, Dynamic_Dispatch(e1, e[1].Method, checked_args, static_type))
      
    elif exp_kind == 'static_dispatch':
      if e[1].Type.str not in all_classes and e[1].Type.str != 'SELF_TYPE':
        print(f"ERROR: {e[0]}: Type-Check: unknown type {e[1].Type.str}")
        exit(1)
      
      if e[1].Type.str == 'SELF_TYPE':
        print(f"ERROR: {e[1].Type.loc}: Type-Check: 'SELF_TYPE' cannot be used in static dispatch")
        exit(1)

      method_name = e[1].Method.str
      checked_e = typecheck(o, m, c, e[1].Exp)
      t0 = checked_e[1].StaticType
      t = e[1].Type.str
      if not is_subtype(c, t0, t):
        print(f"ERROR: {line_num}: Type-Check: {t0} does not conform to {t} in static dispatch")
        exit(1)

      if e[1].Method.str not in m[t0].keys():
        print(f"ERROR: {e[1].Method.loc}: Type-Check: unknown method {method_name} in dispatch on {t0}")
        exit(1)
      
     
      method_formals_lst = (m[t][method_name]).Formals
      given_formals_lst = e[1].Args
      if len(given_formals_lst) != len(method_formals_lst):
        print(f"ERROR: {e[1].Method.loc}: Type-Check: wrong number of actual arguments ({len(given_formals_lst)} vs. {len(method_formals_lst)})")
        exit(1)
      arg_type = None
      if len(method_formals_lst) == 0:
        arg_type = (m[t][method_name]).ReturnType.str
      checked_args = []
      for i in range(len(given_formals_lst)):
        a = typecheck(o, m, c, given_formals_lst[i])
        arg_type = a[1].StaticType
        if not is_subtype(c, arg_type, method_formals_lst[i].Type.str):
          print(f"ERROR: {e[1].Method.loc}: Type-Check: argument #{i+1} type {arg_type} does not conform to formal type {method_formals_lst[i].Type.str}")
          exit(1)
        checked_args.append(a)
      
      m_sig = m[t][e[1].Method.str]
      if m_sig.ReturnType.str == 'SELF_TYPE': static_type = e1[1].StaticType
      else: static_type = m_sig.ReturnType.str
      return(line_num, Static_Dispatch(checked_e, e[1].Type, e[1].Method, checked_args, static_type))

    elif exp_kind == 'self_dispatch':
      if e[1].Method.str not in m[c].keys():
          print(f"ERROR: {e[1].Method.loc}: Type-Check: unknown method {e[1].Method.str}")
          exit(1)
      m_sig = m[c][e[1].Method.str]
      declared_args = m_sig.Formals
      checked_args = []
      
      if len(e[1].Args) != len(declared_args):
        print(f"ERROR: {e[1].Method.loc}: Type-Check: wrong number of actual arguments ({len(e[1].Args)} vs. {len(declared_args)})")
        exit(1)

      for i in range(len(e[1].Args)):
        a = typecheck(o, m, c, e[1].Args[i])
        if not is_subtype(c, a[1].StaticType, declared_args[i].Type.str):
          print(f"ERROR: {e[1].Method.loc}: Type-Check: argument #{i+1} type {a[1].StaticType} does not conform to formal type {declared_args[i].Type.str}")
          exit(1)
        checked_args.append(a)
      return(line_num, Self_Dispatch(e[1].Method, checked_args, m_sig.ReturnType.str))
      
    
    elif exp_kind == 'if':
      e1 = typecheck(o, m, c, e[1].Predicate)
      if e1[1].StaticType != 'Bool':
        print(f"ERROR: {e1[0]}: Type-Check: conditional has type {e1[1].StaticType} instead of Bool")
        exit(1)
      e2 = typecheck(o, m, c, e[1].Then)
      e2Type = e2[1].StaticType
      e3 = typecheck(o, m, c, e[1].Else)
      e3Type = e3[1].StaticType
      
      lub = find_lub(c, e2Type, e3Type)
      # Using the reverse of the topsort, check the least type of e2 and e3
      return (line_num, If(e1, e2, e3, lub))

    elif exp_kind == 'block':
      new_block = []
      for i in range(len(e[1].Body)):
        new_block.append(typecheck(o, m, c, e[1].Body[i]))

      t = (new_block[-1])[1].StaticType
      return (line_num, Block(new_block, t))

    elif exp_kind == 'let':
      # Let = namedtuple("Let", "Bindings Body StaticType")
      # Let_No_Init = namedtuple("Let_No_Init", "Var Type StaticType")
      # Let_Init = namedtuple("Let_Init", "Var Type Exp StaticType")
      #type check initialization

      binding_list = e[1].Bindings
      # new_bindings = []
      # for i in range(len(binding_list)):
      #   e1 = typecheck(o, m, c, e[1].Bindings)
      binding = binding_list[0]
      e1 = typecheck(o, m, c, (binding.Var.loc, binding))
      extended_o = copy.deepcopy(o)
      extended_o[c][e1[1].Var.str] = e1[1].StaticType
      #type check body with modified environment
      e2 = typecheck(extended_o, m, c, e[1].Body)
      checked_e = e[1]._replace(Bindings=e1, Body=e2, StaticType=e2[1].StaticType)
      return (line_num, checked_e)
    
    elif exp_kind == 'let_init':
      if e[1].Type.str not in all_classes and e[1].Type.str != 'SELF_TYPE':
        print(f"ERROR: {e[0]}: Type-Check: unknown type {e[1].Type.str}")
        exit(1)

      #Type (can be SELF_TYPE)
      if e[1].Type == "SELF_TYPE": var_type = c
      else: var_type = e[1].Type.str

      #Type check
      e1 = typecheck(o, m, c, e[1].Exp)
      #REMOVE
      if not is_subtype(c, e1[1].StaticType, var_type):
        print(f"ERROR: {e[1].Exp[0]}: Type-Check: initializer type {e1[1].StaticType} does not conform to type {var_type}")
        exit(1)
      checked_e = e[1]._replace(Exp=e1, StaticType=e1[1].StaticType)
      return (1, checked_e)
      
    elif exp_kind == 'let_no_init':
      if e[1].Type.str not in all_classes and e[1].Type.str != 'SELF_TYPE':
          print(f"ERROR: {e[0]}: Type-Check: unknown type {e[1].Type.str}")
          exit(1)

      if e[1].Type.str == "SELF_TYPE": var_type = c
      else: var_type = e[1].Type.str

      checked_e = e[1]._replace(StaticType=var_type)
      return (1, checked_e)

    elif exp_kind == 'case':
      #Case = namedtuple("Case", "Exp Elements StaticType")
      #Case_element = namedtuple("Case_element", "Var Type Body StaticType")
      checked_e = typecheck(o, m, c, e[1].Exp)
      case_elements = e[1].Elements
      checked_elements = []
      element_types = []
      for i in range(len(case_elements)):
        extended_o = copy.deepcopy(o)
        extended_o[c][case_elements[i].Var.str] = case_elements[i].Type.str
        elem = typecheck(extended_o, m, c, (case_elements[i].Var.loc, case_elements[i]))
        if elem[1].Type.str not in all_classes:
          print(f"ERROR: {elem[0]}: Type-Check: unknown type {elem[1].Type.str}")
          exit(1)
        if elem[1].Type.str in element_types:
          print(f"ERROR: {elem[0]}: Type-Check: case branch type {elem[1].Type.str} is bound twice")
          exit(1)
        element_types.append(elem[1].Type.str)
        checked_elements.append(elem)

      static_type = (checked_elements[0])[1].StaticType
      for elem in checked_elements[1:]:
        static_type = find_lub(c, static_type, elem[1].StaticType)
      e = e[1]._replace(Exp=checked_e, Elements=checked_elements, StaticType=static_type)
      return (line_num, e)


    elif exp_kind == 'case_element':
      checked_e = typecheck(o, m, c, e[1].Body)
      return (line_num, Case_element(e[1].Var, e[1].Type, checked_e, checked_e[1].StaticType))

    elif exp_kind == 'while':
      # While = namedtuple("While", "Predicate Body StaticType") 
      e1 = typecheck(o, m, c, e[1].Predicate)
      if e1[1].StaticType != 'Bool':
        print(f"ERROR: {e1[0]}: Type-Check: predicate has type {e1[1].StaticType} instead of Bool")
        exit(1)
      e2 = typecheck(o, m, c, e[1].Body)
      return (line_num, While(e1, e2, "Object"))
    
    elif exp_kind == 'isVoid':
      e1 = typecheck(o, m, c, e[1].Exp)
      checked_e = e[1]._replace(Exp=e1, StaticType="Bool")
      return (line_num, checked_e) 

    elif exp_kind == 'not':
      e1 = typecheck(o, m, c, e[1].Exp)
      if e1[1].StaticType != 'Bool':
        # Get actual line number
        print(f"Error: {line_num} Not a boolean expression")
        exit(1)
      checked_e = e[1]._replace(Exp=e1, StaticType="Bool")
      return (line_num, checked_e) 
    
    elif exp_kind == 'negate':
      e1 = typecheck(o, m, c, e[1].Exp)
      static_type = e1[1].StaticType
      if e1[1].StaticType == 'SELF_TYPE': static_type = c
      if static_type == 'void' or static_type != 'Int':
        # Get actual line number
        print(f"ERROR: {e[0]}: Type-Check: negate applied to type {static_type} instead of Int")
        exit(1)
      checked_e = e[1]._replace(Exp=e1, StaticType="Int")
      return (line_num, checked_e) 
    
    elif exp_kind in ['eq', 'lt', 'le']:
      # Lt = namedtuple("Lt", "Left Right StaticType")
      # Le = namedtuple("Le", "Left Right StaticType")
      # Eq = namedtuple("Eq", "Left Right StaticType")
      e1 = typecheck(o, m, c, e[1].Left)
      e1Type = e1[1].StaticType
      e2 = typecheck(o, m, c, e[1].Right)
      e2Type = e2[1].StaticType
      if e1Type == "SELF_TYPE":
        e1Type = c
      if e2Type == "SELF_TYPE":
        e2Type = c
      if e2Type in ['Int', 'String', 'Bool']:
        if e1Type != e2Type:
          print(f"ERROR: {line_num}: Type-Check: comparison between {e1Type} and {e2Type}")
          exit(1)

      e = e[1]._replace(Left=e1, Right=e2, StaticType="Bool")
      return (line_num, e)

    else:
      print("ERROR: TYPE NOT FOUND: ")
      print(e)
      exit(1)
        
  type_filename = (sys.argv[1])[:-4] + '-type'
  fout = open(type_filename , 'w')

  def print_id(id):
    fout.write(id.loc + '\n')
    fout.write(id.str + '\n')

  def print_list(list, print_func): # Higher order function
    for elem in list:
      print_func(elem)
  
  def print_element(element):
    print_id(element[1].Var)
    print_id(element[1].Type)
    print_exp(element[1].Body)
  
  # def print_binding(binding):
  #   exp_name = type(binding).__name__.lower()
  #   fout.write(exp_name + '\n')
  #   print_id(binding.Var)
  #   print_id(binding.Type)

  def print_exp(e):
    # For everything other than these given functions, fout.write line number
    # fout.write(e)
    # print(e)
    exp_name = type(e[1]).__name__.lower()
    e_line = e[0]
    fout.write(str(e_line) + '\n')
    if exp_name not in ['let_init', 'let_no_init']:
      fout.write(str(e[1].StaticType) + '\n') 
    if exp_name in ['identifier']:
      fout.write('identifier' + '\n')
      print_id(e[1].Var)
    # Output expression \n x:exp y:exp
    elif exp_name in ['plus','times', 'eq', 'le', 'lt', 'minus', 'divide']:
      fout.write(exp_name + '\n')
      print_exp(e[1].Left)
      print_exp(e[1].Right)
    # Output integer or string then \n the_integer_constant \n
    elif exp_name in ['integer', 'string']:
      fout.write(exp_name + '\n')
      fout.write(e[1][0] + '\n')
    # Just Output true or false
    elif exp_name in ['true', 'false']:
      fout.write(exp_name + '\n')
    # Output expression \n x:exp
    elif exp_name in ['not', 'negate', 'isvoid']:
      fout.write(exp_name + '\n')
      print_exp(e[1].Exp)
    # Output expression \n variable:identifier
    elif exp_name in ['new']:
      fout.write(exp_name + '\n')
      print_id(e[1].Type)
    elif exp_name in ['while']:
      fout.write(exp_name + '\n')
      print_exp(e[1].Predicate)
      print_exp(e[1].Body)
    elif exp_name in ['block']:
      fout.write(exp_name + '\n')
      fout.write(str(len(e[1].Body)) + '\n')
      print_list(e[1].Body, print_exp)
    elif exp_name in ['if']:
      fout.write(exp_name + '\n')
      print_exp(e[1].Predicate)
      print_exp(e[1].Then)
      print_exp(e[1].Else)
    elif exp_name == 'dynamic_dispatch':
      fout.write(exp_name + '\n')
      print_exp(e[1].Exp)
      print_id(e[1].Method)
      fout.write(str(len(e[1].Args)) + '\n')
      print_list(e[1].Args, print_exp)
    elif exp_name == 'static_dispatch':
      fout.write(exp_name + '\n')
      print_exp(e[1].Exp)
      print_id(e[1].Type)
      print_id(e[1].Method)
      fout.write(str(len(e[1].Args)) + '\n')
      print_list(e[1].Args, print_exp)
    elif exp_name == 'self_dispatch':
      fout.write(exp_name + '\n')
      print_id(e[1].Method)
      fout.write(str(len(e[1].Args)) + '\n')
      print_list(e[1].Args, print_exp)
    elif exp_name == 'assign':
      fout.write(exp_name + '\n')
      print_id(e[1].Var)
      print_exp(e[1].Exp) 
    elif exp_name == 'let':
      fout.write(exp_name + '\n')
      print_exp(e[1].Bindings)
      print_exp(e[1].Body)
    elif exp_name == 'let_no_init':
      fout.write("let_binding_no_init" + '\n')
      print_id(e[1].Var)
      print_id(e[1].Type)
    elif exp_name == 'let_init':
      fout.write("let_binding_init" + '\n')
      print_id(e[1].Var)
      print_id(e[1].Type)
      print_exp(e[1].Exp)
    elif exp_name == 'case':
      fout.write(exp_name + '\n')
      print_exp(e[1].Exp)
      fout.write(str(len(e[1].Elements)) + '\n')
      print_list(e[1].Elements, print_element)
    else:
      print(exp_name)
      print(e)
      print("unhandled expression")
      exit(1)

  # Print out attributes of a class
  def print_attributes(c):
    m = copy.deepcopy(method_dict)
    inherited_c = None
    if c.Inherits != None:
      inherited_c = mappedClassNames.get((c.Inherits).str)
    if inherited_c != None and inherited_c.Name.str not in base_classes:
      print_attributes(inherited_c)
    for f in c.Features:
      if type(f).__name__.lower() == "attribute":
        if f.Initializer == None: fout.write("no_initializer" + '\n')
        else: fout.write("initializer" + '\n')
        if f.Name.str == 'self':
          print(f"ERROR: {f.Name.loc}: Type-Check: class {c.Name.str} has an attribute named self")
          exit(1)
        if f.Type.str not in all_classes and f.Type.str != 'SELF_TYPE':
          print(f"ERROR: {f.Name.loc}: Type-Check: class {c.Name.str} has attribute {f.Name.str} with unknown type {f.Type.str}")
          exit(1)
        fout.write(f.Name.str + '\n')
        fout.write(f.Type.str + '\n')
        if f.Initializer != None: 
          extended_o = copy.deepcopy(attribute_dict)
          extended_o[c.Name.str][f.Name.str] = f.Type.str
          extended_o[c.Name.str]['self'] = 'SELF_TYPE'
          e = typecheck(extended_o, m, c.Name.str, f.Initializer)
          if not is_subtype(cName, e[1].StaticType, f.Type.str):
            print(f"ERROR: {e[0]}: Type-Check: {e[1].StaticType} does not conform to {f.Type.str} in initialized attribute")
            exit(1)
          print_exp(e)
    
  
  def print_class_map():
    fout.write("class_map" + '\n')
    fout.write(str(len(all_classes)) + '\n')
    all_classes.sort()
    for cName in all_classes:
      c = mappedClassNames.get(cName)
      fout.write(cName + '\n')
      # TODO: Check this
      if attribute_dict.get(cName) != None:
        attribute_lst = attribute_dict.get(cName).keys()
      else:
        attribute_lst = []
      if cName in base_classes or len(attribute_lst) == 0:
        fout.write("0\n")
      else: 
        fout.write(str(len(attribute_lst)) + '\n')
        print_attributes(c)
  
  def print_parent_map():
    fout.write("parent_map" + '\n')
    fout.write(str(len(all_classes) - 1) + '\n')
    for cName in sorted(parent_dict.keys()):
      if cName == "Object":continue
      fout.write(cName + '\n')
      fout.write(parent_dict[cName][-1] + '\n')

  def print_implementation_map():
    o = copy.deepcopy(attribute_dict)
    m = copy.deepcopy(method_dict)
    fout.write("implementation_map" + '\n')
    fout.write(str(len(all_classes)) + '\n')
    alpha_class_lst = sorted(all_classes)
    for cName in alpha_class_lst:
      # print(cName)
      fout.write(cName + '\n')
      methods_lst = method_dict[cName]
      # print(methods_lst)
      fout.write(str(len(methods_lst)) + '\n')
      for methodName in methods_lst.keys():
        method = methods_lst.get(methodName)
        fout.write(method.Name.str + '\n')
        formals_lst = method.Formals
        fout.write(str(len(formals_lst)) + '\n')
        for formal in formals_lst:
          fout.write(formal.Name.str + '\n')
        method_overriden = True
        if methodName not in own_methods[cName]:
          for parent in reversed(parent_dict[cName]):
            if methodName in own_methods[parent]:
              fout.write(parent + '\n')
              break
              # This if statement is not working/printing sometimes
          if parent in base_classes:
            fout.write('0' + '\n')
            fout.write(method.ReturnType.str + '\n')
            fout.write('internal' + '\n')
            fout.write(parent + '.' + methodName + '\n')
          method_overriden = False
        elif cName in base_classes:
          fout.write(cName + '\n')
          fout.write('0' + '\n')
          fout.write(method.ReturnType.str + '\n')
          fout.write('internal' + '\n')
          fout.write(cName + '.' + methodName + '\n')
          method_overriden = False
        if method_overriden:
          fout.write(cName + '\n')
        if method.Body != '':
          #TODO: extend environment & do SELFTYPE STUFF
          extended_o = copy.deepcopy(o)
          for formal in method.Formals:
            extended_o[cName][formal.Name.str] = formal.Type.str
            if formal.Name.str == 'self':
              print(f"ERROR: {method.Name.loc}: Type-Check: class {cName} has method {method.Name.str} with formal parameter named self")
              exit(1)
          extended_o[cName]['self'] = 'SELF_TYPE'
          if method.ReturnType.str not in all_classes and method.ReturnType.str != 'SELF_TYPE':
            print(f"ERROR: {method.Name.loc}: Type-Check: class {cName} has method {method.Name.str} with unknown return type {method.ReturnType.str}")
            exit(1)
          e = typecheck(extended_o, m, cName, method.Body)
          declared_returned = method.ReturnType.str
          if declared_returned == 'SELF_TYPE': t_0 = cName
          else: t_0 = e[1].StaticType
          if not is_subtype(cName, e[1].StaticType, t_0):
            print(f"ERROR: {method.Name.loc}: Type-Check: {e[1].StaticType} does not conform to {declared_returned} in method {methodName}")
            exit(1)
          print_exp(e)

  def print_formal(formal):
    print_id(formal.Name)
    print_id(formal.Type)
  
  def print_ast ():
    o = copy.deepcopy(attribute_dict)
    # TODO: set m = method_dict
    m = copy.deepcopy(method_dict)
    fout.write(str(len(user_classes)) + '\n')
    for c in ast:
      fout.write(c.Name.loc + '\n')
      fout.write(c.Name.str + '\n')
      if c.Inherits != None:
        fout.write("inherits" + '\n')
        print_id(c.Inherits)
      else:
        fout.write("no_inherits" + '\n')
      fout.write(str(len(c.Features)) + '\n')
      for f in c.Features:
        if type(f).__name__.lower() == 'attribute':
          if f.Initializer == None:
            fout.write("attribute_no_init" + '\n')
            print_id(f.Name)
            print_id(f.Type)
          else:
            fout.write("attribute_init" + '\n')
            print_id(f.Name)
            print_id(f.Type)
            extended_o = copy.deepcopy(o)
            extended_o[c.Name.str][f.Name.str] = f.Type.str
            extended_o[c.Name.str]['self'] = 'SELF_TYPE'
            e = typecheck(extended_o, m, c.Name.str, f.Initializer)
            print_exp(e)
        else:
          fout.write("method" + '\n')
          print_id(f.Name)
          fout.write(str(len(f.Formals)) + '\n')
          print_list(f.Formals, print_formal)
          print_id(f.ReturnType)
          extended_o = copy.deepcopy(o)
          for formal in f.Formals:
            extended_o[c.Name.str][formal.Name.str] = formal.Type.str
          extended_o[c.Name.str]['self'] = 'SELF_TYPE'
          e = typecheck(extended_o, m, c.Name.str, f.Body)
          print_exp(e)

  
  print_class_map()
  print_implementation_map()
  print_parent_map()
  print_ast()

  
  fout.close() 

main()