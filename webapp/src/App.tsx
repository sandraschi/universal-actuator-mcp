import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '@/components/layout/app-layout';
import { Dashboard } from '@/pages/dashboard';
import { Control } from '@/pages/control';
import { Visualizer } from '@/pages/visualizer';
import { Chat } from '@/pages/chat';
import { Settings } from '@/pages/settings';
import { AppsHub } from '@/pages/apps';
import { ToolsPage } from '@/pages/tools';
import { LocalLLM } from '@/pages/llm';
import { Help } from '@/pages/help';
import { About } from '@/pages/about';
import MediaLibrary from '@/pages/library';
import { Status } from '@/pages/status';

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
          <Route path="/status" element={<Status />} />
          <Route path="/about" element={<About />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;
