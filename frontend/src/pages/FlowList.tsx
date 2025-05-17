import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

export default function FlowList() {
  const [flows, setFlows] = useState<any[]>([]);
  const navigate = useNavigate();

  const fetchFlows = async () => {
    const res = await axios.get('http://localhost:5000/get_flows');
    setFlows(res.data.flows);
  };

  const handleNew = () => {
    const newId = uuidv4();
    navigate(`/flow/${newId}`);
  };

  useEffect(() => {
    fetchFlows();
  }, []);

  return (
    <div className="p-4">
      <button onClick={handleNew}>➕ 新建流程</button>
      <ul>
        {flows.map(flow => (
          <li key={flow.id}>
            {flow.id} - {flow.nodeCount} nodes
            <button onClick={() => navigate(`/flow/${flow.id}`)}>编辑</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
