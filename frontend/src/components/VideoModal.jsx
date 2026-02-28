import { useEffect, useRef } from "react";

export default function VideoModal({ member, videoUrl, onClose }) {
  const videoRef = useRef(null);
  const overlayRef = useRef(null);

  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [onClose]);

  const handleOverlayClick = (e) => {
    if (e.target === overlayRef.current) onClose();
  };

  return (
    <div className="modal-overlay" ref={overlayRef} onClick={handleOverlayClick}>
      <div className="modal-content">
        <button className="modal-close" onClick={onClose}>
          &times;
        </button>
        <div className="modal-header">
          <h2>{member.name}</h2>
        </div>
        <div className="modal-video">
          <video
            ref={videoRef}
            src={videoUrl}
            autoPlay
            controls
            onEnded={onClose}
          />
        </div>
      </div>
    </div>
  );
}
