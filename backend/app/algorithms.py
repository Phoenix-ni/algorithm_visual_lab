from __future__ import annotations

import math
import random
from collections import defaultdict
from dataclasses import dataclass
from heapq import heappop, heappush
from typing import Any

from .models import AlgorithmInfo, RunResponse, Step, TestCase


class InputError(ValueError):
    """Raised when user input cannot be visualized safely."""


@dataclass(frozen=True)
class AlgorithmSpec:
    info: AlgorithmInfo
    random_input: Any
    run: Any


def make_step(
    steps: list[Step],
    phase: str,
    status: str,
    message: str,
    state: dict[str, Any],
    explain: str,
) -> None:
    steps.append(
        Step(
            index=len(steps) + 1,
            phase=phase,
            status=status,
            message=message,
            state=state,
            explain=explain,
        )
    )


def parse_number_array(text: str, max_len: int = 30) -> list[int]:
    raw = [part.strip() for part in text.replace("，", ",").replace("\n", " ").replace(",", " ").split()]
    if not raw:
        raise InputError("请输入数组数据。")
    numbers: list[int] = []
    for item in raw:
        try:
            value = int(item)
        except ValueError as exc:
            raise InputError("数组只能包含整数。") from exc
        numbers.append(value)
    if len(numbers) < 3 or len(numbers) > max_len:
        raise InputError(f"数组长度需要在 3 到 {max_len} 之间。")
    if any(value < 0 or value > 999 for value in numbers):
        raise InputError("为了便于观察，元素范围请控制在 0 到 999。")
    return numbers


def run_quicksort(text: str) -> RunResponse:
    values = parse_number_array(text)
    arr = values[:]
    steps: list[Step] = []
    sorted_indexes: set[int] = set()
    compare_count = 0
    swap_count = 0

    def snapshot(
        message: str,
        *,
        phase: str = "排序中",
        status: str = "观察数组状态",
        compare: list[int] | None = None,
        pivot: int | None = None,
        swap: list[int] | None = None,
        explain: str = "快速排序每次固定一个基准位置，再缩小左右子问题。",
    ) -> None:
        make_step(
            steps,
            phase,
            status,
            message,
            {
                "kind": "sort",
                "values": arr[:],
                "compare": compare or [],
                "pivot": pivot,
                "swap": swap or [],
                "sorted": sorted(sorted_indexes),
            },
            explain,
        )

    snapshot(
        "初始化数组，准备以分治方式排序。",
        phase="初始化",
        status="准备",
        explain="保留原始数据，后续每一步展示数组在局部区间中的变化。",
    )

    def partition(left: int, right: int) -> int:
        nonlocal compare_count, swap_count
        pivot_value = arr[right]
        store_index = left
        snapshot(
            f"选择下标 {right} 的 {pivot_value} 作为基准，处理区间 [{left}, {right}]。",
            phase="选择基准",
            pivot=right,
            explain="基准右侧暂时不动，storeIndex 维护小于基准区域的右边界。",
        )
        for index in range(left, right):
            compare_count += 1
            snapshot(
                f"比较 {arr[index]} 与基准 {pivot_value}。",
                phase="比较",
                compare=[index, right],
                pivot=right,
                explain=f"{arr[index]} {'小于' if arr[index] < pivot_value else '不小于'}基准。",
            )
            if arr[index] < pivot_value:
                if index != store_index:
                    arr[index], arr[store_index] = arr[store_index], arr[index]
                    swap_count += 1
                    snapshot(
                        f"交换下标 {index} 和 {store_index}，扩大左侧较小区域。",
                        phase="交换",
                        pivot=right,
                        swap=[index, store_index],
                        explain="交换后，storeIndex 左侧元素都小于基准。",
                    )
                else:
                    snapshot(
                        f"下标 {index} 已在正确区域，边界右移。",
                        phase="边界移动",
                        compare=[index],
                        pivot=right,
                    )
                store_index += 1
        arr[store_index], arr[right] = arr[right], arr[store_index]
        swap_count += 1
        sorted_indexes.add(store_index)
        snapshot(
            f"基准 {pivot_value} 放到最终位置 {store_index}。",
            phase="定位基准",
            status="划分完成",
            swap=[store_index, right],
            explain="此时基准左侧都更小，右侧都不小于它，基准位置已经确定。",
        )
        return store_index

    def quicksort(left: int, right: int) -> None:
        if left > right:
            return
        if left == right:
            sorted_indexes.add(left)
            snapshot(
                f"区间 [{left}, {right}] 只有一个元素 {arr[left]}，位置确定。",
                phase="递归终止",
                status="单元素有序",
            )
            return
        pivot_index = partition(left, right)
        quicksort(left, pivot_index - 1)
        quicksort(pivot_index + 1, right)

    quicksort(0, len(arr) - 1)
    sorted_indexes.update(range(len(arr)))
    snapshot(
        f"排序完成：{', '.join(map(str, arr))}。",
        phase="完成",
        status="得到最终结果",
        explain="所有递归区间都已处理，数组整体有序。",
    )
    return RunResponse(
        algorithm_id="quicksort",
        input=text,
        result={"sorted": arr},
        steps=steps,
        metrics={"stepCount": len(steps), "compareCount": compare_count, "swapCount": swap_count},
    )


def build_bubble_sort(text: str, algorithm_id: str = "bubble_sort") -> RunResponse:
    values = parse_number_array(text)
    arr = values[:]
    steps: list[Step] = []
    compare_count = 0
    swap_count = 0
    sorted_indexes: set[int] = set()

    def snapshot(
        message: str,
        *,
        phase: str = "比较",
        status: str = "相邻比较",
        compare: list[int] | None = None,
        swap: list[int] | None = None,
        explain: str = "冒泡排序每轮把当前未排序区间中的最大值交换到右侧。",
    ) -> None:
        make_step(
            steps,
            phase,
            status,
            message,
            {
                "kind": "sort",
                "values": arr[:],
                "compare": compare or [],
                "pivot": None,
                "swap": swap or [],
                "sorted": sorted(sorted_indexes),
            },
            explain,
        )

    snapshot(
        "初始化数组，准备从左到右进行相邻比较。",
        phase="初始化",
        status="准备",
        explain="冒泡排序通过多轮扫描逐步把较大元素移动到数组右端。",
    )
    n = len(arr)
    for end in range(n - 1, 0, -1):
        swapped = False
        for index in range(end):
            compare_count += 1
            snapshot(
                f"比较相邻元素 {arr[index]} 和 {arr[index + 1]}。",
                compare=[index, index + 1],
            )
            if arr[index] > arr[index + 1]:
                arr[index], arr[index + 1] = arr[index + 1], arr[index]
                swapped = True
                swap_count += 1
                snapshot(
                    f"左侧元素更大，交换下标 {index} 和 {index + 1}。",
                    phase="交换",
                    swap=[index, index + 1],
                    explain="较大的值继续向右移动，像气泡一样浮到本轮末尾。",
                )
        sorted_indexes.add(end)
        snapshot(
            f"第 {n - end} 轮结束，下标 {end} 的元素已确定。",
            phase="轮次结束",
            status="固定最大值",
        )
        if not swapped:
            sorted_indexes.update(range(end))
            snapshot(
                "本轮没有发生交换，数组已经整体有序。",
                phase="提前结束",
                status="得到最终结果",
            )
            break
    sorted_indexes.update(range(n))
    snapshot(
        f"排序完成：{', '.join(map(str, arr))}。",
        phase="完成",
        status="得到最终结果",
        explain="所有元素都已经按升序排列。",
    )
    return RunResponse(
        algorithm_id=algorithm_id,
        input=text,
        result={"sorted": arr},
        steps=steps,
        metrics={"stepCount": len(steps), "compareCount": compare_count, "swapCount": swap_count},
    )


def run_bubble_sort(text: str) -> RunResponse:
    return build_bubble_sort(text)


def parse_graph(text: str) -> dict[str, Any]:
    if ";" not in text:
        raise InputError("图输入需要包含起点和边列表，中间用分号分隔。")
    start_part, edge_part = text.split(";", 1)
    start = start_part.strip()
    if not start or not start.replace("_", "").isalnum() or start[0].isdigit():
        raise InputError("起点名称请使用字母开头的字母、数字或下划线。")
    edge_texts = [item.strip() for item in edge_part.replace("，", ",").split(",") if item.strip()]
    if len(edge_texts) < 3 or len(edge_texts) > 30:
        raise InputError("边数量需要在 3 到 30 之间。")
    nodes = {start}
    edges: list[dict[str, Any]] = []
    for item in edge_texts:
        if ":" not in item or "-" not in item:
            raise InputError(f"边格式错误：{item}")
        pair, weight_text = item.split(":", 1)
        from_node, to_node = [part.strip() for part in pair.split("-", 1)]
        if not from_node or not to_node:
            raise InputError(f"边格式错误：{item}")
        try:
            weight = int(weight_text.strip())
        except ValueError as exc:
            raise InputError(f"边权重必须是整数：{item}") from exc
        if weight <= 0 or weight > 999:
            raise InputError("边权重需要在 1 到 999 之间。")
        nodes.update([from_node, to_node])
        edges.append({"from": from_node, "to": to_node, "weight": weight})
    if start not in nodes:
        raise InputError("起点必须出现在图中。")
    if len(nodes) < 3 or len(nodes) > 12:
        raise InputError("顶点数量需要在 3 到 12 之间。")
    return {"start": start, "nodes": sorted(nodes), "edges": edges}


def run_dijkstra(text: str) -> RunResponse:
    graph = parse_graph(text)
    distances: dict[str, int | None] = {node: None for node in graph["nodes"]}
    previous: dict[str, str | None] = {node: None for node in graph["nodes"]}
    distances[graph["start"]] = 0
    visited: set[str] = set()
    steps: list[Step] = []
    relax_count = 0
    adjacency: dict[str, list[dict[str, Any]]] = {node: [] for node in graph["nodes"]}
    for edge in graph["edges"]:
        adjacency[edge["from"]].append({"to": edge["to"], "weight": edge["weight"]})
        adjacency[edge["to"]].append({"to": edge["from"], "weight": edge["weight"]})

    def snapshot(
        message: str,
        *,
        phase: str = "松弛",
        status: str = "计算最短距离",
        current: str | None = None,
        active_edge: list[str] | None = None,
        path_edges: list[list[str]] | None = None,
        explain: str = "每轮选择未确定顶点中距离最小者，并用它尝试更新相邻顶点的距离。",
    ) -> None:
        make_step(
            steps,
            phase,
            status,
            message,
            {
                "kind": "graph",
                "graph": graph,
                "distances": distances.copy(),
                "previous": previous.copy(),
                "visited": sorted(visited),
                "current": current,
                "activeEdge": active_edge,
                "pathEdges": path_edges or [],
            },
            explain,
        )

    snapshot(
        f"从起点 {graph['start']} 开始，起点距离设为 0，其余为 ∞。",
        phase="初始化",
        status="准备",
    )
    while len(visited) < len(graph["nodes"]):
        candidates = [node for node in graph["nodes"] if node not in visited]
        reachable = [node for node in candidates if distances[node] is not None]
        if not reachable:
            break
        current = min(reachable, key=lambda node: distances[node] or 0)
        visited.add(current)
        snapshot(
            f"选择未确定顶点中距离最小的 {current}，当前距离为 {distances[current]}。",
            phase="选择顶点",
            status="确定一个顶点",
            current=current,
            explain="被选中的顶点距离已经是最终最短距离，之后不会再被更新。",
        )
        for edge in adjacency[current]:
            target = edge["to"]
            if target in visited:
                snapshot(
                    f"{target} 已确定，跳过边 {current}-{target}。",
                    phase="跳过",
                    current=current,
                    active_edge=[current, target],
                )
                continue
            candidate = (distances[current] or 0) + edge["weight"]
            snapshot(
                f"检查边 {current}-{target}，候选距离 {distances[current]} + {edge['weight']} = {candidate}。",
                phase="检查边",
                current=current,
                active_edge=[current, target],
            )
            if distances[target] is None or candidate < distances[target]:
                distances[target] = candidate
                previous[target] = current
                relax_count += 1
                snapshot(
                    f"更新 {target} 的最短距离为 {candidate}，前驱改为 {current}。",
                    phase="松弛成功",
                    status="距离已更新",
                    current=current,
                    active_edge=[current, target],
                    explain="发现更短路径时，记录新的距离和前驱顶点，用于最后还原路径。",
                )
            else:
                snapshot(
                    f"{target} 当前距离更优，不更新。",
                    phase="松弛失败",
                    current=current,
                    active_edge=[current, target],
                )
    reachable_nodes = [node for node in graph["nodes"] if distances[node] is not None]
    farthest = max(reachable_nodes, key=lambda node: distances[node] or 0)
    path_edges: list[list[str]] = []
    cursor = farthest
    while previous[cursor]:
        parent = previous[cursor]
        path_edges.append([parent, cursor])
        cursor = parent
    path_edges.reverse()
    snapshot(
        f"计算完成。示例最短路径：{graph['start']} 到 {farthest}，距离 {distances[farthest]}。",
        phase="完成",
        status="得到最终结果",
        path_edges=path_edges,
        explain="表格中的前驱列可以还原任意顶点从起点出发的最短路径。",
    )
    return RunResponse(
        algorithm_id="dijkstra",
        input=text,
        result={"distances": distances, "previous": previous, "samplePathEdges": path_edges},
        steps=steps,
        metrics={"stepCount": len(steps), "relaxCount": relax_count},
    )


def parse_maze(text: str) -> list[list[int]]:
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        row = []
        for item in line.replace("，", ",").replace(",", " ").split():
            try:
                value = int(item)
            except ValueError as exc:
                raise InputError("迷宫只能包含 0 和 1。") from exc
            row.append(value)
        rows.append(row)
    if len(rows) < 3 or len(rows) > 12:
        raise InputError("迷宫行数需要在 3 到 12 之间。")
    width = len(rows[0])
    if width < 3 or width > 12 or any(len(row) != width for row in rows):
        raise InputError("每行列数需要一致，且列数在 3 到 12 之间。")
    if any(cell not in (0, 1) for row in rows for cell in row):
        raise InputError("迷宫只能包含 0 和 1。")
    if rows[0][0] != 0 or rows[-1][-1] != 0:
        raise InputError("左上角起点和右下角终点必须为 0。")
    return rows


def run_maze(text: str) -> RunResponse:
    grid = parse_maze(text)
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False for _ in range(cols)] for _ in range(rows)]
    path: list[list[int]] = []
    steps: list[Step] = []
    directions = [(0, 1, "右"), (1, 0, "下"), (0, -1, "左"), (-1, 0, "上")]

    def snapshot(
        message: str,
        *,
        phase: str = "搜索",
        status: str = "深度优先搜索",
        current: list[int] | None = None,
        failed: list[int] | None = None,
        explain: str = "DFS 会先沿一个方向深入；如果走不通，就回退到上一个岔路继续尝试。",
    ) -> None:
        make_step(
            steps,
            phase,
            status,
            message,
            {
                "kind": "maze",
                "grid": [row[:] for row in grid],
                "visited": [row[:] for row in visited],
                "path": [point[:] for point in path],
                "current": current,
                "failed": failed,
            },
            explain,
        )

    snapshot("初始化迷宫，从左上角起点开始搜索。", phase="初始化", status="准备")

    def dfs(row: int, col: int) -> bool:
        if row < 0 or row >= rows or col < 0 or col >= cols:
            snapshot(f"位置 ({row}, {col}) 越界，返回上一层。", phase="剪枝", failed=[row, col])
            return False
        if grid[row][col] == 1:
            snapshot(f"位置 ({row}, {col}) 是墙，不能进入。", phase="剪枝", failed=[row, col])
            return False
        if visited[row][col]:
            snapshot(f"位置 ({row}, {col}) 已访问，避免重复搜索。", phase="剪枝", failed=[row, col])
            return False
        visited[row][col] = True
        path.append([row, col])
        snapshot(
            f"进入位置 ({row}, {col})。",
            phase="前进",
            current=[row, col],
            explain="把当前位置加入路径，并标记为已访问。",
        )
        if row == rows - 1 and col == cols - 1:
            snapshot(
                "到达终点，搜索成功。",
                phase="完成",
                status="找到路径",
                current=[row, col],
                explain="当前路径就是从起点到终点的一条可行路线。",
            )
            return True
        for dr, dc, name in directions:
            snapshot(f"尝试从 ({row}, {col}) 向{name}移动。", phase="尝试方向", current=[row, col])
            if dfs(row + dr, col + dc):
                return True
        removed = path.pop()
        snapshot(
            f"位置 ({removed[0]}, {removed[1]}) 四个方向都失败，回溯。",
            phase="回溯",
            current=path[-1] if path else None,
            explain="回溯表示这条分支无法通向终点，需要撤销选择并返回上一格。",
        )
        return False

    solved = dfs(0, 0)
    if not solved:
        snapshot("搜索结束，没有找到从起点到终点的路径。", phase="完成", status="无解")
    return RunResponse(
        algorithm_id="maze",
        input=text,
        result={"solved": solved, "path": path},
        steps=steps,
        metrics={"stepCount": len(steps), "visitedCount": sum(sum(row) for row in visited)},
    )


def parse_huffman(text: str) -> list[dict[str, Any]]:
    items = [item.strip() for item in text.replace("，", ",").split(",") if item.strip()]
    if len(items) < 3 or len(items) > 15:
        raise InputError("哈夫曼节点数量需要在 3 到 15 之间。")
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        if ":" not in item:
            raise InputError(f"节点格式错误：{item}")
        label, weight_text = [part.strip() for part in item.split(":", 1)]
        if not label:
            raise InputError(f"节点名称不能为空：{item}")
        if label in seen:
            raise InputError(f"节点名称重复：{label}")
        try:
            weight = int(weight_text)
        except ValueError as exc:
            raise InputError(f"权重必须是整数：{item}") from exc
        if weight <= 0 or weight > 999:
            raise InputError("权重需要在 1 到 999 之间。")
        seen.add(label)
        result.append({"id": label, "label": label, "weight": weight, "left": None, "right": None})
    return result


def run_huffman(text: str) -> RunResponse:
    leaves = parse_huffman(text)
    steps: list[Step] = []
    nodes: dict[str, dict[str, Any]] = {node["id"]: node.copy() for node in leaves}
    heap: list[tuple[int, int, str]] = []
    counter = 0
    for node in leaves:
        heappush(heap, (node["weight"], counter, node["id"]))
        counter += 1

    def active_nodes() -> list[str]:
        return [item[2] for item in sorted(heap)]

    def tree_state(selected: list[str] | None = None, merged: str | None = None) -> dict[str, Any]:
        return {
            "kind": "huffman",
            "nodes": list(nodes.values()),
            "queue": active_nodes(),
            "selected": selected or [],
            "merged": merged,
            "codes": build_codes(nodes, merged) if merged and len(heap) == 1 else {},
        }

    make_step(
        steps,
        "初始化",
        "准备",
        "将所有字符按权重放入优先队列。",
        tree_state(),
        "哈夫曼树每次选择权重最小的两个节点进行合并。",
    )
    merge_round = 1
    while len(heap) > 1:
        w1, _, left_id = heappop(heap)
        w2, _, right_id = heappop(heap)
        make_step(
            steps,
            "选择节点",
            "取出最小权重",
            f"第 {merge_round} 轮选出 {nodes[left_id]['label']}({w1}) 和 {nodes[right_id]['label']}({w2})。",
            tree_state([left_id, right_id]),
            "优先队列保证每一轮取出的两个节点权重最小，这会让高频字符获得更短编码。",
        )
        parent_id = f"N{merge_round}"
        nodes[parent_id] = {
            "id": parent_id,
            "label": f"{nodes[left_id]['label']}+{nodes[right_id]['label']}",
            "weight": w1 + w2,
            "left": left_id,
            "right": right_id,
        }
        heappush(heap, (w1 + w2, counter, parent_id))
        counter += 1
        make_step(
            steps,
            "合并节点",
            "生成父节点",
            f"合并得到新节点 {nodes[parent_id]['label']}，权重为 {w1 + w2}，放回队列。",
            tree_state([left_id, right_id], parent_id),
            "左分支记为 0，右分支记为 1，最终从根到叶子的路径就是字符编码。",
        )
        merge_round += 1
    root_id = heap[0][2]
    codes = build_codes(nodes, root_id)
    make_step(
        steps,
        "完成",
        "得到编码表",
        "哈夫曼树构造完成，生成每个字符的编码。",
        {**tree_state(merged=root_id), "codes": codes},
        "权重越大的字符通常越靠近根节点，编码长度更短。",
    )
    return RunResponse(
        algorithm_id="huffman",
        input=text,
        result={"root": root_id, "codes": codes, "nodes": list(nodes.values())},
        steps=steps,
        metrics={"stepCount": len(steps), "mergeCount": len(leaves) - 1},
    )


def build_codes(nodes: dict[str, dict[str, Any]], root_id: str | None) -> dict[str, str]:
    if not root_id:
        return {}
    codes: dict[str, str] = {}

    def walk(node_id: str, prefix: str) -> None:
        node = nodes[node_id]
        if not node.get("left") and not node.get("right"):
            codes[node["label"]] = prefix or "0"
            return
        if node.get("left"):
            walk(node["left"], prefix + "0")
        if node.get("right"):
            walk(node["right"], prefix + "1")

    walk(root_id, "")
    return codes


CNN_SAMPLES = {
    "digit_3": {
        "label": "数字 3",
        "target": 3,
        "matrix": [
            "0001111000",
            "0010000100",
            "0000000100",
            "0000011000",
            "0000000100",
            "0000000100",
            "0010000100",
            "0001111000",
            "0000000000",
            "0000000000",
        ],
    },
    "digit_7": {
        "label": "数字 7",
        "target": 7,
        "matrix": [
            "0011111100",
            "0000001000",
            "0000010000",
            "0000100000",
            "0001000000",
            "0010000000",
            "0010000000",
            "0010000000",
            "0000000000",
            "0000000000",
        ],
    },
}


def run_cnn(sample: str = "digit_3") -> RunResponse:
    if sample not in CNN_SAMPLES:
        raise InputError("请选择内置 CNN 样例：digit_3 或 digit_7。")
    sample_data = CNN_SAMPLES[sample]
    image = [[float(char) for char in row] for row in sample_data["matrix"]]
    steps: list[Step] = []
    edge_kernel = [[1, 0, -1], [1, 0, -1], [1, 0, -1]]
    top_kernel = [[1, 1, 1], [0, 0, 0], [-1, -1, -1]]
    conv_a = conv2d(image, edge_kernel)
    conv_b = conv2d(image, top_kernel)
    relu_a = [[max(0.0, value) for value in row] for row in conv_a]
    relu_b = [[max(0.0, value) for value in row] for row in conv_b]
    pool_a = max_pool(relu_a)
    pool_b = max_pool(relu_b)
    features = [sum_matrix(pool_a), sum_matrix(pool_b), count_active(image), diagonal_score(image)]
    logits = fake_digit_logits(features, sample_data["target"])
    probs = softmax(logits)
    prediction = max(range(len(probs)), key=lambda index: probs[index])

    make_step(
        steps,
        "预处理",
        "读取输入图像",
        f"载入内置样例 {sample_data['label']}，转换为 0/1 灰度矩阵。",
        {"kind": "cnn", "stage": "input", "image": image, "sample": sample, "label": sample_data["label"]},
        "真实 CNN 通常会先把图像缩放、归一化，再送入卷积层。",
    )
    make_step(
        steps,
        "卷积",
        "提取局部特征",
        "使用两个 3x3 卷积核扫描图像，分别突出垂直边缘和水平边缘。",
        {
            "kind": "cnn",
            "stage": "conv",
            "image": image,
            "kernels": [edge_kernel, top_kernel],
            "featureMaps": [round_matrix(conv_a), round_matrix(conv_b)],
        },
        "卷积核每次只观察局部区域，通过加权求和得到当前位置的特征响应。",
    )
    make_step(
        steps,
        "ReLU",
        "过滤负响应",
        "将小于 0 的卷积结果置为 0，保留更明显的正向特征。",
        {
            "kind": "cnn",
            "stage": "relu",
            "image": image,
            "featureMaps": [round_matrix(relu_a), round_matrix(relu_b)],
        },
        "ReLU 引入非线性，让网络保留被激活的特征并抑制负响应。",
    )
    make_step(
        steps,
        "池化",
        "降低特征尺寸",
        "对特征图做 2x2 最大池化，压缩尺寸并保留局部最强响应。",
        {
            "kind": "cnn",
            "stage": "pool",
            "image": image,
            "featureMaps": [round_matrix(pool_a), round_matrix(pool_b)],
        },
        "最大池化可以减少计算量，同时让特征对轻微位移更稳定。",
    )
    make_step(
        steps,
        "分类",
        "输出概率",
        f"展平特征并计算 Softmax，预测类别为 {prediction}。",
        {
            "kind": "cnn",
            "stage": "softmax",
            "image": image,
            "features": [round(value, 3) for value in features],
            "probabilities": [{"label": str(index), "value": round(value, 4)} for index, value in enumerate(probs)],
            "prediction": prediction,
        },
        "Softmax 把分类得分转换为概率分布，概率最高的类别作为预测结果。",
    )
    return RunResponse(
        algorithm_id="cnn",
        input=sample,
        result={"prediction": prediction, "probabilities": steps[-1].state["probabilities"]},
        steps=steps,
        metrics={"stepCount": len(steps), "featureCount": len(features)},
    )


def conv2d(image: list[list[float]], kernel: list[list[int]]) -> list[list[float]]:
    rows = len(image)
    cols = len(image[0])
    output: list[list[float]] = []
    for row in range(rows - 2):
        out_row = []
        for col in range(cols - 2):
            total = 0.0
            for kr in range(3):
                for kc in range(3):
                    total += image[row + kr][col + kc] * kernel[kr][kc]
            out_row.append(total)
        output.append(out_row)
    return output


def max_pool(matrix: list[list[float]], size: int = 2) -> list[list[float]]:
    output = []
    for row in range(0, len(matrix) - 1, size):
        out_row = []
        for col in range(0, len(matrix[0]) - 1, size):
            window = [matrix[row + dr][col + dc] for dr in range(size) for dc in range(size)]
            out_row.append(max(window))
        output.append(out_row)
    return output


def sum_matrix(matrix: list[list[float]]) -> float:
    return sum(sum(row) for row in matrix)


def count_active(image: list[list[float]]) -> float:
    return sum(1 for row in image for value in row if value > 0)


def diagonal_score(image: list[list[float]]) -> float:
    return sum(image[index][min(len(image[0]) - 1, index + 1)] for index in range(min(len(image), len(image[0]) - 1)))


def fake_digit_logits(features: list[float], target: int) -> list[float]:
    base = [-1.4, -1.1, -0.4, -0.2, -0.8, -0.5, -0.7, -0.3, -0.9, -1.0]
    edge, top, active, diagonal = features
    logits = [value + (edge * 0.015) + (top * 0.012) + (active * 0.01) for value in base]
    logits[3] += 1.2 if target == 3 else -0.25
    logits[7] += 1.2 if target == 7 else -0.25
    logits[target] += 1.4 + diagonal * 0.03
    return logits


def softmax(logits: list[float]) -> list[float]:
    max_logit = max(logits)
    exps = [math.exp(value - max_logit) for value in logits]
    total = sum(exps)
    return [value / total for value in exps]


def round_matrix(matrix: list[list[float]]) -> list[list[float]]:
    return [[round(value, 2) for value in row] for row in matrix]


def compare_sort(text: str) -> dict[str, Any]:
    values = parse_number_array(text)
    input_text = ", ".join(str(value) for value in values)
    quick = run_quicksort(input_text)
    bubble = build_bubble_sort(input_text, algorithm_id="bubble_sort")
    return {
        "input": input_text,
        "quick": quick.model_dump(),
        "bubble": bubble.model_dump(),
        "summary": {
            "sameResult": quick.result["sorted"] == bubble.result["sorted"],
            "quickSteps": len(quick.steps),
            "bubbleSteps": len(bubble.steps),
            "quickCompare": quick.metrics["compareCount"],
            "bubbleCompare": bubble.metrics["compareCount"],
            "quickSwap": quick.metrics["swapCount"],
            "bubbleSwap": bubble.metrics["swapCount"],
        },
    }


def random_array() -> str:
    return ", ".join(str(random.randint(5, 96)) for _ in range(9))


def random_graph() -> str:
    nodes = ["A", "B", "C", "D", "E", "F"]
    edges = [
        ("A", "B"),
        ("A", "C"),
        ("B", "C"),
        ("B", "D"),
        ("C", "E"),
        ("D", "E"),
        ("D", "F"),
        ("E", "F"),
    ]
    return "A; " + ", ".join(f"{a}-{b}:{random.randint(1, 12)}" for a, b in edges)


def random_maze() -> str:
    size = 6
    grid = [[1 if random.random() < 0.28 else 0 for _ in range(size)] for _ in range(size)]
    for index in range(size):
        grid[0][index] = 0
        grid[index][size - 1] = 0
    grid[0][0] = 0
    grid[-1][-1] = 0
    return "\n".join(" ".join(str(cell) for cell in row) for row in grid)


def random_huffman() -> str:
    labels = ["A", "B", "C", "D", "E", "F"]
    return ", ".join(f"{label}:{random.randint(4, 45)}" for label in labels)


ALGORITHMS: dict[str, AlgorithmSpec] = {
    "quicksort": AlgorithmSpec(
        info=AlgorithmInfo(
            id="quicksort",
            type="排序",
            title="快速排序",
            difficulty="中等",
            input_label="数组元素",
            input_hint="输入 3 到 30 个整数，用逗号、空格或换行分隔，例如：8, 3, 5, 1, 9, 2",
            summary="快速排序选择基准元素，将区间划分为小于基准和大于基准的两部分，再递归处理左右区间。",
            time_complexity="平均 O(n log n)，最坏 O(n^2)",
            space_complexity="O(log n)",
            test_cases=[
                TestCase(name="测试 1", value="8, 3, 5, 1, 9, 2, 7", expected="1,2,3,5,7,8,9"),
                TestCase(name="测试 2", value="12 4 18 6 1 15 9 3", expected="1,3,4,6,9,12,15,18"),
            ],
        ),
        random_input=random_array,
        run=run_quicksort,
    ),
    "bubble_sort": AlgorithmSpec(
        info=AlgorithmInfo(
            id="bubble_sort",
            type="排序",
            title="冒泡排序",
            difficulty="基础",
            input_label="数组元素",
            input_hint="输入 3 到 30 个整数，用逗号、空格或换行分隔。该算法也用于排序对比。",
            summary="冒泡排序重复比较相邻元素，把较大的元素逐步交换到未排序区间末尾。",
            time_complexity="O(n^2)",
            space_complexity="O(1)",
            test_cases=[
                TestCase(name="测试 1", value="9, 1, 6, 3, 8"),
                TestCase(name="测试 2", value="5 4 3 2 1"),
            ],
        ),
        random_input=random_array,
        run=run_bubble_sort,
    ),
    "dijkstra": AlgorithmSpec(
        info=AlgorithmInfo(
            id="dijkstra",
            type="图算法",
            title="Dijkstra 最短路径",
            difficulty="中等",
            input_label="无向带权图",
            input_hint="格式：起点; 边列表。边使用 A-B:4，以逗号分隔，例如：A; A-B:4, A-C:2, C-B:1",
            summary="Dijkstra 从起点出发，每轮选择当前距离最小的未确定顶点，并尝试松弛它的邻接边。",
            time_complexity="O(V^2 + E)",
            space_complexity="O(V + E)",
            test_cases=[
                TestCase(name="测试 1", value="A; A-B:4, A-C:2, C-B:1, B-D:5, C-D:8, C-E:10, D-E:2"),
                TestCase(name="测试 2", value="S; S-A:7, S-B:3, A-C:4, B-A:2, B-C:6, B-D:5, C-T:2, D-T:4"),
            ],
        ),
        random_input=random_graph,
        run=run_dijkstra,
    ),
    "maze": AlgorithmSpec(
        info=AlgorithmInfo(
            id="maze",
            type="回溯",
            title="迷宫求解",
            difficulty="中-高",
            input_label="迷宫矩阵",
            input_hint="使用 0 表示通路、1 表示墙。每行等长，用换行分隔。起点为左上角，终点为右下角。",
            summary="迷宫求解使用深度优先搜索与回溯，遇到墙、越界或已访问节点就撤回。",
            time_complexity="O(R x C)",
            space_complexity="O(R x C)",
            test_cases=[
                TestCase(name="测试 1", value="0 0 1 0 0 0\n1 0 1 0 1 0\n0 0 0 0 1 0\n0 1 1 0 0 0\n0 0 0 1 1 0\n1 1 0 0 0 0"),
                TestCase(name="测试 2", value="0 1 0 0 0\n0 1 0 1 0\n0 0 0 1 0\n1 1 0 0 0\n0 0 0 1 0"),
            ],
        ),
        random_input=random_maze,
        run=run_maze,
    ),
    "huffman": AlgorithmSpec(
        info=AlgorithmInfo(
            id="huffman",
            type="树结构",
            title="哈夫曼树构造",
            difficulty="中等",
            input_label="字符权重",
            input_hint="格式：字符:权重，以逗号分隔。例如：A:5, B:9, C:12, D:13, E:16, F:45",
            summary="哈夫曼树每轮选出两个最小权重节点合并，最终得到前缀编码表。",
            time_complexity="O(n log n)",
            space_complexity="O(n)",
            test_cases=[
                TestCase(name="测试 1", value="A:5, B:9, C:12, D:13, E:16, F:45"),
                TestCase(name="测试 2", value="a:7, b:3, c:11, d:14, e:22"),
            ],
        ),
        random_input=random_huffman,
        run=run_huffman,
    ),
    "cnn": AlgorithmSpec(
        info=AlgorithmInfo(
            id="cnn",
            type="人工智能",
            title="简化 CNN 推理",
            difficulty="创新扩展",
            input_label="内置样例",
            input_hint="输入 digit_3 或 digit_7。系统会展示预处理、卷积、ReLU、池化和 Softmax 分类过程。",
            summary="使用 NumPy 风格的轻量计算展示 CNN 前向推理，不依赖深度学习框架或模型下载。",
            time_complexity="O(K x H x W)",
            space_complexity="O(H x W)",
            test_cases=[
                TestCase(name="数字 3", value="digit_3"),
                TestCase(name="数字 7", value="digit_7"),
            ],
        ),
        random_input=lambda: random.choice(["digit_3", "digit_7"]),
        run=run_cnn,
    ),
}


def algorithm_list() -> list[AlgorithmInfo]:
    return [spec.info for spec in ALGORITHMS.values()]


def get_algorithm(algorithm_id: str) -> AlgorithmSpec:
    try:
        return ALGORITHMS[algorithm_id]
    except KeyError as exc:
        raise InputError(f"未知算法：{algorithm_id}") from exc
