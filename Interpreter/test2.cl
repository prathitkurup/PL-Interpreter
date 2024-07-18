class Main inherits IO {
    new_b : B;
    basic_test : Object <- new Object;
    x : Int <- 15;
    con_test : String <- "hey";
    sub_test : String <- "watermelon";
    
    main() : Object {
        let test_let : Int <- 2, test_let : Int in
        {
            case_test(new_b <- new B);
            out_int(x);
        }
    } ;

    -- This method overrides the built-in out_int method of the IO class
    out_int(x : Int) : SELF_TYPE {
       
        {
            out_string("out_int\n");
            self;
        }
    };

    -- Case test
    case_test(var : B) : SELF_TYPE {
        case var of
	    a : Object => out_string("Class type is now ob\n");
	    b : Int => out_string("Class type is now int\n");
	    c : C => out_string("Class type is now C\n");
        d : B => out_string("Class type is now B\n");
        esac
    };
};

class A inherits IO {
};

class B inherits A {
    hehe : SELF_TYPE <- out_string("Viking Bride\n");
};

class C inherits B {
    my_a : String <- "check";
};

