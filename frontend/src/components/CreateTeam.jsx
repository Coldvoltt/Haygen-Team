import { useState } from "react";
import { createTeam } from "../api";

export default function CreateTeam({ onTeamCreated }) {
  const [teamName, setTeamName] = useState("");
  const [members, setMembers] = useState([
    { name: "", intro_text: "", photo: null },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const addMember = () => {
    setMembers([...members, { name: "", intro_text: "", photo: null }]);
  };

  const removeMember = (index) => {
    if (members.length <= 1) return;
    setMembers(members.filter((_, i) => i !== index));
  };

  const updateMember = (index, field, value) => {
    const updated = [...members];
    updated[index] = { ...updated[index], [field]: value };
    setMembers(updated);
  };

  const updateMemberPhoto = (index, file) => {
    const updated = [...members];
    updated[index] = { ...updated[index], photo: file };
    setMembers(updated);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!teamName.trim()) {
      setError("Team name is required");
      return;
    }

    // Track original indices so we can map photos correctly
    const validEntries = members
      .map((m, i) => ({ member: m, originalIndex: i }))
      .filter((e) => e.member.name.trim() && e.member.intro_text.trim());

    if (validEntries.length === 0) {
      setError("Add at least one member with name and intro text");
      return;
    }

    // Build photos map: { newIndex: File }
    const photos = {};
    validEntries.forEach((entry, newIndex) => {
      if (entry.member.photo) {
        photos[newIndex] = entry.member.photo;
      }
    });

    // Strip photo from the JSON payload (it goes as a file)
    const membersPayload = validEntries.map(({ member }) => ({
      name: member.name.trim(),
      intro_text: member.intro_text.trim(),
    }));

    setLoading(true);
    try {
      const result = await createTeam(teamName.trim(), membersPayload, photos);
      onTeamCreated(result.team);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-team">
      <h2>Create Your Team</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Team Name</label>
          <input
            type="text"
            value={teamName}
            onChange={(e) => setTeamName(e.target.value)}
            placeholder="e.g. Engineering Team"
          />
        </div>

        <h3>Team Members</h3>
        {members.map((member, index) => (
          <div key={index} className="member-form">
            <div className="member-header">
              <span>Member {index + 1}</span>
              {members.length > 1 && (
                <button
                  type="button"
                  className="btn-remove"
                  onClick={() => removeMember(index)}
                >
                  Remove
                </button>
              )}
            </div>
            <label className="photo-circle-wrapper">
              <input
                type="file"
                accept="image/jpeg,image/png"
                hidden
                onChange={(e) =>
                  updateMemberPhoto(index, e.target.files[0] || null)
                }
              />
              {member.photo ? (
                <img
                  className="photo-circle"
                  src={URL.createObjectURL(member.photo)}
                  alt="Preview"
                />
              ) : (
                <div className="photo-circle photo-circle-empty">
                  <span>+</span>
                </div>
              )}
              <span className="photo-hint">
                {member.photo ? "Change photo" : "Add photo"}
              </span>
            </label>
            <input
              type="text"
              value={member.name}
              onChange={(e) => updateMember(index, "name", e.target.value)}
              placeholder="Name"
            />
            <textarea
              value={member.intro_text}
              onChange={(e) =>
                updateMember(index, "intro_text", e.target.value)
              }
              placeholder="Introduction text the avatar will speak..."
              rows={3}
            />
          </div>
        ))}

        <button type="button" className="btn-secondary" onClick={addMember}>
          + Add Member
        </button>

        {error && <div className="error">{error}</div>}

        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? "Creating Team..." : "Create Team"}
        </button>
      </form>
    </div>
  );
}
