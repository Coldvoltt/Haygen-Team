import { useState } from "react";
import CreateTeam from "./components/CreateTeam";
import TeamGrid from "./components/TeamGrid";
import "./App.css";

function App() {
  const [team, setTeam] = useState(null);

  const handleBack = () => {
    setTeam(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Team Avatar Introductions</h1>
        <p>Create your team and let AI avatars introduce each member</p>
      </header>

      <main>
        {team ? (
          <>
            <button className="btn-back" onClick={handleBack}>
              &larr; Create New Team
            </button>
            <TeamGrid team={team} />
          </>
        ) : (
          <CreateTeam onTeamCreated={setTeam} />
        )}
      </main>
    </div>
  );
}

export default App;
