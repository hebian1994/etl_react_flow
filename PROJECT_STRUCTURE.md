# ETL Tool Project Structure

## 项目概述
这是一个基于React和Python Flask的ETL工具，支持可视化流程设计、数据处理和转换。

## 技术栈
- 前端：React + TypeScript + React Flow + MUI
- 后端：Python Flask + SQLAlchemy
- 数据库：SQLite
- 构建工具：Vite

## 项目结构

```
etl_dask/
├── frontend/                    # 前端项目
│   ├── src/
│   │   ├── components/         # 通用组件
│   │   │   ├── FlowDesign/    # 流程设计相关组件
│   │   │   ├── FlowList/      # 流程列表相关组件
│   │   │   └── common/        # 公共组件
│   │   ├── pages/             # 页面组件
│   │   │   ├── FlowDesign/    # 流程设计页面
│   │   │   └── FlowList/      # 流程列表页面
│   │   ├── hooks/             # 自定义Hooks
│   │   ├── services/          # API服务
│   │   ├── types/             # TypeScript类型定义
│   │   ├── utils/             # 工具函数
│   │   └── styles/            # 样式文件
│   ├── public/                # 静态资源
│   └── package.json           # 项目配置
│
├── backend/                    # 后端项目
│   ├── app/
│   │   ├── api/              # API路由
│   │   │   ├── flow.py      # 流程相关API
│   │   │   ├── node.py      # 节点相关API
│   │   │   └── config.py    # 配置相关API
│   │   ├── core/            # 核心功能
│   │   │   ├── etl.py       # ETL处理逻辑
│   │   │   └── dag.py       # DAG图处理
│   │   ├── models/          # 数据模型
│   │   │   ├── flow.py      # 流程模型
│   │   │   ├── node.py      # 节点模型
│   │   │   └── config.py    # 配置模型
│   │   ├── services/        # 业务服务
│   │   │   ├── flow_service.py
│   │   │   └── node_service.py
│   │   ├── utils/           # 工具函数
│   │   │   ├── file_utils.py
│   │   │   └── db_utils.py
│   │   └── main.py          # 应用入口
│   └── requirements.txt      # Python依赖
│
├── docs/                      # 项目文档
│   ├── api/                  # API文档
│   ├── architecture/         # 架构文档
│   └── user-guide/          # 用户指南
│
└── tests/                    # 测试文件
    ├── frontend/            # 前端测试
    └── backend/             # 后端测试
```

## 核心功能模块

### 1. 流程管理
- 流程创建、编辑、删除
- 流程列表展示
- 流程版本管理
- 流程配置保存和加载

### 2. 节点系统
- 节点类型：
  - File Input：文件输入节点
  - Data Viewer：数据预览节点
  - Filter：数据过滤节点
  - Left Join：数据关联节点
- 节点配置管理
- 节点依赖关系管理
- 节点Schema管理

### 3. 数据处理
- DAG图处理
- 数据转换
- 数据预览
- 数据验证

### 4. 配置管理
- 节点配置选项
- 节点配置状态
- 节点Schema配置
- 流程配置

## 数据库结构

### 主要表
1. flows
   - flow_id (PK)
   - flow_data
   - flow_name

2. nodes
   - id (PK)
   - type
   - created_at

3. node_configs
   - flow_id (PK)
   - node_id (PK)
   - config_name (PK)
   - config_param

4. dependencies
   - source (PK)
   - target (PK)

5. node_schemas
   - node_id (PK)
   - node_schema
   - created_at
   - updated_at

6. node_config_status
   - flow_id (PK)
   - node_id (PK)
   - config_status
   - created_at
   - updated_at

7. node_config_options
   - node_type (PK)
   - node_config_option
   - created_at
   - updated_at

## 开发规范

### 前端规范
1. 组件开发
   - 使用TypeScript
   - 遵循React Hooks最佳实践
   - 使用MUI组件库
   - 实现响应式设计

2. 状态管理
   - 使用React Context进行全局状态管理
   - 使用自定义Hooks封装业务逻辑

3. API调用
   - 统一使用services层处理API请求
   - 实现请求错误处理
   - 支持请求取消

### 后端规范
1. API设计
   - RESTful API设计
   - 统一的响应格式
   - 完善的错误处理

2. 数据库操作
   - 使用SQLAlchemy ORM
   - 实现事务管理
   - 优化查询性能

3. 业务逻辑
   - 服务层封装业务逻辑
   - 工具类处理通用功能
   - 完善的日志记录

## 部署说明
1. 环境要求
   - Node.js >= 14
   - Python >= 3.8
   - SQLite >= 3

2. 安装步骤
   - 前端依赖安装
   - 后端依赖安装
   - 数据库初始化
   - 环境配置

3. 运行说明
   - 开发环境运行
   - 生产环境部署
   - 性能优化建议 