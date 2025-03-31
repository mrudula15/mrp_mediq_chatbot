SELECT 
    city,
    COUNT(*) AS patient_count
FROM patients
GROUP BY city
ORDER BY patient_count DESC
OFFSET 0 ROWS FETCH NEXT 5 ROWS ONLY;
