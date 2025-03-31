SELECT 
    race,
    AVG(age) AS average_age
FROM patients
GROUP BY race
ORDER BY average_age DESC;
