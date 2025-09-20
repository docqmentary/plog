export interface SessionPayload {
  user_id: number;
  email: string;
  display_name?: string | null;
  api_key: string;
}

export type BlogStatus = "pending" | "verified" | "disowned";

export interface BlogPayload {
  id: number;
  naver_blog_id: string;
  title?: string | null;
  status: BlogStatus;
  verified_at?: string | null;
  title_token: string;
  body_token: string;
}

export type InvitationStatus = "pending" | "accepted" | "revoked";

export interface CollaboratorPayload {
  id: number;
  email?: string | null;
  status: InvitationStatus;
  invited_at: string;
}

export interface StatusResponse {
  status: string;
  reason?: string | null;
}
