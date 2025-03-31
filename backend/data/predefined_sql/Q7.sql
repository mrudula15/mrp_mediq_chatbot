SELECT TOP 5
    p.county,
    COUNT(*) AS stress_case_count
FROM conditions c
JOIN patients p ON c.patientid = p.patientid
WHERE LOWER(c.description) LIKE '%stress%' --Includes stress and post-traumatic stress
GROUP BY p.county
ORDER BY stress_case_count DESC;
