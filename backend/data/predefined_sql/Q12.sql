SELECT 
    encounterclass,
    ROUND(AVG(encounter_duration_minutes), 0) AS avg_duration_minutes,
    CONCAT(
        CASE 
            WHEN FLOOR(AVG(encounter_duration_minutes) / 1440) > 0 
                THEN CONCAT(FLOOR(AVG(encounter_duration_minutes) / 1440), ' day(s) ')
            ELSE ''
        END,
        CASE 
            WHEN FLOOR((AVG(encounter_duration_minutes) % 1440) / 60) > 0 
                THEN CONCAT(FLOOR((AVG(encounter_duration_minutes) % 1440) / 60), ' hour(s) ')
            ELSE ''
        END,
        CASE 
            WHEN ROUND(AVG(encounter_duration_minutes) % 60, 0) > 0 
                THEN CONCAT(ROUND(AVG(encounter_duration_minutes) % 60, 0), ' minute(s)')
            ELSE ''
        END
    ) AS readable_duration
FROM encounters
WHERE encounter_duration_minutes IS NOT NULL
GROUP BY encounterclass
ORDER BY avg_duration_minutes DESC;
