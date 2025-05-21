{
  inputs = {
    opam-repository.url = "github:ocaml/opam-repository";
        opam-repository.flake = false;

    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flakelight.url = "github:nix-community/flakelight";
    opam-nix.url = "github:tweag/opam-nix";
        opam-nix.inputs.nixpkgs.follows = "nixpkgs";
    opam-nix.inputs.opam-repository.follows = "opam-repository";

  };

  outputs = {
    flakelight,
    nixpkgs,
    ...
  }: let
    # Function to extract dependencies from kamel.opam file (generated from dune-project)
    extractDepsFromOpam = lib: path: let
      content = builtins.readFile path;
      # Simple list of OCaml dependencies we want to extract from the opam file
      # This is a more reliable approach than regex parsing the dune-project file
      knownDeps = [
        "cohttp"
        "cohttp-lwt-unix"
        "lwt"
        "lwt_ppx"
        "yojson"
        "melange"
        "reason"
        "ocaml-lsp-server"
        "ocamlformat"
        "ppx_deriving"
        "rtop"
        "melange-atdgen-codec-runtime"
        "dream"
        "alcotest"
        "logs"
        "fmt"
        "cmdliner"
      ];

      # Check if each dependency is in the opam file
      isDependencyPresent = dep: builtins.match ".*\"${dep}\".*" content != null;

      # Filter the known dependencies by presence in the opam file
      presentDeps = lib.lists.filter isDependencyPresent knownDeps;
    in
      presentDeps;
  in
    flakelight ./. {
      description = "Kamel OCaml project";

      # Package definition
      package = {
        ocamlPackages,
        pkgs,
        lib,
        stdenv,
        fetchFromGitHub,
        defaultMeta,
      }: let
        opamDeps = extractDepsFromOpam lib ./kamel.opam;

        # Convert opam dependencies to OCaml packages
        opamDepPkgs =
          builtins.map
          (dep:
            if builtins.hasAttr dep ocamlPackages
            then ocamlPackages.${dep}
            else null)
          opamDeps;

        # Filter out null packages (dependencies that don't exist in nixpkgs)
        validOpamDepPkgs = builtins.filter (x: x != null) opamDepPkgs;
      in
        ocamlPackages.buildDunePackage {
          pname = "kamel";
          version = "0.1.0";
          src = ./.;

          # Use the dependencies from kamel.opam
          buildInputs = validOpamDepPkgs ++ [
            ocamlPackages.dream
            ocamlPackages.lwt
            ocamlPackages.yojson
            ocamlPackages.cohttp
            ocamlPackages.cohttp-lwt-unix
          ];

          nativeBuildInputs = [
            ocamlPackages.reason
            ocamlPackages.lwt_ppx
            ocamlPackages.ppx_deriving
          ];

          # Enable tests during build
          doCheck = true;

          # The dune build system will automatically run tests with @runtest target
          # when doCheck is true, so we don't need to override checkPhase

          meta =
            defaultMeta
            // {
              description = "🐫 Kamel";
              homepage = "https://github.com/keinsell/kamel";
              license = lib.licenses.mit;
            };
        };

      # Development shell
      devShell = {
        pkgs,
        lib,
        ...
      }: let
        # Reuse the dependency extraction function
        opamDeps = extractDepsFromOpam lib ./kamel.opam;

        # Basic development tools that should always be included
        basePkgs = with pkgs; [
          ocaml
          opam
          dune_3
          ocaml_make
          ocamlformat
          ocamlPackages.reason
          ocamlPackages.menhir
          ocamlPackages.dream
          nil
          nixd
          statix
          onefetch
        ];

        # Convert opam dependencies to OCaml packages for development
        opamDevDepPkgs =
          builtins.map
          (dep:
            if builtins.hasAttr dep pkgs.ocamlPackages
            then pkgs.ocamlPackages.${dep}
            else null)
          opamDeps;

        # Filter out null packages
        validOpamDevDepPkgs = builtins.filter (x: x != null) opamDevDepPkgs;

        # Additional development packages not in dune-project
        additionalDevPkgs = with pkgs.ocamlPackages; [
          reason-react
          reason-react-ppx
          dune-release
          merlin
          utop
          alcotest
          junit_alcotest
          opam-state
          opam-format
          opam-repository
          opam-file-format
        ];
      in {
        packages = _: basePkgs ++ validOpamDevDepPkgs ++ additionalDevPkgs;
        shellHook = ''
          onefetch
        '';
      };
    };
}
