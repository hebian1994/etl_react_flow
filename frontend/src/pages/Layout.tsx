import React, { useCallback, useEffect, useRef, useState } from 'react';
import './Layout.css';
import FlowDesign from './FlowDesign';
import ReactFlow, {
    addEdge,
    Background,
    Connection,
    Controls,
    Edge,
    MarkerType,
    MiniMap,
    Node,
    ReactFlowInstance,
    useEdgesState,
    useNodesState,
    useReactFlow,
} from 'reactflow';
import 'reactflow/dist/style.css';
import 'reactflow/dist/style.css';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import { v4 as uuidv4 } from 'uuid';
import PreviewBox4 from './PreviewBox4';


const nodeTypes = ['File Input', 'Data Viewer', 'Filter', 'Aggregate', 'Left Join'];
const initialNodes = [
    {
        id: '1',
        data: { label: '节点 1' },
        position: { x: 50, y: 50 },
    },
];
const initialEdges: any[] = [];

const Layout: React.FC = () => {
    const [showBox2, setShowBox2] = useState<boolean>(true);
    const [showBox4, setShowBox4] = useState<boolean>(true);
    const reactFlowWrapper = useRef(null);
    const { flowId } = useParams<{ flowId: string }>();
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [rfInstance, setRfInstance] = useState<ReactFlowInstance | null>(null);
    const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, nodeId: '' });
    const [selectedNode, setSelectedNode] = useState<Node | null>(null);
    const [modalType, setModalType] = useState<'file' | 'viewer' | null>(null);
    const [configForm, setConfigForm] = useState<Record<string, any>>({});
    const [previewData, setPreviewData] = useState<any[] | null>(null);
    const [newKey, setNewKey] = useState('');
    const [newValue, setNewValue] = useState('');



    // 加载流程初始数据
    useEffect(() => {
        const fetchFlow = async () => {
            const res = await axios.get(`http://localhost:5000/get_flow/${flowId}`);
            if (res.data.nodes) setNodes(res.data.nodes);
            if (res.data.edges) setEdges(res.data.edges);
        };
        fetchFlow();
    }, [flowId]);


    const onNodeDoubleClick = useCallback(async (_: any, node: Node) => {
        console.log('node', node);
        console.log('node', node.data.label);
        const payload = {
            flow_id: flowId,
            node_id: node.id,
        };

        setSelectedNode(node);



        // should send request to get config @app.route('/get_node_config', methods=['POST'])
        const node_config = await axios.post('http://localhost:5000/get_node_config', payload);
        console.log("node_config", node_config.data);
        setConfigForm(node_config.data || {});
        setShowBox2(true);


        // 如果有 dataPreview 数据，展示底部面板
        const res = await axios.post('http://localhost:5000/preview_data', payload);
        console.log(res.data);

        if (res.data.length > 0) {
            setPreviewData(res.data);
        } else {
            setPreviewData([]);
        }
    }, []);



    const handleConfigChange = (key: string, value: any) => {
        setConfigForm(prev => ({ ...prev, [key]: value }));
    };

    const handleSaveConfig = async () => {
        if (!selectedNode) return;

        const save_config_payload = {
            flow_id: flowId,
            node_id: selectedNode.id,
            config: configForm,
        };

        console.log("save_config_payload", save_config_payload);

        try {
            await axios.post('http://localhost:5000/save_config', save_config_payload);
            alert('配置保存成功');

            // 同时更新本地节点数据
            setSelectedNode(prev => {
                if (!prev) return null;
                return {
                    ...prev,
                    data: {
                        ...prev.data,
                        config: configForm,
                    }
                };
            });

        } catch (err) {
            console.error(err);
            alert('保存失败');
        }
    };


    // 拖拽处理
    const onDrop = useCallback(
        async (event: React.DragEvent) => {
            event.preventDefault();
            const type = event.dataTransfer.getData('application/reactflow');
            const bounds = (reactFlowWrapper.current as any).getBoundingClientRect();

            const position = {
                x: event.clientX - bounds.left,
                y: event.clientY - bounds.top,
            };

            const id = uuidv4();
            const newNode: Node = {
                id,
                type: 'default',
                position,
                data: { label: type, type, config: {} },
            };

            setNodes((nds) => [...nds, newNode]);

            // 通知后端新节点
            await axios.post('http://localhost:5000/save_node', {
                flow_id: flowId,
                id,
                type,
                created_at: new Date().toISOString(),
            });
        },
        [flowId]
    );

    const onDragOver = useCallback((event: React.DragEvent) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }, []);

    // 连线
    const onConnect = useCallback(
        async (params: Edge | Connection) => {
            setEdges((eds) => addEdge(params, eds));
            await axios.post('http://localhost:5000/add_dependency', {
                flow_id: flowId,
                source: params.source,
                target: params.target,
            });
        },
        [flowId]
    );

    // 删除节点
    const deleteNode = async () => {
        if (!contextMenu.nodeId) return;

        setNodes((nds) => nds.filter((n) => n.id !== contextMenu.nodeId));
        setEdges((eds) => eds.filter((e) => e.source !== contextMenu.nodeId && e.target !== contextMenu.nodeId));

        await axios.post('http://localhost:5000/delete_node_dependencies', {
            flow_id: flowId,
            nodeId: contextMenu.nodeId,
        });

        setContextMenu({ ...contextMenu, visible: false });
    };

    const handleRightClick = (event: React.MouseEvent, node: Node) => {
        event.preventDefault();
        setContextMenu({
            visible: true,
            x: event.clientX,
            y: event.clientY,
            nodeId: node.id,
        });
    };

    // 保存流程
    const handleSave = async () => {
        await axios.post('http://localhost:5000/save_flow', {
            flow_id: flowId,
            nodes,
            edges,
        });
        alert('流程保存成功！');
    };


    return (
        <div className="container">
            {/* 顶部栏 - 框1 */}
            <div className="box1">
                <div className="top-buttons">
                    <button onClick={() => setShowBox2(prev => !prev)}>切换左侧框（框2）</button>
                    <button onClick={() => setShowBox4(prev => !prev)}>切换底部框（框4）</button>
                    {/* 顶部工具栏 */}
                    <div style={{
                        width: '100%', height: '20%',
                        padding: '10px',
                        // borderBottom: '1px solid #ddd',
                        background: '#f0f0f0'
                    }}>
                        {nodeTypes.map((type) => (
                            <div
                                key={type}
                                onDragStart={(e) => e.dataTransfer.setData('application/reactflow', type)}
                                draggable
                                style={{
                                    display: 'inline-block',
                                    marginRight: 10,
                                    padding: '6px 12px',
                                    background: '#fff',
                                    border: '1px solid #ccc',
                                    cursor: 'move',
                                }}
                            >
                                {type}
                            </div>
                        ))}
                        <button onClick={handleSave} style={{ marginLeft: 20 }}>💾 保存flow</button>
                    </div>
                </div>
            </div>

            <div className="content-area">
                {/* 框2 - 左侧边栏 */}
                {showBox2 && (
                    <div className="box2">
                        {selectedNode && (
                            <div className="fixed top-0 left-0 h-full w-1/4 bg-white border-r shadow-lg p-4 z-50">
                                {/* Header */}
                                <div className="flex justify-between items-center mb-4">
                                    <h2 className="text-lg font-semibold">
                                        节点配置：{selectedNode.data.label}
                                    </h2>
                                    <button
                                        onClick={() => {
                                            setSelectedNode(null);
                                            setShowBox2((prev) => !prev);
                                        }}
                                        className="text-sm text-blue-500 underline"
                                    >
                                        关闭
                                    </button>
                                </div>

                                {/* 配置项列表 */}
                                <div className="space-y-3">
                                    {Object.entries(configForm).map(([key, value]) => (
                                        <div key={key} className="flex items-center gap-2">
                                            <div className="flex-1">
                                                <label className="block text-sm font-medium text-gray-700">{key}</label>
                                                <input
                                                    value={value}
                                                    onChange={(e) => handleConfigChange(key, e.target.value)}
                                                    className="w-full border px-2 py-1 rounded text-sm"
                                                />
                                                <button
                                                    onClick={() => {
                                                        const { [key]: _, ...rest } = configForm;
                                                        setConfigForm(rest);
                                                    }}
                                                    className="text-red-500 hover:text-red-700 text-sm"
                                                    title="删除该配置项"
                                                >
                                                    删除
                                                </button>
                                            </div>

                                        </div>
                                    ))}
                                </div>

                                {/* 添加新配置项 */}
                                <div className="mt-4 flex gap-2">
                                    <input
                                        value={newKey}
                                        onChange={(e) => setNewKey(e.target.value)}
                                        placeholder="新配置名"
                                    // className="w-32 border px-2 py-1 rounded text-sm"
                                    />
                                    <input
                                        value={newValue}
                                        onChange={(e) => setNewValue(e.target.value)}
                                        placeholder="新值"
                                    // className="flex-1 border px-2 py-1 rounded text-sm"
                                    />
                                    <button
                                        onClick={() => {
                                            if (newKey.trim()) {
                                                setConfigForm((prev) => ({ ...prev, [newKey]: newValue }));
                                                setNewKey('');
                                                setNewValue('');
                                            }
                                        }}
                                        className="bg-green-500 text-white px-2 py-1 rounded hover:bg-green-600"
                                    >
                                        添加
                                    </button>
                                </div>

                                {/* 保存按钮 */}
                                <div className="mt-6">
                                    <button
                                        onClick={handleSaveConfig}
                                        className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                                    >
                                        保存配置
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>

                )}

                {/* 框3 - 主内容区 */}
                <div className="main-content">
                    <div className="box3">
                        <div ref={reactFlowWrapper}
                            style={{
                                width: '100%', height: '100%',
                                padding: '0px',
                                border: '2px solid green',
                            }}>
                            {/* 画布区域 */}
                            {/* <div ref={reactFlowWrapper}
                            // style={{ flex: 1 }}
                            > */}
                            <ReactFlow
                                nodes={nodes}
                                edges={edges}
                                onNodesChange={onNodesChange}
                                onEdgesChange={onEdgesChange}
                                onNodeDoubleClick={onNodeDoubleClick}
                                onConnect={onConnect}
                                onInit={setRfInstance}
                                onDrop={onDrop}
                                onDragOver={onDragOver}
                                onNodeContextMenu={handleRightClick}
                                fitView
                                defaultEdgeOptions={{
                                    style: { strokeWidth: 2, stroke: '#555' },
                                    markerEnd: { type: MarkerType.ArrowClosed, color: '#555' },
                                }}
                            >
                                <MiniMap />
                                <Controls />
                                <Background />
                            </ReactFlow>
                            {/* </div> */}
                            {/* 右键菜单 */}
                            {contextMenu.visible && (
                                <div
                                    style={{
                                        position: 'absolute',
                                        top: contextMenu.y,
                                        left: contextMenu.x,
                                        background: '#fff',
                                        border: '1px solid #ccc',
                                        zIndex: 1000,
                                        padding: 5,
                                    }}
                                >
                                    <button onClick={deleteNode}>🗑 删除节点</button>
                                </div>
                            )}
                        </div>


                    </div>
                </div>
            </div>

            {/* 框4 - 底部固定栏 */}
            <PreviewBox4
                show={showBox4}
                previewData={previewData}
                setPreviewData={setPreviewData}
            />
        </div>
    );
};

export default Layout;
