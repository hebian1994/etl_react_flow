import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import FlowList from './pages/FlowList';
import Designer from './pages/Designer/Designer';
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<FlowList />} />
        <Route path="/flow/:flowId" element={<Designer />} />
      </Routes>
    </Router>
  );
}

export default App;
