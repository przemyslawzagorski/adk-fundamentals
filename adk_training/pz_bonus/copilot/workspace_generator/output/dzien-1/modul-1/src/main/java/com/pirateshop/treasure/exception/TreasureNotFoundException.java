package com.pirateshop.treasure.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

/**
 * Custom exception to indicate that a treasure was not found.
 * Demonstrates custom exception handling in Spring Boot.
 */
@ResponseStatus(HttpStatus.NOT_FOUND)
public class TreasureNotFoundException extends RuntimeException {

    // TODO: Use Copilot to suggest adding constructors for different error message types or cause chaining

    public TreasureNotFoundException(String message) {
        super(message);
    }

    public TreasureNotFoundException(String message, Throwable cause) {
        super(message, cause);
    }
}
