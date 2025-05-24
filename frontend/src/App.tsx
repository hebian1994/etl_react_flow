import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import FlowList from './pages/dashboard/FlowList';
import Designer from './pages/Designer/Designer';
import History from './pages/history/History';
// import Components from './pages/components/Components';
import { Navbar } from './components/dashboard/Navbar';
import { Box } from '@mui/material';

function AppContent() {
  const location = useLocation();
  const isDesignerPage = location.pathname.startsWith('/flow/');

  return (
    <Box display="flex" flexDirection="column" height="100vh">
      {!isDesignerPage && <Navbar />}
      <Box flex={1}>
        <Routes>
          <Route path="/" element={<FlowList />} />
          <Route path="/history" element={<History />} />
          {/* <Route path="/components" element={<Components />} /> */}
          <Route path="/flow/:flowId" element={<Designer />} />
        </Routes>
      </Box>
    </Box>
  );
}

export default function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}
