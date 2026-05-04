"use client";

import { useState, useEffect } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const MOOD_EMOJIS = ["😢", "😟", "😕", "😐", "🙂", "😊", "😄", "😁", "🤩", "🥳"];

interface MoodEntry {
  id: string;
  score: number;
  emotion: string | null;
  notes: string | null;
  timestamp: string;
}

interface MoodSummaryData {
  average_score: number;
  trend: string;
  dominant_emotion: string;
  entries_count: number;
  ai_summary: string | null;
}

export default function MoodDashboard() {
  const [moodScore, setMoodScore] = useState(5);
  const [moodNotes, setMoodNotes] = useState("");
  const [history, setHistory] = useState<MoodEntry[]>([]);
  const [summary, setSummary] = useState<MoodSummaryData | null>(null);
  const [isLogging, setIsLogging] = useState(false);
  const [userId] = useState(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("mindos_user_id") || "user_default";
    }
    return "user_default";
  });

  useEffect(() => {
    fetchHistory();
    fetchSummary();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/mood/${userId}?days=30`);
      if (res.ok) setHistory(await res.json());
    } catch {}
  };

  const fetchSummary = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/mood/${userId}/summary`);
      if (res.ok) setSummary(await res.json());
    } catch {}
  };

  const logMood = async () => {
    setIsLogging(true);
    try {
      await fetch(`${API_BASE}/api/mood`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          score: moodScore,
          emotion: MOOD_EMOJIS[moodScore - 1],
          notes: moodNotes || null,
        }),
      });
      setMoodNotes("");
      await fetchHistory();
      await fetchSummary();
    } catch {}
    setIsLogging(false);
  };

  const trendIcon = summary?.trend === "improving" ? "📈" : summary?.trend === "declining" ? "📉" : "➡️";

  return (
    <div className="dashboard">
      <h2>Mood Tracker 📊</h2>

      {/* Stats Grid */}
      <div className="dashboard-grid">
        <div className="stat-card glass-card">
          <span className="stat-label">Average Mood</span>
          <span className="stat-value" style={{ color: "var(--purple-400)" }}>
            {summary?.average_score?.toFixed(1) || "—"}
          </span>
          <span className="stat-label">out of 10</span>
        </div>
        <div className="stat-card glass-card">
          <span className="stat-label">Trend</span>
          <span className="stat-value">{trendIcon}</span>
          <span className={`stat-trend ${summary?.trend || "stable"}`}>
            {summary?.trend || "No data yet"}
          </span>
        </div>
        <div className="stat-card glass-card">
          <span className="stat-label">Dominant Emotion</span>
          <span className="stat-value">{summary?.dominant_emotion || "—"}</span>
          <span className="stat-label">{summary?.entries_count || 0} entries</span>
        </div>
      </div>

      {/* AI Summary */}
      {summary?.ai_summary && (
        <div className="glass-card" style={{ padding: 20, marginBottom: 24 }}>
          <h3 style={{ fontSize: "1rem", color: "var(--text-secondary)", marginBottom: 12 }}>
            🧠 AI Insight
          </h3>
          <p style={{ color: "var(--text-primary)", lineHeight: 1.7 }}>{summary.ai_summary}</p>
        </div>
      )}

      {/* Mood Chart (Simple visual) */}
      {history.length > 0 && (
        <div className="mood-chart-container glass-card">
          <h3>Last 30 Days</h3>
          <div style={{ display: "flex", alignItems: "flex-end", gap: 4, height: 120, paddingTop: 8 }}>
            {history.slice(0, 30).reverse().map((entry, i) => (
              <div
                key={entry.id}
                style={{
                  flex: 1,
                  minWidth: 6,
                  height: `${(entry.score / 10) * 100}%`,
                  background: `linear-gradient(to top, var(--purple-600), ${entry.score >= 7 ? "var(--mint-400)" : entry.score >= 4 ? "var(--purple-400)" : "var(--rose-400)"})`,
                  borderRadius: "3px 3px 0 0",
                  transition: "height 0.3s ease",
                  opacity: 0.7 + (i / 30) * 0.3,
                }}
                title={`${new Date(entry.timestamp).toLocaleDateString()}: ${entry.score}/10`}
              />
            ))}
          </div>
          <div style={{
            display: "flex", justifyContent: "space-between",
            marginTop: 8, fontSize: "0.7rem", color: "var(--text-muted)",
          }}>
            <span>30 days ago</span>
            <span>Today</span>
          </div>
        </div>
      )}

      {/* Mood Logger */}
      <div className="mood-logger glass-card">
        <h3>How are you feeling right now?</h3>

        <div className="mood-emojis">
          {MOOD_EMOJIS.map((emoji, i) => (
            <span
              key={i}
              className={`mood-emoji ${moodScore === i + 1 ? "active" : ""}`}
              onClick={() => setMoodScore(i + 1)}
              title={`${i + 1}/10`}
            >
              {emoji}
            </span>
          ))}
        </div>

        <div className="mood-slider-row">
          <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", width: 20 }}>1</span>
          <input
            type="range"
            className="mood-slider"
            min={1}
            max={10}
            value={moodScore}
            onChange={(e) => setMoodScore(Number(e.target.value))}
          />
          <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", width: 20 }}>10</span>
        </div>

        <textarea
          className="mood-notes"
          placeholder="Any notes about how you're feeling? (optional)"
          value={moodNotes}
          onChange={(e) => setMoodNotes(e.target.value)}
        />

        <button className="btn-primary" onClick={logMood} disabled={isLogging}>
          {isLogging ? "Logging..." : `Log Mood — ${MOOD_EMOJIS[moodScore - 1]} ${moodScore}/10`}
        </button>
      </div>

      {/* Recent History */}
      {history.length > 0 && (
        <div className="glass-card" style={{ padding: 20, marginTop: 24 }}>
          <h3 style={{ fontSize: "1rem", color: "var(--text-secondary)", marginBottom: 12 }}>
            Recent Entries
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {history.slice(0, 10).map((entry) => (
              <div key={entry.id} style={{
                display: "flex", alignItems: "center", gap: 12,
                padding: "8px 12px", borderRadius: "var(--radius-sm)",
                background: "var(--bg-surface)",
              }}>
                <span style={{ fontSize: "1.2rem" }}>{MOOD_EMOJIS[(entry.score || 5) - 1]}</span>
                <span style={{ fontWeight: 600 }}>{entry.score}/10</span>
                <span style={{ flex: 1, fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                  {entry.notes || "No notes"}
                </span>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                  {new Date(entry.timestamp).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
