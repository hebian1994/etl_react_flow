import React, { useState } from 'react';

const FileInputModal = ({
    node,
    onSave,
    onClose,
}: {
    node: any;
    onSave: (config: any) => void;
    onClose: () => void;
}) => {
    const [path, setPath] = useState(node.data.config?.path || '');

    const handleSubmit = () => {
        onSave({ path });
    };

    return (
        <div className="modal">
            <h3>配置 File Input 节点</h3>
            <input
                type="text"
                value={path}
                onChange={(e) => setPath(e.target.value)}
                placeholder="文件路径，例如：data.csv"
            />
            <div className="modal-actions">
                <button onClick={handleSubmit}>保存</button>
                <button onClick={onClose}>取消</button>
            </div>
        </div>
    );
};

export default FileInputModal;
