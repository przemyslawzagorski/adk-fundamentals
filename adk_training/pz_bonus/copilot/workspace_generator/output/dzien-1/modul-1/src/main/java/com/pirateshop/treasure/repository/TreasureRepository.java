package com.pirateshop.treasure.repository;

import com.pirateshop.treasure.model.Treasure;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Repository interface for managing Treasure entities.
 * Demonstrates Spring Data JPA capabilities.
 */
@Repository
public interface TreasureRepository extends JpaRepository<Treasure, Long> {

    // TODO: Use Copilot Agent Mode to generate custom query methods (e.g., findByNameContaining, findByTypeAndValueGreaterThan)
    // TODO: Refactor existing repository to use QueryDslPredicateExecutor for dynamic queries
    List<Treasure> findByType(String type);

    // TODO: Use Copilot to suggest a method for finding treasures within a certain value range
    List<Treasure> findByValueBetween(double minValue, double maxValue);

    // TODO: Apply @workspace context to suggest adding a method that uses @Query annotation for a complex SQL join
}
