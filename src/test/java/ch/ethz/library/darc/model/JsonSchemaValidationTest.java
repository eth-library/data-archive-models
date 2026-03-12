package ch.ethz.library.darc.model;

import com.networknt.schema.Error;
import com.networknt.schema.InputFormat;
import com.networknt.schema.Schema;
import com.networknt.schema.SchemaLocation;
import com.networknt.schema.SchemaRegistry;
import com.networknt.schema.SpecificationVersion;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Test class to validate JSON schema files against the official JSON Schema draft specification.
 */
public class JsonSchemaValidationTest {

    private static final String SCHEMAS_DIR = "schemas/data-archive";

    /**
     * Validates all JSON schema files in the schemas/data-archive directory against
     * the official JSON Schema draft specification.
     */
    @Test
    @DisplayName("Validate all JSON schemas against the official draft schema")
    public void validateAllJsonSchemas() throws IOException {
        // Get all JSON files in the schemas directory (excluding _shared directory)
        Set<Path> schemaFiles = findJsonFiles(SCHEMAS_DIR);

        // Create a schema registry for Draft 2020-12
        SchemaRegistry registry = SchemaRegistry.withDefaultDialect(SpecificationVersion.DRAFT_2020_12);

        // Load the bundled meta-schema (no network fetch needed)
        Schema metaSchema = registry.getSchema(
                SchemaLocation.of("https://json-schema.org/draft/2020-12/schema"));

        // Track if any validation errors occurred
        boolean allSchemasValid = true;
        StringBuilder errorMessages = new StringBuilder();

        // Validate each schema file using string-based validation
        for (Path schemaPath : schemaFiles) {
            String schemaContent = Files.readString(schemaPath);
            List<Error> errors = metaSchema.validate(schemaContent, InputFormat.JSON);

            if (!errors.isEmpty()) {
                allSchemasValid = false;
                errorMessages.append("Validation errors in ").append(schemaPath).append(":\n");
                for (Error error : errors) {
                    errorMessages.append("  - ").append(error).append("\n");
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
