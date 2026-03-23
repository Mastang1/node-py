# NodeGraphQt Technical Guide For Visual Instrument Programming

## 1. Scope
这份文档基于本地 `NodeGraphQt` 源码、示例和运行验证整理，目标不是简单抄 API，而是让你能理解并复述该库的基本原理，再把它改造成你自己的“Python 图形化编程 / 虚拟仪器流程编辑器”。

本文聚焦公开核心 API。

- 重点覆盖：`NodeGraph`、`NodeObject`、`BaseNode`、`Port`、`GroupNode`、`BackdropNode`、节点控件、菜单、序列化、调色板、属性面板。
- 不重点覆盖：`_xxx` 私有方法、底层 `QGraphicsItem` 绘制细节、内部命令对象逐个源码分析。
- 最重要结论：`NodeGraphQt` 是图编辑器框架，不是流程执行器。拖拽、连线、属性编辑、保存加载它能做；图怎么执行、怎么导出 Python、怎么调用你的仪器 API，必须由你自己实现。

## 2. 用费曼学习法先解释清楚

### 2.1 把它想成一块可编程白板
如果你要向别人解释 `NodeGraphQt`，最容易懂的说法是：

> `NodeGraphQt` 就像一个“可以拖节点积木、再用线把积木连起来”的白板编辑器。  
> 你负责定义每个积木代表什么业务动作，`NodeGraphQt` 负责让这些积木能被创建、拖动、连线、修改参数、保存和重新加载。

换一种更工程化的表述：

- `NodeGraph` 是总控台。
- `Node` 是业务动作单元。
- `Port` 是节点上的插口。
- `Pipe` 是连接线。
- `Property` 是节点参数。
- `Node Widget` 是节点上的输入控件。
- `serialize_session()` / `save_session()` 是保存图结构。

### 2.2 这套库解决的是什么问题
它解决的是“图的编辑问题”，不是“图的执行问题”。

它负责：

- 拖一个节点到画布上
- 给节点加输入输出口
- 让节点之间连线
- 编辑节点参数
- 显示属性面板
- 保存/恢复整张图

它不负责：

- 自动执行节点逻辑
- 自动决定业务拓扑顺序
- 自动导出 Python
- 自动调用你的设备驱动

所以对你的需求，正确分工是：

- `NodeGraphQt` 负责前台图编辑
- 你的代码负责后台执行器、代码生成器、仪器 API 封装

### 2.3 你应该能这样复述它
如果你真的理解了，你应该能对别人讲出这段话：

> 我先定义多个继承自 `BaseNode` 的业务节点类，每个节点有端口和参数控件。  
> 然后把这些节点类注册给 `NodeGraph`。  
> `NodeGraph` 会负责节点创建、拖拽、连线、显示和保存。  
> 但是图的“执行语义”不在库里，我必须自己遍历图，按拓扑顺序执行节点，或者把节点转换成 Python 代码。

只要你能顺着讲清楚这段话，你就已经掌握了这个库的核心。

## 3. 源码结构怎么读

### 3.1 最重要的文件
- `NodeGraphQt/NodeGraphQt/__init__.py`
  公开导出主 API，普通使用者最应该先看这里。
- `NodeGraphQt/NodeGraphQt/base/graph.py`
  `NodeGraph` 与 `SubGraph` 核心实现，最重要。
- `NodeGraphQt/NodeGraphQt/base/node.py`
  `NodeObject` 的属性、模型、序列化基础。
- `NodeGraphQt/NodeGraphQt/nodes/base_node.py`
  `BaseNode` 的端口、嵌入控件、连接回调。
- `NodeGraphQt/NodeGraphQt/base/port.py`
  `Port` 的连接、断开、锁定、约束。
- `NodeGraphQt/NodeGraphQt/base/factory.py`
  节点注册和实例工厂。
- `NodeGraphQt/NodeGraphQt/base/model.py`
  图/节点/端口的数据模型与序列化结构。
- `NodeGraphQt/NodeGraphQt/base/menu.py`
  右键菜单 API。
- `NodeGraphQt/NodeGraphQt/custom_widgets/nodes_palette.py`
  节点调色板。
- `NodeGraphQt/NodeGraphQt/custom_widgets/nodes_tree.py`
  节点树。
- `NodeGraphQt/NodeGraphQt/custom_widgets/properties_bin/node_property_widgets.py`
  属性面板。
- `NodeGraphQt/examples/basic_example.py`
  最完整的官方示例。

### 3.2 运行时架构
运行时可以理解成三层：

1. 数据层
- `NodeGraphModel`
- `NodeModel`
- `PortModel`

2. 控制层
- `NodeGraph`
- `NodeFactory`
- undo/redo 命令

3. 视图层
- `NodeViewer`
- `NodeScene`
- `NodeGraphWidget`
- 各种 `QGraphicsItem`
- 调色板 / 属性面板 / 节点树

一句话总结：

> `NodeGraph` 驱动界面与数据同步，`Model` 保存状态，`Node/Port` 表达结构，`Viewer` 负责绘制和交互。

## 4. 关键概念

### 4.1 节点身份不是显示名，而是 `type_`
每个节点类都应该定义：

- `__identifier__`
- `NODE_NAME`

例如：

```python
class SetVoltageNode(BaseNode):
    __identifier__ = "demo.instrument"
    NODE_NAME = "Set Voltage"
```

它最终会得到一个稳定类型字符串：

```python
"demo.instrument.SetVoltageNode"
```

这很关键，因为：

- `NODE_NAME` 主要用于显示
- `type_` 才是保存/加载图时真正依赖的类型标识
- 你一旦改了类名或 `__identifier__`，旧图文件可能加载失败

### 4.2 图保存的是结构，不是运行现场
`serialize_session()` / `save_session()` 保存的是：

- 图级设置
- 节点类型
- 节点位置和样式
- 节点属性
- 连接关系

不是：

- 实际线程状态
- 设备连接句柄
- 执行堆栈
- 中间缓存数据

所以恢复 session，恢复的是“编辑现场”，不是“执行现场”。

### 4.3 连接关系不等于执行逻辑
在 `NodeGraphQt` 里，连线本身只是一种结构关系。

- A 的输出连到 B 的输入，表示图里存在依赖。
- 它不等于库会自动执行 A 再执行 B。

如果你要做虚拟仪器流程执行，就必须自己定义：

- 哪些端口表示控制流
- 控制流如何拓扑排序
- 每个节点执行什么 Python

## 5. 针对你的需求，应该如何设计

### 5.1 正确拆分职责
你的目标可以拆成 5 个部件：

1. 图编辑器
- 由 `NodeGraphQt` 实现

2. 业务节点
- 你自己写 `BaseNode` 子类
- 例如 `Open Instrument`、`Set Voltage`、`Measure Voltage`

3. 图执行器
- 你自己做拓扑排序
- 顺序调用每个节点的执行方法

4. 代码导出器
- 把节点转换成 Python 语句
- 输出为 `.py`

5. 控制台输出
- 你自己的日志面板或控制器窗口

### 5.2 推荐的运行模型
最实用的方式是“控制流端口 + 上下文字典”：

- 用线表示执行顺序
- 用节点属性表示参数
- 用 `context` 字典保存中间结果
- 后续节点再从 `context` 取值

例如：

- `Measure Voltage` 写入 `context["measured_voltage"]`
- `Print Context` 再去读这个 key

这比做复杂的数据类型系统更容易落地，也更容易导出 Python。

### 5.3 `demo_01.py` 已经做的事
本目录中的 `demo_01.py` 已经实现了一个完整 demo：

- 用 `NodeGraphQt` 搭建可拖拽图编辑器
- 把虚拟仪器 API 封装成多个节点
- 支持保存图 JSON
- 支持导出独立 Python 脚本
- 支持执行图并在日志区打印
- 支持 headless smoke test 自动验证

运行：

```bash
python "f:\workspace\ai_workspace\design_tcs\NodeGraphQt_notes\demo_01.py"
```

闭环验证：

```bash
python "f:\workspace\ai_workspace\design_tcs\NodeGraphQt_notes\demo_01.py" --headless-smoke-test
```

## 6. API 手册
下面按公开核心 API 分类说明。这里的“每个 API”指公开使用层 API；内部私有实现如 `_deserialize()`、`_wire_signals()` 不作为常规使用层 API。

## 6.1 `NodeGraph`
`NodeGraph` 是图控制器，是最应该优先掌握的类。

### 构造函数
- `NodeGraph(parent=None, **kwargs)`
  - `parent`: Qt 父对象。
  - `kwargs`: 可覆写内部对象，例如 `model`、`node_factory`、`undo_stack`、`viewer`、`layout_direction`、`pipe_style`。
  - 用途：初始化图、模型、工厂、撤销栈、视图、菜单和信号。

### 重要信号
- `nodes_registered(list)`
  节点类注册完成后触发。
- `node_created(NodeObject)`
  调用 `create_node()` 创建节点时触发。
- `nodes_deleted(list[str])`
  节点删除后触发，参数是节点 id 列表。
- `node_selected(NodeObject)`
  单击选中节点时触发。
- `node_selection_changed(list, list)`
  选择集变化时触发，参数分别是新增选择和取消选择的节点列表。
- `node_double_clicked(NodeObject)`
  双击节点时触发，适合弹出属性编辑器。
- `port_connected(Port, Port)`
  连线建立时触发。
- `port_disconnected(Port, Port)`
  连线断开时触发。
- `property_changed(NodeObject, str, object)`
  节点属性变化时触发。
- `data_dropped(QMimeData, QPoint)`
  外部拖放数据到图时触发。
- `session_changed(str)`
  当前 session 文件路径变化时触发。
- `context_menu_prompt(menu, node)`
  菜单显示前触发，可动态改菜单。

### 基础对象访问
- `graph.model`
  返回 `NodeGraphModel`。
- `graph.node_factory`
  返回 `NodeFactory`。
- `graph.widget`
  返回 `NodeGraphWidget`，通常把它塞进主窗口布局。
- `graph.undo_view`
  返回 `QUndoView`，用于查看撤销历史。
- `graph.viewer()`
  返回内部 `NodeViewer`。普通集成优先用 `graph.widget`。
- `graph.scene()`
  返回 `NodeScene`。

### 外观与交互控制
- `background_color()`
  读取背景色。
- `set_background_color(r, g, b)`
  设置背景色。
- `grid_color()`
  读取网格色。
- `set_grid_color(r, g, b)`
  设置网格色。
- `set_grid_mode(mode=None)`
  设置网格显示模式。
  - 常用值：`ViewerEnum.GRID_DISPLAY_NONE`、`DOTS`、`LINES`
- `acyclic()`
  查看是否为有向无环图模式。
- `set_acyclic(mode=True)`
  控制是否禁止形成环。
- `pipe_collision()`
  查看是否允许拖节点插入到线中间。
- `set_pipe_collision(mode=True)`
  开关“节点碰线插入”功能。
- `pipe_slicing()`
  查看是否允许切线。
- `set_pipe_slicing(mode=True)`
  开关切线功能。启用后通常可用 `Alt + Shift + LMB Drag` 切断连线。
- `pipe_style()`
  读取线条样式。
- `set_pipe_style(style)`
  设置连线样式。
  - 常用值：`PipeLayoutEnum.CURVED`、`STRAIGHT`、`ANGLE`
- `layout_direction()`
  读取图布局方向。
- `set_layout_direction(direction)`
  设置全图布局方向，并同步到当前图里所有节点。
  - 常用值：`LayoutDirectionEnum.HORIZONTAL`、`VERTICAL`

### 视图导航
- `cursor_pos()`
  返回当前光标在场景中的位置。
- `toggle_node_search()`
  开关节点搜索弹窗。
- `show()`
  便捷调用 `graph.widget.show()`。
- `close()`
  便捷关闭图控件。
- `fit_to_selection()`
  缩放到刚好包住选中节点；如果没有选中，则缩放到全部节点。
- `reset_zoom()`
  重置缩放。
- `set_zoom(zoom=0)`
  设置缩放值。
- `get_zoom()`
  读取当前缩放。
- `center_on(nodes=None)`
  视图中心对准指定节点列表。
- `center_selection()`
  视图中心对准当前选中节点。

### 节点注册与创建
- `registered_nodes()`
  返回所有已注册节点类型字符串列表。
- `register_node(node, alias=None)`
  注册单个节点类。
  - `node`: 节点类，必须是 `NodeObject` / `BaseNode` 子类。
  - `alias`: 可选别名，例如内置 `Backdrop` 就通过别名注册。
  - 用途：让该节点可以被图创建、被调色板显示、被反序列化。
- `register_nodes(nodes)`
  批量注册节点类列表。
- `create_node(node_type, name=None, selected=True, color=None, text_color=None, pos=None, push_undo=True)`
  创建节点实例并加入图。
  - `node_type`: 节点类型字符串或别名。
  - `name`: 显示名。
  - `selected`: 创建后是否选中。
  - `color`: 节点颜色，支持 `(r, g, b)` 或 `"#RRGGBB"`。
  - `text_color`: 文本颜色。
  - `pos`: 初始位置 `(x, y)`。
  - `push_undo`: 是否登记到撤销栈。
  - 返回：节点实例。
- `add_node(node, pos=None, selected=True, push_undo=True, inherite_graph_style=True)`
  把已存在的节点对象加入图。
  - 与 `create_node()` 的区别：不通过工厂创建，不触发 `node_created` 信号。
  - 用途：当你手工构造节点对象时使用。

### 删除、查询、选择
- `delete_node(node, push_undo=True)`
  删除单个节点。
- `remove_node(node, push_undo=True)`
  从图中移除节点。
- `delete_nodes(nodes, push_undo=True)`
  批量删除节点。
- `extract_nodes(nodes, push_undo=True, prompt_warning=True)`
  提取节点，断开与其余节点连接。
- `all_nodes()`
  返回图中全部节点。
- `selected_nodes()`
  返回当前选中节点列表。
- `selected_pipes()`
  返回当前选中的连线。
- `select_all()`
  全选。
- `clear_selection()`
  清除选中。
- `invert_selection()`
  反选。
- `get_node_by_id(node_id)`
  通过节点 id 获取节点。
- `get_node_by_name(name)`
  通过名称查找节点。
- `get_nodes_by_type(node_type)`
  按类型筛选节点。
- `get_unique_name(name)`
  返回当前图中不冲突的唯一名称。

### session 保存、加载与剪贴板
- `current_session()`
  返回当前 session 文件路径。
- `clear_session()`
  清空当前图。
- `serialize_session()`
  把整张图转为字典。
  - 返回结构核心是 `graph`、`nodes`、`connections`。
- `deserialize_session(layout_data, clear_session=True, clear_undo_stack=True)`
  从字典恢复整张图。
- `save_session(file_path)`
  保存为 JSON 文件。
- `load_session(file_path)`
  清空当前图后再从文件加载。
- `import_session(file_path, clear_undo_stack=True)`
  导入到当前图，不一定清空。
- `copy_nodes(nodes=None)`
  把节点复制为 JSON 字符串写入系统剪贴板。
- `cut_nodes(nodes=None)`
  剪切节点。
- `paste_nodes(adjust_graph_style=True)`
  从剪贴板粘贴节点。
- `duplicate_nodes(nodes)`
  复制一份节点。
- `disable_nodes(nodes, mode=None)`
  批量启用/禁用节点。

### 自动排版与辅助弹窗
- `auto_layout_nodes(nodes=None, down_stream=True, start_nodes=None)`
  自动排版。
  - `nodes`: 要参与排版的节点列表。
  - `down_stream`: 是否按下游方向排。
  - `start_nodes`: 手工指定排版起点。
  - 用途：很适合把“执行流图”排成一列或多列。
- `question_dialog(text, title='Node Graph', dialog_icon=None, custom_icon=None, parent=None)`
  询问框。
- `message_dialog(text, title='Node Graph', dialog_icon=None, custom_icon=None, parent=None)`
  消息框。
- `load_dialog(current_dir=None, ext=None, parent=None)`
  文件打开框。
- `save_dialog(current_dir=None, ext=None, parent=None)`
  文件保存框。

### 撤销栈
- `undo_stack()`
  获取 `QUndoStack`。
- `clear_undo_stack()`
  清空撤销栈。
- `begin_undo(name)`
  开始一个撤销宏块。
- `end_undo()`
  结束撤销宏块。

### 菜单 API
- `context_menu()`
  相当于 `get_context_menu('graph')`。
- `context_nodes_menu()`
  相当于 `get_context_menu('nodes')`。
- `get_context_menu(menu)`
  返回指定菜单对象。
  - `menu='graph'`: 图空白区菜单
  - `menu='nodes'`: 节点菜单
- `set_context_menu(menu_name, data, anchor_path=None)`
  用序列化字典填充菜单。
- `set_context_menu_from_file(file_path, menu='graph')`
  从 JSON 配置文件生成菜单。
- `disable_context_menu(disabled=True, name='all')`
  禁用/启用菜单。

### Group/SubGraph 相关
- `is_root`
  当前图是否是根图。
- `sub_graphs`
  当前已展开的子图字典。
- `expand_group_node(node)`
  展开 `GroupNode`。
- `collapse_group_node(node)`
  折叠 `GroupNode`。

## 6.2 `NodeObject`
`NodeObject` 是所有节点的基础类，`BaseNode` 也是继承它。

### 类属性
- `__identifier__`
  节点命名空间。
- `NODE_NAME`
  节点默认显示名。
- `type_`
  由 `__identifier__ + '.' + 类名` 自动组成。

### 重要属性/方法
- `id`
  节点唯一 id。
- `graph`
  所属 `NodeGraph`。
- `view`
  节点对应的 `QGraphicsItem`。
- `set_view(item)`
  切换绘制视图对象。
- `model`
  节点数据模型 `NodeModel`。
- `set_model(model)`
  替换模型。
- `update_model()`
  把 view 当前状态回写到 model。
- `update()`
  把 model 当前状态刷新到 view。
- `serialize()`
  把当前节点转为字典。
- `name()`
  读取名称。
- `set_name(name='')`
  设置名称。
- `color()`
  读取颜色。
- `set_color(r=0, g=0, b=0)`
  设置颜色。
- `disabled()`
  是否禁用。
- `set_disabled(mode=False)`
  启用/禁用节点。
- `selected()`
  是否选中。
- `set_selected(selected=True)`
  设置选中状态。

### 属性系统
- `create_property(name, value, items=None, range=None, widget_type=None, widget_tooltip=None, tab=None)`
  创建一个自定义属性。
  - `name`: 属性名。
  - `value`: 默认值。
  - `items`: 供下拉框之类使用的候选项。
  - `range`: 供 slider 使用的范围。
  - `widget_type`: 指定在 `PropertiesBinWidget` 里如何显示。
  - `widget_tooltip`: 属性提示。
  - `tab`: 属性面板 tab 名。
- `properties()`
  获取节点全部属性字典。
- `get_property(name)`
  获取属性值。
- `set_property(name, value, push_undo=True)`
  设置属性值。
  - `push_undo`: 是否进入撤销栈。
- `has_property(name)`
  判断属性是否存在。

### 位置与布局
- `set_x_pos(x)`
  设置 X。
- `set_y_pos(y)`
  设置 Y。
- `set_pos(x, y)`
  设置位置。
- `x_pos()`
  获取 X。
- `y_pos()`
  获取 Y。
- `pos()`
  获取 `(x, y)`。
- `layout_direction()`
  获取当前节点布局方向。
- `set_layout_direction(value=0)`
  设置当前节点布局方向。

## 6.3 `BaseNode`
`BaseNode` 是你写业务节点时最常继承的类。它比 `NodeObject` 多了“端口”和“节点内控件”能力。

### 基础
- `set_icon(icon=None)`
  设置节点图标路径。
- `icon()`
  获取图标路径。
- `widgets()`
  返回当前节点所有嵌入控件。
- `get_widget(name)`
  通过属性名获取嵌入控件。

### 添加节点内控件
- `add_custom_widget(widget, widget_type=None, tab=None)`
  添加自定义 `NodeBaseWidget`。
- `add_combo_menu(name, label='', items=None, tooltip=None, tab=None)`
  添加下拉框。
- `add_text_input(name, label='', text='', placeholder_text='', tooltip=None, tab=None)`
  添加文本框。
- `add_spinbox(name, label='', value=0, min_value=0, max_value=100, tooltip=None, tab=None, double=False)`
  添加整数/浮点 spinbox。
- `add_button(name, label='', text='', tooltip=None, tab=None)`
  添加按钮。
- `add_checkbox(name, label='', text='', state=False, tooltip=None, tab=None)`
  添加复选框。
- `hide_widget(name, push_undo=True)`
  隐藏节点内控件。
- `show_widget(name, push_undo=True)`
  显示节点内控件。

### 端口 API
- `add_input(name='input', multi_input=False, display_name=True, color=None, locked=False, painter_func=None)`
  添加输入口。
  - `name`: 端口名。
  - `multi_input`: 是否允许多个输入连接到这个输入口。
  - `display_name`: 是否显示端口名。
  - `color`: 端口颜色。
  - `locked`: 是否锁定。
  - `painter_func`: 自定义端口形状绘制函数。
  - 返回：`Port`
- `add_output(name='output', multi_output=True, display_name=True, color=None, locked=False, painter_func=None)`
  添加输出口。
- `get_input(port)`
  按名字或索引取输入口。
- `get_output(port)`
  按名字或索引取输出口。
- `delete_input(port)`
  删除输入口。
  - 注意：要求先 `set_port_deletion_allowed(True)`。
- `delete_output(port)`
  删除输出口。
- `set_port_deletion_allowed(mode=False)`
  允许动态删除端口。
- `port_deletion_allowed()`
  查看是否允许删除端口。
- `set_ports(port_data)`
  从序列化数据重建输入输出端口。
- `inputs()`
  返回 `{port_name: port_obj}` 字典。
- `input_ports()`
  返回输入口列表。
- `outputs()`
  返回 `{port_name: port_obj}` 字典。
- `output_ports()`
  返回输出口列表。
- `input(index)`
  按索引取输入口。
- `set_input(index, port)`
  把本节点第 `index` 个输入口连接到目标端口。
- `output(index)`
  按索引取输出口。
- `set_output(index, port)`
  把本节点第 `index` 个输出口连接到目标端口。
- `connected_input_nodes()`
  返回输入口上游节点映射。
- `connected_output_nodes()`
  返回输出口下游节点映射。

### 连接约束与回调
- `add_accept_port_type(port, port_type_data)`
  为指定端口添加“允许连接”约束。
- `accepted_port_types(port)`
  查询某个端口的允许连接规则。
- `add_reject_port_type(port, port_type_data)`
  为指定端口添加“拒绝连接”约束。
- `rejected_port_types(port)`
  查询某个端口的拒绝连接规则。
- `on_input_connected(in_port, out_port)`
  输入口连接建立时回调。
  - 默认什么都不做。
  - 非常适合做“当连接建立时自动同步某些节点状态”的逻辑。
- `on_input_disconnected(in_port, out_port)`
  输入口断开连接时回调。

## 6.4 `Port`
`Port` 是节点端口对象，负责连接关系。

### 基础属性
- `view`
  返回端口对应的图元。
- `model`
  返回 `PortModel`。
- `type_()`
  端口类型，通常是 `in` 或 `out`。
- `multi_connection()`
  是否支持多连接。
- `node()`
  返回所属节点。
- `name()`
  返回端口名。
- `visible()`
  是否可见。
- `set_visible(visible=True, push_undo=True)`
  设置可见性。

### 锁定与连接
- `locked()`
  是否锁定。
- `lock()`
  锁定端口。
- `unlock()`
  解锁端口。
- `set_locked(state=False, connected_ports=True, push_undo=True)`
  设置锁定状态。
  - `connected_ports=True` 时会把相连端口也同步锁定/解锁。
- `connected_ports()`
  返回所有相连端口。
- `connect_to(port=None, push_undo=True, emit_signal=True)`
  连接到目标端口。
- `disconnect_from(port=None, push_undo=True, emit_signal=True)`
  断开与目标端口的连接。
- `clear_connections(push_undo=True, emit_signal=True)`
  清空本端口的全部连接。

### 连接约束
- `add_accept_port_type(port_name, port_type, node_type)`
  添加“只允许连接到这些类型”规则。
- `accepted_port_types()`
  查询允许连接规则。
- `add_reject_port_type(port_name, port_type, node_type)`
  添加“拒绝这些类型连接”规则。
- `rejected_port_types()`
  查询拒绝连接规则。

### 外观
- `color`
  端口填充色。
- `border_color`
  端口边框色。

## 6.5 `GroupNode`
`GroupNode` 是可以展开成子图的复合节点。

### 关键能力
- `is_expanded`
  是否已展开。
- `get_sub_graph()`
  获取子图控制器。
- `get_sub_graph_session()`
  获取子图序列化 session。
- `set_sub_graph_session(serialized_session)`
  设置子图 session。
- `expand()`
  展开 group node，返回 `SubGraph`。
- `collapse()`
  折叠 group node。
- `set_name(name='')`
  改名后还会同步更新 tab 和导航标签。
- `add_input(...)`
  新增输入口时，如果已展开，还会自动创建对应 `PortInputNode`。
- `add_output(...)`
  新增输出口时，如果已展开，还会自动创建对应 `PortOutputNode`。

### 什么时候该用
适合做：

- 子流程
- 复合功能块
- 大流程折叠

对于你的仪器编程平台，如果以后要做“初始化子流程”“校准子流程”“采样子流程”，`GroupNode` 很有价值。

## 6.6 `BackdropNode`
`BackdropNode` 不是执行节点，更像视觉分组容器。

### API
- `on_backdrop_updated(update_prop, value=None)`
  backdrop 被拖拽缩放时触发。
- `auto_size()`
  自动包裹当前覆盖的节点。
- `wrap_nodes(nodes)`
  包裹指定节点列表。
- `nodes()`
  返回 backdrop 下面包着的节点。
- `set_text(text='')`
  设置说明文字。
- `text()`
  获取说明文字。
- `set_size(width, height)`
  设置大小。
- `size()`
  获取大小。

### 用途
非常适合在流程图里做：

- “初始化区”
- “采样区”
- “安全关断区”
- “异常处理区”

## 6.7 `BaseNodeCircle` 与 `BaseNodeSVG`
- `BaseNodeCircle`
  - 本质上还是 `BaseNode`
  - 只是视觉样式变成圆形
- `BaseNodeSVG`
  - 也是 `BaseNode`
  - 多了 `svg_file` 属性
  - `set_svg(svg_file)` 可切换 SVG 外观

它们适合做更有识别度的节点，例如：

- Start/End 节点画成圆形
- 特殊仪器节点画成 SVG 图标

## 6.8 `NodeBaseWidget` 及内置节点控件
`NodeBaseWidget` 是“把普通 Qt 控件嵌入节点”的包装器。

### `NodeBaseWidget`
- `value_changed(str, object)`
  值变化信号，通常连到 `BaseNode.set_property()`。
- `type_`
  控件类型名。
- `node`
  所属节点。
- `get_name()`
  获取对应属性名。
- `set_name(name)`
  设置属性名。
- `get_value()`
  获取当前值，通常需要子类实现。
- `set_value(value)`
  设置当前值，通常需要子类实现。
- `get_custom_widget()`
  获取真正被包裹的 Qt widget。
- `set_custom_widget(widget)`
  设置真正的 Qt widget。
- `get_label()`
  获取控件标签。
- `set_label(label='')`
  设置控件标签。

### 内置子类
- `NodeComboBox`
  - 适合枚举值、通道选择、模式选择
  - 额外方法：`add_item()`、`add_items()`、`all_items()`、`sort_items()`、`clear()`
- `NodeLineEdit`
  - 适合字符串、资源地址、变量名、命令文本
- `NodeSpinBox`
  - 适合数字参数
- `NodeCheckBox`
  - 适合布尔开关
- `NodeButton`
  - 适合触发动作

## 6.9 菜单系统：`NodeGraphMenu`、`NodesMenu`、`NodeGraphCommand`

### `NodeGraphMenu`
- `qmenu`
  底层 `QMenu`。
- `name()`
  菜单名。
- `get_items()`
  获取添加顺序中的菜单项列表。
- `get_menu(name)`
  获取子菜单。
- `get_command(name)`
  获取命令项。
- `add_menu(name)`
  添加子菜单。
- `add_command(name, func=None, shortcut=None)`
  添加命令。
  - `func` 对 graph 菜单来说通常是 `func(graph)`
- `add_separator()`
  添加分隔线。

### `NodesMenu`
- `add_command(name, func=None, node_type=None, node_class=None, shortcut=None)`
  为特定节点类型添加右键命令。
  - `func` 通常是 `func(graph, node)`
  - `node_type` 和 `node_class` 至少给一个

### `NodeGraphCommand`
- `qaction`
  底层 `QAction`
- `slot_function`
  绑定的槽函数
- `name()`
  命令名
- `set_shortcut(shortcut=None)`
  设快捷键
- `run_command()`
  主动触发命令
- `set_enabled(state)`
  启用/禁用
- `set_hidden(hidden)`
  隐藏/显示
- `show()`
  显示
- `hide()`
  隐藏

### 菜单配置文件能力
`NodeGraph.set_context_menu_from_file()` 支持从 JSON 加载菜单。

这意味着你可以把图编辑器快捷命令配置化，例如：

- 打开图
- 保存图
- 导出代码
- 执行流程
- 自动排版

## 6.10 调色板、节点树、属性面板

### `NodesPaletteWidget`
- `NodesPaletteWidget(parent=None, node_graph=None)`
  节点调色板，支持拖拽创建节点。
- `set_category_label(category, label)`
  修改分类标签显示名。
- `tab_widget()`
  获取内部 tab 控件。
- `update()`
  刷新调色板。

### `NodesTreeWidget`
- `NodesTreeWidget(parent=None, node_graph=None)`
  树状节点浏览器。
- `set_category_label(category, label)`
  修改分类标签。
- `update()`
  重建树结构。

### `PropertiesBinWidget`
- `PropertiesBinWidget(parent=None, node_graph=None)`
  属性面板，会自动接入图信号。
- `property_changed(node_id, prop_name, prop_value)`
  属性变化信号。
- `set_limit(limit)`
  限制最多显示几个节点的属性编辑器。
- `add_node(node)`
  把节点加载到属性面板。
- `remove_node(node)`
  从属性面板移除节点。
- `lock_bin()`
  锁定/解锁属性面板。
- `clear_bin()`
  清空属性面板。
- `get_property_editor_widget(node)`
  获取某个节点当前的属性编辑器。

经验上：

- 节点内控件适合少量高频参数
- `PropertiesBinWidget` 适合完整属性编辑

## 6.11 `NodeFactory`、`NodeModel`、`PortModel`
这三个类不是日常 UI 直接调用最多的类，但理解它们有助于你真正掌握序列化和注册机制。

### `NodeFactory`
- `names`
  节点显示名到类型列表的映射。
- `aliases`
  别名到类型字符串的映射。
- `nodes`
  类型字符串到节点类的映射。
- `create_node_instance(node_type=None)`
  按类型或别名创建实例。
- `register_node(node, alias=None)`
  注册节点类。
- `clear_registered_nodes()`
  清空已注册节点。

### `NodeModel`
`NodeModel` 保存节点数据，例如：

- `type_`
- `id`
- `name`
- `color`
- `text_color`
- `disabled`
- `selected`
- `visible`
- `width`
- `height`
- `pos`
- `layout_direction`
- `inputs`
- `outputs`
- `subgraph_session`
- 自定义属性

重要方法：

- `add_property(name, value, items=None, range=None, widget_type=None, widget_tooltip=None, tab=None)`
- `set_property(name, value)`
- `get_property(name)`
- `is_custom_property(name)`
- `get_widget_type(name)`
- `get_tab_name(name)`
- `to_dict`

### `PortModel`
保存端口数据，例如：

- `type_`
- `name`
- `display_name`
- `multi_connection`
- `visible`
- `locked`
- `connected_ports`

重要属性：

- `to_dict`

## 7. 常用常量与枚举

### 布局与显示
- `LayoutDirectionEnum.HORIZONTAL`
  左到右布局
- `LayoutDirectionEnum.VERTICAL`
  上到下布局
- `ViewerEnum.GRID_DISPLAY_NONE`
  不显示网格
- `ViewerEnum.GRID_DISPLAY_DOTS`
  点状网格
- `ViewerEnum.GRID_DISPLAY_LINES`
  线状网格

### 端口与连线
- `PortTypeEnum.IN`
  输入口
- `PortTypeEnum.OUT`
  输出口
- `PipeLayoutEnum.STRAIGHT`
  直线
- `PipeLayoutEnum.CURVED`
  曲线
- `PipeLayoutEnum.ANGLE`
  折线

### 属性控件类型
`NodePropWidgetEnum` 决定属性面板里的显示控件，常用值包括：

- `HIDDEN`
- `QLABEL`
- `QLINE_EDIT`
- `QTEXT_EDIT`
- `QCOMBO_BOX`
- `QCHECK_BOX`
- `QSPIN_BOX`
- `QDOUBLESPIN_BOX`
- `COLOR_PICKER`
- `COLOR4_PICKER`
- `SLIDER`
- `DOUBLE_SLIDER`
- `FILE_OPEN`
- `FILE_SAVE`
- `VECTOR2`
- `VECTOR3`
- `VECTOR4`
- `FLOAT`
- `INT`
- `BUTTON`

## 8. 序列化数据长什么样
`NodeGraph.serialize_session()` 返回的数据核心结构是：

```python
{
    "graph": {...},
    "nodes": {
        "<node_id>": {
            "type_": "demo.instrument.SetVoltageNode",
            "name": "Set Voltage",
            "pos": [100.0, 50.0],
            "custom": {...},
        }
    },
    "connections": [
        {
            "in": ["<node_id>", "flow_in"],
            "out": ["<node_id>", "flow_out"]
        }
    ]
}
```

这意味着：

- 图文件是“结构描述”
- 要能正确加载，必须事先把同样的节点类型注册回 `NodeGraph`
- 节点类型字符串一旦改动，旧图就可能无法恢复

## 9. 用它做虚拟仪器图形化编程时的最佳实践

### 9.1 推荐节点粒度
每个节点代表一个“可复用业务动作”，不要把太多动作塞进一个节点。

推荐：

- `Open Instrument`
- `Set Output`
- `Set Voltage`
- `Measure Voltage`
- `Delay`
- `Close Instrument`

不推荐：

- 一个节点里既打开仪器又配置又采样又导出

原因很简单：

- 难以复用
- 难以调试
- 难以导出代码
- 图也会变得不透明

### 9.2 推荐端口设计
对于你的场景，建议先只做“控制流端口”：

- `flow_in`
- `flow_out`

把数据先放 `context` 字典，不要一开始就设计复杂的数据流线系统。等系统跑稳了，再升级成“控制流 + 数据流”双系统。

### 9.3 推荐导出方式
节点类里同时实现两套逻辑：

1. `execute(context)`
- 真正运行时调用

2. `emit_python()`
- 导出 Python 时调用

这样你就能保证：

- 图编辑器里的节点语义
- 实时执行语义
- Python 导出语义

三者保持一致。

## 10. 已验证的兼容性与踩坑记录

### 10.1 `NodeSpinBox` 序列化兼容坑
在本地验证的 `NodeGraphQt 0.6.44 + PySide6` 组合下，内置 `NodeSpinBox` 有一个实战坑：

- 节点里用 `add_spinbox()` 添加浮点控件
- 保存 session 后，值会以字符串形态回到节点属性
- 反序列化恢复时，底层会把这个字符串直接传给 `QDoubleSpinBox.setValue(float)`
- 从而触发类型错误

也就是说，这种组合下：

- 图可以保存
- 但重新加载时可能崩在 spinbox 恢复阶段

因此 `demo_01.py` 里对数字参数采用了更稳的做法：

- 节点显示层用 `add_text_input()`
- 执行前手工 `float(...)` 解析

这不是最华丽的方案，但在当前版本下是更稳定的闭环方案。

### 10.2 其他重要限制
- `NodeGraphQt` 没有内置执行引擎。
- 图保存依赖节点 `type_` 稳定不变。
- 节点 `id` 更适合运行时对象身份，不建议拿它当跨版本业务主键。
- Qt GUI 相关操作必须在主线程里做。
- 长耗时仪器操作不要直接阻塞 GUI 线程，后续最好接工作线程。

## 11. `demo_01.py` 的结构说明
`demo_01.py` 里核心分成四层：

1. `VirtualInstrumentAPI`
- 用虚拟仪器 API 模拟真实设备

2. `InstrumentFlowNode` 及各个子节点
- 每个节点负责自己的参数、执行逻辑、Python 导出逻辑

3. `WorkflowCompiler`
- 从图里取出可达节点
- 做拓扑排序
- 顺序执行或导出代码

4. `InstrumentWorkflowWindow`
- 搭建 `NodeGraphQt` UI
- 接入调色板、属性面板、日志面板、保存/加载/导出/执行按钮

这套结构很适合你后续替换成真实 API：

- 只需要把 `VirtualInstrumentAPI` 换成真实仪器封装
- 节点类调用真实 API
- `WorkflowCompiler` 基本不需要大改

## 12. 一条建议的学习路径
如果你准备把这个库真正用于你的项目，建议按下面顺序学：

1. 先只会用 `NodeGraph` + `BaseNode`
- 能创建图
- 能注册节点
- 能连线

2. 再掌握属性系统
- `create_property()`
- `add_text_input()`
- `add_combo_menu()`
- `PropertiesBinWidget`

3. 再掌握保存/加载
- `serialize_session()`
- `save_session()`
- `load_session()`

4. 再掌握执行器
- 拓扑排序
- 节点执行
- 上下文传递

5. 最后再做高级功能
- `GroupNode`
- 自定义菜单
- 自定义 widget
- 后台线程执行
- 数据流端口系统

## 13. 最后的判断
如果你的目标是：

- 把虚拟仪器 API 封装成节点
- 拖拽形成控制流程
- 保存为图文件
- 导出为 Python
- 执行时在控制器打印日志

那么 `NodeGraphQt` 是一个非常合适的前端图编辑基础框架。

但要记住最核心的一句：

> 它负责“画图和存图”，你负责“解释图和执行图”。

只要这个边界你始终想清楚，后面的架构就不会走偏。
