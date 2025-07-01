"""
Script to generate a Mermaid class diagram from Pydantic models in the data_archive package.

This script:
1. Identifies all Pydantic model files in the data_archive package
2. Parses the files to extract class and field information
3. Generates a Mermaid class diagram
4. Outputs the diagram to a .mmd file
"""

import ast
from pathlib import Path
from typing import Dict, List


class PydanticModelVisitor(ast.NodeVisitor):
    """AST visitor to extract Pydantic model information from Python files."""
    
    def __init__(self):
        self.models = {}
        self.current_class = None
        self.imports = {}
        self.from_imports = {}
        
    def visit_ImportFrom(self, node):
        """Process from-import statements."""
        module = node.module
        for name in node.names:
            if module:
                self.from_imports[name.name] = f"{module}.{name.name}"
            else:
                self.from_imports[name.name] = name.name
        self.generic_visit(node)
        
    def visit_Import(self, node):
        """Process import statements."""
        for name in node.names:
            self.imports[name.name] = name.name
        self.generic_visit(node)
        
    def visit_ClassDef(self, node):
        """Process class definitions."""
        # Check if this is a Pydantic model (inherits from BaseModel)
        is_pydantic_model = False
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "BaseModel":
                is_pydantic_model = True
                break
            elif isinstance(base, ast.Attribute) and base.attr == "BaseModel":
                is_pydantic_model = True
                break
                
        if is_pydantic_model:
            self.current_class = node.name
            self.models[node.name] = {"fields": {}, "docstring": self.get_docstring(node)}
            self.generic_visit(node)
            self.current_class = None
        else:
            self.generic_visit(node)
            
    def visit_AnnAssign(self, node):
        """Process annotated assignments (fields in Pydantic models)."""
        if self.current_class and isinstance(node.target, ast.Name):
            field_name = node.target.id
            field_type = self.get_type_annotation(node.annotation)
            
            # Check for Field with description
            description = None
            if node.value and isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Name) and node.value.func.id == "Field":
                    for keyword in node.value.keywords:
                        if keyword.arg == "description" and isinstance(keyword.value, ast.Constant):
                            description = keyword.value.value
            
            self.models[self.current_class]["fields"][field_name] = {
                "type": field_type,
                "description": description
            }
            
    def get_docstring(self, node):
        """Extract docstring from a class or function."""
        if (node.body and isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Constant) and 
                isinstance(node.body[0].value.value, str)):
            return node.body[0].value.value.strip()
        return None
        
    def get_type_annotation(self, node):
        """Convert AST type annotation to string representation."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self.get_type_annotation(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            value = self.get_type_annotation(node.value)
            if isinstance(node.slice, ast.Index):  # Python 3.8 and below
                slice_value = self.get_type_annotation(node.slice.value)
            else:  # Python 3.9+
                slice_value = self.get_type_annotation(node.slice)
            return f"{value}[{slice_value}]"
        elif isinstance(node, ast.Tuple):
            return ", ".join(self.get_type_annotation(elt) for elt in node.elts)
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.List):
            return "[" + ", ".join(self.get_type_annotation(elt) for elt in node.elts) + "]"
        else:
            return "Any"


def find_pydantic_model_files(directory: Path) -> List[Path]:
    """Find all Python files that might contain Pydantic models."""
    return list(directory.glob("**/*.py"))


def parse_pydantic_models(file_path: Path) -> Dict:
    """Parse a Python file and extract Pydantic model information."""
    try:
        with open(file_path, "r") as f:
            content = f.read()
        
        tree = ast.parse(content)
        visitor = PydanticModelVisitor()
        visitor.visit(tree)
        
        return visitor.models
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return {}


def generate_mermaid_diagram(all_models: Dict[str, Dict]) -> str:
    """Generate a Mermaid class diagram from parsed model information."""
    # Start the Mermaid class diagram
    mermaid_text = "classDiagram\n"
    
    # Track relationships between models
    relationships = []
    
    # Process each model
    for model_name, model_info in all_models.items():
        # Add the class definition
        mermaid_text += f"    class {model_name} {{\n"
        
        # Add docstring as a comment if available
        if model_info.get("docstring"):
            docstring = model_info["docstring"].replace("\n", "\\n")
            mermaid_text += f"        %% {docstring}\n"
        
        # Add fields to the class definition
        for field_name, field_info in model_info.get("fields", {}).items():
            field_type = field_info.get("type", "Any")
            
            # Add field to class definition
            mermaid_text += f"        +{field_type} {field_name}\n"
            
            # Check for relationships with other models
            for other_model_name in all_models.keys():
                if other_model_name in field_type:
                    # Add relationship
                    if "List" in field_type or "list" in field_type:
                        relationships.append(f"    {model_name} *-- {other_model_name} : contains many")
                    else:
                        relationships.append(f"    {model_name} *-- {other_model_name} : contains")
        
        # Close the class definition
        mermaid_text += "    }\n"
    
    # Add relationships to the diagram
    for relationship in set(relationships):  # Use set to remove duplicates
        mermaid_text += relationship + "\n"
    
    return mermaid_text


def main():
    """Main function to generate the Mermaid diagram."""
    # Find the src directory - adjusted for scripts subdirectory
    src_dir = Path(__file__).parent.parent / "src"
    data_archive_dir = src_dir / "data_archive"
    
    if not data_archive_dir.exists():
        print(f"Error: Directory {data_archive_dir} does not exist.")
        return
    
    # Find all Python files that might contain Pydantic models
    model_files = find_pydantic_model_files(data_archive_dir)
    print(f"Found {len(model_files)} Python files in the data_archive package.")
    
    # Parse all model files
    all_models = {}
    for file_path in model_files:
        models = parse_pydantic_models(file_path)
        all_models.update(models)
    
    print(f"Found {len(all_models)} Pydantic models in the data_archive package.")
    
    # Generate the Mermaid diagram
    mermaid_text = generate_mermaid_diagram(all_models)
    
    # Write the diagram to a file - adjusted for scripts subdirectory
    output_file = Path(__file__).parent.parent / "data_archive_models.mmd"
    output_file.write_text(mermaid_text)
    
    print(f"Mermaid diagram generated and saved to {output_file}")


if __name__ == "__main__":
    main()