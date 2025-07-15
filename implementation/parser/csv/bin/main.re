let parseLine = (line: string) => String.split_on_char(',', line);

let parseContent = (content: string): list(list(string)) => {
  print_endline("=== IN ===");
  print_endline(content);
  let lines = String.split_on_char('\n', content);
  let parsed = List.map(line => parseLine(line), lines);
  parsed;
};

let cli = (args: array(string)): unit => {
  let argc = Array.length(args);

  if (argc != 2) {
    print_endline("Usage: ./main <file_path>");
    exit(0);
  };

  let file_path = args[1];
  let is_file = Sys.file_exists(file_path);

  if (!is_file) {
    print_endline("File does not exist");
    exit(1);
  };

  let read_file = (path: string): string => {
    print_endline("=== OPEN_FILE ===");
    print_endline(path);

    let ch = open_in(path);
    let content =
      String.trim(really_input_string(ch, in_channel_length(ch)));
    close_in(ch);
    print_endline("=== FILE_READ ===");
    print_endline(content);
    content;
  };

  let parsed = parseContent(read_file(file_path));
  print_endline("=== PARSED ===");
  print_endline("[");
  List.iter(
    line => print_endline(" [ " ++ String.concat(", ", line) ++ " ]"),
    parsed,
  );
  print_endline("]");
};

let () = cli(Sys.argv);
