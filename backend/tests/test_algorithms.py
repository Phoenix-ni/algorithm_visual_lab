from fastapi.testclient import TestClient

from app.algorithms import compare_sort, run_cnn, run_dijkstra, run_huffman, run_maze, run_quicksort
from app.digit_cnn import run_drawn_digit_cnn
from app.main import app


client = TestClient(app)


def test_quicksort_result_and_steps() -> None:
    response = run_quicksort("8, 3, 5, 1, 9, 2, 7")
    assert response.result["sorted"] == [1, 2, 3, 5, 7, 8, 9]
    assert len(response.steps) > 5
    assert response.metrics["compareCount"] > 0


def test_dijkstra_distances() -> None:
    response = run_dijkstra("A; A-B:4, A-C:2, C-B:1, B-D:5, C-D:8, C-E:10, D-E:2")
    assert response.result["distances"]["E"] == 10
    assert response.result["previous"]["E"] == "D"


def test_maze_finds_path() -> None:
    response = run_maze("0 0 0\n1 1 0\n0 0 0")
    assert response.result["solved"] is True
    assert response.steps[-1].phase == "完成"


def test_huffman_generates_codes() -> None:
    response = run_huffman("A:5, B:9, C:12, D:13, E:16, F:45")
    assert set(response.result["codes"]) == {"A", "B", "C", "D", "E", "F"}
    assert response.metrics["mergeCount"] == 5


def test_compare_sort_same_result() -> None:
    response = compare_sort("8, 3, 5, 1, 9, 2, 7")
    assert response["summary"]["sameResult"] is True
    assert response["summary"]["bubbleCompare"] >= response["summary"]["quickCompare"]


def test_cnn_has_probabilities() -> None:
    response = run_cnn("digit_3")
    probabilities = response.result["probabilities"]
    assert len(probabilities) == 10
    assert response.result["prediction"] == 3


def test_api_algorithm_run_validation() -> None:
    response = client.post("/api/algorithms/quicksort/run", json={"input": "1, 2"})
    assert response.status_code == 400
    assert "数组长度" in response.json()["detail"]


def test_drawn_digit_canvas_validation() -> None:
    blank = [[0.0 for _ in range(28)] for _ in range(28)]
    response = client.post("/api/cnn/draw-predict", json={"image": blank})
    assert response.status_code == 400
    assert "画板" in response.json()["detail"]


def test_drawn_digit_predicts_with_model() -> None:
    image = [[0.0 for _ in range(28)] for _ in range(28)]
    for row in range(4, 24):
        image[row][20] = 1.0
        image[row][19] = 0.9
    for col in range(8, 21):
        image[4][col] = 1.0
        image[13][col] = 1.0
        image[23][col] = 1.0
    response = run_drawn_digit_cnn(image)
    assert len(response.result["probabilities"]) == 10
    assert 0 <= response.result["prediction"] <= 9
