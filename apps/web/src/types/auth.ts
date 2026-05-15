export type AuthUser = {
  id: number;
  email: string;
  display_name: string | null;
  role: "admin";
};

export type LoginPayload = {
  email: string;
  password: string;
};
