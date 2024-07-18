# Nick Chu DeChristofaro and Prathit Kurup
# This is a lexer for Cool (PA2)
# Portions of this code were adpated from the PLY documentation

import sys
import ply.lex as lex
# import lex as lex

# reserved keywords for reference
reserved = ['case',
            'class',
            'else',
            'esac',
            'fi',
            'if',
            'in',
            'inherits',
            'isvoid',
            'let',
            'loop',
            'new',
            'not',
            'of',
            'pool',
            'then',
            'while'
            ]

# List of token names.
tokens = (
   'at',
   'case',
   'class',
   'colon',
   'comma',
   'divide',
   'dot',
   'else',
   'equals',
   'esac',
   'false',
   'fi',
   'if',
   'in',
   'inherits',
   'integer',
   'isvoid',
   'larrow',
   'lbrace',
   'le',
   'let',
   'loop',
   'lparen',
   'lt',
   'minus',
   'new',
   'not',
   'of',
   'plus',
   'pool',
   'rarrow',
   'rbrace',
   'rparen',
   'semi',
   'string',
   'then',
   'tilde',
   'times',
   'true',
   'while',
   'type',
   'identifier' # used to catch identifiers, keywords, and types
)

# Regular expression rules for simple tokens
t_at = r'@'
t_colon = r':'
t_comma = r","
t_divide  = r'/'
t_dot = r'\.'
t_equals = r'='
t_larrow = r'<-'
t_lbrace = r'\{'
t_le = r'<='
t_lparen  = r'\('
t_lt = r'<'
t_minus = '-'
t_plus = r'\+'
t_rarrow = '=>'
t_rbrace = r'\}'
t_rparen  = r'\)'
t_semi = r';'
t_tilde = r'~'
t_times = r'\*'

# First type of comment with a dash
def t_dash_comment(t):
    r'--.*'
    pass

# Declare the state (to deal with multiline comments)
states = (
    ('comment', 'exclusive'),
)

# Adapted from PLY documentation, section 4.19 : Conditional lexing and start conditions
# Match the first comment opener, and enter the comment state
def t_comment(t):
    r'\(\*'
    t.lexer.level = 1 # initial comment ( '(*' ) level
    t.lexer.begin('comment') # enter the 'comment' state

def t_comment_start(t):
    r'\(\*'
    t.lexer.level += 1 # advance a level because another comment began

def t_comment_end(t):
    r'\*\)'
    t.lexer.level -= 1 # go back a level because comment ends
    # when all open comments have been closed...
    if t.lexer.level == 0:
        t.lexer.begin('INITIAL')           
        pass

def t_comment_content(t):
    r'([^\\]|(\\.))+?' # anything inside the comment
    t.lexer.lineno += t.value.count('\n')
    pass

def t_comment_error(t):
    print("ERROR: %d: Lexer: invalid character: %s" % (t.lexer.lineno, t.value[0]))
    exit(1)

t_comment_ignore = " \t"

# If the comment has not been closed before the EOF:
def t_comment_eof(t):
    print("ERROR: %d: Lexer: EOF in (* comment *)" % t.lexer.lineno)
    exit(1)

def t_string(t):
    r'\"([^\\\n\0]|(\\.))*?\"'
    t.value = t.value[1:-1] # do not include the quotation marks
    # Handle strings that are too long
    if len(t.value) > 1024:
        print("ERROR: %d: Lexer: string constant is too long (%d > 1024)" % (t.lexer.lineno, len(t.value)))
        exit(1)
    return t

def t_true(t):
    r't[rR]{1}[uU]{1}[eE]{1}' # ensures 'true' keyword stats with a lowercase t
    t.type = 'true'
    return t

def t_false(t):
    r'f[aA]{1}[lL]{1}[sS]{1}[eE]{1}' # ensures 'false' keyword stats with a lowercase f
    t.type = 'false'
    return t

# Includes handling of keywords, types, and identifiers
def t_identifier(t):
    r'([a-zA-Z][a-zA-Z_0-9]*)' 
    # check if a keyword
    if t.value.lower() in reserved:
        t.type = t.value.lower()
    # check if a type (starts with uppercase)
    elif t.value[0].isupper():
        t.type = 'type'
    # otherwise it is an identifier
    return t

def t_integer(t):
    r'[0-9]+'
    t.value = int(t.value)
    # Error handling for integers that are too long
    if t.value > 2147483647:
        print("ERROR: %d: Lexer: not a non-negative 32-bit signed integer: %d" % (t.lexer.lineno, t.value))
        exit(1)
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters 
t_ignore  = ' \t\r\f\v' #whitespace

# General error handling rule
def t_error(t):
    print("ERROR: %d: Lexer: invalid character: %s" % (t.lexer.lineno, t.value[0]))
    exit(1)

# Build the lexer
lexer = lex.lex()

# Run the lexer
filename = sys.argv[1]
file_handle = open (filename, "r")
file_contents = file_handle.read()
lexer.input(file_contents)

out_string = ""
# Tokenize
while True:
    tok = lexer.token()
    if not tok: 
        break      # No more input
    out_string += str(tok.lineno) + "\n"
    out_string += str(tok.type) + "\n"
    # For given token types, print out lexeme
    if tok.type in ['identifier','integer','string','type']: out_string += str(tok.value) + "\n"

outfile = open(sys.argv[1] + "-lex", 'w')
outfile.write(out_string)
outfile.close()