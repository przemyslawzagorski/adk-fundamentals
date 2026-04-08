package com.pirateshop.treasure.dto;

import java.util.Objects;

/**
 * Data Transfer Object for Pirate Treasure.
 * Used for exposing treasure data via REST API and receiving input.
 */
public class TreasureDTO {
    private Long id;
    private String name;
    private String type;
    private double value;
    private String origin;

    // TODO: Use Copilot to suggest adding Bean Validation annotations (e.g., @NotBlank, @Min) to fields

    public TreasureDTO() {
    }

    public TreasureDTO(Long id, String name, String type, double value, String origin) {
        this.id = id;
        this.name = name;
        this.type = type;
        this.value = value;
        this.origin = origin;
    }

    // Getters and Setters
    // TODO: Use Copilot to generate all boilerplate getters and setters if not already present
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public double getValue() {
        return value;
    }

    public void setValue(double value) {
        this.value = value;
    }

    public String getOrigin() {
        return origin;
    }

    public void setOrigin(String origin) {
        this.origin = origin;
    }

    // equals, hashCode, toString
    // TODO: Use Copilot to generate robust equals, hashCode, and toString methods
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        TreasureDTO that = (TreasureDTO) o;
        return Double.compare(that.value, value) == 0 && Objects.equals(id, that.id) && Objects.equals(name, that.name) && Objects.equals(type, that.type) && Objects.equals(origin, that.origin);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, name, type, value, origin);
    }

    @Override
    public String toString() {
        return "TreasureDTO{" +
               "id=" + id +
               ", name='" + name + '\'' +
               ", type='" + type + '\'' +
               ", value=" + value +
               ", origin='" + origin + '\'' +
               '}';
    }
}
