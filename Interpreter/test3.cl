class Main inherits IO {
    i : Int <- 0;
    main() : Object {
        while (i < 10) loop {
            {
                -- Calls IO out_string method instead of overriden definition
                self@IO.out_string("IO Out_string call\n");
                i <- i + 1;
            };
        } pool
    } ; 

    out_string(s : String) : SELF_TYPE {
        {
            abort();
            self;
        }
    };
};