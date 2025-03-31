SELECT TOP 5
    p.county,
    COUNT(*) AS obese_case_count
FROM conditions c
JOIN patients p ON c.patientid = p.patientid
WHERE LOWER(c.description) LIKE '%obes%' --includes obese and obesity
GROUP BY p.county
ORDER BY obese_case_count DESC;
