SELECT TOP 5
    p.county,
    COUNT(*) AS sepsis_case_count
FROM conditions c
JOIN patients p ON c.patientid = p.patientid
WHERE LOWER(c.description) LIKE '%sepsis%'
GROUP BY p.county
ORDER BY sepsis_case_count DESC;
