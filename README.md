# 使用说明

## 创建房间和KP/DM

目前只能由管理员手动创建房间并指定DP/DM。请在注册后告诉我你的账号，我会帮你创建房间和KP/DM账号。

## 进入房间

在大厅输入房间名称即可进入房间。**注意：**目前房间**没有密码**，请不要将你的房间名随意告诉他人。

## 导入角色

* 本站点目前不支持建卡。请在风羽大大的[网站](https://hina.moe/coc/)进行建卡，之后在[这里](https://hina.moe/coc/card-gallery.php)找到你的人物卡，点击*txt卡*并将内容粘贴到导入角色的输入框中。

* 你可能会遇到显示乱码的问题，请将浏览器编码调整为UTF-8或将页面保存为txt后用记事本打开。

* 导入同名角色会更新原有人物卡。可以使用这种方法更新数值。

## 开始跑团

* 整个房间面板由两部分组成，分别是 **角色面板** 和 **聊天面板**。

* 角色面板：

  * 列出了你创建的所有角色（KP/DM可以看到房间中的所有角色）；

  * 点击角色名字可以查看角色卡。此时在右边的聊天面板中将会以**当前选中角色**进行发言/掷骰。因此在发言和掷骰前请务必**注意选好角色**（尤其是KP/DM）；

  * 角色卡中，点击某个数值属性，可以将右边聊天面板的掷骰的检定内容设置为该属性。如果你在属性右边的框中填写了加值或减值，这个值也会反映在检定内容中（需要填写后重新点击）；

  * 还可以拖拽常用的检定属性到列表中靠前的位置

* 聊天面板

  * 聊天窗口每1秒刷新一次；

  * 在发言和掷骰前请务必**注意选好角色**（尤其是KP/DM）；

  * 掷骰语法为`<骰子> +|- <骰子>...`
    * 其中，`<骰子>`可以是一个整数，或者是形如`xdy`的骰子指令，`x`为1时可以省略；
    * 例子：`d100+3d6-5`；

  * 检定语法为`{c:角色名}{v:属性值}检定项目`，只填检定项目时会尝试从当前角色的属性中查找项目并自动填写；

  * 要求掷骰(TODO)：DM/KP专用，发信息要求当前角色对检定项目掷骰

  * 快捷掷骰(TODO)

## 意见反馈

请在GitHub上[提出issue](https://github.com/jffifa/trpg/issues)，或直接向我的QQ反馈。
