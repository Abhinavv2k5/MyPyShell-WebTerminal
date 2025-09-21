# MyPyShell - AI-Powered Web Terminal

MyPyShell is an interactive web-based terminal designed to replicate the experience of a real Linux terminal with an **AI-powered natural language interface**. It allows users to execute standard terminal commands, manage files and directories, and leverage AI to translate natural language instructions into actionable commands.

## 🌟 Features

- **Standard Terminal Commands**:
  - `ls` → List files and directories
  - `pwd` → Show current directory
  - `cd <dir>` → Change directory
  - `mkdir <dir>` → Create one or multiple directories
  - `touch <file>` → Create one or multiple files
  - `rm <target>` → Delete files or folders (supports multiple targets)
  - `move <file> <folder>` → Move one or multiple files/folders
  - `cat <file>` → Display file content
  - `cpu` → Show current CPU usage
  - `mem` → Show current memory usage
  - `ps` → List active processes

- **AI Mode**:
  - Translate natural language instructions into terminal commands
  - Handles multiple commands in a single sentence
  - Supports pronouns like `it` or `them` for recently created files/folders
  - Animated “AI thinking” indicator for a futuristic terminal feel

- **Multiple File/Folder Operations**:
  - Create multiple files/folders at once
  - Delete or move multiple items in a single command

- **Sandbox Security**:
  - Users cannot access files outside the sandbox directory
  - Safe path enforcement prevents accidental deletion or movement of system files

- **Terminal-Like UI**:
  - Realistic terminal appearance with color-coded output
  - Blinking cursor for authentic feel
  - Animated AI status for AI-powered commands

## 💻 Tech Stack

- Backend: Python 3, Flask, psutil
- Frontend: HTML, CSS, JavaScript
- AI: Rule-based NLP + HuggingFace API integration
- Hosting: Any Python-compatible hosting service (Render, Railway, etc.)

## 🚀 Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/<repo-name>.git
   cd <repo-name>
