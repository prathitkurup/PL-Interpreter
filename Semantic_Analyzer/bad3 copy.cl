class Main {
    int_test : Int <- 3;
    string_test : Object <- while (false) loop {
        int_test = int_test + 1;
        if (true) then
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
    
} ;

class FirstClass inherits IO {
    -- t : Object <- main();
    -- n : Int <- my_str@String.length();
};

class SecondClass inherits FirstClass {
    testmethod(num : Int) : Object {3};
    a : Object;

} ;

class ThirdClass inherits SecondClass{
    z : Int;
    -- We should not be able to redefine attributes
    a : Object <- 3 ;
    my_str : String <- "my string";
    x : Int <- my_str@String.length();
} ;
