# dachuang项目介绍
本项目用于保存大创期间的源代码，内容部分包括气象数据的收集与整理，机器学习模型的选取、训练等内容。

<span style="color:red">WARNING: This repository is deprecated, the latest one can be visited by https://github.com/leosssssss/TC-predict-model</span>

## 本脚本的功能
## 脚本的使用指南
### 运行脚本（OperationScript）的使用方法介绍
1. 本脚本通过读取脚本运行控制文件工作，请按照控制文件的编写格式正确书写[控制文件](#ctrfile)，以免发生错误。
2. 本脚本的功能为读入气象数据文件、降水数据文件、台风数据文件等预测相关的资料在本机的地址，{需要施工}
#### <a id="ctrfile"></a>控制文件的编写格式
 1. 控制文件格式为文本文档（.txt），编码格式为utf-8。
 2. 控制代码按行读取，请将每个控制代码的内容保持在一行内，否则将引起报错。
 3. 台风文件所在地址的读入方法为"dataset typhoon fileAdress"。其中dataset关键字表示本行读入的是数据文件位置；typhoon关键字表示读入的数据文件是台风数据；fileAdress为台风数据文件所在的绝对路径，结束在文件夹处，例：'E:\Example'，其中Examle为容纳台风数据文件的文件夹名。
 4. 降水文件所在地址的读入方法为"dataset precipitation fileAdress"。其中dataset关键字表示本行读入的是数据文件位置；precipitation关键字表示读入的数据文件是降水数据；fileAdress为降水数据文件所在的绝对路径，结束在文件夹处，例：'E:\Example'，其中Examle为容纳降水数据文件的文件夹名。
 5. ERA5气象文件所在地址的读入方法为"dataset ERA fileAdress"。其中dataset关键字表示本行读入的是数据文件位置；ERA关键字表示读入的数据文件是降水数据；fileAdress为降水数据文件所在的绝对路径，结束在文件夹处，例：'E:\Example'，其中Examle为容纳RERA5数据文件的文件夹名。
