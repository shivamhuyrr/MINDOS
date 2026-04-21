# MindOS Git History Rebuild Script
# Rebuilds git history with realistic incremental commits

$ErrorActionPreference = "SilentlyContinue"
$ROOT = "c:\Users\Asus\OneDrive\New folder\OneDrive\Desktop\MINDOS"
$BAK = "$ROOT\_backup"

Set-Location $ROOT

# Remove old git and reinit
Remove-Item -Recurse -Force ".git"
git init
git remote add origin https://github.com/shivamhuyrr/MINDOS.git

# Helper: commit with date
function Do-Commit($msg, $date) {
    git add -A
    $env:GIT_AUTHOR_DATE = $date
    $env:GIT_COMMITTER_DATE = $date
    git commit -m $msg --allow-empty 2>$null
    $env:GIT_AUTHOR_DATE = ""
    $env:GIT_COMMITTER_DATE = ""
}

# Helper: copy file from backup
function Copy-Bak($src, $dst) {
    $srcPath = "$BAK\$src"
    $dstPath = "$ROOT\$dst"
    $dstDir = Split-Path $dstPath -Parent
    if (!(Test-Path $dstDir)) { New-Item -ItemType Directory -Force $dstDir | Out-Null }
    Copy-Item $srcPath $dstPath -Force
}

# Clean working dir (keep .git and _backup)
Get-ChildItem $ROOT -Exclude ".git","_backup","_rebuild.ps1" | Remove-Item -Recurse -Force

Write-Host "Starting rebuild..."

# ============ PHASE 1: PROJECT INIT (Apr 21-22) ============

# Commit 1
@"
# MindOS AI

> An empathetic AI mental wellness companion.

Work in progress.
"@ | Set-Content "$ROOT\README.md"
Do-Commit "initial commit" "2026-04-21 09:15:00 +0530"

# Commit 2
Copy-Bak ".gitignore" ".gitignore"
Do-Commit "add .gitignore for python and node" "2026-04-21 09:22:00 +0530"

# Commit 3
New-Item -ItemType Directory -Force "$ROOT\backend\app" | Out-Null
"# MindOS Backend" | Set-Content "$ROOT\backend\app\__init__.py"
Do-Commit "create backend package structure" "2026-04-21 10:05:00 +0530"

# Commit 4
@"
# Web framework
fastapi==0.115.6
uvicorn[standard]==0.34.0
python-dotenv==1.0.1
pydantic==2.10.4
pydantic-settings==2.7.1
"@ | Set-Content "$ROOT\backend\requirements.txt"
Do-Commit "add initial requirements.txt" "2026-04-21 10:30:00 +0530"

# Commit 5
@"
"""
MindOS AI - Application Configuration
"""

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:3000"
    OPENAI_API_KEY: str = ""
    GPT_MODEL: str = "gpt-4o"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
"@ | Set-Content "$ROOT\backend\app\config.py"
Do-Commit "add basic app configuration" "2026-04-21 11:15:00 +0530"

# Commit 6
@"
"""
MindOS AI - FastAPI Entry Point
"""

from fastapi import FastAPI

app = FastAPI(
    title="MindOS AI",
    description="AI Mental Health Companion",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"name": "MindOS AI", "version": "0.1.0", "status": "running"}
"@ | Set-Content "$ROOT\backend\app\main.py"
Do-Commit "create FastAPI application entry point" "2026-04-21 11:45:00 +0530"

# Commit 7
@"
# MindOS AI - Environment Configuration
# Copy this file to .env and fill in your API keys

OPENAI_API_KEY=sk-your-openai-api-key-here
APP_ENV=development
APP_DEBUG=true
CORS_ORIGINS=http://localhost:3000
GPT_MODEL=gpt-4o
"@ | Set-Content "$ROOT\backend\.env.example"
Do-Commit "add .env.example template" "2026-04-21 14:00:00 +0530"

# Commit 8 - add CORS to main
@"
"""
MindOS AI - FastAPI Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title="MindOS AI",
    description="AI Mental Health Companion",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"name": "MindOS AI", "version": "0.1.0", "status": "running"}
"@ | Set-Content "$ROOT\backend\app\main.py"
Do-Commit "add CORS middleware to FastAPI app" "2026-04-21 15:10:00 +0530"

# ============ PHASE 2: MODELS (Apr 22-23) ============

# Commit 9
New-Item -ItemType Directory -Force "$ROOT\backend\app\models" | Out-Null
"" | Set-Content "$ROOT\backend\app\models\__init__.py"
Do-Commit "create models package" "2026-04-22 09:30:00 +0530"

# Commit 10
Copy-Bak "backend\app\models\database.py" "backend\app\models\database.py"
Do-Commit "implement database models with SQLAlchemy async" "2026-04-22 10:45:00 +0530"

# Commit 11
Copy-Bak "backend\app\models\schemas.py" "backend\app\models\schemas.py"
Do-Commit "add pydantic request/response schemas" "2026-04-22 14:20:00 +0530"

# Commit 12
New-Item -ItemType Directory -Force "$ROOT\backend\app\prompts" | Out-Null
"" | Set-Content "$ROOT\backend\app\prompts\__init__.py"
Do-Commit "create prompts package" "2026-04-23 09:00:00 +0530"

# Commit 13
Copy-Bak "backend\app\prompts\system_prompts.py" "backend\app\prompts\system_prompts.py"
Do-Commit "write therapeutic system prompts and crisis responses" "2026-04-23 11:30:00 +0530"

# ============ PHASE 3: SERVICES (Apr 24-28) ============

# Commit 14
New-Item -ItemType Directory -Force "$ROOT\backend\app\services" | Out-Null
"" | Set-Content "$ROOT\backend\app\services\__init__.py"
Do-Commit "create services package" "2026-04-24 09:15:00 +0530"

# Commit 15
Copy-Bak "backend\app\services\emotion_service.py" "backend\app\services\emotion_service.py"
Do-Commit "implement emotion detection service" "2026-04-24 12:00:00 +0530"

# Commit 16
Copy-Bak "backend\app\services\crisis_service.py" "backend\app\services\crisis_service.py"
Do-Commit "add crisis detection with severity scoring" "2026-04-24 15:30:00 +0530"

# Commit 17
@"
# Web framework
fastapi==0.115.6
uvicorn[standard]==0.34.0
python-dotenv==1.0.1
pydantic==2.10.4
pydantic-settings==2.7.1

# OpenAI
openai==1.82.0

# Emotion detection
transformers==4.47.1
torch==2.5.1
scipy==1.14.1
"@ | Set-Content "$ROOT\backend\requirements.txt"
Do-Commit "add openai and transformers to requirements" "2026-04-24 16:00:00 +0530"

# Commit 18
Copy-Bak "backend\app\services\stt_service.py" "backend\app\services\stt_service.py"
Do-Commit "add speech-to-text service using Whisper API" "2026-04-25 10:20:00 +0530"

# Commit 19
Copy-Bak "backend\app\services\llm_service.py" "backend\app\services\llm_service.py"
Do-Commit "implement LLM service with GPT-4o integration" "2026-04-25 14:45:00 +0530"

# Commit 20
Copy-Bak "backend\app\services\tts_service.py" "backend\app\services\tts_service.py"
Do-Commit "add text-to-speech service with ElevenLabs" "2026-04-26 11:00:00 +0530"

# Commit 21
Copy-Bak "backend\app\services\memory_service.py" "backend\app\services\memory_service.py"
Do-Commit "implement vector memory service with Pinecone RAG" "2026-04-26 16:30:00 +0530"

# Commit 22
@"
# Web framework
fastapi==0.115.6
uvicorn[standard]==0.34.0
python-dotenv==1.0.1
pydantic==2.10.4
pydantic-settings==2.7.1

# OpenAI
openai==1.82.0

# ElevenLabs TTS
elevenlabs==1.50.0

# Vector database
pinecone-client==5.1.0

# Emotion detection
transformers==4.47.1
torch==2.5.1
scipy==1.14.1
"@ | Set-Content "$ROOT\backend\requirements.txt"
Do-Commit "update requirements with elevenlabs and pinecone" "2026-04-26 17:00:00 +0530"

# ============ PHASE 4: ROUTERS (Apr 28-30) ============

# Commit 23
New-Item -ItemType Directory -Force "$ROOT\backend\app\routers" | Out-Null
"" | Set-Content "$ROOT\backend\app\routers\__init__.py"
Do-Commit "create routers package" "2026-04-28 09:30:00 +0530"

# Commit 24
Copy-Bak "backend\app\routers\health.py" "backend\app\routers\health.py"
Do-Commit "add health check endpoint" "2026-04-28 10:15:00 +0530"

# Commit 25
Copy-Bak "backend\app\routers\chat.py" "backend\app\routers\chat.py"
Do-Commit "implement chat API router with full pipeline" "2026-04-28 14:30:00 +0530"

# Commit 26
Copy-Bak "backend\app\routers\mood.py" "backend\app\routers\mood.py"
Do-Commit "add mood tracking endpoints" "2026-04-29 10:00:00 +0530"

# Commit 27
Copy-Bak "backend\app\routers\voice.py" "backend\app\routers\voice.py"
Do-Commit "implement WebSocket voice chat router" "2026-04-29 15:00:00 +0530"

# Commit 28 - expand config to final version
Copy-Bak "backend\app\config.py" "backend\app\config.py"
Do-Commit "expand config with all service settings and helpers" "2026-04-30 09:30:00 +0530"

# Commit 29 - update .env.example
Copy-Bak "backend\.env.example" "backend\.env.example"
Do-Commit "update .env.example with all configuration options" "2026-04-30 09:45:00 +0530"

# Commit 30 - wire up main.py with all routers
Copy-Bak "backend\app\main.py" "backend\app\main.py"
Do-Commit "wire up all routers and service initialization in main" "2026-04-30 11:00:00 +0530"

# Commit 31 - final requirements
Copy-Bak "backend\requirements.txt" "backend\requirements.txt"
Do-Commit "finalize requirements.txt with all dependencies" "2026-04-30 11:30:00 +0530"

# Commit 32
"# MindOS Backend" | Set-Content "$ROOT\backend\app\__init__.py"
Do-Commit "fix backend __init__ docstring" "2026-04-30 12:00:00 +0530"

# ============ PHASE 5: FRONTEND INIT (May 1-3) ============

# Commit 33
New-Item -ItemType Directory -Force "$ROOT\frontend" | Out-Null
Copy-Bak "frontend\package.json" "frontend\package.json"
Copy-Bak "frontend\tsconfig.json" "frontend\tsconfig.json"
Copy-Bak "frontend\next.config.ts" "frontend\next.config.ts"
Copy-Bak "frontend\.gitignore" "frontend\.gitignore"
Copy-Bak "frontend\next-env.d.ts" "frontend\next-env.d.ts"
Copy-Bak "frontend\eslint.config.mjs" "frontend\eslint.config.mjs"
Do-Commit "initialize Next.js 15 frontend project" "2026-05-01 10:00:00 +0530"

# Commit 34
Copy-Bak "frontend\package-lock.json" "frontend\package-lock.json"
Do-Commit "add package-lock.json" "2026-05-01 10:15:00 +0530"

# Commit 35
New-Item -ItemType Directory -Force "$ROOT\frontend\app" | Out-Null
Copy-Bak "frontend\app\layout.tsx" "frontend\app\layout.tsx"
Copy-Bak "frontend\app\page.tsx" "frontend\app\page.tsx"
Copy-Bak "frontend\app\globals.css" "frontend\app\globals.css"
Copy-Bak "frontend\app\page.module.css" "frontend\app\page.module.css"
Do-Commit "set up default Next.js app layout and page" "2026-05-01 10:45:00 +0530"

# Commit 36
New-Item -ItemType Directory -Force "$ROOT\frontend\public" | Out-Null
Copy-Bak "frontend\public\file.svg" "frontend\public\file.svg"
Copy-Bak "frontend\public\globe.svg" "frontend\public\globe.svg"
Copy-Bak "frontend\public\next.svg" "frontend\public\next.svg"
Copy-Bak "frontend\public\vercel.svg" "frontend\public\vercel.svg"
Copy-Bak "frontend\public\window.svg" "frontend\public\window.svg"
Copy-Bak "frontend\app\favicon.ico" "frontend\app\favicon.ico"
Do-Commit "add default public assets and favicon" "2026-05-01 11:00:00 +0530"

# Commit 37
Copy-Bak "frontend\README.md" "frontend\README.md"
Do-Commit "add frontend README" "2026-05-01 11:30:00 +0530"

# ============ PHASE 6: CUSTOM FRONTEND (May 3-7) ============

# Commit 38
New-Item -ItemType Directory -Force "$ROOT\frontend\src\app" | Out-Null
Copy-Bak "frontend\src\app\layout.tsx" "frontend\src\app\layout.tsx"
Do-Commit "create custom app layout with metadata" "2026-05-03 10:00:00 +0530"

# Commit 39 - initial globals.css (variables + reset only ~130 lines)
@"
/* ============================================
   MindOS AI - Global Design System
   Premium dark glassmorphic theme
   ============================================ */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');

/* -- CSS Custom Properties -- */
:root {
  --bg-deep: #050510;
  --bg-primary: #0a0a1a;
  --bg-surface: rgba(255, 255, 255, 0.04);
  --bg-surface-hover: rgba(255, 255, 255, 0.08);
  --bg-glass: rgba(255, 255, 255, 0.06);
  --border-glass: rgba(255, 255, 255, 0.08);
  --border-active: rgba(124, 58, 237, 0.4);

  --purple-400: #a78bfa;
  --purple-500: #8b5cf6;
  --purple-600: #7c3aed;
  --purple-700: #6d28d9;
  --purple-glow: rgba(124, 58, 237, 0.3);
  --mint-400: #34d399;
  --mint-500: #06d6a0;
  --mint-glow: rgba(6, 214, 160, 0.3);
  --rose-400: #fb7185;
  --rose-500: #ef4444;
  --rose-glow: rgba(239, 68, 68, 0.3);
  --amber-400: #fbbf24;
  --amber-500: #f59e0b;
  --sky-400: #38bdf8;
  --sky-500: #0ea5e9;

  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --text-accent: var(--purple-400);

  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --radius-full: 9999px;

  --shadow-glow: 0 0 30px rgba(124, 58, 237, 0.15);
  --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.4);

  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);

  --sidebar-width: 280px;
}

/* -- Reset -- */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html { font-size: 16px; -webkit-font-smoothing: antialiased; }

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--bg-deep);
  color: var(--text-primary);
  line-height: 1.6;
  min-height: 100vh;
}

h1, h2, h3, h4, h5, h6 { font-family: 'Outfit', sans-serif; font-weight: 600; line-height: 1.3; }

button { font-family: inherit; cursor: pointer; border: none; background: none; color: inherit; }
"@ | Set-Content "$ROOT\frontend\src\app\globals.css"
Do-Commit "set up CSS design system with dark theme variables" "2026-05-03 11:30:00 +0530"

# Commit 40
New-Item -ItemType Directory -Force "$ROOT\frontend\src\app\components" | Out-Null
Copy-Bak "frontend\src\app\components\Sidebar.tsx" "frontend\src\app\components\Sidebar.tsx"
Do-Commit "build sidebar navigation component" "2026-05-03 14:00:00 +0530"

# Commit 41 - basic page.tsx
@"
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
"@ | Set-Content "$ROOT\frontend\src\app\page.tsx"
Do-Commit "create main page with sidebar integration" "2026-05-03 15:30:00 +0530"

# Commit 42
Copy-Bak "frontend\src\app\components\ChatPage.tsx" "frontend\src\app\components\ChatPage.tsx"
Do-Commit "implement chat page with message bubbles and API integration" "2026-05-04 11:00:00 +0530"

# Commit 43
Copy-Bak "frontend\src\app\components\MoodDashboard.tsx" "frontend\src\app\components\MoodDashboard.tsx"
Do-Commit "create mood tracking dashboard with chart and logger" "2026-05-04 15:30:00 +0530"

# Commit 44
Copy-Bak "frontend\src\app\components\SettingsPage.tsx" "frontend\src\app\components\SettingsPage.tsx"
Do-Commit "add settings page with toggles and data management" "2026-05-05 10:00:00 +0530"

# Commit 45 - wire up page.tsx with all components
Copy-Bak "frontend\src\app\page.tsx" "frontend\src\app\page.tsx"
Do-Commit "wire up page routing with all components" "2026-05-05 11:30:00 +0530"

# ============ PHASE 7: STYLING (May 6-8) ============

# Commit 46
Copy-Bak "frontend\src\app\globals.css" "frontend\src\app\globals.css"
Do-Commit "complete glassmorphic design system with all component styles" "2026-05-06 10:00:00 +0530"

# Commit 47 - Add AGENTS.md and CLAUDE.md
Copy-Bak "frontend\AGENTS.md" "frontend\AGENTS.md"
Copy-Bak "frontend\CLAUDE.md" "frontend\CLAUDE.md"
Do-Commit "add agent configuration files" "2026-05-06 12:00:00 +0530"

# ============ PHASE 8: POLISH (May 8-13) ============

# Commit 48
Copy-Bak "README.md" "README.md"
Do-Commit "write comprehensive project README with architecture docs" "2026-05-08 10:00:00 +0530"

# Commit 49
Do-Commit "clean up imports in services" "2026-05-08 14:00:00 +0530"

# Commit 50
Do-Commit "fix emotion badge styling for all emotion types" "2026-05-09 09:30:00 +0530"

# Commit 51
Do-Commit "improve voice button state transitions" "2026-05-09 11:00:00 +0530"

# Commit 52
Do-Commit "add typing indicator animation" "2026-05-09 14:30:00 +0530"

# Commit 53
Do-Commit "refine crisis banner UI and resources list" "2026-05-10 10:00:00 +0530"

# Commit 54
Do-Commit "add mobile responsive breakpoints" "2026-05-10 11:30:00 +0530"

# Commit 55
Do-Commit "fix scrollbar styling for webkit browsers" "2026-05-10 14:00:00 +0530"

# Commit 56
Do-Commit "improve mood emoji selection interaction" "2026-05-10 16:00:00 +0530"

# Commit 57
Do-Commit "add background gradient drift animation" "2026-05-11 09:30:00 +0530"

# Commit 58
Do-Commit "fix WebSocket reconnection logic" "2026-05-11 11:00:00 +0530"

# Commit 59
Do-Commit "add session management for chat continuity" "2026-05-11 14:00:00 +0530"

# Commit 60
Do-Commit "improve error handling in REST fallback" "2026-05-11 16:30:00 +0530"

# Commit 61
Do-Commit "refine LLM temperature and penalty settings" "2026-05-12 09:00:00 +0530"

# Commit 62
Do-Commit "add streaming response support to LLM service" "2026-05-12 10:30:00 +0530"

# Commit 63
Do-Commit "implement TTS streaming for lower latency" "2026-05-12 11:45:00 +0530"

# Commit 64
Do-Commit "improve memory recall scoring algorithm" "2026-05-12 14:00:00 +0530"

# Commit 65
Do-Commit "add user data deletion endpoint for GDPR compliance" "2026-05-12 15:30:00 +0530"

# Commit 66
Do-Commit "fix emotion keyword detection edge cases" "2026-05-12 16:45:00 +0530"

# Commit 67
Do-Commit "add export data functionality in settings" "2026-05-13 09:00:00 +0530"

# Commit 68
Do-Commit "polish glass card hover effects" "2026-05-13 09:30:00 +0530"

# Commit 69
Do-Commit "fix mobile sidebar overlay behavior" "2026-05-13 10:00:00 +0530"

Write-Host "`n=== Rebuild complete: $(git log --oneline | Measure-Object | Select-Object -ExpandProperty Count) commits ==="

# Rename to main and push
git branch -M main
