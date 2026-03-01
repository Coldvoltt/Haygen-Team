import { useEffect, useRef, useState } from "react";
import StreamingAvatar, {
  StreamingEvents,
  TaskType,
} from "@heygen/streaming-avatar";
import { fetchStreamingToken } from "../api";

export default function StreamingModal({ member, onClose }) {
  const videoRef = useRef(null);
  const overlayRef = useRef(null);
  const avatarRef = useRef(null);
  const [status, setStatus] = useState("connecting"); // connecting | streaming | done | error
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [onClose]);

  useEffect(() => {
    let cancelled = false;

    async function startSession() {
      try {
        const token = await fetchStreamingToken();
        if (cancelled) return;

        const avatar = new StreamingAvatar({ token });
        avatarRef.current = avatar;

        avatar.on(StreamingEvents.STREAM_READY, () => {
          if (cancelled) return;
          if (videoRef.current && avatar.mediaStream) {
            videoRef.current.srcObject = avatar.mediaStream;
            videoRef.current.play().catch(() => {});
          }
          setStatus("streaming");

          avatar.speak({
            text: member.intro_text,
            task_type: TaskType.REPEAT,
          });
        });

        avatar.on(StreamingEvents.AVATAR_STOP_TALKING, () => {
          if (!cancelled) setStatus("done");
        });

        avatar.on(StreamingEvents.STREAM_DISCONNECTED, () => {
          if (!cancelled && status !== "done") {
            setStatus("error");
            setErrorMsg("Stream disconnected unexpectedly.");
          }
        });

        await avatar.createStartAvatar({
          avatarName: member.avatar_id,
          voice: { voiceId: member.voice_id },
        });
      } catch (err) {
        if (!cancelled) {
          setStatus("error");
          setErrorMsg(err.message || "Failed to start streaming session.");
        }
      }
    }

    startSession();

    return () => {
      cancelled = true;
      if (avatarRef.current) {
        avatarRef.current.stopAvatar().catch(() => {});
        avatarRef.current = null;
      }
    };
  }, [member]);

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
          <video ref={videoRef} autoPlay playsInline />

          {status === "connecting" && (
            <div className="stream-loading-overlay">
              <div className="spinner" />
              <span>Connecting...</span>
            </div>
          )}

          {status === "done" && (
            <div className="modal-status">Introduction complete</div>
          )}

          {status === "error" && (
            <div className="modal-error">{errorMsg}</div>
          )}
        </div>
      </div>
    </div>
  );
}
