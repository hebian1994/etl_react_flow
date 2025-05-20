import React from 'react';
import {
    getBezierPath,
    EdgeProps,
} from 'reactflow';

const CustomEdge = ({
    id,
    sourceX,
    sourceY,
    targetX,
    targetY,
    selected,
    markerEnd,
    style,
    data,
}: EdgeProps) => {
    const [edgePath, labelX, labelY] = getBezierPath({
        sourceX,
        sourceY,
        targetX,
        targetY,
    });

    return (
        <>
            <path
                id={id}
                style={style}
                className="react-flow__edge-path"
                d={edgePath}
                markerEnd={markerEnd}
            />
            {data?.showDelete && (
                <foreignObject
                    x={labelX - 20}
                    y={labelY - 10}
                    width={100}
                    height={40}
                >
                    <div
                        style={{
                            background: 'white',
                            border: '1px solid #ccc',
                            borderRadius: 4,
                            padding: '2px 4px',
                            display: 'flex',
                            gap: 4,
                        }}
                    >
                        <button
                            style={{ fontSize: 12 }}
                            onClick={() => data.onDelete?.(id)}
                        >
                            删除
                        </button>
                        <button
                            style={{ fontSize: 12 }}
                            onClick={() => data.onCancel?.()}
                        >
                            取消
                        </button>
                    </div>
                </foreignObject>
            )}
        </>
    );
};

export default CustomEdge;
