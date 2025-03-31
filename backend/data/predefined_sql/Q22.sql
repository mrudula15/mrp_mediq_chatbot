SELECT TOP 5
    c.departmentid,
    FORMAT(ROUND(AVG(e.claim_profit_margin), 0), 'N0') AS avg_claim_profit_margin
FROM claims c
JOIN encounters e ON c.patientid = e.patientid
WHERE c.departmentid IS NOT NULL
  AND e.claim_profit_margin IS NOT NULL
GROUP BY c.departmentid
ORDER BY AVG(e.claim_profit_margin) DESC;
