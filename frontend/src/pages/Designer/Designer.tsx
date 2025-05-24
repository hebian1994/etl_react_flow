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
    const [previewData, setPreviewData] = useState<{
        cols: string[];
        data: Array<Record<string, any>>;
    } | null>(null);

    const [flowName, setFlowName] = useState<string>('');

    // 加载流程初始数据
    useEffect(() => {
        setShowBox2(false);
        setShowBox4(false);
        console.log(process.env.NODE_ENV)
        const fetchFlow = async () => {
            const res = await api.get(`/get_flow/${flowId}`);
            console.log('res', res.data);
            if (res.data.flow_data.nodes) setNodes(res.data.flow_data.nodes);
            if (res.data.flow_data.edges) setEdges(res.data.flow_data.edges);
            if (res.data.flow_name) setFlowName(res.data.flow_name);
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



        // 获取节点详情（包括连线、配置状态、config/schema/data）
        const response = await api.post(`/handle_node_double_click`, payload);
        console.log("response", response.data);
        const res_status = response.data.status;
        if (res_status === 'error') {
            alert(response.data.message);
            if (response.data.error_code === 'node_config_not_ok') {
                setSelectedNode(node);
                setConfigForm({});
                setNodeSchema([]);
                setPreviewData(null);
                setShowBox2(true);
            } else {
                setSelectedNode(node);
                setShowBox2(false);
                setShowBox4(false);
            }
            return;
        }

        const {
            node_config,
            node_schema,
            preview_data
        } = response.data;

        // 如果配置完成，展示 config/schema/preview
        setSelectedNode(node);

        console.log("node_config", node_config);
        setConfigForm(node_config || {});
        setNodeSchema(node_schema || []);
        setPreviewData(preview_data?.data?.length > 0 ? preview_data : null);

        setShowBox2(true);
        setShowBox4(preview_data?.data?.length > 0);

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
            flow_data: { nodes: nodes, edges: edges },
        };

        console.log("save_config_payload", save_config_payload);

        try {

            // 保存节点配置
            const res_save_node_config = await api.post(`/save_node_config`, save_config_payload);
            alert('配置保存成功');

            // 如果节点的配置保存成功，说明节点的schema已经更新了，那么就更新本地节点数据
            const node_schema = res_save_node_config.data.node_schema;
            setNodeSchema(node_schema);
            console.log("node_schema", node_schema);

            // 如果节点的配置保存成功，说明节点的preview_data已经更新了，那么就更新本地节点数据
            const preview_data = res_save_node_config.data.preview_data;
            setPreviewData(preview_data);
            setShowBox4(true);

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

            // 如果all_nodes_config_status不是ok，也return
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
                flow_name: flowName,
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
            setEdges((eds) => {
                const updated = addEdge(params, eds);

                // 调用 API 发送连线数据
                api.post(`/add_dependency`, {
                    flow_id: flowId,
                    source: params.source,
                    target: params.target,
                });

                // 同步保存 flow，带上当前 nodes 和最新连线
                api.post(`/save_flow`, {
                    flow_id: flowId,
                    flow_name: flowName,
                    nodes,
                    edges: updated,
                });

                return updated;
            });

            console.log("params", params);
        },
        [flowId, nodes]
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
            flow_name: flowName,
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
            flow_name: flowName,
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
            flow_name: flowName,
            nodes,
            edges,
        });
        alert('流程保存成功！');
    };


    return (
        <div className="container">
            {/* 顶部栏 - 框1 */}
            <TopToolbar
                setShowBox2={setShowBox2}
                setShowBox4={setShowBox4}
                handleSave={handleSave}
                flowName={flowName} // 从flow_name表中获取
                setFlowName={setFlowName}
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
                setShow={setShowBox4}
                previewData={previewData}
                setPreviewData={setPreviewData}
            />

        </div>
    );
};

export default Designer;
