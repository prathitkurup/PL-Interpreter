This is the semantic analyzer that uses an abstract syntax tree file as input to determine whether the program typechecks.
The program either indicates that there is an error in the input (e.g., a type error) or emit file.cl-type, which includes 
a serialized Cool abstract syntax tree, class map, implementation map, and parent map for use in the final interpreter.
