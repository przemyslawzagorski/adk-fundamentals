import React, { useState } from 'react';
import { NewPost } from '../types';

interface CreatePostFormProps {
  onPostCreated: (post: NewPost) => void;
}

const CreatePostForm: React.FC<CreatePostFormProps> = ({ onPostCreated }) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) {
      alert('Title and content cannot be empty.');
      return;
    }
    const newPost: NewPost = {
      title,
      content,
      authorId: 'currentUserId', // TODO: Replace with actual logged-in user ID from context/auth
    };
    onPostCreated(newPost);
    setTitle('');
    setContent('');
  };

  return (
    <form className="create-post-form" onSubmit={handleSubmit}>
      <div>
        <label htmlFor="postTitle">Title:</label>
        <input
          type="text"
          id="postTitle"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What's on your mind?"
          required
        />
      </div>
      <div>
        <label htmlFor="postContent">Content:</label>
        <textarea
          id="postContent"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Share your thoughts..."
          rows={5}
          required
        ></textarea>
      </div>
      <button type="submit">Create Post</button>
      {/* TODO: Add a character counter for the content field */}
      {/* TODO: Implement a preview feature for the post content */}
    </form>
  );
};

export default CreatePostForm;
