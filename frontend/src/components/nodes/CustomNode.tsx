import React from 'react';
import { Handle, Position } from 'reactflow';
import { BookOpen, Eye, Filter, GitMerge, Sigma } from 'lucide-react'; // 图标库，可换其他

const getIcon = (type: string) => {
    switch (type) {
        case 'File Input':
            return <BookOpen className="text-blue-500" />;
        case 'Filter':
            return <Filter className="text-green-500" />;
        case 'Left Join':
            return <GitMerge className="text-purple-500" />;
        case 'Data Viewer':
            return <Eye className="text-red-500" />;
        case 'Aggregate':
            return <Sigma className="text-yellow-600" />;
        default:
            return <span>🔧</span>;
    }
};

export const CustomNode = ({ data }: any) => {
    return (
        <div
            style={{
                padding: 10,
                border: '2px solid #777',
                borderRadius: 8,
                backgroundColor: '#fff',
                boxShadow: '2px 2px 10px rgba(0,0,0,0.1)',
                minWidth: 120,

                display: 'flex',
                alignItems: 'center', // 垂直居中
                gap: 8,               // 图标和文字之间的间距
            }}
        >
            {getIcon(data.type)}
            <span style={{ fontWeight: 500 }}>{data.type}</span>

            <Handle type="source" position={Position.Right} />
            <Handle type="target" position={Position.Left} />
        </div>
    );
};

