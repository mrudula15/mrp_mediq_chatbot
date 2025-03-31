SELECT TOP 5
    p.county,
    COUNT(*) AS chronic_case_count
FROM conditions c
JOIN patients p ON c.patientid = p.patientid
WHERE c.condition_duration_days >= 365	--CDC reference time period.
GROUP BY p.county
ORDER BY chronic_case_count DESC;
