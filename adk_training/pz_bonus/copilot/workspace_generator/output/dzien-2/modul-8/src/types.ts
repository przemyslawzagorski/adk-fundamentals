export interface User {
  id: string;
  username: string;
  email: string;
  // TODO: Add more user-related fields like profile picture, bio, etc.
}

export interface Post {
  id: string;
  title: string;
  content: string;
  author: User;
  createdAt: string;
  updatedAt: string;
  likes: number;
  // TODO: Add fields for comments, tags, media attachments (images/videos)
}

export interface NewPost {
  title: string;
  content: string;
  authorId: string; // Refers to the ID of the user creating the post
}

// TODO: Use Copilot to define interfaces for comments, notifications, etc.
// TODO: Create an interface for API responses, including pagination metadata
