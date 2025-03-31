SELECT 
    encounterclass,
    COUNT(*) AS encounter_count,
    FORMAT(100.0 * COUNT(*) * 1.0 / (SELECT COUNT(*) FROM encounters), 'N2') AS percentage
FROM encounters
GROUP BY encounterclass
ORDER BY COUNT(*) DESC;
