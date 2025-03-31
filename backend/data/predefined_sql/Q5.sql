SELECT 
    race,
    FORMAT(ROUND(AVG(healthcare_expenses), 0), 'N0') AS avg_expenses_usd,
    FORMAT(ROUND(AVG(healthcare_coverage), 0), 'N0') AS avg_coverage_usd,
    FORMAT(ROUND(AVG(income), 0), 'N0') AS avg_income_usd
FROM patients
GROUP BY race
ORDER BY AVG(healthcare_expenses) DESC;

