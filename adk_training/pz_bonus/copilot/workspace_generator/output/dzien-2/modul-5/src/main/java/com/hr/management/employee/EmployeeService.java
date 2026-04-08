package com.hr.management.employee;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.data.crossstore.ChangeSetPersister.NotFoundException;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Service layer for managing Employee-related business logic.
 * Handles operations such as creating, retrieving, updating, and deleting employee records.
 *
 * Learning objectives for Copilot:
 * - Implement service methods that interact with repositories.
 * - Handle exceptions gracefully (e.g., entity not found).
 * - Apply transactional annotations for data consistency.
 * - Implement DTO-to-entity and entity-to-DTO conversion logic.
 */
@Service
public class EmployeeService {

    private final EmployeeRepository employeeRepository;

    // TODO: Using inline completion in `EmployeeService.java`, generate the constructor and inject `EmployeeRepository`.
    public EmployeeService(EmployeeRepository employeeRepository) {
        this.employeeRepository = employeeRepository;
    }

    // TODO: Using inline completion, implement the `getAllEmployees` method, ensuring proper conversion to DTOs.
    //       Use Copilot Chat with `@workspace` context if needed to recall Employee to EmployeeDTO mapping logic.
    @Transactional(readOnly = true)
    public List<EmployeeDTO> getAllEmployees() {
        return employeeRepository.findAll().stream()
                .map(employee -> {
                    EmployeeDTO dto = new EmployeeDTO();
                    // TODO: Use Copilot Chat with `@workspace` context to map all fields from employee to dto here
                    dto.setId(employee.getId());
                    dto.setFirstName(employee.getFirstName());
                    dto.setLastName(employee.getLastName());
                    dto.setEmail(employee.getEmail());
                    dto.setPosition(employee.getPosition());
                    dto.setHireDate(employee.getHireDate());
                    dto.setSalary(employee.getSalary());
                    return dto;
                })
                .collect(Collectors.toList());
    }

    // TODO: Using inline completion, implement the `getEmployeeById` method, returning an Optional<EmployeeDTO>.
    //       Use Copilot Chat with `@workspace` context if needed to recall Employee to EmployeeDTO mapping logic.
    @Transactional(readOnly = true)
    public Optional<EmployeeDTO> getEmployeeById(Long id) {
        return employeeRepository.findById(id)
                .map(employee -> {
                    EmployeeDTO dto = new EmployeeDTO();
                    // TODO: Use Copilot Chat with `@workspace` context to map all fields from employee to dto here
                    dto.setId(employee.getId());
                    dto.setFirstName(employee.getFirstName());
                    dto.setLastName(employee.getLastName());
                    dto.setEmail(employee.getEmail());
                    dto.setPosition(employee.getPosition());
                    dto.setHireDate(employee.getHireDate());
                    dto.setSalary(employee.getSalary());
                    return dto;
                });
    }

    // TODO: Using inline completion, implement the `createEmployee` method from an EmployeeDTO.
    //       Use Copilot Chat with `@workspace` context if needed to recall EmployeeDTO to Employee mapping logic.
    @Transactional
    public EmployeeDTO createEmployee(EmployeeDTO employeeDTO) {
        Employee employee = new Employee();
        // TODO: Use Copilot Chat with `@workspace` context to map fields from dto to employee (excluding id) here
        employee.setFirstName(employeeDTO.getFirstName());
        employee.setLastName(employeeDTO.getLastName());
        employee.setEmail(employeeDTO.getEmail());
        employee.setPosition(employeeDTO.getPosition());
        employee.setHireDate(employeeDTO.getHireDate());
        employee.setSalary(employeeDTO.getSalary());

        Employee savedEmployee = employeeRepository.save(employee);
        // TODO: Use Copilot Chat with `@workspace` context to convert saved Employee entity back to EmployeeDTO here
        employeeDTO.setId(savedEmployee.getId()); // Set the generated ID back to DTO
        return employeeDTO;
    }

    // TODO: Using inline completion, implement the `updateEmployee` method, throwing `NotFoundException` if not found.
    //       Use Copilot Chat with `@workspace` context if needed to recall mapping logic.
    @Transactional
    public EmployeeDTO updateEmployee(Long id, EmployeeDTO employeeDTO) throws NotFoundException {
        return employeeRepository.findById(id).map(existingEmployee -> {
            // TODO: Use Copilot Chat with `@workspace` context to update fields of existingEmployee with data from employeeDTO here
            existingEmployee.setFirstName(employeeDTO.getFirstName());
            existingEmployee.setLastName(employeeDTO.getLastName());
            existingEmployee.setEmail(employeeDTO.getEmail());
            existingEmployee.setPosition(employeeDTO.getPosition());
            existingEmployee.setHireDate(employeeDTO.getHireDate());
            existingEmployee.setSalary(employeeDTO.getSalary());

            Employee updatedEmployee = employeeRepository.save(existingEmployee);
            employeeDTO.setId(updatedEmployee.getId()); // Ensure DTO has correct ID
            return employeeDTO;
        }).orElseThrow(NotFoundException::new);
    }

    // TODO: Using inline completion, implement the `deleteEmployee` method by ID.
    @Transactional
    public void deleteEmployee(Long id) {
        employeeRepository.deleteById(id);
    }

    // TODO: Using inline completion, implement the `getEmployeesByPosition` method using the repository method.
    //       Use Copilot Chat with `@workspace` context if needed to recall mapping logic.
    @Transactional(readOnly = true)
    public List<EmployeeDTO> getEmployeesByPosition(String position) {
        return employeeRepository.findByPositionOrderByLastNameAsc(position).stream()
                .map(employee -> {
                    EmployeeDTO dto = new EmployeeDTO();
                    // TODO: Use Copilot Chat with `@workspace` context to map fields from employee to dto here
                    dto.setId(employee.getId());
                    dto.setFirstName(employee.getFirstName());
                    dto.setLastName(employee.getLastName());
                    dto.setEmail(employee.getEmail());
                    dto.setPosition(employee.getPosition());
                    dto.setHireDate(employee.getHireDate());
                    dto.setSalary(employee.getSalary());
                    return dto;
                })
                .collect(Collectors.toList());
    }
}
