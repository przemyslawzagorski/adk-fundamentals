package com.platform.edu.migration;

import com.platform.edu.model.Course;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST Controller for managing course migration operations.
 */
@RestController
@RequestMapping("/api/v1/migrations/courses")
public class CourseMigrationController {

    private final CourseMigrationService courseMigrationService;

    public CourseMigrationController(CourseMigrationService courseMigrationService) {
        this.courseMigrationService = courseMigrationService;
    }

    /**
     * Endpoint to initiate a course migration from a list of raw data strings.
     * Example raw data: ["Course A;60;Java", "Course B;90;Python"]
     *
     * @param rawCourseData List of raw course data strings.
     * @return A list of successfully migrated Course objects.
     */
    @PostMapping
    public ResponseEntity<List<Course>> startMigration(@RequestBody List<String> rawCourseData) {
        // TODO: Use Copilot to add input validation and error handling.
        // Ensure the raw data format is as expected before passing to the service.
        if (rawCourseData == null || rawCourseData.isEmpty()) {
            return ResponseEntity.badRequest().build();
        }

        try {
            List<Course> migratedCourses = courseMigrationService.migrateCourses(rawCourseData);
            // TODO: Enhance response with migration summary or statistics.
            return ResponseEntity.ok(migratedCourses);
        } catch (RuntimeException e) {
            // TODO: Use Copilot to implement more specific error handling based on exception type (e.g., AI rate limit).
            return ResponseEntity.status(500).body(null); // Generic error for now
        }
    }

    // TODO: Implement an endpoint for reverting migrations.
    // @DeleteMapping("/{migrationId}")
    // public ResponseEntity<Void> revertMigration(@PathVariable String migrationId) {
    //     // Use Copilot to complete this endpoint.
    //     return ResponseEntity.ok().build();
    // }

    // TODO: Implement an endpoint to check migration status.
    // @GetMapping("/status/{migrationId}")
    // public ResponseEntity<MigrationStatus> getMigrationStatus(@PathVariable String migrationId) {
    //     // Use Copilot to complete this endpoint.
    //     return ResponseEntity.ok(new MigrationStatus());
    // }
}

// Dummy class for compilation purposes. In a real scenario, this would be a separate file.
// TODO: Use Copilot Agent Mode to extract this into a proper file.
class Course {
    private Long id;
    private String title;
    private String description;
    private int durationMinutes;
    private String category;
    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public int getDurationMinutes() { return durationMinutes; }
    public void setDurationMinutes(int durationMinutes) { this.durationMinutes = durationMinutes; }
    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
}
