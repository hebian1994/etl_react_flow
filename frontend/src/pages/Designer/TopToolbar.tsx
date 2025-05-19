import React from 'react';
import { AppBar, Toolbar, Button, Paper, Stack, Tooltip } from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import { useNavigate } from 'react-router-dom';

const TopToolbar = ({
    nodeTypes,
    setShowBox2,
    setShowBox4,
    handleSave
}: {
    nodeTypes: string[];
    setShowBox2: React.Dispatch<React.SetStateAction<boolean>>;
    setShowBox4: React.Dispatch<React.SetStateAction<boolean>>;
    handleSave: () => void;
}) => {
    const navigate = useNavigate();

    return (
        <AppBar position="static" color="default" elevation={1} sx={{ zIndex: 10 }}>
            <Toolbar variant="dense" sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Stack direction="row" spacing={1}>
                    <Tooltip title="返回首页" arrow>
                        <Button
                            variant="outlined"
                            startIcon={<HomeIcon />}
                            onClick={() => navigate('/')}
                        >
                            首页
                        </Button>
                    </Tooltip>
                    <Button variant="outlined" onClick={() => setShowBox2(prev => !prev)}>切换左侧框</Button>
                    <Button variant="outlined" onClick={() => setShowBox4(prev => !prev)}>切换底部框</Button>
                    <Tooltip title="保存 Flow" arrow>
                        <Button variant="contained" color="primary" onClick={handleSave}>💾 保存</Button>
                    </Tooltip>
                </Stack>

                <Stack direction="row" spacing={1} sx={{ overflowX: 'auto', ml: 4 }}>
                    {nodeTypes.map((type) => (
                        <Tooltip key={type} title={`拖拽添加 ${type}`} arrow>
                            <Paper
                                draggable
                                onDragStart={(e) => e.dataTransfer.setData('application/reactflow', type)}
                                sx={{
                                    px: 2,
                                    py: 1,
                                    bgcolor: 'background.paper',
                                    border: '1px solid',
                                    borderColor: 'divider',
                                    borderRadius: 1,
                                    cursor: 'grab',
                                    userSelect: 'none',
                                    whiteSpace: 'nowrap',
                                    '&:hover': {
                                        bgcolor: 'grey.100'
                                    }
                                }}
                            >
                                {type}
                            </Paper>
                        </Tooltip>
                    ))}
                </Stack>
            </Toolbar>
        </AppBar>
    );
};

export default TopToolbar;
