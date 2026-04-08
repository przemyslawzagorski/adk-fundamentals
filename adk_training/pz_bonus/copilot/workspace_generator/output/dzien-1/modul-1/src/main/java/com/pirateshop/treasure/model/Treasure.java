package com.pirateshop.treasure.model;

import jakarta.persistence.*;

import java.util.Objects;

/**
 * Represents a pirate treasure entity in the database.
 * Demonstrates JPA entity mapping and basic domain model structure.
 */
@Entity
@Table(name = "treasures")
public class Treasure {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;
    private String type;
    private double value;
    private String origin;

    // TODO: Use Copilot Agent Mode to suggest adding auditing fields (e.g., createdAt, updatedAt) with @CreatedDate, @LastModifiedDate
    // TODO: Implement optimistic locking with @Version annotation

    public Treasure() {
    }

    public Treasure(Long id, String name, String type, double value, String origin) {
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
    // TODO: Use Copilot to generate robust equals, hashCode, and toString methods for entity consistency
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Treasure treasure = (Treasure) o;
        return Double.compare(treasure.value, value) == 0 && Objects.equals(id, treasure.id) && Objects.equals(name, treasure.name) && Objects.equals(type, treasure.type) && Objects.equals(origin, treasure.origin);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, name, type, value, origin);
    }

    @Override
    public String toString() {
        return "Treasure{" +
               "id=" + id +
               ", name='" + name + '\'' +
               ", type='" + type + '\'' +
               ", value=" + value +
               ", origin='" + origin + '\'' +
               '}';
    }
}
