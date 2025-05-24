import React, { useState } from 'react';
import {
    Box,
    IconButton,
    Paper,
    Stack,
    Tooltip,
    Divider
} from '@mui/material';
import { Folder, Shuffle, UploadCloud, BookOpen, Eye, Filter, GitMerge, Sigma, FolderDown } from 'lucide-react';

const groupedNodeTypes: Record<string, string[]> = {
    "所有": ["File Input", "Filter", "Aggregate", "Left Join", "Data Viewer"],
    "输入类": ["File Input"],
    "转换类": ["Filter", "Aggregate", "Left Join"],
    "输出类": ["Data Viewer"],
};

const categoryIcons: Record<string, React.ReactNode> = {
    "所有": <Folder size={18} />,
    "输入类": <UploadCloud size={18} />,
    "转换类": <Shuffle size={18} />,
    "输出类": <FolderDown size={18} />,
};

const getIcon = (type: string) => {
    switch (type) {
        case 'File Input':
            return <BookOpen className="text-blue-500" size={16} />;
        case 'Filter':
            return <Filter className="text-green-500" size={16} />;
        case 'Left Join':
            return <GitMerge className="text-purple-500" size={16} />;
        case 'Data Viewer':
            return <Eye className="text-red-500" size={16} />;
        case 'Aggregate':
            return <Sigma className="text-yellow-600" size={16} />;
        default:
            return <span>🔧</span>;
    }
};

const NodeTypeSelector = () => {
    const [selectedTab, setSelectedTab] = useState('输入类');

    return (
        <>
            <Divider sx={{ my: 0.5 }} />
            <Stack direction="row" alignItems="center" sx={{ px: 1, gap: 0.5, minHeight: 36 }}>
                {Object.keys(groupedNodeTypes).map((category) => (
                    <Tooltip key={category} title={category} arrow>
                        <IconButton
                            onClick={() => setSelectedTab(category)}
                            color={selectedTab === category ? 'primary' : 'default'}
                            size="small"
                            sx={{
                                border: selectedTab === category ? '1px solid' : 'none',
                                borderColor: 'primary.main',
                                bgcolor: selectedTab === category ? 'primary.light' : 'transparent',
                                '&:hover': { bgcolor: 'grey.100' },
                                p: 0.5,
                            }}
                        >
                            {categoryIcons[category]}
                        </IconButton>
                    </Tooltip>
                ))}
            </Stack>

            <Box
                sx={{
                    display: 'flex',
                    gap: 0.5,
                    overflowX: 'auto',
                    px: 1,
                    py: 0.5,
                    minHeight: 42,
                    '&::-webkit-scrollbar': { height: '4px' },
                    '&::-webkit-scrollbar-thumb': { backgroundColor: '#bbb', borderRadius: '2px' },
                }}
            >
                {(groupedNodeTypes[selectedTab] || []).map((type) => (
                    <Tooltip key={type} title={`拖拽添加 ${type}`} arrow>
                        <Paper
                            draggable
                            onDragStart={(e) => e.dataTransfer.setData('application/reactflow', type)}
                            sx={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 0.5,
                                px: 1,
                                py: 0.5,
                                fontSize: '0.75rem',
                                bgcolor: 'background.paper',
                                border: '1px solid',
                                borderColor: 'divider',
                                borderRadius: 1,
                                cursor: 'grab',
                                userSelect: 'none',
                                whiteSpace: 'nowrap',
                                minWidth: 80,
                                '&:hover': {
                                    bgcolor: 'grey.100',
                                },
                            }}
                        >
                            {getIcon(type)}
                            <span>{type}</span>
                        </Paper>
                    </Tooltip>
                ))}
            </Box>
        </>
    );
};

export default NodeTypeSelector;
