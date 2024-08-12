# PL-Interpreter
CSCI 2320 Principles of Programming Languages - Classroom Object Oriented Language Interpreter

The objective of this course was to construct an interpreter for the Classroom Object Oriented Language (COOL). This involves scanning, parsing, type-checking and interpreting code. Cool is an imperative, strongly-typed classroom object-oriented programming language that represents a subset of Java.

Each phase covers one component of the interpreter: lexical analysis, parsing, semantic analysis, and operational semantics. The phases collectively result in a working interpreter phase which can interface with the other phases.

**Phase 1: Lexical Analyzer**
We wrote a lexical analyzer, or scanner, using the [PLY](http://www.dabeaz.com/ply/) lexical analyzer generator. The program serializes and outputs the tokens for the Cool program it is fed. 

**Phase 2: Parser**
For this phase, we wrote a parser program using a parser generator. The parser uses the lexed .cl file and describes the Cool grammar for the parser generator. Cool tokens are unserialized to produce an abstract syntax tree (AST).

**Phase 3: Semantic Analyzer**
The semantic analyzer, or type-checker, unserializes the AST to create a class map, parent map, implementation map, and an annotated AST. The program also rejects poorly typed Cool programs.

**Phase 4: Interpreter**
For the final phase, we wrote a Cool interpreter to implement the operational seantics of the language. The program uses the maps produced my the Semantic Analyzer to actually interpret the program and produce output. The program also catches run-time errors.
