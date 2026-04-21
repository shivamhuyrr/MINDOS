"use client";

import { useState } from "react";

export default function SettingsPage() {
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [soundEffects, setSoundEffects] = useState(true);
  const [showEmotions, setShowEmotions] = useState(true);

  const handleDeleteData = () => {
    if (window.confirm("Are you sure? This will permanently delete all your chat history, mood data, and memories. This action cannot be undone.")) {
      localStorage.clear();
      window.location.reload();
    }
  };

  const handleExportData = () => {
    const data = {
      userId: localStorage.getItem("mindos_user_id"),
      exportDate: new Date().toISOString(),
      note: "Connect to backend API for full data export",
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "mindos-data-export.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="settings-page">
      <h2>Settings ⚙️</h2>

      {/* Voice & Audio */}
      <div className="settings-section glass-card">
        <h3>🎤 Voice & Audio</h3>
        <div className="setting-row">
          <div>
            <div className="setting-label">Voice Input</div>
            <div className="setting-desc">Enable microphone for voice conversations</div>
          </div>
          <div className={`toggle ${voiceEnabled ? "active" : ""}`} onClick={() => setVoiceEnabled(!voiceEnabled)} />
        </div>
        <div className="setting-row">
          <div>
            <div className="setting-label">Sound Effects</div>
            <div className="setting-desc">Play sounds for message sent/received</div>
          </div>
          <div className={`toggle ${soundEffects ? "active" : ""}`} onClick={() => setSoundEffects(!soundEffects)} />
        </div>
      </div>

      {/* Display */}
      <div className="settings-section glass-card">
        <h3>🎨 Display</h3>
        <div className="setting-row">
          <div>
            <div className="setting-label">Show Emotions</div>
            <div className="setting-desc">Display detected emotion badges on messages</div>
          </div>
          <div className={`toggle ${showEmotions ? "active" : ""}`} onClick={() => setShowEmotions(!showEmotions)} />
        </div>
      </div>

      {/* Data & Privacy */}
      <div className="settings-section glass-card">
        <h3>🔒 Data & Privacy</h3>
        <div className="setting-row">
          <div>
            <div className="setting-label">Export Data</div>
            <div className="setting-desc">Download all your data as JSON</div>
          </div>
          <button className="btn-primary" style={{ padding: "8px 20px", fontSize: "0.85rem" }} onClick={handleExportData}>
            Export
          </button>
        </div>
        <div className="setting-row">
          <div>
            <div className="setting-label">Delete All Data</div>
            <div className="setting-desc">Permanently remove all your data from MindOS</div>
          </div>
          <button className="btn-danger" onClick={handleDeleteData}>
            Delete Everything
          </button>
        </div>
      </div>

      {/* About */}
      <div className="settings-section glass-card">
        <h3>ℹ️ About</h3>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span className="setting-label">Version</span>
            <span style={{ color: "var(--text-muted)" }}>0.1.0 MVP</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span className="setting-label">AI Model</span>
            <span style={{ color: "var(--text-muted)" }}>GPT-4o</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span className="setting-label">Memory</span>
            <span style={{ color: "var(--text-muted)" }}>Pinecone Vector DB</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span className="setting-label">Voice</span>
            <span style={{ color: "var(--text-muted)" }}>ElevenLabs TTS</span>
          </div>
        </div>
        <div style={{ marginTop: 16, padding: 12, background: "var(--bg-surface)", borderRadius: "var(--radius-sm)" }}>
          <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", lineHeight: 1.6 }}>
            ⚠️ <strong>Disclaimer:</strong> MindOS AI is a wellness companion tool and is NOT a substitute for professional mental health care. If you are in crisis, please contact a licensed therapist or call your local emergency number.
          </p>
        </div>
      </div>
    </div>
  );
}
