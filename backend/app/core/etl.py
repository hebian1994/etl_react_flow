import pandas as pd

from models.node import Node
from ..utils.db_utils import get_db_session
from ..models.config import NodeConfig
from ..core.dag import get_node_dependencies

class ETLProcessor:
    def __init__(self, flow_id, node_id):
        self.flow_id = flow_id
        self.node_id = node_id
        self.data = None

    def get_node_config(self):
        """获取节点配置"""
        with get_db_session() as db:
            configs = db.query(NodeConfig).filter(
                NodeConfig.flow_id == self.flow_id,
                NodeConfig.node_id == self.node_id
            ).all()
            return {c.config_name: c.config_param for c in configs}

    def process_file_input(self):
        """处理文件输入节点"""
        config = self.get_node_config()
        if 'path' in config:
            try:
                self.data = pd.read_csv(config['path'])
                return True
            except Exception as e:
                print(f"Error reading file: {e}")
                return False
        return False

    def process_filter(self):
        """处理过滤节点"""
        dependencies = get_node_dependencies(self.node_id, self.flow_id)
        if not dependencies:
            return False
        
        # TODO: 实现过滤逻辑
        return True

    def process_left_join(self):
        """处理左连接节点"""
        dependencies = get_node_dependencies(self.node_id, self.flow_id)
        if len(dependencies) < 2:
            return False
        
        # TODO: 实现左连接逻辑
        return True

    def process_data_viewer(self):
        """处理数据预览节点"""
        dependencies = get_node_dependencies(self.node_id, self.flow_id)
        if not dependencies:
            return False
        
        # TODO: 实现数据预览逻辑
        return True

    def execute(self):
        """执行ETL处理"""
        with get_db_session() as db:
            node_type = db.query(Node).filter(Node.id == self.node_id).first().type
            
            if node_type == 'File Input':
                return self.process_file_input()
            elif node_type == 'Filter':
                return self.process_filter()
            elif node_type == 'Left Join':
                return self.process_left_join()
            elif node_type == 'Data Viewer':
                return self.process_data_viewer()
            
            return False 