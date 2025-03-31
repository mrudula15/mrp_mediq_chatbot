SELECT 
    py.ownership,
    py.payer_name,
    FORMAT(ROUND(AVG(e.cost_coverage_ratio), 2), 'N2') AS avg_coverage_ratio
FROM encounters e
JOIN payers py ON e.payerid = py.payerid
WHERE e.cost_coverage_ratio IS NOT NULL
GROUP BY py.ownership, py.payer_name
ORDER BY AVG(e.cost_coverage_ratio) DESC;
