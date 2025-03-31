SELECT 
    encounterclass,
    FORMAT(ROUND(AVG(claim_profit_margin), 2), 'N2') AS avg_claim_profit_margin
FROM encounters
WHERE claim_profit_margin IS NOT NULL
GROUP BY encounterclass
ORDER BY AVG(claim_profit_margin) DESC;  -- sort by actual number
