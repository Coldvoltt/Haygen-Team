const API_BASE = "http://localhost:8000/api";

export async function fetchAvatars() {
  const res = await fetch(`${API_BASE}/avatars`);
  if (!res.ok) throw new Error("Failed to fetch avatars");
  return res.json();
}

export async function createTeam(teamName, members) {
  const res = await fetch(`${API_BASE}/team`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ team_name: teamName, members }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to create team");
  }
  return res.json();
}

export async function getTeam(teamId) {
  const res = await fetch(`${API_BASE}/team/${teamId}`);
  if (!res.ok) throw new Error("Failed to fetch team");
  return res.json();
}

export async function listTeams() {
  const res = await fetch(`${API_BASE}/teams`);
  if (!res.ok) throw new Error("Failed to list teams");
  return res.json();
}

export async function fetchStreamingToken() {
  const res = await fetch(`${API_BASE}/streaming-token`, { method: "POST" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to fetch streaming token");
  }
  const data = await res.json();
  return data.token;
}
