# OCaml INI Parser

A robust and flexible INI configuration file parser implemented in OCaml.

## Overview

This project provides a library for parsing INI configuration files, a common format used for configuration in many applications. The implementation is designed to be efficient, correct, and easy to use within OCaml projects.

## Features

- Parsing of standard INI file format
- Support for sections and key-value pairs
- Handling of comments
- Error reporting with line and column information
- Type-safe access to configuration values

## Getting Started

### Prerequisites

- OCaml (recommended version 4.13.0+)
- Dune build system
- opam (OCaml package manager)

### Installation

From the opam repository:

```shell
opam install ini
```

Or build from source:

```shell
git clone <repository-url>
cd ini
make
```

### Usage

```ocaml
open Ini

(* Parse an INI file *)
let config = Ini.parse_file "config.ini"

(* Get a value *)
let server_host = Ini.get_string config "server" "host"
let server_port = Ini.get_int config "server" "port"

(* Check if a key exists *)
let has_debug = Ini.has_key config "settings" "debug"
```

## Project Structure

- `lib/`: Library implementation
- `bin/`: Command-line tools
- `test/`: Test suite
- `_build/`: Build artifacts (generated)

## Development

### Building

```shell
dune build
```

### Running Tests

```shell
dune runtest
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Learning OCaml

This project is also intended as a learning resource for OCaml programming. Some notable aspects demonstrated:

- Lexing and parsing
- Error handling
- Functional data structures
- Testing strategies
- Using the Dune build system

## Resources

- [Real World OCaml](https://dev.realworldocaml.org/)
- [OCaml Manual](https://ocaml.org/docs/)
- [Dune Documentation](https://dune.readthedocs.io/)