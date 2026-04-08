# Module 3: Chirurgiczny Refaktoring (Copilot Edits) - Healthcare / Medical Records

## Overview
This module focuses on demonstrating advanced GitHub Copilot features, particularly Agent Mode and `@workspace` context, within the domain of a **Healthcare / Medical Records** system. The goal is to simulate complex refactoring tasks and illustrate how Copilot can assist in multi-file operations, self-correction, and context-aware code generation.

## Domain: Healthcare / Medical Records
This project implements a basic system for managing patient information and their medical records. It includes core functionalities such as patient registration, adding medical records, and retrieving patient history.

## Project Structure
```
dzien-1/modul-3/
├── src/
│   ├── models.py                   # Data models (Patient, MedicalRecord, Doctor)
│   ├── patient_repository.py       # Data access layer for patients and medical records
│   ├── medical_record_service.py   # Business logic for medical record operations
│   └── medical_record_controller.py # Simulated API controller for handling requests
├── tests/
│   └── test_medical_record_service.py # Unit tests for the MedicalRecordService
├── config.py                       # Application configuration (development, production, testing)
├── main.py                         # Application entry point and demonstration
└── README.md                       # Project overview and instructions
```

## Key Concepts Demonstrated
- **Agent Mode:** Used for multi-file refactoring, database integration, and complex task execution.
- **`@workspace` Context:** Applied for context-aware suggestions, ensuring consistency across related files, and generating comprehensive solutions.
- **Self-correction Loops:** Illustrated through `TODO` comments, guiding the user to employ Copilot's iterative refinement capabilities.
- **Chirurgiczny Refaktoring (Surgical Refactoring):** Focused on precise, targeted code modifications guided by Copilot.

## How to Use (with GitHub Copilot)
1.  **Explore `TODO` Comments:** Open any `.py` file in the `src` or `tests` directory. You will find numerous `TODO` comments indicating places where GitHub Copilot's advanced features can be leveraged.
2.  **Agent Mode Activation:** For `TODO`s mentioning "Agent Mode," engage Copilot Chat and follow the instructions to initiate a multi-step refactoring or implementation.
    *   *Example Prompt for Agent Mode:* "`@workspace` I need to replace the in-memory `PatientRepository` with a SQLite database. Refactor all necessary parts of the application, including the service layer and relevant test mocks, and generate the necessary SQL schema. Use self-correction if initial attempts fail."
3.  **`@workspace` Context:** When a `TODO` suggests using `@workspace`, use Copilot Chat with this prefix to provide a broader context for your query. This helps Copilot understand the entire project's structure for more accurate suggestions.
    *   *Example Prompt for `@workspace`:* "`@workspace` Refactor the error handling in `medical_record_controller.py` to use a standardized error response format. Ensure this format is consistent across all endpoints."
4.  **Self-correction:** Pay attention to `TODO`s that prompt for self-correction. This involves providing feedback to Copilot on its output and iterating until the desired outcome is achieved.

## Running the Demo
To run the basic application flow, execute `main.py`:

```bash
python dzien-1/modul-3/main.py
```

This will simulate patient registration, medical record addition, and data retrieval using the in-memory repositories.

## TODO Highlights for Copilot
-   **`src/models.py`**: Add validation logic, enhance data structures (e.g., for medication details).
-   **`src/patient_repository.py`**: Replace in-memory storage with a real database (SQLite/PostgreSQL) using Agent Mode.
-   **`src/medical_record_service.py`**: Implement event publishing, input validation, and advanced data processing (e.g., sensitive data redaction).
-   **`src/medical_record_controller.py`**: Standardize error responses, integrate notification services, and refine API endpoints.
-   **`tests/test_medical_record_service.py`**: Enhance test coverage, refine mock objects, and add advanced test cases.
-   **`config.py`**: Implement dynamic configuration loading and production-grade security practices.
-   **`main.py`**: Convert to a full web framework (FastAPI/Flask) application with proper dependency injection.

This module is designed to give you hands-on experience with Copilot's powerful capabilities for complex code transformations and intelligent assistance.
