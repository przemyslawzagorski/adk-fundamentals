package com.pirateshop.treasure.service;

import com.pirateshop.treasure.dto.TreasureDTO;
import com.pirateshop.treasure.model.Treasure;
import com.pirateshop.treasure.repository.TreasureRepository;
import com.pirateshop.treasure.exception.TreasureNotFoundException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Service layer for managing pirate treasures.
 * Demonstrates transactional operations and integration with AI suggestion service.
 */
@Service
public class TreasureService {

    private final TreasureRepository treasureRepository;
    private final AISuggestionService aiSuggestionService;

    public TreasureService(TreasureRepository treasureRepository, AISuggestionService aiSuggestionService) {
        this.treasureRepository = treasureRepository;
        this.aiSuggestionService = aiSuggestionService;
    }

    // TODO: Use Copilot Agent Mode to implement advanced search logic using QueryDSL or Specification API
    // TODO: Refactor to use a dedicated Mapper (e.g., MapStruct) for DTO to Entity conversion
    public List<TreasureDTO> findAllTreasures() {
        // TODO: Apply @workspace context to suggest adding caching here for frequently accessed treasure lists
        return treasureRepository.findAll().stream()
                .map(this::toDto)
                .collect(Collectors.toList());
    }

    public Optional<TreasureDTO> findTreasureById(Long id) {
        // TODO: Use Copilot to suggest implementing a circuit breaker pattern for external calls (e.g., AI service)
        return treasureRepository.findById(id).map(this::toDto);
    }

    @Transactional
    public TreasureDTO saveTreasure(TreasureDTO treasureDTO) {
        // TODO: Use Copilot Agent Mode to implement a recommendation engine call here to suggest similar treasures after creation
        Treasure treasure = toEntity(treasureDTO);
        Treasure savedTreasure = treasureRepository.save(treasure);
        // Example AI interaction: get a suggestion for the new treasure
        // TODO: Use Copilot to suggest a more sophisticated prompt engineering for AI service
        String aiComment = aiSuggestionService.getTreasureSuggestion(savedTreasure.getName());
        System.out.println("AI Comment for new treasure: " + aiComment);
        return toDto(savedTreasure);
    }

    @Transactional
    public TreasureDTO updateTreasure(Long id, TreasureDTO treasureDTO) {
        // TODO: Implement optimistic locking for concurrent updates
        // TODO: Use Copilot to suggest a domain event to be published upon treasure update
        return treasureRepository.findById(id).map(existingTreasure -> {
            existingTreasure.setName(treasureDTO.getName());
            existingTreasure.setType(treasureDTO.getType());
            existingTreasure.setValue(treasureDTO.getValue());
            existingTreasure.setOrigin(treasureDTO.getOrigin());
            return toDto(treasureRepository.save(existingTreasure));
        }).orElseThrow(() -> new TreasureNotFoundException("Treasure not found with id: " + id));
    }

    @Transactional
    public void deleteTreasure(Long id) {
        // TODO: Use Copilot Agent Mode to implement a 'soft delete' mechanism instead of physical deletion
        if (!treasureRepository.existsById(id)) {
            throw new TreasureNotFoundException("Treasure not found with id: " + id);
        }
        treasureRepository.deleteById(id);
    }

    private TreasureDTO toDto(Treasure treasure) {
        // TODO: Use Copilot to suggest boilerplate code for a more complex DTO mapping
        return new TreasureDTO(treasure.getId(), treasure.getName(), treasure.getType(), treasure.getValue(), treasure.getOrigin());
    }

    private Treasure toEntity(TreasureDTO treasureDTO) {
        // TODO: Use Copilot to suggest boilerplate code for a more complex Entity mapping
        return new Treasure(treasureDTO.getId(), treasureDTO.getName(), treasureDTO.getType(), treasureDTO.getValue(), treasureDTO.getOrigin());
    }
}
