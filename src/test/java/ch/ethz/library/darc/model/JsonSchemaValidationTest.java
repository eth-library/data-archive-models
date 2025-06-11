package ch.ethz.library.darc.model;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.networknt.schema.JsonSchema;
import com.networknt.schema.JsonSchemaFactory;
import com.networknt.schema.SpecVersion;
import com.networknt.schema.ValidationMessage;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Test class to validate JSON schema files against the official JSON Schema draft specification.
 */
public class JsonSchemaValidationTest {

    private static final String SCHEMAS_DIR = "schemas/data-archive";
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
    
    /**
     * Validates all JSON schema files in the schemas/data-archive directory against
     * the official JSON Schema draft specification.
     */
    @Test
    @DisplayName("Validate all JSON schemas against the official draft schema")
    public void validateAllJsonSchemas() throws IOException {
        // Get all JSON files in the schemas directory (excluding _shared directory)
        Set<Path> schemaFiles = findJsonFiles(SCHEMAS_DIR);
        
        // Create a JSON Schema validator for Draft 2020-12
        JsonSchemaFactory factory = JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V202012);
        
        // Load the official meta-schema using URL instead of string
        URL metaSchemaUrl = new URL("https://json-schema.org/draft/2020-12/schema");
        InputStream metaSchemaStream = metaSchemaUrl.openStream();
        JsonSchema metaSchema = factory.getSchema(metaSchemaStream);
        
        // Track if any validation errors occurred
        boolean allSchemasValid = true;
        StringBuilder errorMessages = new StringBuilder();
        
        // Validate each schema file
        for (Path schemaPath : schemaFiles) {
            JsonNode schemaNode = OBJECT_MAPPER.readTree(schemaPath.toFile());
            Set<ValidationMessage> validationMessages = metaSchema.validate(schemaNode);
            
            if (!validationMessages.isEmpty()) {
                allSchemasValid = false;
                errorMessages.append("Validation errors in ").append(schemaPath).append(":\n");
                for (ValidationMessage message : validationMessages) {
                    errorMessages.append("  - ").append(message).append("\n");
                }
            }
        }
        
        // Assert that all schemas are valid
        assertTrue(allSchemasValid, 
                "Some JSON schemas are not valid against the official draft schema:\n" + 
                errorMessages);
    }
    
    /**
     * Finds all JSON files in the specified directory and its subdirectories,
     * excluding files in the _shared directory.
     */
    private Set<Path> findJsonFiles(String directory) throws IOException {
        try (Stream<Path> paths = Files.walk(Paths.get(directory))) {
            return paths
                    .filter(Files::isRegularFile)
                    .filter(path -> path.toString().endsWith(".json"))
                    .filter(path -> !path.toString().contains("_shared"))
                    .collect(Collectors.toSet());
        }
    }
}