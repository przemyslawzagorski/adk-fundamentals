# Module 8: Grand Finale - Social Media Frontend (React/TypeScript)

This module focuses on building a modern social media content platform frontend using React and TypeScript.
It demonstrates advanced concepts in React development, API integration, and state management.

## Project Structure

- `src/App.tsx`: The main application component, orchestrating different sections.
- `src/components/`: Contains reusable UI components like `PostFeed`, `PostCard`, and `CreatePostForm`.
- `src/api.ts`: Centralized service for interacting with the backend API.
- `src/types.ts`: TypeScript type definitions for data models.
- `src/App.css`: Basic styling for the application (not provided in detail, assumed for project setup).

## Key Features Implemented (with TODOs for Copilot)

- **Post Feed:** Displaying a list of social media posts.
  - TODO: Implement pagination/infinite scrolling.
  - TODO: Add real-time updates for new posts.
- **Post Creation:** A form for users to create and publish new posts.
  - TODO: Integrate with backend API for post submission.
  - TODO: Add client-side validation and character limits.
- **Individual Post Cards:** Displaying details of a single post.
  - TODO: Implement like/comment functionality.
  - TODO: Display user profile information.
- **API Integration:** Centralized service for fetching and creating posts.
  - TODO: Add error handling and loading states.
  - TODO: Implement authentication headers.
- **Type Safety:** Using TypeScript for robust and maintainable code.

## How to Run (Local Development)

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd dzien-2/modul-8
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    # or yarn install
    ```
3.  **Start the development server:**
    ```bash
    npm start
    # or yarn start
    ```
    The application should now be running on `http://localhost:3000` (or another port).

## GitHub Copilot Masterclass Learning Objectives

This module is designed to challenge you with advanced scenarios for GitHub Copilot:

-   **Multi-file Refactoring:** Use Copilot Agent Mode to refactor components and integrate new features across multiple files (e.g., adding a comment section).
-   **Complex API Logic:** Leverage Copilot to assist in building intricate API request and response handling, including authentication and error management.
-   **State Management:** Utilize Copilot to suggest and implement advanced state management patterns (e.g., Redux Toolkit, React Context API, Zustand) for the application.
-   **Testing:** Employ Copilot to generate unit and integration tests for React components and API services using libraries like React Testing Library and Jest.
-   **Performance Optimization:** Ask Copilot for suggestions on optimizing component rendering and API call efficiency.

Remember to use `@workspace` context and engage in self-correction loops with Copilot Agent Mode for the best results.
