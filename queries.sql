-- hottest day per city
SELECT city, date, temp_max_c
FROM (
  SELECT city, date, temp_max_c,
         RANK() OVER (PARTITION BY city ORDER BY temp_max_c DESC) AS rnk
  FROM daily_weather
)
WHERE rnk = 1;

-- 7-day rolling average high for Atlanta
SELECT city, date, temp_max_c,
       ROUND(AVG(temp_max_c) OVER (
         PARTITION BY city ORDER BY date
         ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 1) AS rolling_7d_avg
FROM daily_weather
WHERE city = 'Atlanta';

-- top 10 biggest day-to-day temperature swings
SELECT * FROM (
  SELECT city, date,
         temp_max_c - LAG(temp_max_c) OVER (PARTITION BY city ORDER BY date) AS change_c
  FROM daily_weather
)
WHERE change_c IS NOT NULL
ORDER BY ABS(change_c) DESC
LIMIT 10;

-- rainiest months
SELECT city, strftime('%Y-%m', date) AS month, ROUND(SUM(precip_mm), 1) AS total_mm
FROM daily_weather
GROUP BY city, month
ORDER BY total_mm DESC
LIMIT 10;