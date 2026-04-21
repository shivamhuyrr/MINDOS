"use client";

import { useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatPage from "./components/ChatPage";
import MoodDashboard from "./components/MoodDashboard";
import SettingsPage from "./components/SettingsPage";

export default function Home() {
  const [currentPage, setCurrentPage] = useState<string>("chat");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const renderPage = () => {
    switch (currentPage) {
      case "mood":
        return <MoodDashboard />;
      case "settings":
        return <SettingsPage />;
      default:
        return <ChatPage />;
    }
  };

  return (
    <div className="app-layout">
      <Sidebar
        currentPage={currentPage}
        onNavigate={(page) => {
          setCurrentPage(page);
          setSidebarOpen(false);
        }}
        isOpen={sidebarOpen}
      />

      {/* Mobile menu button */}
      <button
        className="mobile-menu-btn"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        style={{
          position: "fixed",
          top: 16,
          left: 16,
          zIndex: 200,
          display: "none",
          width: 40,
          height: 40,
          borderRadius: "var(--radius-md)",
          background: "var(--bg-glass)",
          border: "1px solid var(--border-glass)",
          backdropFilter: "blur(10px)",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "1.2rem",
        }}
      >
        ☰
      </button>

      <main className="app-main">{renderPage()}</main>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.5)",
            zIndex: 99,
          }}
        />
      )}

      <style jsx>{`
        @media (max-width: 768px) {
          .mobile-menu-btn {
            display: flex !important;
          }
        }
      `}</style>
    </div>
  );
}
