class Main inherits IO {
  x : Int <- 123 + 456 * 789 ;
  y : Bool <- true ;
  z : Bool <- false ;
  sum : Int <- (9 + 7);
  my_bool : Bool <- 4 = 5;
  boolio : Bool <- 4 <= 5;
  goolio : Bool <- 4 < 5;
  my_bool2 : Bool <- not y;
  check_precedence : Int <- 8 - 3 / 1 ; 
  testing_tilde : Bool <- ~ z;
  testing_void : Bool <- isvoid y;
  cat : Object <- new Object;
  blocky : Int <- {
    if 1 = 2
    then 1
	  else 1
	  fi;
    -- case test
    case var of
      x : Int => out_string("Class type is now A\n");
    esac;

    -- self dispatch test
    out_string("hey");

    let num : Int <- 2, str : String in
      while num < 5 loop 
        {
          num <- num + 1;
          
        }
      pool;
  }; 
  str : String <- "test";
  -- dynamic dispatch test (this should fail!!)
  len : Int <- str@substr(4,1);

  method1(num : Int, num2 : Int, num3 : Int) : SELF_TYPE {
      self
   };

  str : String <- "testing whitespace ";
} ;




