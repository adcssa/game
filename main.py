from __future__ import annotations

import random
import re
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import winsound

from story_data import INTRO_TEXT, NODES, STATS, total_story_text


APP_TITLE = "雾港回声"
WINDOW_SIZE = "1280x820"
MUSIC_FILE = "bgm.wav"

GLOBAL_BACKGROUND = (
    "七年前，雾港钟塔发生爆炸，林澈的父亲林岐舟死在其中，官方将其定性为锅炉事故。"
    "\n如今，城里不断出现“断忆者”，他们会突然失去一段记忆，像是有人偷走了他们的昨天。"
    "\n林澈因旧友沈砚的一封急信重返雾港，开始追查钟塔旧案、晨星引擎与失忆事件之间的关系。"
)

STORY_TIMELINE = (
    "主线脉络：\n"
    "1. 归乡：林澈回到雾港，在线索中重新接触父亲旧案。\n"
    "2. 调查：列车、报社、医院、地下剧场的线索逐步汇合。\n"
    "3. 真相：晨星引擎被揭露为可操纵记忆的装置，父亲当年试图阻止它。\n"
    "4. 抉择：钟塔核心阶段，你必须决定改造、摧毁，或公开这一切。"
)

NODE_BRIEFS = {
    "prologue": "开场导读：你刚回到雾港，知道父亲旧案可能另有隐情，但还不知道幕后全貌。",
    "listen_door": "线索推进：你已经偷听到关键名词“晨星引擎”，并第一次确认父亲之死与它有关。",
    "push_door": "线索推进：你主动撞破现场，已经和运送神秘装置的人正面接触。",
    "note_clues": "线索推进：你先压住冲动，准备带着关键词下车，转入更稳妥的调查。",
    "meet_shen": "人物补充：沈砚是你最信任的旧友，也是调查记者，会成为你的重要情报来源。",
    "underground_theater": "地点补充：地下剧场是旧案的重要节点，父亲与乔曼都在这里留下了关键信息。",
    "clocktower_plan": "局势升级：你已经进入最终准备阶段，接下来要决定面对晨星引擎的方式。",
    "clocktower_core": "最终对峙：你已进入钟塔核心机房，所有人物、真相与选择都在此收束。",
}


def resource_path(relative: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return Path(base) / relative


def clamp(value: int, low: int = 0, high: int = 10) -> int:
    return max(low, min(high, value))


def format_story_text(text: str) -> str:
    normalized = re.sub(r"\s+", "", text)
    sentences = re.split(r"(?<=[。！？])", normalized)
    sentences = [item.strip() for item in sentences if item.strip()]

    paragraphs: list[str] = []
    current: list[str] = []
    current_len = 0

    for sentence in sentences:
        current.append(sentence)
        current_len += len(sentence)
        if len(current) >= 2 or current_len >= 56:
            paragraphs.append("".join(current))
            current = []
            current_len = 0

    if current:
        paragraphs.append("".join(current))

    return "\n".join(paragraphs)


class AdventureGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.minsize(1160, 760)
        self.root.configure(bg="#071119")

        self.current_node = "prologue"
        self.state: dict[str, object] = {}
        self.history: list[str] = []
        self.music_enabled = True
        self.choice_buttons: list[tk.Button] = []
        self.particles: list[dict[str, float | int]] = []

        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg="#071119")
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.screen = tk.Frame(self.root, bg="#102330")
        self.screen.place(relx=0.04, rely=0.05, relwidth=0.92, relheight=0.9)

        self._reset_state()
        self._seed_particles()
        self._draw_background()
        self._play_music()
        self.show_menu()

    def _reset_state(self) -> None:
        self.current_node = "prologue"
        self.state = {
            "courage": 0,
            "insight": 0,
            "trust": 0,
            "goal": "",
            "shen_ally": False,
            "qiaoman_ally": False,
            "lugeng_witness": False,
        }
        self.history.clear()

    def _seed_particles(self) -> None:
        for _ in range(40):
            self.particles.append(
                {
                    "x": random.randint(0, 1400),
                    "y": random.randint(0, 900),
                    "r": random.randint(1, 3),
                    "speed": random.uniform(0.2, 0.9),
                }
            )
        self._animate_particles()

    def _animate_particles(self) -> None:
        for particle in self.particles:
            particle["y"] = float(particle["y"]) + float(particle["speed"])
            if particle["y"] > max(self.root.winfo_height(), 820) + 20:
                particle["y"] = -10
                particle["x"] = random.randint(0, max(self.root.winfo_width(), 1280))
        self._draw_background()
        self.root.after(90, self._animate_particles)

    def _draw_background(self) -> None:
        width = max(self.root.winfo_width(), 1280)
        height = max(self.root.winfo_height(), 820)
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, width, height, fill="#071119", outline="")
        self.canvas.create_oval(-220, -160, width * 0.45, height * 0.50, fill="#123247", outline="")
        self.canvas.create_oval(width * 0.42, -120, width * 1.08, height * 0.52, fill="#1d4b68", outline="")
        self.canvas.create_oval(width * 0.75, height * 0.18, width * 1.18, height * 0.94, fill="#0d2431", outline="")
        self.canvas.create_rectangle(0, height * 0.80, width, height, fill="#050a0f", outline="")
        for particle in self.particles:
            x = float(particle["x"])
            y = float(particle["y"])
            r = int(particle["r"])
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#d7c18a", outline="")

    def _play_music(self) -> None:
        music_path = resource_path(MUSIC_FILE)
        if self.music_enabled and music_path.exists():
            winsound.PlaySound(
                str(music_path),
                winsound.SND_ASYNC | winsound.SND_FILENAME | winsound.SND_LOOP,
            )

    def toggle_music(self) -> None:
        self.music_enabled = not self.music_enabled
        label = "音乐：开" if self.music_enabled else "音乐：关"
        if hasattr(self, "music_button"):
            self.music_button.configure(text=label)
        if hasattr(self, "menu_music_button"):
            self.menu_music_button.configure(text=label)
        if self.music_enabled:
            self._play_music()
        else:
            winsound.PlaySound(None, winsound.SND_PURGE)

    def clear_screen(self) -> None:
        for child in self.screen.winfo_children():
            child.destroy()

    def show_menu(self) -> None:
        self.clear_screen()

        menu_frame = tk.Frame(self.screen, bg="#102330")
        menu_frame.pack(fill="both", expand=True)

        top_bar = tk.Frame(menu_frame, bg="#102330")
        top_bar.pack(fill="x", padx=30, pady=(24, 0))

        self.menu_music_button = tk.Button(
            top_bar,
            text="音乐：开" if self.music_enabled else "音乐：关",
            command=self.toggle_music,
            font=("Microsoft YaHei UI", 11),
            bg="#1a4c63",
            fg="#f1f7fb",
            activebackground="#236987",
            activeforeground="#ffffff",
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
        )
        self.menu_music_button.pack(side="right")

        main_panel = tk.Frame(menu_frame, bg="#102330")
        main_panel.pack(fill="both", expand=True, padx=30, pady=26)
        main_panel.grid_columnconfigure(0, weight=3)
        main_panel.grid_columnconfigure(1, weight=2)
        main_panel.grid_rowconfigure(0, weight=1)

        hero = tk.Frame(main_panel, bg="#0d1e29")
        hero.grid(row=0, column=0, sticky="nsew", padx=(0, 18))

        tk.Label(
            hero,
            text=APP_TITLE,
            font=("Microsoft YaHei UI", 34, "bold"),
            fg="#f4e7c5",
            bg="#0d1e29",
        ).pack(anchor="w", padx=28, pady=(34, 12))

        tk.Label(
            hero,
            text="蒸汽悬疑文字冒险",
            font=("Microsoft YaHei UI", 15),
            fg="#8fc6d3",
            bg="#0d1e29",
        ).pack(anchor="w", padx=28)

        intro_text = (
            "七年前，钟塔爆炸夺走了林澈的父亲。\n"
            "七年后，雾港开始出现被偷走昨天的人。\n\n"
            "你将扮演归乡的钟表修复师，在列车、剧场、医院与钟塔之间做出选择。\n"
            "每个决定都会影响胆识、洞察、人心，以及最终结局。"
        )
        tk.Label(
            hero,
            text=intro_text,
            justify="left",
            font=("Microsoft YaHei UI", 14),
            fg="#d5e5eb",
            bg="#0d1e29",
            wraplength=620,
        ).pack(anchor="w", padx=28, pady=(26, 18))

        feature_box = tk.Frame(hero, bg="#153243")
        feature_box.pack(fill="x", padx=28, pady=(0, 28))
        for text in (
            f"原创剧情：约 {total_story_text()} 字",
            "多分支推进：4 个主要结局",
            "阅读优化：更紧凑的分段排版与节点导读",
            "交互优化：选项区支持滚动并可同时显示多个按钮",
        ):
            tk.Label(
                feature_box,
                text=text,
                anchor="w",
                font=("Microsoft YaHei UI", 12),
                fg="#eef7fa",
                bg="#153243",
            ).pack(fill="x", padx=18, pady=10)

        side = tk.Frame(main_panel, bg="#112835")
        side.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            side,
            text="主菜单",
            font=("Microsoft YaHei UI", 24, "bold"),
            fg="#f4e7c5",
            bg="#112835",
        ).pack(anchor="w", padx=26, pady=(40, 20))

        self._menu_button(side, "开始游戏", self.start_game, primary=True).pack(fill="x", padx=26, pady=(0, 14))
        self._menu_button(side, "查看世界观", self.show_story_intro).pack(fill="x", padx=26, pady=(0, 14))
        self._menu_button(side, "退出游戏", self.root.destroy).pack(fill="x", padx=26, pady=(0, 14))

        tk.Label(
            side,
            text=(
                "操作说明：\n"
                "1. 点击“开始游戏”进入剧情。\n"
                "2. 标题下方会显示当前节点导读。\n"
                "3. 底部“可选行动”区域可滚动，能一次看到多个选项。"
            ),
            justify="left",
            font=("Microsoft YaHei UI", 11),
            fg="#c6dde4",
            bg="#112835",
            wraplength=300,
        ).pack(anchor="w", padx=26, pady=(28, 0))

    def _menu_button(self, parent: tk.Widget, text: str, command, primary: bool = False) -> tk.Button:
        bg = "#825b25" if primary else "#17435a"
        hover = "#a97731" if primary else "#236987"
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Microsoft YaHei UI", 13, "bold" if primary else "normal"),
            bg=bg,
            fg="#f7fbff",
            activebackground=hover,
            activeforeground="#ffffff",
            relief="flat",
            padx=18,
            pady=14,
            cursor="hand2",
        )
        button.bind("<Enter>", lambda _event, b=button, color=hover: b.configure(bg=color))
        button.bind("<Leave>", lambda _event, b=button, color=bg: b.configure(bg=color))
        return button

    def show_story_intro(self) -> None:
        messagebox.showinfo(APP_TITLE, GLOBAL_BACKGROUND + "\n\n" + STORY_TIMELINE)

    def start_game(self) -> None:
        self._reset_state()
        self.clear_screen()

        self.game_frame = tk.Frame(self.screen, bg="#102330")
        self.game_frame.pack(fill="both", expand=True)

        self._build_game_ui()
        self.render_current_node()

    def _build_game_ui(self) -> None:
        header = tk.Frame(self.game_frame, bg="#102330")
        header.pack(fill="x", padx=24, pady=(20, 12))

        tk.Label(
            header,
            text=APP_TITLE,
            font=("Microsoft YaHei UI", 28, "bold"),
            fg="#f4e7c5",
            bg="#102330",
        ).pack(side="left")

        tk.Label(
            header,
            text="蒸汽悬疑文字冒险",
            font=("Microsoft YaHei UI", 12),
            fg="#8fc6d3",
            bg="#102330",
        ).pack(side="left", padx=(16, 0), pady=(10, 0))

        self.music_button = tk.Button(
            header,
            text="音乐：开" if self.music_enabled else "音乐：关",
            command=self.toggle_music,
            font=("Microsoft YaHei UI", 11),
            bg="#1a4c63",
            fg="#f1f7fb",
            activebackground="#236987",
            activeforeground="#ffffff",
            relief="flat",
            padx=14,
            pady=8,
            cursor="hand2",
        )
        self.music_button.pack(side="right")

        tk.Button(
            header,
            text="返回菜单",
            command=self.show_menu,
            font=("Microsoft YaHei UI", 11),
            bg="#28424f",
            fg="#f1f7fb",
            activebackground="#3a6274",
            activeforeground="#ffffff",
            relief="flat",
            padx=14,
            pady=8,
            cursor="hand2",
        ).pack(side="right", padx=(0, 12))

        tk.Button(
            header,
            text="重新开始",
            command=self.restart_game,
            font=("Microsoft YaHei UI", 11),
            bg="#28424f",
            fg="#f1f7fb",
            activebackground="#3a6274",
            activeforeground="#ffffff",
            relief="flat",
            padx=14,
            pady=8,
            cursor="hand2",
        ).pack(side="right", padx=(0, 12))

        content = tk.Frame(self.game_frame, bg="#102330")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        content.grid_columnconfigure(0, weight=4)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self.left_panel = tk.Frame(content, bg="#0d1e29")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(2, weight=1)

        self.right_panel = tk.Frame(content, bg="#112835", width=310)
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self.right_panel.grid_propagate(False)

        self.chapter_label = tk.Label(
            self.left_panel,
            text="",
            font=("Microsoft YaHei UI", 20, "bold"),
            fg="#f5d78f",
            bg="#0d1e29",
            anchor="w",
        )
        self.chapter_label.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 8))

        self.summary_label = tk.Label(
            self.left_panel,
            text="",
            justify="left",
            wraplength=840,
            font=("Microsoft YaHei UI", 11),
            fg="#c9dde4",
            bg="#143241",
            anchor="w",
            padx=14,
            pady=10,
        )
        self.summary_label.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))

        main_area = tk.Frame(self.left_panel, bg="#0d1e29")
        main_area.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 18))
        main_area.grid_columnconfigure(0, weight=1)
        main_area.grid_rowconfigure(0, weight=3, minsize=330)
        main_area.grid_rowconfigure(1, weight=2, minsize=250)

        story_box = tk.Frame(main_area, bg="#0d1e29")
        story_box.grid(row=0, column=0, sticky="nsew")
        story_box.grid_columnconfigure(0, weight=1)
        story_box.grid_rowconfigure(0, weight=1)

        self.story_text = tk.Text(
            story_box,
            wrap="word",
            font=("Microsoft YaHei UI", 13),
            bg="#102733",
            fg="#edf4f8",
            relief="flat",
            padx=18,
            pady=14,
            spacing1=0,
            spacing2=3,
            spacing3=6,
            insertbackground="#ffffff",
        )
        self.story_text.grid(row=0, column=0, sticky="nsew")
        self.story_text.configure(state="disabled")

        story_scrollbar = tk.Scrollbar(story_box, orient="vertical", command=self.story_text.yview)
        story_scrollbar.grid(row=0, column=1, sticky="ns")
        self.story_text.configure(yscrollcommand=story_scrollbar.set)

        self.choice_box = tk.Frame(main_area, bg="#0f2330")
        self.choice_box.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        self.choice_box.grid_columnconfigure(0, weight=1)
        self.choice_box.grid_rowconfigure(1, weight=1)

        tk.Label(
            self.choice_box,
            text="可选行动",
            font=("Microsoft YaHei UI", 13, "bold"),
            fg="#f4e7c5",
            bg="#0f2330",
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 8))

        choice_scroll_area = tk.Frame(self.choice_box, bg="#0f2330")
        choice_scroll_area.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 12))
        choice_scroll_area.grid_columnconfigure(0, weight=1)
        choice_scroll_area.grid_rowconfigure(0, weight=1)

        self.choice_canvas = tk.Canvas(choice_scroll_area, bg="#0f2330", highlightthickness=0, bd=0)
        self.choice_canvas.grid(row=0, column=0, sticky="nsew")

        self.choice_scrollbar = tk.Scrollbar(choice_scroll_area, orient="vertical", command=self.choice_canvas.yview)
        self.choice_scrollbar.grid(row=0, column=1, sticky="ns")
        self.choice_canvas.configure(yscrollcommand=self.choice_scrollbar.set)

        self.choice_frame = tk.Frame(self.choice_canvas, bg="#0f2330")
        self.choice_window = self.choice_canvas.create_window((0, 0), window=self.choice_frame, anchor="nw")

        self.choice_frame.bind("<Configure>", self._update_choice_scrollregion)
        self.choice_canvas.bind("<Configure>", self._resize_choice_window)
        self.choice_canvas.bind("<Enter>", self._bind_choice_mousewheel)
        self.choice_canvas.bind("<Leave>", self._unbind_choice_mousewheel)
        self.choice_frame.bind("<Enter>", self._bind_choice_mousewheel)
        self.choice_frame.bind("<Leave>", self._unbind_choice_mousewheel)

        self._build_side_panel()

    def _build_side_panel(self) -> None:
        tk.Label(
            self.right_panel,
            text="调查档案",
            font=("Microsoft YaHei UI", 18, "bold"),
            fg="#f4e7c5",
            bg="#112835",
        ).pack(anchor="w", padx=18, pady=(18, 8))

        tk.Label(
            self.right_panel,
            text=GLOBAL_BACKGROUND,
            justify="left",
            wraplength=260,
            font=("Microsoft YaHei UI", 10),
            fg="#bfd5dc",
            bg="#112835",
        ).pack(anchor="w", padx=18, pady=(0, 14))

        timeline_box = tk.Frame(self.right_panel, bg="#17394a")
        timeline_box.pack(fill="x", padx=18, pady=(0, 14))
        tk.Label(
            timeline_box,
            text="主线脉络",
            font=("Microsoft YaHei UI", 12, "bold"),
            fg="#f1f4f6",
            bg="#17394a",
        ).pack(anchor="w", padx=12, pady=(10, 6))
        tk.Label(
            timeline_box,
            text=STORY_TIMELINE,
            justify="left",
            wraplength=236,
            font=("Microsoft YaHei UI", 9),
            fg="#d6e6eb",
            bg="#17394a",
        ).pack(anchor="w", padx=12, pady=(0, 10))

        stats_box = tk.Frame(self.right_panel, bg="#17394a")
        stats_box.pack(fill="x", padx=18, pady=(0, 14))

        self.stat_labels: dict[str, tk.Label] = {}
        for key, label in STATS.items():
            row = tk.Frame(stats_box, bg="#17394a")
            row.pack(fill="x", padx=12, pady=7)
            tk.Label(
                row,
                text=label,
                font=("Microsoft YaHei UI", 11, "bold"),
                fg="#f1f4f6",
                bg="#17394a",
            ).pack(side="left")
            value = tk.Label(
                row,
                text="0",
                font=("Consolas", 11, "bold"),
                fg="#8ed1ff",
                bg="#17394a",
            )
            value.pack(side="right")
            self.stat_labels[key] = value

        route_box = tk.Frame(self.right_panel, bg="#17394a")
        route_box.pack(fill="x", padx=18, pady=(0, 14))
        tk.Label(
            route_box,
            text="当前状态",
            font=("Microsoft YaHei UI", 12, "bold"),
            fg="#f1f4f6",
            bg="#17394a",
        ).pack(anchor="w", padx=12, pady=(10, 6))

        self.route_label = tk.Label(
            route_box,
            text="目标：尚未确定",
            justify="left",
            wraplength=236,
            font=("Microsoft YaHei UI", 10),
            fg="#cce1e7",
            bg="#17394a",
        )
        self.route_label.pack(anchor="w", padx=12, pady=(0, 10))

        tk.Label(
            self.right_panel,
            text=f"文本总量：约 {total_story_text()} 字",
            font=("Microsoft YaHei UI", 10),
            fg="#7fb3c4",
            bg="#112835",
        ).pack(anchor="w", padx=18, pady=(0, 8))

        tk.Label(
            self.right_panel,
            text="结局数量：4",
            font=("Microsoft YaHei UI", 10),
            fg="#7fb3c4",
            bg="#112835",
        ).pack(anchor="w", padx=18, pady=(0, 12))

        tk.Label(
            self.right_panel,
            text="经历片段",
            font=("Microsoft YaHei UI", 12, "bold"),
            fg="#f1f4f6",
            bg="#112835",
        ).pack(anchor="w", padx=18)

        self.history_list = tk.Listbox(
            self.right_panel,
            bg="#0b1b25",
            fg="#d8e8ee",
            highlightthickness=0,
            relief="flat",
            activestyle="none",
            font=("Microsoft YaHei UI", 10),
        )
        self.history_list.pack(fill="both", expand=True, padx=18, pady=(8, 18))

    def _update_choice_scrollregion(self, _event=None) -> None:
        self.choice_canvas.configure(scrollregion=self.choice_canvas.bbox("all"))

    def _resize_choice_window(self, event) -> None:
        self.choice_canvas.itemconfigure(self.choice_window, width=event.width)

    def _bind_choice_mousewheel(self, _event=None) -> None:
        self.choice_canvas.bind_all("<MouseWheel>", self._on_choice_mousewheel)

    def _unbind_choice_mousewheel(self, _event=None) -> None:
        self.choice_canvas.unbind_all("<MouseWheel>")

    def _on_choice_mousewheel(self, event) -> None:
        delta = -1 * int(event.delta / 120) if event.delta else 0
        self.choice_canvas.yview_scroll(delta, "units")

    def restart_game(self) -> None:
        self._reset_state()
        self.render_current_node()

    def update_stats_display(self) -> None:
        for key in STATS:
            self.stat_labels[key].configure(text=str(self.state[key]))

        if self.state["goal"] == "restore":
            goal_text = "目标：改造晨星引擎"
        elif self.state["goal"] == "destroy":
            goal_text = "目标：摧毁晨星引擎"
        elif self.state["goal"] == "confront":
            goal_text = "目标：公开罪证并逼停"
        else:
            goal_text = "目标：尚未确定"

        route_lines = [
            goal_text,
            f"沈砚协力：{'是' if self.state['shen_ally'] else '否'}",
            f"乔曼协力：{'是' if self.state['qiaoman_ally'] else '否'}",
            f"陆庚证词：{'已取得' if self.state['lugeng_witness'] else '未取得'}",
        ]
        self.route_label.configure(text="\n".join(route_lines))

    def set_story_text(self, text: str) -> None:
        self.story_text.configure(state="normal")
        self.story_text.delete("1.0", tk.END)
        self.story_text.insert("1.0", format_story_text(text))
        self.story_text.see("1.0")
        self.story_text.configure(state="disabled")

    def clear_choices(self) -> None:
        for button in self.choice_buttons:
            button.destroy()
        self.choice_buttons.clear()
        if hasattr(self, "choice_canvas"):
            self.choice_canvas.yview_moveto(0)

    def render_current_node(self) -> None:
        node = NODES[self.current_node]
        self.chapter_label.configure(text=node["title"])
        summary = NODE_BRIEFS.get(
            self.current_node,
            "当前导读：继续沿着已知线索推进，留意人物关系、地点用途，以及最终路线的取舍。",
        )
        self.summary_label.configure(text=summary)
        self.set_story_text(node["text"])
        self.clear_choices()
        self.update_stats_display()

        self.history_list.delete(0, tk.END)
        for item in self.history[-10:]:
            self.history_list.insert(tk.END, f"• {item}")

        if node.get("ending"):
            self._create_choice_button("重新开始", self.restart_game, primary=True).pack(fill="x", pady=(0, 8))
            self._create_choice_button("返回主菜单", self.show_menu).pack(fill="x", pady=(0, 8))
            self._create_choice_button("退出游戏", self.root.destroy).pack(fill="x")
            self._update_choice_scrollregion()
            return

        visible_options = [
            option for option in node.get("options", [])
            if self._requirements_met(option.get("requires", {}))
        ]
        for option in visible_options:
            command = lambda opt=option: self.choose_option(opt)
            self._create_choice_button(option["text"], command).pack(fill="x", pady=(0, 8))

        if not visible_options:
            self._create_choice_button("返回主菜单", self.show_menu).pack(fill="x")

        self._update_choice_scrollregion()

    def _requirements_met(self, requirements: dict[str, object]) -> bool:
        for key, expected in requirements.items():
            if self.state.get(key) != expected:
                return False
        return True

    def _create_choice_button(self, text: str, command, primary: bool = False) -> tk.Button:
        bg = "#825b25" if primary else "#17435a"
        hover = "#a97731" if primary else "#236987"
        button = tk.Button(
            self.choice_frame,
            text=text,
            command=command,
            wraplength=760,
            justify="left",
            anchor="w",
            font=("Microsoft YaHei UI", 12),
            bg=bg,
            fg="#f7fbff",
            activebackground=hover,
            activeforeground="#ffffff",
            relief="flat",
            padx=16,
            pady=14,
            cursor="hand2",
        )
        button.bind("<Enter>", lambda _event, b=button, color=hover: b.configure(bg=color))
        button.bind("<Leave>", lambda _event, b=button, color=bg: b.configure(bg=color))
        self.choice_buttons.append(button)
        return button

    def choose_option(self, option: dict[str, object]) -> None:
        self.apply_effects(option.get("effects", {}))
        self.history.append(NODES[self.current_node]["title"])
        self.current_node = str(option["target"])
        self.render_current_node()

    def apply_effects(self, effects: dict[str, object]) -> None:
        for key, value in effects.items():
            if key in STATS and isinstance(value, int):
                self.state[key] = clamp(int(self.state[key]) + value)
            else:
                self.state[key] = value


def main() -> None:
    root = tk.Tk()
    AdventureGame(root)
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    try:
        root.mainloop()
    finally:
        winsound.PlaySound(None, winsound.SND_PURGE)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        messagebox.showerror(APP_TITLE, f"游戏启动失败：{exc}")
