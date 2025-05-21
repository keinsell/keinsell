/* ANSI Colors for terminal output */
let reset = "\027[0m";
let bold = "\027[1m";
let bright_green = "\027[92m";
let bright_cyan = "\027[96m";

/* Print a colorful welcome message */
let print_welcome = () => {
  print_endline(bold ++ bright_green ++ "🐫 Kamel API Server" ++ reset);
  print_endline(bright_cyan ++ "Running at http://localhost:8080/api/todos" ++ reset);
  print_endline("Press Ctrl+C to stop the server");
  print_endline("");
};

/* Main entry point */
let () = {
  print_welcome();

  let register_identity: Kamel.Identity.Command.register_identity = {
    username: "test-user",
    password: Kamel.Identity.Password.create("test-pass")
  };

  let in_memory_identity_repository: Kamel.Identity.identity_repository = {
    insert: (identity) => {
      print_endline("Identity inserted: " ++ identity.username);
      Ok(identity);
    },
  };

  let identity = Kamel.Identity.register_identity(register_identity, in_memory_identity_repository) |> fun(result) => switch(result) {
    | Ok(identity_created) => {
        print_endline("Identity created: " ++ identity_created.username);
        identity_created
      }
    | Error(error_during_identity_creation) => {
        print_endline("Error creating identity: " ++ error_during_identity_creation);
        exit(1);
      }
  };

  print_newline();
  print_endline("Identity created.");
  print_endline("Username: " ++ identity.username);
  print_endline("Password: " ++ identity.password);
  print_newline();

  Kamel.Application.Configuration.configure_application();
};
