import React from 'react';
import {
    Box,
    Typography,
    TextField,
    Button,
    IconButton,
    Stack,
    Paper,
    Divider,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

interface Props {
    selectedNode: { data: { label: string } } | null;
    configForm: Record<string, string>;
    newKey: string;
    newValue: string;
    setSelectedNode: (node: null) => void;
    setShowBox2: (show: boolean) => void;
    handleConfigChange: (key: string, value: string) => void;
    setConfigForm: React.Dispatch<React.SetStateAction<Record<string, string>>>;
    setNewKey: React.Dispatch<React.SetStateAction<string>>;
    setNewValue: React.Dispatch<React.SetStateAction<string>>;
    handleSaveConfig: () => void;
}

const NodeConfigDrawer: React.FC<Props> = ({
    selectedNode,
    configForm,
    newKey,
    newValue,
    setSelectedNode,
    setShowBox2,
    handleConfigChange,
    setConfigForm,
    setNewKey,
    setNewValue,
    handleSaveConfig,
}) => {
    return (
        <Paper
            elevation={3}
            sx={{
                p: 3,
                borderRadius: 3,
                width: '100%',
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                boxSizing: 'border-box',
                overflow: 'hidden', // 防止撑出外层容器
            }}
        >
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6">
                    节点配置：{selectedNode?.data.label}
                </Typography>
                <IconButton
                    aria-label="关闭配置栏"
                    onClick={() => {
                        setSelectedNode(null);
                        setShowBox2(false);
                    }}
                >
                    <CloseIcon />
                </IconButton>
            </Box>

            <Divider sx={{ my: 2 }} />

            {/* 配置项列表 - 可滚动区域 */}
            <Box
                sx={{
                    flex: 1,
                    overflowY: 'auto',
                    pr: 1,
                }}
            >
                <Stack spacing={2}>
                    {Object.entries(configForm).map(([key, value]) => (
                        <Box
                            key={key}
                            sx={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 1,
                                flexWrap: 'wrap',
                            }}
                        >
                            {/* 显示配置名 */}
                            <Typography
                                variant="body2"
                                sx={{ width: 140, fontWeight: 500, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}
                                title={key}
                            >
                                {key}
                            </Typography>

                            {/* 值输入框 */}
                            <TextField
                                variant="outlined"
                                size="small"
                                value={value}
                                onChange={(e) => handleConfigChange(key, e.target.value)}
                                fullWidth
                            />

                            {/* 删除按钮 */}
                            <Button
                                color="error"
                                variant="outlined"
                                size="small"
                                onClick={() => {
                                    const { [key]: _, ...rest } = configForm;
                                    setConfigForm(rest);
                                }}
                            >
                                删除
                            </Button>
                        </Box>

                    ))}
                </Stack>
            </Box>

            {/* 添加新配置 */}
            <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                <TextField
                    label="新配置名"
                    variant="outlined"
                    size="small"
                    value={newKey}
                    onChange={(e) => setNewKey(e.target.value)}
                    sx={{ width: 160 }}
                />
                <TextField
                    label="新值"
                    variant="outlined"
                    size="small"
                    value={newValue}
                    onChange={(e) => setNewValue(e.target.value)}
                    fullWidth
                />
                <Button
                    variant="contained"
                    color="success"
                    onClick={() => {
                        if (newKey.trim()) {
                            setConfigForm((prev) => ({ ...prev, [newKey]: newValue }));
                            setNewKey('');
                            setNewValue('');
                        }
                    }}
                >
                    添加
                </Button>
            </Box>

            {/* 保存按钮 */}
            <Box sx={{ mt: 2 }}>
                <Button
                    variant="contained"
                    color="primary"
                    fullWidth
                    onClick={handleSaveConfig}
                >
                    保存配置
                </Button>
            </Box>
        </Paper>
    );
};

export default NodeConfigDrawer;
