# CSV Parser

A CSV parser implementation in ReasonML.

## Setup

```bash
# Create an opam switch for the project
make create_switch

# Install dependencies
make deps
```

## Development

The project is configured with various Make targets to help with development:

| Command         | Description                                        |
| --------------- | -------------------------------------------------- |
| `make all`      | Build the project                                  |
| `make build`    | Build the project, including non-installable parts |
| `make test`     | Run the unit tests                                 |
| `make fmt`      | Format the codebase with ocamlformat               |
| `make lint`     | Run linters (equivalent to `dune build @check`)    |
| `make deps`     | Install development dependencies                   |
| `make clean`    | Clean build artifacts                              |
| `make doc`      | Generate documentation                             |
| `make servedoc` | Open documentation in web browser                  |
| `make watch`    | Watch filesystem and rebuild on changes            |
| `make utop`     | Run a REPL with project libraries                  |
| `make release`  | Run the release script                             |
| `make start`    | Run the produced executable                        |

## Contributing

Take a look at our [Contributing Guide](CONTRIBUTING.md).