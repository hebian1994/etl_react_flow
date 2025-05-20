import React, { useCallback, useEffect, useRef, useState } from 'react';
import './Designer.css';
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
import NodeDataPreview from './NodeDataPreview';
import TopToolbar from './TopToolbar';
import NodeConfig from './NodeConfig';
import { CustomNode } from '../../components/CustomNode';
import FileInputNode from '../../components/FileInputNode';
import ContextMenu from '../../components/ContextMenu';
const API_BASE = process.env.REACT_APP_API_BASE_URL;



const nodeTypes = ['File Input', 'Data Viewer', 'Filter', 'Aggregate', 'Left Join'];

const CustomNodeTypes = {
    custom: CustomNode,
    fileInput: FileInputNode,
};


const Designer: React.FC = () => {
    const [showBox2, setShowBox2] = useState<boolean>(true);
    const [showBox4, setShowBox4] = useState<boolean>(true);
    const reactFlowWrapper = useRef(null);
    const { flowId } = useParams<{ flowId: string }>();
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [rfInstance, setRfInstance] = useState<ReactFlowInstance | null>(null);
    const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, nodeId: '' });
    const [edgeContextMenu, setEdgeContextMenu] = useState({ visible: false, x: 0, y: 0, edgeId: '' });
    const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);

    const [selectedNode, setSelectedNode] = useState<Node | null>(null);
    const [modalType, setModalType] = useState<'file' | 'viewer' | null>(null);
    const [configForm, setConfigForm] = useState<Record<string, any>>({});
    const [previewData, setPreviewData] = useState<any[] | null>(null);



    // 加载流程初始数据
    useEffect(() => {
        setShowBox2(false);
        setShowBox4(false);
        console.log(process.env.NODE_ENV)
        const fetchFlow = async () => {
            const res = await axios.get(`${API_BASE}/get_flow/${flowId}`);
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
        const node_config = await axios.post(`${API_BASE}/get_node_config`, payload);
        console.log("node_config", node_config.data);
        setConfigForm(node_config.data || {});
        setShowBox2(true);


        // 如果有 dataPreview 数据，展示底部面板
        const res = await axios.post(`${API_BASE}/preview_data`, payload);
        console.log(res.data);

        if (res.data.length > 0) {
            setShowBox4(true);
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
            await axios.post(`${API_BASE}/save_config`, save_config_payload);
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
                type: 'custom',
                position,
                data: { label: type, type, config: {} },
            };

            setNodes((nds) => [...nds, newNode]);

            // 通知后端新节点
            await axios.post(`${API_BASE}/save_node`, {
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
            await axios.post(`${API_BASE}/add_dependency`, {
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

        await axios.post(`${API_BASE}/delete_node_dependencies`, {
            flow_id: flowId,
            nodeId: contextMenu.nodeId,
        });
        // 同时也保存flow
        await axios.post(`${API_BASE}/save_flow`, {
            flow_id: flowId,
            nodes,
            edges,
        });

        setContextMenu({ ...contextMenu, visible: false });
    };

    const deleteEdge = async () => {
        if (!edgeContextMenu.edgeId) return;

        const edgeIdToDelete = edgeContextMenu.edgeId;

        // 获取要删除的边的信息
        const edgeToDelete = edges.find((e) => e.id === edgeIdToDelete);
        if (!edgeToDelete) return;

        const { source, target } = edgeToDelete;

        // 后端删除依赖
        await axios.post(`${API_BASE}/delete_dependency`, {
            flow_id: flowId,
            source,
            target,
        });

        // 新的边列表
        const newEdges = edges.filter((e) => e.id !== edgeIdToDelete);

        // 更新 state
        setEdges(newEdges);

        // 保存 flow（用新的 edges）
        await axios.post(`${API_BASE}/save_flow`, {
            flow_id: flowId,
            nodes,
            edges: newEdges,
        });

        // 关闭右键菜单
        setEdgeContextMenu({ ...edgeContextMenu, visible: false });
    };


    // 节点右键菜单
    const onNodeContextMenu = (event: React.MouseEvent, node: Node) => {
        event.preventDefault();
        setContextMenu({
            visible: true,
            x: event.clientX,
            y: event.clientY,
            nodeId: node.id,
        });
    };

    // 连线右键菜单
    const onEdgeContextMenu = async (event: React.MouseEvent, edge: Edge) => {
        event.preventDefault();

        console.log("edges", edges);
        console.log("nodes", nodes);
        setEdgeContextMenu({
            visible: true,
            x: event.clientX,
            y: event.clientY,
            edgeId: edge.id,
        });

    }



    // 保存流程
    const handleSave = async () => {
        await axios.post(`${API_BASE}/save_flow`, {
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
                            <NodeConfig
                                selectedNode={selectedNode}
                                configForm={configForm}
                                setSelectedNode={setSelectedNode}
                                setShowBox2={setShowBox2}
                                setConfigForm={setConfigForm}
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
                                onNodeContextMenu={onNodeContextMenu}
                                onEdgeContextMenu={onEdgeContextMenu}
                                fitView
                                defaultEdgeOptions={{
                                    style: { strokeWidth: 2, stroke: '#555' },
                                    markerEnd: { type: MarkerType.ArrowClosed, color: '#555' },
                                }}
                                nodeTypes={CustomNodeTypes}
                            >
                                {/* <MiniMap /> */}
                                <Controls />
                                <Background />
                            </ReactFlow>
                            {/* </div> */}
                            {/* 右键菜单 */}
                            <ContextMenu
                                visible={contextMenu.visible}
                                x={contextMenu.x}
                                y={contextMenu.y}
                                onClose={() => setContextMenu({ ...contextMenu, visible: false })}
                                actions={[
                                    {
                                        label: '🗑 删除节点',
                                        onClick: deleteNode,
                                    },
                                ]}
                            />

                            <ContextMenu
                                visible={edgeContextMenu.visible}
                                x={edgeContextMenu.x}
                                y={edgeContextMenu.y}
                                onClose={() => setEdgeContextMenu({ ...edgeContextMenu, visible: false })}
                                actions={[
                                    {
                                        label: '删除连线',
                                        onClick: deleteEdge,
                                    },
                                ]}
                            />
                        </div>


                    </div>
                </div>
            </div>

            {/* 框4 - 底部固定栏 */}
            <NodeDataPreview
                show={showBox4}
                previewData={previewData}
                setPreviewData={setPreviewData}
            />
        </div>
    );
};

export default Designer;
