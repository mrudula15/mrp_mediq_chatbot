SELECT 
    py.ownership,
    FORMAT(ROUND(AVG(e.encounter_duration_minutes), 0), 'N0') AS avg_duration_minutes,
    FORMAT(ROUND(AVG(e.out_of_pocket_cost), 0), 'N0') AS avg_out_of_pocket_usd
FROM encounters e
JOIN payers py ON e.payerid = py.payerid
WHERE e.encounter_duration_minutes IS NOT NULL
  AND e.out_of_pocket_cost IS NOT NULL
GROUP BY py.ownership
ORDER BY avg_out_of_pocket_usd DESC;
