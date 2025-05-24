import React, { useState } from 'react';
import {
    Stack,
    Button,
    Tooltip,
    Typography,
    TextField
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import HomeIcon from '@mui/icons-material/Home';
import { useNavigate } from 'react-router-dom';

const FlowToolbarControls = ({
    flowName,
    setFlowName,
    setShowBox2,
    setShowBox4,
    handleSave,
}: {
    flowName: string;
    setFlowName: React.Dispatch<React.SetStateAction<string>>;
    setShowBox2: React.Dispatch<React.SetStateAction<boolean>>;
    setShowBox4: React.Dispatch<React.SetStateAction<boolean>>;
    handleSave: () => void;
}) => {
    const navigate = useNavigate();
    const [isEditing, setIsEditing] = useState(false);
    const [tempName, setTempName] = useState(flowName || '');

    const handleNameClick = () => setIsEditing(true);
    const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => setTempName(e.target.value);
    const handleNameBlur = () => {
        setIsEditing(false);
        setFlowName(tempName.trim());
    };
    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') handleNameBlur();
    };

    return (
        <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Stack direction="row" spacing={2} alignItems="center">
                <Tooltip title="返回首页" arrow>
                    <Button variant="outlined" startIcon={<HomeIcon />} onClick={() => navigate('/')}>
                        回到首页
                    </Button>
                </Tooltip>

                {isEditing ? (
                    <TextField
                        variant="standard"
                        value={tempName}
                        onChange={handleNameChange}
                        onBlur={handleNameBlur}
                        onKeyDown={handleKeyDown}
                        autoFocus
                        placeholder="请输入流程名称"
                        sx={{ minWidth: 200 }}
                    />
                ) : (
                    <Stack direction="row" alignItems="center" spacing={0.5} sx={{ cursor: 'pointer' }} onClick={handleNameClick}>
                        <Typography
                            variant="h6"
                            sx={{
                                color: flowName ? 'text.primary' : 'text.disabled',
                                fontStyle: flowName ? 'normal' : 'italic',
                            }}
                        >
                            {flowName || '未命名流程'}
                        </Typography>
                        <Tooltip title="编辑流程名">
                            <EditIcon fontSize="small" color="action" />
                        </Tooltip>
                    </Stack>
                )}
            </Stack>

            <Stack direction="row" spacing={1}>
                <Button variant="outlined" onClick={() => setShowBox2((prev) => !prev)}>
                    切换左侧框
                </Button>
                <Button variant="outlined" onClick={() => setShowBox4((prev) => !prev)}>
                    切换底部框
                </Button>
                <Tooltip title="保存 Flow" arrow>
                    <Button variant="contained" color="primary" onClick={handleSave}>
                        💾 保存
                    </Button>
                </Tooltip>
            </Stack>
        </Stack>
    );
};

export default FlowToolbarControls;
