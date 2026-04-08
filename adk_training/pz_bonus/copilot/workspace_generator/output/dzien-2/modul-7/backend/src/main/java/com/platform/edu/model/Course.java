package com.platform.edu.model;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

/**
 * Represents a Course in the Online Learning Platform.
 * This model is used across various services including migration.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Course {
    private Long id;
    private String title;
    private String description;
    private int durationMinutes;
    private String category;
    private String legacyId; // Used for tracking during migrations

    // TODO: Using Copilot Chat, add constructors for common use cases (e.g., without ID, with essential fields).
    // Example: public Course(String title, int durationMinutes) { ... }

    // TODO: Using Copilot Chat, generate equals() and hashCode() methods based on 'id' and 'legacyId'.
    // Ensure proper object equality for comparisons during migration and data management.
}
