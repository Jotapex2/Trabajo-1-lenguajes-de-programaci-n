import argparse
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import benchmark_python
import benchmark_sqlite
import generate_dataset

BASE_DIR = Path(__file__).resolve().parent

#Este es el archivo main, genera primero el archivo CSV y después ejecuta los benchmark en orden:"Python", "Java" y "SQL" y entrega las respuestas en orden.
#El benchmark de SQL está sobre SQLLITE y se ejecuta en un script .py
@dataclass
class BenchmarkRun:
    name: str
    elapsed_seconds: float
    processed_rows: int
    grouped_rows: int
    sample_rows: list[tuple[str, str, int]]


def run_setup(csv_path: Path, rows: int, seed: int) -> None:
    print("=== FASE 1: SETUP ===")
    print(f"Generando CSV: {csv_path}")
    generate_dataset.generate_rows(rows, csv_path, seed)
    print(f"CSV generado con {rows} filas y seed={seed}")

    print("Compilando benchmark Java...")
    subprocess.run(
        ["javac", str(BASE_DIR / "benchmark_java" / "src" / "BenchmarkJava.java")],
        check=True,
    )
    print("Compilacion Java finalizada")
    print()


def run_python(csv_path: Path) -> BenchmarkRun:
    elapsed, processed_rows, grouped_rows = benchmark_python.run_benchmark(csv_path)
    return BenchmarkRun(
        name="Python",
        elapsed_seconds=elapsed,
        processed_rows=processed_rows,
        grouped_rows=len(grouped_rows),
        sample_rows=grouped_rows[:10],
    )


def run_sql(csv_path: Path) -> BenchmarkRun:
    elapsed, processed_rows, grouped_rows = benchmark_sqlite.run_benchmark(csv_path)
    return BenchmarkRun(
        name="SQL",
        elapsed_seconds=elapsed,
        processed_rows=processed_rows,
        grouped_rows=len(grouped_rows),
        sample_rows=grouped_rows[:10],
    )


def parse_java_output(output: str) -> BenchmarkRun:
    elapsed = None
    processed_rows = None
    grouped_rows = None
    sample_rows: list[tuple[str, str, int]] = []
    capture_sample = False

    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("Benchmark:"):
            continue
        if line.startswith("Tiempo total de ejecucion:"):
            elapsed = float(line.split(":", 1)[1].strip().split()[0])
        elif line.startswith("Total de registros procesados:"):
            processed_rows = int(line.split(":", 1)[1].strip())
        elif line.startswith("Total de combinaciones agrupadas:"):
            grouped_rows = int(line.split(":", 1)[1].strip())
        elif line == "codigo_icd10 | rango_etario | frecuencia":
            capture_sample = True
        elif capture_sample:
            code, age_bucket, frequency = [part.strip() for part in line.split("|")]
            sample_rows.append((code, age_bucket, int(frequency)))

    if elapsed is None or processed_rows is None or grouped_rows is None:
        raise ValueError("No se pudo parsear la salida del benchmark Java.")

    return BenchmarkRun(
        name="Java",
        elapsed_seconds=elapsed,
        processed_rows=processed_rows,
        grouped_rows=grouped_rows,
        sample_rows=sample_rows[:10],
    )


def run_java(csv_path: Path) -> BenchmarkRun:
    result = subprocess.run(
        ["java", "-cp", str(BASE_DIR / "benchmark_java" / "src"), "BenchmarkJava", str(csv_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return parse_java_output(result.stdout)


def print_run_result(run: BenchmarkRun) -> None:
    print(f"Benchmark: {run.name}")
    print(f"Tiempo total de ejecucion: {run.elapsed_seconds:.6f} segundos")
    print(f"Total de registros procesados: {run.processed_rows}")
    print(f"Total de combinaciones agrupadas: {run.grouped_rows}")
    print("Primeras 10 filas:")
    print("codigo_icd10 | rango_etario | frecuencia")
    for code, age_bucket, count in run.sample_rows:
        print(f"{code} | {age_bucket} | {count}")
    print()


def compare_runs(runs: list[BenchmarkRun]) -> None:
    ordered = sorted(runs, key=lambda item: item.elapsed_seconds)
    fastest = ordered[0]

    print("=== COMPARACION FINAL ===")
    print("Ranking por tiempo total:")
    for index, run in enumerate(ordered, start=1):
        delta = run.elapsed_seconds - fastest.elapsed_seconds
        print(
            f"{index}. {run.name}: {run.elapsed_seconds:.6f} s "
            f"(+{delta:.6f} s vs mas rapido)"
        )
    print()

    print(f"Mas rapido: {fastest.name}")
    for run in ordered[1:]:
        ratio = run.elapsed_seconds / fastest.elapsed_seconds if fastest.elapsed_seconds else float("inf")
        print(f"{run.name} tarda {ratio:.2f}x respecto de {fastest.name}")
    print()


def print_multi_run_summary(history: dict[str, list[BenchmarkRun]]) -> None:
    print("=== RESUMEN MULTI-RUN ===")
    for name, runs in history.items():
        elapsed_values = [run.elapsed_seconds for run in runs]
        avg = statistics.mean(elapsed_values)
        best = min(elapsed_values)
        worst = max(elapsed_values)
        deviation = statistics.pstdev(elapsed_values) if len(elapsed_values) > 1 else 0.0
        print(
            f"{name}: promedio={avg:.6f} s | minimo={best:.6f} s | "
            f"maximo={worst:.6f} s | desvio={deviation:.6f} s"
        )
    print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Runner maestro del benchmark triple: setup + Python + Java + SQL."
    )
    parser.add_argument("--rows", type=int, default=2_000_000, help="Filas del CSV a generar.")
    parser.add_argument("--seed", type=int, default=42, help="Semilla para generar el CSV.")
    parser.add_argument(
        "--csv",
        default="fichas_clinicas_mock.csv",
        help="Ruta del CSV generado y usado por los benchmarks.",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Cantidad de veces que se ejecuta la fase benchmark completa.",
    )
    parser.add_argument(
        "--skip-setup",
        action="store_true",
        help="Salta la generacion del CSV y la compilacion Java si ya estan listos.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    csv_path = Path(args.csv)
    if not csv_path.is_absolute():
        csv_path = BASE_DIR / csv_path

    if args.repeat < 1:
        raise SystemExit("--repeat debe ser mayor o igual a 1")

    if not args.skip_setup:
        run_setup(csv_path, args.rows, args.seed)
    else:
        print("=== FASE 1: SETUP ===")
        print("Setup omitido por --skip-setup")
        print()

    print("=== FASE 2: BENCHMARK ===")
    runners = [run_python, run_java, run_sql]
    history: dict[str, list[BenchmarkRun]] = {"Python": [], "Java": [], "SQL": []}

    for iteration in range(1, args.repeat + 1):
        print(f"Corrida {iteration} de {args.repeat}")
        current_runs: list[BenchmarkRun] = []
        for runner in runners:
            start_wall = time.perf_counter()
            run = runner(csv_path)
            end_wall = time.perf_counter()
            current_runs.append(run)
            history[run.name].append(run)
            print_run_result(run)
            print(f"Duracion total observada por el maestro para {run.name}: {end_wall - start_wall:.6f} segundos")
            print()
        compare_runs(current_runs)

    if args.repeat > 1:
        print_multi_run_summary(history)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"Error ejecutando comando externo: {exc}", file=sys.stderr)
        raise
