package com.hr.management.employee;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.LocalDate;

/**
 * Represents an Employee entity in the HR management system.
 * This class defines the structure for employee data, including personal and professional details.
 *
 * Learning objectives for Copilot:
 * - Generate entity definitions with JPA annotations.
 * - Create constructors, getters, and setters based on fields.
 * - Implement data validation constraints.
 */
@Entity
@Table(name = "employees")
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String firstName;
    private String lastName;
    private String email;
    private String position;
    private LocalDate hireDate;
    private Double salary;

    // TODO: Using inline completion in `Employee.java`, generate a no-arg constructor.
    public Employee() {
    }

    // TODO: Using inline completion in `Employee.java`, generate an all-arg constructor, excluding the 'id' field.
    public Employee(String firstName, String lastName, String email, String position, LocalDate hireDate, Double salary) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.email = email;
        this.position = position;
        this.hireDate = hireDate;
        this.salary = salary;
    }

    // TODO: Using inline completion in `Employee.java`, generate all getters.
    public Long getId() {
        return id;
    }

    public String getFirstName() {
        return firstName;
    }

    public String getLastName() {
        return lastName;
    }

    public String getEmail() {
        return email;
    }

    public String getPosition() {
        return position;
    }

    public LocalDate getHireDate() {
        return hireDate;
    }

    public Double getSalary() {
        return salary;
    }

    // TODO: Using inline completion in `Employee.java`, generate all setters (excluding `id`).
    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public void setPosition(String position) {
        this.position = position;
    }

    public void setHireDate(LocalDate hireDate) {
        this.hireDate = hireDate;
    }

    public void setSalary(Double salary) {
        this.salary = salary;
    }

    // TODO: Implement a meaningful toString() method for logging and debugging
    @Override
    public String toString() {
        return "Employee{" +
               "id=" + id +
               ", firstName='" + firstName + ''' +
               ", lastName='" + lastName + ''' +
               ", email='" + email + ''' +
               ", position='" + position + ''' +
               ", hireDate=" + hireDate +
               ", salary=" + salary +
               '}';
    }

    // TODO: Using Copilot Chat, ask to generate `equals()` and `hashCode()` methods based on the `email` field for `Employee.java`.
}
