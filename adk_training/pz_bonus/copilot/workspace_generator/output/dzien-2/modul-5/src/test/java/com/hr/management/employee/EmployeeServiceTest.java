package com.hr.management.employee;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.crossstore.ChangeSetPersister.NotFoundException;
import org.mockito.ArgumentCaptor;

import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

/**
 * Unit tests for the EmployeeService class.
 * Focuses on testing the business logic within the service layer in isolation.
 *
 * Learning objectives for Copilot:
 * - Generate JUnit 5 test methods for service functionalities.
 * - Use Mockito for mocking repository dependencies.
 * - Write assertions to verify service method outcomes.
 * - Cover edge cases and exception handling.
 */
@ExtendWith(MockitoExtension.class)
public class EmployeeServiceTest {

    @Mock
    private EmployeeRepository employeeRepository;

    @InjectMocks
    private EmployeeService employeeService;

    private Employee employee1;
    private Employee employee2;
    private EmployeeDTO employeeDTO1;
    private EmployeeDTO employeeDTO2;

    @BeforeEach
    void setUp() {
        employee1 = new Employee("John", "Doe", "john.doe@example.com", "Developer", LocalDate.of(2020, 1, 1), 60000.0);
        employee1.setId(1L);
        employee2 = new Employee("Jane", "Smith", "jane.smith@example.com", "QA Engineer", LocalDate.of(2021, 5, 10), 55000.0);
        employee2.setId(2L);

        employeeDTO1 = new EmployeeDTO("John", "Doe", "john.doe@example.com", "Developer", LocalDate.of(2020, 1, 1), 60000.0);
        employeeDTO1.setId(1L);
        employeeDTO2 = new EmployeeDTO("Jane", "Smith", "jane.smith@example.com", "QA Engineer", LocalDate.of(2021, 5, 10), 55000.0);
        employeeDTO2.setId(2L);
    }

    // TODO: Using inline completion, write a test for `getAllEmployees` method, verifying mock interactions and returned DTOs.
    @Test
    void getAllEmployees_shouldReturnListOfEmployeeDTOs() {
        when(employeeRepository.findAll()).thenReturn(Arrays.asList(employee1, employee2));

        List<EmployeeDTO> result = employeeService.getAllEmployees();

        assertNotNull(result);
        assertEquals(2, result.size());
        assertEquals(employeeDTO1.getFirstName(), result.get(0).getFirstName());
        assertEquals(employeeDTO2.getFirstName(), result.get(1).getFirstName());
        verify(employeeRepository, times(1)).findAll();
    }

    // TODO: Using inline completion, write a test for `getEmployeeById` method when employee exists.
    @Test
    void getEmployeeById_whenEmployeeExists_shouldReturnEmployeeDTO() {
        when(employeeRepository.findById(1L)).thenReturn(Optional.of(employee1));

        Optional<EmployeeDTO> result = employeeService.getEmployeeById(1L);

        assertTrue(result.isPresent());
        assertEquals(employeeDTO1.getEmail(), result.get().getEmail());
        verify(employeeRepository, times(1)).findById(1L);
    }

    // TODO: Using inline completion, write a test for `getEmployeeById` method when employee does not exist.
    @Test
    void getEmployeeById_whenEmployeeDoesNotExist_shouldReturnEmptyOptional() {
        when(employeeRepository.findById(anyLong())).thenReturn(Optional.empty());

        Optional<EmployeeDTO> result = employeeService.getEmployeeById(99L);

        assertFalse(result.isPresent());
        verify(employeeRepository, times(1)).findById(99L);
    }

    // TODO: Using inline completion, write a test for `createEmployee` method.
    @Test
    void createEmployee_shouldReturnCreatedEmployeeDTO() {
        Employee newEmployee = new Employee("Alice", "Brown", "alice.brown@example.com", "Designer", LocalDate.of(2022, 3, 15), 70000.0);
        Employee savedEmployee = new Employee("Alice", "Brown", "alice.brown@example.com", "Designer", LocalDate.of(2022, 3, 15), 70000.0);
        savedEmployee.setId(3L);

        when(employeeRepository.save(any(Employee.class))).thenReturn(savedEmployee);

        EmployeeDTO newEmployeeDTO = new EmployeeDTO("Alice", "Brown", "alice.brown@example.com", "Designer", LocalDate.of(2022, 3, 15), 70000.0);
        EmployeeDTO result = employeeService.createEmployee(newEmployeeDTO);

        assertNotNull(result);
        assertEquals(3L, result.getId());
        assertEquals("Alice", result.getFirstName());
        verify(employeeRepository, times(1)).save(any(Employee.class));
    }

    // TODO: Using inline completion, write a test for `updateEmployee` method when employee exists.
    @Test
    void updateEmployee_whenEmployeeExists_shouldReturnUpdatedEmployeeDTO() throws NotFoundException {
        Employee updatedEmployee = new Employee("John", "Doey", "john.doey@example.com", "Senior Developer", LocalDate.of(2020, 1, 1), 65000.0);
        updatedEmployee.setId(1L);

        EmployeeDTO updatedEmployeeDTO = new EmployeeDTO("John", "Doey", "john.doey@example.com", "Senior Developer", LocalDate.of(2020, 1, 1), 65000.0);
        updatedEmployeeDTO.setId(1L);

        when(employeeRepository.findById(1L)).thenReturn(Optional.of(employee1));
        when(employeeRepository.save(any(Employee.class))).thenReturn(updatedEmployee);

        EmployeeDTO result = employeeService.updateEmployee(1L, updatedEmployeeDTO);

        assertNotNull(result);
        assertEquals("john.doey@example.com", result.getEmail());
        assertEquals("Senior Developer", result.getPosition());
        verify(employeeRepository, times(1)).findById(1L);
        verify(employeeRepository, times(1)).save(any(Employee.class));
    }

    // TODO: Using inline completion, write a test for `updateEmployee` method when employee does not exist, expecting `NotFoundException`.
    @Test
    void updateEmployee_whenEmployeeDoesNotExist_shouldThrowNotFoundException() {
        when(employeeRepository.findById(anyLong())).thenReturn(Optional.empty());

        EmployeeDTO nonExistentEmployeeDTO = new EmployeeDTO("Ghost", "Man", "ghost.man@example.com", "Spectre", LocalDate.now(), 0.0);

        assertThrows(NotFoundException.class, () -> employeeService.updateEmployee(99L, nonExistentEmployeeDTO));
        verify(employeeRepository, times(1)).findById(99L);
        verify(employeeRepository, never()).save(any(Employee.class));
    }

    // TODO: Using inline completion, write a test for `deleteEmployee` method.
    @Test
    void deleteEmployee_shouldCallRepositoryDeleteById() {
        doNothing().when(employeeRepository).deleteById(1L);

        employeeService.deleteEmployee(1L);

        verify(employeeRepository, times(1)).deleteById(1L);
    }

    // TODO: Using inline completion, write a test for `getEmployeesByPosition` method.
    @Test
    void getEmployeesByPosition_shouldReturnFilteredListOfEmployeeDTOs() {
        when(employeeRepository.findByPositionOrderByLastNameAsc("Developer")).thenReturn(Arrays.asList(employee1));

        List<EmployeeDTO> result = employeeService.getEmployeesByPosition("Developer");

        assertNotNull(result);
        assertEquals(1, result.size());
        assertEquals("John", result.get(0).getFirstName());
        assertEquals("Developer", result.get(0).getPosition());
        verify(employeeRepository, times(1)).findByPositionOrderByLastNameAsc("Developer");
    }

    // TODO: Using Copilot Agent Mode, ask to refactor all test methods in `EmployeeServiceTest.java` to use `ArgumentCaptor` for verifying complex arguments passed to mocked methods.
}
