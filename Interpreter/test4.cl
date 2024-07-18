-- Substring out of range Testcase

class Main inherits IO {
    main() : Object {
        let str : String <- "Hello, Professor Weimer!" in
            out_string(str.substr(0, 30))  -- This will cause a runtime error
    };
};