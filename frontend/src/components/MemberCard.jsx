export default function MemberCard({ member, onClick }) {
  return (
    <div
      className="member-card"
      onClick={() => onClick(member)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && onClick(member)}
    >
      <div className="avatar-preview">
        {member.avatar_preview_image ? (
          <img src={member.avatar_preview_image} alt={member.avatar_name} />
        ) : (
          <div className="avatar-placeholder">
            {member.name.charAt(0).toUpperCase()}
          </div>
        )}
      </div>

      <div className="member-info">
        <h3>{member.name}</h3>
      </div>
    </div>
  );
}
