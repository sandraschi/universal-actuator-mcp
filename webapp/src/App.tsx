import {
  Navigate,
  Route,
  BrowserRouter as Router,
  Routes,
} from "react-router-dom";
import { AppLayout } from "@/components/layout/app-layout";
import { About } from "@/pages/about";
import { AppsHub } from "@/pages/apps";
import { Chat } from "@/pages/chat";
import { Control } from "@/pages/control";
import { Dashboard } from "@/pages/dashboard";
import { Help } from "@/pages/help";
import MediaLibrary from "@/pages/library";
import { LocalLLM } from "@/pages/llm";
import Logs from "@/pages/logs";
import { Settings } from "@/pages/settings";
import { Status } from "@/pages/status";
import { ToolsPage } from "@/pages/tools";
import { Visualizer } from "@/pages/visualizer";

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/control" element={<Control />} />
          <Route path="/visualizer" element={<Visualizer />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/tools" element={<ToolsPage />} />
          <Route path="/apps" element={<AppsHub />} />
          <Route path="/llm" element={<LocalLLM />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/library" element={<MediaLibrary />} />
          <Route path="/help" element={<Help />} />
          <Route path="/logs" element={<Logs />} />
          <Route path="/status" element={<Status />} />
          <Route path="/about" element={<About />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;
