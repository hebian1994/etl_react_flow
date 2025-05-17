import React, { useEffect, useState } from 'react';
import axios from 'axios';

const DataViewerModal = ({
    node,
    nodes,
    onClose,
}: {
    node: any;
    nodes: any[];
    onClose: () => void;
}) => {
    const [data, setData] = useState<any[]>([]);

    useEffect(() => {
        const upstream = nodes.find((n) => n.id !== node.id && n.data.type === 'File Input');
        if (upstream && upstream.data.config?.path) {
            axios
                .post('http://localhost:5000/preview_data', {
                    path: upstream.data.config.path,
                })
                .then((res) => setData(res.data))
                .catch(() => alert('读取数据失败'));
        }
    }, [node, nodes]);

    return (
        <div className="modal">
            <h3>数据预览</h3>
            <pre>{JSON.stringify(data, null, 2)}</pre>
            <button onClick={onClose}>关闭</button>
        </div>
    );
};

export default DataViewerModal;
