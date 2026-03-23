import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

#Genera el dataset en python

TOTAL_ROWS = 2_000_000
SEED = 42
OUTPUT_FILE = "fichas_clinicas_mock.csv"
ICD10_WEIGHTS = [
    ("J00", 0.12),
    ("I10", 0.16),
    ("E11", 0.15),
    ("K21", 0.08),
    ("M54", 0.12),
    ("N39", 0.10),
    ("F32", 0.07),
    ("J45", 0.08),
    ("A09", 0.07),
    ("B34", 0.05),
]
SEX_VALUES = ("M", "F", "X")
SEX_WEIGHTS = (0.485, 0.495, 0.02)
START_DATE = date(2019, 1, 1)
END_DATE = date(2025, 12, 31)
DATE_SPAN_DAYS = (END_DATE - START_DATE).days


def generate_age(rng: random.Random) -> int:
    bucket = rng.choices(
        population=("child", "teen", "young_adult", "adult", "older_adult", "elder"),
        weights=(0.08, 0.08, 0.17, 0.31, 0.23, 0.13),
        k=1,
    )[0]

    ranges = {
        "child": (0, 9),
        "teen": (10, 19),
        "young_adult": (20, 39),
        "adult": (40, 59),
        "older_adult": (60, 79),
        "elder": (80, 100),
    }
    low, high = ranges[bucket]
    return rng.randint(low, high)


def generate_rows(total_rows: int, output_path: Path, seed: int) -> None:
    rng = random.Random(seed)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["id_ficha", "edad", "sexo", "codigo_icd10", "fecha_atencion"])

        for row_id in range(1, total_rows + 1):
            age = generate_age(rng)
            sex = rng.choices(SEX_VALUES, weights=SEX_WEIGHTS, k=1)[0]
            icd10 = rng.choices(
                population=[code for code, _ in ICD10_WEIGHTS],
                weights=[weight for _, weight in ICD10_WEIGHTS],
                k=1,
            )[0]
            attention_date = START_DATE + timedelta(days=rng.randint(0, DATE_SPAN_DAYS))
            writer.writerow([row_id, age, sex, icd10, attention_date.isoformat()])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera el dataset CSV para el benchmark triple Python vs Java vs SQL."
    )
    parser.add_argument("--rows", type=int, default=TOTAL_ROWS, help="Cantidad de filas a generar.")
    parser.add_argument("--seed", type=int, default=SEED, help="Semilla fija para reproducibilidad.")
    parser.add_argument(
        "--output",
        default=OUTPUT_FILE,
        help="Ruta de salida del CSV. Por defecto: fichas_clinicas_mock.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate_rows(args.rows, Path(args.output), args.seed)
    print(
        f"CSV generado: {args.output} | filas={args.rows} | seed={args.seed}"
    )


if __name__ == "__main__":
    main()
