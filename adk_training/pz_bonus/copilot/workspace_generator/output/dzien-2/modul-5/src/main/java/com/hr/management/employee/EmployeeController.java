package com.hr.management.employee;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import jakarta.validation.Valid;
import org.springframework.data.crossstore.ChangeSetPersister.NotFoundException;

import java.util.List;

/**
 * REST Controller for Employee management operations.
 * Exposes endpoints for CRUD operations on employee resources.
 *
 * Learning objectives for Copilot:
 * - Generate RESTful API endpoints (GET, POST, PUT, DELETE).
 * - Implement request body validation using @Valid.
 * - Handle exceptions and return appropriate HTTP status codes.
 * - Inject and utilize service layer components.
 */
@RestController
@RequestMapping("/api/employees")
public class EmployeeController {

    private final EmployeeService employeeService;

    // TODO: Using inline completion in `EmployeeController.java`, generate the constructor and inject `EmployeeService`.
    public EmployeeController(EmployeeService employeeService) {
        this.employeeService = employeeService;
    }

    // TODO: Using inline completion, implement the GET endpoint to retrieve all employees.
    @GetMapping
    public ResponseEntity<List<EmployeeDTO>> getAllEmployees() {
        List<EmployeeDTO> employees = employeeService.getAllEmployees();
        return ResponseEntity.ok(employees);
    }

    // TODO: Using inline completion, implement the GET endpoint to retrieve an employee by ID.
    @GetMapping("/{id}")
    public ResponseEntity<EmployeeDTO> getEmployeeById(@PathVariable Long id) {
        return employeeService.getEmployeeById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    // TODO: Using inline completion, implement the POST endpoint to create a new employee.
    @PostMapping
    public ResponseEntity<EmployeeDTO> createEmployee(@Valid @RequestBody EmployeeDTO employeeDTO) {
        EmployeeDTO createdEmployee = employeeService.createEmployee(employeeDTO);
        // TODO: Return 201 Created status and the newly created employee DTO
        return new ResponseEntity<>(createdEmployee, HttpStatus.CREATED);
    }

    // TODO: Using inline completion, implement the PUT endpoint to update an existing employee by ID.
    @PutMapping("/{id}")
    public ResponseEntity<EmployeeDTO> updateEmployee(@PathVariable Long id, @Valid @RequestBody EmployeeDTO employeeDTO) {
        try {
            EmployeeDTO updatedEmployee = employeeService.updateEmployee(id, employeeDTO);
            return ResponseEntity.ok(updatedEmployee);
        } catch (NotFoundException e) {
            return ResponseEntity.notFound().build();
        }
    }

    // TODO: Using inline completion, implement the DELETE endpoint to delete an employee by ID.
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteEmployee(@PathVariable Long id) {
        employeeService.deleteEmployee(id);
        // TODO: Return 204 No Content status upon successful deletion
        return ResponseEntity.noContent().build();
    }

    // TODO: Using inline completion, implement the GET endpoint to find employees by position (e.g., /api/employees/search?position=Developer).
    @GetMapping("/search")
    public ResponseEntity<List<EmployeeDTO>> getEmployeesByPosition(@RequestParam String position) {
        List<EmployeeDTO> employees = employeeService.getEmployeesByPosition(position);
        return ResponseEntity.ok(employees);
    }

    // TODO: Using Copilot Chat with `@workspace` context, ask for best practices to handle `NotFoundException` globally in a Spring Boot application (e.g., using `@ControllerAdvice`). Then apply self-correction to this controller.
}
