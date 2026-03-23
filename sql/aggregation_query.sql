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
ORDER BY codigo_icd10, rango_etario;
