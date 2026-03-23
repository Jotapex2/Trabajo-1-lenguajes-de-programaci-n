import java.io.BufferedReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

//Carga las clases y ordena.

public class BenchmarkJava {
    private record GroupKey(String codigoIcd10, String rangoEtario) {}
    private record GroupRow(String codigoIcd10, String rangoEtario, int frecuencia) {}

    private static String ageRange(int age) {
        if (age < 10) return "0-9";
        if (age < 20) return "10-19";
        if (age < 30) return "20-29";
        if (age < 40) return "30-39";
        if (age < 50) return "40-49";
        if (age < 60) return "50-59";
        if (age < 70) return "60-69";
        if (age < 80) return "70-79";
        return "80+";
    }

    //Ejecuta el benchmark
    public static void main(String[] args) throws IOException {
        Path csvPath = args.length > 0 ? Paths.get(args[0]) : Paths.get("fichas_clinicas_mock.csv");
        runBenchmark(csvPath);
    }

    private static void runBenchmark(Path csvPath) throws IOException {
        Map<GroupKey, Integer> counts = new HashMap<>();
        int processedRows = 0;

        long start = System.nanoTime();
        try (BufferedReader reader = Files.newBufferedReader(csvPath)) {
            String line = reader.readLine();
            if (line == null) {
                throw new IllegalStateException("El CSV no tiene cabecera.");
            }

            while ((line = reader.readLine()) != null) {
                String[] parts = line.split(",", -1);
                int age = Integer.parseInt(parts[1]);
                String codigoIcd10 = parts[3];
                GroupKey key = new GroupKey(codigoIcd10, ageRange(age));
                counts.merge(key, 1, Integer::sum);
                processedRows++;
            }
        }
        long elapsedNanos = System.nanoTime() - start;

        List<GroupRow> groupedRows = new ArrayList<>();
        for (Map.Entry<GroupKey, Integer> entry : counts.entrySet()) {
            groupedRows.add(
                new GroupRow(entry.getKey().codigoIcd10(), entry.getKey().rangoEtario(), entry.getValue())
            );
        }
        groupedRows.sort(
            Comparator.comparing(GroupRow::codigoIcd10).thenComparing(GroupRow::rangoEtario)
        );

        System.out.println("Benchmark: Java");
        System.out.printf(
            Locale.US,
            "Tiempo total de ejecucion: %.6f segundos%n",
            elapsedNanos / 1_000_000_000.0
        );
        System.out.println("Total de registros procesados: " + processedRows);
        System.out.println("Total de combinaciones agrupadas: " + groupedRows.size());
        System.out.println("Primeras 10 filas:");
        System.out.println("codigo_icd10 | rango_etario | frecuencia");

        int limit = Math.min(10, groupedRows.size());
        for (int i = 0; i < limit; i++) {
            GroupRow row = groupedRows.get(i);
            System.out.printf("%s | %s | %d%n", row.codigoIcd10(), row.rangoEtario(), row.frecuencia());
        }
    }
}
