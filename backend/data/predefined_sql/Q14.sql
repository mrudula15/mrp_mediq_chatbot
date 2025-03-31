SELECT TOP 5
    c.departmentid,
    ROUND(AVG(CAST(e.encounter_duration_minutes AS FLOAT)), 0) AS avg_duration_minutes,
    CONCAT(
        CASE 
            WHEN FLOOR(AVG(CAST(e.encounter_duration_minutes AS FLOAT)) / 1440) > 0 
                THEN CONCAT(FLOOR(AVG(CAST(e.encounter_duration_minutes AS FLOAT)) / 1440), ' day(s) ')
            ELSE ''
        END,
        CASE 
            WHEN FLOOR((CAST(AVG(CAST(e.encounter_duration_minutes AS FLOAT)) AS INT) % 1440) / 60) > 0 
                THEN CONCAT(FLOOR((CAST(AVG(CAST(e.encounter_duration_minutes AS FLOAT)) AS INT) % 1440) / 60), ' hour(s) ')
            ELSE ''
        END,
        CASE 
            WHEN (CAST(AVG(CAST(e.encounter_duration_minutes AS FLOAT)) AS INT) % 60) > 0 
                THEN CONCAT((CAST(AVG(CAST(e.encounter_duration_minutes AS FLOAT)) AS INT) % 60), ' minute(s)')
            ELSE ''
        END
    ) AS readable_duration
FROM claims c
JOIN encounters e ON c.patientid = e.patientid
WHERE e.encounter_duration_minutes IS NOT NULL AND c.departmentid IS NOT NULL
GROUP BY c.departmentid
ORDER BY avg_duration_minutes DESC;
