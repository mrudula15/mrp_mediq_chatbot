SELECT 
    CASE 
        WHEN age < 20 THEN '0-19'
        WHEN age BETWEEN 20 AND 49 THEN '20-49'
        WHEN age BETWEEN 50 AND 69 THEN '50-69'
        ELSE '70+'
    END AS age_group,
    FORMAT(ROUND(AVG(e.out_of_pocket_cost), 0), 'N0') AS avg_out_of_pocket_usd,
    FORMAT(ROUND(AVG(e.cost_coverage_ratio), 2), 'N2') AS avg_coverage_ratio
FROM patients p
JOIN encounters e ON p.patientid = e.patientid
WHERE e.out_of_pocket_cost IS NOT NULL AND e.cost_coverage_ratio IS NOT NULL
GROUP BY 
    CASE 
        WHEN age < 20 THEN '0-19'
        WHEN age BETWEEN 20 AND 49 THEN '20-49'
        WHEN age BETWEEN 50 AND 69 THEN '50-69'
        ELSE '70+'
    END
ORDER BY age_group;
