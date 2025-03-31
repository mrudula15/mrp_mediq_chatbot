SELECT *
FROM (
    SELECT 
        race,
        gender,
        COUNT(*) AS patient_count,
        CAST(100.0 * COUNT(*) * 1.0 / (SELECT COUNT(*) FROM patients) AS DECIMAL(5,2)) AS percentage
    FROM patients
    GROUP BY race, gender

    UNION ALL

    SELECT 
        'Total' AS race,
        '' AS gender,
        COUNT(*) AS patient_count,
        100.00 AS percentage
    FROM patients
) AS combined_result
ORDER BY 
    CASE WHEN race = 'Total' THEN 1 ELSE 0 END,
    patient_count DESC;
