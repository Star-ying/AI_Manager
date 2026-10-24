# -*- coding: utf-8 -*-
"""
AI 语音助手桌面小人（桌宠原型）
独立进程，通过 http://127.0.0.1:5001/api 与后端交互（轮询 /api/status）
透明置顶无边框小窗 + 状态驱动动画 + 可拖动 + 右键菜单
形象暂用代码绘制的胖鲸占位（真·动图素材后置）
"""

import random
import sys
import threading
import time

import requests
from PySide6.QtCore import Qt, QPoint, QTimer, QPropertyAnimation, QEasingCurve, Property, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QBrush,
    QFontMetrics,
)
from PySide6.QtWidgets import (
    QApplication,
    QInputDialog,
    QMenu,
    QWidget,
)

API_BASE = "http://127.0.0.1:5001/api"
POLL_INTERVAL_MS = 800

# 状态 → 配色/文案（映射后端 current_status 四字段）
STATE_IDLE = "idle"
STATE_LISTENING = "listening"
STATE_THINKING = "thinking"
STATE_SPEAKING = "speaking"
STATE_OFFLINE = "offline"

STATE_STYLE = {
    STATE_IDLE: (QColor(120, 180, 235), "戳我"),
    STATE_LISTENING: (QColor(80, 200, 140), "我在听！"),
    STATE_THINKING: (QColor(240, 190, 90), "唔…想想"),
    STATE_SPEAKING: (QColor(170, 130, 230), "说话中~"),
    STATE_OFFLINE: (QColor(150, 175, 205), "去潜水了…"),
}

# 指令响应层（2026-10-24 新增）：待机闲聊台词 + 操作→特效后缀映射
IDLE_LINES = ["戳我", "好无聊…先游两圈", "偷偷吃条小鱼干", "今天也要元气满满！", "要不要说点什么？"]
OP_REACTIONS = [
    (("play", "music", "音乐", "播放"), "♪"),
    (("pause", "stop", "暂停", "停止"), "▐▐"),
    (("next", "previous", "下一首", "上一首", "切歌"), "♪~"),
    (("timer", "remind", "提醒", "闹钟"), "⏰"),
    (("open", "launch", "app", "打开", "启动"), "✦"),
    (("volume", "音量"), "🔊"),
    (("file", "read", "write", "文件"), "✧"),
    (("exit", "quit", "退出", "再见"), "👋"),
]


class BubbleWhale(QWidget):
    """透明置顶桌宠主窗体：绘制胖鲸 + 气泡 + 呼吸动画 + 拖动/菜单"""

    # 跨线程回调必须经信号回 GUI 线程（后台线程直接动 QTimer 会报
    # "Timers can only be used with threads started with QThread"）
    status_ready = Signal(dict)
    poll_failed = Signal()
    cmd_ready = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint
            | Qt.FramelessWindowHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(240, 220)

        self._state = STATE_OFFLINE
        self._last_transcript = ""
        self._drag_offset: QPoint | None = None
        self._breath = 0.0  # 呼吸相位 0~1，Property 动画驱动
        self._bob = 0.0     # 浮动相位

        # 呼吸动画：0→1 往返
        self._breath_anim = QPropertyAnimation(self, b"breath", self)
        self._breath_anim.setDuration(2400)
        self._breath_anim.setStartValue(0.0)
        self._breath_anim.setEndValue(1.0)
        self._breath_anim.setLoopCount(-1)
        self._breath_anim.setEasingCurve(QEasingCurve.InOutSine)
        # QPropertyAnimation 往返需要自定义，这里用定时器推进相位更简单
        self._breath_anim.stop()

        self._tick = QTimer(self)
        self._tick.setInterval(50)
        self._tick.timeout.connect(self._on_tick)
        self._tick.start()

        # 状态轮询
        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(POLL_INTERVAL_MS)
        self._poll_timer.timeout.connect(self._poll_status_async)
        self._poll_timer.start()

        self._speech_timer = QTimer(self)
        self._speech_timer.setSingleShot(True)
        self._speech_timer.timeout.connect(self._clear_bubble)

        # ---- 指令响应层（2026-10-24 新增）：表情/戳击/长按/闲聊/粒子 ----
        self._expr = "sleepy"  # normal/happy/focused/thinking/speaking/dizzy/sleepy
        self._expr_hold = False
        self._expr_timer = QTimer(self)
        self._expr_timer.setSingleShot(True)
        self._expr_timer.timeout.connect(self._revert_expr)

        self._last_msg_shown = ""
        self._poke_count = 0
        self._last_poke = 0.0
        self._moved = False
        self._press_timer = QTimer(self)
        self._press_timer.setSingleShot(True)
        self._press_timer.setInterval(600)
        self._press_timer.timeout.connect(self._on_press_hold)
        self._press_timer2 = QTimer(self)
        self._press_timer2.setSingleShot(True)
        self._press_timer2.setInterval(2200)
        self._press_timer2.timeout.connect(lambda: self._show_bubble("咕噜咕噜～", 2500))

        self._burst = []  # 粒子特效 [(x, y, vx, vy, t)]

        self._idle_timer = QTimer(self)
        self._idle_timer.setInterval(30000)
        self._idle_timer.timeout.connect(self._idle_chat)
        self._idle_timer.start()

        # 信号→槽（Qt 自动队列连接，保证在 GUI 线程执行）
        self.status_ready.connect(self._apply_status)
        self.poll_failed.connect(lambda: self._set_state(STATE_OFFLINE))
        self.cmd_ready.connect(self._on_command_reply)

    # ---- Property: breath ----
    def _get_breath(self):
        return self._breath

    def _set_breath(self, v):
        self._breath = v
        self.update()

    breath = Property(float, _get_breath, _set_breath)

    def _on_tick(self):
        import math
        # 【留痕】原 elapsed_count 探测无意义已删：
        # t = self._tick.elapsed_count if hasattr(self._tick, "elapsed_count") else 0
        self._phase = getattr(self, "_phase", 0.0) + 0.05
        self._breath = (math.sin(self._phase) + 1) / 2
        self._bob = math.sin(self._phase * 0.7)
        if self._burst:
            for pt in self._burst:
                pt[0] += pt[2]
                pt[1] += pt[3]
                pt[3] += 0.12
                pt[4] += 1
            self._burst = [pt for pt in self._burst if pt[4] < 34]
        self.update()

    # ---- 状态轮询（后台线程发 HTTP，避免卡 UI）----
    def _poll_status_async(self):
        def work():
            try:
                r = requests.get(f"{API_BASE}/status", timeout=2)
                data = r.json()
                self.status_ready.emit(data)
            except Exception:
                self.poll_failed.emit()
        threading.Thread(target=work, daemon=True).start()

    def _apply_status(self, data: dict):
        if data.get("is_tts_playing"):
            st = STATE_SPEAKING
        elif data.get("is_processing"):
            st = STATE_THINKING
        elif data.get("is_listening"):
            st = STATE_LISTENING
        else:
            st = STATE_IDLE
        self._set_state(st)

        transcript = (data.get("last_transcript") or "").strip()
        if transcript and transcript != self._last_transcript:
            self._last_transcript = transcript
            self._show_bubble(f"「{transcript}」", 2500)

        # 指令结果驱动反馈（成功=开心+粒子，失败=晕倒）【2026-10-24 新增】
        result = data.get("last_command_result") or {}
        msg = (result.get("message") or "").strip()
        if msg and msg != self._last_msg_shown:
            self._last_msg_shown = msg
            if result.get("success", True):
                react = self._reaction_for(str(result.get("operation") or ""), msg)
                self._show_bubble(f"{msg} {react}".strip(), 6000)
                self._set_expr("happy", hold=4000)
                self._spawn_burst(8)
            else:
                self._show_bubble(f"呜… {msg}", 6000)
                self._set_expr("dizzy", hold=4000)

    _STATE_EXPR = {
        STATE_IDLE: "normal",
        STATE_LISTENING: "focused",
        STATE_THINKING: "thinking",
        STATE_SPEAKING: "speaking",
        STATE_OFFLINE: "sleepy",
    }

    def _set_state(self, st: str):
        if st != self._state:
            self._state = st
            # offline 优先级最高：掉线不能被反馈 hold 挡住【2026-10-24 新增】
            if st == STATE_OFFLINE:
                self._expr_hold = False
                self._expr_timer.stop()
            if not self._expr_hold:
                self._expr = self._STATE_EXPR.get(st, "normal")
            self.update()

    def _set_expr(self, ex: str, hold: int = 0):
        self._expr = ex
        self._expr_hold = hold > 0
        if hold > 0:
            self._expr_timer.start(hold)
        self.update()

    def _revert_expr(self):
        self._expr_hold = False
        self._expr = self._STATE_EXPR.get(self._state, "normal")
        self.update()

    # ---- 气泡 ----
    def _show_bubble(self, text: str, msec: int = 3000):
        self._bubble_text = text
        self._speech_timer.start(msec)
        self.update()

    def _clear_bubble(self):
        self._bubble_text = ""
        self.update()

    _bubble_text = ""

    # ---- 交互：戳击 / 拖动 / 长按 / 右键（【升级】原 press 即弹"搬家中"改为移动阈值触发；双击并入戳击计数）----
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_offset = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._moved = False
            self._press_timer.start()
        elif e.button() == Qt.RightButton:
            self._popup_menu(e.globalPosition().toPoint())

    def _on_press_hold(self):
        if self._drag_offset is not None and not self._moved:
            self._show_bubble("别捏", 1500)
            self._press_timer2.start()

    def mouseMoveEvent(self, e):
        if self._drag_offset is not None and e.buttons() & Qt.LeftButton:
            if not self._moved:
                self._moved = True
                self._press_timer.stop()
                self._press_timer2.stop()
                self._show_bubble("搬家中")
            self.move(e.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._press_timer.stop()
            self._press_timer2.stop()
            moved = self._moved
            self._drag_offset = None
            self._moved = False
            if moved:
                self._show_bubble("放好啦", 1500)
            else:
                self._on_poke()

    def _on_poke(self):
        now = time.monotonic()
        if now - self._last_poke > 1.5:
            self._poke_count = 0
        self._last_poke = now
        self._poke_count += 1
        if self._poke_count == 1:
            self._show_bubble("嘻", 1500)
        else:
            self._show_bubble(f"再戳×{min(self._poke_count, 9)}", 1500)
        self._set_expr("happy", hold=2000)
        self._spawn_burst(5)

    def _popup_menu(self, pos: QPoint):
        menu = QMenu(self)
        act_listen = menu.addAction("开始收音" if self._state != STATE_LISTENING else "停止收音")
        act_cmd = menu.addAction("下指令…")
        act_hello = menu.addAction("打个招呼")
        menu.addSeparator()
        act_quit = menu.addAction("让小人下线")
        chosen = menu.exec(pos)
        if chosen == act_listen:
            self._toggle_listen()
        elif chosen == act_cmd:
            self._ask_command()
        elif chosen == act_hello:
            self._say_hello()
        elif chosen == act_quit:
            QApplication.quit()

    def _toggle_listen(self):
        action = "stop" if self._state == STATE_LISTENING else "start"

        def work():
            try:
                requests.post(f"{API_BASE}/listen", json={"action": action}, timeout=3)
            except Exception:
                pass
        threading.Thread(target=work, daemon=True).start()

    def _say_hello(self):
        def work():
            try:
                requests.post(f"{API_BASE}/tts/speak", json={"text": "你好呀，我是你的语音小助手！"}, timeout=3)
            except Exception:
                pass
        threading.Thread(target=work, daemon=True).start()

    # ---- 文字指令入口（2026-10-24 新增）：思考态→/api/command→回复气泡 ----
    def _ask_command(self):
        text, ok = QInputDialog.getText(self, "下指令", "想让本鱼做什么？")
        if not ok or not text.strip():
            return
        text = text.strip()
        self._show_bubble(f"「{text}」…", 60000)
        self._set_expr("thinking", hold=60000)

        def work():
            try:
                r = requests.post(
                    f"{API_BASE}/command",
                    json={"text": text, "options": {"should_speak": True}},
                    timeout=60,
                )
                data = r.json()
            except Exception as e:
                data = {"success": False, "response_to_user": f"后端没接住：{e}"}
            self.cmd_ready.emit(data)
        threading.Thread(target=work, daemon=True).start()

    def _on_command_reply(self, data: dict):
        self._expr_timer.stop()
        ok = bool(data.get("success"))
        resp = (data.get("response_to_user") or "").strip() or "……"
        if ok:
            react = self._reaction_for(str(data.get("operation") or ""), resp)
            self._show_bubble(f"{resp} {react}".strip(), 6000)
            self._set_expr("happy", hold=4000)
            self._spawn_burst(8)
        else:
            self._show_bubble(f"呜… {resp}", 6000)
            self._set_expr("dizzy", hold=4000)

    def _reaction_for(self, op: str, msg: str) -> str:
        text = (op + " " + msg).lower()
        for keys, emoji in OP_REACTIONS:
            if any(k in text for k in keys):
                return emoji
        return ""

    def _spawn_burst(self, n: int = 8):
        cx, cy = self.width() * 0.5, self.height() * 0.28
        for _ in range(n):
            vx = random.uniform(-1.6, 1.6)
            vy = random.uniform(-2.6, -0.8)
            self._burst.append([cx + random.uniform(-14, 14), cy, vx, vy, 0])

    def _idle_chat(self):
        if self._state == STATE_IDLE and not self._bubble_text:
            self._show_bubble(random.choice(IDLE_LINES), 2500)

    # ---- 绘制：占位胖鲸 ----
    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        body_color, hint = STATE_STYLE[self._state]
        w, h = self.width(), self.height()

        # offline：整体下沉半透明（【修复】原设在画完身体后只淡了气泡）
        if self._state == STATE_OFFLINE:
            p.setOpacity(0.55)

        # 鲸鱼本体椭圆（呼吸缩放 + 上下浮动）【重画：原尾巴/眼睛/肚皮比例失调】
        cx, cy = w * 0.5, h * 0.60 + self._bob * 4
        bw = 134 + self._breath * 6
        bh = 88 + self._breath * 4
        body_rect = self._rect_centered(cx, cy, bw, bh)

        p.setPen(Qt.NoPen)

        # 尾巴：V 形双叶尾鳍（右侧，缺口朝外）
        tx, ty = cx + bw * 0.47, cy
        tail = QPainterPath()
        tail.moveTo(tx, ty - 8)
        tail.lineTo(tx + 26, ty - 28)
        tail.quadTo(tx + 14, ty - 8, tx + 12, ty)
        tail.quadTo(tx + 14, ty + 8, tx + 26, ty + 28)
        tail.lineTo(tx, ty + 8)
        tail.closeSubpath()
        p.setBrush(QBrush(body_color.darker(112)))
        p.drawPath(tail)

        # 身体
        p.setBrush(QBrush(body_color))
        p.drawEllipse(body_rect)

        # 白肚皮（下半部，前倾）【微调：原 cx-0.10 偏左，右移】
        belly = self._rect_centered(cx + bw * 0.05, cy + bh * 0.24, bw * 0.72, bh * 0.46)
        p.setBrush(QBrush(QColor(245, 250, 253)))
        p.drawEllipse(belly)

        # 胸鳍（身体中部小椭圆）
        fin = self._rect_centered(cx - bw * 0.02, cy + bh * 0.10, bw * 0.20, bh * 0.26)
        p.setBrush(QBrush(body_color.darker(120)))
        p.drawEllipse(fin)

        # ---- 表情（眼+嘴）【2026-10-24 新增：按 _expr 驱动，原固定眼/微笑并入 normal 分支】----
        eye_x = int(cx - bw * 0.30)
        eye_y = int(cy - bh * 0.12)
        mouth_x = cx - bw * 0.36
        mouth_y = cy + bh * 0.07
        ex = self._expr
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(40, 50, 60)))
        if ex == "happy":
            pen_e = QPen(QColor(40, 50, 60)); pen_e.setWidth(2); pen_e.setCapStyle(Qt.RoundCap)
            p.setPen(pen_e); p.setBrush(Qt.NoBrush)
            arc = QPainterPath()
            arc.moveTo(eye_x - 5, eye_y + 2)
            arc.quadTo(eye_x, eye_y - 6, eye_x + 5, eye_y + 2)
            p.drawPath(arc)
            p.setPen(Qt.NoPen)
        elif ex == "dizzy":
            pen_e = QPen(QColor(40, 50, 60)); pen_e.setWidth(2)
            p.setPen(pen_e)
            p.drawLine(eye_x - 4, eye_y - 4, eye_x + 4, eye_y + 4)
            p.drawLine(eye_x + 4, eye_y - 4, eye_x - 4, eye_y + 4)
            p.setPen(Qt.NoPen)
        elif ex == "sleepy":
            pen_e = QPen(QColor(40, 50, 60)); pen_e.setWidth(2); pen_e.setCapStyle(Qt.RoundCap)
            p.setPen(pen_e); p.setBrush(Qt.NoBrush)
            arc = QPainterPath()
            arc.moveTo(eye_x - 5, eye_y - 1)
            arc.quadTo(eye_x, eye_y + 5, eye_x + 5, eye_y - 1)
            p.drawPath(arc)
            p.setPen(Qt.NoPen)
        elif ex == "thinking":
            pen_e = QPen(QColor(40, 50, 60)); pen_e.setWidth(2); pen_e.setCapStyle(Qt.RoundCap)
            p.setPen(pen_e)
            p.drawLine(eye_x - 4, eye_y + 1, eye_x + 4, eye_y - 2)
            p.setPen(Qt.NoPen)
        elif ex == "focused":
            p.drawEllipse(QPoint(eye_x, eye_y), 6, 8)
            p.setBrush(QBrush(QColor(255, 255, 255)))
            p.drawEllipse(QPoint(eye_x - 2, eye_y - 3), 1, 1)
        else:  # normal / speaking
            p.drawEllipse(QPoint(eye_x, eye_y), 5, 5)
            p.setBrush(QBrush(QColor(255, 255, 255)))
            p.drawEllipse(QPoint(eye_x - 2, eye_y - 2), 1, 1)

        # 嘴
        if ex == "speaking":
            p.setBrush(QBrush(QColor(60, 70, 85)))
            p.drawEllipse(QPoint(int(mouth_x), int(mouth_y)), 4, int(2 + self._breath * 5))
        elif ex == "happy":
            pen_s = QPen(QColor(60, 70, 85, 200)); pen_s.setWidth(2); pen_s.setCapStyle(Qt.RoundCap)
            p.setPen(pen_s); p.setBrush(Qt.NoBrush)
            sm = QPainterPath()
            sm.moveTo(mouth_x - 6, mouth_y - 2)
            sm.quadTo(mouth_x, mouth_y + 5, mouth_x + 6, mouth_y - 2)
            p.drawPath(sm)
            p.setPen(Qt.NoPen)
        elif ex == "dizzy":
            pen_s = QPen(QColor(60, 70, 85, 200)); pen_s.setWidth(2)
            p.setPen(pen_s)
            p.drawLine(int(mouth_x) - 5, int(mouth_y) + 2, int(mouth_x), int(mouth_y) - 2)
            p.drawLine(int(mouth_x), int(mouth_y) - 2, int(mouth_x) + 5, int(mouth_y) + 2)
            p.setPen(Qt.NoPen)
        elif ex in ("thinking", "sleepy"):
            pen_s = QPen(QColor(60, 70, 85, 160)); pen_s.setWidth(2); pen_s.setCapStyle(Qt.RoundCap)
            p.setPen(pen_s)
            p.drawLine(int(mouth_x) - 4, int(mouth_y), int(mouth_x) + 4, int(mouth_y))
            p.setPen(Qt.NoPen)
        else:
            smile = QPainterPath()
            smile.moveTo(cx - bw * 0.40, cy + bh * 0.02)
            smile.quadTo(cx - bw * 0.33, cy + bh * 0.10, cx - bw * 0.22, cy + bh * 0.06)
            pen_s = QPen(QColor(60, 70, 85, 160)); pen_s.setWidth(2); pen_s.setCapStyle(Qt.RoundCap)
            p.setPen(pen_s); p.setBrush(Qt.NoBrush)
            p.drawPath(smile)
            p.setPen(Qt.NoPen)

        # 呆毛（头顶前部弯钩）
        tuft = QPainterPath()
        hx = cx - bw * 0.18
        hy = body_rect.top() + 4
        tuft.moveTo(hx, hy)
        tuft.cubicTo(hx - 2, hy - 16, hx + 14, hy - 16, hx + 10, hy - 4)
        pen = QPen(body_color.darker(130))
        pen.setWidth(4)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawPath(tuft)

        # 喷水泡泡（speaking 时从头顶飘音符点）
        if self._state == STATE_SPEAKING:
            p.setPen(QPen(QColor(170, 130, 230, 180)))
            for i in range(3):
                yy = body_rect.top() - 10 - i * 12 - (self._phase * 8 % 12)
                p.drawEllipse(QPoint(int(cx + 14 + i * 6), int(yy)), 3 - i, 3 - i)

        # offline 半透明已移至 paintEvent 开头统一设置

        # 粒子特效（指令完成/戳击反馈）【2026-10-24 新增】
        for x, y, vx, vy, t in self._burst:
            alpha = max(0, 210 - t * 7)
            r = max(1, 3 - t // 12)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor(255, 205, 90, alpha)))
            p.drawEllipse(QPoint(int(x), int(y)), r, r)

        # 气泡框
        bubble_text = self._bubble_text if self._bubble_text else (
            hint if self._state in (STATE_IDLE, STATE_OFFLINE) else ""
        )
        if self._state == STATE_OFFLINE:
            bubble_text = bubble_text or "去潜水了… Zzz"
        if bubble_text:
            self._draw_bubble(p, bubble_text)

        p.end()

    @staticmethod
    def _rect_centered(cx, cy, w, h):
        from PySide6.QtCore import QRectF
        return QRectF(cx - w / 2, cy - h / 2, w, h)

    def _draw_bubble(self, p: QPainter, text: str):
        font = QFont("Microsoft YaHei", 9)
        p.setFont(font)
        fm = QFontMetrics(font)
        tw = min(fm.horizontalAdvance(text) + 20, 210)
        lines = self._wrap(text, fm, 190)
        bh = 16 * len(lines) + 14
        rect = self._rect_centered(self.width() * 0.5, 26 + bh / 2, tw, bh)
        p.setBrush(QBrush(QColor(255, 255, 255, 225)))
        p.setPen(QPen(QColor(180, 190, 205), 1.2))
        p.drawRoundedRect(rect, 10, 10)
        # 指向小尖
        tailp = QPainterPath()
        tailp.moveTo(self.width() * 0.5 - 6, rect.bottom())
        tailp.lineTo(self.width() * 0.5 + 6, rect.bottom())
        tailp.lineTo(self.width() * 0.5, rect.bottom() + 8)
        tailp.closeSubpath()
        p.drawPath(tailp)
        p.setPen(QPen(QColor(60, 70, 85)))
        # 【留痕】原文字左上偏置已废：
        # y = rect.top() + 16
        # for ln in lines:
        #     p.drawText(rect.adjusted(10, y - rect.top() - 12, -10, y - rect.top()),
        #                Qt.AlignVCenter | Qt.AlignLeft, ln)
        #     y += 16
        from PySide6.QtCore import QRectF
        block_h = 16 * len(lines)
        y = rect.top() + (rect.height() - block_h) / 2
        for ln in lines:
            strip = QRectF(rect.left() + 6, y, rect.width() - 12, 16)
            p.drawText(strip, Qt.AlignCenter, ln)
            y += 16

    @staticmethod
    def _wrap(text, fm: QFontMetrics, maxw: int):
        lines, cur = [], ""
        for ch in text:
            if fm.horizontalAdvance(cur + ch) > maxw:
                lines.append(cur)
                cur = ch
            else:
                cur += ch
        if cur:
            lines.append(cur)
        return lines[:3]


def main():
    app = QApplication(sys.argv)
    pet = BubbleWhale()
    # 默认停在屏幕右下角
    screen = app.primaryScreen().availableGeometry()
    pet.move(screen.right() - pet.width() - 40, screen.bottom() - pet.height() - 40)
    pet.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
