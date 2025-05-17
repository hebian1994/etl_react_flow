import React, { useCallback, useEffect, useRef, useState } from 'react';
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
// import '../styles.css';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import { v4 as uuidv4 } from 'uuid';
import FileInputModal from './FileInputModal';
import DataViewerModal from './DataViewerModal';

const nodeTypes = ['File Input', 'Data Viewer'];

const FlowDesign = () => {
  const { flowId } = useParams<{ flowId: string }>();
  const reactFlowWrapper = useRef(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [rfInstance, setRfInstance] = useState<ReactFlowInstance | null>(null);
  const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, nodeId: '' });
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [modalType, setModalType] = useState<'file' | 'viewer' | null>(null);
  const [configForm, setConfigForm] = useState<Record<string, any>>({});
  const [previewData, setPreviewData] = useState<any[] | null>(null);


  // 加载流程初始数据
  useEffect(() => {
    const fetchFlow = async () => {
      const res = await axios.get(`http://localhost:5000/get_flow/${flowId}`);
      if (res.data.nodes) setNodes(res.data.nodes);
      if (res.data.edges) setEdges(res.data.edges);
    };
    fetchFlow();
  }, [flowId]);


  const onNodeDoubleClick = useCallback((_: any, node: Node) => {
    setSelectedNode(node);
    setConfigForm(node.data.config || {});

    // 如果有 dataPreview 数据，展示底部面板
    if (node.data.preview) {
      setPreviewData(node.data.preview); // 假设 preview 是个数组（如 table）
    } else {
      setPreviewData(null);
    }
  }, []);



  const handleConfigChange = (key: string, value: any) => {
    setConfigForm(prev => ({ ...prev, [key]: value }));
  };

  const handleSaveConfig = async () => {
    if (!selectedNode) return;

    const payload = {
      flow_id: flowId,
      node_id: selectedNode.id,
      config: configForm,
    };

    try {
      await axios.post('http://localhost:5000/save_config', payload);
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
    <div style={{ width: '100%', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* 顶部工具栏 */}
      <div style={{ padding: '10px', borderBottom: '1px solid #ddd', background: '#f0f0f0' }}>
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
        <button onClick={handleSave} style={{ marginLeft: 20 }}>💾 保存</button>
      </div>

      {/* 画布区域 */}
      <div ref={reactFlowWrapper}
        style={{ flex: 1 }}
      >
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
      </div>



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

      {selectedNode && (
        <div className="fixed top-0 left-0 h-full w-1/4 bg-white border-r shadow-lg p-4 z-50">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-lg font-semibold">节点配置：{selectedNode.type}</h2>
            <button onClick={() => setSelectedNode(null)} className="text-sm text-blue-500 underline">关闭</button>
          </div>

          {Object.entries(configForm).map(([key, value]) => (
            <div key={key} className="mb-2">
              <label className="block text-sm font-medium text-gray-700">{key}</label>
              <input
                value={value}
                onChange={(e) => handleConfigChange(key, e.target.value)}
                className="w-full border px-2 py-1 rounded text-sm"
              />
            </div>
          ))}

          <button
            onClick={handleSaveConfig}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            保存配置1
          </button>
        </div>
      )}

      {previewData && (
        <div className="fixed bottom-0 left-0 w-full h-[30%] bg-gray-100 border-t overflow-auto z-40">
          <div className="flex justify-between items-center px-4 py-2 bg-gray-200 border-b">
            <h3 className="font-semibold text-gray-700">数据预览</h3>
            <button
              onClick={() => setPreviewData([
                { col1: "value1", col2: "value2" },
                { col1: "value3", col2: "value4" }
              ]
              )}
              className="text-sm text-blue-600 hover:underline"
            >
              关闭
            </button>
          </div>

          <div className="p-4 overflow-auto">
            {previewData.length === 0 ? (
              <p className="text-gray-500">暂无数据</p>
            ) : (
              <table className="text-sm w-full border">
                <thead className="bg-white">
                  <tr>
                    {Object.keys(previewData[0]).map((col) => (
                      <th key={col} className="text-left border-b p-1 font-medium">{col}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {previewData.map((row, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      {Object.values(row).map((val, i) => (
                        <td key={i} className="border-b p-1">{String(val)}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}



    </div>
  );
};

export default FlowDesign;
