import { apiFetch } from "./client";
import type { BlogPayload, CollaboratorPayload, StatusResponse } from "../types/api";

export interface CreateBlogPayload {
  naver_blog_id: string;
  title?: string;
}

export interface VerifyBlogPayload {
  post_url: string;
  title?: string;
  body?: string;
}

export async function fetchBlogs(apiKey: string): Promise<BlogPayload[]> {
  return apiFetch<BlogPayload[]>("/blogs", {
    apiKey,
  });
}

export async function createBlog(apiKey: string, payload: CreateBlogPayload): Promise<BlogPayload> {
  return apiFetch<BlogPayload>("/blogs", {
    method: "POST",
    apiKey,
    body: payload,
  });
}

export async function verifyBlog(
  apiKey: string,
  blogId: number,
  payload: VerifyBlogPayload
): Promise<StatusResponse> {
  return apiFetch<StatusResponse>(`/blogs/${blogId}/verify`, {
    method: "POST",
    apiKey,
    body: payload,
  });
}

export async function disownBlog(apiKey: string, blogId: number): Promise<StatusResponse> {
  return apiFetch<StatusResponse>(`/blogs/${blogId}/disown`, {
    method: "POST",
    apiKey,
  });
}

export async function fetchCollaborators(apiKey: string, blogId: number): Promise<CollaboratorPayload[]> {
  const response = await apiFetch<{ collaborators: CollaboratorPayload[] }>(`/blogs/${blogId}/collaborators`, {
    apiKey,
  });
  return response.collaborators;
}

export async function inviteCollaborator(apiKey: string, blogId: number, email: string): Promise<void> {
  await apiFetch(`/blogs/${blogId}/collaborators`, {
    method: "POST",
    apiKey,
    body: { email },
    parseJson: false,
  });
}

export async function revokeCollaborator(apiKey: string, blogId: number, collaboratorId: number): Promise<void> {
  await apiFetch(`/blogs/${blogId}/collaborators/${collaboratorId}`, {
    method: "DELETE",
    apiKey,
    parseJson: false,
  });
}
