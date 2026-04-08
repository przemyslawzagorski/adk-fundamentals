package com.hr.management.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.provisioning.InMemoryUserDetailsManager;
import org.springframework.security.web.SecurityFilterChain;

import static org.springframework.security.config.Customizer.withDefaults;

/**
 * Spring Security Configuration for the HR Management application.
 * Defines security rules, authentication mechanisms, and authorization policies.
 *
 * Learning objectives for Copilot:
 * - Generate basic Spring Security configurations for REST APIs.
 * - Configure URL-based authorization rules.
 * - Integrate custom authentication providers (if applicable).
 * - Disable CSRF for stateless REST APIs.
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    // TODO: Using Copilot Chat, ask for a `SecurityFilterChain` configuration in `SecurityConfig.java` that secures all `/api/**` endpoints except `/api/public/**` (which doesn't exist yet, but for future proofing), and uses HTTP Basic Authentication.
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable()) // Disable CSRF for stateless REST APIs
            .authorizeHttpRequests(authorize -> authorize
                .requestMatchers("/api/public/**").permitAll() // Example public access path
                .requestMatchers("/api/employees/**").authenticated() // Require authentication for employee endpoints
                // TODO: Add more specific authorization rules, e.g., .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .httpBasic(withDefaults()); // Use HTTP Basic Authentication

        return http.build();
    }

    // TODO: Using inline completion, generate a `BCryptPasswordEncoder` bean in `SecurityConfig.java`.
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    // TODO: Using Copilot Chat, ask to generate an `InMemoryUserDetailsManager` bean in `SecurityConfig.java` for development purposes, with a user 'admin' and role 'ADMIN'.
    @Bean
    public UserDetailsService userDetailsService() {
        UserDetails user = User.builder()
            .username("admin")
            .password(passwordEncoder().encode("password")) // Encode the password
            .roles("ADMIN")
            .build();
        return new InMemoryUserDetailsManager(user);
    }
}
