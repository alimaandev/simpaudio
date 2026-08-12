import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as ttk

from ssml_parser import SSMLNode, ssml_to_tree


class SSMLEditor(tk.Toplevel):
    def __init__(self, parent, initial_text="", callback=None):
        super().__init__(parent)
        self.callback = callback
        self.title("SSML Editor")
        self.geometry("700x550")
        self.minsize(500, 400)

        self.transient(parent)
        self.grab_set()

        self.root_node = SSMLNode("root")
        self.root_node.children.append(SSMLNode("text", initial_text or "Enter text here..."))

        self._build_ui()
        self._refresh_tree()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)

        self._create_toolbar()
        self._create_tree_area()
        self._create_properties_area()

    def _create_toolbar(self):
        frame = ttk.Frame(self, padding=(8, 4))
        frame.grid(row=0, column=0, sticky="ew")

        ttk.Label(frame, text="Insert:").pack(side="left", padx=(0, 4))
        ttk.Button(frame, text="Text", command=lambda: self._insert_node("text")).pack(side="left", padx=2)
        ttk.Button(frame, text="Break", command=lambda: self._insert_node("break")).pack(side="left", padx=2)
        ttk.Button(frame, text="Prosody", command=lambda: self._insert_node("prosody")).pack(side="left", padx=2)
        ttk.Button(frame, text="Emphasis", command=lambda: self._insert_node("emphasis")).pack(side="left", padx=2)
        ttk.Button(frame, text="Say-as", command=lambda: self._insert_node("say-as")).pack(side="left", padx=2)
        ttk.Button(frame, text="Paragraph", command=lambda: self._insert_node("p")).pack(side="left", padx=2)
        ttk.Separator(frame, orient="vertical").pack(side="left", padx=8, fill="y")
        ttk.Button(frame, text="Delete", command=self._delete_selected).pack(side="left", padx=2)

    def _create_tree_area(self):
        frame = ttk.LabelFrame(self, text="SSML Tree", padding=(4, 4))
        frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 4))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(frame, columns=("type", "detail"), show="tree headings", height=12)
        self.tree.heading("#0", text="Node")
        self.tree.heading("type", text="Type")
        self.tree.heading("detail", text="Detail")
        self.tree.column("#0", width=30)
        self.tree.column("type", width=80)
        self.tree.column("detail", width=450)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _create_properties_area(self):
        frame = ttk.LabelFrame(self, text="Properties", padding=(8, 4))
        frame.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        frame.columnconfigure(1, weight=1)

        self.props_frame = frame
        self._props_widgets = []

        ttk.Label(frame, text="Select a node to edit properties.").grid(
            row=0, column=0, columnspan=2, pady=4
        )

        self._create_action_buttons(frame)

    def _create_action_buttons(self, frame):
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 8))
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        ttk.Button(btn_frame, text="Save & Close", command=self._save_and_close).grid(
            row=0, column=0, padx=(0, 4), sticky="e"
        )
        ttk.Button(btn_frame, text="Cancel", command=self._on_close).grid(
            row=0, column=1, padx=(4, 0), sticky="w"
        )

    def _refresh_tree(self, selected_id=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._populate_tree("", self.root_node)
        if selected_id and self.tree.exists(selected_id):
            self.tree.selection_set(selected_id)
            self.tree.focus(selected_id)

    def _populate_tree(self, parent_id: str, node: SSMLNode):
        detail = self._node_detail(node)
        node_id = self.tree.insert(parent_id, "end", text="", values=(node.tag, detail), open=True)
        for child in node.children:
            self._populate_tree(node_id, child)
        node._tree_id = node_id

    def _node_detail(self, node: SSMLNode) -> str:
        if node.tag == "text":
            return (node.text or "")[:60]
        elif node.tag == "break":
            return f'time="{node.attrs.get("time", "500ms")}"'
        elif node.tag == "prosody":
            parts = [f'{k}="{v}"' for k, v in node.attrs.items()]
            return ", ".join(parts) if parts else "(default)"
        elif node.tag == "emphasis":
            return f'level="{node.attrs.get("level", "strong")}"'
        elif node.tag == "say-as":
            return f'interpret-as="{node.attrs.get("interpret-as", "characters")}"'
        elif node.tag == "p":
            return ""
        return ""

    def _find_node_by_id(self, node: SSMLNode, tree_id: str) -> SSMLNode:
        if getattr(node, "_tree_id", None) == tree_id:
            return node
        for child in node.children:
            result = self._find_node_by_id(child, tree_id)
            if result:
                return result
        return None

    def _find_parent(self, node: SSMLNode, target: SSMLNode) -> SSMLNode:
        if target in node.children:
            return node
        for child in node.children:
            result = self._find_parent(child, target)
            if result:
                return result
        return None

    def _on_select(self, event):
        for w in self._props_widgets:
            w.destroy()
        self._props_widgets.clear()

        selected = self.tree.selection()
        if not selected:
            return
        tree_id = selected[0]
        node = self._find_node_by_id(self.root_node, tree_id)
        if node is None:
            return

        row = 0
        if node.tag == "text":
            tk.Label(self.props_frame, text="Text:").grid(row=row, column=0, padx=(0, 4), pady=2, sticky="w")
            var = tk.StringVar(value=node.text or "")
            entry = ttk.Entry(self.props_frame, textvariable=var, width=50)
            entry.grid(row=row, column=1, pady=2, sticky="ew")
            def on_change(var=var, n=node):
                n.text = var.get()
                self._refresh_tree(selected[0])
            var.trace_add("write", lambda *_: on_change())
            self._props_widgets.extend([entry])

        elif node.tag == "break":
            tk.Label(self.props_frame, text="Time (e.g. 500ms, 1s):").grid(
                row=row, column=0, padx=(0, 4), pady=2, sticky="w"
            )
            var = tk.StringVar(value=node.attrs.get("time", "500ms"))
            entry = ttk.Entry(self.props_frame, textvariable=var, width=20)
            entry.grid(row=row, column=1, pady=2, sticky="w")
            def on_change(var=var, n=node):
                n.attrs["time"] = var.get()
                self._refresh_tree(selected[0])
            var.trace_add("write", lambda *_: on_change())
            self._props_widgets.append(entry)

        elif node.tag == "prosody":
            fields = [("Rate (0.5-2.0)", "rate"), ("Pitch (0.5-2.0)", "pitch"), ("Volume (0-2.0)", "volume")]
            for label, key in fields:
                tk.Label(self.props_frame, text=label+":").grid(
                    row=row, column=0, padx=(0, 4), pady=2, sticky="w"
                )
                var = tk.StringVar(value=node.attrs.get(key, "1.0"))
                entry = ttk.Entry(self.props_frame, textvariable=var, width=20)
                entry.grid(row=row, column=1, pady=2, sticky="w")
                def on_change(var=var, k=key, n=node):
                    n.attrs[k] = var.get()
                    self._refresh_tree(selected[0])
                var.trace_add("write", lambda *_: on_change())
                self._props_widgets.append(entry)
                row += 1

        elif node.tag == "emphasis":
            tk.Label(self.props_frame, text="Level:").grid(
                row=row, column=0, padx=(0, 4), pady=2, sticky="w"
            )
            var = tk.StringVar(value=node.attrs.get("level", "strong"))
            combo = ttk.Combobox(self.props_frame, textvariable=var,
                                 values=["strong", "moderate", "reduced"], state="readonly", width=16)
            combo.grid(row=row, column=1, pady=2, sticky="w")
            def on_change(var=var, n=node):
                n.attrs["level"] = var.get()
                self._refresh_tree(selected[0])
            var.trace_add("write", lambda *_: on_change())
            self._props_widgets.append(combo)

        elif node.tag == "say-as":
            tk.Label(self.props_frame, text="Interpret as:").grid(
                row=row, column=0, padx=(0, 4), pady=2, sticky="w"
            )
            var = tk.StringVar(value=node.attrs.get("interpret-as", "characters"))
            combo = ttk.Combobox(self.props_frame, textvariable=var,
                                 values=["characters", "date", "time", "telephone"],
                                 state="readonly", width=16)
            combo.grid(row=row, column=1, pady=2, sticky="w")
            def on_change(var=var, n=node):
                n.attrs["interpret-as"] = var.get()
                self._refresh_tree(selected[0])
            var.trace_add("write", lambda *_: on_change())
            self._props_widgets.append(combo)

    def _insert_node(self, tag: str):
        selected = self.tree.selection()
        parent_node = self.root_node
        if selected:
            parent = self._find_node_by_id(self.root_node, selected[0])
            if parent:
                parent_node = parent

        if tag == "text":
            new_node = SSMLNode("text", "new text")
        elif tag == "break":
            new_node = SSMLNode("break", attrs={"time": "500ms"})
        elif tag == "prosody":
            new_node = SSMLNode("prosody", attrs={"rate": "1.0", "pitch": "1.0", "volume": "1.0"})
            new_node.children.append(SSMLNode("text", "text"))
        elif tag == "emphasis":
            new_node = SSMLNode("emphasis", attrs={"level": "strong"})
            new_node.children.append(SSMLNode("text", "text"))
        elif tag == "say-as":
            new_node = SSMLNode("say-as", attrs={"interpret-as": "characters"})
            new_node.children.append(SSMLNode("text", "text"))
        elif tag == "p":
            new_node = SSMLNode("p")
            new_node.children.append(SSMLNode("text", "paragraph text"))
        else:
            return

        parent_node.children.append(new_node)
        self._refresh_tree()
        if hasattr(new_node, "_tree_id") and self.tree.exists(new_node._tree_id):
            self.tree.selection_set(new_node._tree_id)
            self.tree.focus(new_node._tree_id)

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        tree_id = selected[0]
        node = self._find_node_by_id(self.root_node, tree_id)
        if node is None or node == self.root_node:
            return
        parent = self._find_parent(self.root_node, node)
        if parent and node in parent.children:
            parent.children.remove(node)
        self._refresh_tree()

    def _save_and_close(self):
        ssml = self.root_node.to_ssml()
        if self.callback:
            self.callback(ssml)
        self.destroy()

    def _on_close(self):
        self.destroy()