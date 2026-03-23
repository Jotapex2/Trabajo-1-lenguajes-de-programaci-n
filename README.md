# Benchmark Triple: Python vs Java vs SQL con CSV

Este proyecto implementa el benchmark pedido para comparar `Python`, `Java` y `SQL` resolviendo exactamente el mismo problema sobre un origen exclusivo en `CSV`. Este fue creado por Juan Pablo González, Rebeca Huerta e Isabel Marín para el trabajo de Lenguajes de Programación. 

## Problema de negocio
Se generará un archivo CSV de prueba con el siguiente nombre:`fichas_clinicas_mock.csv`

Cada implementación debe:

1. Leer el CSV.
2. Construir `rango_etario` desde `edad`.
3. Agrupar por `codigo_icd10` y `rango_etario`.
4. Contar ocurrencias por grupo.
5. Medir solo lectura + procesamiento + agregación.

Rangos etarios:

- `0-9`
- `10-19`
- `20-29`
- `30-39`
- `40-49`
- `50-59`
- `60-69`
- `70-79`
- `80+`

## Estructura

- `generate_dataset.py`: fase de setup. Genera el CSV mock.
- `benchmark_python.py`: benchmark en Python con `csv.DictReader` + `Counter`.
- `benchmark_sqlite.py`: benchmark SQL usando `SQLite` en memoria. El CSV sigue siendo la fuente base; se carga temporalmente para ejecutar SQL.
- `benchmark_java/src/BenchmarkJava.java`: benchmark Java con `BufferedReader` + `HashMap`.
- `benchmark_master.py`: runner maestro que ejecuta setup y benchmark, y luego compara los tres resultados.
- `sql/aggregation_query.sql`: consulta SQL equivalente usada como referencia.

## Diseño del dataset

El generador crea `2.000.000` filas por defecto con:

- `id_ficha`: entero incremental único.
- `edad`: entero entre `0` y `100`.
- `sexo`: `M`, `F`, `X`.
- `codigo_icd10`: uno de 10 diagnósticos ICD-10 frecuentes con pesos probabilísticos.
- `fecha_atencion`: fecha aleatoria válida entre `2019-01-01` y `2025-12-31`.

Supuestos de realismo:

- La edad no es uniforme.
- Hay más registros en edades adultas que en extremos etarios.
- La semilla es fija (`42`) para reproducibilidad.

## Fase 1: Setup

Generar el CSV:

```powershell
python .\generate_dataset.py
```

Opciones útiles:

```powershell
python .\generate_dataset.py --rows 2000000 --seed 42 --output .\fichas_clinicas_mock.csv
```

Compilar Java:

```powershell
javac .\benchmark_java\src\BenchmarkJava.java
```

## Fase 2: Benchmark

Python:

```powershell
python .\benchmark_python.py --csv .\fichas_clinicas_mock.csv
```

Java:

```powershell
java -cp .\benchmark_java\src BenchmarkJava .\fichas_clinicas_mock.csv
```

SQL:

```powershell
python .\benchmark_sqlite.py --csv .\fichas_clinicas_mock.csv
```

Runner maestro:

```powershell
python .\benchmark_master.py
```

Multiples corridas con comparacion agregada:

```powershell
python .\benchmark_master.py --rows 2000000 --repeat 3
```

Si ya existe el CSV y Java ya fue compilado:

```powershell
python .\benchmark_master.py --skip-setup --repeat 3
```

## Criterios de medición

- `Python`: `time.perf_counter()`
- `Java`: `System.nanoTime()`
- `SQL`: `time.perf_counter()` midiendo carga operativa del CSV a staging temporal + consulta SQL

La generación del CSV no se mide, puesto que es necesario como un paso previo al benchmark.

## Salida esperada

Cada implementación entrega:

- tiempo total de ejecución
- total de registros procesados
- total de combinaciones agrupadas
- primeras 10 filas del resultado

Formato:

```text
codigo_icd10 | rango_etario | frecuencia
```

## Comparación técnica esperada

- `Java` debería rendir mejor en CPU y control fino de memoria en este caso batch.
- `Python` debería ser más simple de implementar y mantener, con menor performance bruta.
- `SQL` ofrece la solución declarativa más compacta, pero en este diseño el costo de carga temporal desde CSV forma parte del benchmark, además corre desde Python con SQLite, así que debe tener cierto problema de rendimiento.
