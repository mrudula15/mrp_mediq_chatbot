SELECT TOP 5
    p.zip,
	p.county,
    COUNT(*) AS emergency_visits
FROM encounters e
JOIN patients p ON e.patientid = p.patientid
WHERE LOWER(e.encounterclass) = 'emergency'
  AND p.zip IS NOT NULL
  AND p.zip NOT IN ('0', '00000')
GROUP BY p.zip, p.county
ORDER BY emergency_visits DESC;
