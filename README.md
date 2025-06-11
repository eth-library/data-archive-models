# Data Archive Models

A collection of JSON schemas defining data models for digital archiving systems based on the OAIS (Open Archival Information System) reference model. These schemas provide standardized definitions for various components of a data archive.

## Core Functionality

The project defines JSON schemas for key entities in a digital archiving workflow:

- **Producer**: Entity that provides data to be archived
- **Deposit**: Information about a submission to the archive
- **SIP (Submission Information Package)**: Package of information submitted to the archive
- **IntellectualEntity**: Conceptual object being preserved
- **Representation**: Digital manifestation of an intellectual entity
- **File**: Individual digital file within a representation
- **Fixity**: Integrity information for digital files

All schemas are currently at version 0.1.0, indicating this is an early-stage project.

## Setup/Installation

### Prerequisites

- Java 21
- Maven
- Python 3.12

### Quick Start

The project uses Nix for reproducible development environments:

```bash
# Clone the repository
git clone <repository-url>
cd data-archive-models

# If you have Nix with flakes enabled
nix develop

# Alternatively, set up manually
python -m venv .venv
source .venv/bin/activate
```

### Build Options

The project provides several Maven build commands:

1. **Validate JSON schemas only**:
   ```bash
   mvn -Dtest=JsonSchemaValidationTest test
   ```

2. **Build without validation** (skip tests):
   ```bash
   mvn package -DskipTests
   ```

3. **Standard build** (validate schemas then generate classes):
   ```bash
   mvn package
   ```

## Continuous Integration

The project uses GitHub Actions for CI. The workflow automatically:
- Sets up the Nix environment shell
- Runs schema validation tests
- Generates Java models from JSON schemas
- Makes generated code available as artifacts

## Future Goals

- Publishing packages from JSON schemas to Maven (GitHub Package Registry)
- Publishing packages from JSON schemas to PyPI
