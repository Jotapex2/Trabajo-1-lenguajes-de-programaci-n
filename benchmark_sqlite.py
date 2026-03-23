import argparse
import sqlite3
import time
from pathlib import Path


QUERY = """
SELECT
    codigo_icd10,
    CASE
        WHEN edad BETWEEN 0 AND 9 THEN '0-9'
        WHEN edad BETWEEN 10 AND 19 THEN '10-19'
        WHEN edad BETWEEN 20 AND 29 THEN '20-29'
        WHEN edad BETWEEN 30 AND 39 THEN '30-39'
        WHEN edad BETWEEN 40 AND 49 THEN '40-49'
        WHEN edad BETWEEN 50 AND 59 THEN '50-59'
        WHEN edad BETWEEN 60 AND 69 THEN '60-69'
        WHEN edad BETWEEN 70 AND 79 THEN '70-79'
        ELSE '80+'
    END AS rango_etario,
    COUNT(*) AS frecuencia
FROM staging_fichas
GROUP BY codigo_icd10, rango_etario
ORDER BY codigo_icd10, rango_etario
"""


def run_benchmark(csv_path: Path) -> tuple[float, int, list[tuple[str, str, int]]]:
    connection = sqlite3.connect(":memory:")
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE staging_fichas (
            id_ficha INTEGER NOT NULL,
            edad INTEGER NOT NULL,
            sexo TEXT NOT NULL,
            codigo_icd10 TEXT NOT NULL,
            fecha_atencion TEXT NOT NULL
        )
        """
    )

    start = time.perf_counter()
    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        cursor.execute(
            """
            CREATE TEMP TABLE raw_csv (
                id_ficha TEXT,
                edad TEXT,
                sexo TEXT,
                codigo_icd10 TEXT,
                fecha_atencion TEXT
            )
            """
        )

        import csv as csv_module

        reader = csv_module.DictReader(csv_file)
        cursor.executemany(
            """
            INSERT INTO raw_csv (id_ficha, edad, sexo, codigo_icd10, fecha_atencion)
            VALUES (:id_ficha, :edad, :sexo, :codigo_icd10, :fecha_atencion)
            """,
            reader,
        )

    cursor.execute(
        """
        INSERT INTO staging_fichas (id_ficha, edad, sexo, codigo_icd10, fecha_atencion)
        SELECT
            CAST(id_ficha AS INTEGER),
            CAST(edad AS INTEGER),
            sexo,
            codigo_icd10,
            fecha_atencion
        FROM raw_csv
        """
    )

    processed_rows = cursor.execute("SELECT COUNT(*) FROM staging_fichas").fetchone()[0]
    grouped_rows = cursor.execute(QUERY).fetchall()
    elapsed = time.perf_counter() - start

    connection.close()
    return elapsed, processed_rows, grouped_rows


def print_results(elapsed: float, processed_rows: int, grouped_rows: list[tuple[str, str, int]]) -> None:
    print("Benchmark: SQL (SQLite en memoria)")
    print(f"Tiempo total de ejecucion: {elapsed:.6f} segundos")
    print(f"Total de registros procesados: {processed_rows}")
    print(f"Total de combinaciones agrupadas: {len(grouped_rows)}")
    print("Primeras 10 filas:")
    print("codigo_icd10 | rango_etario | frecuencia")
    for code, age_bucket, count in grouped_rows[:10]:
        print(f"{code} | {age_bucket} | {count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ejecuta el benchmark SQL usando SQLite en memoria y CSV como fuente."
    )
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
