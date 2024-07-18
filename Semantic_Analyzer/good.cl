class Main {
    int_test : Int <- 3;
    string_test : Object <- while (false) loop {
        int_test = int_test + 1;
        if (not true) then
            int_test = int_test - 5
        else
            false
        fi;
        int_test <- 5;
    } pool;
    string_t : String <- "hello";
    -- leng : Int <- string_t.length();
    main() : Object {3} ;
    my_method(num : Int, str : String) : Object {

    let test_obj : Int <- 3 in 
        let t_obj2 : Object in (
        test_obj 
    )
    } ;
    
    new_obj : Object <- main();
} ;

class FirstClass inherits IO {
    t : String;
    n : Int <- t.length();
    neg_n : Int <- ~n;
    myMethod() : Object {
        while n <= 5 loop 
        {
            neg_n <- neg_n * 3;
            n <- n + 1;
        } 
        pool
    };
};

class SecondClass inherits FirstClass {
    a : Object <- case self of
		      n : Int => out_string("well hello there");
		      n : String => out_string("ruh rho raggy");
		      n : Bool => out_string("i am an output string");
   	         esac;
    testmethod(num : Int) : Object {3};
} ;

class ThirdClass inherits SecondClass{
    z : Int;
    my_str : String <- "my string";
    x : Int <- my_str@String.length();
    test_new : SecondClass <- new SecondClass;
} ;
