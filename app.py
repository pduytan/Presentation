"""
Ứng dụng Demo Khai phá Tập phổ biến & Luật kết hợp (FP-Growth vs. Apriori) — CS313
Kiến trúc 4 Tab theo kế hoạch (plan.md), tích hợp 3 Ứng dụng:
  - Ứng dụng 1: Phân tích Giỏ hàng Bán lẻ (UCI Online Retail)
  - Ứng dụng 2: [Khung chờ tích hợp Ứng dụng 2 - Có sẵn dữ liệu mẫu chạy mượt]
  - Ứng dụng 3: Phân tích Bệnh đồng mắc Lâm sàng (MIMIC-IV Clinical Database Demo)

Chạy ứng dụng:
    streamlit run app.py
"""

from __future__ import annotations

import json
import math
import time
import tracemalloc
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import graphviz
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from mlxtend.frequent_patterns import apriori, association_rules, fpgrowth
from mlxtend.preprocessing import TransactionEncoder

# ==============================================================================
# CẤU HÌNH TRANG & ĐƯỜNG DẪN DỰ ÁN
# ==============================================================================
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

st.set_page_config(
    page_title="FP-Growth Demo — CS313",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.4rem; padding-bottom: 2rem; }
    div[data-baseweb="tab-list"] {
        width: 100%;
        display: flex;
    }
    button[data-baseweb="tab"] {
        flex: 1 1 0%;
        justify-content: center;
    }
    div[data-testid="stMetric"] {
        background: rgba(150, 150, 150, 0.06);
        border: 1px solid rgba(150, 150, 150, 0.25);
        padding: 12px 16px;
        border-radius: 8px;
    }
    .rec-card {
        background: rgba(150, 150, 150, 0.06);
        border: 1px solid rgba(150, 150, 150, 0.28);
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 10px;
        color: inherit;
    }
    .app2-banner {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border-left: 5px solid #f59e0b;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 16px;
        color: #78350f;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# CẤU TRÚC DỮ LIỆU CÂY FP-TREE & TRỰC QUAN HÓA GRAPHVIZ (TAB 2)
# ==============================================================================
class FPTreeNode:
    """Nút trên cây FP-Tree tự định nghĩa để minh họa White-Box."""

    def __init__(self, item: str, count: int = 1, parent: Optional["FPTreeNode"] = None, node_id: int = 0):
        self.item = item
        self.count = count
        self.parent = parent
        self.children: Dict[str, "FPTreeNode"] = {}
        self.node_link: Optional["FPTreeNode"] = None
        self.node_id = node_id


class WhiteBoxFPTree:
    """Xây dựng cây FP-Tree, Header Table (F-List), Conditional Pattern Base & vẽ Graphviz."""

    def __init__(
        self,
        transactions: List[List[str]],
        min_support_count: int,
        fixed_flist_order: Optional[List[str]] = None,
    ):
        self.min_support_count = max(1, min_support_count)
        self.total_transactions = len(transactions)
        self.raw_item_occurrences = sum(len(t) for t in transactions)
        self._node_counter = 0

        item_counts = Counter(item for t in transactions for item in set(t))
        frequent_items = {k: v for k, v in item_counts.items() if v >= self.min_support_count}

        if fixed_flist_order is not None:
            # Giữ nguyên thứ tự F-List toàn cục (Global F-List) thay vì tính lại cục bộ trên tập mẫu
            self.flist_order: List[str] = [x for x in fixed_flist_order if x in frequent_items]
        else:
            self.flist_order = sorted(
                frequent_items.keys(),
                key=lambda x: (-frequent_items[x], str(x)),
            )
        self.rank: Dict[str, int] = {item: idx for idx, item in enumerate(self.flist_order)}

        self.header_table: Dict[str, Dict[str, object]] = {
            item: {"count": frequent_items[item], "head": None, "tail": None}
            for item in self.flist_order
        }

        self.root = FPTreeNode(item="{null}", count=0, parent=None, node_id=0)
        self.ordered_transactions: List[List[str]] = []
        self.filtered_item_occurrences = 0

        for trans in transactions:
            unique_valid = [item for item in set(trans) if item in self.rank]
            ordered = sorted(unique_valid, key=lambda x: self.rank[x])
            self.ordered_transactions.append(ordered)
            self.filtered_item_occurrences += len(ordered)
            if ordered:
                self._insert_tree(ordered, self.root, count=1)

    def _insert_tree(self, items: List[str], node: FPTreeNode, count: int = 1) -> None:
        first = items[0]
        if first in node.children:
            child = node.children[first]
            child.count += count
        else:
            self._node_counter += 1
            child = FPTreeNode(item=first, count=count, parent=node, node_id=self._node_counter)
            node.children[first] = child

            entry = self.header_table[first]
            if entry["head"] is None:
                entry["head"] = child
                entry["tail"] = child
            else:
                tail_node: FPTreeNode = entry["tail"]  # type: ignore[assignment]
                tail_node.node_link = child
                entry["tail"] = child

        if len(items) > 1:
            self._insert_tree(items[1:], child, count=count)

    @property
    def num_tree_nodes(self) -> int:
        return self._node_counter

    def get_header_dataframe(self, item_labels: Dict[str, str]) -> pd.DataFrame:
        rows = []
        for rank_idx, item in enumerate(self.flist_order, start=1):
            cnt = int(self.header_table[item]["count"])  # type: ignore[arg-type]
            node_cnt = 0
            curr = self.header_table[item]["head"]
            while curr is not None:
                node_cnt += 1
                curr = curr.node_link
            rows.append(
                {
                    "Thứ tự F-List": rank_idx,
                    "Mã Item": item,
                    "Tên hiển thị": item_labels.get(item, item),
                    "Số lần xuất hiện (Support Count)": cnt,
                    "Support (%)": round(cnt / max(1, self.total_transactions) * 100, 2),
                    "Số nút trên FP-Tree": node_cnt,
                }
            )
        return pd.DataFrame(rows)

    def get_conditional_pattern_base(self, target_item: str) -> List[Tuple[List[str], int]]:
        if target_item not in self.header_table:
            return []
        patterns: List[Tuple[List[str], int]] = []
        curr: Optional[FPTreeNode] = self.header_table[target_item]["head"]  # type: ignore[assignment]
        while curr is not None:
            path: List[str] = []
            parent = curr.parent
            while parent is not None and parent.item != "{null}":
                path.append(parent.item)
                parent = parent.parent
            path.reverse()
            if path:
                patterns.append((path, curr.count))
            curr = curr.node_link
        return patterns

    def to_graphviz_dot(
        self,
        item_labels: Optional[Dict[str, str]] = None,
        show_node_links: bool = True,
        max_nodes: int = 80,
        title: str = "FP-Tree",
    ) -> str:
        dot = graphviz.Digraph(comment=title)
        dot.attr(rankdir="TB", bgcolor="transparent", fontname="Segoe UI, Arial", nodesep="0.35", ranksep="0.45")
        dot.attr("node", fontname="Segoe UI, Arial", fontsize="10", style="filled", shape="box", margin="0.12,0.08")
        dot.attr("edge", fontname="Segoe UI, Arial", fontsize="9")

        dot.node(
            "node_0",
            label="{null}",
            shape="Mcircle",
            fillcolor="#1e293b",
            fontcolor="#ffffff",
            penwidth="1.5",
        )

        queue: List[FPTreeNode] = [self.root]
        visited_ids = {0}
        while queue and len(visited_ids) <= max_nodes:
            curr = queue.pop(0)
            for child in curr.children.values():
                if len(visited_ids) > max_nodes:
                    break
                visited_ids.add(child.node_id)
                short_name = ""
                if item_labels and child.item in item_labels and item_labels[child.item] != child.item:
                    raw_label = str(item_labels[child.item])
                    short_name = f"\n({raw_label[:18]}...)" if len(raw_label) > 18 else f"\n({raw_label})"
                node_label = f"{child.item} : {child.count}{short_name}"
                dot.node(
                    f"node_{child.node_id}",
                    label=node_label,
                    fillcolor="#eef2ff",
                    color="#4f46e5",
                    fontcolor="#1e1b4b",
                    style="filled,rounded",
                )
                dot.edge(
                    f"node_{curr.node_id}",
                    f"node_{child.node_id}",
                    color="#334155",
                    penwidth="1.3",
                )
                queue.append(child)

        if show_node_links:
            for item in self.flist_order:
                curr_node: Optional[FPTreeNode] = self.header_table[item]["head"]  # type: ignore[assignment]
                while curr_node is not None and curr_node.node_link is not None:
                    nxt = curr_node.node_link
                    if curr_node.node_id in visited_ids and nxt.node_id in visited_ids:
                        dot.edge(
                            f"node_{curr_node.node_id}",
                            f"node_{nxt.node_id}",
                            style="dashed",
                            color="#f97316",
                            constraint="false",
                            penwidth="1.1",
                        )
                    curr_node = nxt

        return dot.source


def build_conditional_fptree_dot(
    cond_patterns: List[Tuple[List[str], int]],
    min_support_count: int,
    target_item: str,
    item_labels: Optional[Dict[str, str]] = None,
) -> Tuple[str, Dict[str, int]]:
    cond_counts: Dict[str, int] = defaultdict(int)
    for path, cnt in cond_patterns:
        for item in path:
            cond_counts[item] += cnt

    valid_items = {k: v for k, v in cond_counts.items() if v >= min_support_count}
    ordered_valid = sorted(valid_items.keys(), key=lambda x: (-valid_items[x], str(x)))
    rank = {k: i for i, k in enumerate(ordered_valid)}

    root = FPTreeNode("{null}", 0, None, 0)
    node_counter = 0

    for path, cnt in cond_patterns:
        filtered = sorted([x for x in path if x in rank], key=lambda x: rank[x])
        curr = root
        for item in filtered:
            if item in curr.children:
                curr.children[item].count += cnt
            else:
                node_counter += 1
                curr.children[item] = FPTreeNode(item, cnt, curr, node_counter)
            curr = curr.children[item]

    dot = graphviz.Digraph(comment=f"Conditional FP-Tree for {target_item}")
    dot.attr(rankdir="TB", bgcolor="transparent", fontname="Segoe UI, Arial")
    dot.attr("node", fontname="Segoe UI, Arial", fontsize="10", style="filled,rounded", shape="box")
    dot.node(
        "cnode_0",
        label=f"{{null}}\n(Cond. Tree: {target_item})",
        shape="Mcircle",
        fillcolor="#0f766e",
        fontcolor="#ffffff",
    )

    queue = [root]
    while queue:
        curr = queue.pop(0)
        for child in curr.children.values():
            short_name = ""
            if item_labels and child.item in item_labels and item_labels[child.item] != child.item:
                lbl = str(item_labels[child.item])
                short_name = f"\n({lbl[:18]}...)" if len(lbl) > 18 else f"\n({lbl})"
            dot.node(
                f"cnode_{child.node_id}",
                label=f"{child.item} : {child.count}{short_name}",
                fillcolor="#ecfdf5",
                color="#059669",
                fontcolor="#064e3b",
            )
            dot.edge(f"cnode_{curr.node_id}", f"cnode_{child.node_id}", color="#0f766e", penwidth="1.3")
            queue.append(child)

    return dot.source, valid_items


# ==============================================================================
# HÀM TIỀN XỬ LÝ SPARSE ONE-HOT ENCODING & KHAI PHÁ LUẬT (CÓ @st.cache_data)
# ==============================================================================
@st.cache_data(show_spinner=False)
def encode_transactions_sparse(
    transactions: List[List[str]],
    min_item_support: float = 0.0,
) -> Tuple[pd.DataFrame, List[str]]:
    n_trans = len(transactions)
    if n_trans == 0:
        return pd.DataFrame(), []

    if min_item_support > 0:
        freq = Counter(item for t in transactions for item in set(t))
        valid_items = {k for k, v in freq.items() if (v / n_trans) >= min_item_support}
        filtered_trans = [[x for x in set(t) if x in valid_items] for t in transactions]
    else:
        filtered_trans = [sorted(set(t)) for t in transactions]

    te = TransactionEncoder()
    sparse_arr = te.fit(filtered_trans).transform(filtered_trans, sparse=True)
    sparse_df = pd.DataFrame.sparse.from_spmatrix(sparse_arr, columns=te.columns_)
    dense_bool_df = sparse_df.sparse.to_dense().astype(bool)
    return dense_bool_df, list(te.columns_)


@st.cache_data(show_spinner=False)
def run_fpgrowth_mining(
    encoded_df: pd.DataFrame,
    min_support: float,
    min_confidence: float,
    min_lift: float,
    max_len: int = 3,
) -> Tuple[pd.DataFrame, pd.DataFrame, float]:
    if encoded_df.empty or encoded_df.shape[1] == 0:
        return pd.DataFrame(), pd.DataFrame(), 0.0

    t0 = time.perf_counter()
    freq_df = fpgrowth(encoded_df, min_support=min_support, use_colnames=True, max_len=max_len)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    if freq_df.empty:
        return pd.DataFrame(), pd.DataFrame(), elapsed_ms

    freq_df["length"] = freq_df["itemsets"].map(len)
    freq_df["count"] = np.rint(freq_df["support"] * len(encoded_df)).astype(int)
    freq_df = freq_df.sort_values(["support", "length"], ascending=[False, True]).reset_index(drop=True)

    try:
        rules_df = association_rules(
            freq_df.drop(columns=["length", "count"], errors="ignore"),
            num_itemsets=len(encoded_df),
            metric="confidence",
            min_threshold=min_confidence,
        )
        if not rules_df.empty:
            rules_df = rules_df[rules_df["lift"] >= min_lift].copy()
            rules_df = rules_df.sort_values(["lift", "confidence", "support"], ascending=False).reset_index(drop=True)
    except ValueError:
        rules_df = pd.DataFrame()

    return freq_df, rules_df, elapsed_ms


@st.cache_data(show_spinner=False)
def run_benchmark_comparison(
    encoded_df: pd.DataFrame,
    support_thresholds: Tuple[float, ...],
    max_len: int = 3,
) -> pd.DataFrame:
    records = []
    col_supports = encoded_df.mean(axis=0)

    for sup in support_thresholds:
        # Chỉ giữ các cột đạt ngưỡng min_support hiện tại để tránh tràn RAM trên Streamlit Cloud
        active_cols = col_supports[col_supports >= sup].index
        sub_df = encoded_df[active_cols]
        n_active = len(active_cols)
        # Nếu số cặp ứng viên vượt quá 15,000 trên tập lớn, bật low_memory=True cho Apriori để tránh OOM (6GB RAM)
        use_low_mem = (n_active * (n_active - 1) // 2) > 15000 and len(sub_df) > 5000

        for algo_name, algo_fn in [("FP-Growth", fpgrowth), ("Apriori", apriori)]:
            tracemalloc.start()
            t0 = time.perf_counter()
            if sub_df.shape[1] == 0:
                res = pd.DataFrame()
            elif algo_name == "Apriori":
                res = algo_fn(sub_df, min_support=sup, use_colnames=True, max_len=max_len, low_memory=use_low_mem)
            else:
                res = algo_fn(sub_df, min_support=sup, use_colnames=True, max_len=max_len)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            _, peak_bytes = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            records.append(
                {
                    "min_support": sup,
                    "min_support_label": f"{sup:.3f} ({sup*100:.1f}%)",
                    "Thuật toán": algo_name,
                    "Thời gian chạy (ms)": round(elapsed_ms, 2),
                    "Bộ nhớ đỉnh (MB)": round(peak_bytes / (1024 * 1024), 4),
                    "Số tập phổ biến": len(res),
                }
            )
    return pd.DataFrame(records)


# ==============================================================================
# TẢI DỮ LIỆU THẬT CHO 3 ỨNG DỤNG
# ==============================================================================

# --- 1. ỨNG DỤNG 1: PHÂN TÍCH GIỎ HÀNG BÁN LẺ (UCI ONLINE RETAIL) ---
@st.cache_data(show_spinner=False)
def load_app1_data() -> Dict[str, object]:
    results_dir = OUTPUTS_DIR / "Ungdung1" / "results"
    basket_csv = results_dir / "basket_items.csv"
    prod_csv = results_dir / "product_support.csv"
    stats_json = results_dir / "stats.json"

    labels: Dict[str, str] = {}
    if stats_json.exists():
        stats_meta = json.loads(stats_json.read_text(encoding="utf-8"))
        labels = stats_meta.get("labels", {})  # type: ignore[assignment]

    if prod_csv.exists() and not labels:
        prod_df = pd.read_csv(prod_csv)
        labels = dict(zip(prod_df["code"].astype(str), prod_df["name"].astype(str)))

    if basket_csv.exists():
        pairs_df = pd.read_csv(basket_csv, dtype=str)
        baskets_series = pairs_df.groupby("InvoiceNo", sort=False)["StockCode"].agg(list)
        transactions = baskets_series.tolist()
        tx_ids = baskets_series.index.astype(str).tolist()
        sample_invoices = baskets_series.head(200)
        raw_df = pd.DataFrame(
            {
                "Mã Hóa Đơn (InvoiceNo)": sample_invoices.index,
                "Số lượng SP": sample_invoices.map(len).values,
                "Danh sách Mã SP": sample_invoices.map(
                    lambda lst: ", ".join(lst[:8]) + ("..." if len(lst) > 8 else "")
                ).values,
                "Tên SP tiêu biểu": sample_invoices.map(
                    lambda lst: " | ".join(labels.get(x, x) for x in lst[:3]) + ("..." if len(lst) > 3 else "")
                ).values,
            }
        )
    else:
        xlsx_path = DATA_DIR / "Online Retail.xlsx"
        raw = pd.read_excel(xlsx_path, engine="openpyxl", dtype={"InvoiceNo": str, "StockCode": str})
        d = raw[raw["Country"] == "United Kingdom"].copy()
        d = d[~d["InvoiceNo"].str.startswith("C", na=False)]
        d = d[(d["Quantity"] > 0) & (d["UnitPrice"] > 0)]
        d = d[d["StockCode"].str.fullmatch(r"\d{5}[A-Z]{0,2}", na=False)]
        labels = d.dropna(subset=["Description"]).groupby("StockCode")["Description"].first().to_dict()
        pairs = d[["InvoiceNo", "StockCode"]].drop_duplicates()
        baskets_series = pairs.groupby("InvoiceNo")["StockCode"].agg(list)
        transactions = baskets_series.tolist()
        tx_ids = baskets_series.index.astype(str).tolist()
        raw_df = d.head(200)

    return {
        "transactions": transactions,
        "tx_ids": tx_ids,
        "raw_df": raw_df,
        "labels": labels,
        "min_item_support_pre": 0.005,
        "default_minsup": 0.02,
        "default_minconf": 0.60,
        "default_minlift": 1.5,
        "benchmark_sups": (0.06, 0.05, 0.04, 0.03),
    }


# ==============================================================================
# [CHỖ CHÈN ỨNG DỤNG 2] - HÀM TẢI & TIỀN XỬ LÝ DỮ LIỆU ỨNG DỤNG 2
# ==============================================================================
@st.cache_data(show_spinner=False)
def load_app2_data() -> Dict[str, object]:
    """
    ===========================================================================
    HƯỚNG DẪN CHÈN ỨNG DỤNG 2 VÀO ĐÂY:
    ---------------------------------------------------------------------------
    Khi bạn có dữ liệu của Ứng dụng 2 (ví dụ: `data/Ungdung2/...` hoặc `src/Ungdung2/...`):
      1. Đọc file dữ liệu của Ứng dụng 2 tại đây.
      2. Biến đổi thành:
         - `transactions`: List[List[str]] (mỗi phần tử là 1 giỏ/giao dịch gồm các mã/tên item)
         - `raw_df`: pd.DataFrame (bảng giao dịch thô hiển thị ở Tab 1)
         - `labels`: Dict[str, str] (từ điển ánh xạ mã item -> tên hiển thị đầy đủ)
      3. Điều chỉnh ngưỡng mặc định `default_minsup`, `default_minconf`, `default_minlift`.
    ===========================================================================
    """
    # TODO [ỨNG DỤNG 2]: Thay thế đường dẫn file dữ liệu thực của Ứng dụng 2 tại đây
    app2_custom_csv = OUTPUTS_DIR / "Ungdung2" / "transactions.csv"

    labels = {
        "BREAD": "Bánh mì Sandwich",
        "MILK": "Sữa tươi tiệt trùng",
        "DIAPER": "Tã em bé",
        "BEER": "Bia lon",
        "EGGS": "Trứng gà tươi",
        "BUTTER": "Bơ lạt",
        "COLA": "Nước ngọt Cola",
        "CHIPS": "Snack Khoai tây",
    }

    base_transactions = [
        ["BREAD", "MILK"],
        ["BREAD", "DIAPER", "BEER", "EGGS"],
        ["MILK", "DIAPER", "BEER", "COLA"],
        ["BREAD", "MILK", "DIAPER", "BEER"],
        ["BREAD", "MILK", "DIAPER", "COLA"],
        ["BREAD", "MILK", "BUTTER"],
        ["DIAPER", "BEER", "CHIPS"],
        ["BREAD", "MILK", "EGGS", "BUTTER"],
        ["BREAD", "DIAPER", "BEER"],
        ["MILK", "DIAPER", "BEER", "CHIPS"],
    ]

    if app2_custom_csv.exists():
        df_custom = pd.read_csv(app2_custom_csv)
        transactions = [
            [x.strip() for x in str(row).split(",") if x.strip()]
            for row in df_custom.iloc[:, 1].dropna()
        ]
    else:
        transactions = base_transactions * 15 + [
            ["BREAD", "BUTTER", "EGGS"],
            ["BEER", "CHIPS", "COLA"],
            ["MILK", "BREAD", "BUTTER"],
        ] * 10

    tx_ids = [f"APP2-TX-{1001 + i}" for i in range(len(transactions))]
    raw_df = pd.DataFrame(
        [
            {
                "Mã Giao Dịch": tx_ids[i],
                "Số lượng Item": len(items),
                "Mã Items": ", ".join(items),
                "Tên hiển thị": " | ".join(labels.get(x, x) for x in items),
            }
            for i, items in enumerate(transactions[:100])
        ]
    )

    return {
        "transactions": transactions,
        "tx_ids": tx_ids,
        "raw_df": raw_df,
        "labels": labels,
        "min_item_support_pre": 0.0,
        "default_minsup": 0.20,
        "default_minconf": 0.60,
        "default_minlift": 1.1,
        "benchmark_sups": (0.30, 0.20, 0.15, 0.10),
    }


def render_app2_custom_placeholder() -> None:
    """
    [CHỖ CHÈN GIAO DIỆN RIÊNG CỦA ỨNG DỤNG 2]
    Bạn có thể thêm các biểu đồ, bảng thống kê đặc thù của Ứng dụng 2 vào hàm này.
    """
    st.markdown(
        """
        <div class="app2-banner">
            <b>Khu vực chờ tích hợp Ứng dụng 2:</b><br/>
            Hiện tại <b>Ứng dụng 2</b> đang chạy trên bộ dữ liệu mẫu để kiểm thử giao diện.<br/>
            Để chèn Ứng dụng 2 thật vào: mở file <code>app.py</code>, tìm đến hàm
            <code>load_app2_data()</code> và <code>render_app2_custom_placeholder()</code> (đã đánh dấu
            <code>[CHỖ CHÈN ỨNG DỤNG 2]</code>) để gắn dữ liệu của bạn vào.
        </div>
        """,
        unsafe_allow_html=True,
    )


# --- 3. ỨNG DỤNG 3: PHÂN TÍCH BỆNH ĐỒNG MẮC LÂM SÀNG (MIMIC-IV) ---
@st.cache_data(show_spinner=False)
def load_app3_data() -> Dict[str, object]:
    mimic_root = DATA_DIR / "mimic-iv-clinical-database-demo-2.2"
    not_disease_regex = r"^(?:9_[VE]|10_[RVWXYZ])"

    dx_path = mimic_root / "hosp" / "diagnoses_icd.csv.gz"
    dicd_path = mimic_root / "hosp" / "d_icd_diagnoses.csv.gz"

    dx = pd.read_csv(dx_path, dtype={"icd_code": str})
    d_icd = pd.read_csv(dicd_path, dtype={"icd_code": str})

    for t in (dx, d_icd):
        t["icd_code"] = t["icd_code"].str.strip()
        t["icd3"] = t["icd_version"].astype(str) + "_" + t["icd_code"].str[:3]

    dx = dx[~dx["icd3"].str.contains(not_disease_regex, regex=True)].copy()

    top_names = (
        dx.groupby(["icd3", "icd_version", "icd_code"])
        .size()
        .reset_index(name="n")
        .sort_values("n", ascending=False)
        .drop_duplicates("icd3")
        .merge(d_icd[["icd_code", "icd_version", "long_title"]], on=["icd_code", "icd_version"], how="left")
    )
    labels: Dict[str, str] = top_names.set_index("icd3")["long_title"].to_dict()

    grouped_series = dx.groupby("subject_id")["icd3"].apply(lambda s: sorted(set(s)))
    all_transactions = grouped_series.tolist()
    tx_ids = [f"BN-{subj}" for subj in grouped_series.index]

    raw_df = pd.DataFrame(
        [
            {
                "Mã Bệnh Nhân (subject_id)": subj,
                "Tổng số nhóm bệnh (ICD-3)": len(codes),
                "Danh sách Mã ICD-3": ", ".join(codes[:10]) + ("..." if len(codes) > 10 else ""),
                "Các bệnh tiêu biểu": " | ".join(labels.get(c, c) for c in codes[:3]) + ("..." if len(codes) > 3 else ""),
            }
            for subj, codes in grouped_series.items()
        ]
    )

    return {
        "transactions": all_transactions,
        "tx_ids": tx_ids,
        "raw_df": raw_df,
        "labels": labels,
        "min_item_support_pre": 0.0,
        "default_minsup": 0.10,
        "default_minconf": 0.60,
        "default_minlift": 1.05,
        "benchmark_sups": (0.20, 0.15, 0.10, 0.08),
    }


# ==============================================================================
# GIAO DIỆN CHÍNH: SIDEBAR & 4 TABS
# ==============================================================================
def main() -> None:
    app_choice = st.sidebar.radio(
        "Chọn Ứng dụng:",
        options=[
            "Ứng dụng 1: Giỏ hàng Bán lẻ (Online Retail)",
            "Ứng dụng 2: [Chờ tích hợp - Demo mẫu]",
            "Ứng dụng 3: Bệnh đồng mắc (MIMIC-IV)",
        ],
        index=0,
    )

    with st.spinner("Đang nạp và chuẩn hóa dữ liệu..."):
        if app_choice.startswith("Ứng dụng 1"):
            app_key = "app1"
            bundle = load_app1_data()
        elif app_choice.startswith("Ứng dụng 2"):
            app_key = "app2"
            bundle = load_app2_data()
        else:
            app_key = "app3"
            bundle = load_app3_data()

    transactions: List[List[str]] = bundle["transactions"]  # type: ignore[assignment]
    tx_ids: List[str] = bundle["tx_ids"]  # type: ignore[assignment]
    raw_df: pd.DataFrame = bundle["raw_df"]  # type: ignore[assignment]
    labels: Dict[str, str] = bundle["labels"]  # type: ignore[assignment]
    min_item_sup_pre: float = float(bundle["min_item_support_pre"])  # type: ignore[arg-type]
    default_minsup: float = float(bundle["default_minsup"])  # type: ignore[arg-type]
    default_minconf: float = float(bundle["default_minconf"])  # type: ignore[arg-type]
    default_minlift: float = float(bundle["default_minlift"])  # type: ignore[arg-type]
    benchmark_sups: Tuple[float, ...] = bundle["benchmark_sups"]  # type: ignore[assignment]

    st.sidebar.divider()
    st.sidebar.subheader("Tham số Thuật toán")

    if app_key == "app1":
        min_support = st.sidebar.slider(
            "Ngưỡng Support tối thiểu (min_sup):",
            min_value=0.005,
            max_value=0.10,
            value=default_minsup,
            step=0.005,
            format="%.3f",
        )
    else:
        min_support = st.sidebar.slider(
            "Ngưỡng Support tối thiểu (min_sup):",
            min_value=0.05,
            max_value=0.50,
            value=default_minsup,
            step=0.01,
            format="%.2f",
        )

    min_confidence = st.sidebar.slider(
        "Ngưỡng Confidence tối thiểu (min_conf):",
        min_value=0.10,
        max_value=1.00,
        value=default_minconf,
        step=0.05,
        format="%.2f",
    )

    min_lift = st.sidebar.slider(
        "Ngưỡng Lift tối thiểu (min_lift):",
        min_value=1.0,
        max_value=10.0,
        value=default_minlift,
        step=0.1,
        format="%.1f",
    )

    max_len = st.sidebar.slider(
        "Độ dài tập phổ biến tối đa (max_len):",
        min_value=2,
        max_value=5,
        value=3 if app_key != "app3" else 4,
        step=1,
    )

    encoded_df, _ = encode_transactions_sparse(transactions, min_item_support=min_item_sup_pre)
    freq_df, rules_df, fpgrowth_ms = run_fpgrowth_mining(
        encoded_df=encoded_df,
        min_support=min_support,
        min_confidence=min_confidence,
        min_lift=min_lift,
        max_len=max_len,
    )

    st.title(app_choice)

    n_trans = len(transactions)
    all_unique_items = len({x for t in transactions for x in t})
    min_sup_count = math.ceil(min_support * n_trans)

    is_clinical = app_key == "app3"
    unit_name = "hồ sơ bệnh nhân" if is_clinical else "giao dịch"
    unit_count_col = "Số bệnh nhân" if is_clinical else "Số giao dịch"
    id_col_name = "Mã Bệnh Nhân" if is_clinical else ("Mã Hóa Đơn" if app_key == "app1" else "Mã Giao Dịch")

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Số bệnh nhân" if is_clinical else "Số giao dịch", f"{n_trans:,}")
    kpi2.metric("Tổng số Mã bệnh phân biệt" if is_clinical else "Tổng số Items phân biệt", f"{all_unique_items:,}")
    kpi3.metric("Ngưỡng đếm (min_count)", f"{min_sup_count:,} ({min_support*100:.1f}%)")
    kpi4.metric("Tập phổ biến tìm được", f"{len(freq_df):,}")
    kpi5.metric("Luật kết hợp thỏa ngưỡng", f"{len(rules_df):,}")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Khám phá dữ liệu",
            "Giải phẫu FP-Tree",
            "Khai phá Luật & Hệ thống Gợi ý",
            "So sánh Hiệu năng (FP-Growth vs. Apriori)",
        ]
    )

    # --------------------------------------------------------------------------
    # TAB 1: CHỈ CHỨA RAW DATA VÀ TOP 10 ITEMS XUẤT HIỆN NHIỀU NHẤT
    # --------------------------------------------------------------------------
    with tab1:
        st.subheader("Dữ liệu hồ sơ bệnh nhân (Raw Data)" if is_clinical else "Dữ liệu giao dịch thô (Raw Data)")
        st.dataframe(raw_df, width="stretch", height=300)

        st.divider()

        st.subheader("Top 10 Mã bệnh xuất hiện nhiều nhất" if is_clinical else "Top 10 Items xuất hiện nhiều nhất")
        item_counter = Counter(x for t in transactions for x in set(t))
        top10 = item_counter.most_common(10)
        top10_df = pd.DataFrame(
            [
                {
                    "Mã Item": k,
                    "Tên hiển thị": f"{labels.get(k, k)} ({k})" if labels.get(k, k) != k else str(k),
                    unit_count_col: v,
                    "Support (%)": round(v / max(1, n_trans) * 100, 2),
                }
                for k, v in top10
            ]
        )
        fig_bar = px.bar(
            top10_df.iloc[::-1],
            x="Support (%)",
            y="Tên hiển thị",
            orientation="h",
            text=unit_count_col,
            color="Support (%)",
            color_continuous_scale="Blues",
        )
        fig_bar.update_layout(height=400, margin=dict(l=10, r=10, t=20, b=10), showlegend=False)
        st.plotly_chart(fig_bar, width="stretch")

    # --------------------------------------------------------------------------
    # TAB 2: GIẢI PHẪU FP-TREE (MẶC ĐỊNH VẼ MINI FP-TREE)
    # --------------------------------------------------------------------------
    with tab2:
        st.subheader("Giải phẫu cấu trúc Cây FP-Tree & Bảng Header Table (F-List)")

        fptree_obj = WhiteBoxFPTree(transactions=transactions, min_support_count=min_sup_count)
        header_df = fptree_obj.get_header_dataframe(labels)

        if header_df.empty:
            st.warning(
                "Không có item nào thỏa ngưỡng min_support hiện tại để tạo F-List và cây FP-Tree. "
                "Hãy giảm thanh trượt min_support ở Sidebar."
            )
        else:
            col_flist, col_tree = st.columns([1.0, 1.35])

            with col_flist:
                st.markdown("#### Bảng Header Table (F-List)")
                st.dataframe(header_df, width="stretch", height=380, hide_index=True)

            with col_tree:
                st.markdown("#### Sơ đồ Mini FP-Tree")
                ctrl_col1, ctrl_col2 = st.columns([1.2, 1.0])
                with ctrl_col1:
                    num_tree_tx = st.slider(
                        f"Số lượng {unit_name} dùng để vẽ cây:",
                        min_value=3,
                        max_value=30,
                        value=10,
                        step=1,
                    )
                with ctrl_col2:
                    show_dashed_links = st.checkbox(
                        "Hiển thị mũi tên nét đứt (Node-Link)",
                        value=True,
                    )

                # Lọc các giao dịch/hồ sơ có chứa ít nhất 1 item thuộc Top 8 F-List để vẽ cây trực quan
                top8_flist = fptree_obj.flist_order[:8]
                top8_items = set(top8_flist)
                selected_records = []
                for idx_tx, t in enumerate(transactions):
                    filtered_items = [x for x in t if x in top8_items]
                    if filtered_items:
                        tx_code = tx_ids[idx_tx] if idx_tx < len(tx_ids) else f"GD-{idx_tx+1}"
                        selected_records.append((tx_code, t, filtered_items))
                    if len(selected_records) == num_tree_tx:
                        break

                mini_trans = [rec[2] for rec in selected_records]
                mini_tree = WhiteBoxFPTree(
                    mini_trans,
                    min_support_count=1,
                    fixed_flist_order=top8_flist,
                )
                mini_dot = mini_tree.to_graphviz_dot(
                    item_labels=labels,
                    show_node_links=show_dashed_links,
                    max_nodes=80,
                )
                st.graphviz_chart(mini_dot, width="stretch")

            st.divider()
            st.markdown(f"#### Danh sách {len(selected_records)} {unit_name} đã chọn để dựng cây Mini FP-Tree")
            selected_tx_rows = []
            for stt, ((tx_code, orig_items, filt_items), ordered_branch) in enumerate(
                zip(selected_records, mini_tree.ordered_transactions), start=1
            ):
                selected_tx_rows.append(
                    {
                        "STT": stt,
                        id_col_name: tx_code,
                        "Items gốc (thuộc Top F-List)": ", ".join(filt_items),
                        "Nhánh chèn vào FP-Tree (Theo thứ tự F-List)": "{null} -> " + " -> ".join(ordered_branch),
                        "Chi tiết Tên trên nhánh": " -> ".join(labels.get(x, x) for x in ordered_branch),
                    }
                )
            st.dataframe(pd.DataFrame(selected_tx_rows), width="stretch", hide_index=True)

    # --------------------------------------------------------------------------
    # TAB 3: KHAI PHÁ LUẬT & HỆ THỐNG GỢI Ý (RULES & LIVE RECOMMENDER)
    # --------------------------------------------------------------------------
    with tab3:
        st.subheader("1. Live Recommender")

        if not rules_df.empty:
            antecedent_items = sorted({item for s in rules_df["antecedents"] for item in s})
        else:
            antecedent_items = fptree_obj.flist_order[:30]

        default_basket = antecedent_items[:1] if antecedent_items else []
        selected_basket = st.multiselect(
            "Live Recommender",
            options=antecedent_items,
            default=default_basket,
            format_func=lambda x: f"{x} — {labels.get(x, x)}",
            label_visibility="collapsed",
        )

        if selected_basket:
            basket_set = frozenset(selected_basket)
            if rules_df.empty:
                st.warning("Chưa có luật kết hợp nào ở ngưỡng hiện tại. Hãy giảm min_support hoặc min_confidence.")
            else:
                exact_matches = rules_df[
                    (rules_df["antecedents"] == basket_set)
                    & (rules_df["consequents"].map(lambda c: len(c - basket_set) > 0))
                ]
                subset_matches = rules_df[
                    (rules_df["antecedents"].map(lambda a: a.issubset(basket_set)))
                    & (rules_df["consequents"].map(lambda c: len(c - basket_set) > 0))
                ]

                matched_rules = exact_matches if not exact_matches.empty else subset_matches
                matched_rules = matched_rules.sort_values(["lift", "confidence"], ascending=False)

                if matched_rules.empty:
                    st.info("Không tìm thấy luật gợi ý trực tiếp cho tổ hợp này.")
                else:
                    rec_cols = st.columns(min(4, len(matched_rules)))
                    for idx, (_, r_row) in enumerate(matched_rules.head(4).iterrows()):
                        ant_names = ", ".join(f"{labels.get(x, x)} ({x})" for x in sorted(r_row["antecedents"]))
                        con_codes = [x for x in sorted(r_row["consequents"]) if x not in basket_set]
                        con_names = ", ".join(f"<b>{labels.get(x, x)}</b> ({x})" for x in con_codes)
                        with rec_cols[idx]:
                            st.markdown(
                                f"""
                                <div class="rec-card">
                                    <div style="font-size:0.84rem; opacity:0.75;">Khi đã có: {ant_names}</div>
                                    <div style="font-size:1.0rem; margin: 8px 0;">Gợi ý: {con_names}</div>
                                    <div style="font-size:0.88rem; font-weight:600;">
                                        Confidence: {r_row['confidence']*100:.1f}% &nbsp;|&nbsp; Lift: {r_row['lift']:.2f}x
                                    </div>
                                    <div style="font-size:0.8rem; opacity:0.7;">Support: {r_row['support']*100:.2f}%</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

        st.divider()

        col_fi, col_ar = st.columns([1.0, 1.35])

        with col_fi:
            st.subheader("2. Tập phổ biến (Frequent Itemsets)")
            if freq_df.empty:
                st.info("Không có tập phổ biến nào thỏa ngưỡng.")
            else:
                fi_display = freq_df.copy()
                fi_display["Mã Itemsets"] = fi_display["itemsets"].map(lambda s: ", ".join(sorted(s)))
                fi_display["Tên chi tiết"] = fi_display["itemsets"].map(
                    lambda s: " + ".join(labels.get(x, x) for x in sorted(s))
                )
                fi_display["Support"] = fi_display["support"].round(4)
                fi_display = fi_display[["Mã Itemsets", "Tên chi tiết", "length", "count", "Support"]].rename(
                    columns={"length": "Số phần tử", "count": unit_count_col}
                )
                st.dataframe(fi_display, width="stretch", height=360, hide_index=True)

        with col_ar:
            st.subheader("3. Bảng Luật Kết Hợp (Association Rules)")
            if rules_df.empty:
                st.info("Không có luật kết hợp nào thỏa mãn đồng thời min_support, min_confidence và min_lift.")
            else:
                ar_display = rules_df.copy()
                ar_display["Antecedents (X)"] = ar_display["antecedents"].map(
                    lambda s: " + ".join(f"{labels.get(x, x)} ({x})" if labels.get(x, x) != x else x for x in sorted(s))
                )
                ar_display["Consequents (Y)"] = ar_display["consequents"].map(
                    lambda s: " + ".join(f"{labels.get(x, x)} ({x})" if labels.get(x, x) != x else x for x in sorted(s))
                )
                ar_display["Support"] = ar_display["support"].round(4)
                ar_display["Confidence"] = ar_display["confidence"].round(4)
                ar_display["Lift"] = ar_display["lift"].round(3)
                ar_display = ar_display[["Antecedents (X)", "Consequents (Y)", "Support", "Confidence", "Lift"]]
                st.dataframe(ar_display, width="stretch", height=360, hide_index=True)

    # --------------------------------------------------------------------------
    # TAB 4: CHỈ CHỨA BIỂU ĐỒ VÀ BẢNG SỐ LIỆU BENCHMARK CHI TIẾT
    # --------------------------------------------------------------------------
    with tab4:
        st.subheader("So sánh Hiệu năng: FP-Growth vs. Apriori")

        with st.spinner("Đang tính toán Benchmark..."):
            bench_df = run_benchmark_comparison(
                encoded_df=encoded_df,
                support_thresholds=benchmark_sups,
                max_len=max_len,
            )

        bcol1, bcol2 = st.columns(2)
        with bcol1:
            fig_time = px.line(
                bench_df,
                x="min_support_label",
                y="Thời gian chạy (ms)",
                color="Thuật toán",
                markers=True,
                text="Thời gian chạy (ms)",
                color_discrete_map={"FP-Growth": "#4f46e5", "Apriori": "#ef4444"},
                title="Thời gian chạy (ms)",
            )
            fig_time.update_traces(textposition="top center", line=dict(width=3))
            fig_time.update_layout(height=400, xaxis_title="Ngưỡng min_support")
            st.plotly_chart(fig_time, width="stretch")

        with bcol2:
            fig_mem = px.line(
                bench_df,
                x="min_support_label",
                y="Bộ nhớ đỉnh (MB)",
                color="Thuật toán",
                markers=True,
                text="Bộ nhớ đỉnh (MB)",
                color_discrete_map={"FP-Growth": "#059669", "Apriori": "#f97316"},
                title="Bộ nhớ RAM đỉnh (MB)",
            )
            fig_mem.update_traces(textposition="top center", line=dict(width=3))
            fig_mem.update_layout(height=400, xaxis_title="Ngưỡng min_support")
            st.plotly_chart(fig_mem, width="stretch")

        st.markdown("#### Bảng số liệu Benchmark chi tiết")
        st.dataframe(bench_df, width="stretch", hide_index=True)


if __name__ == "__main__":
    main()
