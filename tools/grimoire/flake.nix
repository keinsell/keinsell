{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flakelight = {
      url = "github:nix-community/flakelight";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flakelight, ... }@inputs:
    flakelight ./. {
      inputs = inputs;
      
      devShell = { pkgs, ... }: {
        packages = with pkgs; [
          # Python 3.11
          python311
          
          # UV package manager
          uv
          
          # Python development tools
          ruff
          pyright
          mypy
          black
          isort
          
          # Additional useful tools
          pre-commit
          pipx
          
          # Build tools
          gcc
          gnumake
          pkg-config
          
          # System libraries that might be needed
          zlib
          openssl
          stdenv.cc.cc.lib
        ];
        
        shellHook = ''
          export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"
          echo "🧙 Grimoire development environment"
          echo "Python: $(python --version)"
          echo "UV: $(uv --version)"
          echo ""
          echo "Available commands:"
          echo "  uv sync       - Install dependencies"
          echo "  uv run        - Run commands in virtual environment"
          echo "  ruff check    - Run linter"
          echo "  pyright       - Run type checker"
          echo ""
        '';
        
        env = {
          PYTHONPATH = ".";
          UV_SYSTEM_PYTHON = "false";
          UV_PYTHON = "${pkgs.python311}/bin/python";
        };
      };
    };
}