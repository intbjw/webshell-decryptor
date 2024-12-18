import tkinter
from tkinter import ttk  # 导入内部包


def tree_view_click(*args):
    """根据选中行，弹出对话框，修改对应通信终端的配置"""
    print(tree.selection())  # 选定的iid组成的元组
    if len(tree.selection()) == 0:  # 元组的长度
        return
    str_tree_item = tree.selection()[0]  # iid
    values = tree.item(str_tree_item, option='values')  # 取值
    print(values)

    tree.item(tree.selection()[0], values=["a", "b"])  # 修改
    # 删除 全部 treeview 信息行
    for item in tree.get_children():  # used self.tree instead
        print(item)
        # tree.delete(item)


win = tkinter.Tk()
tree = ttk.Treeview(win, columns=('c1', 'c2'), selectmode="browse", show="tree headings")
tree.column('c1', anchor='center')
tree.column('c2', anchor='center')
# 参数:parent, index, iid=None, **kw (父节点，插入的位置，id，显示出的文本)
myidx = tree.insert("", 0, "中国", text="中国China", values=("1", 1))  # ""表示父节点是根
myidx1 = tree.insert(myidx, 0, "广东", text="中国广东", values=("2", 1))  # text表示显示出的文本，values是隐藏的值
myidx2 = tree.insert(myidx, 1, "江苏", text="中国江苏", values=("3", 1))
myidy = tree.insert("", 1, "美国", text="美国USA", values=("4", 2))
myidy1 = tree.insert(myidy, 0, "加州", text="美国加州", values=("5", 2))
# tree.delete("加州")
tree.bind('<ButtonRelease-1>', tree_view_click)  # 鼠标左键松开事件

tree.pack()
win.mainloop()
