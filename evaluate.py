"""
Evaluation & Benchmark Suite
Runs 40 ground truth queries across:
1. Naive Keyword Search
2. Naive Vector Search (Isolated)
3. Contextual Hinglish Hybrid Search
Computes Hit@1, Hit@5, MRR, Latency, and Zero-Keyword Overlap performance.
"""

import json
import time
import os
import sys

# Ensure engine is on sys.path
engine_dir = os.path.join(os.path.dirname(__file__), "engine")
if os.path.exists(engine_dir):
    sys.path.insert(0, engine_dir)
sys.path.insert(0, os.path.dirname(__file__))

from search_engine import GroupChatSearchEngine

def run_evaluation(data_dir, output_file=None):
    data_path = os.path.join(data_dir, "group_chat_data.json")
    bench_path = os.path.join(data_dir, "benchmark_queries.json")

    print(f"Loading data from {data_path}...")
    with open(data_path, "r", encoding="utf-8") as f:
        messages = json.load(f)

    print(f"Loading benchmark queries from {bench_path}...")
    with open(bench_path, "r", encoding="utf-8") as f:
        benchmark = json.load(f)

    print(f"Initializing Search Engine over {len(messages)} messages...")
    t0 = time.time()
    engine = GroupChatSearchEngine(messages)
    init_time = time.time() - t0
    print(f"Engine initialized in {init_time:.2f}s")

    modes = ["naive_text", "naive_vector", "contextual_hybrid"]
    metrics = {
        m: {
            "total": len(benchmark),
            "hit_at_1": 0,
            "hit_at_5": 0,
            "mrr": 0.0,
            "zero_keyword_total": 0,
            "zero_keyword_hit_at_1": 0,
            "zero_keyword_hit_at_5": 0,
            "zero_keyword_mrr": 0.0,
            "total_latency_ms": 0.0,
            "details": []
        }
        for m in modes
    }

    for q in benchmark:
        qid = q["query_id"]
        qtext = q["query"]
        target_id = q["target_message_id"]
        is_zero = q.get("zero_keyword_overlap", False)

        for mode in modes:
            start_t = time.perf_counter()
            results = engine.search(qtext, mode=mode, top_k=5, context_window=4)
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0

            metrics[mode]["total_latency_ms"] += elapsed_ms

            target_rank = None
            for idx, res in enumerate(results, 1):
                if res["target_message_id"] == target_id:
                    target_rank = idx
                    break
                # Also check if target is visible inside surrounding window
                elif target_id in [m["id"] for m in res["surrounding_window"]]:
                    if target_rank is None:
                        target_rank = idx

            hit1 = (target_rank == 1)
            hit5 = (target_rank is not None and target_rank <= 5)
            rr = 1.0 / target_rank if target_rank else 0.0

            if hit1:
                metrics[mode]["hit_at_1"] += 1
            if hit5:
                metrics[mode]["hit_at_5"] += 1
            metrics[mode]["mrr"] += rr

            if is_zero:
                metrics[mode]["zero_keyword_total"] += 1
                if hit1:
                    metrics[mode]["zero_keyword_hit_at_1"] += 1
                if hit5:
                    metrics[mode]["zero_keyword_hit_at_5"] += 1
                metrics[mode]["zero_keyword_mrr"] += rr

            metrics[mode]["details"].append({
                "query_id": qid,
                "query": qtext,
                "category": q["category"],
                "target_id": target_id,
                "zero_keyword_overlap": is_zero,
                "target_rank": target_rank,
                "hit1": hit1,
                "hit5": hit5,
                "reciprocal_rank": rr,
                "latency_ms": round(elapsed_ms, 2)
            })

    # Summary calculations
    summary = {}
    for mode in modes:
        tot = metrics[mode]["total"]
        z_tot = metrics[mode]["zero_keyword_total"]
        summary[mode] = {
            "mode_name": mode,
            "overall_accuracy_hit1": round((metrics[mode]["hit_at_1"] / tot) * 100, 1),
            "overall_recall_hit5": round((metrics[mode]["hit_at_5"] / tot) * 100, 1),
            "overall_mrr": round(metrics[mode]["mrr"] / tot, 3),
            "zero_keyword_hit1": round((metrics[mode]["zero_keyword_hit_at_1"] / z_tot) * 100, 1) if z_tot else 0,
            "zero_keyword_hit5": round((metrics[mode]["zero_keyword_hit_at_5"] / z_tot) * 100, 1) if z_tot else 0,
            "zero_keyword_mrr": round(metrics[mode]["zero_keyword_mrr"] / z_tot, 3) if z_tot else 0,
            "avg_latency_ms": round(metrics[mode]["total_latency_ms"] / tot, 2)
        }

    # Print clean benchmark report
    print("\n" + "="*80)
    print("           BENCHMARK EVALUATION RESULTS (40 GROUND TRUTH QUERIES)")
    print("="*80)
    header = f"{'Search Engine Mode':<25} | {'Hit@1':<8} | {'Hit@5':<8} | {'MRR':<8} | {'Zero-KW Hit@5':<14} | {'Latency':<8}"
    print(header)
    print("-" * 80)
    for m in modes:
        s = summary[m]
        line = f"{s['mode_name']:<25} | {s['overall_accuracy_hit1']:<6}% | {s['overall_recall_hit5']:<6}% | {s['overall_mrr']:<8} | {s['zero_keyword_hit5']:<12}% | {s['avg_latency_ms']:<5}ms"
        print(line)
    print("="*80 + "\n")

    report = {
        "dataset_size": len(messages),
        "benchmark_queries_count": len(benchmark),
        "zero_keyword_queries_count": metrics["contextual_hybrid"]["zero_keyword_total"],
        "summary": summary,
        "detailed_metrics": metrics
    }

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"Full benchmark report saved to {output_file}")

    return report

if __name__ == "__main__":
    d_dir = sys.argv[1] if len(sys.argv) > 1 else "./data"
    out_f = sys.argv[2] if len(sys.argv) > 2 else os.path.join(d_dir, "evaluation_results.json")
    run_evaluation(d_dir, out_f)
