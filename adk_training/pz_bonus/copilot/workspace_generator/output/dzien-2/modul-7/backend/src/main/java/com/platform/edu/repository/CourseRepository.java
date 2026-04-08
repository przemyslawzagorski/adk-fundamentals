package com.platform.edu.repository;

import com.platform.edu.model.Course;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * Repository interface for Course entities.
 * Leverages Spring Data JPA for data access operations.
 */
@Repository
public interface CourseRepository extends JpaRepository<Course, Long> {

    // TODO: Using Copilot Chat, add a custom query method to find a Course by its legacyId.
    // Example: Optional<Course> findByLegacyId(String legacyId);

    // TODO: Using Copilot Chat, add a method to find all courses belonging to a specific category.
    // Example: List<Course> findByCategory(String category);
}
