"""
Script to update the README.md file with a Mermaid class diagram.

This script:
1. Uses the generate_mermaid_diagram.py script to generate a Mermaid diagram
2. Reads the README.md file
3. Adds markers if they don't exist
4. Replaces the content between the markers with the generated diagram
5. Ensures the diagram is wrapped in a mermaid fenced code block
6. Writes the updated content back to README.md
"""

import re
from pathlib import Path
import importlib.util
import sys

# Add the scripts directory to the Python path
scripts_dir = Path(__file__).parent
sys.path.append(str(scripts_dir))

# Import the generate_mermaid_diagram module from the scripts directory
spec = importlib.util.spec_from_file_location("generate_mermaid_diagram", scripts_dir / "generate_mermaid_diagram.py")
generate_mermaid_diagram = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_mermaid_diagram)

def main():
    """Main function to update the README.md file with a Mermaid class diagram."""
    # Find the src directory - adjusted for scripts subdirectory
    src_dir = Path(__file__).parent.parent / "src"
    data_archive_dir = src_dir / "data_archive"
    
    if not data_archive_dir.exists():
        print(f"Error: Directory {data_archive_dir} does not exist.")
        return
    
    # Find all Python files that might contain Pydantic models
    model_files = generate_mermaid_diagram.find_pydantic_model_files(data_archive_dir)
    print(f"Found {len(model_files)} Python files in the data_archive package.")
    
    # Parse all model files
    all_models = {}
    for file_path in model_files:
        models = generate_mermaid_diagram.parse_pydantic_models(file_path)
        all_models.update(models)
    
    print(f"Found {len(all_models)} Pydantic models in the data_archive package.")
    
    # Generate the Mermaid diagram
    mermaid_text = generate_mermaid_diagram.generate_mermaid_diagram(all_models)
    
    # Read the README.md file - adjusted for scripts subdirectory
    readme_path = Path(__file__).parent.parent / "README.md"
    if not readme_path.exists():
        print(f"Error: README.md file not found at {readme_path}")
        return
    
    readme_content = readme_path.read_text()
    
    # Define the markers
    start_marker = "<!-- BEGIN_MERMAID_DIAGRAM -->"
    end_marker = "<!-- END_MERMAID_DIAGRAM -->"
    
    # Check if the markers exist
    if start_marker not in readme_content or end_marker not in readme_content:
        # Add the markers and the diagram section
        print("Markers not found in README.md. Adding them...")
        
        # Add the diagram section after the Core Functionality section
        core_functionality_section = "## Core Functionality"
        if core_functionality_section in readme_content:
            # Find the end of the Core Functionality section
            core_functionality_end = readme_content.find("##", readme_content.find(core_functionality_section) + len(core_functionality_section))
            if core_functionality_end == -1:
                # If there's no next section, add it at the end
                core_functionality_end = len(readme_content)
            
            # Insert the diagram section
            diagram_section = f"\n\n## Data Model Diagram\n\n{start_marker}\n```mermaid\n{mermaid_text}```\n{end_marker}\n"
            readme_content = readme_content[:core_functionality_end] + diagram_section + readme_content[core_functionality_end:]
        else:
            # If Core Functionality section doesn't exist, add it at the end
            diagram_section = f"\n\n## Data Model Diagram\n\n{start_marker}\n```mermaid\n{mermaid_text}```\n{end_marker}\n"
            readme_content += diagram_section
    else:
        # Replace the content between the markers
        print("Updating the Mermaid diagram in README.md...")
        pattern = f"{re.escape(start_marker)}.*?{re.escape(end_marker)}"
        replacement = f"{start_marker}\n```mermaid\n{mermaid_text}```\n{end_marker}"
        readme_content = re.sub(pattern, replacement, readme_content, flags=re.DOTALL)
    
    # Write the updated content back to README.md
    readme_path.write_text(readme_content)
    
    print(f"README.md updated with the Mermaid diagram.")

if __name__ == "__main__":
    main()