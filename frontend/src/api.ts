export type ExceptionRow = {
  code: string;
  kind: string;
  title: string;
  dollar_impact: number;
  recommendation: string;
  action: string;
  sku_code: string | null;
  dc_code: string | null;
  plant_code: string | null;
  detail: string;
  acknowledged: boolean;
};

export type Queue = {
  week: number;
  n: number;
  total_impact: number;
  exceptions: ExceptionRow[];
};

const TOKEN_KEY = "plantpulse-token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(path, { ...init, headers });
  if (response.status === 401) {
    clearToken();
    throw new Error("unauthorized");
  }
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json() as Promise<T>;
}

export const api = {
  async login(email: string, password: string) {
    const body = new URLSearchParams();
    body.set("username", email);
    body.set("password", password);
    const data = await request<{ access_token: string }>("/api/auth/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    setToken(data.access_token);
  },
  queue: () => request<Queue>("/api/exceptions"),
  ack: (code: string) =>
    request<ExceptionRow>("/api/exceptions/ack", {
      method: "POST",
      body: JSON.stringify({ code }),
    }),
};
