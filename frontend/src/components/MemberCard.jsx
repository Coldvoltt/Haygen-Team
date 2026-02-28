import { useState } from "react";
import { generateIntro } from "../api";

export default function MemberCard({ member, teamId, memberIndex, onPlay }) {
  const [status, setStatus] = useState("idle");
  const [message, setMessage] = useState("");

  const handleClick = async () => {
    if (status === "checking") return;

    setMessage("");
    setStatus("checking");

    try {
      const data = await generateIntro(teamId, memberIndex);

      if (data.status === "completed" && data.video_url) {
        setStatus("ready");
        onPlay(member, data.video_url);
      } else {
        setStatus("not_ready");
        setMessage(`${member.name} will be available shortly.`);
      }
    } catch {
      setStatus("idle");
      setMessage("Something went wrong. Try again.");
    }
  };

  return (
    <div
      className={`member-card ${status}`}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && handleClick()}
    >
      <div className="avatar-preview">
        {member.avatar_preview_image ? (
          <img src={member.avatar_preview_image} alt={member.avatar_name} />
        ) : (
          <div className="avatar-placeholder">
            {member.name.charAt(0).toUpperCase()}
          </div>
        )}
        {status === "checking" && (
          <div className="loading-overlay">
            <div className="spinner" />
          </div>
        )}
        {status === "ready" && <div className="ready-badge" />}
      </div>

      <div className="member-info">
        <h3>{member.name}</h3>
      </div>

      {message && <div className="card-message">{message}</div>}
    </div>
  );
}
