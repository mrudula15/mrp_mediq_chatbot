SELECT 
    gender,
    AVG(age) AS average_age
FROM patients
GROUP BY gender
ORDER BY average_age DESC;
