# Universal Actuator Dashboard (SOTA 2026)

> **High-fidelity React 19 monitoring and control interface for the RoboFang fleet.**

This is the official web interface for the **Universal Actuator MCP Hub**. It provides a real-time, glassmorphism-inspired dashboard for monitoring and interacting with a federated grid of 15+ MCP nodes.

## 🛠 Tech Stack

- **Framework**: [React 19](https://react.dev/)
- **Build Tool**: [Vite 6](https://vitejs.dev/)
- **Styling**: [Tailwind CSS 3.4](https://tailwindcss.com/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **Animation**: [Framer Motion](https://www.framer.com/motion/)
- **Components**: Radix UI + Custom Glassmorphism patterns

## 🚀 Key Features

- **Live Telemetry**: Real-time CPU, Memory, and Uptime streaming from the host RTX 4090.
- **Status 2.0**: High-fidelity federation health dashboard with real-time node status and glassmorphism cards.
- **Semantic RAG Search**: Consolidated media search across Plex, Calibre, and Immich using LanceDB vector indexing.
- **Agentic Workflows**: Integrated [SEP-1577] mission orchestration for autonomous fleet operations.
- **GrokTools**: In-browser MCP tool explorer with dynamic schema analysis.
- **Fleet Launcher**: One-click execution of registered applications via detached processes.

## 📂 Project Structure

```text
webapp/
├── src/
│   ├── components/       # Atomic UI components and Layouts
│   ├── pages/            # View-level page components (Status, Library, etc.)
│   ├── common/           # Shared utilities and hooks
│   ├── App.tsx           # Main routing and navigation provider
│   └── index.css         # Global design system and Tailwind tailing
├── public/               # Static assets and federation iconography
└── start.ps1             # Local development orchestration script
```

## 🎨 Design System (Zero Runts)

The dashboard follows the **SOTA 2026 Semantic Design Blueprint**:
- **Dark Mode Default**: Slate-950 base with 50% opacity overlays.
- **Glassmorphism**: Extensive use of `backdrop-blur-md` and `bg-white/5`.
- **Micro-animations**: Subtle hover transitions and pulse indicators for "online" nodes.
- **Typography**: Inter (System Default) for high-density information display.

## 🏁 Getting Started

### Development
```powershell
npm install
npm run dev
```

### Production Build
```powershell
npm run build
```

---

*Part of the RoboFang Sovereign Infrastructure.*
*Built with Materialist Logic & Reductionist Precision.*
