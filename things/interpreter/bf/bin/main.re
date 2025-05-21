// let memory_size = 128;
// let memory = Array.make(memory_size, 0);
let instruction_pointer = ref(0);
// let memory_pointer = ref(0);
// let address_stack: list<int> = [];

type operation =
 | Forward
 | Backward
 | Increment
 | Decrement
 | Print
 | JumpIfZero
 | JumpIfValue;

 let print_operation = (op: operation) => {
   let operation_name: string = switch(op) {
   | Forward => "Forward"
   | Backward => "Backward"
   | Increment => "Increment"
   | Decrement => "Decrement"
   | Print => "Print"
   | JumpIfZero => "JumpIfZero"
   | JumpIfValue => "JumpIfValue"
   };
   print_endline(operation_name);
}

 let program = "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.";

let () = {
  print_endline("Brainfuck Interpreter v1.0.0");

  let tokens: array<char> = program 
    |> String.to_seq 
    |> Array.of_seq;

  print_endline("Tokens:");
  tokens
  |> Array.iter((token: char) => {
    print_char(token);
    print_string(" ");
  });
  print_endline("");

  let parse_token = (token: char): operation => {
    let operation: option<operation> = switch(token) {
    | '+' => Some(Increment)
    | '-' => Some(Decrement)
    | '>' => Some(Forward)
    | '<' => Some(Backward)
    | '.' => Some(Print)
    | '[' => Some(JumpIfZero)
    | ']' => Some(JumpIfValue)
    | _ => raise(Exit)
    };
    operation |> Option.get
};

  print_endline("Parsed Operations:");
  let print_int = (i: int) => {
    print_string(Int.to_string(i));
  };

  let ops: array<operation> = {
    tokens
    |> Array.map(parse_token)
  };
  print_endline("----------------------");
  while (instruction_pointer^ < Array.length(ops)) {
    instruction_pointer^ |> print_int;
    print_string(" | ");
    Array.get(ops, instruction_pointer^) |> print_operation;
    instruction_pointer := Int.add(instruction_pointer^, 1);
    ();
  }
  print_endline("----------------------");
};
