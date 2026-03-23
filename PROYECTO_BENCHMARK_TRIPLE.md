Prompt Maestro Corregido
Proyecto Benchmark Triple: Python vs Java vs SQL con fuente CSV

Actúa como un Senior Performance Engineer / Data Engineer especializado en benchmarking comparativo entre Python, Java y SQL.

Tu tarea es diseñar una solución técnica completa para un benchmark triple cuyo objetivo es comparar rendimiento, eficiencia y enfoque técnico entre Python, Java y SQL resolviendo exactamente el mismo problema de negocio.

Contexto del proyecto

Se debe resolver el siguiente caso:

Desafío: agrupar 2.000.000 de fichas clínicas anonimizadas para contar la frecuencia de diagnósticos ICD-10 por rango etario.

El benchmark tiene 2 fases:

Fase 1: Setup / Generación de datos

Se deben generar los datos programáticamente.

Fase 2: Benchmark / Test

Se mide exclusivamente el tiempo de lectura, procesamiento y agregación.

Restricción crítica e innegociable

La fuente de datos debe ser exclusivamente un archivo CSV.

Reglas obligatorias

No existe una base de datos real previa.

El dataset debe generarse en un archivo:
fichas_clinicas_mock.csv

La persistencia base del caso debe ser solo CSV.

No diseñes la solución como si el origen fuera una base productiva existente.

Para la versión SQL, se permite usar SQL únicamente como motor de procesamiento del benchmark, leyendo el CSV o cargándolo temporalmente para ejecutar la consulta, pero el origen del benchmark sigue siendo el CSV.

Prohibiciones

No cambiar el problema a otro formato base.

No reemplazar el CSV como fuente principal del benchmark.

No proponer MongoDB, PostgreSQL, MySQL u otros motores como almacenamiento principal del caso.

Objetivo del benchmark

Comparar Python vs Java vs SQL en el mismo problema, evaluando:

tiempo de ejecución

eficiencia técnica

uso del paradigma de cada herramienta

ventajas y desventajas para procesamiento masivo

Dataset a generar

Debes indicar cómo generar programáticamente un archivo CSV con estas características:

Archivo

fichas_clinicas_mock.csv

Volumen

2.000.000 de filas

Columnas

id_ficha: entero incremental único

edad: entero entre 0 y 100

sexo: valores posibles M, F, X

codigo_icd10: diagnóstico ICD-10

fecha_atencion: fecha válida aleatoria

Realismo de los datos

El dataset debe simular un escenario médico razonable.

Códigos ICD-10

Usar al menos 10 códigos comunes, por ejemplo:

J00

I10

E11

K21

M54

N39

F32

J45

A09

B34

Distribución

aplicar pesos probabilísticos a los diagnósticos

la edad no debe distribuirse uniformemente

debe haber más registros en edades adultas que en extremos etarios

usar semilla fija para reproducibilidad

Lógica exacta del problema

Cada tecnología debe resolver exactamente esta misma lógica:

Leer el CSV generado.

Calcular el rango_etario según los siguientes cortes:

0-9

10-19

20-29

30-39

40-49

50-59

60-69

70-79

80+

Agrupar por:

codigo_icd10

rango_etario

Contar la frecuencia de ocurrencias por grupo.

Implementaciones requeridas

Debes proponer y/o generar tres versiones equivalentes del benchmark:

1. Python

Usar Python para:

leer el CSV

transformar la edad en rango etario

agrupar y contar ocurrencias

medir tiempo de benchmark

Preferir enfoque eficiente y claro, por ejemplo:

csv.DictReader + collections.Counter
o

una implementación optimizada equivalente

2. Java

Usar Java para:

leer el CSV

transformar la edad en rango etario

agrupar y contar ocurrencias

medir tiempo de benchmark

Preferir bibliotecas estándar o ampliamente aceptadas, por ejemplo:

BufferedReader

HashMap

clases bien estructuradas

enfoque orientado a performance

3. SQL

Usar SQL como motor de procesamiento para resolver la misma lógica.

Importante:

el origen sigue siendo el CSV

debes explicar claramente cómo SQL leerá o cargará temporalmente el CSV para ejecutar la agregación

la solución SQL debe enfocarse en la consulta de agrupación por diagnóstico y rango etario

Puede usarse, por ejemplo:

carga temporal desde CSV a tabla staging o temporal

luego GROUP BY

CASE WHEN para construir rango_etario

Pero debe quedar explícito que:

el CSV es la fuente base

no hay base de datos previa como insumo original

Separación estricta de fases

Debes dejar muy claro qué parte corresponde a cada fase:

Setup

Incluye únicamente:

generación del CSV

preparación mínima necesaria para que cada tecnología pueda ejecutar el benchmark

Benchmark

Incluye únicamente:

inicio del cronómetro

lectura del CSV o carga operativa necesaria para procesarlo

transformación

agrupación

conteo final

detención del cronómetro

Regla crítica

El tiempo de generación del CSV no se mide.

Medición

Debe indicarse que el benchmark use medición precisa.

Python

time.perf_counter()

Java

System.nanoTime()

SQL

método equivalente de medición del motor SQL usado, dejando explícito el tiempo de ejecución de la carga operativa + consulta, si corresponde al diseño del benchmark

Salida esperada

Cada implementación debe entregar:

tiempo total de ejecución

total de registros procesados

total de combinaciones agrupadas

muestra de las primeras 10 filas del resultado

Formato esperado de salida:

codigo_icd10 | rango_etario | frecuencia

Criterios de comparación técnica

La respuesta debe comparar las tres tecnologías considerando:

velocidad

consumo de memoria

facilidad de implementación

escalabilidad

mantenibilidad

qué tecnología conviene más para este caso y por qué

Estructura esperada de la respuesta

La respuesta debe incluir:

Breve explicación técnica del benchmark

Diseño del dataset mock en CSV

Estrategia de implementación en Python

Estrategia de implementación en Java

Estrategia de implementación en SQL

Criterios de medición

Comparación esperada entre Python, Java y SQL

Conclusión técnica final

Restricción final

No cambies el objetivo del ejercicio.

El benchmark debe comparar obligatoriamente:

Python

Java

SQL

Y el origen de datos debe ser obligatoriamente:

CSV