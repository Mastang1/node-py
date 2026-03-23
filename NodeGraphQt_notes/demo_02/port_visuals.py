"""
Custom port painting: flow vs data, direction, and data-type shapes (LabVIEW-inspired).

Shapes (quick recognition):
- Flow input: rounded rectangle (control entry)
- Flow output: outward-pointing triangle (execution leaves)
- Data handle: diamond
- Data bool/int: square
- Data float/str/enum/any: ellipse
- Data var_ref: upward triangle (reference)
"""

from __future__ import annotations

from typing import Any, Callable

from Qt import QtCore, QtGui

from .common import normalize_data_type


def _resolve_colors(info: dict[str, Any]) -> tuple[QtGui.QColor, QtGui.QColor]:
    fill = QtGui.QColor(*info["color"]) if isinstance(info.get("color"), (list, tuple)) else QtGui.QColor(120, 120, 120)
    border = QtGui.QColor(*info["border_color"]) if isinstance(info.get("border_color"), (list, tuple)) else QtGui.QColor(200, 200, 200)
    if info.get("hovered"):
        fill = QtGui.QColor(255, 255, 255, 230)
        border = QtGui.QColor(255, 220, 120)
    elif info.get("connected"):
        fill = QtGui.QColor(255, 255, 255, 210)
        border = QtGui.QColor(96, 165, 250)
    return fill, border


def paint_flow_input_port(painter: QtGui.QPainter, port_rect: QtCore.QRectF, info: dict[str, Any]) -> None:
    """Wide rounded rect — reads as 'control / sequence' port."""
    fill, border = _resolve_colors(info)
    pen = QtGui.QPen(border, 1.8)
    painter.setPen(pen)
    painter.setBrush(fill)
    r = port_rect.adjusted(-1, 1, 1, -1)
    painter.drawRoundedRect(r, 4, 4)


def paint_flow_output_port(painter: QtGui.QPainter, port_rect: QtCore.QRectF, info: dict[str, Any]) -> None:
    """Triangle pointing along +X (wire exits to the right)."""
    fill, border = _resolve_colors(info)
    pen = QtGui.QPen(border, 1.8)
    painter.setPen(pen)
    painter.setBrush(fill)
    c = port_rect.center()
    w, h = port_rect.width(), port_rect.height()
    path = QtGui.QPainterPath()
    path.moveTo(c.x() - w * 0.35, c.y() - h * 0.45)
    path.lineTo(c.x() + w * 0.55, c.y())
    path.lineTo(c.x() - w * 0.35, c.y() + h * 0.45)
    path.closeSubpath()
    painter.drawPath(path)


def _shape_kind(data_type: str) -> str:
    t = normalize_data_type(data_type)
    if t == "handle":
        return "diamond"
    if t in {"bool", "int"}:
        return "square"
    if t == "var_ref":
        return "triangle_up"
    return "ellipse"


def make_data_port_painter(data_type: str) -> Callable[[QtGui.QPainter, QtCore.QRectF, dict[str, Any]], None]:
    kind = _shape_kind(data_type)

    def paint(painter: QtGui.QPainter, port_rect: QtCore.QRectF, info: dict[str, Any]) -> None:
        fill, border = _resolve_colors(info)
        pen = QtGui.QPen(border, 1.6)
        painter.setPen(pen)
        painter.setBrush(fill)
        c = port_rect.center()
        w, h = port_rect.width(), port_rect.height()

        if kind == "diamond":
            path = QtGui.QPainterPath()
            path.moveTo(c.x(), c.y() - h * 0.5)
            path.lineTo(c.x() + w * 0.48, c.y())
            path.lineTo(c.x(), c.y() + h * 0.5)
            path.lineTo(c.x() - w * 0.48, c.y())
            path.closeSubpath()
            painter.drawPath(path)
        elif kind == "square":
            painter.drawRect(port_rect.adjusted(1, 1, -1, -1))
        elif kind == "triangle_up":
            path = QtGui.QPainterPath()
            path.moveTo(c.x(), c.y() - h * 0.5)
            path.lineTo(c.x() + w * 0.45, c.y() + h * 0.42)
            path.lineTo(c.x() - w * 0.45, c.y() + h * 0.42)
            path.closeSubpath()
            painter.drawPath(path)
        else:
            painter.drawEllipse(port_rect.adjusted(0.5, 0.5, -0.5, -0.5))

    return paint


def flow_input_color() -> tuple[int, int, int]:
    return 251, 191, 36  # amber


def flow_output_color() -> tuple[int, int, int]:
    return 45, 212, 191  # teal
