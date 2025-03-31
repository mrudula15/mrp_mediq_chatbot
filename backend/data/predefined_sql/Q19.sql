SELECT TOP 5
    p.county,
    FORMAT(ROUND(AVG(e.claim_profit_margin), 0), 'N0') AS avg_claim_profit_margin
FROM encounters e
JOIN patients p ON e.patientid = p.patientid
WHERE e.claim_profit_margin IS NOT NULL
  AND p.county IS NOT NULL
GROUP BY p.county
ORDER BY AVG(e.claim_profit_margin) ASC;
