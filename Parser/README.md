This folder contains the parser for COOL and a few test files we created. The parser takes in a cl-lex file and indicates
that either there is an error in the Cool program described by the cl-lex file (e.g., a parse error in the Cool file) 
or it will emit a file.cl-ast, a serialized Cool abstract syntax tree for use in the semantic analyzer.
