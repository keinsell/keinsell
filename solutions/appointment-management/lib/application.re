module Configuration = {
  let configure_application = () => {
  print_endline("Configuring application...");
}
};

module Logger = {
  let log = (message: string) => {
    print_endline("LOG: " ++ message);
  };
};

// TODO: Telemetry, logging, http, documentation, client?, database?, cli?, etc.
