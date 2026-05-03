"use client";

interface SidebarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
  isOpen: boolean;
}

export default function Sidebar({ currentPage, onNavigate, isOpen }: SidebarProps) {
  const navItems = [
    { id: "chat", icon: "💬", label: "Chat" },
    { id: "mood", icon: "📊", label: "Mood Tracker" },
    { id: "settings", icon: "⚙️", label: "Settings" },
  ];

  return (
    <aside className={`app-sidebar ${isOpen ? "open" : ""}`}>
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">🧠</div>
        <h1>MindOS AI</h1>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <button
            key={item.id}
            className={`nav-link ${currentPage === item.id ? "active" : ""}`}
            onClick={() => onNavigate(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div style={{ padding: "12px 16px" }}>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", lineHeight: 1.5 }}>
            MindOS AI is a wellness companion, not a replacement for professional therapy.
          </p>
        </div>
      </div>
    </aside>
  );
}
