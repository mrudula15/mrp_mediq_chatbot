SELECT TOP 5
    c.departmentid,
    COUNT(*) AS uninsured_patient_count
FROM claims c
JOIN payers py ON c.primarypatientinsuranceid = py.payerid
WHERE LOWER(py.ownership) = 'no_insurance'
  AND c.departmentid IS NOT NULL
GROUP BY c.departmentid
ORDER BY uninsured_patient_count DESC;

--not right, patient count mismatch