"use client";

import { useState } from "react";
import Sidebar from "./components/Sidebar";

export default function Home() {
  const [currentPage, setCurrentPage] = useState<string>("chat");

  return (
    <div className="app-layout">
      <Sidebar
        currentPage={currentPage}
        onNavigate={(page) => setCurrentPage(page)}
        isOpen={false}
      />
      <main className="app-main">
        <div style={{ padding: 40 }}>
          <h2>MindOS AI</h2>
          <p>Select a page from the sidebar.</p>
        </div>
      </main>
    </div>
  );
}
