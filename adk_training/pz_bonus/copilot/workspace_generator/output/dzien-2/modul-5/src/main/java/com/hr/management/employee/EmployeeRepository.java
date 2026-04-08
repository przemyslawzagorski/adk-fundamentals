package com.hr.management.employee;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.Optional;
import java.util.List;

/**
 * Repository interface for Employee entities.
 * Provides standard CRUD operations and custom query methods for employee data access.
 *
 * Learning objectives for Copilot:
 * - Generate Spring Data JPA repository interfaces.
 * - Create custom query methods based on method naming conventions.
 * - Define complex queries using @Query annotation.
 */
@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {

    // TODO: Using inline completion in `EmployeeRepository.java`, generate a method `findByEmail(String email)`.
    Optional<Employee> findByEmail(String email);

    // TODO: Using inline completion in `EmployeeRepository.java`, generate a method `findByPositionOrderByLastNameAsc(String position)`.
    List<Employee> findByPositionOrderByLastNameAsc(String position);

    // TODO: Using inline completion in `EmployeeRepository.java`, generate a method `findBySalaryGreaterThan(Double salary)`.
    List<Employee> findBySalaryGreaterThan(Double salary);

    // TODO: Using Copilot Chat, ask to generate a custom `@Query` for `EmployeeRepository.java` to find employees hired before a specific `LocalDate`.
    // Example of what Copilot might generate:
    // @Query("SELECT e FROM Employee e WHERE e.hireDate < :date")
    // List<Employee> findEmployeesHiredBefore(@Param("date") LocalDate date);
}
