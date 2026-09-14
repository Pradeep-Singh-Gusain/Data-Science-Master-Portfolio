-- ==============================================================================
-- PROJECT: Zomato Bangalore Full-Stack Market Intelligence & SQL Analytics
-- AUTHOR: Pradeep Singh
-- DATABASE: PostgreSQL (`zomato_db`)
-- DESCRIPTION: 20 Industry-Standard Business Queries across 4 Core Phases
-- ==============================================================================


--------------------------------------------------------------------------------
-- PHASE 1: DATA CLEANING, AUDIT & INITIAL DATA EXPLORATION (Queries 1 - 5)
--------------------------------------------------------------------------------

-- Query 1: Total volume audit of the restaurant corpus
SELECT COUNT(*) AS total_raw_records 
FROM zomato_restaurants;

-- Query 2: Identify missing or unrated outlets (Null and 'NEW' status checks)
SELECT 
    COUNT(*) AS unrated_or_new_outlets
FROM zomato_restaurants
WHERE rate IS NULL OR rate LIKE '%NEW%' OR rate LIKE '%-%';

-- Query 3: Distribution of online delivery capabilities across the marketplace
SELECT 
    online_order, 
    COUNT(*) AS outlet_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM zomato_restaurants), 2) AS percentage_share
FROM zomato_restaurants
GROUP BY online_order;

-- Query 4: Distribution of table booking capabilities
SELECT 
    book_table, 
    COUNT(*) AS outlet_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM zomato_restaurants), 2) AS percentage_share
FROM zomato_restaurants
GROUP BY book_table;

-- Query 5: Unique locality spread and their raw outlet frequencies
SELECT 
    location, 
    COUNT(*) AS total_outlets
FROM zomato_restaurants
WHERE location IS NOT NULL
GROUP BY location
ORDER BY total_outlets DESC;


--------------------------------------------------------------------------------
-- PHASE 2: CORE BUSINESS METRICS & PRICING TIER ANALYSIS (Queries 6 - 10)
--------------------------------------------------------------------------------

-- Query 6: Average cost for two people across different restaurant types
SELECT 
    rest_type, 
    COUNT(*) AS outlet_count,
    ROUND(AVG(CAST(REPLACE(approx_cost_for_two, ',', '') AS DECIMAL(10,2))), 2) AS avg_cost_for_two
FROM zomato_restaurants
WHERE approx_cost_for_two IS NOT NULL
GROUP BY rest_type
HAVING COUNT(*) > 50
ORDER BY avg_cost_for_two DESC;

-- Query 7: Identifying premium vs budget pricing tiers
SELECT 
    CASE 
        WHEN CAST(REPLACE(approx_cost_for_two, ',', '') AS DECIMAL(10,2)) < 400 THEN 'Budget Tier (< 400)'
        WHEN CAST(REPLACE(approx_cost_for_two, ',', '') AS DECIMAL(10,2)) BETWEEN 400 AND 800 THEN 'Mid Tier (400-800)'
        ELSE 'Premium Tier (> 800)'
    END AS pricing_tier,
    COUNT(*) AS total_outlets,
    ROUND(AVG(CAST(REPLACE(rate, '/5', '') AS DECIMAL(3,2))), 2) AS avg_segment_rating
FROM zomato_restaurants
WHERE approx_cost_for_two IS NOT NULL 
  AND rate IS NOT NULL 
  AND rate NOT LIKE '%NEW%' 
  AND rate NOT LIKE '%-%'
GROUP BY pricing_tier
ORDER BY avg_segment_rating DESC;

-- Query 8: Average cost comparison between online delivery enabled vs disabled outlets
SELECT 
    online_order,
    ROUND(AVG(CAST(REPLACE(approx_cost_for_two, ',', '') AS DECIMAL(10,2))), 2) AS avg_meal_cost
FROM zomato_restaurants
WHERE approx_cost_for_two IS NOT NULL
GROUP BY online_order;

-- Query 9: Most expensive dining localities in Bangalore
SELECT 
    location, 
    ROUND(AVG(CAST(REPLACE(approx_cost_for_two, ',', '') AS DECIMAL(10,2))), 2) AS avg_cost
FROM zomato_restaurants
WHERE approx_cost_for_two IS NOT NULL
GROUP BY location
ORDER BY avg_cost DESC
LIMIT 10;

-- Query 10: Cost evaluation across different service types
SELECT 
    listed_in_type AS service_category,
    COUNT(*) AS total_listings,
    ROUND(AVG(CAST(REPLACE(approx_cost_for_two, ',', '') AS DECIMAL(10,2))), 2) AS avg_cost
FROM zomato_restaurants
WHERE approx_cost_for_two IS NOT NULL
GROUP BY listed_in_type
ORDER BY avg_cost DESC;


--------------------------------------------------------------------------------
-- PHASE 3: CUSTOMER ENGAGEMENT & PERFORMANCE BENCHMARKING (Queries 11 - 15)
--------------------------------------------------------------------------------

-- Query 11: Top 10 most voted restaurants across Bangalore
SELECT 
    name, 
    location, 
    votes, 
    rate,
    approx_cost_for_two
FROM zomato_restaurants
WHERE votes IS NOT NULL AND rate NOT LIKE '%NEW%'
ORDER BY votes DESC
LIMIT 10;

-- Query 12: High-rated market leaders (Rating >= 4.5 with votes > 500)
SELECT 
    name, 
    location, 
    rate, 
    votes, 
    cuisines
FROM zomato_restaurants
WHERE rate NOT LIKE '%NEW%' AND rate IS NOT NULL
  AND CAST(SUBSTRING(rate, 1, 3) AS DECIMAL(3,2)) >= 4.5
  AND votes > 500
ORDER BY votes DESC;

-- Query 13: Localities with the highest total customer engagement (Votes)
SELECT 
    location, 
    SUM(votes) AS total_locality_votes,
    COUNT(name) AS total_restaurants
FROM zomato_restaurants
WHERE votes IS NOT NULL
GROUP BY location
ORDER BY total_locality_votes DESC
LIMIT 10;

-- Query 14: Top performing cuisines based on average consumer rating
SELECT 
    cuisines, 
    COUNT(*) AS restaurant_count,
    ROUND(AVG(CAST(SUBSTRING(rate, 1, 3) AS DECIMAL(3,2))), 2) AS avg_cuisine_rating
FROM zomato_restaurants
WHERE rate IS NOT NULL 
  AND rate NOT LIKE '%NEW%' 
  AND rate NOT LIKE '%-%' 
  AND cuisines IS NOT NULL
GROUP BY cuisines
HAVING COUNT(*) > 30
ORDER BY avg_cuisine_rating DESC
LIMIT 10;

-- Query 15: Impact of Table Booking on Average Ratings
SELECT 
    book_table,
    ROUND(AVG(CAST(SUBSTRING(rate, 1, 3) AS DECIMAL(3,2))), 2) AS avg_rating,
    SUM(votes) AS total_votes_received
FROM zomato_restaurants
WHERE rate IS NOT NULL 
  AND rate NOT LIKE '%NEW%' 
  AND rate NOT LIKE '%-%' 
  AND votes IS NOT NULL
GROUP BY book_table;


--------------------------------------------------------------------------------
-- PHASE 4: ADVANCED BUSINESS ANALYTICS & CHURN RISK (Queries 16 - 20)
--------------------------------------------------------------------------------

-- Query 16: Operational Churn Risk (Outlets with low ratings < 3.5)
WITH ParsedRatings AS (
    SELECT 
        name, 
        location, 
        CAST(SUBSTRING(rate, 1, 3) AS DECIMAL(3,2)) AS clean_rating,
        cuisines
    FROM zomato_restaurants
    WHERE rate IS NOT NULL 
      AND rate NOT LIKE '%NEW%' 
      AND rate NOT LIKE '%-%'
)
SELECT 
    name, 
    location, 
    clean_rating, 
    cuisines
FROM ParsedRatings
WHERE clean_rating < 3.5
ORDER BY clean_rating ASC
LIMIT 15;

-- Query 17: Window Function - Ranking top restaurants by votes within each locality
WITH RankedLocalities AS (
    SELECT 
        name,
        location,
        votes AS total_votes,
        rate,
        ROW_NUMBER() OVER (PARTITION BY location ORDER BY votes DESC) AS vote_rank
    FROM zomato_restaurants
    WHERE votes IS NOT NULL 
      AND location IS NOT NULL
      AND rate IS NOT NULL 
      AND rate NOT LIKE '%NEW%' 
      AND rate NOT LIKE '%-%'
)
SELECT * 
FROM RankedLocalities
WHERE vote_rank <= 3;

-- Query 18: Window Function - Running total of votes across Bangalore localities
SELECT 
    location,
    SUM(votes) AS locality_votes,
    SUM(SUM(votes)) OVER (ORDER BY SUM(votes) DESC) AS running_total_votes
FROM zomato_restaurants
WHERE votes IS NOT NULL AND location IS NOT NULL
GROUP BY location;

-- Query 19: Identifying multi-chain dominance (Brands with > 5 outlets)
SELECT 
    name AS brand_name,
    COUNT(*) AS total_outlets,
    ROUND(AVG(CAST(SUBSTRING(rate, 1, 3) AS DECIMAL(3,2))), 2) AS avg_brand_rating,
    SUM(votes) AS cumulative_brand_votes
FROM zomato_restaurants
WHERE rate IS NOT NULL 
  AND rate NOT LIKE '%NEW%' 
  AND rate NOT LIKE '%-%' 
  AND votes IS NOT NULL
GROUP BY name
HAVING COUNT(*) > 5
ORDER BY total_outlets DESC
LIMIT 10;

-- Query 20: Comprehensive Executive Summary View combining service, cost, and rating
SELECT 
    listed_in_type AS service_type,
    online_order,
    book_table,
    COUNT(*) AS total_outlets,
    ROUND(AVG(CAST(REPLACE(approx_cost_for_two, ',', '') AS DECIMAL(10,2))), 2) AS average_cost,
    ROUND(AVG(CAST(SUBSTRING(rate, 1, 3) AS DECIMAL(3,2))), 2) AS average_rating
FROM zomato_restaurants
WHERE rate IS NOT NULL 
  AND rate NOT LIKE '%NEW%' 
  AND rate NOT LIKE '%-%' 
  AND approx_cost_for_two IS NOT NULL 
  AND approx_cost_for_two NOT LIKE '%-%'
GROUP BY listed_in_type, online_order, book_table
ORDER BY average_rating DESC;