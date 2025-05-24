import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Typography,
  Stack
} from '@mui/material';
import Grid from '@mui/material/Grid'; // ✅ 正确

import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import { DeleteIcon } from 'lucide-react';

export default function FlowList() {
  const [flows, setFlows] = useState<any[]>([]);
  const navigate = useNavigate();

  const fetchFlows = async () => {
    const res = await axios.get('http://localhost:5000/get_flows');
    setFlows(res.data.flows || []);
  };

  const handleNew = () => {
    const newId = uuidv4();
    navigate(`/flow/${newId}`);
  };

  const handleDelete = async (id: string) => {
    const res = await axios.post(`http://localhost:5000/delete_flow`, {
      flow_id: id
    });
    if (res.status === 200) {
      fetchFlows();
    }
  };

  useEffect(() => {
    fetchFlows();
  }, []);

  return (
    <Box p={4}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h5">流程列表</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleNew}>
          新建流程
        </Button>
      </Stack>

      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)', // 三列布局，列宽完全一致
          gap: 3,
        }}
      >
        {flows.map((flow) => (
          <Card
            key={flow.id}
            sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}
          >
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {flow.flowName || `流程 ${flow.id}`}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                节点数量: {flow.nodeCount}
              </Typography>
            </CardContent>
            <CardActions sx={{ mt: 'auto', justifyContent: 'flex-end' }}>
              <Button
                size="small"
                startIcon={<EditIcon />}
                onClick={() => navigate(`/flow/${flow.id}`)}
              >
                编辑
              </Button>
              <Button
                size="small"
                startIcon={<DeleteIcon />}
                onClick={() => handleDelete(flow.id)}
              >
                删除
              </Button>
            </CardActions>
          </Card>
        ))}
      </Box>

    </Box>
  );
}
