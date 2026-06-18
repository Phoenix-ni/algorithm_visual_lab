from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from .algorithms import InputError, algorithm_list, compare_sort, get_algorithm, run_cnn
from .digit_cnn import run_drawn_digit_cnn
from .models import (
    CnnCanvasRequest,
    CnnRequest,
    CustomData,
    CustomDataCreate,
    ExportLogRequest,
    ExportLogResponse,
    RunRequest,
    RunResponse,
    SortCompareRequest,
    TestCase,
)
from .storage import JsonStore


BASE_DIR = Path(__file__).resolve().parents[1]
store = JsonStore(BASE_DIR / "data")

app = FastAPI(title="算法过程可视化实验平台 API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/algorithms")
def list_algorithms() -> list:
    return algorithm_list()


@app.get("/api/algorithms/{algorithm_id}/cases")
def list_cases(algorithm_id: str) -> list[TestCase]:
    try:
        return get_algorithm(algorithm_id).info.test_cases
    except InputError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/algorithms/{algorithm_id}/random")
def random_input(algorithm_id: str) -> dict[str, str]:
    try:
        return {"input": get_algorithm(algorithm_id).random_input()}
    except InputError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/algorithms/{algorithm_id}/run")
def run_algorithm(algorithm_id: str, payload: RunRequest) -> RunResponse:
    try:
        return get_algorithm(algorithm_id).run(payload.input)
    except InputError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/custom-data")
def list_custom_data(algorithm_id: str | None = Query(default=None)) -> list[CustomData]:
    return store.list_custom_data(algorithm_id)


@app.post("/api/custom-data")
def create_custom_data(payload: CustomDataCreate) -> CustomData:
    try:
        get_algorithm(payload.algorithm_id)
    except InputError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return store.create_custom_data(payload)


@app.delete("/api/custom-data/{item_id}")
def delete_custom_data(item_id: int) -> dict[str, bool]:
    deleted = store.delete_custom_data(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="未找到自定义数据。")
    return {"deleted": True}


@app.post("/api/logs/export")
def export_log(payload: ExportLogRequest) -> ExportLogResponse:
    try:
        algorithm = get_algorithm(payload.algorithm_id).info
    except InputError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    lines = [
        f"算法：{algorithm.title}",
        f"类型：{algorithm.type}",
        f"时间复杂度：{algorithm.time_complexity}",
        f"空间复杂度：{algorithm.space_complexity}",
        f"输入：{payload.input}",
        "",
        "指标：",
        *[f"- {key}: {value}" for key, value in payload.metrics.items()],
        "",
        "结果：",
        str(payload.result),
        "",
        "执行步骤：",
        *[f"{step.index}. [{step.phase}] {step.message}" for step in payload.steps],
    ]
    return ExportLogResponse(filename=f"{payload.algorithm_id}-log.txt", content="\n".join(lines))


@app.post("/api/logs/export.txt", response_class=PlainTextResponse)
def export_log_text(payload: ExportLogRequest) -> str:
    return export_log(payload).content


@app.post("/api/compare/sort")
def compare_sort_endpoint(payload: SortCompareRequest) -> dict:
    try:
        return compare_sort(payload.input)
    except InputError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/cnn/predict")
def cnn_predict(payload: CnnRequest) -> RunResponse:
    try:
        return run_cnn(payload.sample)
    except InputError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/cnn/visualize")
def cnn_visualize(payload: CnnRequest) -> RunResponse:
    return cnn_predict(payload)


@app.post("/api/cnn/draw-predict")
def cnn_draw_predict(payload: CnnCanvasRequest) -> RunResponse:
    try:
        return run_drawn_digit_cnn(payload.image)
    except InputError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
