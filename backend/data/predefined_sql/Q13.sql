SELECT TOP 5
    pr.name AS provider_name,
    ROUND(AVG(e.encounter_duration_minutes), 0) AS avg_duration_minutes,
    CONCAT(
        CASE 
            WHEN FLOOR(AVG(e.encounter_duration_minutes) / 1440) > 0 
                THEN CONCAT(FLOOR(AVG(e.encounter_duration_minutes) / 1440), ' day(s) ')
            ELSE ''
        END,
        CASE 
            WHEN FLOOR((AVG(e.encounter_duration_minutes) % 1440) / 60) > 0 
                THEN CONCAT(FLOOR((AVG(e.encounter_duration_minutes) % 1440) / 60), ' hour(s) ')
            ELSE ''
        END,
        CASE 
            WHEN ROUND(AVG(e.encounter_duration_minutes) % 60, 0) > 0 
                THEN CONCAT(ROUND(AVG(e.encounter_duration_minutes) % 60, 0), ' minute(s)')
            ELSE ''
        END
    ) AS readable_duration
FROM encounters e
JOIN providers pr ON e.providerid = pr.providerid
WHERE e.encounter_duration_minutes IS NOT NULL
GROUP BY pr.name
ORDER BY avg_duration_minutes DESC;
