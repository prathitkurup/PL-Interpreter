class Main {
    main(): Object {
        {
            -- Test let statements
            let x: Int <- 5, y: Int <- 10 in
            {
                -- Test if statements and comparisons
                if x < y then
                    -- Test dispatch with new
                    (new IO).out_string("x is less than y\n")
                else
                    (new IO).out_string("x is not less than y\n")
                fi;
                x <- x + y;
                y <- x - y;
                x <- x - y;
                -- Test printing mutiple values with new IO
                (new IO).out_string("After swap, x is ").out_int(x).out_string(" and y is ").out_int(y).out_string("\n");
            };
            -- Test new object creation
            let my_first : FirstClass <- new FirstClass in
            my_first.first();
        }
    };
};

class FirstClass inherits IO {
    first(): Object {
        {
            let my_int: Int <- 10 in
            {
                -- Test some internals
                out_string("Created a new Int: ");
                out_int(my_int);
                out_string("\n");
            };
        }
    };
};
