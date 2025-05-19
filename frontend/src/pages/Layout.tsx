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
import TopToolbar from './TopToolbar';
import NodeConfigDrawer from './NodeConfigDrawer';


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
            <TopToolbar
                nodeTypes={nodeTypes}
                setShowBox2={setShowBox2}
                setShowBox4={setShowBox4}
                handleSave={handleSave}
            />


            <div className="content-area">
                {/* 框2 - 左侧边栏 */}
                {showBox2 && (
                    <div className="box2">
                        {selectedNode && (
                            <NodeConfigDrawer
                                selectedNode={selectedNode}
                                configForm={configForm}
                                newKey={newKey}
                                newValue={newValue}
                                setSelectedNode={setSelectedNode}
                                setShowBox2={setShowBox2}
                                handleConfigChange={handleConfigChange}
                                setConfigForm={setConfigForm}
                                setNewKey={setNewKey}
                                setNewValue={setNewValue}
                                handleSaveConfig={handleSaveConfig}
                            />
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
