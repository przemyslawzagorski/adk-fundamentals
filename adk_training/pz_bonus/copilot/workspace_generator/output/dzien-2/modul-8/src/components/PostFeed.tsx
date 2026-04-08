import React from 'react';
import PostCard from './PostCard';
import { Post } from '../types';

interface PostFeedProps {
  posts: Post[];
  // TODO: Add a prop for handling post deletion or editing if applicable
}

const PostFeed: React.FC<PostFeedProps> = ({ posts }) => {
  // TODO: Implement loading state and error handling for the post feed
  // TODO: Add pagination or infinite scrolling logic

  if (!posts || posts.length === 0) {
    return <p>No posts to display yet. Be the first to share!</p>;
  }

  return (
    <div className="post-feed">
      {posts.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  );
};

export default PostFeed;
