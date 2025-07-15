let parse_line = (line: string) => String.split_on_char(',', line);

let parse_content = (content: string): list(list(string)) => {
  print_endline("=== IN ===");
  print_endline(content);
  let lines = String.split_on_char('\n', content);
  let parsed = List.map(line => parse_line(line), lines);
  parsed;
};
