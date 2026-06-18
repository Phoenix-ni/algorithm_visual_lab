from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from .algorithms import InputError, make_step, round_matrix
from .models import RunResponse, Step


MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "digit_cnn_model.pt"


class MnistCnn(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(32 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x: torch.Tensor, return_features: bool = False) -> Any:
        conv1 = self.conv1(x)
        relu1 = F.relu(conv1)
        pool1 = F.max_pool2d(relu1, 2)
        conv2 = self.conv2(pool1)
        relu2 = F.relu(conv2)
        pool2 = F.max_pool2d(relu2, 2)
        flat = torch.flatten(pool2, 1)
        hidden = F.relu(self.fc1(flat))
        logits = self.fc2(hidden)
        if return_features:
            return logits, {
                "conv1": conv1,
                "relu1": relu1,
                "pool1": pool1,
                "conv2": conv2,
                "relu2": relu2,
                "pool2": pool2,
            }
        return logits


@lru_cache(maxsize=1)
def load_digit_model() -> tuple[MnistCnn, dict[str, Any]]:
    if not MODEL_PATH.exists():
        raise InputError("未找到 PyTorch CNN 模型文件，请先运行 backend/ml/train_digit_cnn.py。")
    checkpoint = torch.load(MODEL_PATH, map_location="cpu", weights_only=False)
    model = MnistCnn()
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    metadata = checkpoint.get("metadata", {})
    return model, metadata


def validate_canvas_image(image: list[list[float]]) -> np.ndarray:
    if len(image) != 28 or any(len(row) != 28 for row in image):
        raise InputError("画板输入需要是 28x28 灰度矩阵。")
    matrix = np.array(image, dtype=np.float32)
    if not np.isfinite(matrix).all():
        raise InputError("画板数据包含非法数值。")
    matrix = np.clip(matrix, 0.0, 1.0)
    if float(matrix.max()) < 0.03:
        raise InputError("请先在画板上写一个数字。")
    return matrix


def preprocess_canvas(image: np.ndarray, output_size: int = 28, digit_size: int = 20) -> np.ndarray:
    ys, xs = np.where(image > 0.05)
    if len(xs) == 0 or len(ys) == 0:
        raise InputError("请先在画板上写一个数字。")
    top = max(int(ys.min()) - 2, 0)
    bottom = min(int(ys.max()) + 3, image.shape[0])
    left = max(int(xs.min()) - 2, 0)
    right = min(int(xs.max()) + 3, image.shape[1])
    crop = image[top:bottom, left:right]
    side = max(crop.shape)
    square = np.zeros((side, side), dtype=np.float32)
    y_offset = (side - crop.shape[0]) // 2
    x_offset = (side - crop.shape[1]) // 2
    square[y_offset : y_offset + crop.shape[0], x_offset : x_offset + crop.shape[1]] = crop
    target_digit = min(digit_size, output_size)
    resized = resize_bilinear(square, target_digit, target_digit)
    if resized.max() > 0:
        resized = resized / resized.max()
    canvas = np.zeros((output_size, output_size), dtype=np.float32)
    place_top = (output_size - target_digit) // 2
    place_left = (output_size - target_digit) // 2
    canvas[place_top : place_top + target_digit, place_left : place_left + target_digit] = resized
    return center_by_mass(np.clip(canvas, 0.0, 1.0)).astype(np.float32)


def center_by_mass(image: np.ndarray) -> np.ndarray:
    total = float(image.sum())
    if total <= 0:
        return image
    rows, cols = np.indices(image.shape)
    center_y = float((rows * image).sum() / total)
    center_x = float((cols * image).sum() / total)
    target = (image.shape[0] - 1) / 2
    shift_y = int(round(target - center_y))
    shift_x = int(round(target - center_x))
    return shift_image(image, shift_y, shift_x)


def shift_image(image: np.ndarray, shift_y: int, shift_x: int) -> np.ndarray:
    shifted = np.zeros_like(image)
    src_y0 = max(0, -shift_y)
    src_y1 = min(image.shape[0], image.shape[0] - shift_y)
    src_x0 = max(0, -shift_x)
    src_x1 = min(image.shape[1], image.shape[1] - shift_x)
    dst_y0 = max(0, shift_y)
    dst_y1 = min(image.shape[0], image.shape[0] + shift_y)
    dst_x0 = max(0, shift_x)
    dst_x1 = min(image.shape[1], image.shape[1] + shift_x)
    shifted[dst_y0:dst_y1, dst_x0:dst_x1] = image[src_y0:src_y1, src_x0:src_x1]
    return shifted


def resize_bilinear(image: np.ndarray, out_h: int, out_w: int) -> np.ndarray:
    in_h, in_w = image.shape
    output = np.zeros((out_h, out_w), dtype=np.float32)
    for row in range(out_h):
        src_y = (row + 0.5) * in_h / out_h - 0.5
        y0 = max(int(np.floor(src_y)), 0)
        y1 = min(y0 + 1, in_h - 1)
        wy = src_y - y0
        for col in range(out_w):
            src_x = (col + 0.5) * in_w / out_w - 0.5
            x0 = max(int(np.floor(src_x)), 0)
            x1 = min(x0 + 1, in_w - 1)
            wx = src_x - x0
            top = image[y0, x0] * (1 - wx) + image[y0, x1] * wx
            bottom = image[y1, x0] * (1 - wx) + image[y1, x1] * wx
            output[row, col] = top * (1 - wy) + bottom * wy
    return output


def normalize_tensor(image: np.ndarray, metadata: dict[str, Any]) -> torch.Tensor:
    mean = float(metadata.get("mean", 0.1307))
    std = float(metadata.get("std", 0.3081))
    tensor = torch.from_numpy(image).float().unsqueeze(0).unsqueeze(0)
    return (tensor - mean) / std


def tensor_matrix(tensor: torch.Tensor) -> list[list[float]]:
    return round_matrix(tensor.detach().cpu().numpy().astype(float).tolist())


def feature_maps_to_list(tensor: torch.Tensor, count: int = 4) -> list[list[list[float]]]:
    maps = tensor.detach().cpu()[0, :count]
    result = []
    for item in maps:
        item = item - item.min()
        if float(item.max()) > 0:
            item = item / item.max()
        result.append(tensor_matrix(item))
    return result


def run_drawn_digit_cnn(image: list[list[float]]) -> RunResponse:
    canvas = validate_canvas_image(image)
    model, metadata = load_digit_model()
    input_size = int(metadata.get("input_size", 28))
    digit_size = int(metadata.get("digit_size", 20))
    processed = preprocess_canvas(canvas, output_size=input_size, digit_size=digit_size)
    input_tensor = normalize_tensor(processed, metadata)
    with torch.no_grad():
        logits, features = model(input_tensor, return_features=True)
        probabilities_tensor = torch.softmax(logits, dim=1)[0]
    prediction = int(torch.argmax(probabilities_tensor).item())
    probabilities = [
        {"label": str(index), "value": round(float(value), 4)}
        for index, value in enumerate(probabilities_tensor.tolist())
    ]
    steps: list[Step] = []
    make_step(
        steps,
        "画板采样",
        "读取手写输入",
        "读取画板笔迹，转换为 28x28 灰度矩阵。",
        {"kind": "cnn", "stage": "canvas", "image": round_matrix(canvas.tolist()), "source": "drawn"},
        "画板中的黑色笔迹会被转换为 0 到 1 之间的灰度强度，背景接近 0。",
    )
    make_step(
        steps,
        "预处理",
        "裁剪并居中",
        f"根据笔迹边界裁剪数字区域，并缩放到 MNIST 模型使用的 {input_size}x{input_size} 输入。",
        {
            "kind": "cnn",
            "stage": "preprocess",
            "image": round_matrix(processed.tolist()),
            "metadata": metadata,
        },
        "预处理会把手写数字裁剪、缩放并按质心居中，使画板输入接近 MNIST 训练样本分布。",
    )
    make_step(
        steps,
        "第一层卷积",
        "提取边缘和笔画",
        "PyTorch CNN 的第一层卷积从 28x28 输入中提取局部笔画特征。",
        {
            "kind": "cnn",
            "stage": "conv",
            "image": round_matrix(processed.tolist()),
            "featureMaps": feature_maps_to_list(features["relu1"], 4),
        },
        "这些卷积核来自 MNIST 训练，不是手写规则；特征图亮处表示该卷积核响应更强。",
    )
    make_step(
        steps,
        "池化与深层卷积",
        "组合局部特征",
        "池化降低特征尺寸，第二层卷积组合更高层的数字结构。",
        {
            "kind": "cnn",
            "stage": "pool",
            "image": round_matrix(processed.tolist()),
            "featureMaps": feature_maps_to_list(features["pool2"], 4),
        },
        "深层特征已经不只是单条边缘，而是更接近数字局部结构的组合响应。",
    )
    make_step(
        steps,
        "模型推理",
        "输出分类概率",
        f"全连接层和 Softmax 输出概率，模型预测数字为 {prediction}。",
        {
            "kind": "cnn",
            "stage": "softmax",
            "image": round_matrix(processed.tolist()),
            "probabilities": probabilities,
            "prediction": prediction,
            "metadata": metadata,
        },
        "柱状图展示 0 到 9 的概率分布，最高的一项就是模型预测结果。",
    )
    return RunResponse(
        algorithm_id="cnn",
        input="drawn-canvas",
        result={
            "prediction": prediction,
            "probabilities": probabilities,
            "model": metadata,
        },
        steps=steps,
        metrics={
            "stepCount": len(steps),
            "testAccuracy": metadata.get("test_accuracy"),
            "trainSamples": metadata.get("train_samples"),
        },
    )
