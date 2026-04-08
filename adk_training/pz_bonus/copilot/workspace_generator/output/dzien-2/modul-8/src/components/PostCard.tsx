import React from 'react';
import { Post } from '../types';

interface PostCardProps {
  post: Post;
}

const PostCard: React.FC<PostCardProps> = ({ post }) => {
  // TODO: Implement like/dislike functionality for the post
  // TODO: Add a comment section or a button to view comments
  // TODO: Display user information (avatar, username) associated with the post

  return (
    <div className="post-card">
      <div className="post-header">
        <h3 className="post-title">{post.title}</h3>
        <span className="post-author">By {post.author.username}</span>
        <span className="post-date">{new Date(post.createdAt).toLocaleDateString()}</span>
      </div>
      <p className="post-content">{post.content}</p>
      <div className="post-footer">
        <button className="like-button">Like ({post.likes})</button>
        {/* TODO: Add a share button */}
      </div>
    </div>
  );
};

export default PostCard;
