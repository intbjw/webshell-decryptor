import json
import os
import tkinter
from tkinter import *
from tkinter import filedialog
from ttkbootstrap import Style
import ttkbootstrap as ttk
from tkinter import messagebox
import threading
import time

from util.jsonReader import getJsonData
from util.pcapReader import pcapRead
import traceback
from tkinterhtml import HtmlFrame


def selectPacpPath():
    filetypes = [("pcap files", "*.pcap"), ("All files", "*")]
    file_name = filedialog.askopenfilename(title="选在一个pcap文件", filetypes=filetypes, initialdir="./")
    pcapName.set(file_name)


def show_progress_window(parent):
    progress_win = Toplevel(parent)
    progress_win.title("Progress")
    progress_win.geometry("300x100")

    # Center the progress window relative to the parent window
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()

    progress_win.geometry(f"+{parent_x + parent_width // 2 - 150}+{parent_y + parent_height // 2 - 50}")

    progress_label = ttk.Label(progress_win, text="分析中，请稍候...")
    progress_label.pack(pady=10)

    progress_bar = ttk.Progressbar(progress_win, mode='indeterminate')
    progress_bar.pack(pady=10, padx=20, fill='x')
    progress_bar.start()

    return progress_win, progress_bar


def populate_tree(tree, parent, data):
    for key, value in data.items():

        print(key, value)
        node = tree.insert(parent, 'end', text=key)
        if 'children' in value:
            populate_tree(tree, node, value['children'])


def get_item_path(tree, item):
    path = []
    while item:
        path.insert(0, tree.item(item, 'text'))
        item = tree.parent(item)
    return '/' + '/'.join(path[1:]) if len(path) > 1 else '/'


def on_tree_select(event, tree, file_browser, file_tree_data):
    file_browser.delete(*file_browser.get_children())
    selected_item = tree.selection()[0]
    item_path = get_item_path(tree, selected_item)
    print(f"Selected path: {item_path}")
    item_path = item_path if item_path == '/' else item_path + '/'
    print(file_tree_data['filelist'][item_path])
    for file in file_tree_data['filelist'][item_path]:
        print(f"{file['perm']}\t\t{file['type']}\t\t{file['size']}\t\t{file['lastModified']}\t\t{file['name']}")
        file_browser.insert('', 'end',
                            values=(file['perm'], file['type'], file['size'], file['lastModified'], file['name']))


def show_result_window(parent):
    result_win = ttk.Toplevel(parent)
    result_win.title("结果")
    result_win.geometry("800x600")
    # 读取jsonl文件
    data = getJsonData("webshell.pcap_decrypted.jsonl")

    # 创建Notebook控件
    notebook = ttk.Notebook(result_win)

    # 创建三个Frame作为tab页
    tab1 = ttk.Frame(notebook)
    # tab1中显示一个文本框，用来显示 信息获取
    html_frame = HtmlFrame(tab1, horizontal_scrollbar="auto", fontscale=1.3)
    html_frame.set_content(data['信息获取'])
    html_frame.pack(fill="both", expand=True)

    tab2 = ttk.Frame(notebook)
    tab3 = ttk.Frame(notebook)
    # 创建一个Text控件，用于显示终端样式的文本
    terminal_text = Text(tab3, wrap='word', bg='black', fg='white')
    terminal_text.pack(fill='both', expand=True)

    # 示例文本
    # Define tags with different colors
    terminal_text.tag_configure('red', foreground='red')
    terminal_text.tag_configure('green', foreground='green')
    terminal_text.tag_configure('blue', foreground='blue')

    # Insert text with different colors
    terminal_text.insert('end', '欢迎使用终端模拟器\n', 'green')
    for cmd in data['历史命令']:
        terminal_text.insert('end', f'{cmd[0]} -> ', 'green')
        terminal_text.insert('end', f'{cmd[1]}\n', 'blue')
        terminal_text.insert('end', f'{cmd[2]}\n')

    # 禁用编辑
    terminal_text.config(state='disabled')
    tab4 = ttk.Frame(notebook)

    # 将Frame添加到Notebook中
    notebook.add(tab1, text='信息获取')
    notebook.add(tab2, text='文件管理器')
    notebook.add(tab3, text='终端')
    notebook.add(tab4, text='数据库')

    # 显示Notebook
    notebook.pack(expand=True, fill='both')

    # 在第一个tab页中添加文件浏览器
    # Create a PanedWindow to split the area into two sections
    paned_window = ttk.PanedWindow(tab2, orient=HORIZONTAL)
    paned_window.pack(fill='both', expand=True)

    # Left frame for path selection
    left_frame = ttk.Frame(paned_window)
    paned_window.add(left_frame, weight=1)

    # Right frame for directory/file display
    right_frame = ttk.Frame(paned_window)
    paned_window.add(right_frame, weight=3)

    # Path selection (left frame) using Treeview
    tree = ttk.Treeview(left_frame)
    tree.pack(side='left', fill='both', expand=True)
    # 在右侧生成一个列表
    file_browser = ttk.Treeview(right_frame, columns=['c1', 'c2', 'c3', 'c4', 'c5', 'c6'], selectmode="browse",
                                show="headings")
    file_browser.column('c1', width=200, anchor='center')
    file_browser.column('c2', width=200, anchor='center')
    file_browser.column('c3', width=200, anchor='center')
    file_browser.column('c4', width=200, anchor='center')
    file_browser.column('c5', width=200, anchor='center')
    file_browser.column('c6', width=200, anchor='center')
    file_browser.heading('c1', text='权限')
    file_browser.heading('c2', text='类型')
    file_browser.heading('c3', text='文件大小')
    file_browser.heading('c4', text='最后修改时间')
    file_browser.heading('c5', text='文件名')
    # 在第6列添加一个按钮
    file_browser.heading('c6', text='Action')
    file_browser.bind("<<TreeviewSelect>>", on_tree_select)
    file_browser.pack(side='right', fill='both', expand=True)

    # file_tree_data = {'/': {}, 'children': {'root': {}, 'usr': {'children': {'local': {'children': {'tomcat': {
    #     'children': {'webapps': {'children': {'ofcms-admin': {'children': {
    #         'WEB-INF': {'children': {'classes': {'children': {'conf': {'children': {'db.properties': {}}}}}}}}}}}}}}}}},
    #                                         'var': {'children': {'lib': {'children': {
    #                                             'mysql': {'children': {'secret': {'children': {'aptupdate': {}}}}}}}}}}}
    file_tree_data = data['文件操作']

    root_node = tree.insert('', 'end', text='/', open=True)
    populate_tree(tree, root_node, file_tree_data['filetree']['children'])

    # Add the PanedWindow to tab2
    notebook.add(tab2, text='文件管理器')
    # Bind the selection event to the Treeview
    tree.bind("<<TreeviewSelect>>", lambda event: on_tree_select(event, tree, file_browser, file_tree_data))


def startAnalysis():
    def run_analysis():
        try:
            progress_win, progress_bar = show_progress_window(win)
            time.sleep(1)  # Simulate analysis time
            pcapRead(pcapName.get(), url_str.get(), key_str.get(), script_type.get(), 'aes')
            progress_bar.stop()
            progress_win.destroy()
            messagebox.showinfo("完成", "分析完成")
            # 生成一个子的窗口
            win.after(0, show_result_window, win)


        except:
            progress_win.destroy()
            # 打印错误信息
            traceback.print_exc()

            exit(1)

    threading.Thread(target=run_analysis).start()


if __name__ == "__main__":
    # 创建一个窗口
    win = ttk.Window(themename="litera")
    # 设置标题
    win.title("webshell流量分析")

    # 获取屏幕宽度和高度
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    # 计算窗口位置
    window_width = 600
    window_height = 300
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)

    # 设置窗口大小和位置
    win.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

    # 创建一个文本标签
    pcap_txt = ttk.Label(win, text="pcap文件路径:")
    pcap_txt.grid(row=0, column=0, padx=10, pady=10, sticky="w")
    pcapName = ttk.StringVar()
    pcapFile = ttk.Entry(win, textvariable=pcapName)
    pcapFile.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
    select_btn = ttk.Button(win, text="选择", command=selectPacpPath)
    select_btn.grid(row=0, column=2, padx=10, pady=10)

    url_txt = ttk.Label(win, text="url:")
    url_txt.grid(row=1, column=0, padx=10, pady=10, sticky="w")
    url_str = ttk.StringVar()
    url = ttk.Entry(win, textvariable=url_str)
    url.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

    key_txt = ttk.Label(win, text="key:")
    key_txt.grid(row=2, column=0, padx=10, pady=10, sticky="w")
    key_str = ttk.StringVar()
    key = ttk.Entry(win, textvariable=key_str)
    key.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

    # 脚本类型 下拉框
    script_type_txt = ttk.Label(win, text="脚本类型:")
    script_type_txt.grid(row=3, column=0, padx=10, pady=10, sticky="w")
    script_type = ttk.Combobox(win, values=["php", "asp", "aspx", "jsp"])
    script_type.grid(row=3, column=1, padx=10, pady=10)

    start_btn = ttk.Button(win, text="开始分析", command=startAnalysis)
    start_btn.grid(row=4, column=1, padx=10, pady=10)

    # Configure grid column weights
    win.grid_columnconfigure(1, weight=1)

    # 展示窗口
    win.mainloop()
