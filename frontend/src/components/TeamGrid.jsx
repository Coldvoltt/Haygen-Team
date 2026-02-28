import { useState } from "react";
import MemberCard from "./MemberCard";
import VideoModal from "./VideoModal";

export default function TeamGrid({ team }) {
  const [activeMember, setActiveMember] = useState(null);
  const [activeVideoUrl, setActiveVideoUrl] = useState(null);

  const handlePlay = (member, videoUrl) => {
    setActiveMember(member);
    setActiveVideoUrl(videoUrl);
  };

  const handleClose = () => {
    setActiveMember(null);
    setActiveVideoUrl(null);
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
            teamId={team.team_id}
            memberIndex={index}
            onPlay={handlePlay}
          />
        ))}
      </div>

      {activeMember && activeVideoUrl && (
        <VideoModal
          member={activeMember}
          videoUrl={activeVideoUrl}
          onClose={handleClose}
        />
      )}
    </div>
  );
}
