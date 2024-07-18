# Prathit Kurup & Nicolas Chu DeChristofaro
# Parser for PA3 for Cool

import sys
from lex import LexToken
import yacc as yacc

# Parts of this code were modeled after PLY documentation

# Read in the CL-LEX file
tokens_filename = sys.argv[1]
tokens_filehandle = open(tokens_filename,'r')
tokens_lines = tokens_filehandle.readlines()
tokens_filehandle.close()

# Use paramater to check if string
def get_token_line(type):
    global tokens_lines
    # if string, only strip newlines
    if type == 'string':
        result = tokens_lines[0].strip('\n')
    # Otherwise strip leading and trailing whtiespace
    else: result = tokens_lines[0].strip()
    tokens_lines = tokens_lines[1:]
    return result

# Deserealize input file into tokens
pa2_tokens = []
while tokens_lines != []:
    line_num = get_token_line(None)
    token_type = get_token_line(None)
    token_lexeme = token_type
    if token_type in ['identifier', 'integer', 'type', 'string']:
        if token_type == 'string': # should not strip spaces within string
            token_lexeme = get_token_line('string')
        else: token_lexeme = get_token_line(None)
    pa2_tokens = pa2_tokens + [(line_num, token_type.upper(), token_lexeme)]

# Use PA2 Tokens as Lexer
class PA2Lexer(object):
    def token(whatever):
        global pa2_tokens
        if pa2_tokens == []:
            return None
        (line, token_type, lexeme) = pa2_tokens[0]
        pa2_tokens = pa2_tokens[1:]
        tok = LexToken()
        tok.type = token_type
        tok.value = lexeme
        tok.lineno = line
        tok.lexpos = 0
        return tok
pa2lexer = PA2Lexer()

# Given tokens for COOL
tokens = (
    'AT',
    'CASE',
    'CLASS',
    'COLON',
    'COMMA',
    'DIVIDE',
    'DOT',
    'ELSE',
    'EQUALS',
    'ESAC',
    'FALSE',
    'FI',
    'IDENTIFIER',
    'IF',
    'IN',
    'INHERITS',
    'INTEGER',
    'ISVOID',
    'LARROW',
    'LBRACE',
    'LE',
    'LET',
    'LOOP',
    'LPAREN',
    'LT',
    'MINUS',
    'NEW',
    'NOT',
    'OF',
    'PLUS',
    'POOL',
    'RARROW',
    'RBRACE',
    'RPAREN',
    'SEMI',
    'STRING',
    'THEN',
    'TILDE',
    'TIMES',
    'TRUE',
    'TYPE',
    'WHILE',
)

# Need to specify precendence rules
precedence = (
    ('right', 'LARROW'),
    ('left', 'NOT'),
    ('nonassoc', 'LE', 'LT', 'EQUALS'),
    ('left', 'MINUS', 'PLUS'),
    ('left', 'DIVIDE', 'TIMES'),
    ('left', 'ISVOID'),
    ('left', 'TILDE'),
    ('left', 'AT'),
    ('left', 'DOT') # binds more tightly
)

# Our AST is nested tuples:
#    (line_numb, AST_node_type, AST_node_child1, AST_node_child2...)

# The following functions are based on the Cool Syntax and used to build the AST

# program ::= [[class;]]+
def p_program_classlist(p):
    'program : classlist_start'
    p[0] = p[1]
def p_classlist_start(p):
    'classlist_start : class SEMI classlist'
    p[0] = [p[1]] + p[3]
def p_classlist_none(p):
    'classlist : '
    p[0] = []
def p_classlist_some(p):
    'classlist : class SEMI classlist'
    p[0] = [p[1]] + p[3]

# class ::= class TYPE [inherits TYPE]{ [[feature;]]* }
def p_class_inherit(p):
    'class : CLASS type INHERITS type LBRACE featurelist RBRACE'
    p[0] = (p.lineno(1), 'class_inherit', p[2], p[4], p[6])
def p_class_noinherit(p):
    'class : CLASS type LBRACE featurelist RBRACE'
    p[0] = (p.lineno(1), 'class_noinherit', p[2], p[4])

# Declare type and identifier for future use
def p_type(p):
    'type : TYPE'
    p[0] = (p.lineno(1), p[1])
def p_identifier(p):
    'identifier : IDENTIFIER'
    p[0] = (p.lineno(1), p[1])

# feature ::= ID : TYPE[ <- expr]
def p_featurelist_none(p):
    'featurelist : '
    p[0] = []
def p_featurelist_some(p):
    'featurelist : feature SEMI featurelist'
    p[0] = [p[1]] + p[3]
def p_feature_attribute_no_init(p):
    'feature : identifier COLON type'
    p[0] = (p.lineno(1), 'attribute_no_init', p[1], p[3])
def p_feature_attribute_init(p):
    'feature : identifier COLON type LARROW exp'
    p[0] = (p.lineno(1), 'attribute_init', p[1], p[3], p[5])
# feature ::= ID( [ formal[[,formal]]* ]):TYPE { expr }
def p_feature_method(p):
    'feature : identifier LPAREN argsFormal RPAREN COLON type LBRACE exp RBRACE'
    p[0] = ((p[1])[0], 'method', p[1], p[3], p[6], p[8])

# Form formal list with possibility of one formal, multiple, or none
def p_formalList_single_arg(p):
    'argsFormal : formal' 
    p[0] = [p[1]]
def p_formal_multi_arg(p):
    'argsFormal : formal formalList' 
    p[0] = [p[1]] + p[2]
def p_formal_no_arg(p):
    'argsFormal : '
    p[0] = []
# Piece together with comma in between
def p_formal_list_some(p):
    'formalList : COMMA formal formalList'
    p[0] = [p[2]] + p[3]
def p_formal_list_none(p):
    'formalList : '
    p[0] = []

# formal ::= ID : TYPE
def p_formal(p):
    'formal : identifier COLON type'
    p[0] = (p.lineno(1), 'formal', p[1], p[3])

# expr ::= let ID : TYPE[ <- expr][[,ID:TYPE[ <-expr]]]* in expr
def p_let(p):
    'exp : LET binding_list_start IN exp'
    p[0] = (p.lineno(1), 'let', p[2], p[4]) 
# Beginning of binding list
def p_let_binding_list_start(p):
    'binding_list_start : binding binding_list'
    p[0] = [p[1]] + p[2]
def p_let_binding_list(p):
    '''binding_list : COMMA binding binding_list
                    | '''
    if len(p) > 1: p[0] = [p[2]] + p[3]
    else: p[0] = []
# Handle whether this is an expression or not
def p_let_binding(p):
    '''binding : identifier COLON type LARROW exp
               | identifier COLON type'''
    if len(p) == 6: 
        p[0] = ((p[1])[0], 'let_binding_init', p[1], p[3], p[5]) 
    else:
        p[0] = ((p[1])[0], 'let_binding_no_init', p[1], p[3])

# expr ::= case expr of [[ID : TYPE => expr;]]+ esac
def p_case(p):
    'exp : CASE exp OF case_list_start ESAC'
    p[0] = (p.lineno(1), 'case', p[2], p[4])
def p_case_list_start(p):
    'case_list_start : case_element case_list'
    p[0] = [p[1]] + p[2]
def p_case_list(p):
    '''case_list : case_element case_list
                 | '''
    if len(p) > 1: p[0] = [p[1]] + p[2]
    else: p[0] = []
# Inner optional case element
def p_case_element(p):
    'case_element : identifier COLON type RARROW exp SEMI'
    p[0] = [(p[1])[0], 'case_element', p[1], p[3], p[5]]

# expr ::= exp.ID([expr[[,expr]]*])
def p_dynamic_dispatch(p):
    'exp : exp DOT identifier LPAREN args RPAREN'
    p[0] = ((p[1])[0], 'dynamic_dispatch', p[1], p[3], p[5])

# expr ::= exp@TYPE.ID([expr[[,expr]]*])
def p_static_dispatch(p):
    'exp : exp AT type DOT identifier LPAREN args RPAREN'
    p[0] = ((p[1])[0], 'static_dispatch', p[1], p[3], p[5], p[7])

# expr ::= ID([expr[[,expr]]*])
def p_self_dispatch(p):
    'exp : identifier LPAREN args RPAREN'
    p[0] = ((p[1])[0], 'self_dispatch', p[1], p[3])
def p_dispatch_single_arg(p):
    'args : exp' 
    p[0] = [p[1]]
# Might have  multiple arguments
def p_dispatch_multi_arg(p):
    'args : exp exp_list' 
    p[0] = [p[1]] + p[2]
def p_dispatch_no_arg(p):
    'args : '
    p[0] = []

# For use when we have a comma separated lsit of expressions
def p_exp_list_some(p):
    'exp_list : COMMA exp exp_list'
    p[0] = [p[2]] + p[3]
def p_exp_list_none(p):
    'exp_list : '
    p[0] = []

# expr ::= ID
def p_exp_identifier(p):
    'exp : identifier'
    p[0] = ((p[1])[0], 'identifier', p[1])

# For use when we have a semicolon separated lsit of expressions
def p_expBlock(p):
    'exp : LBRACE expBlock_start RBRACE'
    p[0] = (p.lineno(1), 'block', p[2])
def p_expBlock_start(p):
    'expBlock_start : exp SEMI expBlock'
    p[0] = [p[1]] + p[3]
def p_expBlock_some(p):
    'expBlock : exp SEMI expBlock'
    p[0] = [p[1]] + p[3]
def p_expBlock_none(p):
    'expBlock : '
    p[0] = []

# expr ::= ID <- expr
def p_assign(p):
    'exp : identifier LARROW exp'
    p[0] = ((p[1])[0], 'assign', p[1], p[3])

# expr ::= new TYPE
def p_exp_new(p):
    'exp : NEW type'
    p[0] = (p.lineno(1), 'new', p[2])

# expr ::= if expr then expr else expr fi
def p_exp_if(p):
    'exp : IF exp THEN exp ELSE exp FI'
    p[0] = (p.lineno(1), 'if', p[2], p[4], p[6])

# expr ::= while expr loop expr pool
def p_exp_while(p):
    'exp : WHILE exp LOOP exp POOL'
    p[0] = (p.lineno(1), 'while', p[2], p[4])


# expr ::= expr + expr
def p_exp_plus(p):
    'exp : exp PLUS exp'
    # p[0] = (p.lineno(1), 'plus', p[1], p[3])
    p[0] = ((p[1])[0], 'plus', p[1], p[3])

# expr ::= expr * expr
def p_exp_times(p):
    'exp : exp TIMES exp'
    p[0] = ((p[1])[0], 'times', p[1], p[3])

# expr ::= expr - expr
def p_exp_minus(p):
    'exp : exp MINUS exp'
    p[0] = ((p[1])[0], 'minus', p[1], p[3])

# expr ::= expr / expr
def p_exp_divide(p):
    'exp : exp DIVIDE exp'
    p[0] = ((p[1])[0], 'divide', p[1], p[3])

# expr ::= expr = expr
def p_exp_eq(p):
    'exp : exp EQUALS exp'
    p[0] = ((p[1])[0], 'eq', p[1], p[3])

# expr ::= expr <= expr
def p_exp_le(p):
    'exp : exp LE exp'
    p[0] = ((p[1])[0], 'le', p[1], p[3])

# expr ::= expr < expr
def p_exp_lt(p):
    'exp : exp LT exp'
    p[0] = ((p[1])[0], 'lt', p[1], p[3])

# expr ::= (expr)
def p_exp_paren_exp(p):
    'exp : LPAREN exp RPAREN'
    p[0] = (p.lineno(1), 'paren_exp', p[2])

# expr ::= integer
def p_exp_integer(p):
    'exp : INTEGER'
    p[0] = (p.lineno(1), 'integer', p[1])

# expr ::= string
def p_exp_string(p):
    'exp : STRING'
    p[0] = (p.lineno(1), 'string', p[1])

# expr ::= not expr
def p_exp_not(p):
    'exp : NOT exp'
    p[0] = (p.lineno(1), 'not', p[2])

# expr ::= ~ expr
def p_exp_negate(p):
    'exp : TILDE exp'
    p[0] = (p.lineno(1), 'negate', p[2])

# expr ::= isvoid expr
def p_exp_isvoid(p):
    'exp : ISVOID exp'
    p[0] = (p.lineno(1), 'isvoid', p[2])

# expr ::= true
def p_exp_true(p):
    'exp : TRUE'
    p[0] = (p.lineno(1), 'true', p[1])

# expr ::= false
def p_exp_false(p):
    'exp : FALSE'
    p[0] = (p.lineno(1), 'false', p[1])

# If does not fit grammer rules, print an error and exit
def p_error(p):
    if p:
        print("ERROR:", p.lineno, ": Parser: syntax error near", p.value)
        # Just discard the token and tell the parser it's okay.
        exit(1)
    if p == None:
        print("ERROR: 1: Parser: syntax error near")
        exit(1)
    else:
        print("ERROR: Syntax error at EOF")
        exit(1)

parser = yacc.yacc() 
ast = yacc.parse(lexer=pa2lexer) # Build the AST!

# Output a PA3 Parser from the above rules
ast_filename = (sys.argv[1])[:-4] + "-ast"
fout = open(ast_filename , 'w')

# Define a number of print_foo() methods that call each other to serialize AST
def print_list(ast, print_element_function): # Higher order function
    fout.write(str(len(ast)) + "\n")
    for elem in ast:
        print_element_function(elem)

# Output source-file line number, then a newline, then the identifier string, then a newline
def print_identifier(ast):
    # ast = (p. lineno(1), p[11)
    fout.write(str(ast[0]) + "\n")
    fout.write(ast[1] + "\n" )

def print_exp(ast):
    # For everything other than these given functions, print line number
    if ast[1] not in ['paren_exp', 'let_binding_init', 'let_binding_no_init', 'case_element']:
        fout.write(str(ast[0]) + "\n")
    if ast[1] in ['paren_exp']:
        print_exp(ast[2]) 
    # Output expression \n x:exp y:exp
    elif ast[1] in ['plus','times', 'eq', 'le', 'lt', 'minus', 'divide', 'while']:
        fout.write(ast[1] + "\n")
        print_exp(ast[2])
        print_exp(ast[3])
    # Output integer or string then \n the_integer_constant \n
    elif ast[1] in ['integer', 'string']:
        fout.write(ast[1] + "\n")
        fout.write(str(ast[2]) + "\n")
    # Just Output true or false
    elif ast[1] in ['true', 'false']:
        fout.write(ast[1] + "\n")
    # Output expression \n x:exp
    elif ast[1] in ['not', 'negate', 'isvoid']:
        fout.write(ast[1] + "\n")
        print_exp(ast[2])
    # Output expression \n variable:identifier
    elif ast[1] in ['identifier', 'new']:
        fout.write(ast[1] + "\n")
        print_identifier(ast[2])
    # Output if \n predicate:exp then:exp else:exp
    elif ast[1] in ['if']:
        fout.write(ast[1] + "\n")
        print_exp(ast[2])
        print_exp(ast[3])
        print_exp(ast[4])
    # Output block \n body:exp-list
    elif ast[1] in ['block']:
        fout.write(ast[1] + "\n")
        print_list(ast[2], print_exp)
    # Output dynamic_dispatch \n e:exp method:identifier args:exp-list
    elif ast[1] in ['dynamic_dispatch']:
        fout.write(ast[1] + "\n")
        print_exp(ast[2])
        print_identifier(ast[3])
        print_list(ast[4], print_exp)
    # Output static_dispatch \n e:exp type:identifier method:identifier args:exp-list
    elif ast[1] in ['static_dispatch']:
        fout.write(ast[1] + "\n")
        print_exp(ast[2])
        print_identifier(ast[3])
        print_identifier(ast[4])
        print_list(ast[5], print_exp)
    # Output self_dispatch \n method:identifier args:exp-list
    elif ast[1] in ['self_dispatch']:
        fout.write(ast[1] + "\n")
        print_identifier(ast[2])
        print_list(ast[3], print_exp)
    # Output let \n binding-list
    elif ast[1] in ['let']:
        fout.write(ast[1] + "\n")
        print_list(ast[2], print_exp)
        print_exp(ast[3])
    # Output let_binding_init \n variable:identifier type:identifier value:exp
    elif ast[1] in ['let_binding_init']:
        fout.write(ast[1] + "\n")
        print_identifier(ast[2])
        print_identifier(ast[3])
        print_exp(ast[4])
    # Output let_binding_no_init \n variable:identifier type:identifier
    elif ast[1] in ['let_binding_no_init']:
        fout.write(ast[1] + "\n")
        print_identifier(ast[2])
        print_identifier(ast[3]) 
    # Output assign \n var:identifier rhs:exp
    elif ast[1] in ['assign']:
        fout.write(ast[1] + "\n")
        print_identifier(ast[2])
        print_exp(ast[3])
    # Output case \n case-exp case-element
    elif ast[1] in ['case']:
        fout.write(ast[1] + "\n")
        print_exp(ast[2])
        print_list(ast[3], print_exp)
    # Output variable as an identifier, then the type as an identifier, then the case-element-body as an exp
    elif ast[1] in ['case_element']:
        print_identifier(ast[2])
        print_identifier(ast[3])
        print_exp(ast[4])
    # Catch unhandled expressions
    else:
        print("unhandled expression")
        exit(1)

# Output name as an identifier on line and then the type as an identifier on a line
def print_formal(ast):
    print_identifier(ast[2])
    print_identifier(ast[3])

# Outout name of the feature and then a newline, then subparts
def print_feature(ast):
    # Output attribute_no_init \n name:identifier type:identifier
    if ast[1] == 'attribute_no_init':
        fout.write("attribute_no_init\n")
        print_identifier(ast[2])
        print_identifier(ast[3])
    # Output attribute_init \n name:identifier type:identifier init:exp
    elif ast[1] == 'attribute_init':
        fout.write("attribute_init\n")
        print_identifier(ast[2])
        print_identifier(ast[3])
        print_exp(ast[4])
    # Output method \n name:identifier formals-list \n type:identifier body:exp
    elif ast[1] == 'method':
        fout.write(ast[1] + "\n")
        print_identifier(ast[2])
        print_list(ast[3], print_formal)
        print_identifier(ast[4])
        print_exp(ast[5])
    else:
        print("unhandled expression")
        exit(1)
    

def print_class(ast):
    # ast = (p. lineno (1), 'class_noinherit', p[2] name, p[4] feature list)
    print_identifier(ast[2]) # output class name
    # Then output inherits \n superclass:identifier
    if ast[1] == 'class_inherit':
        fout.write("inherits\n")
        print_identifier(ast[3])
        print_list(ast[4], print_feature)
    # Otherwise  output no_inherits \n
    else:
        fout.write("no_inherits\n")
        print_list(ast[3], print_feature)

# A Cool AST is a list of classes. Output the list of classes.
def print_program(ast):
    print_list(ast, print_class)

print_program(ast)
fout.close()