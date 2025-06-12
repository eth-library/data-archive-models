{
  description = "Development environment for the data archive models project";

  # Define inputs with pinned versions for reproducibility
  inputs = {
    # Use the NixOS 25.05 "stable" branch
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    # flake-utils provides helper functions for working with flakes
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    let
      javaVersion = 21; # Change this value to update the whole stack

      # Define overlay for all systems
      overlay = final: prev: let
        jdk = prev."jdk${toString javaVersion}";
      in {
        maven = prev.maven.override { jdk_headless = jdk; };
      };
    in
    # First define non-system-specific outputs (overlays)
    {
      # Make the overlay available to dependent flakes
      overlays.default = overlay;
    } 
    // (flake-utils.lib.eachDefaultSystem (system:
      let
        # Import nixpkgs with our custom overlay
        pkgs = import nixpkgs { 
          inherit system; 
          overlays = [ overlay ];
        };
        
        # Define the path to the Python virtual environment
        venvDir = "./.venv";
        
        # Define functions for structured logging without color codes
        log = {
          info = message: "echo \"[INFO] ${message}\"";
          success = message: "echo \"[SUCCESS] ${message}\"";
          warning = message: "echo \"[WARNING] ${message}\"";
          error = message: "echo \"[ERROR] ${message}\"";
        };
      in
      {
        devShells.default = pkgs.mkShell {
          # Packages to include in the environment
          packages = with pkgs; [
            jdk
            maven
            python312
            python312Packages.datamodel-code-generator
            python312Packages.hatchling
            uv
          ];

          # Shell hook runs when the environment is entered
          shellHook = ''
            echo ""
            ${log.info "Initializing Python environment..."}

            # Create virtual environment if it doesn't exist
            if [ ! -d ${venvDir} ]; then
              ${log.info "Creating virtual environment in .venv..."}
              ${pkgs.python312}/bin/python -m venv ${venvDir}
            fi

            # Activate virtual environment
            ${log.info "Activating virtual environment..."}
            source ${venvDir}/bin/activate

            if [ ! -f uv.lock ]; then
              ${log.info "Generating lock file..."}
              uv lock
            fi

            ${log.info "Installing Python dependencies with uv..."}
            uv sync --index-strategy unsafe-best-match

            # Print helpful information
            ${log.success "Development environment activated!"}
            echo "Java version: $(java --version | head -n 1)"
            echo "Java home path: $(java -XshowSettings:properties -version 2>&1 > /dev/null | grep java.home | awk '{print $3}')"
            echo "Maven version: $(mvn --version | head -n 1)"
            echo "Python version: $(python --version)"
            echo "Python interpreter path: $(python -c 'import sys; print(sys.executable)')"
            echo "uv version: $(uv --version)"
            echo ""
          '';
        };
      }
    ));
}