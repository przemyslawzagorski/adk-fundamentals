package com.hr.management.employee;

import java.time.LocalDate;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;

/**
 * Data Transfer Object for Employee information.
 * Used for transferring employee data between layers, often for API requests/responses.
 *
 * Learning objectives for Copilot:
 * - Generate DTO structures with appropriate validation annotations.
 * - Create constructors, getters, and setters for DTO fields.
 * - Map DTO fields to entity fields (e.g., in a service layer).
 */
public class EmployeeDTO {

    private Long id;

    @NotBlank(message = "First name cannot be empty")
    private String firstName;

    @NotBlank(message = "Last name cannot be empty")
    private String lastName;

    @NotBlank(message = "Email cannot be empty")
    @Email(message = "Email should be valid")
    private String email;

    @NotBlank(message = "Position cannot be empty")
    private String position;

    @NotNull(message = "Hire date cannot be null")
    private LocalDate hireDate;

    @PositiveOrZero(message = "Salary must be positive or zero")
    private Double salary;

    // TODO: Using inline completion in `EmployeeDTO.java`, generate a no-arg constructor.
    public EmployeeDTO() {
    }

    // TODO: Using inline completion in `EmployeeDTO.java`, generate an all-arg constructor, excluding the 'id' field.
    public EmployeeDTO(String firstName, String lastName, String email, String position, LocalDate hireDate, Double salary) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.email = email;
        this.position = position;
        this.hireDate = hireDate;
        this.salary = salary;
    }

    // TODO: Using inline completion in `EmployeeDTO.java`, generate all getters and setters.
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getFirstName() {
        return firstName;
    }

    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }

    public String getLastName() {
        return lastName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPosition() {
        return position;
    }

    public void setPosition(String position) {
        this.position = position;
    }

    public LocalDate getHireDate() {
        return hireDate;
    }

    public void setHireDate(LocalDate hireDate) {
        this.hireDate = hireDate;
    }

    public Double getSalary() {
        return salary;
    }

    public void setSalary(Double salary) {
        this.salary = salary;
    }

    // TODO: Using Copilot Chat, ask to implement the `fromEntity` method in `EmployeeDTO.java` to map fields from an `Employee` entity. Pay attention to `id`.
    public static EmployeeDTO fromEntity(Employee employee) {
        // TODO: Copilot should fill this in
        return null; // Placeholder
    }

    // TODO: Using Copilot Chat, ask to implement the `toEntity` method in `EmployeeDTO.java` to map fields to an `Employee` entity.
    public Employee toEntity() {
        // TODO: Copilot should fill this in
        return null; // Placeholder
    }
}
