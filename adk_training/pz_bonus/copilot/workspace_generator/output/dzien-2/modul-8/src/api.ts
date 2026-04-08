import { Post, NewPost } from './types';

const API_BASE_URL = 'http://localhost:3000/api'; // TODO: Configure this URL based on environment variables

export const fetchPosts = async (): Promise<Post[]> => {
  // TODO: Use Copilot to implement error handling for network requests (try-catch, etc.)
  // TODO: Add support for query parameters (e.g., pagination, sorting, filtering)
  const response = await fetch(`${API_BASE_URL}/posts`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
};

export const createPost = async (post: NewPost): Promise<Post> => {
  // TODO: Implement authentication headers (e.g., JWT token) for creating posts
  const response = await fetch(`${API_BASE_URL}/posts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      // 'Authorization': 'Bearer YOUR_TOKEN' // Example auth header
    },
    body: JSON.stringify(post),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
  }
  return response.json();
};

// TODO: Use Copilot to add functions for updating and deleting posts
// TODO: Implement user authentication related API calls (login, register, logout)
