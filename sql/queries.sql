-- Q1: Top Inventors
-- Who has the most patents?
SELECT i.name, COUNT(r.patent_id) as total_patents
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
GROUP BY i.name
ORDER BY total_patents DESC
LIMIT 10;

-- Q2: Top Companies
-- Which companies own the most patents?
SELECT c.name, COUNT(r.patent_id) as total_patents
FROM companies c
JOIN relationships r ON c.company_id = r.company_id
GROUP BY c.name
ORDER BY total_patents DESC
LIMIT 10;

-- Q3: Countries
-- Which countries produce the most patents?
SELECT i.country, COUNT(r.patent_id) as total_patents
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
GROUP BY i.country
ORDER BY total_patents DESC;

-- Q4: Trends Over Time
-- How many patents are created each year?
SELECT year, COUNT(patent_id) as total_patents
FROM patents
GROUP BY year
ORDER BY year ASC;

-- Q5: JOIN Query
-- Combine patents with inventors and companies
SELECT p.patent_id, p.title, i.name as inventor_name, c.name as company_name, p.year
FROM patents p
JOIN relationships r ON p.patent_id = r.patent_id
JOIN inventors i ON r.inventor_id = i.inventor_id
LEFT JOIN companies c ON r.company_id = c.company_id
LIMIT 20;

-- Q6: CTE Query (WITH statement)
-- Break a complex query into steps: Find companies with more than 10 patents, then get their average patents per year
WITH CompanyPatentCounts AS (
    SELECT c.company_id, c.name, COUNT(r.patent_id) as total_patents
    FROM companies c
    JOIN relationships r ON c.company_id = r.company_id
    GROUP BY c.company_id, c.name
)
SELECT name, total_patents 
FROM CompanyPatentCounts 
WHERE total_patents > 10
ORDER BY total_patents DESC;

-- Q7: Ranking Query
-- Rank inventors using window functions based on total patents produced
SELECT name, total_patents,
       RANK() OVER (ORDER BY total_patents DESC) as rank
FROM (
    SELECT i.name, COUNT(r.patent_id) as total_patents
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    GROUP BY i.name
);
