package com.platform.edu.migration;

import com.platform.edu.model.Course;
import com.platform.edu.repository.CourseRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

/**
 * Unit tests for {@link CourseMigrationService}.
 * Focuses on testing migration logic, AI integration, and error handling.
 */
@ExtendWith(MockitoExtension.class)
class CourseMigrationServiceTest {

    @Mock
    private CourseRepository courseRepository;

    @Mock
    private AISuggestionAgent aiSuggestionAgent;

    @InjectMocks
    private CourseMigrationService courseMigrationService;

    @BeforeEach
    void setUp() {
        // Common setup for tests
        // TODO: Use Copilot to refine common mocking behavior.
        when(courseRepository.save(any(Course.class))).thenAnswer(invocation -> {
            Course course = invocation.getArgument(0);
            if (course.getId() == null) {
                course.setId(1L); // Simulate ID generation for new courses
            }
            return course;
        });

        when(aiSuggestionAgent.enrichCourse(any(Course.class))).thenAnswer(invocation -> {
            Course course = invocation.getArgument(0);
            if (course.getCategory() == null || course.getCategory().isEmpty()) {
                course.setCategory("AI-Suggested Category");
            }
            course.setDescription(course.getDescription() + " (AI enriched)");
            return course;
        });
    }

    @Test
    void testMigrateCourses_success() {
        // TODO: Use Copilot to write a comprehensive test for successful migration.
        // Verify that courses are parsed, enriched by AI, and saved to the repository.
        List<String> rawData = Arrays.asList("Intro to Java;90;Programming", "Advanced Python;120;Data Science");

        List<Course> migratedCourses = courseMigrationService.migrateCourses(rawData);

        assertNotNull(migratedCourses);
        assertEquals(2, migratedCourses.size());
        verify(courseRepository, times(2)).save(any(Course.class));
        verify(aiSuggestionAgent, times(2)).enrichCourse(any(Course.class));

        Course firstCourse = migratedCourses.get(0);
        assertTrue(firstCourse.getTitle().contains("Intro to Java"));
        assertTrue(firstCourse.getDescription().contains("AI enriched"));
        assertNotNull(firstCourse.getCategory());
    }

    @Test
    void testMigrateCourses_emptyInput() {
        // TODO: Use Copilot to ensure the service handles empty input gracefully.
        List<String> rawData = List.of();
        List<Course> migratedCourses = courseMigrationService.migrateCourses(rawData);
        assertTrue(migratedCourses.isEmpty());
        verify(courseRepository, never()).save(any(Course.class));
    }

    @Test
    void testMigrateCourses_aiRateLimitExceeded() {
        // TODO: Use Copilot to simulate and test behavior when AI rate limit is hit.
        // Ensure the service throws an appropriate exception or handles it as designed.
        when(aiSuggestionAgent.enrichCourse(any(Course.class)))
                .thenThrow(new RuntimeException("AI API call limit exceeded"));

        List<String> rawData = Arrays.asList("Course 1", "Course 2");

        Exception exception = assertThrows(RuntimeException.class, () -> {
            courseMigrationService.migrateCourses(rawData);
        });

        assertTrue(exception.getMessage().contains("AI API call limit exceeded"));
        // Depending on error handling strategy, verify if any courses were saved before the error.
        // For now, assume no courses are saved if the first AI call fails.
        verify(courseRepository, never()).save(any(Course.class));
    }

    // TODO: Add more tests for data parsing edge cases, validation failures, etc.
    // Use @workspace context to get suggestions for comprehensive test coverage.
}

// Dummy classes for compilation purposes.
// TODO: Use Copilot Agent Mode to refactor these into their proper locations.
class Course {
    private Long id;
    private String title;
    private String description;
    private int durationMinutes;
    private String category;

    public Course() {}

    public Course(String title, int durationMinutes, String category) {
        this.title = title;
        this.durationMinutes = durationMinutes;
        this.category = category;
    }

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

interface CourseRepository {
    Course save(Course course);
    List<Course> findAll();
    void delete(Course course);
}
