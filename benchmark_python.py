import argparse
import csv
import time
from collections import Counter
from pathlib import Path

#Corre el benchmark en python. Primero define el rango de edad

def age_range(age: int) -> str:
    if age < 10:
        return "0-9"
    if age < 20:
        return "10-19"
    if age < 30:
        return "20-29"
    if age < 40:
        return "30-39"
    if age < 50:
        return "40-49"
    if age < 60:
        return "50-59"
    if age < 70:
        return "60-69"
    if age < 80:
        return "70-79"
    return "80+"

#Corre el benchmark

def run_benchmark(csv_path: Path) -> tuple[float, int, list[tuple[str, str, int]]]:
    counter: Counter[tuple[str, str]] = Counter()
    processed_rows = 0

    start = time.perf_counter()
    with csv_path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            counter[(row["codigo_icd10"], age_range(int(row["edad"])))] += 1
            processed_rows += 1
    elapsed = time.perf_counter() - start

    grouped_rows = sorted(
        ((code, age_bucket, count) for (code, age_bucket), count in counter.items()),
        key=lambda item: (item[0], item[1]),
    )
    return elapsed, processed_rows, grouped_rows


def print_results(elapsed: float, processed_rows: int, grouped_rows: list[tuple[str, str, int]]) -> None:
    print("Benchmark: Python")
    print(f"Tiempo total de ejecucion: {elapsed:.6f} segundos")
    print(f"Total de registros procesados: {processed_rows}")
    print(f"Total de combinaciones agrupadas: {len(grouped_rows)}")
    print("Primeras 10 filas:")
    print("codigo_icd10 | rango_etario | frecuencia")
    for code, age_bucket, count in grouped_rows[:10]:
        print(f"{code} | {age_bucket} | {count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ejecuta el benchmark de Python sobre el CSV.")
    parser.add_argument(
        "--csv",
        default="fichas_clinicas_mock.csv",
        help="Ruta al CSV de entrada. Por defecto: fichas_clinicas_mock.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    elapsed, processed_rows, grouped_rows = run_benchmark(Path(args.csv))
    print_results(elapsed, processed_rows, grouped_rows)


if __name__ == "__main__":
    main()
