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
import { useParams } from 'react-router-dom';
import { v4 as uuidv4 } from 'uuid';
import NodeDataPreview from './NodeDataPreview';
import TopToolbar from './TopToolbar';
import NodeConfig from './NodeConfig';
import { CustomNode } from '../../components/CustomNode';
import FileInputNode from '../../components/FileInputNode';
import ContextMenu from '../../components/ContextMenu';
import api from '../../utils/api';




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
    const [nodeSchema, setNodeSchema] = useState<any[] | null>(null);

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
            const res = await api.get(`/get_flow/${flowId}`);
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

        // 如果该节点的类型不是File Input，那么他肯定要有前置节点，也就是必须有它作为target的边，否则弹出提示先建立连线
        // 要先确有连线      
        if (node.data.type !== 'File Input') {
            console.log('edges', edges);
            const filteredEdges = edges.filter((e: any) => e.target === node.id);
            if (filteredEdges.length === 0) {
                alert('请先建立连线');
                // 
                setShowBox2(false);
                setShowBox4(false);
                return;
            }
        }


        // 查看该节点是否允许双击来查看配置栏和schema和preview_data
        // 查询该节点的node_config_status
        const node_config_status = await api.post(`/check_node_config_status`, {
            flow_id: flowId,
            node_id: node.id,
        });
        console.log("node_config_status", node_config_status.data);
        if (node_config_status.data.status !== 'ok') {
            // 说明该节点还没有完成配置，那么只需要弹出配置栏就行了，而不需要get_node_config和get_node_schema和preview_data
            setConfigForm({});
            setNodeSchema([]);
            setPreviewData([]);
            setShowBox2(true);
            return;
        }


        // should send request to get config @app.route('/get_node_config', methods=['POST'])
        const node_config = await api.post(`/get_node_config`, payload);
        console.log("node_config", node_config.data);
        setConfigForm(node_config.data || {});

        // should send request to get node schema @app.route('/get_node_schema', methods=['POST'])
        const node_schema = await api.post(`/get_node_schema`, payload);
        console.log("node_schema", node_schema.data);
        setNodeSchema(node_schema.data);

        // 如果有 dataPreview 数据，展示底部面板
        const res = await api.post(`/preview_data`, payload);
        console.log(res.data);


        setShowBox2(true);


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
            config: { configForm: configForm, node_schema: nodeSchema },
        };

        console.log("save_config_payload", save_config_payload);

        try {
            // 先保存整个flow，这样推断类型的时候才能构建DAG
            await api.post(`/save_flow`, {
                flow_id: flowId,
                nodes,
                edges,
            });

            // 保存节点配置
            await api.post(`/save_node_config`, save_config_payload);
            alert('配置保存成功');

            // 如果节点的配置保存成功，说明节点的schema已经更新了，那么就更新本地节点数据
            const node_schema = await api.post(`/get_node_schema`, {
                flow_id: flowId,
                node_id: selectedNode.id,
            });
            setNodeSchema(node_schema.data);
            console.log("node_schema", node_schema.data);

            // 如果节点的配置保存成功，说明节点的preview_data已经更新了，那么就更新本地节点数据
            const res = await api.post(`/preview_data`, {
                flow_id: flowId,
                node_id: selectedNode.id,
            });
            setPreviewData(res.data);

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

            console.log("event", event.dataTransfer.getData('application/reactflow'));


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

            // 查询node_config_status
            const node_config_status = await api.post(`/check_flow_all_nodes_config_status`, {
                flow_id: flowId,
            });
            console.log("node_config_status", node_config_status.data);
            console.log("nodes", nodes);

            // 如果该节点的config_status不是ok，也return
            if (node_config_status.data.status !== 'ok') {
                alert('请先完成所有节点的配置');
                return;
            }



            setNodes((nds) => [...nds, newNode]);

            // 保存节点
            await api.post(`/save_node`, {
                flow_id: flowId,
                id,
                type,
                created_at: new Date().toISOString(),
            });
            // 保存flow
            await api.post(`/save_flow`, {
                flow_id: flowId,
                nodes,
                edges,
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
            await api.post(`/add_dependency`, {
                flow_id: flowId,
                source: params.source,
                target: params.target,
            });
            // 保存flow.这里为什么没保存成功？
            const updatedEdges = addEdge(params, edges);

            await api.post(`/save_flow`, {
                flow_id: flowId,
                nodes,
                edges: updatedEdges,
            });
            setEdges(updatedEdges);

        },
        [flowId]
    );

    // 删除节点
    const deleteNode = async () => {
        if (!contextMenu.nodeId) return;

        setNodes((nds) => nds.filter((n) => n.id !== contextMenu.nodeId));
        setEdges((eds) => eds.filter((e) => e.source !== contextMenu.nodeId && e.target !== contextMenu.nodeId));

        // delete node
        await api.post(`/delete_node`, {
            flow_id: flowId,
            nodeId: contextMenu.nodeId,
        });

        // 同时也保存flow
        await api.post(`/save_flow`, {
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
        await api.post(`/delete_dependency`, {
            flow_id: flowId,
            source,
            target,
        });

        // 新的边列表
        const newEdges = edges.filter((e) => e.id !== edgeIdToDelete);

        // 更新 state
        setEdges(newEdges);

        // 保存 flow（用新的 edges）
        await api.post(`/save_flow`, {
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
        await api.post(`/save_flow`, {
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
                                setSelectedNode={setSelectedNode}
                                configForm={configForm}
                                setConfigForm={setConfigForm}
                                nodeSchema={nodeSchema}
                                setNodeSchema={setNodeSchema}
                                setShowBox2={setShowBox2}
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
