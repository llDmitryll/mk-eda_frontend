from __future__ import annotations

import json
import logging
import math
import re
import sys
import typing
from collections import deque
from functools import partial

from PySide6.QtCore import QLineF, QPoint, QPointF, QRectF, QSize, Qt, QTimeLine
from PySide6.QtGui import (
    QAction,
    QColor,
    QCursor,
    QFont,
    QIcon,
    QKeyEvent,
    QMouseEvent,
    QPainterPath,
    QPainterPathStroker,
    QPen,
    QPixmap,
    QTextCursor,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsPathItem,
    QGraphicsScene,
    QGraphicsSceneMouseEvent,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QGraphicsWidget,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from mk_eda.libs.graph.graph import InverterGraph, Node, logger
from mk_eda.libs.optimization.xaig_complexity_optimizer import XAIGComplexityOptimizer
from mk_eda.libs.optimization.xaig_depth_optimizer import XAIGDepthOptimizer
from mk_eda.libs.verification.partitioner.depth.depth_partitioner import depth_partitioner


class RMB_menu_node(QMenu):
    def __init__(self, parent: QWidget) -> None:
        super().__init__("choose action", parent)
        self.delete_node_action = QAction("Delete node", self)
        self.delete_selected_nodes_action = QAction("Delete selected nodes", self)
        self.show_expr_action = QAction("Show expression", self)
        self.output_node_action = QAction("Output/not output node", self)
        self.change_node_action = QAction("Change node", self)
        self.addActions(
            [
                self.delete_node_action,
                self.delete_selected_nodes_action,
                self.show_expr_action,
                self.output_node_action,
                self.change_node_action,
            ]
        )


class RMB_menu_line(QMenu):
    def __init__(self, parent: QGraphicsWidget) -> None:
        super().__init__("choose action")
        self.delete_line_action = QAction("Delete line", self)
        self.addActions([self.delete_line_action])


class RMB_menu_space(QMenu):
    def __init__(self, parent: GraphView) -> None:
        super().__init__(parent=parent)
        self.create_node_action = QAction("Create node", self)
        self.clear_scene_action = QAction("Clear scene", self)
        self.addActions([self.create_node_action, self.clear_scene_action])


class Functions_menu(QMenu):
    def __init__(self, parent: GraphView) -> None:
        super().__init__(parent=parent)
        self.complex_optimizeXAIG_action = QAction("Optimize by complexity[XAIG]", self)
        self.depth_optimizeXAIG_action = QAction("Optimize by depth[XAIG]", self)
        self.depth_choosing = self.addMenu("Depth partition")
        self.addActions([self.complex_optimizeXAIG_action, self.depth_optimizeXAIG_action])


class DialogNode(QDialog):
    def __init__(self, title: str, parent: QWidget) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.main_layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        self.name_line_edit = QLineEdit(self)
        self.ok_button = QPushButton(text="Ok", parent=self)
        self.ok_button.clicked.connect(self.accept)
        self.type_box = QComboBox(self)
        self.type_box.addItems(["input", "const", "and", "or", "xor", "majority"])
        self.check_box = QCheckBox("Output", self)
        self.form_layout.addRow("Name", self.name_line_edit)
        self.form_layout.addRow("Type", self.type_box)
        self.form_layout.addWidget(self.check_box)
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addWidget(self.ok_button)


class QNode(QGraphicsEllipseItem):
    diameter = 70

    def __init__(self, x: float, y: float, name: str, node_type: str, out_flag: bool = False) -> None:
        self.in_lines: list[QNodePath] = []
        self.out_lines: list[QNodePath] = []
        super().__init__(0, 0, self.diameter, self.diameter)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.scene_: Graph | None = None
        self.component_id: int = -1
        self.depth: int = 0
        self.out_flag = out_flag
        self.font_size = 15
        self.condition = True
        self.sync = False
        self.expr = QGraphicsSimpleTextItem(self)
        self.expr.setFont(QFont("Calibri", self.font_size - 3))
        self.expr.setVisible(False)
        self.out_ellipse = QGraphicsEllipseItem(self)
        self.out_ellipse.setBrush(QColor("grey"))
        self.out_ellipse.setRect(-4, -4, self.diameter + 8, self.diameter + 8)
        self.out_ellipse.setZValue(-0.5)
        self.out_ellipse.setFlag(QGraphicsItem.GraphicsItemFlag.ItemStacksBehindParent)
        self.name = QGraphicsSimpleTextItem(name, self)
        self.name.setFont(QFont("Calibri", self.font_size))
        self.name.setPos(
            (self.diameter - self.name.boundingRect().width()) / 2,
            (self.diameter - self.name.boundingRect().height()) / 2 - 10,
        )
        self.node_type = QGraphicsSimpleTextItem(node_type, self)
        self.node_type.setFont(QFont("Calibri", self.font_size))
        self.node_type.setPos(
            (self.diameter - self.node_type.boundingRect().width()) / 2,
            (self.diameter - self.node_type.boundingRect().height()) / 2 + 10,
        )
        self.moveBy(x, y)
        self._out_draw()

    def check_condition(self):
        if self.sync:
            self.setBrush(QColor("green"))
        elif self.condition:
            self.setBrush(QColor("blue"))
        else:
            self.setBrush(QColor("red"))
        if self.expr.isVisible():
            self._check_expr()

    def add_in_line(self, node_path: QNodePath):
        self.in_lines.append(node_path)
        self.node_changed()

    def remove_in_line(self, node_path: QNodePath):
        self.in_lines.remove(node_path)
        self.node_changed()

    def add_out_line(self, node_path: QNodePath):
        self.out_lines.append(node_path)
        self.node_changed()

    def remove_out_line(self, node_path: QNodePath):
        self.out_lines.remove(node_path)
        self.node_changed()

    def change_out(self):
        self.out_flag = not self.out_flag
        self._out_draw()

    def _check_expr(self):
        if self.scene_:
            try:
                text = str(self.scene_.to_InverterGraph()[self.name.text()])
                self.expr.setText(text)
                self.expr.setPos(
                    (self.diameter - self.expr.boundingRect().width()) / 2,
                    -self.node_type.boundingRect().height() - 5,
                )
                return
            except KeyError:
                self.expr.setText("Defective graph or not output")
                self.expr.setPos(
                    (self.diameter - self.expr.boundingRect().width()) / 2,
                    -self.node_type.boundingRect().height() - 5,
                )
                return
        self.expr.setText("Defective graph or not output")
        self.expr.setPos(
            (self.diameter - self.expr.boundingRect().width()) / 2,
            -self.node_type.boundingRect().height() - 5,
        )

    def _show_expr(self):
        self.expr.setVisible(not self.expr.isVisible())
        if self.expr.isVisible():
            self._check_expr()

    def _out_draw(self):
        self.out_ellipse.setVisible(self.out_flag)

    def _dfs(self):
        for line in self.out_lines:
            depth2 = max([line2.vertex1.depth for line2 in line.vertex2.in_lines] + [-1]) + 1
            if line.vertex2.depth == depth2:
                return
            line.vertex2.depth = depth2
            line.vertex2._dfs()

    def node_changed(self):
        if len(self.in_lines) > 0 and self.node_type.text() in ["input", "const"]:
            self.condition = False
        elif self.node_type.text() == "const" and not (self.name.text() in ["0", "1"]):
            self.condition = False
        elif len(self.in_lines) != 2 and self.node_type.text() in ["and", "or", "xor"]:
            self.condition = False
        elif len(self.in_lines) != 3 and self.node_type.text() in ["majority"]:
            self.condition = False
        else:
            self.condition = True
            new_depth = max([line.vertex1.depth for line in self.in_lines] + [-1]) + 1
            if self.scene_ and self.node_type.text() == "input":
                for node in self.scene_.nodes:
                    if self.name.text() == node.name.text() and node.node_type.text() != "input":
                        new_depth = node.depth
            if self.depth != new_depth:
                self.depth = new_depth
                self._dfs()
                if self.scene_ and self.node_type.text() not in ["input", "const"]:
                    for node in self.scene_.nodes:
                        if self.name.text() == node.name.text() and node.node_type.text() == "input":
                            node.node_changed()
        self.check_condition()

    def _change_node(self):
        dialog_node = DialogNode("Node change", self.parentWidget())  # type: ignore
        dialog_node.name_line_edit.setText(self.name.text())
        dialog_node.type_box.setCurrentText(self.node_type.text())
        dialog_node.check_box.setChecked(self.out_flag)
        accepted = dialog_node.exec()
        if accepted:
            if (
                dialog_node.name_line_edit.text()
                and self.scene_ is not None
                and (
                    dialog_node.name_line_edit.text()
                    not in [node.name.text() for node in self.scene_.nodes if node != self]
                    or (
                        dialog_node.type_box.currentText() == "input"
                        and dialog_node.name_line_edit.text()
                        not in [
                            node.name.text()
                            for node in self.scene_.connected_components[self.component_id]
                            if node != self
                        ]
                    )
                    or (
                        dialog_node.type_box.currentText() == "const"
                        and dialog_node.name_line_edit.text() in ["0", "1"]
                    )
                )
            ):
                self.name.setText(dialog_node.name_line_edit.text())
                self.name.setPos(
                    (self.diameter - self.name.boundingRect().width()) / 2,
                    (self.diameter - self.name.boundingRect().height()) / 2 - 10,
                )
                self.node_type.setText(dialog_node.type_box.currentText())
                self.node_type.setPos(
                    (self.diameter - self.node_type.boundingRect().width()) / 2,
                    (self.diameter - self.node_type.boundingRect().height()) / 2 + 10,
                )
                self.out_flag = dialog_node.check_box.isChecked()
                self._out_draw()
                self.node_changed()
                if self.scene_:
                    self.scene_.check_component(self.component_id)
            else:
                error = QMessageBox(
                    QMessageBox.Icon.Critical,
                    "Error",
                    "Name can't be same in graph or empty",
                    parent=self.parentWidget(),  # type: ignore
                )
                error.exec()

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: object):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            for line in self.out_lines + self.in_lines:
                line.draw()
        return value

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.MouseButton.RightButton and self.scene_:
            menu = RMB_menu_node(self.parentWidget())  # type: ignore
            menu.delete_node_action.triggered.connect(partial(self.scene().removeItem, self))
            menu.show_expr_action.triggered.connect(self._show_expr)
            menu.output_node_action.triggered.connect(self.change_out)
            menu.change_node_action.triggered.connect(self._change_node)
            menu.delete_selected_nodes_action.triggered.connect(self.scene_.remove_selected_items)  # type: ignore
            menu.exec(event.screenPos())
        return super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent):
        print("Глубина вершины", str(self.depth))
        return super().mouseDoubleClickEvent(event)


class QNodePath(QGraphicsPathItem):
    pens = [
        QPen(
            Qt.GlobalColor.black,
            4,
            Qt.PenStyle.DashLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        ),
        QPen(
            Qt.GlobalColor.black,
            4,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        ),
    ]
    base_shift = 15

    def __init__(self, vertex1: QNode, vertex2: QNode, n: int) -> None:
        super().__init__()
        self.setPen(QNodePath.pens[n])
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setZValue(-1)
        self.n = n
        self.shift = 0
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.start: QPointF
        self.end: QPointF
        self.arrow_left = QGraphicsLineItem(self)
        self.arrow_left.setPen(QNodePath.pens[1])
        self.arrow_left.setZValue(-1)
        self.arrow_right = QGraphicsLineItem(self)
        self.arrow_right.setPen(QNodePath.pens[1])
        self.arrow_right.setZValue(-1)
        if vertex1 != vertex2:
            self.draw()

    def shape(self):
        stroker = QPainterPathStroker()
        stroker.createStroke(self.path())
        return stroker.createStroke(self.path())

    def draw(self):
        c = self.shift
        self.start = self.vertex1.pos() + QPointF(QNode.diameter / 2, QNode.diameter / 2)
        self.end = self.vertex2.pos() + QPointF(QNode.diameter / 2, QNode.diameter / 2)
        line = QLineF(self.start, self.end)
        path = QPainterPath()
        self.setRotation(-line.angle())
        self.setTransformOriginPoint(self.start)
        path.moveTo(self.start + QPointF(line.length(), 0))
        rect = QRectF(self.start + QPointF(0, -c), self.start + QPointF(line.length(), c))
        path.arcTo(rect, 0, 180)
        path.moveTo(self.start + QPointF(line.length(), 0))
        path.arcTo(rect, 0, 90)
        arrow_left_line = QLineF(
            path.currentPosition(),
            path.currentPosition() + QPointF(-15 * math.cos(math.pi / 10), -15 * math.sin(math.pi / 10)),
        )
        arrow_right_line = QLineF(
            path.currentPosition(),
            path.currentPosition() + QPointF(-15 * math.cos(math.pi / 10), 15 * math.sin(math.pi / 10)),
        )
        self.arrow_left.setLine(arrow_left_line)
        self.arrow_right.setLine(arrow_right_line)
        self.setPath(path)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        event.accept()

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:
            menu = RMB_menu_line(self.parentWidget())
            menu.delete_line_action.triggered.connect(partial(self.scene().removeItem, self))
            menu.exec(event.screenPos())
        return super().mouseReleaseEvent(event)


class Graph(QGraphicsScene):
    def __init__(self) -> None:
        super().__init__()
        self.nodes: list[QNode] = []
        self.connected_component_id = 0
        self.connected_components: dict[int, list[QNode]] = {}

    def check_component(self, component_id: int):
        component = self.connected_components.get(component_id)
        if not component or not all([node.condition for node in component]):
            for node in self.connected_components[component_id]:
                node.sync = False
                node.check_condition()
        else:
            for node in self.connected_components[component_id]:
                node.sync = True
                node.check_condition()

    def call_function(
        self,
        func: typing.Callable[[InverterGraph], InverterGraph],
    ):
        new_graph = func(self.to_InverterGraph())
        if new_graph.nodes == {} and new_graph.inputs == [] and new_graph.outputs == []:
            return
        self.from_InverterGraph(new_graph)

    def depth_partion(
        self,
        func: typing.Callable[[InverterGraph], list[InverterGraph]],
    ):
        print("Nothing")
        # new_graphs = func(self.to_InverterGraph())
        # for graph in new_graphs:
        #     graph.print()
        # shift = QPointF(0, 0)
        # size = int(len(new_graphs) ** 0.5) + 1
        # i = 0
        # max_down = 0
        # clear = True
        # for graph in new_graphs:
        #     i += 1
        #     rect = self.from_InverterGraph(graph, shift=shift, clear=clear)
        #     down = rect.bottom()
        #     top = rect.top()
        #     right = rect.right()
        #     left = rect.left()
        #     if down - top > max_down:
        #         max_down = down - top
        #     if clear:
        #         clear = False
        #     if i % size == 0:
        #         shift = QPointF(0, shift.y() + max_down + 100)
        #         max_down = 0
        #     else:
        #         shift = QPointF(shift.x() + right - left + 100, shift.y())

    def to_InverterGraph(self) -> InverterGraph:
        graph = InverterGraph()
        self.nodes.sort(key=self._sorting_nodes)
        for node in [n for n in self.nodes if n.sync]:
            if (
                node.node_type.text() == "input"
                and node.name.text() not in graph.inputs
                and node.name.text()
                not in [gui_node.name.text() for gui_node in self.nodes if gui_node.node_type.text() != "input"]
            ):
                graph.add_input(node.name.text())
        for node in [n for n in self.nodes if n.sync]:
            if node.node_type.text() not in ["const", "input"]:
                graph.add_node(
                    Node(
                        node.node_type.text(),
                        [x for xs in [[line.vertex1.name.text(), line.n] for line in node.in_lines] for x in xs],
                    ),
                    node.name.text(),
                )
            if node.out_flag:
                graph.add_output(node.name.text())
        return graph

    def clear(self):
        self.nodes.clear()
        self.connected_component_id = 0
        self.connected_components.clear()
        super().clear()

    def from_InverterGraph(self, graph: InverterGraph, shift: QPointF | None = None, clear: bool = True) -> QRectF:
        if not shift:
            shift = QPointF(0, 0)
        top_left = QPointF(shift.x(), shift.y())
        bottom_right = QPointF(0, 0)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        load = True
        if clear:
            self.clear()
        depths: dict[str, int] = {}
        nodes: dict[str, QNode] = {}
        is_out: dict[str, bool] = {}
        for input in graph.inputs:
            depths[input] = 0
        for node_out, node in graph.nodes.items():
            self._depth_recurs(node_out, node, graph, depths)
        bottom_right.setX(150 * max(depths.values()) + shift.x())
        for output in graph.outputs:
            is_out[output] = True
        last_index = 0
        for index, input in enumerate(graph.inputs):
            nodes[input] = QNode(
                0 + shift.x(),
                index * 100 + shift.y(),
                input,
                "input",
                is_out.get(input, False),
            )
            self.addItem(nodes[input], load)
            last_index = index
        bottom_right.setY(last_index * 100 + shift.y())
        items = list(graph.nodes.items())
        items.sort(key=lambda x: depths[x[0]])
        for node_name, node in items:
            for child in node.children:
                if (child.name in ["1", "0"]) and nodes.get(child.name, None) is None:
                    nodes[child.name] = QNode(-150 + shift.x(), int(child.name) * 100, child.name, "const")
                    self.addItem(nodes[child.name], load)
                    top_left.setX(-150 + shift.x())
        for node_name in graph.outputs:
            if (node_name in ["1", "0"]) and nodes.get(node_name, None) is None:
                nodes[node_name] = QNode(-150 + shift.x(), int(node_name) * 100, node_name, "const", True)
                self.addItem(nodes[node_name], load)
                top_left.setX(-150 + shift.x())
        for node_name, node in items:
            named_children = [child for child in node.children if not (child.name in ["1", "0"])]
            if named_children:
                nodes[node_name] = QNode(
                    150 * depths[node_name] + shift.x(),
                    (nodes[named_children[0].name].y() + nodes[named_children[-1].name].y()) / 2,
                    node_name,
                    node.function,
                    is_out.get(node_name, False),
                )
            else:
                nodes[node_name] = QNode(
                    150 * depths[node_name] + shift.x(),
                    (nodes[node.children[0].name].y() + nodes[node.children[-1].name].y()) / 2,
                    node_name,
                    node.function,
                    is_out.get(node_name, False),
                )
            self.addItem(nodes[node_name], load)
            last_y = 0
            while True:
                colliding_items = [item for item in nodes[node_name].collidingItems() if isinstance(item, QNode)]
                if colliding_items:
                    nodes[node_name].setPos(
                        QPointF(
                            colliding_items[0].pos().x(),
                            colliding_items[0].pos().y() + 100,
                        )
                    )
                    last_y = colliding_items[0].pos().y() + 100
                else:
                    if last_y > bottom_right.y():
                        bottom_right.setY(last_y)
                    break
            for child in node.children:
                self.addItem(QNodePath(nodes[child.name], nodes[node_name], child.sign), load)
        lost_id = self.connected_component_id
        for input in graph.inputs + ["1", "0"]:
            if nodes.get(input, None):
                if nodes[input].component_id == lost_id:
                    self.connected_component_id += 1
                    nodes[input].component_id = self.connected_component_id
                    self._bfs(nodes[input])
                    self.check_component(self.connected_component_id)
        self.connected_component_id += 1
        QApplication.restoreOverrideCursor()
        graph_rect = QRectF(top_left, bottom_right + QPointF(QNode.diameter, QNode.diameter))
        self.views()[0].fitInView(graph_rect.adjusted(-200, -200, 200, 200), Qt.AspectRatioMode.KeepAspectRatio)
        return graph_rect

    def addItem(self, item: QGraphicsItem, load: bool = False):
        if isinstance(item, QNodePath):
            if item.vertex1 == item.vertex2:
                print("Нельзя добавить кольцо")
                return
            if not load:
                if item.vertex1.component_id != item.vertex2.component_id:
                    if {node.name.text() for node in self.connected_components[item.vertex1.component_id]}.intersection(
                        {node.name.text() for node in self.connected_components[item.vertex2.component_id]}
                    ):
                        print("Нельзя добавить одинаковые вершины в один граф")
                        return
                    lost_component = self.connected_components.pop(item.vertex2.component_id)
                    for node in lost_component:
                        node.component_id = item.vertex1.component_id
                    self.connected_components[item.vertex1.component_id] += lost_component
                if set(item.vertex1.in_lines).intersection(set(item.vertex2.out_lines)):
                    for item_ in set(item.vertex1.in_lines).intersection(set(item.vertex2.out_lines)):
                        self.removeItem(item_)
                    lost_component = self.connected_components.pop(item.vertex2.component_id)
                    for node in lost_component:
                        node.component_id = item.vertex1.component_id
                    self.connected_components[item.vertex1.component_id] += lost_component
            if len(set(item.vertex1.out_lines).intersection(set(item.vertex2.in_lines))):
                max_shift = 0
                zero = False
                for item_ in set(item.vertex1.out_lines).intersection(set(item.vertex2.in_lines)):
                    if item_.shift >= max_shift:
                        max_shift = item_.shift
                    if item_.shift == 0:
                        zero = True
                if zero:
                    item.shift = max_shift + QNodePath.base_shift
                    for item_ in set(item.vertex1.out_lines).intersection(set(item.vertex2.in_lines)):
                        if item_.shift <= 0:
                            item_.shift -= QNodePath.base_shift
                            item_.draw()
                else:
                    item.shift = max_shift
                    for item_ in set(item.vertex1.out_lines).intersection(set(item.vertex2.in_lines)):
                        if item_.shift > 0:
                            item_.shift -= QNodePath.base_shift
                            item_.draw()
                item.draw()
            item.vertex1.add_out_line(item)
            item.vertex2.add_in_line(item)
            if not load:
                self.check_component(item.vertex1.component_id)
        if isinstance(item, QNode):
            if not load:
                self.connected_components[self.connected_component_id] = [item]
            item.component_id = self.connected_component_id
            self.nodes.append(item)
            item.scene_ = self
            item.node_changed()
            if not load:
                self.check_component(item.component_id)
                self.connected_component_id += 1
        super().addItem(item)

    def remove_selected_items(self):
        for elem in self.selectedItems():
            self.removeItem(elem)

    def remove_component(self, component_id: int):
        for elem in self.connected_components[component_id]:
            self.removeItem(elem, all_component=True)
        self.connected_components.pop(component_id)

    def removeItem(self, item: QGraphicsItem, all_component: bool = False):
        if isinstance(item, QNodePath):
            item.vertex1.remove_out_line(item)
            item.vertex2.remove_in_line(item)
            if not all_component:
                self.connected_components.pop(item.vertex1.component_id)
                item.vertex1.component_id = self.connected_component_id
                self.connected_component_id += 1
                item.vertex2.component_id = self.connected_component_id
                self.connected_component_id += 1
                self._bfs(item.vertex1)
                self.check_component(item.vertex1.component_id)
                if item.vertex1.component_id != item.vertex2.component_id:
                    self._bfs(item.vertex2)
                    self.check_component(item.vertex2.component_id)
        if isinstance(item, QNode):
            for line in item.out_lines + item.in_lines:
                self.removeItem(line, all_component)
            self.nodes.remove(item)
            if not all_component:
                self.connected_components[item.component_id].remove(item)
                if not self.connected_components[item.component_id]:
                    self.connected_components.pop(item.component_id)
        super().removeItem(item)

    def _depth_recurs(self, node_out: str, node: Node, graph: InverterGraph, depths: dict[str, int]):
        if depths.get(node_out, None) is None:
            children_depth: list[int] = []
            for child in node.children:
                child_depth = depths.get(child.name, None)
                if child_depth is not None:
                    children_depth.append(depths[child.name])
                else:
                    if child.name in ["1", "0"]:
                        children_depth.append(0)
                    else:
                        children_depth.append(self._depth_recurs(child.name, graph.nodes[child.name], graph, depths))
            depths[node_out] = max(children_depth) + 1
            return depths[node_out]
        return 0

    def _bfs(self, start: QNode):
        self.connected_components[start.component_id] = [start]
        q: deque[QNode] = deque()
        visited = {}
        for node in self.nodes:
            visited[node] = False
        visited[start] = True
        q.append(start)
        while q:
            curr = q.popleft()
            for x in [line.vertex1 for line in curr.in_lines] + [line.vertex2 for line in curr.out_lines]:
                if not visited[x]:
                    visited[x] = True
                    q.append(x)
                    x.component_id = start.component_id
                    self.connected_components[start.component_id].append(x)

    def _sorting_nodes(self, x: QNode):
        value = re.split(r"(\d+)", x.name.text())
        value.pop()
        if len(value) == 2:
            return (x.depth, value[0], int(value[1]))
        return (
            x.depth,
            x.name.text(),
        )


class GraphView(QGraphicsView):
    def __init__(self, parent: Graph) -> None:
        super().__init__(parent)
        self.parent_ = parent
        self.first_node: QNode | None = None
        self.second_node: QNode | None = None
        self.copied_nodes: dict[QNode, QNode] = {}
        self.copied_lines: list[QNodePath] = []
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSceneRect(-10000, -10000, 20000, 20000)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.mouse_hold = False

        self.arrow_cursor = QToolButton(self)
        self.arrow_cursor.setIcon(QIcon("./mk_eda/tools/graph_editor/images/cursor.png"))
        self.arrow_cursor.setCheckable(True)
        self.arrow_cursor.clicked.connect(self.change_dragmode_arrow)
        self.eraser_cursor_image = QCursor(QPixmap("./mk_eda/tools/graph_editor/images/eraser32.png"), 9, 31)
        self.eraser_cursor = QToolButton(self)
        self.eraser_cursor.setIcon(QIcon("./mk_eda/tools/graph_editor/images/eraser512.png"))
        self.eraser_cursor.setCheckable(True)
        self.eraser_cursor.clicked.connect(self.change_dragmode_eraser)
        self.hand_cursor = QToolButton(self)
        self.hand_cursor.setIcon(QIcon("./mk_eda/tools/graph_editor/images/palm.png"))
        self.hand_cursor.setCheckable(True)
        self.hand_cursor.setChecked(True)
        self.hand_cursor.clicked.connect(self.change_dragmode_hand)

        self.temp_line_item = None
        self.line_select = QToolButton(self)
        self.line_select.setCheckable(True)
        self.dashed_line_icon = QIcon("./mk_eda/tools/graph_editor/images/neg_line512.png")
        self.dashed_line_cursor = QCursor(QPixmap("./mk_eda/tools/graph_editor/images/neg_line32.png"), 0, 32)
        self.solid_line_icon = QIcon("./mk_eda/tools/graph_editor/images/line512.png")
        self.solid_line_cursor = QCursor(QPixmap("./mk_eda/tools/graph_editor/images/line32.png"), 0, 32)
        self.line_select_menu = QMenu(self)
        self.dashed_line_action = QAction(self.dashed_line_icon, "negative edge", self)
        self.dashed_line_action.triggered.connect(self.set_dashed_line)
        self.solid_line_action = QAction(self.solid_line_icon, "positive edge", self)
        self.solid_line_action.triggered.connect(self.set_solid_line)
        self.line_select_menu.addActions([self.solid_line_action, self.dashed_line_action])
        self.line_select.setMenu(self.line_select_menu)
        self.line_select.setIcon(self.solid_line_icon)
        self.line_type = True
        self.line_select.clicked.connect(self.change_line)

    def export_json(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", "./", "JSON (*.json)")
        if not filename:
            return
        file = open(filename, "w")
        graph = self.parent_.to_InverterGraph()._to_raw()  # type: ignore
        json.dump(graph, file, indent=4)
        file.close()

    def load_json(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "./", "JSON (*.json)")
        if not filename:
            return
        file = open(filename)
        graph_raw = json.load(file)
        file.close()
        graph = InverterGraph()
        graph._from_raw(graph_raw)  # type: ignore
        self.parent_.from_InverterGraph(graph)

    def _create_node(self, pos: QPointF):
        dialog_node = DialogNode("Node create", self)
        accepted = dialog_node.exec()
        if accepted:
            if dialog_node.name_line_edit.text() and (
                dialog_node.type_box.currentText() == "input"
                or (dialog_node.type_box.currentText() == "const" and dialog_node.name_line_edit.text() in ["0", "1"])
                or dialog_node.name_line_edit.text() not in [n.name.text() for n in self.parent_.nodes]
            ):
                self.parent_.addItem(
                    QNode(
                        pos.x() - QNode.diameter / 2,
                        pos.y() - QNode.diameter / 2,
                        dialog_node.name_line_edit.text(),
                        dialog_node.type_box.currentText(),
                        dialog_node.check_box.isChecked(),
                    )
                )
            else:
                error = QMessageBox(
                    QMessageBox.Icon.Critical,
                    "Error",
                    "Name can't be same or empty",
                    parent=self,
                )
                error.exec()

    def _choose_node(self, event: QMouseEvent):
        if not self.first_node:
            items = [i for i in self.items(event.position().toPoint()) if type(i) is QNode]
            if items:
                item = items[0]
                self.first_node = item
                self.temp_line_item = QGraphicsLineItem()
                self.temp_line_item.setPen(QNodePath.pens[self.line_type])
                self.temp_line_item.setZValue(-1)
                self.parent_.addItem(self.temp_line_item)
        elif not self.second_node:
            items = [i for i in self.items(event.position().toPoint()) if type(i) is QNode]
            if items:
                item = items[0]
                self.second_node = item
            else:
                if self.temp_line_item:
                    self.parent_.removeItem(self.temp_line_item)
                    self.temp_line_item = None
                    self.first_node = None

    def init_function_menu(self, tool_button: QToolButton):
        menu = Functions_menu(self)
        menu.complex_optimizeXAIG_action.triggered.connect(
            partial(self.parent_.call_function, XAIGComplexityOptimizer().__call__)  # type: ignore
            #  Не приводит тип XorAndInverterGraph к InverterGraph
        )
        menu.depth_optimizeXAIG_action.triggered.connect(
            partial(self.parent_.call_function, XAIGDepthOptimizer().__call__)  # type: ignore
        )
        depth_actions: list[QAction] = []
        if self.parent_.nodes:
            for i in range(
                1,
                max([elem.depth for elem in self.parent_.nodes]),
            ):
                depth_actions.append(QAction(str(i), menu.depth_choosing))
                depth_actions[-1].triggered.connect(
                    partial(
                        self.parent_.depth_partion,
                        partial(depth_partitioner, depth=i),
                    )
                )
            menu.depth_choosing.addActions(depth_actions)
        tool_button.setMenu(menu)
        tool_button.showMenu()
        tool_button.setMenu(QMenu())

    def change_dragmode_eraser(self):
        self.parent_.clearSelection()
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setCursor(self.eraser_cursor_image)
        self.arrow_cursor.setChecked(False)
        self.hand_cursor.setChecked(False)
        self.eraser_cursor.setChecked(True)
        self.line_select.setChecked(False)

    def change_dragmode_hand(self):
        self.unsetCursor()
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.arrow_cursor.setChecked(False)
        self.eraser_cursor.setChecked(False)
        self.hand_cursor.setChecked(True)
        self.line_select.setChecked(False)

    def change_dragmode_arrow(self):
        self.unsetCursor()
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.arrow_cursor.setChecked(True)
        self.hand_cursor.setChecked(False)
        self.eraser_cursor.setChecked(False)
        self.line_select.setChecked(False)

    def change_line(self):
        self.line_select.setChecked(not self.line_select.isChecked())
        self.line_select.showMenu()

    def set_line(self):
        self.parent_.clearSelection()
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.line_select.setChecked(True)
        self.arrow_cursor.setChecked(False)
        self.hand_cursor.setChecked(False)
        self.eraser_cursor.setChecked(False)

    def set_dashed_line(self):
        self.line_type = False
        self.line_select.setIcon(self.dashed_line_icon)
        self.set_line()
        self.setCursor(self.dashed_line_cursor)

    def set_solid_line(self):
        self.line_type = True
        self.line_select.setIcon(self.solid_line_icon)
        self.set_line()
        self.setCursor(self.solid_line_cursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.line_select.isChecked():
            if self.first_node and self.temp_line_item:
                start = self.first_node.pos() + QPointF(QNode.diameter / 2, QNode.diameter / 2)
                temp_line = QLineF(start, self.mapToScene(event.position().toPoint()))
                self.temp_line_item.setLine(temp_line)
            return
        if self.eraser_cursor.isChecked():
            if self.mouse_hold:
                for item in self.items(event.position().toPoint()):
                    if type(item) is QNode:
                        self.parent_.removeItem(item)
                        return
                for item in self.items(event.position().toPoint()):
                    if type(item) is QNodePath:
                        self.parent_.removeItem(item)
                        return
            return
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if self.eraser_cursor.isChecked() or self.line_select.isChecked():
            return
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_hold = True
            if self.eraser_cursor.isChecked():
                return
            if self.line_select.isChecked():
                self._choose_node(event)
                if self.second_node and self.first_node:
                    if self.line_type:
                        node_path = QNodePath(self.first_node, self.second_node, 1)
                        self.parent_.addItem(node_path)
                    else:
                        node_path = QNodePath(self.first_node, self.second_node, 0)
                        self.parent_.addItem(node_path)
                    self.first_node = None
                    self.second_node = None
                    if self.temp_line_item:
                        self.parent_.removeItem(self.temp_line_item)
                        self.temp_line_item = None
                return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_hold = False
        if event.button() == Qt.MouseButton.RightButton and not self.itemAt(event.position().toPoint()):
            menu = RMB_menu_space(self)
            menu.create_node_action.triggered.connect(
                partial(self._create_node, self.mapToScene(event.position().toPoint()))
            )
            menu.clear_scene_action.triggered.connect(self.parent_.clear)
            menu.exec(event.globalPosition().toPoint())
            return
        super().mouseReleaseEvent(event)

    _zooming_queue: list[tuple[QTimeLine, int]] = []

    def wheelEvent(self, event: QWheelEvent):
        timeline = QTimeLine(100, self)
        timeline.setUpdateInterval(10)
        zoom = 1 if event.angleDelta().y() > 0 else -1
        timeline.valueChanged.connect(partial(self.zooming_scene, zoom, event.position().toPoint()))
        timeline.finished.connect(self.zoom_finished)
        if (
            GraphView._zooming_queue
            and GraphView._zooming_queue[-1][0].state() == QTimeLine.State.NotRunning
            and zoom == -GraphView._zooming_queue[-1][1]
        ):
            GraphView._zooming_queue.pop()
            return
        GraphView._zooming_queue.append((timeline, zoom))
        if len(GraphView._zooming_queue) == 1:
            timeline.start()

    def zoom_finished(self):
        if GraphView._zooming_queue:
            timeline, _ = GraphView._zooming_queue.pop(0)
            if timeline.state() == QTimeLine.State.NotRunning:
                timeline.start()

    def zooming_scene(self, zoom: int, pos: QPoint, value: int):
        contents_rect = self.contentsRect()
        tl = self.mapToScene(contents_rect.topLeft() + QPoint(1, 1))
        br = self.mapToScene(contents_rect.bottomRight() - QPoint(2, 2))
        new_rect = QRectF(tl, br)
        width = (br.x() - tl.x()) / 2
        height = (br.y() - tl.y()) / 2
        base_mov = width / 60

        if new_rect.width() + 2 * base_mov > self.sceneRect().width() and zoom < 0:
            return

        mov = self.mapToScene(pos) - new_rect.center()

        base_mov_x = base_mov
        base_mov_y = base_mov * height / width

        new_rect.setLeft(new_rect.left() + zoom * base_mov_x * (1 + mov.x() / width))
        new_rect.setRight(new_rect.right() - zoom * base_mov_x * (1 - mov.x() / width))
        new_rect.setTop(new_rect.top() + zoom * base_mov_y * (1 + mov.y() / height))
        new_rect.setBottom(new_rect.bottom() - zoom * base_mov_y * (1 - mov.y() / height))
        self.fitInView(new_rect, Qt.AspectRatioMode.IgnoreAspectRatio)

    def keyPressEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            event.ignore()
            return
        if event.key() == Qt.Key.Key_Delete:
            self.parent_.remove_selected_items()
        if event.key() == Qt.Key.Key_C and event.modifiers().ControlModifier:
            items = self.parent_.selectedItems()
            self.copied_nodes = {}
            self.copied_lines = []
            if items:
                copied_items = [item for item in items if isinstance(item, QNode)]
                item = copied_items[0]
                shift = item.pos() + QPointF(QNode.diameter / 2, QNode.diameter / 2)
                in_lines: list[QNodePath] = []
                out_lines: list[QNodePath] = []
                for item in copied_items:
                    new_item = QNode(
                        item.x() - shift.x(),
                        item.y() - shift.y(),
                        item.name.text(),
                        item.node_type.text(),
                        item.out_flag,
                    )
                    self.copied_nodes[item] = new_item
                    in_lines += item.in_lines
                    out_lines += item.out_lines
                for line in set(in_lines).intersection(set(out_lines)):
                    self.copied_lines.append(
                        QNodePath(
                            self.copied_nodes[line.vertex1],
                            self.copied_nodes[line.vertex2],
                            line.n,
                        )
                    )
        if event.key() == Qt.Key.Key_V and event.modifiers().ControlModifier:
            if self.copied_nodes:
                old_nodes = list(self.copied_nodes.values())
                old_lines = list(self.copied_lines)
                self.copied_nodes = {}
                self.copied_lines = []
                for item in old_nodes:
                    self.parent_.addItem(item)
                    self.copied_nodes[item] = QNode(
                        item.x(),
                        item.y(),
                        item.name.text(),
                        item.node_type.text(),
                        item.out_flag,
                    )
                    item.moveBy(*(self.mapToScene(self.mapFromGlobal(self.cursor().pos())).toTuple()))  # type: ignore
                for line in old_lines:
                    self.parent_.addItem(line)
                    self.copied_lines.append(
                        QNodePath(
                            self.copied_nodes[line.vertex1],
                            self.copied_nodes[line.vertex2],
                            line.n,
                        )
                    )
                    line.draw()

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            event.ignore()
            return
        if event.key() == Qt.Key.Key_Space:
            if len(self.parent_.selectedItems()) >= 1:
                items = self.parent_.selectedItems()
                components = {item.component_id for item in items if isinstance(item, QNode)}
                for component_id in components:
                    for node in self.parent_.connected_components[component_id]:
                        node.setSelected(True)
        if event.key() == Qt.Key.Key_CapsLock:
            if self.dragMode() == QGraphicsView.DragMode.RubberBandDrag:
                self.change_dragmode_hand()
            else:
                self.change_dragmode_arrow()
        super().keyReleaseEvent(event)


class LogWidget(QPlainTextEdit):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 12))

    def write(self, text: str):
        self.moveCursor(QTextCursor.MoveOperation.End, mode=QTextCursor.MoveMode.MoveAnchor)
        self.insertPlainText(text)

    def flush(self):
        return


class CentralWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.graph = Graph()

        self.graph_view = GraphView(self.graph)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.splitter = QSplitter(self)
        self.splitter.setOrientation(Qt.Orientation.Vertical)

        self.splitter.addWidget(self.graph_view)

        self.log = LogWidget(self)
        sys.stdout = self.log
        sys.stderr = self.log
        handler = logging.StreamHandler(self.log)
        strfmt = "[%(asctime)s] [%(name)s] [%(levelname)s] > %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(fmt=strfmt, datefmt=datefmt)
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

        self.splitter.addWidget(self.log)
        self.main_layout.addWidget(self.splitter)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            event.ignore()
            return
        if event.key() == Qt.Key.Key_Escape:
            print(
                "Компоненты связности: "
                + str(
                    [
                        (component_id, [x.name.text() for x in component])
                        for component_id, component in self.graph.connected_components.items()
                    ]
                )
            )
            self.graph.to_InverterGraph().print()


class MainWindow(QMainWindow):
    def __init__(self, widget: CentralWidget) -> None:
        super().__init__()
        self.setWindowTitle("Graph vizualizer")

        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        self.toolbar = QToolBar("Toolbar", self)
        self.toolbar.setIconSize(QSize(24, 24))
        self.toolbar.toggleViewAction().setVisible(False)
        self.addToolBar(self.toolbar)

        self.exit_action = QAction(QIcon("./mk_eda/tools/graph_editor/images/exit.png"), "Exit", self)
        self.save_graph_action = QAction(
            QIcon("./mk_eda/tools/graph_editor/images/save.png"),
            "Save graph to .json",
            self,
        )
        self.load_graph_action = QAction(
            QIcon("./mk_eda/tools/graph_editor/images/folder.png"),
            "Load graph from .json",
            self,
        )
        self.clear_action = QAction(QIcon("./mk_eda/tools/graph_editor/images/delete.png"), "Clear", self)
        self.call_function_button = QToolButton(self)
        self.call_function_button.setIcon(QIcon("./mk_eda/tools/graph_editor/images/tree.png"))

        self.file_menu.addActions([self.exit_action, self.save_graph_action, self.load_graph_action])
        self.toolbar.addActions([self.exit_action])
        self.toolbar.addSeparator()
        self.toolbar.addWidget(widget.graph_view.arrow_cursor)
        self.toolbar.addWidget(widget.graph_view.hand_cursor)
        self.toolbar.addWidget(widget.graph_view.eraser_cursor)
        self.toolbar.addWidget(widget.graph_view.line_select)
        self.toolbar.addSeparator()
        self.toolbar.addActions([self.load_graph_action, self.save_graph_action])
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.call_function_button)
        self.toolbar.addActions([self.clear_action])

        self.exit_action.triggered.connect(self.close)
        self.exit_action.setToolTip("Exit")
        self.exit_action.setShortcut("Ctrl+Q")

        self.save_graph_action.triggered.connect(widget.graph_view.export_json)
        self.save_graph_action.setToolTip("Save file")

        self.load_graph_action.triggered.connect(widget.graph_view.load_json)
        self.load_graph_action.setToolTip("Open file")

        self.clear_action.triggered.connect(widget.graph_view.parent_.clear)
        self.clear_action.setToolTip("Clear scene")

        self.call_function_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.call_function_button.pressed.connect(
            partial(widget.graph_view.init_function_menu, self.call_function_button)
        )
        self.call_function_button.setToolTip("Call function")

        self.setCentralWidget(widget)


if __name__ == "__main__":
    app = QApplication()

    central_widget = CentralWidget()
    window = MainWindow(central_widget)
    window.resize(1200, 900)
    window.show()

    sys.exit(app.exec())
