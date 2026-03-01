const API_BASE = "http://localhost:8000/api";

export async function fetchAvatars() {
  const res = await fetch(`${API_BASE}/avatars`);
  if (!res.ok) throw new Error("Failed to fetch avatars");
  return res.json();
}

export async function createTeam(teamName, members, photos = {}) {
  const formData = new FormData();

  // Pack text data as a JSON string
  formData.append(
    "team_data",
    JSON.stringify({ team_name: teamName, members })
  );

  // Attach photo files keyed by member index
  for (const [index, file] of Object.entries(photos)) {
    formData.append(`photo_${index}`, file);
  }

  const res = await fetch(`${API_BASE}/team`, {
    method: "POST",
    body: formData,
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

export async function generateIntro(teamId, memberIndex) {
  const res = await fetch(`${API_BASE}/generate-intro`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ team_id: teamId, member_index: memberIndex }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to generate intro");
  }
  return res.json();
}

export async function getVideoStatus(videoId) {
  const res = await fetch(`${API_BASE}/video-status/${videoId}`);
  if (!res.ok) throw new Error("Failed to get video status");
  return res.json();
}
