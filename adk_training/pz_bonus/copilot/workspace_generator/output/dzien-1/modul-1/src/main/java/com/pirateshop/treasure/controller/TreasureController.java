package com.pirateshop.treasure.controller;

import com.pirateshop.treasure.dto.TreasureDTO;
import com.pirateshop.treasure.service.TreasureService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST controller for managing pirate treasures.
 * Demonstrates advanced Spring Boot features and integration points for GitHub Copilot.
 */
@RestController
@RequestMapping("/api/v1/treasures")
public class TreasureController {

    private final TreasureService treasureService;

    public TreasureController(TreasureService treasureService) {
        this.treasureService = treasureService;
    }

    // TODO: Use Copilot Agent Mode to implement a comprehensive search endpoint with multiple criteria (e.g., name, type, origin, value range)
    // TODO: Refactor existing methods to use Spring Data JPA specifications for complex queries
    @GetMapping
    public ResponseEntity<List<TreasureDTO>> getAllTreasures() {
        // TODO: Apply @workspace context to suggest pagination and sorting parameters for this endpoint
        List<TreasureDTO> treasures = treasureService.findAllTreasures();
        return ResponseEntity.ok(treasures);
    }

    @GetMapping("/{id}")
    public ResponseEntity<TreasureDTO> getTreasureById(@PathVariable Long id) {
        // TODO: Implement robust error handling for treasure not found using @ExceptionHandler
        // TODO: Use Copilot to suggest a caching mechanism for frequently accessed treasures
        return treasureService.findTreasureById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<TreasureDTO> createTreasure(@RequestBody TreasureDTO treasureDTO) {
        // TODO: Implement input validation for TreasureDTO using Bean Validation annotations
        // TODO: Use Copilot to suggest an asynchronous event publishing mechanism after treasure creation
        TreasureDTO createdTreasure = treasureService.saveTreasure(treasureDTO);
        return ResponseEntity.status(201).body(createdTreasure);
    }

    @PutMapping("/{id}")
    public ResponseEntity<TreasureDTO> updateTreasure(@PathVariable Long id, @RequestBody TreasureDTO treasureDTO) {
        // TODO: Use Copilot to generate a diff/patch update method for partial updates instead of full replacement
        // TODO: Ensure idempotency for this PUT request
        TreasureDTO updatedTreasure = treasureService.updateTreasure(id, treasureDTO);
        return ResponseEntity.ok(updatedTreasure);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTreasure(@PathVariable Long id) {
        // TODO: Implement soft delete functionality instead of hard delete
        // TODO: Use Copilot to suggest an audit logging mechanism for delete operations
        treasureService.deleteTreasure(id);
        return ResponseEntity.noContent().build();
    }
}
