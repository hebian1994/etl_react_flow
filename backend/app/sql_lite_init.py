import sqlite3
import json

# 假设你的数据库文件名为 config.db
# DATABASE_FILE = 'config.db'

from DB import DATABASE_FILE


def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    # c.execute('''
    #     CREATE TABLE IF NOT EXISTS node_configs (
    #         flow_id TEXT,
    #         node_id TEXT,
    #         config_name TEXT,
    #         config_param TEXT,
    #         PRIMARY KEY (flow_id, node_id, config_name)
    #     )
    # ''')

    # # 创建 nodes 表
    # c.execute('''
    #     CREATE TABLE IF NOT EXISTS nodes (
    #         id TEXT PRIMARY KEY,
    #         type TEXT,
    #         created_at TEXT
    #     )
    # ''')

    # # dependencies 表
    # c.execute('''
    #     CREATE TABLE IF NOT EXISTS dependencies (
    #         source TEXT NOT NULL,
    #         target TEXT NOT NULL,
    #         PRIMARY KEY (source, target)
    #     )
    # ''')

    # # flows 表
    # c.execute('''
    #     CREATE TABLE IF NOT EXISTS flows (
    #         flow_id TEXT PRIMARY KEY,
    #         flow_data TEXT
    #     )
    # ''')

    #
    flow_line = '''{"flow_id": "2789aec8-d8c0-40c5-bbcb-1023d15a81c1", "nodes": [{"data": {"config": {}, "label": "File Input", "type": "File Input"}, "dragging": false, "height": 39, "id": "bbfde227-6cf6-4886-82dc-6563170e70a4", "position": {"x": -93.87876872264434, "y": 15.344686862288427}, "positionAbsolute": {"x": -93.87876872264434, "y": 15.344686862288427}, "selected": false, "type": "default", "width": 150}, {"data": {"config": {}, "label": "Filter", "type": "Filter"}, "dragging": false, "height": 39, "id": "32332a5a-9f84-42a9-b03b-34ea6e823f00", "position": {"x": 127.35868571840206, "y": 116.27799421816718}, "positionAbsolute": {"x": 127.35868571840206, "y": 116.27799421816718}, "selected": false, "type": "default", "width": 150}, {"data": {"config": {}, "label": "Filter", "type": "Filter"}, "dragging": false, "height": 39, "id": "2b643f6b-1f97-4634-8eac-6d592158b62b", "position": {"x": 174.61828928667433, "y": 256.73289242289314}, "positionAbsolute": {"x": 174.61828928667433, "y": 256.73289242289314}, "selected": false, "type": "default", "width": 150}, {"data": {"config": {}, "label": "File Input", "type": "File Input"}, "dragging": false, "height": 39, "id": "eac74617-f4e6-4e25-961d-b2956396cdb8", "position": {"x": 314.10041913484156, "y": 20.80327421430522}, "positionAbsolute": {"x": 314.10041913484156, "y": 20.80327421430522}, "selected": false, "type": "default", "width": 150}, {"data": {"config": {}, "label": "Left Join", "type": "Left Join"}, "dragging": false, "height": 39, "id": "c25eb843-b33e-45b6-bd42-459175e03f0b", "position": {"x": 542.5266665977998, "y": 347.14591122026263}, "positionAbsolute": {"x": 542.5266665977998, "y": 347.14591122026263}, "selected": true, "type": "default", "width": 150}], "edges": [{"id": "reactflow__edge-bbfde227-6cf6-4886-82dc-6563170e70a4-32332a5a-9f84-42a9-b03b-34ea6e823f00", "markerEnd": {"color": "#555", "type": "arrowclosed"}, "source": "bbfde227-6cf6-4886-82dc-6563170e70a4", "sourceHandle": null, "style": {"stroke": "#555", "strokeWidth": 2}, "target": "32332a5a-9f84-42a9-b03b-34ea6e823f00", "targetHandle": null}, {"id": "reactflow__edge-32332a5a-9f84-42a9-b03b-34ea6e823f00-2b643f6b-1f97-4634-8eac-6d592158b62b", "markerEnd": {"color": "#555", "type": "arrowclosed"}, "source": "32332a5a-9f84-42a9-b03b-34ea6e823f00", "sourceHandle": null, "style": {"stroke": "#555", "strokeWidth": 2}, "target": "2b643f6b-1f97-4634-8eac-6d592158b62b", "targetHandle": null}, {"id": "reactflow__edge-eac74617-f4e6-4e25-961d-b2956396cdb8-c25eb843-b33e-45b6-bd42-459175e03f0b", "markerEnd": {"color": "#555", "type": "arrowclosed"}, "source": "eac74617-f4e6-4e25-961d-b2956396cdb8", "sourceHandle": null, "style": {"stroke": "#555", "strokeWidth": 2}, "target": "c25eb843-b33e-45b6-bd42-459175e03f0b", "targetHandle": null}, {"id": "reactflow__edge-2b643f6b-1f97-4634-8eac-6d592158b62b-c25eb843-b33e-45b6-bd42-459175e03f0b", "markerEnd": {"color": "#555", "type": "arrowclosed"}, "source": "2b643f6b-1f97-4634-8eac-6d592158b62b", "sourceHandle": null, "style": {"stroke": "#555", "strokeWidth": 2}, "target": "c25eb843-b33e-45b6-bd42-459175e03f0b", "targetHandle": null}]}'''  # 用你完整那一行替换这个字符串
    flow_data = json.loads(flow_line)
    flow_id = flow_data['flow_id']
    flow_json = json.dumps(flow_data)

    c.execute('UPDATE flows SET flow_data = ? WHERE flow_id = ?',
              (flow_json, flow_id))
    if c.rowcount == 0:
        c.execute('INSERT INTO flows (flow_id, flow_data) VALUES (?, ?)',
                  (flow_id, flow_json))

    conn.commit()
    conn.close()


init_db()
