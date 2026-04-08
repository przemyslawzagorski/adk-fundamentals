package com.bank.copilot.module2;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

/**
 * Main Spring Boot application class for the Banking Financial Services module.
 * Configures component scanning and starts the application context.
 */
@SpringBootApplication
// TODO: Use @workspace context to configure application-wide security (OAuth2, JWT)
@ComponentScan(basePackages = "com.bank.copilot.module2")
public class BankingApplication {

    public static void main(String[] args) {
        // TODO: Use Copilot Agent Mode to add custom Spring Boot starters for observability (metrics, tracing)
        SpringApplication.run(BankingApplication.class, args);
        System.out.println("\nBank Copilot Module 2 Application Started Successfully!\n");
    }
}
