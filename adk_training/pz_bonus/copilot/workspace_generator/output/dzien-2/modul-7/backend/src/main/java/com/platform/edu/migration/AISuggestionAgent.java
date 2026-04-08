package com.platform.edu.migration;

import com.platform.edu.model.Course;
import org.springframework.stereotype.Component;

/**
 * Simulates an AI Agent responsible for enriching course data.
 * This agent demonstrates potential challenges with "Limity AI" (AI Limits) and custom agent design.
 */
@Component
public class AISuggestionAgent {

    private static final int API_CALL_LIMIT = 5; // Example limit per minute
    private int currentApiCallCount = 0;
    private long lastResetTime = System.currentTimeMillis();

    /**
     * Enriches a Course object with AI-driven suggestions.
     * This could involve categorizing, suggesting keywords, or improving descriptions.
     *
     * @param course The course to enrich.
     * @return The enriched course.
     */
    public Course enrichCourse(Course course) {
        // TODO: Use Copilot Agent Mode to implement a robust rate limiting mechanism.
        // If API_CALL_LIMIT is reached within a minute, throw an exception or queue the request.
        // Consider using a more sophisticated token bucket or leaky bucket algorithm.
        checkApiLimits();

        // Simulate AI processing
        String suggestedCategory = generateCategorySuggestion(course.getTitle());
        course.setCategory(suggestedCategory);

        // TODO: Use Copilot to add more AI-driven enrichments (e.g., description enhancement, keyword generation).
        // These should also be subject to API limits.
        course.setDescription(course.getDescription() + " (AI-enhanced)");

        currentApiCallCount++;
        return course;
    }

    private void checkApiLimits() {
        long currentTime = System.currentTimeMillis();
        if (currentTime - lastResetTime >= 60000) { // Reset every minute
            currentApiCallCount = 0;
            lastResetTime = currentTime;
        }

        if (currentApiCallCount >= API_CALL_LIMIT) {
            // TODO: Use Copilot to implement proper exception handling or retry logic.
            // This should inform the caller about the rate limit and potentially suggest a retry after some time.
            throw new RuntimeException("AI API call limit exceeded. Please wait and retry.");
        }
    }

    private String generateCategorySuggestion(String title) {
        // TODO: Use Copilot to implement a more sophisticated category suggestion based on title/description.
        // This could use simple keyword matching or integrate with an external NLP service.
        if (title.toLowerCase().contains("java")) {
            return "Programming - Java";
        } else if (title.toLowerCase().contains("python")) {
            return "Programming - Python";
        } else if (title.toLowerCase().contains("history")) {
            return "Humanities - History";
        } else {
            return "General Education";
        }
    }
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
