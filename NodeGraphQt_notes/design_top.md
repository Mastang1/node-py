
## 概述 
该应用是实现一个基于虚拟仪器的自动化测试系统。实现自定义/模块化(基于class实现仪器模块)的仪器API接口，实现仪器API到可视化NODE的映射，把pythonic的仪器API通过NodeGraphQt转化为NODE，实现所见即所得的可视化仪器测试流程开发，实现流程到API调用流程python脚本代码的生成/存储，实现流程到json的存储/加载/二次修改，该json被称作test case flow，或者test case，其本质是该Zion规划测试系统可以识别/处理的一个NODE FLOW；

## 功能 按照该系统的工作流程顺序，其功能包括：
1. 仪器API发现/加载功能，可以通过某种方式（类似某些单测框架的用例发现）发现API，并加载到可用仪器/API的运行时json文件中，在系统打开仪器列表时候展示在合适的控件中；
2. 通用API实现。一些常用的循环/条件判断/返回/延时等API的实现；
3. 在UI中实现从1中的控件中拖拽指定API到NodeGraphQt的画布，生成NODE功能，这个生成NODE功能是个核心功能；
4. 连接3中的NODE形成FLOW，需要可以通过UI中的RUN按钮执行流程的运行，实现各个NODE中的API的调用并把stdout/stderr信息展示在UI的日志窗口中
5. 