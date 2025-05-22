change log:

现有页面抽取成一个FLOW_DESIGN页面

添加一个FLOW_LIST列表页面，作为项目的初始页面，列表上方有个新增按钮，点击新增后，生成一个随机的FLOW_ID，然后跳转到FLOW_DESIGN页面，并且将FLOW_ID带过去。

拖拽可选操作到下部画布，删除，添加连线，发送到后端的时候都要带上FLOW_ID，保存的时候也要带上。

FLOW_DESIGN页面添加一个SAVE按钮，点击按钮，并且将FLOW_ID和当前画布这个FLOW的所有信息发送给后端保存到flows.txt，后续可以直接从flows.txt中读取出来显示到页面中。

FLOW LIST列表页面打开后，从flows.txt中读取简介信息显示到列表，选择一条记录点击末尾的编辑按钮，从后端查询到这个flow的完整信息，渲染到画布中。

File Input组件

Data Viwer组件

Filter组件

Left Join组件

我的ETL TOOL，前端REACT 和REACT FLOW和MUI，后端PYTHON FLASK。
首页我想设置一个导航栏，可以查看已经建立好的FLOW列表，后期还可以查看FLOW的历史版本，自定义组件等。显示Designer页面的时候是全屏幕，不需要显示导航栏，其他页面有导航栏并且选择显示或者隐藏。帮我修改下，并且创建一些组件来占位方便我后续开发。

PolarsBackend

我的ETL TOOL，前端REACT 和REACT FLOW和MUI，后端PYTHON FLASK。
在整个页面的中部左侧是节点配置栏，我想在这里能够选择这个节点计算结束后保留下来的列名和列的数据类型。但是需要先准备好默认的列和类型。因为每个FLOW最开始的肯定是File Input节点，那么File Input节点的默认列名和数据类型可以从配置栏中指定的文件中直接获得。如果是其他节点，就要根据DAG，依次从前往后获取列名直到该节点：中途的节点，如果是Filter那么保持上一个节点的不变，如果是Aggregate从上一个节点保留分组列和聚合列即可，如果是Left Join节点它有多个上个节点就要取他们JOIN后的列名和数据类型。
可以参考下面这个execute_dag函数，他是直接计算出指定节点的数据，但是现在我只想知道列名和数据类型即可，不需要触发完整的计算。

再创建一个node_config_status表，代表这个节点是否完成了配置。
每次拖拽新节点到画布，都发请求到后端查询 node_config_status 确保所有节点已经完成了配置，都完成了配置才允许拖拽下一个节点到REACT FLOW画布。
双击节点，只有完成了配置的才会生成node schema和获取preview data.



<!-- todo -->
<!-- big data test -->

![Designer页面](doc/pic/Designer0522.png)
![Dashboard页面](doc/pic/Dashboard0522.png)
