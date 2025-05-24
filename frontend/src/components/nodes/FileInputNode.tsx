import React from 'react';
import { Handle, Position } from 'reactflow';
import { Card, CardContent, Typography, Box } from '@mui/material';
import MenuBookIcon from '@mui/icons-material/MenuBook'; // 书本图标

const FileInputNode = ({ data }: any) => {
    return (
        <Card
            variant="outlined"
            sx={{
                minWidth: 160,
                borderRadius: 2,
                borderColor: '#1565C0',
                backgroundColor: '#E3F2FD',
                boxShadow: 3,
                position: 'relative',
            }}
        >
            <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <MenuBookIcon sx={{ color: '#1565C0' }} />
                <Typography variant="subtitle1" fontWeight="bold">
                    {data.label}
                </Typography>
            </CardContent>

            {/* React Flow Handles */}
            <Handle type="target" position={Position.Left} style={{ background: '#1565C0' }} />
            <Handle type="source" position={Position.Right} style={{ background: '#1565C0' }} />
        </Card>
    );
};

export default FileInputNode;
