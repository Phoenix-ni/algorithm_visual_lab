from __future__ import annotations

import gzip
import json
import struct
import sys
import urllib.request
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.digit_cnn import MODEL_PATH, MnistCnn, center_by_mass, shift_image  # noqa: E402


MNIST_DIR = ROOT / "data" / "mnist"
MNIST_URLS = {
    "train_images": "https://storage.googleapis.com/cvdf-datasets/mnist/train-images-idx3-ubyte.gz",
    "train_labels": "https://storage.googleapis.com/cvdf-datasets/mnist/train-labels-idx1-ubyte.gz",
    "test_images": "https://storage.googleapis.com/cvdf-datasets/mnist/t10k-images-idx3-ubyte.gz",
    "test_labels": "https://storage.googleapis.com/cvdf-datasets/mnist/t10k-labels-idx1-ubyte.gz",
}
MEAN = 0.1307
STD = 0.3081


class MnistIdxDataset(Dataset):
    def __init__(self, images: np.ndarray, labels: np.ndarray, train: bool = False) -> None:
        self.images = images.astype(np.float32)
        self.labels = labels.astype(np.int64)
        self.train = train

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        image = self.images[index].copy()
        if self.train:
            image = augment_image(image)
        tensor = torch.from_numpy(image).float().unsqueeze(0)
        tensor = (tensor - MEAN) / STD
        return tensor, torch.tensor(int(self.labels[index]), dtype=torch.long)


def augment_image(image: np.ndarray) -> np.ndarray:
    if np.random.random() < 0.7:
        image = shift_image(image, int(np.random.randint(-2, 3)), int(np.random.randint(-2, 3)))
    if np.random.random() < 0.25:
        image = np.clip(image + np.random.normal(0, 0.025, size=image.shape), 0.0, 1.0)
    return image.astype(np.float32)


def download_mnist() -> None:
    MNIST_DIR.mkdir(parents=True, exist_ok=True)
    for filename, url in MNIST_URLS.items():
        path = MNIST_DIR / f"{filename}.gz"
        if path.exists() and path.stat().st_size > 0:
            continue
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, path)


def read_idx_images(path: Path) -> np.ndarray:
    with gzip.open(path, "rb") as handle:
        magic, count, rows, cols = struct.unpack(">IIII", handle.read(16))
        if magic != 2051:
            raise ValueError(f"Invalid image file: {path}")
        data = np.frombuffer(handle.read(), dtype=np.uint8)
    images = data.reshape(count, rows, cols).astype(np.float32) / 255.0
    return np.array([center_by_mass(image) for image in images], dtype=np.float32)


def read_idx_labels(path: Path) -> np.ndarray:
    with gzip.open(path, "rb") as handle:
        magic, count = struct.unpack(">II", handle.read(8))
        if magic != 2049:
            raise ValueError(f"Invalid label file: {path}")
        data = np.frombuffer(handle.read(), dtype=np.uint8)
    return data.reshape(count).astype(np.int64)


def load_mnist() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    download_mnist()
    train_x = read_idx_images(MNIST_DIR / "train_images.gz")
    train_y = read_idx_labels(MNIST_DIR / "train_labels.gz")
    test_x = read_idx_images(MNIST_DIR / "test_images.gz")
    test_y = read_idx_labels(MNIST_DIR / "test_labels.gz")
    return train_x, train_y, test_x, test_y


def evaluate(model: nn.Module, loader: DataLoader, device: torch.device) -> float:
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)
            logits = model(images)
            predictions = logits.argmax(dim=1)
            correct += int((predictions == labels).sum().item())
            total += int(labels.numel())
    return correct / total


def train() -> dict[str, float | int | str]:
    torch.manual_seed(42)
    np.random.seed(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_x, train_y, test_x, test_y = load_mnist()
    train_loader = DataLoader(
        MnistIdxDataset(train_x, train_y, train=True),
        batch_size=256,
        shuffle=True,
        num_workers=2,
        pin_memory=device.type == "cuda",
    )
    train_eval_loader = DataLoader(MnistIdxDataset(train_x, train_y), batch_size=512, shuffle=False)
    test_loader = DataLoader(MnistIdxDataset(test_x, test_y), batch_size=512, shuffle=False)

    model = MnistCnn().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0012, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.45)
    criterion = nn.CrossEntropyLoss()
    epochs = 7

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for images, labels in train_loader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            logits = model(images)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            running_loss += float(loss.item()) * int(labels.numel())
        scheduler.step()
        test_accuracy = evaluate(model, test_loader, device)
        print(
            f"epoch {epoch + 1}/{epochs} "
            f"loss={running_loss / len(train_loader.dataset):.4f} "
            f"test={test_accuracy:.4f}"
        )

    train_accuracy = evaluate(model, train_eval_loader, device)
    test_accuracy = evaluate(model, test_loader, device)
    metadata = {
        "dataset": "MNIST handwritten digits 28x28",
        "architecture": "PyTorch Conv16 -> Conv32 -> FC128 -> FC10",
        "input_size": 28,
        "digit_size": 20,
        "mean": MEAN,
        "std": STD,
        "epochs": epochs,
        "train_samples": int(len(train_x)),
        "test_samples": int(len(test_x)),
        "train_accuracy": round(float(train_accuracy), 4),
        "test_accuracy": round(float(test_accuracy), 4),
        "train_device": str(device),
        "torch_version": str(torch.__version__),
    }
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model_state": model.cpu().state_dict(), "metadata": metadata}, MODEL_PATH)
    return metadata


if __name__ == "__main__":
    metrics = train()
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
