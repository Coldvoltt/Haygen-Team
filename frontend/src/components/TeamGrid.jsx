import { useState } from "react";
import MemberCard from "./MemberCard";
import StreamingModal from "./StreamingModal";

export default function TeamGrid({ team }) {
  const [activeMember, setActiveMember] = useState(null);

  const handleClose = () => {
    setActiveMember(null);
  };

  return (
    <div className="team-grid-container">
      <h2>{team.team_name}</h2>
      <p className="team-subtitle">
        Click on a team member to hear their introduction
      </p>
      <div className="team-grid">
        {team.members.map((member, index) => (
          <MemberCard
            key={index}
            member={member}
            onClick={setActiveMember}
          />
        ))}
      </div>

      {activeMember && (
        <StreamingModal
          member={activeMember}
          onClose={handleClose}
        />
      )}
    </div>
  );
}
