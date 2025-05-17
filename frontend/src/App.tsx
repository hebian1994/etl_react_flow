import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import FlowList from './pages/FlowList';
import FlowDesign from './pages/FlowDesign';
import Layout from './pages/Layout';
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<FlowList />} />
        {/* <Route path="/" element={<Layout />} /> */}
        <Route path="/flow/:flowId" element={<Layout />} />
      </Routes>
    </Router>
  );
}

export default App;
