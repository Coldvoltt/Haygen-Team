import { useState } from "react";
import { createTeam } from "../api";

export default function CreateTeam({ onTeamCreated }) {
  const [teamName, setTeamName] = useState("");
  const [members, setMembers] = useState([{ name: "", intro_text: "" }]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const addMember = () => {
    setMembers([...members, { name: "", intro_text: "" }]);
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!teamName.trim()) {
      setError("Team name is required");
      return;
    }

    const validMembers = members.filter(
      (m) => m.name.trim() && m.intro_text.trim()
    );
    if (validMembers.length === 0) {
      setError("Add at least one member with name and intro text");
      return;
    }

    setLoading(true);
    try {
      const result = await createTeam(teamName.trim(), validMembers);
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
