# Contributing

## Setup your development environment

You need Opam, you can install it by following [Opam's documentation](https://opam.ocaml.org/doc/Install.html).

With Opam installed, you can install the dependencies in a new local switch with:

```bash
make switch
```

Or globally, with:

```bash
make deps
```

Then, build the project with:

```bash
make build
```

### Running Binary

After building the project, you can run the main binary that is produced.


```bash
make start
```

### Running Tests

You can run the test compiled executable:


```bash
make test
```

### Building documentation

Documentation for the libraries in the project can be generated with:


```bash
make doc
open-cli $(make doc-path)
```

This assumes you have a command like [open-cli](https://github.com/sindresorhus/open-cli) installed on your system.

> NOTE: On macOS, you can use the system command `open`, for instance `open $(make doc-path)`

### Repository Structure

The following snippet describes csv's repository structure.

```text
.
├── bin/
|   Source for csv's binary. This links to the library defined in `lib/`.
│
├── lib/
|   Source for csv's library. Contains csv's core functionnalities.
│
├── test/
|   Unit tests and integration tests for csv.
│
├── dune-project
|   Dune file used to mark the root of the project and define project-wide parameters.
|   For the documentation of the syntax, see https://dune.readthedocs.io/en/stable/dune-files.html#dune-project
│
├── LICENSE
│
├── Makefile
|   Make file containing common development command.
│
├── README.md
│
└── csv.opam
    Opam package definition.
    To know more about creating and publishing opam packages, see https://opam.ocaml.org/doc/Packaging.html.
```