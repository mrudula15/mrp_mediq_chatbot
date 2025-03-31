SELECT TOP 5
    p.county,
    COUNT(*) AS uninsured_patient_count
FROM encounters e
JOIN patients p ON e.patientid = p.patientid
JOIN payers py ON e.payerid = py.payerid
WHERE LOWER(py.ownership) = 'NO_INSURANCE'
  AND p.county IS NOT NULL
GROUP BY p.county
ORDER BY uninsured_patient_count DESC;
