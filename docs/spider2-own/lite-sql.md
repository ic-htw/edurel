# bq

## bq001.sql

```sql
DECLARE start_date STRING DEFAULT '20170201';
DECLARE end_date STRING DEFAULT '20170228';

WITH visit AS (
    SELECT
        fullvisitorid,
        MIN(date) AS date_first_visit
    FROM
        `bigquery-public-data.google_analytics_sample.ga_sessions_*`
    WHERE
       _TABLE_SUFFIX BETWEEN start_date AND end_date
    GROUP BY fullvisitorid
),

transactions AS (
    SELECT
        fullvisitorid,
        MIN(date) AS date_transactions
    FROM
        `bigquery-public-data.google_analytics_sample.ga_sessions_*` AS ga,
        UNNEST(ga.hits) AS hits
    WHERE
        hits.transaction.transactionId IS NOT NULL
        AND
        _TABLE_SUFFIX BETWEEN start_date AND end_date
    GROUP BY fullvisitorid
),

device_transactions AS (
    SELECT DISTINCT
        fullvisitorid,
        date,
        device.deviceCategory
    FROM
        `bigquery-public-data.google_analytics_sample.ga_sessions_*` AS ga,
        UNNEST(ga.hits) AS hits
    WHERE
        hits.transaction.transactionId IS NOT NULL
        AND
        _TABLE_SUFFIX BETWEEN start_date AND end_date
),

visits_transactions AS (
    SELECT
        visit.fullvisitorid,
        date_first_visit,
        date_transactions,
        device_transactions.deviceCategory AS device_transaction
    FROM
        visit
        JOIN transactions
        ON visit.fullvisitorid = transactions.fullvisitorid
        JOIN device_transactions
        ON visit.fullvisitorid = device_transactions.fullvisitorid 
        AND transactions.date_transactions = device_transactions.date
)

SELECT
       fullvisitorid,
       DATE_DIFF(PARSE_DATE('%Y%m%d', date_transactions), PARSE_DATE('%Y%m%d', date_first_visit), DAY) AS time,
       device_transaction
FROM visits_transactions
ORDER BY fullvisitorid;

```

## bq002.sql

```sql
DECLARE start_date STRING DEFAULT '20170101';
DECLARE end_date STRING DEFAULT '20170630';

WITH daily_revenue AS (
    SELECT
        trafficSource.source AS source,
        date,
        SUM(productRevenue) / 1000000 AS revenue
    FROM
        `bigquery-public-data.google_analytics_sample.ga_sessions_*`,
        UNNEST (hits) AS hits,
        UNNEST (hits.product) AS product
    WHERE
        _table_suffix BETWEEN start_date AND end_date
    GROUP BY
        source, date
),
weekly_revenue AS (
    SELECT
        source,
        CONCAT(EXTRACT(YEAR FROM (PARSE_DATE('%Y%m%d', date))), 'W', EXTRACT(WEEK FROM (PARSE_DATE('%Y%m%d', date)))) AS week,
        SUM(revenue) AS revenue
    FROM daily_revenue
    GROUP BY source, week
),
monthly_revenue AS (
    SELECT
        source,
        CONCAT(EXTRACT(YEAR FROM (PARSE_DATE('%Y%m%d', date))),'0', EXTRACT(MONTH FROM (PARSE_DATE('%Y%m%d', date)))) AS month,
        SUM(revenue) AS revenue
    FROM daily_revenue
    GROUP BY source, month
),

top_source AS (
    SELECT source, SUM(revenue) AS total_revenue
    FROM daily_revenue
    GROUP BY source
    ORDER BY total_revenue DESC
    LIMIT 1
),

max_revenues AS (
    (
      SELECT
        'Daily' AS time_type,
        date AS time,
        source,
        MAX(revenue) AS max_revenue
      FROM daily_revenue
      WHERE source = (SELECT source FROM top_source)
      GROUP BY source, date
      ORDER BY max_revenue DESC
      LIMIT 1
    )

    UNION ALL

    (
      SELECT
        'Weekly' AS time_type,
        week AS time,
        source,
        MAX(revenue) AS max_revenue
      FROM weekly_revenue
      WHERE source = (SELECT source FROM top_source)
      GROUP BY source, week
      ORDER BY max_revenue DESC
      LIMIT 1
    )

    UNION ALL

    (
      SELECT
          'Monthly' AS time_type,
          month AS time,
          source,
          MAX(revenue) AS max_revenue
      FROM monthly_revenue
      WHERE source = (SELECT source FROM top_source)
      GROUP BY source, month
      ORDER BY max_revenue DESC
      LIMIT 1
    )
)

SELECT
    max_revenue
FROM max_revenues
ORDER BY max_revenue DESC;

```

## bq003.sql

```sql
WITH cte1 AS (
    SELECT
        CONCAT(EXTRACT(YEAR FROM (PARSE_DATE('%Y%m%d', date))), '0',
            EXTRACT(MONTH FROM (PARSE_DATE('%Y%m%d', date)))) AS month,
        SUM(totals.pageviews) / COUNT(DISTINCT fullVisitorId) AS avg_pageviews_non_purchase
    FROM
        `bigquery-public-data.google_analytics_sample.ga_sessions_2017*`,
        UNNEST (hits) AS hits,
        UNNEST (hits.product) AS product
    WHERE
        _table_suffix BETWEEN '0401' AND '0731'
        AND totals.transactions IS NULL
        AND product.productRevenue IS NULL
    GROUP BY month
),
cte2 AS (
    SELECT
        CONCAT(EXTRACT(YEAR FROM (PARSE_DATE('%Y%m%d', date))), '0',
            EXTRACT(MONTH FROM (PARSE_DATE('%Y%m%d', date)))) AS month,
        SUM(totals.pageviews) / COUNT(DISTINCT fullVisitorId) AS avg_pageviews_purchase
    FROM
        `bigquery-public-data.google_analytics_sample.ga_sessions_2017*`,
        UNNEST (hits) AS hits,
        UNNEST (hits.product) AS product
    WHERE
        _table_suffix BETWEEN '0401' AND '0731'
        AND totals.transactions >= 1
        AND product.productRevenue IS NOT NULL
    GROUP BY month
)
SELECT
    month, avg_pageviews_purchase, avg_pageviews_non_purchase
FROM cte1 INNER JOIN cte2
USING(month)
ORDER BY month;

```

## bq004.sql

```sql
with product_and_quatity AS (
    SELECT 
        DISTINCT v2ProductName AS other_purchased_products,
        SUM(productQuantity) AS quatity
    FROM
        `bigquery-public-data.google_analytics_sample.ga_sessions_2017*`,
        UNNEST(hits) AS hits,
        UNNEST(hits.product) AS product
    WHERE
        _table_suffix BETWEEN '0701' AND '0731'
        AND NOT REGEXP_CONTAINS(LOWER(v2ProductName), 'youtube')
        AND fullVisitorID IN (
            SELECT 
            DISTINCT fullVisitorId
            FROM
                `bigquery-public-data.google_analytics_sample.ga_sessions_2017*`,
                UNNEST(hits) AS hits,
                UNNEST(hits.product) AS product
            WHERE
                _table_suffix BETWEEN '0701' AND '0731'
                AND REGEXP_CONTAINS(LOWER(v2ProductName), 'youtube')
        )
    GROUP BY v2ProductName
)
SELECT other_purchased_products
FROM product_and_quatity
ORDER BY quatity DESC
LIMIT 1;

```

## bq006.sql

```sql
WITH incident_stats AS (
  SELECT 
    COUNT(descript) AS total_pub_intox
  FROM 
    `bigquery-public-data.austin_incidents.incidents_2016` 
  WHERE 
    descript = 'PUBLIC INTOXICATION' 
  GROUP BY 
    date
),
average_and_stddev AS (
  SELECT 
    AVG(total_pub_intox) AS avg, 
    STDDEV(total_pub_intox) AS stddev 
  FROM 
    incident_stats
),
daily_z_scores AS (
  SELECT 
    date, 
    COUNT(descript) AS total_pub_intox, 
    ROUND((COUNT(descript) - a.avg) / a.stddev, 2) AS z_score
  FROM 
    `bigquery-public-data.austin_incidents.incidents_2016`,
    (SELECT avg, stddev FROM average_and_stddev) AS a
  WHERE 
    descript = 'PUBLIC INTOXICATION'
  GROUP BY 
    date, avg, stddev
)

SELECT 
  date
FROM 
  daily_z_scores
ORDER BY 
  z_score DESC
LIMIT 1
OFFSET 1
```

## bq008.sql

```sql
with page_visit_sequence AS (
    SELECT
        fullVisitorID,
        visitID,
        pagePath,
        LEAD(timestamp, 1) OVER (PARTITION BY fullVisitorId, visitID order by timestamp) - timestamp AS page_duration,
        LEAD(pagePath, 1) OVER (PARTITION BY fullVisitorId, visitID order by timestamp) AS next_page,
        RANK() OVER (PARTITION BY fullVisitorId, visitID order by timestamp) AS step_number
    FROM (
        SELECT
            pages.fullVisitorID,
            pages.visitID,
            pages.pagePath,
            visitors.campaign,
            MIN(pages.timestamp) timestamp
        FROM (
            SELECT
                fullVisitorId,
                visitId,
                trafficSource.campaign campaign
            FROM
                `bigquery-public-data.google_analytics_sample.ga_sessions_*`,
                UNNEST(hits) as hits
            WHERE
                _TABLE_SUFFIX BETWEEN '20170101' AND '20170131'
                AND hits.type='PAGE'
                AND REGEXP_CONTAINS(hits.page.pagePath, r'^/home')
                AND REGEXP_CONTAINS(trafficSource.campaign, r'Data Share')
        ) AS visitors
        JOIN(
            SELECT
                fullVisitorId,
                visitId,
                visitStartTime + hits.time / 1000 AS timestamp,
                hits.page.pagePath AS pagePath
            FROM
                `bigquery-public-data.google_analytics_sample.ga_sessions_*`,
                UNNEST(hits) as hits
            WHERE
                _TABLE_SUFFIX BETWEEN '20170101' AND '20170131'
        ) as pages
        ON
            visitors.fullVisitorID = pages.fullVisitorID
            AND visitors.visitID = pages.visitID
        GROUP BY 
            pages.fullVisitorID, visitors.campaign, pages.visitID, pages.pagePath
        ORDER BY 
            pages.fullVisitorID, pages.visitID, timestamp
    )
    ORDER BY fullVisitorId, visitID, step_number
),
most_common_next_page AS (
    SELECT
        next_page,
        COUNT(next_page) as page_count
    FROM page_visit_sequence
    WHERE
        next_page IS NOT NULL
        AND REGEXP_CONTAINS(pagePath, r'^/home')
    GROUP BY next_page
    ORDER BY page_count DESC
    LIMIT 1
),
max_page_duration AS (
    SELECT MAX(page_duration) as max_duration
    FROM page_visit_sequence
    WHERE
        page_duration IS NOT NULL
        AND REGEXP_CONTAINS(pagePath, r'^/home')
)
SELECT
    next_page,
    max_duration
FROM
    most_common_next_page,
    max_page_duration;

```

## bq009.sql

```sql
WITH MONTHLY_REVENUE AS (
    SELECT 
        FORMAT_DATE("%Y%m", PARSE_DATE("%Y%m%d", date)) AS month,
        trafficSource.source AS source,
        ROUND(SUM(totals.totalTransactionRevenue) / 1000000, 2) AS revenue
    FROM `bigquery-public-data.google_analytics_sample.ga_sessions_2017*`
    GROUP BY 1, 2
),

YEARLY_REVENUE AS (
    SELECT
        source,
        SUM(revenue) AS total_revenue
    FROM MONTHLY_REVENUE
    GROUP BY source
),

TOP_SOURCE AS (
    SELECT 
        source
    FROM YEARLY_REVENUE
    ORDER BY total_revenue DESC
    LIMIT 1
),

SOURCE_MONTHLY_REVENUE AS (
    SELECT
        month,
        source,
        revenue
    FROM MONTHLY_REVENUE
    WHERE source IN (SELECT source FROM TOP_SOURCE)
),

REVENUE_DIFF AS (
    SELECT 
        source,
        ROUND(MAX(revenue), 2) AS max_revenue,
        ROUND(MIN(revenue), 2) AS min_revenue,
        ROUND(MAX(revenue) - MIN(revenue), 2) AS diff_revenue
    FROM SOURCE_MONTHLY_REVENUE
    GROUP BY source
)

SELECT 
    source,
    diff_revenue
FROM REVENUE_DIFF;

```

## bq010.sql

```sql
WITH GET_CUS_ID AS (
    SELECT 
        DISTINCT fullVisitorId as Henley_CUSTOMER_ID
    FROM 
        `bigquery-public-data.google_analytics_sample.ga_sessions_201707*`,
        UNNEST(hits) AS hits,
        UNNEST(hits.product) as product
    WHERE
        product.v2ProductName = "YouTube Men's Vintage Henley"
        AND product.productRevenue IS NOT NULL
    )

SELECT
    product.v2ProductName AS other_purchased_products
FROM
    `bigquery-public-data.google_analytics_sample.ga_sessions_201707*` TAB_A 
    RIGHT JOIN GET_CUS_ID
    ON GET_CUS_ID.Henley_CUSTOMER_ID=TAB_A.fullVisitorId,
    UNNEST(hits) AS hits,
    UNNEST(hits.product) as product
WHERE
    TAB_A.fullVisitorId IN (
        SELECT * FROM GET_CUS_ID
    )
    AND product.v2ProductName <> "YouTube Men's Vintage Henley"
    AND product.productRevenue IS NOT NULL
GROUP BY
    product.v2ProductName
ORDER BY
    SUM(product.productQuantity) DESC
LIMIT 1;

```

## bq011.sql

```sql
SELECT
  COUNT(DISTINCT MDaysUsers.user_pseudo_id) AS n_day_inactive_users_count
FROM
  (
    SELECT
      user_pseudo_id
    FROM
      `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*` AS T
    CROSS JOIN
      UNNEST(T.event_params) AS event_params
    WHERE
      event_params.key = 'engagement_time_msec' AND event_params.value.int_value > 0
      AND event_timestamp > UNIX_MICROS(TIMESTAMP_SUB(TIMESTAMP('2021-01-07 23:59:59'), INTERVAL 7 DAY))
      AND _TABLE_SUFFIX BETWEEN '20210101' AND '20210107'
  ) AS MDaysUsers
LEFT JOIN
  (
    SELECT
      user_pseudo_id
    FROM
      `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*` AS T
    CROSS JOIN
      UNNEST(T.event_params) AS event_params
    WHERE
      event_params.key = 'engagement_time_msec' AND event_params.value.int_value > 0
      AND event_timestamp > UNIX_MICROS(TIMESTAMP_SUB(TIMESTAMP('2021-01-07 23:59:59'), INTERVAL 2 DAY))
      AND _TABLE_SUFFIX BETWEEN '20210105' AND '20210107'
  ) AS NDaysUsers
ON MDaysUsers.user_pseudo_id = NDaysUsers.user_pseudo_id
WHERE
  NDaysUsers.user_pseudo_id IS NULL;

```

## bq018.sql

```sql
WITH us_cases_by_date AS (
  SELECT
    date,
    SUM( cumulative_confirmed ) AS cases
  FROM
    `bigquery-public-data.covid19_open_data.covid19_open_data`
  WHERE
    country_name="United States of America"
    AND date between '2020-03-01' and '2020-04-30'
  GROUP BY
    date
  ORDER BY
    date ASC
 )

, us_previous_day_comparison AS
(SELECT
  date,
  cases,
  LAG(cases) OVER(ORDER BY date) AS previous_day,
  cases - LAG(cases) OVER(ORDER BY date) AS net_new_cases,
  (cases - LAG(cases) OVER(ORDER BY date))*100/LAG(cases) OVER(ORDER BY date) AS percentage_increase
FROM us_cases_by_date
)
SELECT
  FORMAT_DATE('%m-%d', Date) 
FROM
  us_previous_day_comparison
ORDER BY  
  percentage_increase
DESC
LIMIT 1
```

## bq021.sql

```sql
WITH top20route AS (
SELECT
  start_station_name, end_station_name, avg_bike_duration, avg_taxi_duration
FROM (
  SELECT
    start_station_name,
    end_station_name,
    ROUND(start_station_latitude, 3) AS ss_lat,
    ROUND(start_station_longitude, 3) AS ss_long,
    ROUND(end_station_latitude, 3) AS es_lat,
    ROUND(end_station_longitude, 3) AS es_long,
    AVG(tripduration) AS avg_bike_duration,
    COUNT(*) AS bike_trips
  FROM
    `bigquery-public-data.new_york.citibike_trips`
  WHERE 
  EXTRACT(YEAR from starttime) = 2016 AND
    start_station_name != end_station_name
  GROUP BY
    start_station_name, end_station_name, ss_lat, ss_long, es_lat, es_long
  ORDER BY
    bike_trips DESC
  LIMIT
    20
) a
JOIN (
  SELECT
    ROUND(pickup_latitude, 3) AS pu_lat,
    ROUND(pickup_longitude, 3) AS pu_long,
    ROUND(dropoff_latitude, 3) AS do_lat,
    ROUND(dropoff_longitude, 3) AS do_long,
    AVG(UNIX_SECONDS(dropoff_datetime)-UNIX_SECONDS(pickup_datetime)) AS avg_taxi_duration,
    COUNT(*) AS taxi_trips
  FROM
    `bigquery-public-data.new_york.tlc_yellow_trips_2016`
  GROUP BY
    pu_lat, pu_long, do_lat, do_long
) b
ON
  a.ss_lat = b.pu_lat AND
  a.es_lat = b.do_lat AND
  a.ss_long = b.pu_long AND
  a.es_long = b.do_long
)

SELECT start_station_name
FROM top20route
WHERE avg_bike_duration < avg_taxi_duration
ORDER BY
avg_bike_duration
DESC
LIMIT 1

```

## bq022.sql

```sql
SELECT
  ROUND(MIN(trip_seconds) / 60, 0) AS min_minutes,
  ROUND(MAX(trip_seconds) / 60, 0) AS max_minutes,
  COUNT(*) AS total_trips,
  AVG(fare) AS average_fare
FROM (
  SELECT
    trip_seconds,
    NTILE(6) OVER (ORDER BY trip_seconds) AS quantile,
    fare
  FROM
    `bigquery-public-data.chicago_taxi_trips.taxi_trips`
  WHERE
    trip_seconds BETWEEN 0 AND 3600
)
GROUP BY
  quantile
ORDER BY
  min_minutes, max_minutes;

```

## bq025.sql

```sql
SELECT
  age.country_name,
  SUM(age.population) AS under_25,
  pop.midyear_population AS total,
  ROUND((SUM(age.population) / pop.midyear_population) * 100,2) AS pct_under_25
FROM (
  SELECT
    country_name,
    population,
    country_code
  FROM
    `bigquery-public-data.census_bureau_international.midyear_population_agespecific`
  WHERE
    year =2020
    AND age < 20) age
INNER JOIN (
  SELECT
    midyear_population,
    country_code
  FROM
    `bigquery-public-data.census_bureau_international.midyear_population`
  WHERE
    year = 2020) pop
ON
  age.country_code = pop.country_code
GROUP BY
  1,
  3
ORDER BY
  4 DESC
/* Remove limit for visualization */
LIMIT
  10

```

## bq031.sql

```sql
WITH transrate AS (
    SELECT
        DATE(CAST(year AS INT64), CAST(mo AS INT64), CAST(da AS INT64)) AS observation_date
        , ROUND((temp - 32.0) / 1.8, 1) AS temp_mean_c -- using Celsius instead of Fahrenheit
        , ROUND(prcp * 2.54, 1) AS prcp_cm -- from inches to centimeters
        , ROUND(CAST(wdsp AS FLOAT64) * 1.852 / 3.6, 1) AS wdsp_ms -- from knots to meters per second
    FROM `bigquery-public-data.noaa_gsod.gsod*`
    WHERE _TABLE_SUFFIX = "2019"
        AND CAST(mo AS INT64) <= 3
        AND stn in (SELECT usaf FROM `bigquery-public-data.noaa_gsod.stations` WHERE name = "ROCHESTER")
),

moving_avg AS (
    SELECT
        observation_date
        , temp_mean_c
        , prcp_cm
        , wdsp_ms
        , AVG(temp_mean_c) OVER (ORDER BY observation_date ROWS 7 PRECEDING) AS temp_moving_avg
        , AVG(prcp_cm) OVER (ORDER BY observation_date ROWS 7 PRECEDING) AS prcp_moving_avg
        , AVG(wdsp_ms) OVER (ORDER BY observation_date ROWS 7 PRECEDING) AS wdsp_moving_avg
    FROM transrate
),

lag_moving_avg AS (
    SELECT
        observation_date
        , temp_mean_c
        , prcp_cm
        , wdsp_ms
        , LAG(temp_moving_avg, 1) OVER (ORDER BY observation_date) AS lag1_temp_moving_avg
        , LAG(prcp_moving_avg, 1) OVER (ORDER BY observation_date) AS lag1_prcp_moving_avg
        , LAG(wdsp_moving_avg, 1) OVER (ORDER BY observation_date) AS lag1_wdsp_moving_avg

        , LAG(temp_moving_avg, 2) OVER (ORDER BY observation_date) AS lag2_temp_moving_avg
        , LAG(prcp_moving_avg, 2) OVER (ORDER BY observation_date) AS lag2_prcp_moving_avg
        , LAG(wdsp_moving_avg, 2) OVER (ORDER BY observation_date) AS lag2_wdsp_moving_avg

        , LAG(temp_moving_avg, 3) OVER (ORDER BY observation_date) AS lag3_temp_moving_avg
        , LAG(prcp_moving_avg, 3) OVER (ORDER BY observation_date) AS lag3_prcp_moving_avg
        , LAG(wdsp_moving_avg, 3) OVER (ORDER BY observation_date) AS lag3_wdsp_moving_avg

        , LAG(temp_moving_avg, 4) OVER (ORDER BY observation_date) AS lag4_temp_moving_avg
        , LAG(prcp_moving_avg, 4) OVER (ORDER BY observation_date) AS lag4_prcp_moving_avg
        , LAG(wdsp_moving_avg, 4) OVER (ORDER BY observation_date) AS lag4_wdsp_moving_avg

        , LAG(temp_moving_avg, 5) OVER (ORDER BY observation_date) AS lag5_temp_moving_avg
        , LAG(prcp_moving_avg, 5) OVER (ORDER BY observation_date) AS lag5_prcp_moving_avg
        , LAG(wdsp_moving_avg, 5) OVER (ORDER BY observation_date) AS lag5_wdsp_moving_avg

        , LAG(temp_moving_avg, 6) OVER (ORDER BY observation_date) AS lag6_temp_moving_avg
        , LAG(prcp_moving_avg, 6) OVER (ORDER BY observation_date) AS lag6_prcp_moving_avg
        , LAG(wdsp_moving_avg, 6) OVER (ORDER BY observation_date) AS lag6_wdsp_moving_avg

        , LAG(temp_moving_avg, 7) OVER (ORDER BY observation_date) AS lag7_temp_moving_avg
        , LAG(prcp_moving_avg, 7) OVER (ORDER BY observation_date) AS lag7_prcp_moving_avg
        , LAG(wdsp_moving_avg, 7) OVER (ORDER BY observation_date) AS lag7_wdsp_moving_avg

        , LAG(temp_moving_avg, 8) OVER (ORDER BY observation_date) AS lag8_temp_moving_avg
        , LAG(prcp_moving_avg, 8) OVER (ORDER BY observation_date) AS lag8_prcp_moving_avg
        , LAG(wdsp_moving_avg, 8) OVER (ORDER BY observation_date) AS lag8_wdsp_moving_avg
    FROM moving_avg
)

SELECT
    observation_date
    , temp_mean_c
    , prcp_cm
    , wdsp_ms

    , ROUND(lag1_temp_moving_avg, 1) AS lag1_temp_moving_avg
    , ROUND(lag1_prcp_moving_avg, 1) AS lag1_prcp_moving_avg
    , ROUND(lag1_wdsp_moving_avg, 1) AS lag1_wdsp_moving_avg
    
    , ROUND(lag1_temp_moving_avg - lag2_temp_moving_avg, 1) AS diff2_temp_moving_avg
    , ROUND(lag1_prcp_moving_avg - lag2_prcp_moving_avg, 1) AS diff2_prcp_moving_avg
    , ROUND(lag1_wdsp_moving_avg - lag2_wdsp_moving_avg, 1) AS diff2_wdsp_moving_avg
    , ROUND(lag2_temp_moving_avg, 1) AS lag2_temp_moving_avg
    , ROUND(lag2_prcp_moving_avg, 1) AS lag2_prcp_moving_avg
    , ROUND(lag2_wdsp_moving_avg, 1) AS lag2_wdsp_moving_avg
    
    , ROUND(lag2_temp_moving_avg - lag3_temp_moving_avg, 1) AS diff3_temp_moving_avg
    , ROUND(lag2_prcp_moving_avg - lag3_prcp_moving_avg, 1) AS diff3_prcp_moving_avg
    , ROUND(lag2_wdsp_moving_avg - lag3_wdsp_moving_avg, 1) AS diff3_wdsp_moving_avg
    , ROUND(lag3_temp_moving_avg, 1) AS lag3_temp_moving_avg
    , ROUND(lag3_prcp_moving_avg, 1) AS lag3_prcp_moving_avg
    , ROUND(lag3_wdsp_moving_avg, 1) AS lag3_wdsp_moving_avg
    
    , ROUND(lag3_temp_moving_avg - lag4_temp_moving_avg, 1) AS diff4_temp_moving_avg
    , ROUND(lag3_prcp_moving_avg - lag4_prcp_moving_avg, 1) AS diff4_prcp_moving_avg
    , ROUND(lag3_wdsp_moving_avg - lag4_wdsp_moving_avg, 1) AS diff4_wdsp_moving_avg
    , ROUND(lag4_temp_moving_avg, 1) AS lag4_temp_moving_avg
    , ROUND(lag4_prcp_moving_avg, 1) AS lag4_prcp_moving_avg
    , ROUND(lag4_wdsp_moving_avg, 1) AS lag4_wdsp_moving_avg
    
    , ROUND(lag4_temp_moving_avg - lag5_temp_moving_avg, 1) AS diff5_temp_moving_avg
    , ROUND(lag4_prcp_moving_avg - lag5_prcp_moving_avg, 1) AS diff5_prcp_moving_avg
    , ROUND(lag4_wdsp_moving_avg - lag5_wdsp_moving_avg, 1) AS diff5_wdsp_moving_avg
    , ROUND(lag5_temp_moving_avg, 1) AS lag5_temp_moving_avg
    , ROUND(lag5_prcp_moving_avg, 1) AS lag5_prcp_moving_avg
    , ROUND(lag5_wdsp_moving_avg, 1) AS lag5_wdsp_moving_avg
    
    , ROUND(lag5_temp_moving_avg - lag6_temp_moving_avg, 1) AS diff6_temp_moving_avg
    , ROUND(lag5_prcp_moving_avg - lag6_prcp_moving_avg, 1) AS diff6_prcp_moving_avg
    , ROUND(lag5_wdsp_moving_avg - lag6_wdsp_moving_avg, 1) AS diff6_wdsp_moving_avg
    , ROUND(lag6_temp_moving_avg, 1) AS lag6_temp_moving_avg
    , ROUND(lag6_prcp_moving_avg, 1) AS lag6_prcp_moving_avg
    , ROUND(lag6_wdsp_moving_avg, 1) AS lag6_wdsp_moving_avg
    
    , ROUND(lag6_temp_moving_avg - lag7_temp_moving_avg, 1) AS diff7_temp_moving_avg
    , ROUND(lag6_prcp_moving_avg - lag7_prcp_moving_avg, 1) AS diff7_prcp_moving_avg
    , ROUND(lag6_wdsp_moving_avg - lag7_wdsp_moving_avg, 1) AS diff7_wdsp_moving_avg
    , ROUND(lag7_temp_moving_avg, 1) AS lag7_temp_moving_avg
    , ROUND(lag7_prcp_moving_avg, 1) AS lag7_prcp_moving_avg
    , ROUND(lag7_wdsp_moving_avg, 1) AS lag7_wdsp_moving_avg
    
    , ROUND(lag7_temp_moving_avg - lag8_temp_moving_avg, 1) AS diff8_temp_moving_avg
    , ROUND(lag7_prcp_moving_avg - lag8_prcp_moving_avg, 1) AS diff8_prcp_moving_avg
    , ROUND(lag7_wdsp_moving_avg - lag8_wdsp_moving_avg, 1) AS diff8_wdsp_moving_avg
    , ROUND(lag8_temp_moving_avg, 1) AS lag8_temp_moving_avg
    , ROUND(lag8_prcp_moving_avg, 1) AS lag8_prcp_moving_avg
    , ROUND(lag8_wdsp_moving_avg, 1) AS lag8_wdsp_moving_avg
FROM lag_moving_avg
WHERE
  lag8_temp_moving_avg IS NOT NULL
ORDER BY observation_date;
-- all result rounded to 1 decimal place
```

## bq032.sql

```sql
WITH hurricane_geometry AS (
  SELECT
    * EXCEPT (longitude, latitude),
    ST_GEOGPOINT(longitude, latitude) AS geom,
    MAX(usa_wind) OVER (PARTITION BY sid) AS max_wnd_speed
  FROM
    `bigquery-public-data.noaa_hurricanes.hurricanes`
  WHERE
    season = '2020'
    AND basin = 'NA'
    AND name != 'NOT NAMED'
),
dist_between_points AS (
  SELECT
    sid,
    name,
    season,
    iso_time,
    max_wnd_speed,
    geom,
    ST_DISTANCE(geom, LAG(geom, 1) OVER (PARTITION BY sid ORDER BY iso_time ASC)) / 1000 AS dist
  FROM
    hurricane_geometry
),
total_distances AS (
  SELECT
    sid,
    name,
    season,
    iso_time,
    max_wnd_speed,
    geom,
    SUM(dist) OVER (PARTITION BY sid ORDER BY iso_time ASC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_distance,
    SUM(dist) OVER (PARTITION BY sid) AS total_dist
  FROM
    dist_between_points
),
ranked_hurricanes AS (
  SELECT
    *,
    DENSE_RANK() OVER (ORDER BY total_dist DESC) AS dense_rank
  FROM
    total_distances
)

SELECT
  ST_Y(geom)
FROM
  ranked_hurricanes
WHERE
  dense_rank = 2
ORDER BY
cumulative_distance
DESC
LIMIT 1
;

```

## bq034.sql

```sql
WITH params AS (
  SELECT ST_GeogPoint(-87.6847, 41.8319) AS center,
         50 AS maxdist_km
),
distance_from_center AS (
  SELECT
    id,
    name,
    state,
    ST_GeogPoint(longitude, latitude) AS loc,
    ST_Distance(ST_GeogPoint(longitude, latitude), params.center) AS dist_meters
  FROM
    `bigquery-public-data.ghcn_d.ghcnd_stations`,
    params
  WHERE ST_DWithin(ST_GeogPoint(longitude, latitude), params.center, params.maxdist_km*1000)
),
nearest_stations AS (
  SELECT 
    *, 
    RANK() OVER (ORDER BY dist_meters ASC) AS rank
  FROM 
    distance_from_center
),
nearest_nstations AS (
  SELECT 
    station.* 
  FROM 
    nearest_stations AS station, params
)
SELECT * from nearest_nstations
```

## bq035.sql

```sql
SELECT
  bike_number, 
  AVG(dist_in_m) AS avg_dist_m, 
  SUM(dist_in_m) AS total_dist_m
FROM (
  SELECT
    ST_DISTANCE(
      ST_GEOGPOINT(start_lon, start_lat),
      ST_GEOGPOINT(end_lon, end_lat)
    ) AS dist_in_m,
    starts.bike_number
  FROM (
    SELECT 
      latitude AS start_lat,
      longitude AS start_lon,
      bike_number,
      trip_id
    FROM `bigquery-public-data.san_francisco.bikeshare_trips` trips
    LEFT JOIN `bigquery-public-data.san_francisco.bikeshare_stations` stations
      ON trips.start_station_id = stations.station_id
  ) starts
  LEFT JOIN (
    SELECT 
      latitude AS end_lat,
      longitude AS end_lon,
      bike_number,
      trip_id
    FROM `bigquery-public-data.san_francisco.bikeshare_trips` trips
    LEFT JOIN `bigquery-public-data.san_francisco.bikeshare_stations` stations
      ON trips.end_station_id = stations.station_id
  ) ends ON ends.trip_id = starts.trip_id
)
GROUP BY bike_number
ORDER BY total_dist_m DESC
```

## bq039.sql

```sql
SELECT 
    tz.zone_name AS pickup_zone,
    tz1.zone_name AS dropoff_zone, 
    time_duration_in_secs,
    driving_speed_miles_per_hour,
    tip_rate
FROM
(
SELECT *,
    TIMESTAMP_DIFF(dropoff_datetime,pickup_datetime,SECOND) as time_duration_in_secs,
    ROUND(trip_distance / (TIMESTAMP_DIFF(dropoff_datetime, pickup_datetime, SECOND) / 3600), 2) AS driving_speed_miles_per_hour,
    (CASE WHEN total_amount=0 THEN 0
          ELSE (tip_amount*100/total_amount) END) as tip_rate
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2016`
) t
INNER JOIN `bigquery-public-data.new_york_taxi_trips.taxi_zone_geom` tz
ON t.pickup_location_id = tz.zone_id
INNER JOIN `bigquery-public-data.new_york_taxi_trips.taxi_zone_geom` tz1
ON t.dropoff_location_id = tz1.zone_id
WHERE 
    pickup_datetime BETWEEN '2016-07-01' AND '2016-07-07' 
    AND dropoff_datetime BETWEEN '2016-07-01' AND '2016-07-07'
    AND TIMESTAMP_DIFF(dropoff_datetime,pickup_datetime,SECOND) > 0
    AND passenger_count > 5
    AND trip_distance >= 10
    AND tip_amount >= 0 
    AND tolls_amount >= 0 
    AND mta_tax >= 0 
    AND fare_amount >= 0
    AND total_amount >= 0
ORDER BY total_amount DESC
LIMIT 10;

```

## bq042.sql

```sql
SELECT
  -- Create a timestamp from the date components.
  TIMESTAMP(CONCAT(year,"-",mo,"-",da)) AS timestamp,
  -- Replace numerical null values with actual null
  AVG(IF (temp=9999.9,
      null,
      temp)) AS temperature,
  AVG(IF (wdsp="999.9",
      null,
      CAST(wdsp AS Float64))) AS wind_speed,
  AVG(IF (prcp=99.99,
      0,
      prcp)) AS precipitation
FROM
  `bigquery-public-data.noaa_gsod.gsod20*`
WHERE
  CAST(YEAR AS INT64) > 2010
  AND CAST(YEAR AS INT64) < 2021
  AND CAST(MO AS INT64) = 6
  AND CAST(DA AS INT64) = 12
  AND stn = "725030" -- La Guardia
GROUP BY
  timestamp
ORDER BY
  timestamp ASC;

```

## bq045.sql

```sql
WITH WashingtonStations2023 AS 
    (
        SELECT 
            weather.stn AS station_id,
            ANY_VALUE(station.name) AS name
        FROM
            `bigquery-public-data.noaa_gsod.stations` AS station
        INNER JOIN
            `bigquery-public-data.noaa_gsod.gsod2023` AS weather
        ON
            station.usaf = weather.stn
        WHERE
            station.state = 'WA' 
            AND 
            station.usaf != '999999'
        GROUP BY
            station_id
    ),
prcp2023 AS (
SELECT
    washington_stations.name,
    (
        SELECT 
            COUNT(*)
        FROM
            `bigquery-public-data.noaa_gsod.gsod2023` AS weather
        WHERE
            washington_stations.station_id = weather.stn
            AND
            prcp > 0
            AND
            prcp !=99.99
    )
    AS rainy_days
FROM 
    WashingtonStations2023 AS washington_stations
ORDER BY
    rainy_days DESC
),
WashingtonStations2022 AS 
    (
        SELECT 
            weather.stn AS station_id,
            ANY_VALUE(station.name) AS name
        FROM
            `bigquery-public-data.noaa_gsod.stations` AS station
        INNER JOIN
            `bigquery-public-data.noaa_gsod.gsod2022` AS weather
        ON
            station.usaf = weather.stn
        WHERE
            station.state = 'WA' 
            AND 
            station.usaf != '999999'
        GROUP BY
            station_id
    ),
prcp2022 AS (
SELECT
    washington_stations.name,
    (
        SELECT 
            COUNT(*)
        FROM
            `bigquery-public-data.noaa_gsod.gsod2022` AS weather
        WHERE
            washington_stations.station_id = weather.stn
            AND
            prcp > 0
            AND
            prcp != 99.99
    )
    AS rainy_days
FROM 
    WashingtonStations2022 AS washington_stations
ORDER BY
    rainy_days DESC
)

SELECT prcp2023.name
FROM prcp2023
JOIN prcp2022
on prcp2023.name = prcp2022.name
WHERE prcp2023.rainy_days > 150
AND prcp2023.rainy_days < prcp2022.rainy_days
```

## bq049.sql

```sql
WITH DUBUQUE_LIQUOR_CTE AS (
SELECT
  CASE
      WHEN UPPER(category_name) LIKE 'BUTTERSCOTCH SCHNAPPS' THEN 'All Other' --Edge case is not a scotch
      WHEN UPPER(category_name) LIKE '%WHISKIES' 
            AND UPPER(category_name) NOT LIKE '%RYE%'
            AND UPPER(category_name) NOT LIKE '%BOURBON%'
            AND UPPER(category_name) NOT LIKE '%SCOTCH%'     THEN 'Other Whiskey'
      WHEN UPPER(category_name) LIKE '%RYE%'                 THEN 'Rye Whiskey'
      WHEN UPPER(category_name) LIKE '%BOURBON%'             THEN 'Bourbon Whiskey'
      WHEN UPPER(category_name) LIKE '%SCOTCH%'              THEN 'Scotch Whiskey'
      ELSE 'All Other'
  END                              AS category_group,
  EXTRACT(MONTH FROM date)         AS month,    -- At the time of this query, there is only data until month 6.
  LEFT(CAST(zip_code AS string),5) AS zip_code, -- Casting to string necessary because zip_code has a mix of int & str types.
  ROUND(SUM(sale_dollars), 2)      AS sale_dollars_sum,

FROM 
  bigquery-public-data.iowa_liquor_sales.sales

WHERE
  UPPER(county)               = 'DUBUQUE'
  AND EXTRACT(YEAR FROM date) = 2022

GROUP BY
  category_group,
  month,
  zip_code
  
ORDER BY 
  category_group,
  month,
  zip_code
),

DUBUQUE_POPULATION_CTE AS (
SELECT
  zipcode,
  SUM(population) AS population_sum
FROM bigquery-public-data.census_bureau_usa.population_by_zip_2010
WHERE 
  minimum_age >= 21
GROUP BY 
  zipcode
),
MONTH_INFO AS (
SELECT 
  l.month,
  l.zip_code,
  l.sale_dollars_sum,
  ROUND(sale_dollars_sum/p.population_sum, 2) AS dollars_per_capita
FROM 
  DUBUQUE_LIQUOR_CTE AS l
  LEFT JOIN 
  DUBUQUE_POPULATION_CTE AS p
  ON l.zip_code = p.zipcode
WHERE
  category_group = 'Bourbon Whiskey'
GROUP BY 
  category_group,
  zip_code,
  month,
  sale_dollars_sum,
  zipcode,
  population_sum
ORDER BY
  zip_code,
  month
),
zip_code_sales AS (
    SELECT
        zip_code,
        SUM(sale_dollars_sum) AS total_sale_dollars_sum
    FROM MONTH_INFO
    GROUP BY zip_code
),
ranked_zip_codes AS (
    SELECT
        zip_code,
        total_sale_dollars_sum,
        ROW_NUMBER() OVER (ORDER BY total_sale_dollars_sum DESC) AS rank
    FROM zip_code_sales
)
SELECT
    t.month,
    t.zip_code,
    t.dollars_per_capita
FROM MONTH_INFO t
JOIN ranked_zip_codes r
ON t.zip_code = r.zip_code
WHERE r.rank = 3
ORDER BY t.month;

```

## bq053.sql

```sql
SELECT
  c.fall_color,
  SUM(d.count_growth) AS change
FROM (
  SELECT
    fall_color,
    UPPER(species_scientific_name) AS latin
  FROM
    `bigquery-public-data.new_york.tree_species`)c
JOIN (
  SELECT
    IFNULL(a.upper_latin,
      b.upper_latin) AS latin,
    (IFNULL(count_2015,
        0)-IFNULL(count_1995,
        0)) AS count_growth
  FROM (
    SELECT
      UPPER(spc_latin) AS upper_latin,
      spc_common,
      COUNT(*) AS count_2015
    FROM
      `bigquery-public-data.new_york.tree_census_2015`
    WHERE
      status="Alive"
    GROUP BY
      spc_latin,
      spc_common)a
  FULL OUTER JOIN (
    SELECT
      UPPER(spc_latin) AS upper_latin,
      COUNT(*) AS count_1995
    FROM
      `bigquery-public-data.new_york.tree_census_1995`
    WHERE
      status !="Dead"
    GROUP BY
      spc_latin)b
  ON
    a.upper_latin=b.upper_latin
  ORDER BY
    count_growth DESC)d
ON
  d.latin=c.latin
GROUP BY
  fall_color
ORDER BY
  change DESC
```

## bq059.sql

```sql
WITH stations AS (
  SELECT station_id
  FROM
    `bigquery-public-data.san_francisco_bikeshare.bikeshare_station_info` AS stainfo
  WHERE stainfo.region_id = (
    SELECT region.region_id
    FROM `bigquery-public-data.san_francisco_bikeshare.bikeshare_regions` AS region
    WHERE region.name = "Berkeley"
  )
),
meta_data AS (
    SELECT
        round(st_distance(start_station_geom, end_station_geom), 1) as distancia_metros,
        round(st_distance(start_station_geom, end_station_geom) / duration_sec, 1) as velocidade_media
    FROM
        `bigquery-public-data.san_francisco_bikeshare.bikeshare_trips` AS trips
    WHERE
        cast(trips.start_station_id as string) IN (SELECT station_id FROM stations)
        AND cast(trips.end_station_id as string) IN (SELECT station_id FROM stations)
        AND start_station_latitude IS NOT NULL
        AND start_station_longitude IS NOT NULL
        AND end_station_latitude IS NOT NULL
        AND end_station_longitude IS NOT NULL
        AND st_distance(start_station_geom, end_station_geom) > 1000
    ORDER BY
        velocidade_media DESC
    LIMIT 1
)

SELECT velocidade_media as max_velocity
FROM meta_data;

```

## bq060.sql

```sql
WITH results AS (
    SELECT
        growth.country_name,
        growth.net_migration,
        CAST(area.country_area as INT64) as country_area
    FROM (
        SELECT
            country_name,
            net_migration,
            country_code
        FROM
            `bigquery-public-data.census_bureau_international.birth_death_growth_rates`
        WHERE
            year = 2017
    ) growth
    INNER JOIN (
        SELECT
            country_area,
            country_code
        FROM
            `bigquery-public-data.census_bureau_international.country_names_area`
        WHERE
            country_area > 500
    ) area
    ON
        growth.country_code = area.country_code
    ORDER BY
        net_migration DESC
    LIMIT 3
)
SELECT country_name, net_migration
FROM results;

```

## bq061.sql

```sql
WITH acs_2018 AS (
    SELECT
      geo_id,
      median_income AS median_income_2018
    FROM
      `bigquery-public-data.census_bureau_acs.censustract_2018_5yr` 
),
acs_2015 AS (
    SELECT
      geo_id,
      median_income AS median_income_2015
    FROM
      `bigquery-public-data.census_bureau_acs.censustract_2015_5yr` ),
acs_diff AS (
    SELECT
      a18.geo_id,
      a18.median_income_2018,
      a15.median_income_2015,
      (a18.median_income_2018 - a15.median_income_2015) AS median_income_diff,
    FROM
      acs_2018 a18
    JOIN
      acs_2015 a15
    ON
      a18.geo_id = a15.geo_id
),
max_geo_id AS (
    SELECT
      geo_id
    FROM
      acs_diff
    WHERE
      median_income_diff IS NOT NULL
      AND acs_diff.geo_id in (
        SELECT
          geo_id
        FROM
          `bigquery-public-data.geo_census_tracts.census_tracts_california`
      )
    ORDER BY
      median_income_diff DESC
    LIMIT 1
)
SELECT
    tracts.tract_ce as tract_code
FROM
    max_geo_id
JOIN
    `bigquery-public-data.geo_census_tracts.census_tracts_california` AS tracts
ON
    max_geo_id.geo_id = tracts.geo_id;

```

## bq064.sql

```sql
WITH all_zip_tract_join AS (
  SELECT 
    zips.zip_code, 
    zips.functional_status as zip_functional_status,
    tracts.tract_ce, 
    tracts.geo_id as tract_geo_id, 
    tracts.functional_status as tract_functional_status,
    ST_Area(ST_Intersection(tracts.tract_geom, zips.zip_code_geom))
        / ST_Area(tracts.tract_geom) as tract_pct_in_zip_code
  FROM  
    `bigquery-public-data.geo_census_tracts.us_census_tracts_national` tracts,
    `bigquery-public-data.geo_us_boundaries.zip_codes` zips
  WHERE 
    ST_Intersects(tracts.tract_geom, zips.zip_code_geom)
),
zip_tract_join AS (
  SELECT * FROM all_zip_tract_join WHERE tract_pct_in_zip_code > 0
),
census_totals AS (
  -- convert averages to additive totals
  SELECT 
    geo_id,
    total_pop,
    total_pop * income_per_capita AS total_income 
  FROM 
    `bigquery-public-data.census_bureau_acs.censustract_2017_5yr` 
),
joined AS ( 
  -- join with precomputed census/zip pairs,
  -- compute zip's share of tract
  SELECT 
    zip_code, 
    total_pop * tract_pct_in_zip_code    AS zip_pop,
    total_income * tract_pct_in_zip_code AS zip_income
  FROM census_totals c
  JOIN zip_tract_join ztj
  ON c.geo_id = ztj.tract_geo_id
),
sums AS ( 
  -- aggregate all "pieces" of zip code
  SELECT
    zip_code, 
    SUM(zip_pop) AS zip_pop,
    SUM(zip_income) AS zip_total_inc
  FROM joined 
  GROUP BY zip_code
),
zip_pop_income AS (
    SELECT 
        zip_code, zip_pop, 
        -- convert to averages
        zip_total_inc / zip_pop AS income_per_capita
    FROM sums
),
zipcodes_within_distance as (
    SELECT 
        zip_code, zip_code_geom
    FROM 
        `bigquery-public-data.geo_us_boundaries.zip_codes`
    WHERE
        state_code = 'WA'  -- Washington state code
        AND
        ST_DWithin(
            ST_GeogPoint(-122.191667, 47.685833),
            zip_code_geom,
            8046.72
        )
)
select 
  stats.zip_code,
  ROUND(stats.zip_pop, 1) as zip_population,
  ROUND(stats.income_per_capita, 1) as average_income
from 
  zipcodes_within_distance area
join 
  zip_pop_income stats
on area.zip_code = stats.zip_code
ORDER BY
    average_income DESC;

```

## bq066.sql

```sql
WITH poverty_and_natality AS (
  SELECT
    EXTRACT(YEAR FROM n.Year) AS data_year,
    p.geo_id AS county_fips,
    (p.poverty / p.pop_determined_poverty_status) * 100 AS poverty_rate,
    SUM(n.Births) AS total_births,
    SUM(CASE WHEN n.Maternal_Morbidity_YN = 0 THEN n.Births ELSE 0 END) AS births_without_morbidity
  FROM
    `bigquery-public-data.census_bureau_acs.county_2015_5yr` p
  JOIN
    `bigquery-public-data.sdoh_cdc_wonder_natality.county_natality_by_maternal_morbidity` n
  ON p.geo_id = n.County_of_Residence_FIPS
  WHERE
    p.pop_determined_poverty_status > 0 AND
    EXTRACT(YEAR FROM n.Year) = 2016
  GROUP BY
    p.geo_id, p.poverty, p.pop_determined_poverty_status, EXTRACT(YEAR FROM n.Year)
  UNION ALL
  SELECT
    EXTRACT(YEAR FROM n.Year) AS data_year,
    p.geo_id AS county_fips,
    (p.poverty / p.pop_determined_poverty_status) * 100 AS poverty_rate,
    SUM(n.Births) AS total_births,
    SUM(CASE WHEN n.Maternal_Morbidity_YN = 0 THEN n.Births ELSE 0 END) AS births_without_morbidity
  FROM
    `bigquery-public-data.census_bureau_acs.county_2016_5yr` p
  JOIN
    `bigquery-public-data.sdoh_cdc_wonder_natality.county_natality_by_maternal_morbidity` n
  ON p.geo_id = n.County_of_Residence_FIPS
  WHERE
    p.pop_determined_poverty_status > 0 AND
    EXTRACT(YEAR FROM n.Year) = 2017
  GROUP BY
    p.geo_id, p.poverty, p.pop_determined_poverty_status, EXTRACT(YEAR FROM n.Year)
  UNION ALL
  SELECT
    EXTRACT(YEAR FROM n.Year) AS data_year,
    p.geo_id AS county_fips,
    (p.poverty / p.pop_determined_poverty_status) * 100 AS poverty_rate,
    SUM(n.Births) AS total_births,
    SUM(CASE WHEN n.Maternal_Morbidity_YN = 0 THEN n.Births ELSE 0 END) AS births_without_morbidity
  FROM
    `bigquery-public-data.census_bureau_acs.county_2017_5yr` p
  JOIN
    `bigquery-public-data.sdoh_cdc_wonder_natality.county_natality_by_maternal_morbidity` n
  ON p.geo_id = n.County_of_Residence_FIPS
  WHERE
    p.pop_determined_poverty_status > 0 AND
    EXTRACT(YEAR FROM n.Year) = 2018
  GROUP BY
    p.geo_id, p.poverty, p.pop_determined_poverty_status, EXTRACT(YEAR FROM n.Year)
)

SELECT
  data_year,
  CORR(poverty_rate, (births_without_morbidity / total_births) * 100) AS correlation_coefficient
FROM
  poverty_and_natality
GROUP BY
  data_year

```

## bq074.sql

```sql
WITH acs_2018 AS (
  SELECT geo_id, unemployed_pop AS unemployed_2018  
  FROM `bigquery-public-data.census_bureau_acs.county_2018_5yr` 
),
 
acs_2015 AS (
  SELECT geo_id, unemployed_pop AS unemployed_2015  
  FROM `bigquery-public-data.census_bureau_acs.county_2015_5yr` 
),
 
unemployed_change AS (
  SELECT
    u18.unemployed_2018, u18.geo_id, u15.unemployed_2015,
    (u18.unemployed_2018 - u15.unemployed_2015) AS u_change
  FROM acs_2018 u18
  JOIN acs_2015 u15
  ON u18.geo_id = u15.geo_id
),
 
duals_Jan_2018 AS (
  SELECT Public_Total AS duals_2018, County_Name, FIPS 
  FROM `bigquery-public-data.sdoh_cms_dual_eligible_enrollment.dual_eligible_enrollment_by_county_and_program` 
  WHERE Date = '2018-12-01'
),

duals_Jan_2015 AS (
  SELECT Public_Total AS duals_2015, County_Name, FIPS
  FROM `bigquery-public-data.sdoh_cms_dual_eligible_enrollment.dual_eligible_enrollment_by_county_and_program` 
  WHERE Date = '2015-12-01'
),

duals_change AS (
  SELECT
    d18.FIPS, d18.County_Name, d18.duals_2018, d15.duals_2015,
    (d18.duals_2018 - d15.duals_2015) AS total_duals_diff
  FROM duals_Jan_2018 d18
  JOIN duals_Jan_2015 d15
  ON d18.FIPS = d15.FIPS
),
 
corr_tbl AS (
  SELECT unemployed_change.geo_id, duals_change.County_Name, unemployed_change.u_change, duals_change.total_duals_diff
  FROM unemployed_change
  JOIN duals_change
  ON unemployed_change.geo_id = duals_change.FIPS
)


SELECT COUNT(*)
FROM corr_tbl
WHERE
u_change >0
AND
corr_tbl.total_duals_diff < 0
```

## bq076.sql

```sql

SELECT
  incidents AS highest_monthly_thefts
FROM (
  SELECT
    year,
    EXTRACT(MONTH FROM date) AS month,
    COUNT(1) AS incidents,
    RANK() OVER (PARTITION BY year ORDER BY COUNT(1) DESC) AS ranking
  FROM
    `bigquery-public-data.chicago_crime.crime`
  WHERE
    primary_type = 'MOTOR VEHICLE THEFT'
    AND year = 2016
  GROUP BY
    year,
    month
)
WHERE
  ranking = 1
ORDER BY
  year DESC
LIMIT 1;

```

## bq077.sql

```sql
SELECT
  year,
  incidents
FROM (
  SELECT
    year,
    EXTRACT(MONTH
    FROM
      date) AS month,
    COUNT(1) AS incidents,
    RANK() OVER (PARTITION BY year ORDER BY COUNT(1) DESC) AS ranking
  FROM
    `bigquery-public-data.chicago_crime.crime`
  WHERE
    primary_type = 'MOTOR VEHICLE THEFT'
    AND year BETWEEN 2010 AND 2016
  GROUP BY
    year,
    month )
WHERE
  ranking = 1
ORDER BY
  year ASC
```

## bq078.sql

```sql
SELECT
  T1.targetId AS target_id,
  T1.datasourceId,
  targets.approvedSymbol AS approved_symbol,
  overall_associations.score AS overall_score
FROM
  `bigquery-public-data.open_targets_platform.associationByDatasourceDirect` as T1
JOIN
  `bigquery-public-data.open_targets_platform.targets` AS targets
ON
  targetId = targets.id
JOIN
  `bigquery-public-data.open_targets_platform.associationByOverallDirect` AS overall_associations
ON
  T1.targetId = overall_associations.targetId
WHERE
  overall_associations.diseaseId = 'EFO_0000676' AND datasourceId = 'impc'
ORDER BY
  overall_associations.score DESC
LIMIT
  1;

```

## bq081.sql

```sql
SELECT t1.*
  FROM 
  (SELECT Trips.trip_id TripId,
               Trips.duration_sec TripDuration,
               Trips.start_date TripStartDate,
               Trips.start_station_name TripStartStation,
               Trips.member_gender Gender,
               Regions.name RegionName
          FROM `bigquery-public-data.san_francisco_bikeshare.bikeshare_trips` Trips
         INNER JOIN `bigquery-public-data.san_francisco_bikeshare.bikeshare_station_info` StationInfo
            ON CAST(Trips.start_station_id AS STRING) = CAST(StationInfo.station_id AS STRING)
         INNER JOIN `bigquery-public-data.san_francisco_bikeshare.bikeshare_regions` Regions
            ON StationInfo.region_id = Regions.region_id
         WHERE (EXTRACT(YEAR from Trips.start_date)) BETWEEN 2014 AND 2017
           ) 
           t1
 RIGHT JOIN (SELECT MAX(start_date) TripStartDate,
                   Regions.name RegionName
              FROM `bigquery-public-data.san_francisco_bikeshare.bikeshare_station_info` StationInfo
             INNER JOIN `bigquery-public-data.san_francisco_bikeshare.bikeshare_trips` Trips
                ON CAST(StationInfo.station_id AS STRING) = CAST(Trips.start_station_id AS STRING)
             INNER JOIN `bigquery-public-data.san_francisco_bikeshare.bikeshare_regions` Regions
                ON Regions.region_id = StationInfo.region_id
                 WHERE (EXTRACT(YEAR from Trips.start_date) BETWEEN 2014 AND 2017
           AND Regions.name IS NOT NULL)
             GROUP BY RegionName) 
             t2
    ON t1.RegionName = t2.RegionName AND t1.TripStartDate = t2.TripStartDate
```

## bq085.sql

```sql
SELECT
  c.country,
  c.total_confirmed_cases,
  (c.total_confirmed_cases / p.population) * 100000 AS cases_per_100k
FROM
  (
    SELECT
      CASE
        WHEN country_region = 'US' THEN 'United States'
        WHEN country_region = 'Iran' THEN 'Iran, Islamic Rep.'
        ELSE country_region
      END AS country,
      SUM(confirmed) AS total_confirmed_cases
    FROM
      `bigquery-public-data.covid19_jhu_csse.summary`
    WHERE
      date = '2020-04-20'
      AND country_region IN ('US', 'France', 'China', 'Italy', 'Spain', 'Germany', 'Iran')
    GROUP BY
      country
  ) AS c
JOIN
  (
    SELECT
      country_name AS country,
      SUM(value) AS population
    FROM
      `bigquery-public-data.world_bank_wdi.indicators_data`
    WHERE
      indicator_code = 'SP.POP.TOTL'
      AND year = 2020
    GROUP BY
      country_name
  ) AS p
ON
  c.country = p.country
ORDER BY
  cases_per_100k DESC
```

## bq086.sql

```sql
WITH
  country_pop AS (
  SELECT
    country_code AS iso_3166_1_alpha_3,
    year_2018 AS population_2018
  FROM
    `bigquery-public-data.world_bank_global_population.population_by_country`)
SELECT
  country_code,
  country_name,
  cumulative_confirmed AS june_confirmed_cases,
  population_2018,
  ROUND(cumulative_confirmed/population_2018 * 100,2) AS case_percent
FROM
  `bigquery-public-data.covid19_open_data.covid19_open_data`
JOIN
  country_pop
USING
  (iso_3166_1_alpha_3)
WHERE
  date = '2020-06-30'
  AND aggregation_level = 0
ORDER BY
  case_percent DESC
```

## bq087.sql

```sql
SELECT
  table_2019.avg_symptom_Anosmia_2019,
  table_2020.avg_symptom_Anosmia_2020,
  ((table_2020.avg_symptom_Anosmia_2020 - table_2019.avg_symptom_Anosmia_2019) / table_2019.avg_symptom_Anosmia_2019) * 100 AS avg_increase
FROM (
  SELECT
    AVG(SAFE_CAST(symptom_Anosmia AS FLOAT64)) AS avg_symptom_Anosmia_2020
  FROM
    `bigquery-public-data.covid19_symptom_search.symptom_search_sub_region_2_weekly`
  WHERE
    sub_region_1 = "New York"
    AND sub_region_2 IN ("Bronx County", "Queens County", "Kings County", "New York County", "Richmond County")
    AND date >= '2020-01-01'
    AND date < '2021-01-01'
) AS table_2020,
(
  SELECT
    AVG(SAFE_CAST(symptom_Anosmia AS FLOAT64)) AS avg_symptom_Anosmia_2019
  FROM
    `bigquery-public-data.covid19_symptom_search.symptom_search_sub_region_2_weekly`
  WHERE
    sub_region_1 = "New York"
    AND sub_region_2 IN ("Bronx County", "Queens County", "Kings County", "New York County", "Richmond County")
    AND date >= '2019-01-01'
    AND date < '2020-01-01'
) AS table_2019

```

## bq088.sql

```sql
SELECT
  table_2019.avg_symptom_Anxiety_2019,
  table_2020.avg_symptom_Anxiety_2020,
  ((table_2020.avg_symptom_Anxiety_2020 - table_2019.avg_symptom_Anxiety_2019)/table_2019.avg_symptom_Anxiety_2019) * 100 AS percent_increase_anxiety,
  table_2019.avg_symptom_Depression_2019,
  table_2020.avg_symptom_Depression_2020,
  ((table_2020.avg_symptom_Depression_2020 - table_2019.avg_symptom_Depression_2019)/table_2019.avg_symptom_Depression_2019) * 100 AS percent_increase_depression
FROM (
  SELECT
    AVG(CAST(symptom_Anxiety AS FLOAT64)) AS avg_symptom_Anxiety_2020,
    AVG(CAST(symptom_Depression AS FLOAT64)) AS avg_symptom_Depression_2020,
  FROM
    `bigquery-public-data.covid19_symptom_search.symptom_search_country_weekly`
  WHERE
    country_region_code = "US"
    AND date >= '2020-01-01'
    AND date <'2021-01-01') AS table_2020,
  (
  SELECT
    AVG(CAST(symptom_Anxiety AS FLOAT64)) AS avg_symptom_Anxiety_2019,
    AVG(CAST(symptom_Depression AS FLOAT64)) AS avg_symptom_Depression_2019,
  FROM
    `bigquery-public-data.covid19_symptom_search.symptom_search_country_weekly`
  WHERE
    country_region_code = "US"
    AND date >= '2019-01-01'
    AND date <'2020-01-01') AS table_2019
```

## bq089.sql

```sql
WITH
  num_vaccine_sites_per_county AS (
  SELECT
    facility_sub_region_1 AS us_state,
    facility_sub_region_2 AS us_county,
    facility_sub_region_2_code AS us_county_fips,
    COUNT(DISTINCT facility_place_id) AS num_vaccine_sites
  FROM
    bigquery-public-data.covid19_vaccination_access.facility_boundary_us_all
  WHERE
    STARTS_WITH(facility_sub_region_2_code, "06")
  GROUP BY
    facility_sub_region_1,
    facility_sub_region_2,
    facility_sub_region_2_code ),
  total_population_per_county AS (
  SELECT
    LEFT(geo_id, 5) AS us_county_fips,
    ROUND(SUM(total_pop)) AS total_population
  FROM
    bigquery-public-data.census_bureau_acs.censustract_2018_5yr
  WHERE
    STARTS_WITH(LEFT(geo_id, 5), "06")
  GROUP BY
    LEFT(geo_id, 5) )
SELECT
  * EXCEPT(us_county_fips),
  ROUND((num_vaccine_sites * 1000) / total_population, 2) AS sites_per_1k_ppl
FROM
  num_vaccine_sites_per_county
INNER JOIN
  total_population_per_county
USING
  (us_county_fips)
ORDER BY
  sites_per_1k_ppl ASC
LIMIT
  100;

```

## bq090.sql

```sql
WITH MomentumTrades AS (
  SELECT
    StrikePrice - LastPx AS priceDifference
  FROM
    `bigquery-public-data.cymbal_investments.trade_capture_report`
  WHERE
    SUBSTR(TargetCompID, 0, 4) = 'MOMO'
    AND (SELECT Side FROM UNNEST(Sides)) = 'LONG'
),

FeelingLuckyTrades AS (
  SELECT
    StrikePrice - LastPx AS priceDifference
  FROM
    `bigquery-public-data.cymbal_investments.trade_capture_report`
  WHERE
    SUBSTR(TargetCompID, 0, 4) = 'LUCK'
    AND (SELECT Side FROM UNNEST(Sides)) = 'LONG'
)

SELECT
  AVG(FeelingLuckyTrades.priceDifference) - AVG(MomentumTrades.priceDifference) AS averageDifference 
FROM
  MomentumTrades,
  FeelingLuckyTrades
```

## bq095.sql

```sql
SELECT
  targets.approvedSymbol AS target_symbol,
  drugs.name AS drug_name,
  source_urls.element.url AS clinical_trial_reference_url,
FROM
  `open-targets-prod.platform.evidence` AS evidence,
  UNNEST(evidence.urls.list) AS source_urls
JOIN
  `open-targets-prod.platform.targets` AS targets
ON
  evidence.targetId=targets.id
JOIN
  `open-targets-prod.platform.molecule` AS drugs
ON
  evidence.drugId=drugs.id
WHERE
  datasourceId="chembl"
  AND diseaseId="EFO_0007416"
  AND evidence.clinicalStatus = "Completed"
```

## bq096.sql

```sql
WITH tenplus AS (
  SELECT 
    year, 
    EXTRACT(DAYOFYEAR FROM DATE(eventdate)) AS dayofyear, 
    COUNT(*) AS count
  FROM 
    bigquery-public-data.gbif.occurrences
  WHERE 
    eventdate IS NOT NULL 
    AND species = 'Sterna paradisaea' 
    AND decimallatitude > 40.0 
    AND month > 1
  GROUP BY 
    year, 
    eventdate
  HAVING 
    COUNT(*) > 10
)

SELECT 
  year AS year
FROM 
  tenplus
GROUP BY 
  year
ORDER BY 
  MIN(dayofyear)
LIMIT 1;

```

## bq097.sql

```sql
WITH bea_2012 AS (
  SELECT GeoFIPS, GeoName, Earnings_per_job_avg AS earnings_2012
  FROM `bigquery-public-data.sdoh_bea_cainc30.fips`
  WHERE Year='2012-01-01' AND ENDS_WITH(GeoName, "MA") IS TRUE
),

bea_2017 AS (
  SELECT GeoFIPS, GeoName, Earnings_per_job_avg AS earnings_2017
  FROM `bigquery-public-data.sdoh_bea_cainc30.fips`
  WHERE Year='2017-01-01' AND ENDS_WITH(GeoName, "MA") IS TRUE
),

earnings_diff AS (
  SELECT
    bea_2017.GeoFIPS, bea_2017.GeoName, bea_2017.earnings_2017, bea_2012.earnings_2012, 
    (bea_2017.earnings_2017 - bea_2012.earnings_2012) AS earnings_change
   FROM bea_2017 
   JOIN bea_2012
   ON bea_2017.GeoFIPS = bea_2012.GeoFIPS
)
 
SELECT * FROM earnings_diff WHERE earnings_change IS NOT NULL ORDER BY earnings_change DESC
```

## bq098.sql

```sql
WITH t2 AS
(
SELECT 
    t.*,
    t.pickup_location_id as pickup_zone_id,
    tz.borough as pickup_borough
FROM
(
SELECT *,
    TIMESTAMP_DIFF(dropoff_datetime,pickup_datetime,SECOND) as time_duration_in_secs,
    (CASE WHEN total_amount=0 THEN 0
    ELSE (tip_amount*100/total_amount) END) as tip_rate
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2016`
) t
INNER JOIN `bigquery-public-data.new_york_taxi_trips.taxi_zone_geom` tz
ON t.pickup_location_id = tz.zone_id
WHERE 
    pickup_datetime BETWEEN '2016-01-01' AND '2016-01-07' 
    AND dropoff_datetime BETWEEN '2016-01-01' AND '2016-01-07'
    AND TIMESTAMP_DIFF(dropoff_datetime,pickup_datetime,SECOND) > 0
    AND passenger_count > 0
    AND trip_distance >= 0 
    AND tip_amount >= 0 
    AND tolls_amount >= 0 
    AND mta_tax >= 0 
    AND fare_amount >= 0
    AND total_amount >= 0
),
t3 AS
(SELECT 
pickup_borough,
(CASE 
    WHEN tip_rate = 0 THEN 'no tip'
    WHEN tip_rate <= 5 THEN 'Less than 5%'
    WHEN tip_rate <= 10 THEN '5% to 10%'
    WHEN tip_rate <= 15 THEN '10% to 15%'
    WHEN tip_rate <= 20 THEN '15% to 20%'
    WHEN tip_rate <= 25 THEN '20% to 25%'
    ELSE 'More than 25%' END)as tip_category,
COUNT(*) as no_of_trips
FROM t2
GROUP BY 1,2
ORDER BY pickup_borough ASC),
INFO AS (
SELECT pickup_borough
     , tip_category
     , Sum(no_of_trips) as no_of_trips,
     (CASE 
          WHEN pickup_borough is null THEN (select sum(no_of_trips)
          FROM t3)
          
          WHEN pickup_borough is not null and tip_category is null THEN (select sum(no_of_trips)
          FROM t3)
          
          WHEN pickup_borough is not null and tip_category is not null THEN (select sum(no_of_trips)
          FROM t3
          WHERE pickup_borough = m.pickup_borough)
          END) as parent_sum,
       (
          Sum(no_of_trips)
            /
          (
            CASE 
          WHEN pickup_borough is null THEN (select sum(no_of_trips)
          FROM t3)
          
          WHEN pickup_borough is not null and tip_category is null THEN (select sum(no_of_trips)
          FROM t3)
          
          WHEN pickup_borough is not null and tip_category is not null THEN (select sum(no_of_trips)
          FROM t3
          WHERE pickup_borough = m.pickup_borough)
          END
          )
        ) as percentage
FROM t3 m
GROUP BY ROLLUP(pickup_borough, tip_category)
order by 1, 2
)

SELECT 
    pickup_borough,
    (SUM(CASE WHEN tip_category = 'no tip' THEN no_of_trips ELSE 0 END) * 100.0 / SUM(no_of_trips)) AS percentage_no_tip
FROM t3
GROUP BY pickup_borough
ORDER BY pickup_borough;

```

## bq102.sql

```sql
WITH gene_region AS (
  SELECT 
    MIN(start_position) AS start_pos, 
    MAX(end_position) AS end_pos
  FROM `bigquery-public-data.gnomAD.v2_1_1_genomes__chr17` AS main_table
  WHERE EXISTS (
    SELECT 1 
    FROM UNNEST(main_table.alternate_bases) AS alternate_bases
    WHERE EXISTS (
      SELECT 1 
      FROM UNNEST(alternate_bases.vep) AS vep
      WHERE vep.SYMBOL = 'BRCA1'
    )
  )
)


SELECT 
  DISTINCT start_position
FROM `bigquery-public-data.gnomAD.v2_1_1_genomes__chr17` AS main_table,
     UNNEST(main_table.alternate_bases) AS alternate_bases,
     UNNEST(alternate_bases.vep) AS vep,
     gene_region
WHERE main_table.start_position >= gene_region.start_pos
  AND main_table.start_position <= gene_region.end_pos
  AND REGEXP_CONTAINS(vep.Consequence, r"missense_variant")
  AND reference_bases = "C"
  AND alternate_bases.alt = "T"

```

## bq103.sql

```sql
WITH summary_stats AS (
  SELECT
    COUNT(1) AS num_variants,
    SUM((SELECT alt.AC FROM UNNEST(alternate_bases) AS alt)) AS sum_AC,
    SUM(AN) AS sum_AN,
    -- Also include some information from Variant Effect Predictor (VEP).
    STRING_AGG(DISTINCT (SELECT annot.symbol FROM UNNEST(alternate_bases) AS alt,
                                               UNNEST(vep) AS annot LIMIT 1), ', ') AS genes
  FROM bigquery-public-data.gnomAD.v3_genomes__chr1 AS main_table
  WHERE start_position >= 55039447 AND start_position <= 55064852
)
SELECT
  ROUND((55064852 - 55039447) / num_variants, 3) AS burden_of_mutation,
  *
FROM summary_stats;

```

## bq105.sql

```sql
SELECT * FROM
(
SELECT
  '2015' AS year,
  COUNT(a.consecutive_number) AS total,
  a.state_name AS state,
  c.state_pop AS population,
  (COUNT(a.consecutive_number) / c.state_pop * 100000) AS rate_per_100000
FROM
  `bigquery-public-data.nhtsa_traffic_fatalities.accident_2015` a
JOIN
  `bigquery-public-data.nhtsa_traffic_fatalities.distract_2015` b
ON
  a.consecutive_number = b.consecutive_number
JOIN (
  SELECT
    SUM(d.population) AS state_pop,
    e.state_name AS state
  FROM
    `bigquery-public-data.census_bureau_usa.population_by_zip_2010` d
  JOIN
    `bigquery-public-data.utility_us.zipcode_area` e
  ON
    d.zipcode = e.zipcode
  GROUP BY
    state ) c
ON
  c.state = a.state_name
WHERE
  b.driver_distracted_by_name NOT IN ('Not Distracted', 'Unknown if Distracted', 'Not Reported')
GROUP BY
  state,
  population,
  c.state_pop
ORDER BY
  rate_per_100000 DESC
LIMIT 5
)
UNION ALL
(
SELECT
  '2016' AS year,
  COUNT(a.consecutive_number) AS total,
  a.state_name AS state,
  c.state_pop AS population,
  (COUNT(a.consecutive_number) / c.state_pop * 100000) AS rate_per_100000
FROM
  `bigquery-public-data.nhtsa_traffic_fatalities.accident_2016` a
JOIN
  `bigquery-public-data.nhtsa_traffic_fatalities.distract_2016` b
ON
  a.consecutive_number = b.consecutive_number
JOIN (
  SELECT
    SUM(d.population) AS state_pop,
    e.state_name AS state
  FROM
    `bigquery-public-data.census_bureau_usa.population_by_zip_2010` d
  JOIN
    `bigquery-public-data.utility_us.zipcode_area` e
  ON
    d.zipcode = e.zipcode
  GROUP BY
    state ) c
ON
  c.state = a.state_name
WHERE
  b.driver_distracted_by_name NOT IN ('Not Distracted', 'Unknown if Distracted', 'Not Reported')
GROUP BY
  state,
  population,
  c.state_pop
ORDER BY
  rate_per_100000 DESC
LIMIT 5
)
```

## bq109.sql

```sql
WITH coloc_stats AS (
  SELECT
    coloc.coloc_log2_h4_h3,
    coloc.right_study AS qtl_source
  FROM
    `open-targets-genetics.genetics.variant_disease_coloc` AS coloc
  JOIN
    `open-targets-genetics.genetics.studies` AS studies
  ON
    coloc.left_study = studies.study_id
  WHERE
    coloc.right_gene_id = "ENSG00000169174"
    AND coloc.coloc_h4 > 0.8
    AND coloc.coloc_h3 < 0.02
    AND studies.trait_reported LIKE "%lesterol levels%"
    AND coloc.right_bio_feature = 'IPSC'
    AND CONCAT(coloc.left_chrom, '_', coloc.left_pos, '_', coloc.left_ref, '_', coloc.left_alt) = '1_55029009_C_T'
),
max_value AS (
  SELECT
    MAX(coloc_log2_h4_h3) AS max_log2_h4_h3
  FROM
    coloc_stats
)

SELECT
  AVG(coloc_log2_h4_h3) AS average,
  VAR_SAMP(coloc_log2_h4_h3) AS variance,
  MAX(coloc_log2_h4_h3) - MIN(coloc_log2_h4_h3) AS max_min_difference,
  (SELECT qtl_source FROM coloc_stats WHERE coloc_log2_h4_h3 = (SELECT max_log2_h4_h3 FROM max_value)) AS qtl_source_of_max
FROM
  coloc_stats;

```

## bq110.sql

```sql
WITH homeless_2012 AS (
  SELECT Homeless_Veterans AS Vet12, CoC_Name  
  FROM `bigquery-public-data.sdoh_hud_pit_homelessness.hud_pit_by_coc` 
  WHERE SUBSTR(CoC_Number,0,2) = "NY" AND Count_Year = 2012
),
 
homeless_2018 AS (
  SELECT Homeless_Veterans AS Vet18, CoC_Name  
  FROM `bigquery-public-data.sdoh_hud_pit_homelessness.hud_pit_by_coc` 
  WHERE SUBSTR(CoC_Number,0,2) = "NY" AND Count_Year = 2018
),
 
veterans_change AS (
  SELECT homeless_2012.COC_Name, Vet12, Vet18, Vet18 - Vet12 AS VetChange
  FROM homeless_2018
  JOIN homeless_2012
  ON homeless_2018.CoC_Name = homeless_2012.CoC_Name
)

SELECT COC_Name, VetChange FROM veterans_change
ORDER BY CoC_Name;

```

## bq112.sql

```sql
WITH geo AS (
  SELECT DISTINCT geo_id
  FROM `bigquery-public-data.geo_us_boundaries.counties`
  WHERE county_name = "Allegheny" 
),
avg_wage_1998 AS(
  SELECT
    ROUND(AVG(avg_wkly_wage_10_total_all_industries) * 52, 2) AS wages_1998
  FROM
    `bigquery-public-data.bls_qcew.1998*`
  WHERE
    geoid = (SELECT geo_id FROM geo) --Selecting Allgeheny County
),
    
avg_wage_2017 AS (
  SELECT
    ROUND(AVG(avg_wkly_wage_10_total_all_industries) * 52, 2) AS wages_2017
  FROM
    `bigquery-public-data.bls_qcew.2017*`
  WHERE
    geoid = (SELECT geo_id FROM geo) --Selecting Allgeheny County
),

avg_cpi_1998 AS (
  SELECT
    AVG(value) AS cpi_1998
  FROM
    `bigquery-public-data.bls.cpi_u` c
  WHERE
    year = 1998
    AND item_code in (
      SELECT DISTINCT item_code FROM `bigquery-public-data.bls.cpi_u` WHERE LOWER(item_name) = "all items"
    )
    AND area_code = (
      SELECT DISTINCT area_code FROM `bigquery-public-data.bls.cpi_u` WHERE area_name LIKE '%Pittsburgh%'
    )
), 
-- A104 is the code for Pittsburgh, PA
-- SA0 is the code for all items
    
avg_cpi_2017 AS(
  SELECT
    AVG(value) AS cpi_2017
  FROM
    `bigquery-public-data.bls.cpi_u` c
  WHERE
    year = 2017
    AND item_code in (
      SELECT DISTINCT item_code FROM `bigquery-public-data.bls.cpi_u` WHERE LOWER(item_name) = "all items"
    )
    AND area_code = (
      SELECT DISTINCT area_code FROM `bigquery-public-data.bls.cpi_u` WHERE area_name LIKE '%Pittsburgh%'
    )
)
-- A104 is the code for Pittsburgh, PA
-- SA0 is the code for all items

SELECT
  ROUND((wages_2017 - wages_1998) / wages_1998 * 100, 2) AS wages_percent_change,
  ROUND((cpi_2017 - cpi_1998) / cpi_1998 * 100, 2) AS cpi_percent_change
FROM
  avg_wage_2017,
  avg_wage_1998,
  avg_cpi_2017,
  avg_cpi_1998
```

## bq113.sql

```sql
WITH utah_code AS (
  SELECT DISTINCT geo_id
  FROM bigquery-public-data.geo_us_boundaries.states
  WHERE state_name = 'Utah'
),
e2000 as(
  SELECT
    AVG(month3_emplvl_23_construction) AS construction_employees_2000,
    geoid
  FROM
    `bigquery-public-data.bls_qcew.2000_*`
  WHERE
    geoid LIKE CONCAT((SELECT geo_id FROM utah_code), '%')
  GROUP BY
    geoid),

e2018 AS (
  SELECT
    AVG(month3_emplvl_23_construction) AS construction_employees_2018,
    geoid,
  FROM
    `bigquery-public-data.bls_qcew.2018_*` e2018
  WHERE
    geoid LIKE CONCAT((SELECT geo_id FROM utah_code), '%')
  GROUP BY
    geoid)

SELECT
  c.county_name AS county,
  (construction_employees_2018 - construction_employees_2000) / construction_employees_2000 * 100 AS increase_rate
FROM
  e2000
JOIN
  e2018 USING (geoid)
JOIN 
  `bigquery-public-data.geo_us_boundaries.counties` c ON c.geo_id = e2018.geoid
WHERE
  c.state_fips_code = (SELECT geo_id FROM utah_code)
ORDER BY
  increase_rate desc
LIMIT 1
```

## bq114.sql

```sql
SELECT
  aq.city,
  epa.arithmetic_mean,
  aq.value,
  aq.timestamp,
  (epa.arithmetic_mean - aq.value)
FROM
  `bigquery-public-data.openaq.global_air_quality` AS aq
JOIN
  `bigquery-public-data.epa_historical_air_quality.air_quality_annual_summary` AS epa
ON
  ROUND(aq.latitude, 2) = ROUND(epa.latitude, 2)
  AND ROUND(aq.longitude, 2) = ROUND(epa.longitude, 2)
WHERE
  epa.units_of_measure = "Micrograms/cubic meter (LC)"
  AND epa.parameter_name = "Acceptable PM2.5 AQI & Speciation Mass"
  AND epa.year = 1990
  AND aq.pollutant = "pm25"
  AND EXTRACT(YEAR FROM aq.timestamp) = 2020
ORDER BY
  (epa.arithmetic_mean - aq.value) DESC
LIMIT 3




```

## bq115.sql

```sql
SELECT
country_name
FROM
(SELECT
  age.country_name,
  SUM(age.population) AS under_25,
  pop.midyear_population AS total,
  ROUND((SUM(age.population) / pop.midyear_population) * 100,2) AS pct_under_25
FROM (
  SELECT
    country_name,
    population,
    country_code
  FROM
    `bigquery-public-data.census_bureau_international.midyear_population_agespecific`
  WHERE
    year =2017
    AND age < 25) age
INNER JOIN (
  SELECT
    midyear_population,
    country_code
  FROM
    `bigquery-public-data.census_bureau_international.midyear_population`
  WHERE
    year = 2017) pop
ON
  age.country_code = pop.country_code
GROUP BY
  1,
  3
ORDER BY
  4 DESC
)
LIMIT
1
```

## bq119.sql

```sql
WITH hurricane_geometry AS (
  SELECT
    * EXCEPT (longitude, latitude),
    ST_GEOGPOINT(longitude, latitude) AS geom,
  FROM
    `bigquery-public-data.noaa_hurricanes.hurricanes`
  WHERE
    season = '2020'
    AND basin = 'NA'
    AND name != 'NOT NAMED'
),
dist_between_points AS (
  SELECT
    sid,
    name,
    season,
    iso_time,
    usa_wind,
    geom,
    ST_DISTANCE(geom, LAG(geom, 1) OVER (PARTITION BY sid ORDER BY iso_time ASC)) / 1000 AS dist
  FROM
    hurricane_geometry
),
total_distances AS (
  SELECT
    sid,
    name,
    season,
    iso_time,
    usa_wind,
    geom,
    SUM(dist) OVER (PARTITION BY sid ORDER BY iso_time ASC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_distance,
    SUM(dist) OVER (PARTITION BY sid) AS total_dist
  FROM
    dist_between_points
),
ranked_hurricanes AS (
  SELECT
    *,
    DENSE_RANK() OVER (ORDER BY total_dist DESC) AS dense_rank
  FROM
    total_distances
)

SELECT
  geom,cumulative_distance,usa_wind
FROM
  ranked_hurricanes
WHERE
  dense_rank = 3
ORDER BY
cumulative_distance;

```

## bq120.sql

```sql
WITH acs_2017 AS (
  SELECT geo_id, income_less_10000 AS i10, income_10000_14999 AS i15, income_15000_19999 AS i20
  FROM `bigquery-public-data.census_bureau_acs.county_2017_5yr`
 ),

snap_2017_Jan AS (
  SELECT FIPS, SNAP_All_Participation_Households AS snap_total
  FROM `bigquery-public-data.sdoh_snap_enrollment.snap_enrollment`
  WHERE Date = '2017-01-01'
)

SELECT acs_2017.geo_id, snap_2017_Jan.snap_total,
(acs_2017.i10 + acs_2017.i15 + acs_2017.i20) As households_under_20,
(acs_2017.i10 + acs_2017.i15 + acs_2017.i20)/snap_2017_Jan.snap_total As under_20_snap_ratio 
FROM acs_2017
JOIN snap_2017_Jan
ON  acs_2017.geo_id = snap_2017_Jan.FIPS
WHERE snap_2017_Jan.snap_total > 0
ORDER BY snap_2017_Jan.snap_total DESC
LIMIT 10

```

## bq123.sql

```sql
WITH first_answers AS (
  SELECT
    parent_id AS question_id,
    MIN(creation_date) AS first_answer_date
  FROM
    `bigquery-public-data.stackoverflow.posts_answers`
  GROUP BY
    parent_id
)

SELECT
  FORMAT_DATE('%A', DATE(q.creation_date)) AS question_day,
  SUM(CASE WHEN f.first_answer_date IS NOT NULL AND TIMESTAMP_DIFF(f.first_answer_date, q.creation_date, MINUTE) <= 60 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS percent_questions
FROM
  `bigquery-public-data.stackoverflow.posts_questions` q
LEFT JOIN
  first_answers f
ON
  q.id = f.question_id
GROUP BY
  question_day
ORDER BY
  percent_questions DESC
LIMIT 1 OFFSET 2
```

## bq124.sql

```sql
With INFO AS (
SELECT 
  MR.patientId, 
  P.last_name,
  ARRAY_TO_STRING(P.first_name, " ") AS First_name,
  Condition.Codes, 
  Condition.Conditions,
  MR.med_count AS COUNT_NUMBER
FROM
  (SELECT 
    id, 
    name[safe_offset(0)].family as last_name, 
    name[safe_offset(0)].given as first_name, 
    TIMESTAMP(deceased.dateTime) AS deceased_datetime 
  FROM `bigquery-public-data.fhir_synthea.patient`) AS P
JOIN
  (SELECT  subject.patientId as patientId, 
           COUNT(DISTINCT medication.codeableConcept.coding[safe_offset(0)].code) AS med_count
   FROM    `bigquery-public-data.fhir_synthea.medication_request`
   WHERE   status = 'active'
   GROUP BY 1
   ) AS MR
ON MR.patientId = P.id 
JOIN
  (SELECT 
  PatientId, 
  STRING_AGG(DISTINCT condition_desc, ", ") AS Conditions, 
  STRING_AGG(DISTINCT condition_code, ", ") AS Codes
  FROM(
    SELECT 
      subject.patientId as PatientId, 
              code.coding[safe_offset(0)].code condition_code,
              code.coding[safe_offset(0)].display condition_desc
       FROM `bigquery-public-data.fhir_synthea.condition`
       wHERE 
         code.coding[safe_offset(0)].display = 'Diabetes'
         OR 
         code.coding[safe_offset(0)].display = 'Hypertension' 
    )
  GROUP BY PatientId
  ) AS Condition
ON MR.patientId = Condition.PatientId
WHERE med_count >= 7 
AND P.deceased_datetime is NULL /*only alive patients*/
GROUP BY patientId, last_name, first_name, Condition.Codes, Condition.Conditions, MR.med_count
ORDER BY last_name
)

SELECT COUNT(*) FROM INFO
```

## bq126.sql

```sql
SELECT
  o.artist_display_name,
  o.title,
  o.object_end_date,
  o.medium,
  i.original_image_url
FROM (
  SELECT
    object_id,
    title,
    artist_display_name,
    object_end_date,
    medium
  FROM
    `bigquery-public-data.the_met.objects`
  WHERE
    department = "Photographs"
    AND object_name LIKE "%Photograph%"
    AND artist_display_name != "Unknown"
    AND object_end_date <= 1839
) o
INNER JOIN (
  SELECT
    original_image_url,
    object_id
  FROM
    `bigquery-public-data.the_met.images`
) i
ON
  o.object_id = i.object_id
ORDER BY
  o.object_end_date
;

```

## bq130.sql

```sql
WITH StateCases AS (
    SELECT
        b.state_name,
        b.date,
        b.confirmed_cases - a.confirmed_cases AS daily_new_cases
    FROM 
        (SELECT
            state_name,
            state_fips_code,
            confirmed_cases,
            DATE_ADD(date, INTERVAL 1 DAY) AS date_shift
        FROM
            `bigquery-public-data.covid19_nyt.us_states`
        WHERE
            date >= '2020-02-29' AND date <= '2020-05-30'
        ) a
    JOIN
        `bigquery-public-data.covid19_nyt.us_states` b 
        ON a.state_fips_code = b.state_fips_code AND a.date_shift = b.date
    WHERE
        b.date >= '2020-03-01' AND b.date <= '2020-05-31'
),
RankedStatesPerDay AS (
    SELECT
        state_name,
        date,
        daily_new_cases,
        RANK() OVER (PARTITION BY date ORDER BY daily_new_cases DESC) as rank
    FROM
        StateCases
),
TopStates AS (
    SELECT
        state_name,
        COUNT(*) AS appearance_count
    FROM
        RankedStatesPerDay
    WHERE
        rank <= 5
    GROUP BY
        state_name
    ORDER BY
        appearance_count DESC
),
FourthState AS (
    SELECT
        state_name
    FROM
        TopStates
    LIMIT 1
    OFFSET 3
),
CountyCases AS (
    SELECT
        b.county,
        b.date,
        b.confirmed_cases - a.confirmed_cases AS daily_new_cases
    FROM 
        (SELECT
            county,
            county_fips_code,
            confirmed_cases,
            DATE_ADD(date, INTERVAL 1 DAY) AS date_shift
        FROM
            `bigquery-public-data.covid19_nyt.us_counties`
        WHERE
            date >= '2020-02-29' AND date <= '2020-05-30'
        ) a
    JOIN
        `bigquery-public-data.covid19_nyt.us_counties` b 
        ON a.county_fips_code = b.county_fips_code AND a.date_shift = b.date
    WHERE
        b.date >= '2020-03-01' AND b.date <= '2020-05-31'
        AND b.state_name = (SELECT state_name FROM FourthState)
),
RankedCountiesPerDay AS (
    SELECT
        county,
        date,
        daily_new_cases,
        RANK() OVER (PARTITION BY date ORDER BY daily_new_cases DESC) as rank
    FROM
        CountyCases
),
TopCounties AS (
    SELECT
        county,
        COUNT(*) AS appearance_count
    FROM
        RankedCountiesPerDay
    WHERE
        rank <= 5
    GROUP BY
        county
    ORDER BY
        appearance_count DESC
    LIMIT 5
)
SELECT
    county
FROM
    TopCounties;

```

## bq143.sql

```sql
WITH 
quant AS (
    SELECT 
        meta.sample_submitter_id, 
        meta.sample_type, 
        quant.case_id, 
        quant.aliquot_id, 
        quant.gene_symbol, 
        CAST(quant.protein_abundance_log2ratio AS FLOAT64) AS protein_abundance_log2ratio 
    FROM 
        `isb-cgc-bq.CPTAC.quant_proteome_CPTAC_CCRCC_discovery_study_pdc_current` AS quant
    JOIN 
        `isb-cgc-bq.PDC_metadata.aliquot_to_case_mapping_current` AS meta
        ON quant.case_id = meta.case_id
        AND quant.aliquot_id = meta.aliquot_id
        AND meta.sample_type IN ('Primary Tumor', 'Solid Tissue Normal')
),
gexp AS (
    SELECT DISTINCT 
        meta.sample_submitter_id, 
        meta.sample_type, 
        rnaseq.gene_name, 
        LOG(rnaseq.fpkm_unstranded + 1) AS HTSeq__FPKM   -- Confirm the correct column name here
    FROM 
        `isb-cgc-bq.CPTAC.RNAseq_hg38_gdc_current` AS rnaseq
    JOIN 
        `isb-cgc-bq.PDC_metadata.aliquot_to_case_mapping_current` AS meta
        ON meta.sample_submitter_id = rnaseq.sample_barcode
),
correlation AS (
    SELECT 
        quant.gene_symbol, 
        gexp.sample_type, 
        COUNT(*) AS n, 
        CORR(protein_abundance_log2ratio, HTSeq__FPKM) AS corr  -- Confirm the correct column name here
    FROM 
        quant 
    JOIN 
        gexp 
        ON quant.sample_submitter_id = gexp.sample_submitter_id
        AND gexp.gene_name = quant.gene_symbol
        AND gexp.sample_type = quant.sample_type
    GROUP BY 
        quant.gene_symbol, gexp.sample_type
),
pval AS (
    SELECT  
        gene_symbol, 
        sample_type, 
        n, 
        corr
    FROM 
        correlation
    WHERE 
        ABS(corr) <= 0.5
)
SELECT sample_type, AVG(corr)
FROM pval
GROUP BY sample_type;

```

## bq144.sql

```sql
WITH outcomes AS (
SELECT

  season, # 1994
  "win" AS label, # our label
  win_seed AS seed, # ranking # this time without seed even
  win_school_ncaa AS school_ncaa,
  lose_seed AS opponent_seed, # ranking
  lose_school_ncaa AS opponent_school_ncaa
FROM `data-to-insights.ncaa.mbb_historical_tournament_games` t
WHERE season >= 2014
UNION ALL

SELECT

  season, # 1994
  "loss" AS label, # our label
  lose_seed AS seed, # ranking
  lose_school_ncaa AS school_ncaa,
  win_seed AS opponent_seed, # ranking
  win_school_ncaa AS opponent_school_ncaa
FROM
`data-to-insights.ncaa.mbb_historical_tournament_games` t
WHERE season >= 2014
UNION ALL

SELECT
  season,
  label,
  seed,
  school_ncaa,
  opponent_seed,
  opponent_school_ncaa
FROM
  `data-to-insights.ncaa.2018_tournament_results`
)
SELECT
o.season,
label,
  seed,
  school_ncaa,
  team.pace_rank,
  team.poss_40min,
  team.pace_rating,
  team.efficiency_rank,
  team.pts_100poss,
  team.efficiency_rating,
  opponent_seed,
  opponent_school_ncaa,
  opp.pace_rank AS opp_pace_rank,
  opp.poss_40min AS opp_poss_40min,
  opp.pace_rating AS opp_pace_rating,
  opp.efficiency_rank AS opp_efficiency_rank,
  opp.pts_100poss AS opp_pts_100poss,
  opp.efficiency_rating AS opp_efficiency_rating,
  opp.pace_rank - team.pace_rank AS pace_rank_diff,
  opp.poss_40min - team.poss_40min AS pace_stat_diff,
  opp.pace_rating - team.pace_rating AS pace_rating_diff,
  opp.efficiency_rank - team.efficiency_rank AS eff_rank_diff,
  opp.pts_100poss - team.pts_100poss AS eff_stat_diff,
  opp.efficiency_rating - team.efficiency_rating AS eff_rating_diff
FROM outcomes AS o
LEFT JOIN `data-to-insights.ncaa.feature_engineering` AS team
ON o.school_ncaa = team.team AND o.season = team.season
LEFT JOIN `data-to-insights.ncaa.feature_engineering` AS opp
ON o.opponent_school_ncaa = opp.team AND o.season = opp.season
```

## bq151.sql

```sql
WITH
barcodes AS (
   SELECT bcr_patient_barcode AS ParticipantBarcode
   FROM isb-cgc-bq.pancancer_atlas.Filtered_clinical_PANCAN_patient_with_followup
   WHERE acronym = 'PAAD'
),
table1 AS (
SELECT
   t1.ParticipantBarcode,
   IF(t2.ParticipantBarcode IS NULL, 'NO', 'YES') AS data
FROM
   barcodes AS t1
LEFT JOIN
   (
   SELECT
      ParticipantBarcode AS ParticipantBarcode
   FROM isb-cgc-bq.pancancer_atlas.Filtered_MC3_MAF_V5_one_per_tumor_sample
   WHERE Study = 'PAAD' AND Hugo_Symbol = 'KRAS'
         AND FILTER = 'PASS'
   GROUP BY ParticipantBarcode
   ) AS t2
ON t1.ParticipantBarcode = t2.ParticipantBarcode
),
table2 AS (
SELECT
   t1.ParticipantBarcode,
   IF(t2.ParticipantBarcode IS NULL, 'NO', 'YES') AS data
FROM
   barcodes AS t1
LEFT JOIN
   (
   SELECT
      ParticipantBarcode AS ParticipantBarcode
   FROM isb-cgc-bq.pancancer_atlas.Filtered_MC3_MAF_V5_one_per_tumor_sample
   WHERE Study = 'PAAD' AND Hugo_Symbol = 'TP53'
         AND FILTER = 'PASS'
   GROUP BY ParticipantBarcode
   ) AS t2
ON t1.ParticipantBarcode = t2.ParticipantBarcode
),
summ_table AS (
SELECT
   n1.data AS data1,
   n2.data AS data2,
   COUNT(*) AS Nij
FROM
   table1 AS n1
INNER JOIN
   table2 AS n2
ON
   n1.ParticipantBarcode = n2.ParticipantBarcode
GROUP BY
  data1, data2
),
contingency_table AS (
SELECT
  MAX(IF((data1 = 'YES') AND (data2 = 'YES'), Nij, 0)) AS a,
  MAX(IF((data1 = 'YES') AND (data2 = 'NO'), Nij, 0)) AS b,
  MAX(IF((data1 = 'NO') AND (data2 = 'YES'), Nij, 0)) AS c,
  MAX(IF((data1 = 'NO') AND (data2 = 'NO'), Nij, 0)) AS d,
  (MAX(IF((data1 = 'YES') AND (data2 = 'YES'), Nij, 0)) + MAX(IF((data1 = 'YES') AND (data2 = 'NO'), Nij, 0))) AS row1_total,
  (MAX(IF((data1 = 'NO') AND (data2 = 'YES'), Nij, 0)) + MAX(IF((data1 = 'NO') AND (data2 = 'NO'), Nij, 0))) AS row2_total,
  (MAX(IF((data1 = 'YES') AND (data2 = 'YES'), Nij, 0)) + MAX(IF((data1 = 'NO') AND (data2 = 'YES'), Nij, 0))) AS col1_total,
  (MAX(IF((data1 = 'YES') AND (data2 = 'NO'), Nij, 0)) + MAX(IF((data1 = 'NO') AND (data2 = 'NO'), Nij, 0))) AS col2_total,
  SUM(Nij) AS grand_total
FROM summ_table
)
SELECT
  POWER((a - (row1_total * col1_total) / grand_total), 2) / ((row1_total * col1_total) / grand_total) +
  POWER((b - (row1_total * col2_total) / grand_total), 2) / ((row1_total * col2_total) / grand_total) +
  POWER((c - (row2_total * col1_total) / grand_total), 2) / ((row2_total * col1_total) / grand_total) +
  POWER((d - (row2_total * col2_total) / grand_total), 2) / ((row2_total * col2_total) / grand_total) AS chi_square_statistic
FROM contingency_table
WHERE a IS NOT NULL AND b IS NOT NULL AND c IS NOT NULL AND d IS NOT NULL;

```

## bq161.sql

```sql
WITH
barcodes AS (
   SELECT bcr_patient_barcode AS ParticipantBarcode
   FROM `isb-cgc-bq.pancancer_atlas.Filtered_clinical_PANCAN_patient_with_followup`
   WHERE acronym = 'PAAD'
)
,table1 AS (
SELECT
   t1.ParticipantBarcode,
   IF( t2.ParticipantBarcode is null, 'NO', 'YES') as data
FROM
   barcodes AS t1
LEFT JOIN
   (
   SELECT
      ParticipantBarcode AS ParticipantBarcode
   FROM `isb-cgc-bq.pancancer_atlas.Filtered_MC3_MAF_V5_one_per_tumor_sample`
   WHERE Study = 'PAAD' AND Hugo_Symbol = 'KRAS'
         AND FILTER = 'PASS'
   GROUP BY ParticipantBarcode
   ) AS t2
ON t1.ParticipantBarcode = t2.ParticipantBarcode
)
,table2 AS (
SELECT
   t1.ParticipantBarcode,
   IF( t2.ParticipantBarcode is null, 'NO', 'YES') as data
FROM
   barcodes AS t1
LEFT JOIN
   (
   SELECT
      ParticipantBarcode AS ParticipantBarcode
   FROM `isb-cgc-bq.pancancer_atlas.Filtered_MC3_MAF_V5_one_per_tumor_sample`
   WHERE Study = 'PAAD' AND Hugo_Symbol = 'TP53'
         AND FILTER = 'PASS'
   GROUP BY ParticipantBarcode
   ) AS t2
ON t1.ParticipantBarcode = t2.ParticipantBarcode
),

INFO AS (
SELECT
   n1.data as data1,
   n2.data as data2,
   COUNT(*) as Nij
FROM
   table1 AS n1
INNER JOIN
   table2 AS n2
ON
   n1.ParticipantBarcode = n2.ParticipantBarcode
GROUP BY
  data1, data2
)

SELECT 
(SELECT Nij FROM INFO WHERE data1="YES" AND data2="YES")
-
(SELECT Nij FROM INFO WHERE data1="NO" AND data2="NO")


```

## bq172.sql

```sql
WITH ny_top_drug AS (
  SELECT
    drug_name AS drug_name,
    ROUND(SUM(total_claim_count)) AS total_claim_count
  FROM
    `bigquery-public-data.cms_medicare.part_d_prescriber_2014`
  WHERE
    nppes_provider_state = 'NY'
  GROUP BY
    drug_name
  ORDER BY
    total_claim_count DESC
  LIMIT 1
),
top_5_states AS (
  SELECT
    nppes_provider_state AS state,
    SUM(total_claim_count) AS total_claim_count,
    SUM(total_drug_cost) AS total_drug_cost
  FROM
    `bigquery-public-data.cms_medicare.part_d_prescriber_2014`
  WHERE
    drug_name = (SELECT drug_name FROM ny_top_drug)
  GROUP BY
    state
  ORDER BY
    total_claim_count DESC
  LIMIT 5
)
SELECT
  state,
  total_claim_count,
  total_drug_cost
FROM
  top_5_states;

```

## bq185.sql

```sql
SELECT 
    AVG(TIMESTAMP_DIFF(dropoff_datetime, pickup_datetime, SECOND) / 60.0) AS average_trip_duration_in_minutes
FROM
(
    SELECT *
    FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2016` t
    WHERE 
        pickup_datetime BETWEEN '2016-02-01' AND '2016-02-07' AND 
        dropoff_datetime BETWEEN '2016-02-01' AND '2016-02-07' AND
        TIMESTAMP_DIFF(dropoff_datetime, pickup_datetime, SECOND) > 0 AND 
        passenger_count > 3 AND 
        trip_distance >= 10
) t
INNER JOIN `bigquery-public-data.new_york_taxi_trips.taxi_zone_geom` tz
ON t.pickup_location_id = tz.zone_id
INNER JOIN `bigquery-public-data.new_york_taxi_trips.taxi_zone_geom` tz1
ON t.dropoff_location_id = tz1.zone_id
WHERE 
    tz.borough = "Brooklyn" AND
    tz1.borough = "Brooklyn";

```

## bq198.sql

```sql
SELECT
  team_name,
  COUNT(*) AS top_performer_count
FROM (
  SELECT
    DISTINCT c2.season,
    c2.market AS team_name
  FROM (
    SELECT
      season AS a,
      MAX(wins) AS win_max
    FROM
      `bigquery-public-data.ncaa_basketball.mbb_historical_teams_seasons`
    WHERE
      season<=2000
      AND season >=1900
    GROUP BY
      season ),
    `bigquery-public-data.ncaa_basketball.mbb_historical_teams_seasons` c2
  WHERE
    win_max = c2.wins
    AND a = c2.season
    AND c2.market IS NOT NULL
  ORDER BY
    c2.season)
GROUP BY
  team_name
ORDER BY
  top_performer_count DESC,
  team_name
LIMIT
  5
```

## bq199.sql

```sql
WITH price_2020 AS (
  SELECT 
    category_name AS category, 
    AVG(state_bottle_retail / (bottle_volume_ml / 1000)) AS avg_price_liter_2020
  FROM 
    `bigquery-public-data.iowa_liquor_sales.sales`
  WHERE 
    bottle_volume_ml > 0 
    AND EXTRACT(YEAR FROM date) = 2020
  GROUP BY 
    category
),
price_2019 AS (
  SELECT 
    category_name AS category, 
    AVG(state_bottle_retail / (bottle_volume_ml / 1000)) AS avg_price_liter_2019
  FROM 
    `bigquery-public-data.iowa_liquor_sales.sales`
  WHERE 
    bottle_volume_ml > 0 
    AND EXTRACT(YEAR FROM date) = 2019
  GROUP BY 
    category
),
price_2021 AS (
  SELECT 
    category_name AS category, 
    AVG(state_bottle_retail / (bottle_volume_ml / 1000)) AS avg_price_liter_2021
  FROM 
    `bigquery-public-data.iowa_liquor_sales.sales`
  WHERE 
    bottle_volume_ml > 0 
    AND EXTRACT(YEAR FROM date) = 2021
  GROUP BY 
    category
)
SELECT 
  price_2021.category, 
  price_2019.avg_price_liter_2019, 
  price_2020.avg_price_liter_2020, 
  price_2021.avg_price_liter_2021
FROM 
  price_2021
LEFT JOIN 
  price_2019 ON price_2021.category = price_2019.category
LEFT JOIN 
  price_2020 ON price_2021.category = price_2020.category
ORDER BY 
  price_2021.avg_price_liter_2021 DESC
LIMIT 
  10;

```

## bq203.sql

```sql
WITH stations_n_entrances AS (
      SELECT borough_name,s.station_name,entry,ada_compliant
      FROM `bigquery-public-data.new_york_subway.stations` s
      JOIN `bigquery-public-data.new_york_subway.station_entrances` se
      ON s.station_name = se.station_name
      )

SELECT se.borough_name, COUNT(DISTINCT se.station_name) num_stations,
      COUNT(DISTINCT adas.station_name) num_stations_w_compliant_entrance, 
      (100*COUNT(DISTINCT adas.station_name))/(COUNT(DISTINCT se.station_name)) percent_compliant_stations
FROM `stations_n_entrances` se
LEFT JOIN `stations_n_entrances` adas
ON se.station_name = adas.station_name
AND adas.entry AND adas.ada_compliant
GROUP BY 1
ORDER BY 4 DESC
```

## bq204.sql

```sql
SELECT user
FROM (
Select user
      From `bigquery-public-data.eclipse_megamovie.photos_v_0_1`
      UNION ALL
      Select user
      From`bigquery-public-data.eclipse_megamovie.photos_v_0_2`
      UNION ALL
      Select user
      From`bigquery-public-data.eclipse_megamovie.photos_v_0_3`
) 
GROUP BY user 
HAVING COUNT (user)=( 
SELECT MAX(mycount) 
FROM ( 
SELECT user, COUNT(user) mycount 
FROM (
Select user
      From `bigquery-public-data.eclipse_megamovie.photos_v_0_1`
      UNION ALL
      Select user
      From`bigquery-public-data.eclipse_megamovie.photos_v_0_2`
      UNION ALL
      Select user
      From`bigquery-public-data.eclipse_megamovie.photos_v_0_3`
)
GROUP BY user))
ORDER BY COUNT(user) 
LIMIT 1
```

## bq218.sql

```sql
WITH AnnualSales AS (
  SELECT
    item_description,
    EXTRACT(YEAR FROM date) AS year,
    SUM(sale_dollars) AS total_sales_revenue,
    COUNT(DISTINCT invoice_and_item_number) AS unique_purchases
  FROM
    `bigquery-public-data.iowa_liquor_sales.sales`
  WHERE
    EXTRACT(YEAR FROM date) IN (2022, 2023)
    AND item_description IS NOT NULL
    AND sale_dollars IS NOT NULL
  GROUP BY
    item_description, year
),
YoYGrowth AS (
  SELECT
    curr.item_description,
    curr.year,
    curr.total_sales_revenue,
    curr.unique_purchases,
    LAG(curr.total_sales_revenue) OVER(PARTITION BY curr.item_description ORDER BY curr.year) AS prev_year_sales_revenue,
    (curr.total_sales_revenue - LAG(curr.total_sales_revenue) OVER(PARTITION BY curr.item_description ORDER BY curr.year)) / LAG(curr.total_sales_revenue) OVER(PARTITION BY curr.item_description ORDER BY curr.year) * 100 AS yoy_growth_percentage
  FROM
    AnnualSales curr
),
total_info AS (
SELECT
  item_description,
  year,
  total_sales_revenue,
  unique_purchases,
  prev_year_sales_revenue,
  yoy_growth_percentage
FROM
  YoYGrowth
WHERE
  year = 2023
  AND prev_year_sales_revenue IS NOT NULL -- Exclude rows where there's no previous year data to calculate YoY growth
ORDER BY
  year, total_sales_revenue 
DESC
)

SELECT item_description
FROM total_info
order by yoy_growth_percentage
DESC
LIMIT 5
```

## bq227.sql

```sql
WITH top5_categories AS (
  SELECT minor_category
  FROM `bigquery-public-data.london_crime.crime_by_lsoa`
  WHERE year = 2008
  GROUP BY minor_category
  ORDER BY SUM(value) DESC
  LIMIT 5
),

total_crimes_per_year AS (
  SELECT 
    year, 
    SUM(value) AS total_crimes_year
  FROM `bigquery-public-data.london_crime.crime_by_lsoa`
  GROUP BY year
),

top5_crimes_per_year AS (
  SELECT
    year,
    minor_category,
    SUM(value) AS total_crimes_category_year
  FROM `bigquery-public-data.london_crime.crime_by_lsoa`
  WHERE minor_category IN (SELECT minor_category FROM top5_categories)
  GROUP BY year, minor_category
)

SELECT
  t.year,
  ROUND(SUM(CASE WHEN t.minor_category = (SELECT minor_category FROM top5_categories LIMIT 1 OFFSET 0) THEN t.total_crimes_category_year ELSE 0 END) / y.total_crimes_year * 100, 2) AS `Category 1`,
  ROUND(SUM(CASE WHEN t.minor_category = (SELECT minor_category FROM top5_categories LIMIT 1 OFFSET 1) THEN t.total_crimes_category_year ELSE 0 END) / y.total_crimes_year * 100, 2) AS `Category 2`,
  ROUND(SUM(CASE WHEN t.minor_category = (SELECT minor_category FROM top5_categories LIMIT 1 OFFSET 2) THEN t.total_crimes_category_year ELSE 0 END) / y.total_crimes_year * 100, 2) AS `Category 3`,
  ROUND(SUM(CASE WHEN t.minor_category = (SELECT minor_category FROM top5_categories LIMIT 1 OFFSET 3) THEN t.total_crimes_category_year ELSE 0 END) / y.total_crimes_year * 100, 2) AS `Category 4`,
  ROUND(SUM(CASE WHEN t.minor_category = (SELECT minor_category FROM top5_categories LIMIT 1 OFFSET 4) THEN t.total_crimes_category_year ELSE 0 END) / y.total_crimes_year * 100, 2) AS `Category 5`
FROM
  top5_crimes_per_year t
JOIN
  total_crimes_per_year y ON t.year = y.year
GROUP BY
  t.year, y.total_crimes_year
ORDER BY
  t.year;

```

## bq228.sql

```sql
WITH ranked_crimes AS (
    SELECT
        borough,
        major_category,
        RANK() OVER(PARTITION BY borough ORDER BY SUM(value) DESC) AS rank_per_borough,
        SUM(value) AS no_of_incidents
    FROM
        `bigquery-public-data.london_crime.crime_by_lsoa`
    GROUP BY
        borough,
        major_category
)

SELECT
    borough,
    major_category,
    rank_per_borough,
    no_of_incidents
FROM
    ranked_crimes
WHERE
    rank_per_borough <= 3
AND 
    borough = 'Barking and Dagenham'
ORDER BY
    borough,
    rank_per_borough;

```

## bq232.sql

```sql
WITH borough_data AS (
    SELECT 
        year, 
        month, 
        borough, 
        major_category, 
        minor_category, 
        SUM(value) AS total,
    CASE 
        WHEN 
            major_category = 'Theft and Handling' 
        THEN 
            'Theft and Handling'
        ELSE 
            'Other' 
    END AS major_division,
    CASE 
        WHEN 
            minor_category = 'Other Theft' THEN minor_category
        ELSE 
            'Other'
    END AS minor_division,
    FROM 
        bigquery-public-data.london_crime.crime_by_lsoa
    GROUP BY 1,2,3,4,5
    ORDER BY 1,2
)

SELECT year, SUM(total) AS year_total
FROM borough_data
WHERE 
    borough = 'Westminster'
AND
    major_division != 'Other'
AND 
    minor_division != 'Other'
GROUP BY year, major_division, minor_division
ORDER BY year;

```

## bq234.sql

```sql
SELECT
  A.state,
  drug_name,
  total_claim_count
FROM (
  SELECT
    generic_name AS drug_name,
    nppes_provider_state AS state,
    ROUND(SUM(total_claim_count)) AS total_claim_count,
    ROUND(SUM(total_day_supply)) AS day_supply,
    ROUND(SUM(total_drug_cost)) / 1e6 AS total_cost_millions
  FROM
    `bigquery-public-data.cms_medicare.part_d_prescriber_2014`
  GROUP BY
    state,
    drug_name) A
INNER JOIN (
  SELECT
    state,
    MAX(total_claim_count) AS max_total_claim_count
  FROM (
    SELECT
      nppes_provider_state AS state,
      ROUND(SUM(total_claim_count)) AS total_claim_count
    FROM
      `bigquery-public-data.cms_medicare.part_d_prescriber_2014`
    GROUP BY
      state,
      generic_name)
  GROUP BY
    state) B
ON
  A.state = B.state
  AND A.total_claim_count = B.max_total_claim_count;

```

## bq235.sql

```sql
SELECT
  Provider_Name
FROM
(
SELECT
  OP.provider_state AS State,
  OP.provider_city AS City,
  OP.provider_id AS Provider_ID,
  OP.provider_name AS Provider_Name,
  ROUND(OP.average_OP_cost) AS Average_OP_Cost,
  ROUND(IP.average_IP_cost) AS Average_IP_Cost,
  ROUND(OP.average_OP_cost + IP.average_IP_cost) AS Combined_Average_Cost
FROM (
  SELECT
    provider_state,
    provider_city,
    provider_id,
    provider_name,
    SUM(average_total_payments*outpatient_services)/SUM(outpatient_services) AS average_OP_cost
  FROM
    `bigquery-public-data.cms_medicare.outpatient_charges_2014`
  GROUP BY
    provider_state,
    provider_city,
    provider_id,
    provider_name ) AS OP
INNER JOIN (
  SELECT
    provider_state,
    provider_city,
    provider_id,
    provider_name,
    SUM(average_medicare_payments*total_discharges)/SUM(total_discharges) AS average_IP_cost
  FROM
    `bigquery-public-data.cms_medicare.inpatient_charges_2014`
  GROUP BY
    provider_state,
    provider_city,
    provider_id,
    provider_name ) AS IP
ON
  OP.provider_id = IP.provider_id
  AND OP.provider_state = IP.provider_state
  AND OP.provider_city = IP.provider_city
  AND OP.provider_name = IP.provider_name
ORDER BY
  combined_average_cost DESC
LIMIT
  1
);

```

## bq268.sql

```sql
WITH 

visit AS (
SELECT fullvisitorid, MIN(date) AS date_first_visit, MAX(date) AS date_last_visit 
FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` GROUP BY fullvisitorid),

device_visit AS (
SELECT DISTINCT fullvisitorid, date, device.deviceCategory
FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*`),

transactions AS (
SELECT fullvisitorid, MIN(date) AS date_transactions, 1 AS transaction
FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` AS ga, UNNEST(ga.hits) AS hits
WHERE  hits.transaction.transactionId IS NOT NULL GROUP BY fullvisitorid),

device_transactions AS (
SELECT DISTINCT fullvisitorid, date, device.deviceCategory
FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` AS ga, UNNEST(ga.hits) AS hits
WHERE hits.transaction.transactionId IS NOT NULL),

visits_transactions AS (
SELECT visit.fullvisitorid, date_first_visit, date_transactions, date_last_visit , 
       device_visit.deviceCategory AS device_last_visit, device_transactions.deviceCategory AS device_transaction, 
       IFNULL(transactions.transaction,0) AS transaction
FROM visit LEFT JOIN transactions ON visit.fullvisitorid = transactions.fullvisitorid
LEFT JOIN device_visit ON visit.fullvisitorid = device_visit.fullvisitorid 
AND visit.date_last_visit = device_visit.date

LEFT JOIN device_transactions ON visit.fullvisitorid = device_transactions.fullvisitorid 
AND transactions.date_transactions = device_transactions.date ),

mortality_table AS (
SELECT fullvisitorid, date_first_visit, 
       CASE WHEN date_transactions IS NULL THEN date_last_visit ELSE date_transactions  END AS date_event, 
       CASE WHEN device_transaction IS NULL THEN device_last_visit ELSE device_transaction END AS device, transaction
FROM visits_transactions )

SELECT DATE_DIFF(PARSE_DATE('%Y%m%d',date_event), PARSE_DATE('%Y%m%d', date_first_visit),DAY) AS time 
FROM mortality_table
WHERE device = 'mobile'
ORDER BY DATE_DIFF(PARSE_DATE('%Y%m%d',date_event), PARSE_DATE('%Y%m%d', date_first_visit),DAY) DESC
LIMIT 1
```

## bq269.sql

```sql
WITH visitor_pageviews AS (
  SELECT
    FORMAT_DATE('%Y%m', PARSE_DATE('%Y%m%d', date)) AS month,
    CASE WHEN totals.transactions > 0 THEN 'purchase' ELSE 'non_purchase' END AS purchase_status,
    fullVisitorId,
    SUM(totals.pageviews) AS total_pageviews
  FROM
    `bigquery-public-data.google_analytics_sample.ga_sessions_*`
  WHERE
    _TABLE_SUFFIX BETWEEN '20170601' AND '20170731'
    AND totals.pageviews IS NOT NULL
  GROUP BY
    month, purchase_status, fullVisitorId
),
avg_pageviews AS (
  SELECT
    month,
    purchase_status,
    AVG(total_pageviews) AS avg_pageviews_per_visitor
  FROM
    visitor_pageviews
  GROUP BY
    month, purchase_status
)
SELECT
  month,
  MAX(CASE WHEN purchase_status = 'purchase' THEN avg_pageviews_per_visitor END) AS avg_pageviews_purchase,
  MAX(CASE WHEN purchase_status = 'non_purchase' THEN avg_pageviews_per_visitor END) AS avg_pageviews_non_purchase
FROM
  avg_pageviews
GROUP BY
  month
ORDER BY
  month
```

## bq270.sql

```sql
WITH
  cte1 AS
    (SELECT
      CONCAT(EXTRACT(YEAR FROM (PARSE_DATE('%Y%m%d', date))),'0',
                EXTRACT(MONTH FROM (PARSE_DATE('%Y%m%d', date)))) AS month,
      COUNT(hits.eCommerceAction.action_type) AS num_product_view
    FROM `bigquery-public-data.google_analytics_sample.ga_sessions_2017*`,
      UNNEST(hits) AS hits
    WHERE _table_suffix BETWEEN '0101' AND '0331'
      AND hits.eCommerceAction.action_type = '2'
    GROUP BY month),
  cte2 AS
    (SELECT
      CONCAT(EXTRACT(YEAR FROM (PARSE_DATE('%Y%m%d', date))),'0',
                EXTRACT(MONTH FROM (PARSE_DATE('%Y%m%d', date)))) AS month,
      COUNT(hits.eCommerceAction.action_type) AS num_addtocart
    FROM `bigquery-public-data.google_analytics_sample.ga_sessions_2017*`,
      UNNEST(hits) AS hits
    WHERE _table_suffix BETWEEN '0101' AND '0331'
      AND hits.eCommerceAction.action_type = '3'
    GROUP BY month),
  cte3 AS
    (SELECT
      CONCAT(EXTRACT(YEAR FROM (PARSE_DATE('%Y%m%d', date))),'0',
                EXTRACT(MONTH FROM (PARSE_DATE('%Y%m%d', date)))) AS month,
      COUNT(hits.eCommerceAction.action_type) AS num_purchase
    FROM `bigquery-public-data.google_analytics_sample.ga_sessions_2017*`,
      UNNEST(hits) AS hits,
      UNNEST(hits.product) AS product
    WHERE _table_suffix BETWEEN '0101' AND '0331'
      AND hits.eCommerceAction.action_type = '6'
      AND product.productRevenue IS NOT NULL
    GROUP BY month)
SELECT 
  ROUND((num_addtocart/num_product_view * 100),2) AS add_to_cart_rate,
  ROUND((num_purchase/num_product_view * 100),2) AS purchase_rate
FROM cte1
  LEFT JOIN cte2
  USING(month) 
  LEFT JOIN cte3
  USING(month)
ORDER BY month;

```

## bq275.sql

```sql
WITH 
  visit AS (
    SELECT fullvisitorid, MIN(date) AS date_first_visit
    FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` 
    GROUP BY fullvisitorid
  ),
  
  transactions AS (
    SELECT fullvisitorid, MIN(date) AS date_transactions, 1 AS transaction
    FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` AS ga, 
    UNNEST(ga.hits) AS hits 
    WHERE hits.transaction.transactionId IS NOT NULL 
    GROUP BY fullvisitorid
  ),

  device_transactions AS (
    SELECT DISTINCT fullvisitorid, date, device.deviceCategory AS device_transaction
    FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` AS ga, 
    UNNEST(ga.hits) AS hits 
    WHERE hits.transaction.transactionId IS NOT NULL
  ),

  visits_transactions AS (
    SELECT visit.fullvisitorid, date_first_visit, date_transactions, device_transaction
    FROM visit 
    LEFT JOIN transactions ON visit.fullvisitorid = transactions.fullvisitorid
    LEFT JOIN device_transactions ON visit.fullvisitorid = device_transactions.fullvisitorid 
    AND transactions.date_transactions = device_transactions.date
  )

SELECT fullvisitorid 
FROM visits_transactions
WHERE DATE_DIFF(PARSE_DATE('%Y%m%d', date_transactions), PARSE_DATE('%Y%m%d', date_first_visit), DAY) > 0
AND device_transaction = "mobile";

```

## bq279.sql

```sql
SELECT
    t.year,
    CASE 
        WHEN t.year = 2013 THEN (
                                  SELECT 
                                    COUNT(DISTINCT station_id)
                                  FROM 
                                    `bigquery-public-data.austin_bikeshare.bikeshare_trips` t
                                  INNER JOIN 
                                    `bigquery-public-data.austin_bikeshare.bikeshare_stations` s
                                  ON 
                                    t.start_station_id = s.station_id
                                  WHERE 
                                    s.status = 'active' AND EXTRACT(YEAR FROM start_time) = 2013
                                 ) 
        WHEN t.year = 2014 THEN (
                                  SELECT 
                                    COUNT(DISTINCT station_id)
                                  FROM 
                                    `bigquery-public-data.austin_bikeshare.bikeshare_trips` t
                                  INNER JOIN 
                                    `bigquery-public-data.austin_bikeshare.bikeshare_stations` s
                                  ON 
                                    t.start_station_id = s.station_id
                                  WHERE 
                                    s.status = 'active' AND EXTRACT(YEAR FROM start_time) = 2014
                                 )
    END
    AS number_status_active,
    CASE 
        WHEN t.year = 2013 THEN (
                                  SELECT 
                                   COUNT(DISTINCT station_id)
                                  FROM 
                                  `bigquery-public-data.austin_bikeshare.bikeshare_trips` t
                                  INNER JOIN 
                                  `bigquery-public-data.austin_bikeshare.bikeshare_stations` s
                                  ON 
                                   t.start_station_id = s.station_id
                                  WHERE 
                                   s.status = 'closed' AND EXTRACT(YEAR FROM start_time) = 2013
                                 ) 
        WHEN t.year = 2014 THEN (
                                  SELECT 
                                  COUNT(DISTINCT station_id)
                                  FROM 
                                    `bigquery-public-data.austin_bikeshare.bikeshare_trips` t
                                  INNER JOIN 
                                    `bigquery-public-data.austin_bikeshare.bikeshare_stations` s
                                  ON 
                                    t.start_station_id = s.station_id
                                  WHERE 
                                    s.status = 'closed' AND EXTRACT(YEAR FROM start_time) = 2014
                                 )
    END
    AS number_status_closed
FROM
    (
      SELECT 
         EXTRACT(YEAR FROM start_time) AS year,
         start_station_id
      FROM
         `bigquery-public-data.austin_bikeshare.bikeshare_trips`
    ) 
    AS t
INNER JOIN
    `bigquery-public-data.austin_bikeshare.bikeshare_stations` s
ON
    t.start_station_id = s.station_id
WHERE
    t.year BETWEEN 2013 AND 2014
GROUP BY
    t.year
ORDER BY
    t.year
```

## bq280.sql

```sql
WITH UserAnswers AS (
  SELECT
    owner_user_id AS answer_owner_id,
    COUNT(id) AS answer_count
  FROM bigquery-public-data.stackoverflow.posts_answers
  WHERE owner_user_id IS NOT NULL
  GROUP BY owner_user_id
),
DetailedUsers AS (
  SELECT
    id AS user_id,
    display_name AS user_display_name,
    reputation
  FROM bigquery-public-data.stackoverflow.users
  WHERE display_name IS NOT NULL AND reputation > 10
),
RankedUsers AS (
  SELECT
    u.user_display_name,
    u.reputation,
    a.answer_count,
    ROW_NUMBER() OVER (ORDER BY a.answer_count DESC) AS rank
  FROM DetailedUsers u
  JOIN UserAnswers a ON u.user_id = a.answer_owner_id
)
SELECT
  user_display_name,
FROM RankedUsers
WHERE rank = 1;

```

## bq281.sql

```sql
SELECT
  COUNT(1) AS num_rides
FROM
  `bigquery-public-data.austin_bikeshare.bikeshare_trips` 
WHERE 
start_station_name 
    NOT IN ('Mobile Station', 'Repair Shop')
AND
end_station_name 
    NOT IN ('Mobile Station', 'Repair Shop')
AND 
subscriber_type = 'Student Membership'
AND
bike_type = 'electric'
AND
duration_minutes > 10
GROUP BY 
    EXTRACT(YEAR from start_time), 
    EXTRACT(MONTH from start_time), 
    EXTRACT(DAY from start_time)
ORDER BY num_rides DESC
LIMIT 1
```

## bq282.sql

```sql
SELECT 
  district
FROM (
  SELECT
    S.starting_district AS district,
    T.start_station_id,
    T.end_station_id
  FROM
    `bigquery-public-data.austin_bikeshare.bikeshare_trips` AS T
  INNER JOIN (
    SELECT
      station_id,
      council_district AS starting_district
    FROM
      `bigquery-public-data.austin_bikeshare.bikeshare_stations`
    WHERE
      status = "active"
  ) AS S ON T.start_station_id = S.station_id
  WHERE
    S.starting_district IN (
      SELECT council_district
      FROM `bigquery-public-data.austin_bikeshare.bikeshare_stations`
      WHERE
        status = "active" AND
        station_id = SAFE_CAST(T.end_station_id AS INT64)
    )
    AND T.start_station_id != SAFE_CAST(T.end_station_id AS INT64)
) 
GROUP BY district
ORDER BY COUNT(*) DESC
LIMIT 1;

```

## bq284.sql

```sql
SELECT 
  category,
  COUNT(*) AS number_total_by_category,  
  CASE 
    WHEN category = 'tech' THEN 
          (SELECT count(*)
                FROM `bigquery-public-data.bbc_news.fulltext`
                WHERE (LOWER(body) LIKE '%education%') AND category = 'tech') * 100 /
                (SELECT count(*)
                FROM `bigquery-public-data.bbc_news.fulltext`
                WHERE category = 'tech')
    WHEN category = 'sport' THEN 
          (SELECT count(*)
                FROM `bigquery-public-data.bbc_news.fulltext`
                WHERE (LOWER(body) LIKE '%education%') AND category = 'sport') * 100 /
                (SELECT count(*)
                FROM `bigquery-public-data.bbc_news.fulltext`
                WHERE category = 'sport')
    WHEN category = 'business' THEN 
          (SELECT count(*)
                FROM `bigquery-public-data.bbc_news.fulltext`
                WHERE (LOWER(body) LIKE '%education%') AND category = 'business') * 100 /
                (SELECT count(*)
                FROM `bigquery-public-data.bbc_news.fulltext`
                WHERE category = 'business')
    WHEN category = 'politics' THEN 
          (SELECT count(*)
                FROM `bigquery-public-data.bbc_news.fulltext`
                WHERE (LOWER(body) LIKE '%education%') AND category = 'politics') * 100 /
                (SELECT count(*)
                FROM `bigquery-public-data.bbc_news.fulltext`
                WHERE category = 'politics')
    WHEN category = 'entertainment' THEN 
          (SELECT count(*)
                FROM `bigquery-public-data.bbc_news.fulltext`
                WHERE (LOWER(body) LIKE '%education%') AND category = 'entertainment') * 100 /
                (SELECT count(*)
                FROM `bigquery-public-data.bbc_news.fulltext`
                WHERE category = 'entertainment')
  END AS percent_education
FROM `bigquery-public-data.bbc_news.fulltext`
GROUP BY
  category;

```

## bq285.sql

```sql
with _fips AS
    (
        SELECT
            state_fips_code
        FROM
            `bigquery-public-data.census_utility.fips_codes_states`
        WHERE
            state_name = "Florida"
    )

    ,_zip AS
    (
        SELECT
            z.zip_code,
            z.zip_code_geom,
        FROM
            `bigquery-public-data.geo_us_boundaries.zip_codes` z, _fips u
        WHERE
            z.state_fips_code = u.state_fips_code
    )

    ,locations AS
    (
        SELECT
            COUNT(i.institution_name) AS count_locations,
            l.zip_code
        FROM
            `bigquery-public-data.fdic_banks.institutions` i
        JOIN
            `bigquery-public-data.fdic_banks.locations` l 
        USING (fdic_certificate_number)
        WHERE
            l.state IS NOT NULL
        AND 
            l.state_name IS NOT NULL
        GROUP BY 2
    )

    SELECT
        z.zip_code
    FROM
        _zip z
    JOIN
        locations l 
    USING (zip_code)
    GROUP BY
        z.zip_code
    ORDER BY
        SUM(l.count_locations) DESC
    LIMIT 1;

```

## bq286.sql

```sql
SELECT
  a.name AS name
FROM
  `bigquery-public-data.usa_names.usa_1910_current` a
JOIN (
  SELECT
    name,
    gender,
    year,
    SUM(number) AS total_number
  FROM
    `bigquery-public-data.usa_names.usa_1910_current`
  GROUP BY
    name,
    gender,
    year) b
ON
  a.name = b.name
  AND a.gender = b.gender
  AND a.year = b.year
WHERE 
    a.gender = 'F' AND
    a.state = 'WY' AND
    a.year = 2021
ORDER BY (a.number / b.total_number) DESC
LIMIT 1

```

## bq290.sql

```sql
with 

stations_selected as (
  select
    usaf,
    wban,
    country,
    name
  from
    `bigquery-public-data.noaa_gsod.stations`
  where
    country in ('US', 'UK')
),

data_filtered as (
  select
    gsod.*,
    stations.country
  from
    `bigquery-public-data.noaa_gsod.gsod2023` gsod
  join
    stations_selected stations
  on
    gsod.stn = stations.usaf
    and gsod.wban = stations.wban
  where
    date(gsod.date) between '2023-10-01' and '2023-10-31'
    and gsod.temp != 9999.9
),

-- US Metrics
us_metrics as (
  select
    date(date) as metric_date,
    avg(temp) as avg_temp_us,
    min(temp) as min_temp_us,
    max(temp) as max_temp_us
  from
    data_filtered
  where
    country = 'US'
  group by
    metric_date
),

-- UK Metrics
uk_metrics as (
  select
    date(date) as metric_date,
    avg(temp) as avg_temp_uk,
    min(temp) as min_temp_uk,
    max(temp) as max_temp_uk
  from
    data_filtered
  where
    country = 'UK'
  group by
    metric_date
),

-- Temperature Differences
temp_differences as (
  select
    us.metric_date,
    us.max_temp_us - uk.max_temp_uk as max_temp_diff,
    us.min_temp_us - uk.min_temp_uk as min_temp_diff,
    us.avg_temp_us - uk.avg_temp_uk as avg_temp_diff
  from
    us_metrics us
  join
    uk_metrics uk
  on
    us.metric_date = uk.metric_date
)

select 
  metric_date, 
  max_temp_diff, 
  min_temp_diff, 
  avg_temp_diff
from 
  temp_differences
order by
  metric_date;

```

## bq300.sql

```sql
WITH
  python2_questions AS (
    SELECT
      q.id AS question_id,
      q.title,
      q.body AS question_body,
      q.tags
    FROM
      `bigquery-public-data.stackoverflow.posts_questions` q
    WHERE
      (LOWER(q.tags) LIKE '%python-2%'
      OR LOWER(q.tags) LIKE '%python-2.x%'
      OR (
        LOWER(q.title) LIKE '%python 2%'
        OR LOWER(q.body) LIKE '%python 2%'
        OR LOWER(q.title) LIKE '%python2%'
        OR LOWER(q.body) LIKE '%python2%'
      ))
      AND (
        LOWER(q.title) NOT LIKE '%python 3%'
        AND LOWER(q.body) NOT LIKE '%python 3%'
        AND LOWER(q.title) NOT LIKE '%python3%'
        AND LOWER(q.body) NOT LIKE '%python3%'
      )
  )

SELECT
  COUNT(*) AS count_number
FROM
  python2_questions q
LEFT JOIN
  `bigquery-public-data.stackoverflow.posts_answers` a
ON
  q.question_id = a.parent_id
GROUP BY q.question_id
ORDER BY count_number DESC
LIMIT 1


```

## bq301.sql

```sql
SELECT
    answer.id AS a_id,
    (SELECT users.reputation FROM `bigquery-public-data.stackoverflow.users` users
        WHERE users.id = answer.owner_user_id) AS a_user_reputation,
    answer.score AS a_score,
    answer.comment_count AS answer_comment_count,
    questions.tags as q_tags,
    questions.score AS q_score,  
    questions.answer_count AS answer_count, 
    (SELECT users.reputation FROM `bigquery-public-data.stackoverflow.users` users
        WHERE users.id = questions.owner_user_id) AS q_user_reputation,
    questions.view_count AS q_view_count,
    questions.comment_count AS q_comment_count
FROM
   `bigquery-public-data.stackoverflow.posts_answers` AS answer 
LEFT JOIN
   `bigquery-public-data.stackoverflow.posts_questions` AS questions
      ON answer.parent_id = questions.id
WHERE
    answer.id = questions.accepted_answer_id
    AND 
    (
        questions.tags LIKE '%javascript%' AND
        (questions.tags LIKE '%xss%' OR
        questions.tags LIKE '%cross-site%' OR
        questions.tags LIKE '%exploit%' OR
        questions.tags LIKE '%cybersecurity%')
    )
    AND DATE(questions.creation_date) BETWEEN '2016-01-01' AND '2016-01-31'
    AND DATE(answer.creation_date) BETWEEN '2016-01-01' AND '2016-01-31'

```

## bq302.sql

```sql
WITH
-- Get recent data
RecentData AS (
    SELECT
        FORMAT_TIMESTAMP('%Y%m', creation_date) AS month_index,
        tags
    FROM
        `bigquery-public-data.stackoverflow.posts_questions`
    WHERE
        EXTRACT(YEAR FROM DATE(creation_date)) = 2022
),

-- Monthly number of questions posted
MonthlyQuestions AS (
    SELECT
        month_index,
        COUNT(*) AS num_questions
    FROM
        RecentData
    GROUP BY
        month_index
),

-- Monthly number of questions posted with specific tags
TaggedQuestions AS (
    SELECT
        month_index,
        tag,
        COUNT(*) AS num_tags
    FROM
        RecentData,
        UNNEST(SPLIT(tags, '|')) AS tag
    WHERE
        tag IN ('python')
    GROUP BY
        month_index, tag
)

SELECT
    a.month_index,
    a.num_tags / b.num_questions AS proportion
FROM
    TaggedQuestions a
LEFT JOIN
    MonthlyQuestions b ON a.month_index = b.month_index
ORDER BY
    a.month_index, proportion DESC;

```

## bq303.sql

```sql
SELECT u_id, tags
FROM (
    -- select comments with tags from the post
    SELECT cm.u_id, cm.creation_date, cm.text, pq.tags, "comment" as type
    FROM (
            SELECT a.parent_id as q_id, c.user_id as u_id, c.creation_date as creation_date, c.text as text
            FROM `bigquery-public-data.stackoverflow.comments` as c
            INNER JOIN `bigquery-public-data.stackoverflow.posts_answers` as a ON (a.id = c.post_id)
            WHERE c.user_id BETWEEN 16712208 AND 18712208
              AND DATE(c.creation_date) BETWEEN '2019-07-01' AND '2019-12-31'
            
            UNION ALL 
            
            SELECT q.id as q_id, c.user_id as u_id, c.creation_date as creation_date, c.text as text
            FROM `bigquery-public-data.stackoverflow.comments` as c
            INNER JOIN `bigquery-public-data.stackoverflow.posts_questions` as q ON (q.id = c.post_id)
            WHERE c.user_id BETWEEN 16712208 AND 18712208
              AND DATE(c.creation_date) BETWEEN '2019-07-01' AND '2019-12-31'
        ) as cm
    INNER JOIN `bigquery-public-data.stackoverflow.posts_questions` as pq ON (pq.id = cm.q_id)
        
    UNION ALL
    -- select answers with tags related to the post
    SELECT pa.owner_user_id as u_id, pa.creation_date as creation_date, pa.body as text, pq.tags as tags, "answer" as type
    FROM `bigquery-public-data.stackoverflow.posts_answers` as pa
    LEFT OUTER JOIN `bigquery-public-data.stackoverflow.posts_questions` as pq ON pq.id = pa.parent_id
    WHERE pa.owner_user_id BETWEEN 16712208 AND 18712208
      AND DATE(pa.creation_date) BETWEEN '2019-07-01' AND '2019-12-31'
    
    UNION ALL
    -- select posts
    SELECT pq.owner_user_id as u_id, pq.creation_date as creation_date, pq.body as text, pq.tags as tags, "question" as type
    FROM `bigquery-public-data.stackoverflow.posts_questions` as pq
    WHERE pq.owner_user_id BETWEEN 16712208 AND 18712208
      AND DATE(pq.creation_date) BETWEEN '2019-07-01' AND '2019-12-31'
)
ORDER BY u_id, creation_date;


```

## bq304.sql

```sql
WITH
tags_to_use AS (
    SELECT tag, idx
    FROM UNNEST([
        'android-layout', 
        'android-activity', 
        'android-intent', 
        'android-edittext', 
        'android-fragments', 
        'android-recyclerview', 
        'listview', 
        'android-actionbar', 
        'google-maps', 
        'android-asynctask'
    ]) AS tag WITH OFFSET idx
),
android_how_to_questions AS (
    SELECT
        PQ.*
    FROM
        bigquery-public-data.stackoverflow.posts_questions PQ
    WHERE
        EXISTS (
            SELECT 1
            FROM UNNEST(SPLIT(PQ.tags, '|')) tag
            WHERE tag IN (SELECT tag FROM tags_to_use)
        )
        AND (LOWER(PQ.title) LIKE '%how%' OR LOWER(PQ.body) LIKE '%how%')
        AND NOT (LOWER(PQ.title) LIKE '%fail%' OR LOWER(PQ.title) LIKE '%problem%' OR LOWER(PQ.title) LIKE '%error%'
                 OR LOWER(PQ.title) LIKE '%wrong%' OR LOWER(PQ.title) LIKE '%fix%' OR LOWER(PQ.title) LIKE '%bug%'
                 OR LOWER(PQ.title) LIKE '%issue%' OR LOWER(PQ.title) LIKE '%solve%' OR LOWER(PQ.title) LIKE '%trouble%')
        AND NOT (LOWER(PQ.body) LIKE '%fail%' OR LOWER(PQ.body) LIKE '%problem%' OR LOWER(PQ.body) LIKE '%error%'
                 OR LOWER(PQ.body) LIKE '%wrong%' OR LOWER(PQ.body) LIKE '%fix%' OR LOWER(PQ.body) LIKE '%bug%'
                 OR LOWER(PQ.body) LIKE '%issue%' OR LOWER(PQ.body) LIKE '%solve%' OR LOWER(PQ.body) LIKE '%trouble%')
),
questions_with_tag_rankings AS (
    SELECT
        T.id AS tag_id,
        TTU.idx AS tag_offset,
        T.tag_name,
        T.wiki_post_id AS tag_wiki_post_id,
        Q.id AS question_id,
        Q.title,
        Q.tags,
        Q.view_count,
        RANK() OVER (PARTITION BY T.id ORDER BY Q.view_count DESC) AS question_view_count_rank,
        COUNT(*) OVER (PARTITION BY T.id) AS total_valid_questions
    FROM
        bigquery-public-data.stackoverflow.tags T
    INNER JOIN
        tags_to_use TTU ON T.tag_name = TTU.tag
    INNER JOIN
        android_how_to_questions Q ON T.tag_name IN UNNEST(SPLIT(Q.tags, '|'))
)
SELECT
    question_id
FROM
    questions_with_tag_rankings
WHERE
    question_view_count_rank <= 50 AND total_valid_questions >= 50
ORDER BY
    tag_offset ASC, question_view_count_rank ASC;

```

## bq308.sql

```sql
SELECT
  Day_of_Week,
  COUNT(1) AS Num_Questions,
  SUM(answered_in_1h) AS Num_Answered_in_1H,
  ROUND(100 * SUM(answered_in_1h) / COUNT(1),1) AS Percent_Answered_in_1H
FROM
(
  SELECT
    q.id AS question_id,
    EXTRACT(DAYOFWEEK FROM q.creation_date) AS day_of_week,
    MAX(IF(a.parent_id IS NOT NULL AND
           (UNIX_SECONDS(a.creation_date)-UNIX_SECONDS(q.creation_date))/(60*60) <= 1, 1, 0)) AS answered_in_1h
  FROM
    `bigquery-public-data.stackoverflow.posts_questions` q
  LEFT JOIN
    `bigquery-public-data.stackoverflow.posts_answers` a
  ON q.id = a.parent_id
  WHERE EXTRACT(YEAR FROM a.creation_date) = 2020
    AND EXTRACT(YEAR FROM q.creation_date) = 2020
  GROUP BY question_id, day_of_week
)
GROUP BY
  Day_of_Week
ORDER BY
  Day_of_Week;

```

## bq309.sql

```sql
WITH badge_counts AS (
  SELECT
    c.id,
    COUNT(DISTINCT d.id) AS badge_number
  FROM
    `bigquery-public-data.stackoverflow.users` AS c
  JOIN
    `bigquery-public-data.stackoverflow.badges` AS d
  ON
    c.id = d.user_id
  GROUP BY
    c.id
),
labeled_questions AS (
  SELECT
    a.id,
    IF(
      a.id IN (
        SELECT DISTINCT b.id
        FROM
          `bigquery-public-data.stackoverflow.posts_answers` AS a
        JOIN
          `bigquery-public-data.stackoverflow.posts_questions` AS b
        ON
          a.parent_id = b.id
        WHERE
          b.accepted_answer_id IS NULL
          AND a.score / b.view_count > 0.01
      ) OR accepted_answer_id IS NOT NULL,
      1,
      0
    ) AS label,
    a.owner_user_id,
    LENGTH(a.body) AS body_length
  FROM
    `bigquery-public-data.stackoverflow.posts_questions` AS a
)
SELECT
  lq.id,
  b.reputation,
  b.up_votes - b.down_votes AS net_votes,
  e.badge_number
FROM
  labeled_questions AS lq
JOIN
  `bigquery-public-data.stackoverflow.users` AS b
ON
  lq.owner_user_id = b.id
JOIN
  badge_counts AS e
ON
  b.id = e.id
WHERE
  lq.label = 1
ORDER BY
  lq.body_length DESC
LIMIT
  10;



```

## bq310.sql

```sql
WITH
tags_to_use AS (
    SELECT tag, idx
    FROM UNNEST([
        'android-layout', 
        'android-activity', 
        'android-intent', 
        'android-edittext', 
        'android-fragments', 
        'android-recyclerview', 
        'listview', 
        'android-actionbar', 
        'google-maps', 
        'android-asynctask'
    ]) AS tag WITH OFFSET idx
),
android_how_to_questions AS (
    SELECT
        PQ.*
    FROM
        `bigquery-public-data.stackoverflow.posts_questions` PQ
    WHERE
        EXISTS (
            SELECT 1
            FROM UNNEST(SPLIT(PQ.tags, '|')) tag
            WHERE tag IN (SELECT tag FROM tags_to_use)
        )
        AND (LOWER(PQ.title) LIKE '%how%' OR LOWER(PQ.body) LIKE '%how%')
),
most_viewed_question AS (
    SELECT
        T.id AS tag_id,
        T.tag_name,
        Q.id AS question_id,
        Q.title,
        Q.tags,
        Q.view_count
    FROM
        `bigquery-public-data.stackoverflow.tags` T
    INNER JOIN
        tags_to_use TTU ON T.tag_name = TTU.tag
    INNER JOIN
        android_how_to_questions Q ON T.tag_name IN UNNEST(SPLIT(Q.tags, '|'))
    ORDER BY Q.view_count DESC
    LIMIT 1
)
SELECT
    title
FROM
    most_viewed_question;

```

## bq327.sql

```sql
WITH russia_Data AS (
  SELECT DISTINCT 
    id.country_name,
    id.value, -- Format in DataStudio
    id.indicator_name
  FROM (
    SELECT
      country_code,
      region
    FROM
      bigquery-public-data.world_bank_intl_debt.country_summary
    WHERE
      region != "" -- Aggregated countries do not have a region
  ) cs -- Aggregated countries do not have a region
  INNER JOIN (
    SELECT
      country_code,
      country_name,
      value, 
      indicator_name
    FROM
      bigquery-public-data.world_bank_intl_debt.international_debt
    WHERE
      country_code = 'RUS'
  ) id
  ON
    cs.country_code = id.country_code
  WHERE value IS NOT NULL
)
-- Count the number of indicators with a value of 0 for Russia
SELECT 
  COUNT(*) AS number_of_indicators_with_zero
FROM 
  russia_Data
WHERE 
  value = 0;

```

## bq328.sql

```sql
WITH country_data AS (
  -- CTE for country descriptive data
  SELECT 
    country_code, 
    short_name AS country,
    region, 
    income_group 
  FROM 
    `bigquery-public-data.world_bank_wdi.country_summary`
),

gdp_data AS (
  -- Filter data to only include GDP values
  SELECT 
    data.country_code, 
    country,
    region,
    value AS gdp_value
  FROM 
    `bigquery-public-data.world_bank_wdi.indicators_data` data
  LEFT JOIN country_data
    ON data.country_code = country_data.country_code
  WHERE indicator_code = "NY.GDP.MKTP.KD" -- GDP Indicator
    AND country_data.region IS NOT NULL
    AND country_data.income_group IS NOT NULL
),

cal_median_gdp AS (
  -- Calculate the median GDP value for each region
  SELECT 
    region,
    APPROX_QUANTILES(gdp_value, 2)[OFFSET(1)] AS median_gdp
  FROM gdp_data
  GROUP BY region
)
-- Select the regions with their median GDP values
SELECT 
  region
FROM 
  cal_median_gdp
ORDER BY median_gdp DESC
LIMIT 1;

```

## bq330.sql

```sql
WITH _fips AS (
    SELECT
        state_fips_code
    FROM
        `bigquery-public-data.census_utility.fips_codes_states`
    WHERE
        state_name = "Colorado"
),

_bg AS (
    SELECT
        b.geo_id,
        b.blockgroup_geom,
        ST_AREA(b.blockgroup_geom) AS bg_size
    FROM
        `bigquery-public-data.geo_census_blockgroups.us_blockgroups_national` b
    JOIN
        _fips u ON b.state_fips_code = u.state_fips_code
),

_zip AS (
    SELECT
        z.zip_code,
        z.zip_code_geom
    FROM
        `bigquery-public-data.geo_us_boundaries.zip_codes` z
    JOIN
        _fips u ON z.state_fips_code = u.state_fips_code
),

bq_zip_overlap AS (
    SELECT
        b.geo_id,
        z.zip_code,
        ST_AREA(ST_INTERSECTION(b.blockgroup_geom, z.zip_code_geom)) / b.bg_size AS overlap_size,
        b.blockgroup_geom
    FROM
        _zip z
    JOIN
        _bg b ON ST_INTERSECTS(b.blockgroup_geom, z.zip_code_geom)
),

locations AS (
    SELECT
        SUM(overlap_size * count_locations) AS locations_per_bg,
        l.zip_code
    FROM (
        SELECT
            COUNT(CONCAT(institution_name, " : ", branch_name)) AS count_locations,
            zip_code
        FROM
            `bigquery-public-data.fdic_banks.locations`
        WHERE
            state IS NOT NULL
            AND state_name IS NOT NULL
        GROUP BY
            zip_code
    ) l
    JOIN
        bq_zip_overlap ON l.zip_code = bq_zip_overlap.zip_code
    GROUP BY
        l.zip_code
)

SELECT
    l.zip_code
FROM
    locations l
GROUP BY
    l.zip_code
ORDER BY
    MAX(locations_per_bg) DESC
LIMIT 1;

```

## bq338.sql

```sql
WITH population_change AS (
    SELECT
        a.geo_id,
        a.total_pop AS pop_2011,
        b.total_pop AS pop_2018,
        ((b.total_pop - a.total_pop) / a.total_pop) * 100 AS population_change_percentage
    FROM
        bigquery-public-data.census_bureau_acs.censustract_2011_5yr a
    JOIN
        bigquery-public-data.census_bureau_acs.censustract_2018_5yr b
    ON
        a.geo_id = b.geo_id
    WHERE 
        a.total_pop > 1000
        AND b.total_pop > 1000
        AND a.geo_id LIKE '36047%'
        AND b.geo_id LIKE '36047%'
    ORDER BY 
        population_change_percentage DESC
    LIMIT 20
),

acs_2018 AS (
    SELECT 
        geo_id, 
        median_income AS median_income_2018
    FROM 
        bigquery-public-data.census_bureau_acs.censustract_2018_5yr  
    WHERE 
        geo_id LIKE '36047%'
        AND total_pop > 1000
),

acs_2011 AS (
    SELECT 
        geo_id, 
        median_income AS median_income_2011
    FROM 
        bigquery-public-data.census_bureau_acs.censustract_2011_5yr 
    WHERE 
        geo_id LIKE '36047%'
    AND total_pop > 1000
),

acs_diff AS (
    SELECT
        a18.geo_id, 
        a18.median_income_2018, 
        a11.median_income_2011,
        (a18.median_income_2018 - a11.median_income_2011) AS median_income_diff
    FROM 
        acs_2018 a18
    JOIN 
        acs_2011 a11
        ON a18.geo_id = a11.geo_id
    WHERE 
        (a18.median_income_2018 - a11.median_income_2011) IS NOT NULL
    ORDER BY 
        (a18.median_income_2018 - a11.median_income_2011) DESC
    LIMIT 20
),

common_geoids AS (
    SELECT population_change.geo_id
    FROM population_change
    JOIN acs_diff ON population_change.geo_id = acs_diff.geo_id
)

SELECT geo_id FROM common_geoids;

```

## bq339.sql

```sql
WITH monthly_totals AS (
  SELECT
    SUM(CASE WHEN subscriber_type = 'Customer' THEN duration_sec / 60 ELSE NULL END) AS customer_minutes_sum,
    SUM(CASE WHEN subscriber_type = 'Subscriber' THEN duration_sec / 60 ELSE NULL END) AS subscriber_minutes_sum,
    EXTRACT(MONTH FROM end_date) AS end_month
  FROM
    `bigquery-public-data.san_francisco_bikeshare.bikeshare_trips`
  WHERE
    EXTRACT(YEAR FROM end_date) = 2017
  GROUP BY
    end_month
),

cumulative_totals AS (
  SELECT
    end_month,
    SUM(customer_minutes_sum) OVER (ORDER BY end_month ROWS UNBOUNDED PRECEDING) / 1000 AS cumulative_minutes_cust,
    SUM(subscriber_minutes_sum) OVER (ORDER BY end_month ROWS UNBOUNDED PRECEDING) / 1000 AS cumulative_minutes_sub
  FROM
    monthly_totals
),

differences AS (
  SELECT
    end_month,
    ABS(cumulative_minutes_cust - cumulative_minutes_sub) AS abs_diff
  FROM
    cumulative_totals
)

SELECT
  end_month
FROM
  differences
ORDER BY
  abs_diff DESC
LIMIT 1;

```

## bq350.sql

```sql
DECLARE
  my_drug_list ARRAY<STRING>;
SET
  my_drug_list = [
  'Keytruda',
  'Vioxx',
  'Humira',
  'Premarin' ];

SELECT
  id AS drug_id,
  tradeNameList.element AS drug_trade_name,
  drugType AS drug_type,
  hasBeenWithdrawn AS drug_withdrawn
FROM
  `open-targets-prod.platform.molecule`,
  UNNEST (tradeNames.list) AS tradeNameList
WHERE
  tradeNameList.element IN UNNEST(my_drug_list)
  AND isApproved = TRUE
  AND blackBoxWarning = TRUE
  AND drugType != 'Unknown';

```

## bq352.sql

```sql
WITH natality_2018 AS (
  SELECT County_of_Residence_FIPS AS FIPS, Ave_Number_of_Prenatal_Wks AS Vist_Ave, County_of_Residence
  FROM `bigquery-public-data.sdoh_cdc_wonder_natality.county_natality` 
  WHERE SUBSTR(County_of_Residence_FIPS, 0, 2) = "55" AND Year = '2018-01-01'
),

acs_2017 AS (
  SELECT geo_id, commute_45_59_mins, employed_pop
  FROM `bigquery-public-data.census_bureau_acs.county_2017_5yr`
),

corr_tbl AS (
  SELECT
    n.County_of_Residence,
    ROUND((a.commute_45_59_mins / a.employed_pop) * 100, 2) AS percent_high_travel,
    n.Vist_Ave
  FROM acs_2017 a
  JOIN natality_2018 n
  ON a.geo_id = n.FIPS
)

SELECT County_of_Residence, Vist_Ave
FROM corr_tbl
WHERE percent_high_travel > 5

```

## bq354.sql

```sql
WITH skin_condition_ICD_concept_ids AS (
    SELECT
        concept_id,
        CASE concept_code
            WHEN 'L70' THEN 'Acne'
            WHEN 'L20' THEN 'Atopic dermatitis'
            WHEN 'L40' THEN 'Psoriasis'
            ELSE 'Vitiligo'
        END AS skin_condition
    FROM
        `bigquery-public-data.cms_synthetic_patient_data_omop.concept`
    WHERE
        concept_code IN ('L70', 'L20', 'L40', 'L80')
        AND vocabulary_id = 'ICD10CM'
),
standard_concept_ids AS (
    SELECT
        concept_id
    FROM
        `bigquery-public-data.cms_synthetic_patient_data_omop.concept`
    WHERE
        standard_concept = 'S'
),
skin_condition_standard_concept_ids AS (
    SELECT
        s.skin_condition,
        r.concept_id_2 AS concept_id
    FROM
        skin_condition_ICD_concept_ids s
    JOIN
        `bigquery-public-data.cms_synthetic_patient_data_omop.concept_relationship` r
    ON
        s.concept_id = r.concept_id_1
    JOIN
        standard_concept_ids sc
    ON
        sc.concept_id = r.concept_id_2
    WHERE
        r.relationship_id = 'Maps to'
),
all_skin_concept_ids AS (
    SELECT DISTINCT
        skin_condition,
        concept_id
    FROM
        skin_condition_standard_concept_ids
),
descendant_concept_ids AS (
    SELECT
        a.skin_condition,
        ca.descendant_concept_id AS concept_id
    FROM
        all_skin_concept_ids a
    JOIN
        `bigquery-public-data.cms_synthetic_patient_data_omop.concept_ancestor` ca
    ON
        a.concept_id = ca.ancestor_concept_id
),
participants_with_condition AS (
    SELECT
        d.skin_condition,
        COUNT(DISTINCT co.person_id) AS nb_of_participants_with_skin_condition
    FROM
        `bigquery-public-data.cms_synthetic_patient_data_omop.condition_occurrence` co
    JOIN
        descendant_concept_ids d
    ON
        co.condition_concept_id = d.concept_id
    GROUP BY
        d.skin_condition
),
total_participants AS (
    SELECT
        COUNT(DISTINCT person_id) AS nb_of_participants
    FROM
        `bigquery-public-data.cms_synthetic_patient_data_omop.person`
)
SELECT
    p.skin_condition,
    100 * p.nb_of_participants_with_skin_condition / t.nb_of_participants AS percentage_of_participants
FROM
    participants_with_condition p,
    total_participants t
```

## bq355.sql

```sql
WITH quinapril_concept AS (
    SELECT concept_id
    FROM `bigquery-public-data.cms_synthetic_patient_data_omop.concept`
    WHERE concept_code = "35208" AND vocabulary_id = "RxNorm"
),
quinapril_related_medications AS (
    SELECT DISTINCT descendant_concept_id AS concept_id
    FROM `bigquery-public-data.cms_synthetic_patient_data_omop.concept_ancestor`
    WHERE ancestor_concept_id IN (SELECT concept_id FROM quinapril_concept)
),
participants_with_quinapril AS (
    SELECT COUNT(DISTINCT person_id) AS count
    FROM `bigquery-public-data.cms_synthetic_patient_data_omop.drug_exposure`
    WHERE drug_concept_id IN (SELECT concept_id FROM quinapril_related_medications)
),
total_participants AS (
    SELECT COUNT(DISTINCT person_id) AS count
    FROM `bigquery-public-data.cms_synthetic_patient_data_omop.person`
)
SELECT
    100 - (100 * participants_with_quinapril.count / total_participants.count) AS without_quinapril
FROM
    participants_with_quinapril, total_participants
```

## bq357.sql

```sql
WITH DailyAverages AS (
    SELECT 
        year, month, day, latitude, longitude,
        AVG(wind_speed) AS avg_wind_speed,
    FROM 
        `bigquery-public-data.noaa_icoads.icoads_core_*`
    WHERE
        _TABLE_SUFFIX BETWEEN '2005' AND '2015'
    GROUP BY 
        year, month, day, latitude, longitude
)
SELECT 
    year, month, day, latitude, longitude,
    avg_wind_speed,

FROM 
    DailyAverages
WHERE
    avg_wind_speed IS NOT NULL

ORDER BY avg_wind_speed DESC LIMIT 5
```

## bq360.sql

```sql
WITH specialist_counts AS (
  SELECT
    healthcare_provider_taxonomy_1_specialization,
    COUNT(DISTINCT npi) AS number_specialist
  FROM
    `bigquery-public-data.nppes.npi_optimized`
  WHERE
    provider_business_practice_location_address_city_name = "MOUNTAIN VIEW"
    AND provider_business_practice_location_address_state_name = "CA"
    AND healthcare_provider_taxonomy_1_specialization > ""
  GROUP BY
    healthcare_provider_taxonomy_1_specialization
),
top_10_specialists AS (
  SELECT
    healthcare_provider_taxonomy_1_specialization,
    number_specialist
  FROM
    specialist_counts
  ORDER BY
    number_specialist DESC
  LIMIT 10
),
average_value AS (
  SELECT
    AVG(number_specialist) AS average_specialist
  FROM
    top_10_specialists
),
closest_to_average AS (
  SELECT
    healthcare_provider_taxonomy_1_specialization,
    number_specialist,
    ABS(number_specialist - (SELECT average_specialist FROM average_value)) AS difference
  FROM
    top_10_specialists
)
SELECT
  healthcare_provider_taxonomy_1_specialization
FROM
  closest_to_average
ORDER BY
  difference
LIMIT 1;

```

## bq362.sql

```sql
select company from
            (select *,
            row_number() over(partition by company order by month_o_month_calc desc) as rownum
            from
            (select *,
            num_trips - lag(num_trips) over(partition by company order by month) as month_o_month_calc
                from
                (SELECT 
                company,
                format_date("%Y-%m", date_sub((cast(trip_start_timestamp as date)), interval 1 month)) as prev_month,
                format_date("%Y-%m", cast(trip_start_timestamp as date)) AS month,
                count(1) AS num_trips
                from `bigquery-public-data.chicago_taxi_trips.taxi_trips`
                where extract(YEAR from trip_start_timestamp) = 2018
                group by company, month, prev_month
                order by company,month)
            order by company, month_o_month_calc desc)
            ) 
        where rownum = 1
        order by month_o_month_calc desc, company 
        limit 3
```

## bq363.sql

```sql
SELECT
  FORMAT('%02.0fm to %02.0fm', min_minutes, max_minutes) AS minutes_range,
  SUM(trips) AS total_trips,
  FORMAT('%3.2f', SUM(total_fare) / SUM(trips)) AS average_fare
FROM (
  SELECT
    MIN(duration_in_minutes) OVER (quantiles) AS min_minutes,
    MAX(duration_in_minutes) OVER (quantiles) AS max_minutes,
    SUM(trips) AS trips,
    SUM(total_fare) AS total_fare
  FROM (
    SELECT
      ROUND(trip_seconds / 60) AS duration_in_minutes,
      NTILE(10) OVER (ORDER BY trip_seconds / 60) AS quantile,
      COUNT(1) AS trips,
      SUM(fare) AS total_fare
    FROM
      `bigquery-public-data.chicago_taxi_trips.taxi_trips`
    WHERE
      ROUND(trip_seconds / 60) BETWEEN 1 AND 50
    GROUP BY
      trip_seconds,
      duration_in_minutes )
  GROUP BY
    duration_in_minutes,
    quantile
  WINDOW quantiles AS (PARTITION BY quantile)
  )
GROUP BY
  minutes_range
ORDER BY
  Minutes_range
```

## bq366.sql

```sql
SELECT period, description, c FROM (
  SELECT 
a.period, 
b.description, 
count(*) c, 
row_number() over (partition by period order by count(*) desc) seqnum 
  FROM `bigquery-public-data.the_met.objects` a
  JOIN (
    SELECT 
        label.description as description, 
        object_id 
    FROM `bigquery-public-data.the_met.vision_api_data`, UNNEST(labelAnnotations) label
  ) b
  ON a.object_id = b.object_id
  WHERE a.period is not null
  group by 1,2
)
WHERE seqnum <= 3
AND c >= 500 # only include labels that have 50 or more pieces associated with it
ORDER BY period, c desc;

```

## bq374.sql

```sql
WITH initial_visits AS (
    SELECT
        fullVisitorId,
        MIN(visitStartTime) AS initialVisitStartTime
    FROM
        `bigquery-public-data.google_analytics_sample.*`
    WHERE
        totals.newVisits = 1
        AND date BETWEEN '20160801' AND '20170430'
    GROUP BY
        fullVisitorId
),
qualified_initial_visits AS (
  SELECT
    s.fullVisitorId,
    s.visitStartTime AS initialVisitStartTime,
    s.totals.timeOnSite AS time_on_site
  FROM
    `bigquery-public-data.google_analytics_sample.*` s
  JOIN initial_visits i
    ON s.fullVisitorId = i.fullVisitorId
    AND s.visitStartTime = i.initialVisitStartTime
  WHERE
    s.totals.timeOnSite > 300
),
filtered_data AS (
  SELECT
    q.fullVisitorId,
    q.time_on_site,
    IF(COUNTIF(s.visitStartTime > q.initialVisitStartTime AND s.totals.transactions > 0) > 0, 1, 0) AS will_buy_on_return_visit
  FROM
    qualified_initial_visits q
  LEFT JOIN `bigquery-public-data.google_analytics_sample.*` s
    ON q.fullVisitorId = s.fullVisitorId
  GROUP BY
    q.fullVisitorId, q.time_on_site
),
matching_users AS (
  SELECT
    fullVisitorId
  FROM
    filtered_data
  WHERE
    time_on_site > 300 AND will_buy_on_return_visit = 1
),
total_new_users AS (
  SELECT
    COUNT(DISTINCT fullVisitorId) AS total_new_users
  FROM
    `bigquery-public-data.google_analytics_sample.*`
  WHERE
    totals.newVisits = 1
    AND date BETWEEN '20160801' AND '20170430'
),
final_counts AS (
  SELECT
    COUNT(DISTINCT fullVisitorId) AS users_matching_criteria
  FROM
    matching_users
)
SELECT
  (final_counts.users_matching_criteria / total_new_users.total_new_users) * 100 AS percentage_matching_criteria
FROM
  final_counts,
  total_new_users;

```

## bq376.sql

```sql
WITH station_neighborhoods AS (
   SELECT
       bs.station_id,
       bs.name AS station_name,
       nb.neighborhood
   FROM `bigquery-public-data.san_francisco.bikeshare_stations` bs
   JOIN
       bigquery-public-data.san_francisco_neighborhoods.boundaries nb
   ON 
       ST_Intersects(ST_GeogPoint(bs.longitude, bs.latitude), nb.neighborhood_geom)
),

neighborhood_crime_counts AS (
   SELECT
       neighborhood,
       COUNT(*) AS crime_count
   FROM (
       SELECT
           n.neighborhood
       FROM
           bigquery-public-data.san_francisco.sfpd_incidents i
       JOIN
           bigquery-public-data.san_francisco_neighborhoods.boundaries n
       ON
           ST_Intersects(ST_GeogPoint(i.longitude, i.latitude), n.neighborhood_geom)
   ) AS incident_neighborhoods
   GROUP BY
       neighborhood
)

SELECT
  sn.neighborhood,
  COUNT(station_name) AS station_number,
  ANY_VALUE(ncc.crime_count) AS crime_number
FROM
  station_neighborhoods sn
JOIN
  neighborhood_crime_counts ncc
ON
  sn.neighborhood = ncc.neighborhood
GROUP BY sn.neighborhood
ORDER BY
  crime_number ASC


```

## bq379.sql

```sql
WITH AvgScore AS (
  SELECT
    AVG(associations.score) AS avg_score
  FROM
    `open-targets-prod.platform.associationByOverallDirect` AS associations
  JOIN
    `open-targets-prod.platform.diseases` AS diseases
  ON
    associations.diseaseId = diseases.id
  WHERE
    diseases.name = 'psoriasis'
)
SELECT
  targets.approvedSymbol AS target_approved_symbol
FROM
  `open-targets-prod.platform.associationByOverallDirect` AS associations
JOIN
  `open-targets-prod.platform.diseases` AS diseases
ON
  associations.diseaseId = diseases.id
JOIN
  `open-targets-prod.platform.targets` AS targets
ON
  associations.targetId = targets.id
CROSS JOIN
  AvgScore
WHERE
  diseases.name = 'psoriasis'
ORDER BY
  ABS(associations.score - AvgScore.avg_score) ASC
LIMIT 1

```

## bq383.sql

```sql
WITH data AS (
  SELECT
    EXTRACT(YEAR FROM wx.date) AS year,
    MAX(IF(wx.element = 'PRCP', wx.value/10, NULL)) AS max_prcp,
    MAX(IF(wx.element = 'TMIN', wx.value/10, NULL)) AS max_tmin,
    MAX(IF(wx.element = 'TMAX', wx.value/10, NULL)) AS max_tmax
  FROM
    `bigquery-public-data.ghcn_d.ghcnd_2013` AS wx
  WHERE
    wx.id = 'USW00094846' AND
    wx.qflag IS NULL AND
    wx.value IS NOT NULL AND
    DATE_DIFF(DATE('2013-12-31'), wx.date, DAY) < 15
  GROUP BY
    year

  UNION ALL

  SELECT
    EXTRACT(YEAR FROM wx.date) AS year,
    MAX(IF(wx.element = 'PRCP', wx.value/10, NULL)) AS max_prcp,
    MAX(IF(wx.element = 'TMIN', wx.value/10, NULL)) AS max_tmin,
    MAX(IF(wx.element = 'TMAX', wx.value/10, NULL)) AS max_tmax
  FROM
    `bigquery-public-data.ghcn_d.ghcnd_2014` AS wx
  WHERE
    wx.id = 'USW00094846' AND
    wx.qflag IS NULL AND
    wx.value IS NOT NULL AND
    DATE_DIFF(DATE('2014-12-31'), wx.date, DAY) < 15
  GROUP BY
    year

  UNION ALL

  SELECT
    EXTRACT(YEAR FROM wx.date) AS year,
    MAX(IF(wx.element = 'PRCP', wx.value/10, NULL)) AS max_prcp,
    MAX(IF(wx.element = 'TMIN', wx.value/10, NULL)) AS max_tmin,
    MAX(IF(wx.element = 'TMAX', wx.value/10, NULL)) AS max_tmax
  FROM
    `bigquery-public-data.ghcn_d.ghcnd_2015` AS wx
  WHERE
    wx.id = 'USW00094846' AND
    wx.qflag IS NULL AND
    wx.value IS NOT NULL AND
    DATE_DIFF(DATE('2015-12-31'), wx.date, DAY) < 15
  GROUP BY
    year

  UNION ALL

  SELECT
    EXTRACT(YEAR FROM wx.date) AS year,
    MAX(IF(wx.element = 'PRCP', wx.value/10, NULL)) AS max_prcp,
    MAX(IF(wx.element = 'TMIN', wx.value/10, NULL)) AS max_tmin,
    MAX(IF(wx.element = 'TMAX', wx.value/10, NULL)) AS max_tmax
  FROM
    `bigquery-public-data.ghcn_d.ghcnd_2016` AS wx
  WHERE
    wx.id = 'USW00094846' AND
    wx.qflag IS NULL AND
    wx.value IS NOT NULL AND
    DATE_DIFF(DATE('2016-12-31'), wx.date, DAY) < 15
  GROUP BY
    year
)

SELECT
  year,
  MAX(max_prcp) AS annual_max_prcp,
  MAX(max_tmin) AS annual_max_tmin,
  MAX(max_tmax) AS annual_max_tmax
FROM data
GROUP BY year
ORDER BY year ASC;

```

## bq389.sql

```sql
SELECT
  pm10.month AS month,
  pm10.avg AS pm10,
  pm25_frm.avg AS pm25_frm,
  pm25_nonfrm.avg AS pm25_nonfrm,
  co.avg AS co,
  so2.avg AS so2,
  lead.avg AS lead
FROM
  (SELECT AVG(arithmetic_mean) AS avg, 
          EXTRACT(YEAR FROM date_local) AS year, 
          EXTRACT(MONTH FROM date_local) AS month
   FROM `bigquery-public-data.epa_historical_air_quality.pm10_daily_summary`
   WHERE state_name = 'California' AND EXTRACT(YEAR FROM date_local) = 2020
   GROUP BY year, month) AS pm10
JOIN
  (SELECT AVG(arithmetic_mean) AS avg, 
          EXTRACT(YEAR FROM date_local) AS year, 
          EXTRACT(MONTH FROM date_local) AS month
   FROM `bigquery-public-data.epa_historical_air_quality.pm25_frm_daily_summary`
   WHERE state_name = 'California' AND EXTRACT(YEAR FROM date_local) = 2020
   GROUP BY year, month) AS pm25_frm
ON pm10.year = pm25_frm.year AND pm10.month = pm25_frm.month
JOIN
  (SELECT AVG(arithmetic_mean) AS avg, 
          EXTRACT(YEAR FROM date_local) AS year, 
          EXTRACT(MONTH FROM date_local) AS month
   FROM `bigquery-public-data.epa_historical_air_quality.pm25_nonfrm_daily_summary`
   WHERE state_name = 'California' AND EXTRACT(YEAR FROM date_local) = 2020
   GROUP BY year, month) AS pm25_nonfrm
ON pm10.year = pm25_nonfrm.year AND pm10.month = pm25_nonfrm.month
JOIN
  (SELECT AVG(arithmetic_mean) * 100 AS avg, 
          EXTRACT(YEAR FROM date_local) AS year, 
          EXTRACT(MONTH FROM date_local) AS month
   FROM `bigquery-public-data.epa_historical_air_quality.lead_daily_summary`
   WHERE state_name = 'California' AND EXTRACT(YEAR FROM date_local) = 2020
   GROUP BY year, month) AS lead
ON pm10.year = lead.year AND pm10.month = lead.month
JOIN
  (SELECT AVG(arithmetic_mean) AS avg, 
          EXTRACT(YEAR FROM date_local) AS year, 
          EXTRACT(MONTH FROM date_local) AS month
   FROM `bigquery-public-data.epa_historical_air_quality.voc_daily_summary`
   WHERE state_name = 'California' AND EXTRACT(YEAR FROM date_local) = 2020
   GROUP BY year, month) AS co
ON pm10.year = co.year AND pm10.month = co.month
JOIN
  (SELECT AVG(arithmetic_mean) * 10 AS avg, 
          EXTRACT(YEAR FROM date_local) AS year, 
          EXTRACT(MONTH FROM date_local) AS month
   FROM `bigquery-public-data.epa_historical_air_quality.so2_daily_summary`
   WHERE state_name = 'California' AND EXTRACT(YEAR FROM date_local) = 2020
   GROUP BY year, month) AS so2
ON pm10.year = so2.year AND pm10.month = so2.month
ORDER BY
  month;

```

## bq392.sql

```sql
WITH
  # FIRST CAST EACH YEAR, MONTH, DATE TO STRINGS
  T AS (
    SELECT
      *,
      CAST(year AS STRING) AS year_string,
      CAST(mo AS STRING) AS month_string,
      CAST(da AS STRING) AS day_string
    FROM
      `bigquery-public-data.noaa_gsod.gsod2009`
    WHERE
      stn = "723758"
  ),

  # SECOND, CONCAT ALL THE STRINGS TOGETHER INTO ONE COLUMN
  TT AS (
    SELECT
      *,
      CONCAT(year_string, "-", month_string, "-", day_string) AS date_string
    FROM
      T
  ),

  # THIRD, CAST THE DATE STRING INTO A DATE FORMAT
  TTT AS (
    SELECT
      *,
      CAST(date_string AS DATE) AS date_date
    FROM
      TT
  ),

  # FOURTH, CALCULATE THE MEAN TEMPERATURE FOR EACH DATE
  Temp_Avg AS (
    SELECT
      date_date,
      AVG(temp) AS avg_temp
    FROM
      TTT
    WHERE
      date_date BETWEEN '2009-10-01' AND '2009-10-31'
    GROUP BY
      date_date
  )

# FINAL SELECTION OF TOP 3 DATES WITH HIGHEST MEAN TEMPERATURE
SELECT
  date_date AS dates
FROM
  Temp_Avg
ORDER BY
  avg_temp DESC
LIMIT 3;

```

## bq394.sql

```sql
WITH DailyAverages AS (
    SELECT 
        year, month, day,
        air_temperature,
        wetbulb_temperature,
        dewpoint_temperature,
        sea_surface_temp
    FROM 
        `bigquery-public-data.noaa_icoads.icoads_core_*`
    WHERE
        _TABLE_SUFFIX BETWEEN '2010' AND '2014'
),

MonthlyAverages AS (
    SELECT 
        year,
        month,
        AVG(air_temperature) AS avg_air_temperature,
        AVG(wetbulb_temperature) AS avg_wetbulb_temperature,
        AVG(dewpoint_temperature) AS avg_dewpoint_temperature,
        AVG(sea_surface_temp) AS avg_sea_surface_temp
    FROM 
        DailyAverages
    WHERE
        air_temperature IS NOT NULL
        AND wetbulb_temperature IS NOT NULL
        AND dewpoint_temperature IS NOT NULL
        AND sea_surface_temp IS NOT NULL
    GROUP BY 
        year, month
),

DifferenceSums AS (
    SELECT
        year,
        month,
        (ABS(avg_air_temperature - avg_wetbulb_temperature) +
        ABS(avg_air_temperature - avg_dewpoint_temperature) +
        ABS(avg_air_temperature - avg_sea_surface_temp) +
        ABS(avg_wetbulb_temperature - avg_dewpoint_temperature) +
        ABS(avg_wetbulb_temperature - avg_sea_surface_temp) +
        ABS(avg_dewpoint_temperature - avg_sea_surface_temp)) AS sum_of_differences
    FROM 
        MonthlyAverages
)

SELECT
    year,
    month,
    sum_of_differences
FROM
    DifferenceSums
ORDER BY
    sum_of_differences ASC
LIMIT 3;

```

## bq395.sql

```sql
WITH homeless_2015 AS (
  SELECT Unsheltered_Homeless AS U15, SUBSTR(CoC_Number, 0, 2) as State_Abbr
  FROM `bigquery-public-data.sdoh_hud_pit_homelessness.hud_pit_by_coc`
  WHERE Count_Year = 2015
),
 
homeless_2018 AS (
  SELECT Unsheltered_Homeless AS U18, SUBSTR(CoC_Number, 0, 2) as State_Abbr
  FROM `bigquery-public-data.sdoh_hud_pit_homelessness.hud_pit_by_coc`
  WHERE Count_Year = 2018
),

unsheltered_change AS (
  SELECT homeless_2018.State_Abbr, 
         SUM(U15) AS Unsheltered_2015, 
         SUM(U18) AS Unsheltered_2018, 
         (SUM(U18) - SUM(U15)) / SUM(U15) * 100 AS Percent_Change
  FROM homeless_2018
  JOIN homeless_2015
  ON homeless_2018.State_Abbr = homeless_2015.State_Abbr
  GROUP BY State_Abbr
),

average_change AS (
  SELECT AVG(Percent_Change) AS Avg_Change
  FROM unsheltered_change
),

closest_to_avg AS (
  SELECT State_Abbr
  FROM unsheltered_change, average_change
  ORDER BY ABS(Percent_Change - Avg_Change)
  LIMIT 5
)

SELECT State_Abbr FROM closest_to_avg;

```

## bq396.sql

```sql
WITH weekend_accidents AS (
    SELECT
        state_name,
        CASE
            WHEN atmospheric_conditions_1_name = 'Rain' THEN 'Rain'
            WHEN atmospheric_conditions_1_name = 'Clear' THEN 'Clear'
            ELSE 'Other'
        END AS Weather_Condition,
        COUNT(DISTINCT consecutive_number) AS num_accidents
    FROM
        `bigquery-public-data.nhtsa_traffic_fatalities.accident_2016`
    WHERE
        EXTRACT(DAYOFWEEK FROM timestamp_of_crash) IN (1, 7)  -- 1 = Sunday, 7 = Saturday
        AND atmospheric_conditions_1_name IN ('Rain', 'Clear')
    GROUP BY
        state_name, Weather_Condition
),

weather_difference AS (
    SELECT
        state_name,
        MAX(CASE WHEN Weather_Condition = 'Rain' THEN num_accidents ELSE 0 END) AS Rain_Accidents,
        MAX(CASE WHEN Weather_Condition = 'Clear' THEN num_accidents ELSE 0 END) AS Clear_Accidents,
        ABS(MAX(CASE WHEN Weather_Condition = 'Rain' THEN num_accidents ELSE 0 END) -
            MAX(CASE WHEN Weather_Condition = 'Clear' THEN num_accidents ELSE 0 END)) AS Difference
    FROM
        weekend_accidents
    GROUP BY
        state_name
)

SELECT
    state_name,
    Difference
FROM
    weather_difference
ORDER BY
    Difference DESC
LIMIT 3;

```

## bq397.sql

```sql
WITH tmp AS (
  SELECT DISTINCT *
  FROM `data-to-insights.ecommerce.rev_transactions`
  -- Removing duplicated values
),
tmp1 AS (
  SELECT 
    tmp.channelGrouping,
    tmp.geoNetwork_country,
    SUM(tmp.totals_transactions) AS tt
  FROM tmp
  GROUP BY 1, 2
),
tmp2 AS (
  SELECT 
    channelGrouping,
    geoNetwork_country,
    SUM(tt) AS TotalTransaction,
    COUNT(DISTINCT geoNetwork_country) OVER (PARTITION BY channelGrouping) AS CountryCount
  FROM tmp1
  GROUP BY channelGrouping, geoNetwork_country
),
tmp3 AS (
  SELECT
    channelGrouping,
    geoNetwork_country AS Country,
    TotalTransaction,
    RANK() OVER (PARTITION BY channelGrouping ORDER BY TotalTransaction DESC) AS rnk
  FROM tmp2
  WHERE CountryCount > 1
)
SELECT
  channelGrouping,
  Country,
  TotalTransaction
FROM tmp3
WHERE rnk = 1;

```

## bq398.sql

```sql
WITH russia_Data as (
SELECT distinct 
  id.country_name,
  id.value, --format in DataStudio
  id.indicator_name
FROM (
  SELECT
    country_code,
    region
  FROM
    bigquery-public-data.world_bank_intl_debt.country_summary
  WHERE
    region != "" ) cs --aggregated countries do not have a region
INNER JOIN (
  SELECT
    country_code,
    country_name,
    value, 
    indicator_name
  FROM
    bigquery-public-data.world_bank_intl_debt.international_debt
  WHERE true
    and country_code = 'RUS'  
     ) id
ON
  cs.country_code = id.country_code
WHERE value is not null
ORDER BY
  id.value DESC
)
SELECT 
    indicator_name
FROM russia_data
LIMIT 3;

```

## bq399.sql

```sql
WITH country_data AS ( 
  SELECT 
    country_code, 
    short_name AS country,
    region, 
    income_group 
  FROM 
    bigquery-public-data.world_bank_wdi.country_summary
)
, birth_rate_data AS (
  SELECT 
    data.country_code, 
    country_data.country,
    country_data.region,
    AVG(value) AS avg_birth_rate
  FROM 
    bigquery-public-data.world_bank_wdi.indicators_data data 
  LEFT JOIN 
    country_data 
  ON 
    data.country_code = country_data.country_code
  WHERE 
    indicator_code = "SP.DYN.CBRT.IN" -- Birth Rate
    AND EXTRACT(YEAR FROM PARSE_DATE('%Y', CAST(year AS STRING))) BETWEEN 1980 AND 1989 -- 1980s
    AND country_data.income_group = "High income" -- High-income group
  GROUP BY 
    data.country_code, 
    country_data.country,
    country_data.region
)
, ranked_birth_rates AS (
  SELECT
    region,
    country,
    avg_birth_rate,
    RANK() OVER(PARTITION BY region ORDER BY avg_birth_rate DESC) AS rank
  FROM
    birth_rate_data
)
SELECT 
  region, 
  country, 
  avg_birth_rate
FROM 
  ranked_birth_rates
WHERE 
  rank = 1
ORDER BY 
  region;

```

## bq400.sql

```sql
WITH SelectedStops AS (
  SELECT 
      stop_id,
      stop_name
  FROM 
      `bigquery-public-data.san_francisco_transit_muni.stops`
  WHERE 
      stop_name IN ('Clay St & Drumm St', 'Sacramento St & Davis St')
),
FilteredStopTimes AS (
  SELECT 
      st.trip_id, 
      st.stop_id, 
      st.arrival_time, 
      st.departure_time, 
      st.stop_sequence, 
      ss.stop_name
  FROM 
      `bigquery-public-data.san_francisco_transit_muni.stop_times` st
  JOIN 
      SelectedStops ss ON CAST(st.stop_id AS STRING) = ss.stop_id
)
SELECT
    t.trip_headsign,
    MIN(st1.departure_time) AS start_time,
    MAX(st2.arrival_time) AS end_time
FROM 
    `bigquery-public-data.san_francisco_transit_muni.trips` t
JOIN FilteredStopTimes st1 ON t.trip_id = CAST(st1.trip_id AS STRING) AND st1.stop_name = 'Clay St & Drumm St'
JOIN FilteredStopTimes st2 ON t.trip_id = CAST(st2.trip_id AS STRING) AND st2.stop_name = 'Sacramento St & Davis St'
WHERE 
    st1.stop_sequence < st2.stop_sequence
GROUP BY 
    t.trip_headsign;

```

## bq402.sql

```sql
WITH visitors AS (
  SELECT
    COUNT(DISTINCT fullVisitorId) AS total_visitors
  FROM 
    `data-to-insights.ecommerce.web_analytics`
),

purchasers AS (
  SELECT
    COUNT(DISTINCT fullVisitorId) AS total_purchasers
  FROM 
    `data-to-insights.ecommerce.web_analytics`
  WHERE 
    totals.transactions IS NOT NULL
),

transactions AS (
  SELECT
    COUNT(*) AS total_transactions,
    AVG(totals.transactions) AS avg_transactions_per_purchaser
  FROM 
    `data-to-insights.ecommerce.web_analytics`
  WHERE 
    totals.transactions IS NOT NULL
)

SELECT
  p.total_purchasers / v.total_visitors AS conversion_rate,
  a.avg_transactions_per_purchaser AS avg_transactions_per_purchaser
FROM
  visitors v,
  purchasers p,
  transactions a;

```

## bq403.sql

```sql
WITH RankedData AS (
    SELECT
        CONCAT("20", _TABLE_SUFFIX) AS year_filed,
        totrevenue,
        totfuncexpns,
        ROW_NUMBER() OVER (PARTITION BY CONCAT("20", _TABLE_SUFFIX) ORDER BY totrevenue) 
        AS revenue_rank,
        ROW_NUMBER() OVER (PARTITION BY CONCAT("20", _TABLE_SUFFIX) ORDER BY totfuncexpns) 
        AS expense_rank,
        COUNT(*) OVER (PARTITION BY CONCAT("20", _TABLE_SUFFIX)) AS total_count
    FROM 
        `bigquery-public-data.irs_990.irs_990_20*`
),

YearlyMedians AS (
    SELECT
        year_filed,
        IF(MOD(total_count, 2) = 1, 
           MAX(CASE WHEN revenue_rank = (total_count + 1) / 2 THEN totrevenue END),
           AVG(CASE WHEN revenue_rank IN ((total_count / 2), (total_count / 2) + 1) THEN totrevenue END)
        ) AS median_revenue,
        IF(MOD(total_count, 2) = 1, 
           MAX(CASE WHEN expense_rank = (total_count + 1) / 2 THEN totfuncexpns END),
           AVG(CASE WHEN expense_rank IN ((total_count / 2), (total_count / 2) + 1) THEN totfuncexpns END)
        ) AS median_expense
    FROM
        RankedData
    GROUP BY
        year_filed, total_count
),

DifferenceCalculations AS (
    SELECT
        year_filed,
        median_revenue,
        median_expense,
        ABS(median_revenue - median_expense) AS difference
    FROM
        YearlyMedians
)

SELECT
    year_filed,
    difference
FROM
    DifferenceCalculations
WHERE
    year_filed BETWEEN '2012' AND '2017'
ORDER BY
    difference ASC
LIMIT 3;

```

## bq406.sql

```sql
CREATE TEMP FUNCTION GrowthRate(end_value FLOAT64, begin_value FLOAT64)
RETURNS FLOAT64
AS ((end_value - begin_value) / begin_value);

SELECT
  GrowthRate(SUM(IF(report_year=2024, race_asian, 0)),
             SUM(IF(report_year=2014, race_asian, 0))) AS race_asian_growth,
  GrowthRate(SUM(IF(report_year=2024, race_black, 0)),
             SUM(IF(report_year=2014, race_black, 0))) AS race_black_growth,
  GrowthRate(SUM(IF(report_year=2024, race_hispanic_latinx, 0)),
             SUM(IF(report_year=2014, race_hispanic_latinx, 0))) AS race_hispanic_growth,
  GrowthRate(SUM(IF(report_year=2024, race_native_american, 0)),
             SUM(IF(report_year=2014, race_native_american, 0))) AS race_native_american_growth,
  GrowthRate(SUM(IF(report_year=2024, race_white, 0)),
             SUM(IF(report_year=2014, race_white, 0))) AS race_white_growth,
  GrowthRate(SUM(IF(report_year=2024, gender_us_women, 0)),
             SUM(IF(report_year=2014, gender_us_women, 0))) AS gender_us_women_growth,
  GrowthRate(SUM(IF(report_year=2024, gender_us_men, 0)),
             SUM(IF(report_year=2014, gender_us_men, 0))) AS gender_us_men_growth,
  GrowthRate(SUM(IF(report_year=2024, gender_global_women, 0)),
             SUM(IF(report_year=2014, gender_global_women, 0))) AS gender_global_women_growth,
  GrowthRate(SUM(IF(report_year=2024, gender_global_men, 0)),
             SUM(IF(report_year=2014, gender_global_men, 0))) AS gender_global_men_growth
FROM `bigquery-public-data.google_dei.dar_non_intersectional_representation`
WHERE report_year IN (2014, 2024)
  AND workforce = 'overall';

```

## bq407.sql

```sql
WITH population_data AS (
  SELECT
    geo_id,
    median_age,
    total_pop
  FROM
    `bigquery-public-data.census_bureau_acs.county_2020_5yr`
  WHERE
    total_pop > 50000
),
covid_data AS (
  SELECT
    county_fips_code,
    county_name,
    state,
    SUM(confirmed_cases) AS total_cases,
    SUM(deaths) AS total_deaths
  FROM
    `bigquery-public-data.covid19_usafacts.summary`
  WHERE
    date = '2020-08-27'
  GROUP BY
    county_fips_code, county_name, state
)
SELECT
  covid.county_name,
  covid.state,
  pop.median_age,
  pop.total_pop,
  (covid.total_cases / pop.total_pop * 100000) AS confirmed_cases_per_100000,
  (covid.total_deaths / pop.total_pop * 100000) AS deaths_per_100000,
  (covid.total_deaths / covid.total_cases * 100) AS case_fatality_rate
FROM
  covid_data covid
JOIN
  population_data pop ON covid.county_fips_code = pop.geo_id
ORDER BY
  case_fatality_rate DESC
LIMIT 3;

```

## bq413.sql

```sql
SELECT
   COALESCE(p.journal.title, p.proceedings_title.preferred, p.book_title.preferred, p.book_series_title.preferred) AS venue,
FROM
   `bigquery-public-data.dimensions_ai_covid19.publications` p
LEFT JOIN
   UNNEST(research_orgs) AS research_orgs_grids
LEFT JOIN
   `bigquery-public-data.dimensions_ai_covid19.grid` grid
ON
   grid.id=research_orgs_grids
WHERE
   EXTRACT(YEAR FROM date_inserted) >= 2021
   AND
   grid.address.city = 'Qianjiang'
```

## bq414.sql

```sql
SELECT 
  a.object_id,
  a.title,
  FORMAT_TIMESTAMP('%Y-%m-%d', a.metadata_date) AS formatted_metadata_date
FROM `bigquery-public-data.the_met.objects` a
JOIN (
  SELECT object_id,
         cropHints.confidence AS cropConfidence
  FROM `bigquery-public-data.the_met.vision_api_data`, 
       UNNEST(cropHintsAnnotation.cropHints) cropHints
) b
ON a.object_id = b.object_id
WHERE a.department = "The Libraries"
AND b.cropConfidence > 0.5
AND a.title LIKE "%book%"
```

## bq419.sql

```sql
WITH s80 as
  (SELECT state, COUNT(event_id) as num_events
  FROM `bigquery-public-data.noaa_historic_severe_storms.storms_1980` 
  GROUP BY state 
  ORDER BY num_events DESC
  LIMIT 1000),
s81 as
(SELECT state, COUNT(event_id) as num_events
  FROM `bigquery-public-data.noaa_historic_severe_storms.storms_1981` 
  GROUP BY state 
  ORDER BY num_events DESC
  LIMIT 1000),
s82 as
  (SELECT state, COUNT(event_id) as num_events
  FROM `bigquery-public-data.noaa_historic_severe_storms.storms_1982` 
  GROUP BY state 
  ORDER BY num_events DESC
  LIMIT 1000),

s83 as
  (SELECT state, COUNT(event_id) as num_events
  FROM `bigquery-public-data.noaa_historic_severe_storms.storms_1983` 
  GROUP BY state 
  ORDER BY num_events DESC
  LIMIT 1000),

s84 as
  (SELECT state, COUNT(event_id) as num_events
  FROM `bigquery-public-data.noaa_historic_severe_storms.storms_1984` 
  GROUP BY state 
  ORDER BY num_events DESC
  LIMIT 1000),

s85 as
  (SELECT state, COUNT(event_id) as num_events
  FROM `bigquery-public-data.noaa_historic_severe_storms.storms_1985` 
  GROUP BY state 
  ORDER BY num_events DESC
  LIMIT 1000),

s86 as
  (SELECT state, COUNT(event_id) as num_events
  FROM `bigquery-public-data.noaa_historic_severe_storms.storms_1986` 
  GROUP BY state 
  ORDER BY num_events DESC
  LIMIT 1000),

s87 as
  (SELECT state, COUNT(event_id) as num_events
  FROM `bigquery-public-data.noaa_historic_severe_storms.storms_1987` 
  GROUP BY state 
  ORDER BY num_events DESC
  LIMIT 1000),

s88 as
  (SELECT state, COUNT(event_id) as num_events
  FROM `bigquery-public-data.noaa_historic_severe_storms.storms_1988` 
  GROUP BY state 
  ORDER BY num_events DESC
  LIMIT 1000),

s89 as
  (SELECT state, COUNT(event_id) as num_events
  FROM `bigquery-public-data.noaa_historic_severe_storms.storms_1989` 
  GROUP BY state 
  ORDER BY num_events DESC
  LIMIT 1000),

s90 as
  (SELECT state, COUNT(event_id) as num_events
  FROM `bigquery-public-data.noaa_historic_severe_storms.storms_1990` 
  GROUP BY state 
  ORDER BY num_events DESC
  LIMIT 1000),

s91 as
  (SELECT state, COUNT(event_id) as num_events
  FROM `bigquery-public-data.noaa_historic_severe_storms.storms_1991` 
  GROUP BY state 
  ORDER BY num_events DESC
  LIMIT 1000),
s92 as
  (SELECT state, COUNT(event_id) as num_events
  FROM `bigquery-public-data.noaa_historic_severe_storms.storms_1992` 
  GROUP BY state 
  ORDER BY num_events DESC
  LIMIT 1000),

s93 as
  (SELECT state, COUNT(event_id) as num_events
  FROM `bigquery-public-data.noaa_historic_severe_storms.storms_1993` 
  GROUP BY state 
  ORDER BY num_events DESC
  LIMIT 1000),

s94 as
  (SELECT state, COUNT(event_id) as num_events
  FROM `bigquery-public-data.noaa_historic_severe_storms.storms_1994` 
  GROUP BY state 
  ORDER BY num_events DESC
  LIMIT 1000),

s95 as
  (SELECT state, COUNT(event_id) as num_events
  FROM `bigquery-public-data.noaa_historic_severe_storms.storms_1995` 
  GROUP BY state 
  ORDER BY num_events DESC
  LIMIT 1000)

SELECT s80.state, 
s80.num_events + s81.num_events +  s82.num_events +  s83.num_events +  s84.num_events +  s85.num_events +  s86.num_events +  s87.num_events + s88.num_events +  s89.num_events +  s90.num_events + s91.num_events + s92.num_events + s93.num_events + s94.num_events + s95.num_events as total_events 
FROM s80 FULL JOIN s81 ON s80.state = s81.state
FULL JOIN s82 ON s82.state = s81.state
FULL JOIN s83 ON s83.state = s81.state
FULL JOIN s84 ON s84.state = s81.state
FULL JOIN s85 ON s85.state = s81.state
FULL JOIN s86 ON s86.state = s81.state
FULL JOIN s87 ON s87.state = s81.state
FULL JOIN s88 ON s88.state = s81.state
FULL JOIN s89 ON s89.state = s81.state
FULL JOIN s90 ON s90.state = s81.state
FULL JOIN s91 ON s91.state = s81.state 
FULL JOIN s92 ON s92.state = s81.state
FULL JOIN s93 ON s93.state = s81.state
FULL JOIN s94 ON s94.state = s81.state
FULL JOIN s95 ON s95.state = s81.state

ORDER BY total_events DESC
LIMIT 5;

```

## bq424.sql

```sql
SELECT DISTINCT
  id.country_name,
  --cs.region,
  id.value AS debt,
  --id.indicator_code
FROM (
  SELECT
    country_code,
    region
  FROM
    `bigquery-public-data.world_bank_intl_debt.country_summary`
  WHERE
    region != "" ) cs
INNER JOIN (
  SELECT
    country_code,
    country_name,
    value,
    indicator_code
  FROM
    `bigquery-public-data.world_bank_intl_debt.international_debt`
  WHERE
    indicator_code = "DT.AMT.DLXF.CD") id

ON
  cs.country_code = id.country_code
ORDER BY
  id.value DESC
  LIMIT 10
```

## bq425.sql

```sql
SELECT *
  FROM (
  SELECT
  molregno,
  comp.company,
  prod.trade_name,
  prod.approval_date,
  ROW_NUMBER() OVER(PARTITION BY molregno ORDER BY PARSE_DATE('%Y-%m-%d', prod.approval_date) DESC) rn
  FROM bigquery-public-data.ebi_chembl.compound_records_23 AS cmpd_rec
  JOIN bigquery-public-data.ebi_chembl.molecule_synonyms_23 AS ms USING (molregno)
  JOIN bigquery-public-data.ebi_chembl.research_companies_23 AS comp USING (res_stem_id)
  JOIN bigquery-public-data.ebi_chembl.formulations_23 AS form USING (molregno)
  JOIN bigquery-public-data.ebi_chembl.products_23 AS prod USING (product_id)
  ) as subq
 WHERE rn = 1 AND company = 'SanofiAventis'
```

## bq428.sql

```sql
WITH top_teams AS (
  SELECT
    team_market
  FROM (
    SELECT
      team_market,
      player_id AS id,
      SUM(points_scored)
    FROM
      `bigquery-public-data.ncaa_basketball.mbb_pbp_sr`
    WHERE
      season >= 2010 AND season <=2018 AND period = 2
    GROUP BY
      game_id,
      team_market,
      player_id
    HAVING
      SUM(points_scored) >= 15) C
  GROUP BY
    team_market
  HAVING
    COUNT(DISTINCT id) > 5
  ORDER BY
    COUNT(DISTINCT id) DESC
  LIMIT 5
)


SELECT
  season,
  round,
  days_from_epoch,
  game_date,
  day,
  'win' AS label,
  win_seed AS seed,
  win_market AS market,
  win_name AS name,
  win_alias AS alias,
  win_school_ncaa AS school_ncaa,
  lose_seed AS opponent_seed,
  lose_market AS opponent_market,
  lose_name AS opponent_name,
  lose_alias AS opponent_alias,
  lose_school_ncaa AS opponent_school_ncaa
FROM `bigquery-public-data.ncaa_basketball.mbb_historical_tournament_games`
JOIN top_teams ON top_teams.team_market = win_market
WHERE season >= 2010 AND season <=2018

UNION ALL

SELECT
  season,
  round,
  days_from_epoch,
  game_date,
  day,
  'loss' AS label,
  lose_seed AS seed,
  lose_market AS market,
  lose_name AS name,
  lose_alias AS alias,
  lose_school_ncaa AS school_ncaa,
  win_seed AS opponent_seed,
  win_market AS opponent_market,
  win_name AS opponent_name,
  win_alias AS opponent_alias,
  win_school_ncaa AS opponent_school_ncaa
FROM `bigquery-public-data.ncaa_basketball.mbb_historical_tournament_games`
JOIN top_teams ON top_teams.team_market = lose_market
WHERE season >= 2010 AND season <=2018

```

## bq430.sql

```sql
select 
  -- *, 
  greatest(heavy_atoms_1, heavy_atoms_2) as heavy_atoms_greatest,
  greatest(publication_date_1, publication_date_2) as publication_date_greatest,
  greatest(doc_id_1, doc_id_2) as doc_id_greatest,
  case 
    when 
      standard_value_1 > standard_value_2 and 
      standard_relation_1 not in ('<', '<<') and 
      standard_relation_2 not in ('>', '>>')
    then 'decrease'
    when
      standard_value_1 < standard_value_2 and 
      standard_relation_1 not in ('>', '>>') and 
      standard_relation_2 not in ('<', '<<') 
    then 'increase'
    when
      standard_value_1 = standard_value_2 and 
      standard_relation_1 in ('=', '~') and 
      standard_relation_2 in ('=', '~') 
    then 'no-change'
    else null
  end as standard_change,
  to_hex(md5(to_json_string(struct(activity_id_1, activity_id_2)))) as mmp_delta_uuid,
  to_hex(md5(to_json_string(struct(canonical_smiles_1, canonical_smiles_2, 5)))) as mmp_search_uuid
from (
  select 
    act.assay_id,
    act.standard_type,
    act.activity_id as activity_id_1,
    cast(act.standard_value as numeric) as standard_value_1,
    act.standard_relation as standard_relation_1,
    cast(act.pchembl_value as numeric) as pchembl_value_1,
    count(*) over (partition by act.assay_id) as count_activities_1,
    count(*) over (partition by act.assay_id, act.molregno) as duplicate_activities_1,
    act.molregno as molregno_1,
    com.canonical_smiles as canonical_smiles_1,
    cast(cmp.heavy_atoms as int64) as heavy_atoms_1,
    cast(d.doc_id as int64) as doc_id_1,
    date(
      coalesce(cast(d.year as int64), 1970), 
      coalesce(cast(floor(percent_rank() over (
        partition by d.journal, d.year order by SAFE_CAST(d.first_page as int64)) * 11) as int64) + 1, 1),
      coalesce(mod(cast(floor(percent_rank() over (
        partition by d.journal, d.year order by SAFE_CAST(d.first_page as int64)) * 308) as int64), 28) + 1, 1)) as publication_date_1
  FROM `bigquery-public-data.ebi_chembl.activities_29` act
  join `bigquery-public-data.ebi_chembl.compound_structures_29` com using (molregno)
  join `bigquery-public-data.ebi_chembl.compound_properties_29` cmp using (molregno)
  left join `bigquery-public-data.ebi_chembl.docs_29` d using (doc_id)
  where standard_type in (select distinct standard_type from`bigquery-public-data.ebi_chembl.activities_29` where pchembl_value is not null)
  ) a1
join (
  select 
    act.assay_id,
    act.standard_type,
    act.activity_id as activity_id_2,
    cast(act.standard_value as numeric) as standard_value_2,
    act.standard_relation as standard_relation_2,
    cast(act.pchembl_value as numeric) as pchembl_value_2,
    count(*) over (partition by act.assay_id) as count_activities_2,
    count(*) over (partition by act.assay_id, act.molregno) as duplicate_activities_2, 
    act.molregno as molregno_2,
    com.canonical_smiles as canonical_smiles_2, 
    cast(cmp.heavy_atoms as int64) as heavy_atoms_2,
    cast(d.doc_id as int64) as doc_id_2,
    date(
      coalesce(cast(d.year as int64), 1970), 
      coalesce(cast(floor(percent_rank() over (
        partition by d.journal, d.year order by SAFE_CAST(d.first_page as int64)) * 11) as int64) + 1, 1),
      coalesce(mod(cast(floor(percent_rank() over (
        partition by d.journal, d.year order by SAFE_CAST(d.first_page as int64)) * 308) as int64), 28) + 1, 1)) as publication_date_2
  FROM `bigquery-public-data.ebi_chembl.activities_29` act
  join `bigquery-public-data.ebi_chembl.compound_structures_29` com using (molregno)
  join `bigquery-public-data.ebi_chembl.compound_properties_29` cmp using (molregno)
  left join `bigquery-public-data.ebi_chembl.docs_29` d using (doc_id)
  where standard_type in (select distinct standard_type from`bigquery-public-data.ebi_chembl.activities_29` where pchembl_value is not null)
  ) a2 using (assay_id, standard_type)
where 
  a1.molregno_1 != a2.molregno_2 and
  a1.count_activities_1 < 5 and 
  a2.count_activities_2 < 5 and 
  a1.heavy_atoms_1 between 10 and 15 and
  a2.heavy_atoms_2 between 10 and 15 and
  a1.standard_value_1 is not null and 
  a2.standard_value_2 is not null and
  a1.duplicate_activities_1 < 2 and
  a2.duplicate_activities_2 < 2 and
  a1.pchembl_value_1 > 10 and
  a2.pchembl_value_2 > 10


```

## bq442.sql

```sql
SELECT
  OrderID AS tradeID,
  MaturityDate AS tradeTimestamp,
  (
    CASE SUBSTR(TargetCompID, 0, 4)
      WHEN 'MOMO' THEN 'Momentum'
      WHEN 'LUCK' THEN 'Feeling Lucky'
      WHEN 'PRED' THEN 'Prediction'
  END
    ) AS algorithm,
  Symbol AS symbol,
  LastPx AS openPrice,
  StrikePrice AS closePrice,
  (
  SELECT
    Side
  FROM
    UNNEST(Sides)
  ) AS tradeDirection,
  (CASE (
    SELECT
      Side
    FROM
      UNNEST(Sides))
      WHEN 'SHORT' THEN -1
      WHEN 'LONG' THEN 1
  END
    ) AS tradeMultiplier
FROM
  `bigquery-public-data.cymbal_investments.trade_capture_report`cv
ORDER BY closePrice DESC
LIMIT 6
```

## bq452.sql

```sql
SELECT *
FROM (
  SELECT
    `start`,
    `end`,
    ROUND(
      POW(ABS(case_ref_count - (ref_count / allele_count) * case_count) - 0.5, 2) / ((ref_count / allele_count) * case_count) +
      POW(ABS(control_ref_count - (ref_count / allele_count) * control_count) - 0.5, 2) / ((ref_count / allele_count) * control_count) +
      POW(ABS(case_alt_count - (alt_count / allele_count) * case_count) - 0.5, 2) / ((alt_count / allele_count) * case_count) +
      POW(ABS(control_alt_count - (alt_count / allele_count) * control_count) - 0.5, 2) / ((alt_count / allele_count) * control_count),
      3
    ) AS chi_squared_score
  FROM (
    SELECT
      reference_name,
      `start`,
      `end`,
      reference_bases,
      alternate_bases,
      vt,
      SUM(ref_count + alt_count) AS allele_count,
      SUM(ref_count) AS ref_count,
      SUM(alt_count) AS alt_count,
      SUM(IF(is_case, CAST(ref_count + alt_count AS INT64), 0)) AS case_count,
      SUM(IF(NOT is_case, CAST(ref_count + alt_count AS INT64), 0)) AS control_count,
      SUM(IF(is_case, ref_count, 0)) AS case_ref_count,
      SUM(IF(is_case, alt_count, 0)) AS case_alt_count,
      SUM(IF(NOT is_case, ref_count, 0)) AS control_ref_count,
      SUM(IF(NOT is_case, alt_count, 0)) AS control_alt_count
    FROM (
      SELECT
        v.reference_name,
        v.`start`,
        v.`end`,
        v.reference_bases,
        v.alternate_bases,
        v.vt,
        ('EAS' = p.super_population) AS is_case,
        IF(call.genotype[SAFE_OFFSET(0)] = 0, 1, 0) AS ref_count,
        IF(call.genotype[SAFE_OFFSET(0)] = 1, 1, 0) AS alt_count
      FROM
        `spider2-public-data.1000_genomes.variants` AS v,
        UNNEST(v.call) AS call
      JOIN
        `spider2-public-data.1000_genomes.sample_info` AS p
      ON
        call.call_set_name = p.sample
      WHERE
        v.reference_name = '12'
    )
    GROUP BY
      reference_name,
      `start`,
      `end`,
      reference_bases,
      alternate_bases,
      vt
  )
  WHERE
    (ref_count / allele_count) * case_count >= 5.0
    AND (ref_count / allele_count) * control_count >= 5.0
    AND (alt_count / allele_count) * case_count >= 5.0
    AND (alt_count / allele_count) * control_count >= 5.0
)
WHERE
  chi_squared_score >= 29.71679
ORDER BY
  chi_squared_score DESC
```

## bq453.sql

```sql
SELECT
  reference_name,
  start,
  `END`,
  reference_bases,
  alt,
  vt,
  POW(hom_ref_count - expected_hom_ref_count, 2) / expected_hom_ref_count +
    POW(hom_alt_count - expected_hom_alt_count, 2) / expected_hom_alt_count +
    POW(het_count - expected_het_count, 2) / expected_het_count AS chi_squared_score,
  total_count,
  hom_ref_count,
  expected_hom_ref_count AS expected_hom_ref_count,
  het_count,
  expected_het_count AS expected_het_count,
  hom_alt_count,
  expected_hom_alt_count AS expected_hom_alt_count,
  alt_freq AS alt_freq,
  alt_freq_from_1KG
FROM (
  SELECT
    reference_name,
    start,
    `END`,
    reference_bases,
    alt,
    vt,
    alt_freq_from_1KG,
    hom_ref_freq + (0.5 * het_freq) AS hw_ref_freq,
    1 - (hom_ref_freq + (0.5 * het_freq)) AS alt_freq,
    POW(hom_ref_freq + (0.5 * het_freq), 2) * total_count AS expected_hom_ref_count,
    POW(1 - (hom_ref_freq + (0.5 * het_freq)), 2) * total_count AS expected_hom_alt_count,
    2 * (hom_ref_freq + (0.5 * het_freq)) * (1 - (hom_ref_freq + (0.5 * het_freq))) * total_count AS expected_het_count,
    total_count,
    hom_ref_count,
    het_count,
    hom_alt_count,
    hom_ref_freq,
    het_freq,
    hom_alt_freq
  FROM (
    SELECT
      reference_name,
      start,
      `END`,
      reference_bases,
      STRING_AGG(DISTINCT alternate_base) AS alt,
      vt,
      af AS alt_freq_from_1KG,
      COUNTIF(first_allele IN (0, 1) AND second_allele IN (0, 1)) AS total_count,
      COUNTIF(first_allele = 0 AND second_allele = 0) AS hom_ref_count,
      COUNTIF((first_allele = 0 AND second_allele = 1) OR (first_allele = 1 AND second_allele = 0)) AS het_count,
      COUNTIF(first_allele = 1 AND second_allele = 1) AS hom_alt_count,
      SAFE_DIVIDE(COUNTIF(first_allele = 0 AND second_allele = 0), COUNTIF(first_allele IN (0, 1) AND second_allele IN (0, 1))) AS hom_ref_freq,
      SAFE_DIVIDE(COUNTIF((first_allele = 0 AND second_allele = 1) OR (first_allele = 1 AND second_allele = 0)), COUNTIF(first_allele IN (0, 1) AND second_allele IN (0, 1))) AS het_freq,
      SAFE_DIVIDE(COUNTIF(first_allele = 1 AND second_allele = 1), COUNTIF(first_allele IN (0, 1) AND second_allele IN (0, 1))) AS hom_alt_freq
    FROM (
      SELECT
        reference_name,
        start,
        `END`,
        reference_bases,
        vt,
        af,
        call.call_set_name,
        call.genotype[OFFSET(0)] AS first_allele,
        call.genotype[OFFSET(1)] AS second_allele,
        alternate_base
      FROM
        `spider2-public-data.1000_genomes.variants`,
        UNNEST(call) AS call,
        UNNEST(alternate_bases) AS alternate_base
      WHERE
        reference_name = '17'
        AND start BETWEEN 41196311 AND 41277499
    )
    GROUP BY
      reference_name,
      start,
      `END`,
      reference_bases,
      vt,
      af
  )
)

```

# ga

## ga001.sql

```sql
WITH
  Params AS (
    SELECT 'Google Navy Speckled Tee' AS selected_product
  ),
  PurchaseEvents AS (
    SELECT
      user_pseudo_id,
      items
    FROM
      `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE
      _TABLE_SUFFIX BETWEEN '20201201' AND '20201231'
      AND event_name = 'purchase'
  ),
  ProductABuyers AS (
    SELECT DISTINCT
      user_pseudo_id
    FROM
      Params,
      PurchaseEvents,
      UNNEST(items) AS items
    WHERE
      items.item_name = selected_product
  )
SELECT
  items.item_name AS item_name,
  SUM(items.quantity) AS item_quantity
FROM
  Params,
  PurchaseEvents,
  UNNEST(items) AS items
WHERE
  user_pseudo_id IN (SELECT user_pseudo_id FROM ProductABuyers)
  AND items.item_name != selected_product
GROUP BY 1
ORDER BY item_quantity DESC
LIMIT 1;

```

## ga002.sql

```sql
WITH
Params AS (
  SELECT 'Google Red Speckled Tee' AS selected_product
),
DateRanges AS (
  SELECT '20201101' AS start_date, '20201130' AS end_date, '202011' AS period UNION ALL
  SELECT '20201201', '20201231', '202012' UNION ALL
  SELECT '20210101', '20210131', '202101'
),
PurchaseEvents AS (
  SELECT
    period,
    user_pseudo_id,
    items
  FROM
    DateRanges
  JOIN
    `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    ON _TABLE_SUFFIX BETWEEN start_date AND end_date
  WHERE
    event_name = 'purchase'
),
ProductABuyers AS (
  SELECT DISTINCT
    period,
    user_pseudo_id
  FROM
    Params,
    PurchaseEvents,
    UNNEST(items) AS items
  WHERE
    items.item_name = selected_product
),
TopProducts AS (
  SELECT
    pe.period,
    items.item_name AS item_name,
    SUM(items.quantity) AS item_quantity
  FROM
    Params,
    PurchaseEvents pe,
    UNNEST(items) AS items
  WHERE
    user_pseudo_id IN (SELECT user_pseudo_id FROM ProductABuyers pb WHERE pb.period = pe.period)
    AND items.item_name != selected_product
  GROUP BY
    pe.period, items.item_name
),
TopProductPerPeriod AS (
  SELECT
    period,
    item_name,
    item_quantity
  FROM (
    SELECT
      period,
      item_name,
      item_quantity,
      RANK() OVER (PARTITION BY period ORDER BY item_quantity DESC) AS rank
    FROM
      TopProducts
  )
  WHERE
    rank = 1
)
SELECT
  period,
  item_name,
  item_quantity
FROM
  TopProductPerPeriod
ORDER BY
  period;

```

## ga003.sql

```sql
WITH EventData AS (
    SELECT 
        user_pseudo_id, 
        event_timestamp, 
        param
    FROM 
        `firebase-public-project.analytics_153293282.events_20180915`,
        UNNEST(event_params) AS param
    WHERE 
        event_name = "level_complete_quickplay"
        AND (param.key = "value" OR param.key = "board")
),
ProcessedData AS (
    SELECT 
        user_pseudo_id, 
        event_timestamp, 
        MAX(IF(param.key = "value", param.value.int_value, NULL)) AS score,
        MAX(IF(param.key = "board", param.value.string_value, NULL)) AS board_type
    FROM 
        EventData
    GROUP BY 
        user_pseudo_id, 
        event_timestamp
)
SELECT 
    ANY_VALUE(board_type) AS board, 
    AVG(score) AS average_score
FROM 
    ProcessedData
GROUP BY 
    board_type

```

## ga004.sql

```sql
WITH
  UserInfo AS (
    SELECT
      user_pseudo_id,
      COUNTIF(event_name = 'page_view') AS page_view_count,
      COUNTIF(event_name IN ('in_app_purchase', 'purchase')) AS purchase_event_count
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE _TABLE_SUFFIX BETWEEN '20201201' AND '20201231'
    GROUP BY 1
  ),
  Averages AS (
    SELECT
      (purchase_event_count > 0) AS purchaser,
      COUNT(*) AS user_count,
      SUM(page_view_count) AS total_page_views,
      SUM(page_view_count) / COUNT(*) AS avg_page_views
    FROM UserInfo
    GROUP BY 1
  )

SELECT
  MAX(CASE WHEN purchaser THEN avg_page_views ELSE 0 END) -
  MAX(CASE WHEN NOT purchaser THEN avg_page_views ELSE 0 END) AS avg_page_views_difference
FROM Averages;

```

## ga008.sql

```sql
WITH
  UserInfo AS (
    SELECT
      user_pseudo_id,
      PARSE_DATE('%Y%m%d', event_date) AS event_date,
      COUNTIF(event_name = 'page_view') AS page_view_count,
      COUNTIF(event_name = 'purchase') AS purchase_event_count
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20201130'
    GROUP BY 1, 2
  )
SELECT
  event_date,
  SUM(page_view_count) / COUNT(*) AS avg_page_views,
  SUM(page_view_count)
FROM UserInfo
WHERE purchase_event_count > 0
GROUP BY event_date
ORDER BY event_date;

```

## ga010.sql

```sql
WITH prep AS (
  SELECT
    user_pseudo_id,
    (SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'ga_session_id') AS session_id,
    ARRAY_AGG((SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'source') IGNORE NULLS 
              ORDER BY event_timestamp)[SAFE_OFFSET(0)] AS source,
    ARRAY_AGG((SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'medium') IGNORE NULLS 
              ORDER BY event_timestamp)[SAFE_OFFSET(0)] AS medium,
    ARRAY_AGG((SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'campaign') IGNORE NULLS 
              ORDER BY event_timestamp)[SAFE_OFFSET(0)] AS campaign
  FROM
    `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE
    _TABLE_SUFFIX BETWEEN '20201201' AND '20201231'
  GROUP BY
    user_pseudo_id,
    session_id
)
SELECT
  -- session default channel grouping (dimension | the channel group associated with a session) 
  CASE 
    WHEN source = '(direct)' AND (medium IN ('(not set)','(none)')) THEN 'Direct'
    WHEN REGEXP_CONTAINS(campaign, 'cross-network') THEN 'Cross-network'
    WHEN (REGEXP_CONTAINS(source,'alibaba|amazon|google shopping|shopify|etsy|ebay|stripe|walmart')
        OR REGEXP_CONTAINS(campaign, '^(.*(([^a-df-z]|^)shop|shopping).*)$'))
        AND REGEXP_CONTAINS(medium, '^(.*cp.*|ppc|paid.*)$') THEN 'Paid Shopping'
    WHEN REGEXP_CONTAINS(source,'baidu|bing|duckduckgo|ecosia|google|yahoo|yandex')
        AND REGEXP_CONTAINS(medium,'^(.*cp.*|ppc|paid.*)$') THEN 'Paid Search'
    WHEN REGEXP_CONTAINS(source,'badoo|facebook|fb|instagram|linkedin|pinterest|tiktok|twitter|whatsapp')
        AND REGEXP_CONTAINS(medium,'^(.*cp.*|ppc|paid.*)$') THEN 'Paid Social'
    WHEN REGEXP_CONTAINS(source,'dailymotion|disneyplus|netflix|youtube|vimeo|twitch|vimeo|youtube')
        AND REGEXP_CONTAINS(medium,'^(.*cp.*|ppc|paid.*)$') THEN 'Paid Video'
    WHEN medium IN ('display', 'banner', 'expandable', 'interstitial', 'cpm') THEN 'Display'
    WHEN REGEXP_CONTAINS(source,'alibaba|amazon|google shopping|shopify|etsy|ebay|stripe|walmart')
        OR REGEXP_CONTAINS(campaign, '^(.*(([^a-df-z]|^)shop|shopping).*)$') THEN 'Organic Shopping'
    WHEN REGEXP_CONTAINS(source,'badoo|facebook|fb|instagram|linkedin|pinterest|tiktok|twitter|whatsapp')
        OR medium IN ('social','social-network','social-media','sm','social network','social media') THEN 'Organic Social'
    WHEN REGEXP_CONTAINS(source,'dailymotion|disneyplus|netflix|youtube|vimeo|twitch|vimeo|youtube')
        OR REGEXP_CONTAINS(medium,'^(.*video.*)$') THEN 'Organic Video'
    WHEN REGEXP_CONTAINS(source,'baidu|bing|duckduckgo|ecosia|google|yahoo|yandex')
        OR medium = 'organic' THEN 'Organic Search'
    WHEN REGEXP_CONTAINS(source,'email|e-mail|e_mail|e mail')
        OR REGEXP_CONTAINS(medium,'email|e-mail|e_mail|e mail') THEN 'Email'
    WHEN medium = 'affiliate' THEN 'Affiliates'
    WHEN medium = 'referral' THEN 'Referral'
    WHEN medium = 'audio' THEN 'Audio'
    WHEN medium = 'sms' THEN 'SMS'
    WHEN medium LIKE '%push'
        OR REGEXP_CONTAINS(medium,'mobile|notification') THEN 'Mobile Push Notifications'
    ELSE 'Unassigned' 
  END AS channel_grouping_session
FROM
  prep
GROUP BY
  channel_grouping_session
ORDER BY
  COUNT(DISTINCT CONCAT(user_pseudo_id, session_id)) DESC
LIMIT 1 OFFSET 3
```

## ga012.sql

```sql
WITH top_category AS (
  SELECT
    product.item_category,
    SUM(ecommerce.tax_value_in_usd) / SUM(ecommerce.purchase_revenue_in_usd) AS tax_rate
  FROM
    bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_20201130,
    UNNEST(items) AS product
  WHERE
    event_name = 'purchase'
  GROUP BY
    product.item_category
  ORDER BY
    tax_rate DESC
  LIMIT 1
)

SELECT
    ecommerce.transaction_id,
    SUM(ecommerce.total_item_quantity) AS total_item_quantity,
    SUM(ecommerce.purchase_revenue_in_usd) AS purchase_revenue_in_usd,
    SUM(ecommerce.purchase_revenue) AS purchase_revenue
FROM
    bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_20201130, 
    UNNEST(items) AS product
JOIN top_category
ON product.item_category = top_category.item_category
WHERE
    event_name = 'purchase'
GROUP BY
    ecommerce.transaction_id;

```

## ga017.sql

```sql
WITH unnested_events AS (
  SELECT
    MAX(CASE WHEN event_params.key = 'page_location' THEN event_params.value.string_value END) AS page_location,
    user_pseudo_id,
    event_timestamp
  FROM
    `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`,
    UNNEST(event_params) AS event_params
  WHERE
    _TABLE_SUFFIX BETWEEN '20210101' AND '20210131'
    AND event_name = 'page_view'
  GROUP BY user_pseudo_id,event_timestamp
),
temp AS (
    SELECT
    page_location,
    COUNT(*) AS event_count,
    COUNT(DISTINCT user_pseudo_id) AS users
    FROM
    unnested_events
    GROUP BY page_location
    ORDER BY event_count DESC
)

SELECT users 
FROM
temp
LIMIT 1
```

## ga018.sql

```sql
WITH base_table AS (
  SELECT
    event_name,
    event_date,
    event_timestamp,
    user_pseudo_id,
    user_id,
    device,
    geo,
    traffic_source,
    event_params,
    user_properties
  FROM
    `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE
    _table_suffix = '20210102'
  AND event_name IN ('page_view')
)
, unnested_events AS (
-- unnests event parameters to get to relevant keys and values
  SELECT
    event_date AS date,
    event_timestamp AS event_timestamp_microseconds,
    user_pseudo_id,
    MAX(CASE WHEN c.key = 'ga_session_id' THEN c.value.int_value END) AS visitID,
    MAX(CASE WHEN c.key = 'ga_session_number' THEN c.value.int_value END) AS visitNumber,
    MAX(CASE WHEN c.key = 'page_title' THEN c.value.string_value END) AS page_title,
    MAX(CASE WHEN c.key = 'page_location' THEN c.value.string_value END) AS page_location
  FROM 
    base_table,
    UNNEST (event_params) c
  GROUP BY 1,2,3
)

, unnested_events_categorised AS (
-- categorizing Page Titles into PDPs and PLPs
  SELECT
  *,
  CASE WHEN ARRAY_LENGTH(SPLIT(page_location, '/')) >= 5 
            AND
            CONTAINS_SUBSTR(ARRAY_REVERSE(SPLIT(page_location, '/'))[SAFE_OFFSET(0)], '+')
            AND (LOWER(SPLIT(page_location, '/')[SAFE_OFFSET(4)]) IN 
                                        ('accessories','apparel','brands','campus+collection','drinkware',
                                          'electronics','google+redesign',
                                          'lifestyle','nest','new+2015+logo','notebooks+journals',
                                          'office','shop+by+brand','small+goods','stationery','wearables'
                                          )
                  OR
                  LOWER(SPLIT(page_location, '/')[SAFE_OFFSET(3)]) IN 
                                        ('accessories','apparel','brands','campus+collection','drinkware',
                                          'electronics','google+redesign',
                                          'lifestyle','nest','new+2015+logo','notebooks+journals',
                                          'office','shop+by+brand','small+goods','stationery','wearables'
                                          )
            )
            THEN 'PDP'
            WHEN NOT(CONTAINS_SUBSTR(ARRAY_REVERSE(SPLIT(page_location, '/'))[SAFE_OFFSET(0)], '+'))
            AND (LOWER(SPLIT(page_location, '/')[SAFE_OFFSET(4)]) IN 
                                        ('accessories','apparel','brands','campus+collection','drinkware',
                                          'electronics','google+redesign',
                                          'lifestyle','nest','new+2015+logo','notebooks+journals',
                                          'office','shop+by+brand','small+goods','stationery','wearables'
                                          )
                  OR 
                  LOWER(SPLIT(page_location, '/')[SAFE_OFFSET(3)]) IN 
                                          ('accessories','apparel','brands','campus+collection','drinkware',
                                            'electronics','google+redesign',
                                            'lifestyle','nest','new+2015+logo','notebooks+journals',
                                            'office','shop+by+brand','small+goods','stationery','wearables'
                                            )
            )
            THEN 'PLP'
        ELSE page_title
        END AS page_title_adjusted 

  FROM 
    unnested_events
)


, ranked_screens AS (
  SELECT
    *,
    LAG(page_title_adjusted,1) OVER (PARTITION BY  user_pseudo_id, visitID ORDER BY event_timestamp_microseconds ASC) previous_page,
    LEAD(page_title_adjusted,1) OVER (PARTITION BY  user_pseudo_id, visitID ORDER BY event_timestamp_microseconds ASC)  next_page
  FROM 
    unnested_events_categorised

)

,PLPtoPDPTransitions AS (
  SELECT
    user_pseudo_id,
    visitID
  FROM
    ranked_screens
  WHERE
    page_title_adjusted = 'PLP' AND next_page = 'PDP'
)

,TotalPLPViews AS (
  SELECT
    COUNT(*) AS total_plp_views
  FROM
    ranked_screens
  WHERE
    page_title_adjusted = 'PLP'
)

,TotalTransitions AS (
  SELECT
    COUNT(*) AS total_transitions
  FROM
    PLPtoPDPTransitions
)

SELECT
  (total_transitions * 100.0) / total_plp_views AS percentage
FROM
  TotalTransitions, TotalPLPViews;

```

## ga019.sql

```sql
WITH
--List of users who installed
sept_cohort AS (
  SELECT DISTINCT user_pseudo_id,
  FORMAT_DATE('%Y-%m-%d', PARSE_DATE('%Y%m%d', event_date)) AS date_first_open,
  FROM `firebase-public-project.analytics_153293282.events_*`
  WHERE event_name = 'first_open'
  AND _TABLE_SUFFIX BETWEEN '20180801' and '20180930'
),
--Get the list of users who uninstalled
uninstallers AS (
  SELECT DISTINCT user_pseudo_id,
  FORMAT_DATE('%Y-%m-%d', PARSE_DATE('%Y%m%d', event_date)) AS date_app_remove,
  FROM `firebase-public-project.analytics_153293282.events_*`
  WHERE event_name = 'app_remove'
  AND _TABLE_SUFFIX BETWEEN '20180801' and '20180930'
),
--Join the 2 tables and compute for # of days to uninstall
joined AS (
  SELECT a.*,
  b.date_app_remove,
  DATE_DIFF(DATE(b.date_app_remove), DATE(a.date_first_open), DAY) AS days_to_uninstall
  FROM sept_cohort a
  LEFT JOIN uninstallers b
  ON a.user_pseudo_id = b.user_pseudo_id
)
--Compute for the percentage
SELECT
COUNT(DISTINCT
CASE WHEN days_to_uninstall > 7 OR days_to_uninstall IS NULL THEN user_pseudo_id END) /
COUNT(DISTINCT user_pseudo_id)
AS percent_users_7_days
FROM joined

```

## ga020.sql

```sql
-- Define the date range and calculate the minimum date for filtering results
WITH dates AS (
    SELECT 
        DATE('2018-08-01') AS start_date,
        DATE('2018-08-15') AS end_date
),
-- Create a table of active dates for each user within the specified date range
dates_active_table AS (
    SELECT
        user_pseudo_id,
        PARSE_DATE('%Y%m%d', `event_date`) AS user_active_date
    FROM 
        `firebase-public-project.analytics_153293282.events_*` 
    WHERE 
        event_name = 'session_start'
        AND PARSE_DATE('%Y%m%d', `event_date`) BETWEEN (SELECT start_date FROM dates) AND (SELECT end_date FROM dates)
    GROUP BY 
        user_pseudo_id, user_active_date
),
-- Create a table of the earliest quickplay event date for each user within the specified date range
event_table AS (
    SELECT 
        user_pseudo_id,
        event_name,
        MIN(PARSE_DATE('%Y%m%d', `event_date`)) AS event_cohort_date
    FROM 
        `firebase-public-project.analytics_153293282.events_*` 
    WHERE 
        event_name IN ('level_start_quickplay', 'level_end_quickplay', 'level_complete_quickplay', 
                       'level_fail_quickplay', 'level_reset_quickplay', 'level_retry_quickplay')
        AND PARSE_DATE('%Y%m%d', `event_date`) BETWEEN (SELECT start_date FROM dates) AND (SELECT end_date FROM dates)
    GROUP BY 
        user_pseudo_id, event_name
),
-- Calculate the number of days since each user's initial quickplay event
days_since_event_table AS (
    SELECT
        events.user_pseudo_id,
        events.event_name AS event_cohort,
        events.event_cohort_date,
        days.user_active_date,
        DATE_DIFF(days.user_active_date, events.event_cohort_date, DAY) AS days_since_event
    FROM 
        event_table events
    LEFT JOIN 
        dates_active_table days ON events.user_pseudo_id = days.user_pseudo_id
    WHERE 
        events.event_cohort_date <= days.user_active_date
),
-- Calculate the weeks since each user's initial quickplay event and count the active days in each week
weeks_retention AS (
    SELECT
        event_cohort,
        user_pseudo_id,
        CAST(CASE WHEN days_since_event = 0 THEN 0 ELSE CEIL(days_since_event / 7) END AS INTEGER) AS weeks_since_event,
        COUNT(DISTINCT days_since_event) AS days_active_since_event -- Count Days Active in Week
    FROM 
        days_since_event_table
    GROUP BY 
        event_cohort, user_pseudo_id, weeks_since_event
),
-- Aggregate the weekly retention data
aggregated_weekly_retention_table AS (
    SELECT
        event_cohort,
        weeks_since_event,
        SUM(days_active_since_event) AS weekly_days_active,
        COUNT(DISTINCT user_pseudo_id) AS retained_users
    FROM 
        weeks_retention
    GROUP BY 
        event_cohort, weeks_since_event
),
RETENTION_INFO AS (
-- Select and calculate the weekly retention rate for each event cohort
SELECT
    event_cohort,
    weeks_since_event,
    weekly_days_active,
    retained_users,
    (retained_users / MAX(retained_users) OVER (PARTITION BY event_cohort)) AS retention_rate
FROM 
    aggregated_weekly_retention_table
ORDER BY 
    event_cohort, weeks_since_event
)

SELECT event_cohort
FROM
RETENTION_INFO
WHERE weeks_since_event = 2
ORDER BY retention_rate
LIMIT 1
```

## ga021.sql

```sql
-- Define the date range and calculate the minimum date for filtering results
WITH dates AS (
    SELECT 
        DATE('2018-07-02') AS start_date,
        DATE('2018-07-16') AS end_date
),
-- Create a table of active dates for each user within the specified date range
dates_active_table AS (
    SELECT
        user_pseudo_id,
        PARSE_DATE('%Y%m%d', `event_date`) AS user_active_date
    FROM 
        `firebase-public-project.analytics_153293282.events_*` 
    WHERE 
        event_name = 'session_start'
        AND PARSE_DATE('%Y%m%d', `event_date`) BETWEEN (SELECT start_date FROM dates) AND (SELECT end_date FROM dates)
    GROUP BY 
        user_pseudo_id, user_active_date
),
-- Create a table of the earliest quickplay event date for each user within the specified date range
event_table AS (
    SELECT 
        user_pseudo_id,
        event_name,
        MIN(PARSE_DATE('%Y%m%d', `event_date`)) AS event_cohort_date
    FROM 
        `firebase-public-project.analytics_153293282.events_*` 
    WHERE 
        event_name IN ('level_start_quickplay', 'level_end_quickplay', 'level_complete_quickplay', 
                       'level_fail_quickplay', 'level_reset_quickplay', 'level_retry_quickplay')
        AND PARSE_DATE('%Y%m%d', `event_date`) BETWEEN (SELECT start_date FROM dates) AND (SELECT end_date FROM dates)
    GROUP BY 
        user_pseudo_id, event_name
),
-- Calculate the number of days since each user's initial quickplay event
days_since_event_table AS (
    SELECT
        events.user_pseudo_id,
        events.event_name AS event_cohort,
        events.event_cohort_date,
        days.user_active_date,
        DATE_DIFF(days.user_active_date, events.event_cohort_date, DAY) AS days_since_event
    FROM 
        event_table events
    LEFT JOIN 
        dates_active_table days ON events.user_pseudo_id = days.user_pseudo_id
    WHERE 
        events.event_cohort_date <= days.user_active_date
),
-- Calculate the weeks since each user's initial quickplay event and count the active days in each week
weeks_retention AS (
    SELECT
        event_cohort,
        user_pseudo_id,
        CAST(CASE WHEN days_since_event = 0 THEN 0 ELSE CEIL(days_since_event / 7) END AS INTEGER) AS weeks_since_event,
        COUNT(DISTINCT days_since_event) AS days_active_since_event -- Count Days Active in Week
    FROM 
        days_since_event_table
    GROUP BY 
        event_cohort, user_pseudo_id, weeks_since_event
),
-- Aggregate the weekly retention data
aggregated_weekly_retention_table AS (
    SELECT
        event_cohort,
        weeks_since_event,
        SUM(days_active_since_event) AS weekly_days_active,
        COUNT(DISTINCT user_pseudo_id) AS retained_users
    FROM 
        weeks_retention
    GROUP BY 
        event_cohort, weeks_since_event
),
RETENTION_INFO AS (
SELECT
    event_cohort,
    weeks_since_event,
    weekly_days_active,
    retained_users,
    (retained_users / MAX(retained_users) OVER (PARTITION BY event_cohort)) AS retention_rate
FROM 
    aggregated_weekly_retention_table
ORDER BY 
    event_cohort, weeks_since_event
)

SELECT event_cohort, retention_rate
FROM
RETENTION_INFO
WHERE weeks_since_event = 2
```

## ga022.sql

```sql
WITH analytics_data AS (
  SELECT user_pseudo_id, event_timestamp, event_name, 
    UNIX_MICROS(TIMESTAMP("2018-09-01 00:00:00", "+8:00")) AS start_day,
    3600*1000*1000*24*7 AS one_week_micros
  FROM `firebase-public-project.analytics_153293282.events_*`
  WHERE _table_suffix BETWEEN '20180901' AND '20180930'
)

SELECT
 week_1_cohort / week_0_cohort AS week_1_pct,
 week_2_cohort / week_0_cohort AS week_2_pct,
 week_3_cohort / week_0_cohort AS week_3_pct
FROM (
  WITH week_3_users AS (
    SELECT DISTINCT user_pseudo_id
    FROM analytics_data
    WHERE event_timestamp BETWEEN start_day+(3*one_week_micros) AND start_day+(4*one_week_micros)
  ),
  week_2_users AS (
    SELECT DISTINCT user_pseudo_id
    FROM analytics_data
    WHERE event_timestamp BETWEEN start_day+(2*one_week_micros) AND start_day+(3*one_week_micros)
  ),
  week_1_users AS (
    SELECT DISTINCT user_pseudo_id
    FROM analytics_data
    WHERE event_timestamp BETWEEN start_day+(1*one_week_micros) AND start_day+(2*one_week_micros)
  ), 
  week_0_users AS (
    SELECT DISTINCT user_pseudo_id
    FROM analytics_data
    WHERE event_name = 'first_open'
      AND event_timestamp BETWEEN start_day AND start_day+(1*one_week_micros)
  )
  SELECT 
    (SELECT count(*) 
     FROM week_0_users) AS week_0_cohort,
    (SELECT count(*) 
     FROM week_1_users 
     JOIN week_0_users USING (user_pseudo_id)) AS week_1_cohort,
    (SELECT count(*) 
     FROM week_2_users 
     JOIN week_0_users USING (user_pseudo_id)) AS week_2_cohort,
    (SELECT count(*) 
     FROM week_3_users 
     JOIN week_0_users USING (user_pseudo_id)) AS week_3_cohort
)
```

## ga028.sql

```sql
WITH dates AS (
    SELECT 
        DATE('2018-07-02') AS start_date,
        DATE('2018-10-02') AS end_date,
        DATE_ADD(DATE_TRUNC(DATE('2018-10-02'), WEEK(TUESDAY)), INTERVAL -4 WEEK) AS min_date
),

date_table AS (
    SELECT DISTINCT 
        PARSE_DATE('%Y%m%d', `event_date`) AS event_date,
        user_pseudo_id,
        CASE 
            WHEN DATE_DIFF(PARSE_DATE('%Y%m%d', `event_date`), DATE(TIMESTAMP_MICROS(user_first_touch_timestamp)), DAY) = 0 
            THEN 1 
            ELSE 0 
        END AS is_new_user
    FROM 
        `firebase-public-project.analytics_153293282.events_*` 
    WHERE 
        event_name = 'session_start'
),

new_user_list AS (
    SELECT DISTINCT 
        user_pseudo_id,
        event_date
    FROM 
        date_table
    WHERE 
        is_new_user = 1
),

days_since_start_table AS (
    SELECT DISTINCT 
        is_new_user,
        nu.event_date AS date_cohort,
        dt.user_pseudo_id,
        dt.event_date,
        DATE_DIFF(dt.event_date, nu.event_date, DAY) AS days_since_start
    FROM 
        date_table dt
    JOIN 
        new_user_list nu ON dt.user_pseudo_id = nu.user_pseudo_id
),

weeks_retention AS (
    SELECT 
        date_cohort,
        DATE_TRUNC(date_cohort, WEEK(MONDAY)) AS week_cohort,
        user_pseudo_id,
        days_since_start,
        CASE 
            WHEN days_since_start = 0 
            THEN 0 
            ELSE CEIL(days_since_start / 7) 
        END AS weeks_since_start
    FROM 
        days_since_start_table
),
RETENTION_INFO AS (
  SELECT 
      week_cohort,
      weeks_since_start,
      COUNT(DISTINCT user_pseudo_id) AS retained_users
  FROM 
      weeks_retention
  WHERE 
      week_cohort <= (SELECT min_date FROM dates)
  GROUP BY 
      week_cohort,
      weeks_since_start
  HAVING 
      weeks_since_start <= 4
  ORDER BY 
      week_cohort,
      weeks_since_start
)

SELECT weeks_since_start, retained_users
FROM RETENTION_INFO
WHERE week_cohort = DATE('2018-07-02')


```

# local

## local003.sql

```sql
WITH RecencyScore AS (
    SELECT customer_unique_id,
           MAX(order_purchase_timestamp) AS last_purchase,
           NTILE(5) OVER (ORDER BY MAX(order_purchase_timestamp) DESC) AS recency
    FROM orders
        JOIN customers USING (customer_id)
    WHERE order_status = 'delivered'
    GROUP BY customer_unique_id
),
FrequencyScore AS (
    SELECT customer_unique_id,
           COUNT(order_id) AS total_orders,
           NTILE(5) OVER (ORDER BY COUNT(order_id) DESC) AS frequency
    FROM orders
        JOIN customers USING (customer_id)
    WHERE order_status = 'delivered'
    GROUP BY customer_unique_id
),
MonetaryScore AS (
    SELECT customer_unique_id,
           SUM(price) AS total_spent,
           NTILE(5) OVER (ORDER BY SUM(price) DESC) AS monetary
    FROM orders
        JOIN order_items USING (order_id)
        JOIN customers USING (customer_id)
    WHERE order_status = 'delivered'
    GROUP BY customer_unique_id
),

-- 2. Assign each customer to a group
RFM AS (
    SELECT last_purchase, total_orders, total_spent,
        CASE
            WHEN recency = 1 AND frequency + monetary IN (1, 2, 3, 4) THEN "Champions"
            WHEN recency IN (4, 5) AND frequency + monetary IN (1, 2) THEN "Can't Lose Them"
            WHEN recency IN (4, 5) AND frequency + monetary IN (3, 4, 5, 6) THEN "Hibernating"
            WHEN recency IN (4, 5) AND frequency + monetary IN (7, 8, 9, 10) THEN "Lost"
            WHEN recency IN (2, 3) AND frequency + monetary IN (1, 2, 3, 4) THEN "Loyal Customers"
            WHEN recency = 3 AND frequency + monetary IN (5, 6) THEN "Needs Attention"
            WHEN recency = 1 AND frequency + monetary IN (7, 8) THEN "Recent Users"
            WHEN recency = 1 AND frequency + monetary IN (5, 6) OR
                recency = 2 AND frequency + monetary IN (5, 6, 7, 8) THEN "Potentital Loyalists"
            WHEN recency = 1 AND frequency + monetary IN (9, 10) THEN "Price Sensitive"
            WHEN recency = 2 AND frequency + monetary IN (9, 10) THEN "Promising"
            WHEN recency = 3 AND frequency + monetary IN (7, 8, 9, 10) THEN "About to Sleep"
        END AS RFM_Bucket
    FROM RecencyScore
        JOIN FrequencyScore USING (customer_unique_id)
        JOIN MonetaryScore USING (customer_unique_id)
)

SELECT RFM_Bucket, 
       AVG(total_spent / total_orders) AS avg_sales_per_customer
FROM RFM
GROUP BY RFM_Bucket
```

## local004.sql

```sql
WITH CustomerData AS (
    SELECT
        customer_unique_id,
        COUNT(DISTINCT orders.order_id) AS order_count,
        SUM(payment_value) AS total_payment,
        JULIANDAY(MIN(order_purchase_timestamp)) AS first_order_day,
        JULIANDAY(MAX(order_purchase_timestamp)) AS last_order_day
    FROM customers
        JOIN orders USING (customer_id)
        JOIN order_payments USING (order_id)
    GROUP BY customer_unique_id
)
SELECT
    customer_unique_id,
    order_count AS PF,
    ROUND(total_payment / order_count, 2) AS AOV,
    CASE
        WHEN (last_order_day - first_order_day) < 7 THEN
            1
        ELSE
            (last_order_day - first_order_day) / 7
        END AS ACL
FROM CustomerData
ORDER BY AOV DESC
LIMIT 3

```

## local008.sql

```sql
WITH player_stats AS (
    SELECT
        b.player_id,
        p.name_given AS player_name,
        SUM(b.g) AS games_played,
        SUM(b.r) AS runs,
        SUM(b.h) AS hits,
        SUM(b.hr) AS home_runs
    FROM player p
    JOIN batting b ON p.player_id = b.player_id
    GROUP BY b.player_id, p.name_given
)

SELECT 'Games Played' AS Category, player_name AS Player_Name, games_played AS Batting_Table_Topper
FROM player_stats
WHERE games_played = (SELECT MAX(games_played) FROM player_stats)

UNION ALL

SELECT 'Runs' AS Category, player_name AS Player_Name, runs AS Batting_Table_Topper
FROM player_stats
WHERE runs = (SELECT MAX(runs) FROM player_stats)

UNION ALL

SELECT 'Hits' AS Category, player_name AS Player_Name, hits AS Batting_Table_Topper
FROM player_stats
WHERE hits = (SELECT MAX(hits) FROM player_stats)

UNION ALL

SELECT 'Home Runs' AS Category, player_name AS Player_Name, home_runs AS Batting_Table_Topper
FROM player_stats
WHERE home_runs = (SELECT MAX(home_runs) FROM player_stats);

```

## local017.sql

```sql
WITH AnnualTotals AS (
    SELECT 
        STRFTIME('%Y', collision_date) AS Year, 
        COUNT(case_id) AS AnnualTotal
    FROM 
        collisions
    GROUP BY 
        Year
),
CategoryTotals AS (
    SELECT 
        STRFTIME('%Y', collision_date) AS Year,
        pcf_violation_category AS Category,
        COUNT(case_id) AS Subtotal
    FROM 
        collisions
    GROUP BY 
        Year, Category
),
CategoryPercentages AS (
    SELECT 
        ct.Year,
        ct.Category,
        ROUND((ct.Subtotal * 100.0) / at.AnnualTotal, 1) AS PercentageOfAnnualRoadIncidents
    FROM 
        CategoryTotals ct
    JOIN 
        AnnualTotals at ON ct.Year = at.Year
),
RankedCategories AS (
    SELECT
        Year,
        Category,
        PercentageOfAnnualRoadIncidents,
        ROW_NUMBER() OVER (PARTITION BY Year ORDER BY PercentageOfAnnualRoadIncidents DESC) AS Rank
    FROM
        CategoryPercentages
),
TopTwoCategories AS (
    SELECT
        Year,
        GROUP_CONCAT(Category, ', ') AS TopCategories
    FROM
        RankedCategories
    WHERE
        Rank <= 2
    GROUP BY
        Year
),
UniqueYear AS (
    SELECT
        Year
    FROM
        TopTwoCategories
    GROUP BY
        TopCategories
    HAVING COUNT(Year) = 1
),
results AS (
SELECT 
    rc.Year, 
    rc.Category, 
    rc.PercentageOfAnnualRoadIncidents
FROM 
    UniqueYear u
JOIN 
    RankedCategories rc ON u.Year = rc.Year
WHERE 
    rc.Rank <= 2
)

SELECT distinct Year FROM results
```

## local019.sql

```sql
WITH MatchDetails AS (
    SELECT
        b.name AS titles,
        m.duration AS match_duration,
        w1.name || ' vs ' || w2.name AS matches,
        m.win_type AS win_type,
        l.name AS location,
        e.name AS event,
        ROW_NUMBER() OVER (PARTITION BY b.name ORDER BY m.duration ASC) AS rank
    FROM 
        Belts b
    INNER JOIN Matches m ON m.title_id = b.id
    INNER JOIN Wrestlers w1 ON w1.id = m.winner_id
    INNER JOIN Wrestlers w2 ON w2.id = m.loser_id
    INNER JOIN Cards c ON c.id = m.card_id
    INNER JOIN Locations l ON l.id = c.location_id
    INNER JOIN Events e ON e.id = c.event_id
    INNER JOIN Promotions p ON p.id = c.promotion_id
    WHERE
        p.name = 'NXT'
        AND m.duration <> ''
        AND b.name <> ''
        AND b.name NOT IN (
            SELECT name 
            FROM Belts 
            WHERE name LIKE '%title change%'
        )
),
Rank1 AS (
SELECT 
    titles,
    match_duration,
    matches,
    win_type,
    location,
    event
FROM 
    MatchDetails
WHERE 
    rank = 1
)
SELECT
    SUBSTR(matches, 1, INSTR(matches, ' vs ') - 1) AS wrestler1,
    SUBSTR(matches, INSTR(matches, ' vs ') + 4) AS wrestler2
FROM
Rank1
ORDER BY match_duration 
LIMIT 1
```

## local022.sql

```sql
-- Step 1: Calculate players' total runs in each match
WITH player_runs AS (
    SELECT 
        bbb.striker AS player_id, 
        bbb.match_id, 
        SUM(bsc.runs_scored) AS total_runs 
    FROM 
        ball_by_ball AS bbb
    JOIN 
        batsman_scored AS bsc
    ON 
        bbb.match_id = bsc.match_id 
        AND bbb.over_id = bsc.over_id 
        AND bbb.ball_id = bsc.ball_id 
        AND bbb.innings_no = bsc.innings_no
    GROUP BY 
        bbb.striker, bbb.match_id
    HAVING 
        SUM(bsc.runs_scored) >= 100
),

-- Step 2: Identify losing teams for each match
losing_teams AS (
    SELECT 
        match_id, 
        CASE 
            WHEN match_winner = team_1 THEN team_2 
            ELSE team_1 
        END AS loser 
    FROM 
        match
),

-- Step 3: Combine the above results to get players who scored 100 or more runs in losing teams
players_in_losing_teams AS (
    SELECT 
        pr.player_id, 
        pr.match_id 
    FROM 
        player_runs AS pr
    JOIN 
        losing_teams AS lt
    ON 
        pr.match_id = lt.match_id
    JOIN 
        player_match AS pm
    ON 
        pr.player_id = pm.player_id 
        AND pr.match_id = pm.match_id 
        AND lt.loser = pm.team_id
)

-- Step 4: Select distinct player names from the player table
SELECT DISTINCT 
    p.player_name 
FROM 
    player AS p
JOIN 
    players_in_losing_teams AS plt
ON 
    p.player_id = plt.player_id
ORDER BY 
    p.player_name;

```

## local023.sql

```sql
WITH runs_scored AS (
    SELECT 
        bb.striker AS player_id,
        bb.match_id,
        bs.runs_scored AS runs
    FROM 
        ball_by_ball AS bb
    JOIN 
        batsman_scored AS bs ON bb.match_id = bs.match_id 
            AND bb.over_id = bs.over_id 
            AND bb.ball_id = bs.ball_id 
            AND bb.innings_no = bs.innings_no
    WHERE 
        bb.match_id IN (SELECT match_id FROM match WHERE season_id = 5)
),
total_runs AS (
    SELECT 
        player_id, 
        match_id, 
        SUM(runs) AS total_runs 
    FROM 
        runs_scored 
    GROUP BY 
        player_id, match_id
),
batting_averages AS (
    SELECT 
        player_id, 
        SUM(total_runs) AS runs, 
        COUNT(match_id) AS num_matches,
        ROUND(SUM(total_runs) / CAST(COUNT(match_id) AS FLOAT), 3) AS batting_avg
    FROM 
        total_runs 
    GROUP BY 
        player_id 
    ORDER BY 
        batting_avg DESC 
    LIMIT 5
)
SELECT 
    p.player_name,
    b.batting_avg
FROM 
    player AS p
JOIN 
    batting_averages AS b ON p.player_id = b.player_id
ORDER BY 
    b.batting_avg DESC;

```

## local029.sql

```sql
WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        COUNT(o.order_id) AS Total_Orders_By_Customers,
        AVG(p.payment_value) AS Average_Payment_By_Customer,
        c.customer_city,
        c.customer_state
    FROM olist_customers c
    JOIN olist_orders o ON c.customer_id = o.customer_id
    JOIN olist_order_payments p ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id, c.customer_city, c.customer_state
)

SELECT 
    Average_Payment_By_Customer,
    customer_city,
    customer_state
FROM customer_orders
ORDER BY Total_Orders_By_Customers DESC
LIMIT 3;

```

## local038.sql

```sql
SELECT
    actor.first_name || ' ' || actor.last_name AS full_name
FROM
    actor
INNER JOIN film_actor ON actor.actor_id = film_actor.actor_id
INNER JOIN film ON film_actor.film_id = film.film_id
INNER JOIN film_category ON film.film_id = film_category.film_id
INNER JOIN category ON film_category.category_id = category.category_id
-- Join with the language table
INNER JOIN language ON film.language_id = language.language_id
WHERE
    category.name = 'Children' AND
    film.release_year BETWEEN 2000 AND 2010 AND
    film.rating IN ('G', 'PG') AND
    language.name = 'English' AND
    film.length <= 120
GROUP BY
    actor.actor_id, actor.first_name, actor.last_name
ORDER BY
    COUNT(film.film_id) DESC
LIMIT 1;

```

## local039.sql

```sql
SELECT
    category.name
FROM
    category
INNER JOIN film_category USING (category_id)
INNER JOIN film USING (film_id)
INNER JOIN inventory USING (film_id)
INNER JOIN rental USING (inventory_id)
INNER JOIN customer USING (customer_id)
INNER JOIN address USING (address_id)
INNER JOIN city USING (city_id)
WHERE
    LOWER(city.city) LIKE 'a%' OR city.city LIKE '%-%'
GROUP BY
    category.name
ORDER BY
    SUM(CAST((julianday(rental.return_date) - julianday(rental.rental_date)) * 24 AS INTEGER)) DESC
LIMIT
    1;

```

## local058.sql

```sql
WITH UniqueProducts2020 AS (
    SELECT
        dp.segment,
        COUNT(DISTINCT fsm.product_code) AS unique_products_2020
    FROM
        hardware_fact_sales_monthly fsm
    JOIN
        hardware_dim_product dp ON fsm.product_code = dp.product_code
    WHERE
        fsm.fiscal_year = 2020
    GROUP BY
        dp.segment
),
UniqueProducts2021 AS (
    SELECT
        dp.segment,
        COUNT(DISTINCT fsm.product_code) AS unique_products_2021
    FROM
        hardware_fact_sales_monthly fsm
    JOIN
        hardware_dim_product dp ON fsm.product_code = dp.product_code
    WHERE
        fsm.fiscal_year = 2021
    GROUP BY
        dp.segment
)
SELECT
    spc.segment,
    spc.unique_products_2020 AS product_count_2020
FROM
    UniqueProducts2020 spc
JOIN
    UniqueProducts2021 fup ON spc.segment = fup.segment
ORDER BY
    ((fup.unique_products_2021 - spc.unique_products_2020) * 100.0) / (spc.unique_products_2020) DESC;

```

## local065.sql

```sql
WITH get_extras_count AS (
    WITH RECURSIVE split_extras AS (
        SELECT
            order_id,
            TRIM(SUBSTR(extras, 1, INSTR(extras || ',', ',') - 1)) AS each_extra,
            SUBSTR(extras || ',', INSTR(extras || ',', ',') + 1) AS remaining_extras
        FROM
            pizza_clean_customer_orders
        UNION ALL
        SELECT
            order_id,
            TRIM(SUBSTR(remaining_extras, 1, INSTR(remaining_extras, ',') - 1)) AS each_extra,
            SUBSTR(remaining_extras, INSTR(remaining_extras, ',') + 1)
        FROM
            split_extras
        WHERE
            remaining_extras <> ''
    )
    SELECT
        order_id,
        COUNT(each_extra) AS total_extras
    FROM
        split_extras
    GROUP BY
        order_id
),
calculate_totals AS (
    SELECT
        t1.order_id,
        t1.pizza_id,
        SUM(
            CASE
                WHEN pizza_id = 1 THEN 12
                WHEN pizza_id = 2 THEN 10
            END
        ) AS total_price,
        t3.total_extras
    FROM 
        pizza_clean_customer_orders AS t1
    JOIN
        pizza_clean_runner_orders AS t2 
    ON
        t2.order_id = t1.order_id
    LEFT JOIN
        get_extras_count AS t3
    ON
        t3.order_id = t1.order_id
    WHERE
        t2.cancellation IS NULL
    GROUP BY 
        t1.order_id,
        t1.pizza_id,
        t3.total_extras
)
SELECT 
    SUM(total_price) + SUM(total_extras) AS total_income
FROM 
    calculate_totals;

```

## local066.sql

```sql
WITH cte_cleaned_customer_orders AS (
    SELECT
        *,
        ROW_NUMBER() OVER () AS original_row_number
    FROM 
        pizza_clean_customer_orders
),
split_regular_toppings AS (
    SELECT
        pizza_id,
        TRIM(SUBSTR(toppings, 1, INSTR(toppings || ',', ',') - 1)) AS topping_id,
        SUBSTR(toppings || ',', INSTR(toppings || ',', ',') + 1) AS remaining_toppings
    FROM 
        pizza_recipes
    UNION ALL
    SELECT
        pizza_id,
        TRIM(SUBSTR(remaining_toppings, 1, INSTR(remaining_toppings, ',') - 1)) AS topping_id,
        SUBSTR(remaining_toppings, INSTR(remaining_toppings, ',') + 1) AS remaining_toppings
    FROM 
        split_regular_toppings
    WHERE
        remaining_toppings <> ''
),
cte_base_toppings AS (
    SELECT
        t1.order_id,
        t1.customer_id,
        t1.pizza_id,
        t1.order_time,
        t1.original_row_number,
        t2.topping_id
    FROM 
        cte_cleaned_customer_orders AS t1
    LEFT JOIN 
        split_regular_toppings AS t2
    ON 
        t1.pizza_id = t2.pizza_id
),
split_exclusions AS (
    SELECT
        order_id,
        customer_id,
        pizza_id,
        order_time,
        original_row_number,
        TRIM(SUBSTR(exclusions, 1, INSTR(exclusions || ',', ',') - 1)) AS topping_id,
        SUBSTR(exclusions || ',', INSTR(exclusions || ',', ',') + 1) AS remaining_exclusions
    FROM 
        cte_cleaned_customer_orders
    WHERE 
        exclusions IS NOT NULL
    UNION ALL
    SELECT
        order_id,
        customer_id,
        pizza_id,
        order_time,
        original_row_number,
        TRIM(SUBSTR(remaining_exclusions, 1, INSTR(remaining_exclusions, ',') - 1)) AS topping_id,
        SUBSTR(remaining_exclusions, INSTR(remaining_exclusions, ',') + 1) AS remaining_exclusions
    FROM 
        split_exclusions
    WHERE
        remaining_exclusions <> ''
),
split_extras AS (
    SELECT
        order_id,
        customer_id,
        pizza_id,
        order_time,
        original_row_number,
        TRIM(SUBSTR(extras, 1, INSTR(extras || ',', ',') - 1)) AS topping_id,
        SUBSTR(extras || ',', INSTR(extras || ',', ',') + 1) AS remaining_extras
    FROM 
        cte_cleaned_customer_orders
    WHERE 
        extras IS NOT NULL
    UNION ALL
    SELECT
        order_id,
        customer_id,
        pizza_id,
        order_time,
        original_row_number,
        TRIM(SUBSTR(remaining_extras, 1, INSTR(remaining_extras, ',') - 1)) AS topping_id,
        SUBSTR(remaining_extras, INSTR(remaining_extras, ',') + 1) AS remaining_extras
    FROM 
        split_extras
    WHERE
        remaining_extras <> ''
),
cte_combined_orders AS (
    SELECT 
        order_id,
        customer_id,
        pizza_id,
        order_time,
        original_row_number,
        topping_id
    FROM 
        cte_base_toppings
    WHERE topping_id NOT IN (SELECT topping_id FROM split_exclusions WHERE split_exclusions.order_id = cte_base_toppings.order_id)
    UNION ALL
    SELECT 
        order_id,
        customer_id,
        pizza_id,
        order_time,
        original_row_number,
        topping_id
    FROM 
        split_extras
)
SELECT
    t2.topping_name,
    COUNT(*) AS topping_count
FROM 
    cte_combined_orders AS t1
JOIN 
    pizza_toppings AS t2
ON 
    t1.topping_id = t2.topping_id
GROUP BY 
    t2.topping_name
ORDER BY 
    topping_count DESC;

```

## local075.sql

```sql
WITH product_viewed AS (
    SELECT
        t1.page_id,
        SUM(CASE WHEN event_type = 1 THEN 1 ELSE 0 END) AS n_page_views,
        SUM(CASE WHEN event_type = 2 THEN 1 ELSE 0 END) AS n_added_to_cart
    FROM
        shopping_cart_page_hierarchy AS t1
    JOIN
        shopping_cart_events AS t2
    ON
        t1.page_id = t2.page_id
    WHERE
        t1.product_id IS NOT NULL
    GROUP BY
        t1.page_id
),
product_purchased AS (
    SELECT
        t2.page_id,
        SUM(CASE WHEN event_type = 2 THEN 1 ELSE 0 END) AS purchased_from_cart
    FROM
        shopping_cart_page_hierarchy AS t1
    JOIN
        shopping_cart_events AS t2
    ON
        t1.page_id = t2.page_id
    WHERE
        t1.product_id IS NOT NULL
        AND EXISTS (
            SELECT
                visit_id
            FROM
                shopping_cart_events
            WHERE
                event_type = 3
                AND t2.visit_id = visit_id
        )
        AND t1.page_id NOT IN (1, 2, 12, 13)
    GROUP BY
        t2.page_id
),
product_abandoned AS (
    SELECT
        t2.page_id,
        SUM(CASE WHEN event_type = 2 THEN 1 ELSE 0 END) AS abandoned_in_cart
    FROM
        shopping_cart_page_hierarchy AS t1
    JOIN
        shopping_cart_events AS t2
    ON
        t1.page_id = t2.page_id
    WHERE
        t1.product_id IS NOT NULL
        AND NOT EXISTS (
            SELECT
                visit_id
            FROM
                shopping_cart_events
            WHERE
                event_type = 3
                AND t2.visit_id = visit_id
        )
        AND t1.page_id NOT IN (1, 2, 12, 13)
    GROUP BY
        t2.page_id
)
SELECT
    t1.page_id,
    t1.page_name,
    t2.n_page_views AS 'number of product being viewed',
    t2.n_added_to_cart AS 'number added to the cart',
    t4.abandoned_in_cart AS 'without being purchased in cart',
    t3.purchased_from_cart AS 'count of actual purchases'
FROM
    shopping_cart_page_hierarchy AS t1
JOIN
    product_viewed AS t2 
ON
    t2.page_id = t1.page_id
JOIN
    product_purchased AS t3 
ON 
    t3.page_id = t1.page_id
JOIN
    product_abandoned AS t4 
ON 
    t4.page_id = t1.page_id;

```

## local078.sql

```sql
WITH get_interest_rank AS (
    SELECT
        t1.month_year,
        t2.interest_name,
        t1.composition,
        RANK() OVER (
            PARTITION BY t2.interest_name
            ORDER BY t1.composition DESC
        ) AS interest_rank
    FROM 
        interest_metrics AS t1
    JOIN 
        interest_map AS t2
    ON 
        t1.interest_id = t2.id
    WHERE 
        t1.month_year IS NOT NULL
),
get_top_10 AS (
    SELECT
        month_year,
        interest_name,
        composition
    FROM 
        get_interest_rank
    WHERE 
        interest_rank = 1
    ORDER BY 
        composition DESC
    LIMIT 10
),
get_bottom_10 AS (
    SELECT
        month_year,
        interest_name,
        composition
    FROM 
        get_interest_rank
    WHERE 
        interest_rank = 1
    ORDER BY 
        composition ASC
    LIMIT 10
)
SELECT * 
FROM 
    get_top_10
UNION
SELECT * 
FROM 
    get_bottom_10
ORDER BY 
    composition DESC;

```

## local099.sql

```sql
WITH YASH_CHOPRAS_PID AS (
    SELECT
        TRIM(P.PID) AS PID
    FROM
        Person P
    WHERE
        TRIM(P.Name) = 'Yash Chopra'
),
NUM_OF_MOV_BY_ACTOR_DIRECTOR AS (
    SELECT
        TRIM(MC.PID) AS ACTOR_PID,
        TRIM(MD.PID) AS DIRECTOR_PID,
        COUNT(DISTINCT TRIM(MD.MID)) AS NUM_OF_MOV
    FROM
        M_Cast MC
    JOIN
        M_Director MD ON TRIM(MC.MID) = TRIM(MD.MID)
    GROUP BY
        ACTOR_PID,
        DIRECTOR_PID
),
NUM_OF_MOVIES_BY_YC AS (
    SELECT
        NM.ACTOR_PID,
        NM.DIRECTOR_PID,
        NM.NUM_OF_MOV AS NUM_OF_MOV_BY_YC
    FROM
        NUM_OF_MOV_BY_ACTOR_DIRECTOR NM
    JOIN
        YASH_CHOPRAS_PID YCP ON NM.DIRECTOR_PID = YCP.PID
),
MAX_MOV_BY_OTHER_DIRECTORS AS (
    SELECT
        ACTOR_PID,
        MAX(NUM_OF_MOV) AS MAX_NUM_OF_MOV
    FROM
        NUM_OF_MOV_BY_ACTOR_DIRECTOR NM
    JOIN
        YASH_CHOPRAS_PID YCP ON NM.DIRECTOR_PID <> YCP.PID
    GROUP BY
        ACTOR_PID
),
ACTORS_MOV_COMPARISION AS (
    SELECT
        NMY.ACTOR_PID,
        CASE WHEN NMY.NUM_OF_MOV_BY_YC > IFNULL(NMO.MAX_NUM_OF_MOV, 0) THEN 'Y' ELSE 'N' END AS MORE_MOV_BY_YC
    FROM
        NUM_OF_MOVIES_BY_YC NMY
    LEFT OUTER JOIN
        MAX_MOV_BY_OTHER_DIRECTORS NMO ON NMY.ACTOR_PID = NMO.ACTOR_PID
)
SELECT
    COUNT(DISTINCT TRIM(P.PID)) AS "Number of actor"
FROM
    Person P
WHERE
    TRIM(P.PID) IN (
        SELECT
            DISTINCT ACTOR_PID
        FROM
            ACTORS_MOV_COMPARISION
        WHERE
            MORE_MOV_BY_YC = 'Y'
    );

```

## local131.sql

```sql
SELECT 
  Musical_Styles.StyleName,
  COUNT(RankedPreferences.FirstStyle)
    AS FirstPreference,
  COUNT(RankedPreferences.SecondStyle)
    AS SecondPreference,
  COUNT(RankedPreferences.ThirdStyle)
    AS ThirdPreference
FROM Musical_Styles,
 (SELECT (CASE WHEN
    Musical_Preferences.PreferenceSeq = 1
               THEN Musical_Preferences.StyleID
               ELSE Null END) As FirstStyle,
         (CASE WHEN
    Musical_Preferences.PreferenceSeq = 2
               THEN Musical_Preferences.StyleID
               ELSE Null END) As SecondStyle,
         (CASE WHEN
    Musical_Preferences.PreferenceSeq = 3
               THEN Musical_Preferences.StyleID
               ELSE Null END) AS ThirdStyle
   FROM Musical_Preferences)  AS RankedPreferences
WHERE Musical_Styles.StyleID =
         RankedPreferences.FirstStyle
  OR Musical_Styles.StyleID =
         RankedPreferences.SecondStyle
  OR Musical_Styles.StyleID =
         RankedPreferences.ThirdStyle
GROUP BY StyleID, StyleName
HAVING COUNT(FirstStyle) > 0
     OR     COUNT(SecondStyle) > 0
     OR     COUNT(ThirdStyle) > 0
ORDER BY FirstPreference DESC,
        SecondPreference DESC,
        ThirdPreference DESC, StyleID;

```

## local163.sql

```sql
WITH AvgSalaries AS (
    SELECT 
        facrank AS FacRank,
        AVG(facsalary) AS AvSalary
    FROM 
        university_faculty
    GROUP BY 
        facrank
),
SalaryDifferences AS (
    SELECT 
        university_faculty.facrank AS FacRank, 
        university_faculty.facfirstname AS FacFirstName, 
        university_faculty.faclastname AS FacLastName, 
        university_faculty.facsalary AS Salary, 
        ABS(university_faculty.facsalary - AvgSalaries.AvSalary) AS Diff
    FROM 
        university_faculty
    JOIN 
        AvgSalaries ON university_faculty.facrank = AvgSalaries.FacRank
),
MinDifferences AS (
    SELECT 
        FacRank, 
        MIN(Diff) AS MinDiff
    FROM 
        SalaryDifferences
    GROUP BY 
        FacRank
)
SELECT 
    s.FacRank, 
    s.FacFirstName, 
    s.FacLastName, 
    s.Salary
FROM 
    SalaryDifferences s
JOIN 
    MinDifferences m ON s.FacRank = m.FacRank AND s.Diff = m.MinDiff;

```

## local197.sql

```sql
WITH result_table AS (
  SELECT 
    strftime('%m', pm.payment_date) AS pay_mon, 
    customer_id,
    COUNT(pm.amount) AS pay_countpermon, 
    SUM(pm.amount) AS pay_amount 
  FROM 
    payment AS pm 
  GROUP BY 
    pay_mon, 
    customer_id
), 
top10_customer AS (
  SELECT 
    customer_id,
    SUM(tb.pay_amount) AS total_payments 
  FROM 
    result_table AS tb 
  GROUP BY 
    customer_id
  ORDER BY 
    SUM(tb.pay_amount) DESC 
  LIMIT 
    10
), 
difference_per_mon AS (
  SELECT 
    pay_mon AS month_number, 
    pay_mon AS month, 
    tb.pay_countpermon, 
    tb.pay_amount, 
    ABS(tb.pay_amount - LAG(tb.pay_amount) OVER (PARTITION BY tb.customer_id)) AS diff 
  FROM 
    result_table tb 
    JOIN top10_customer top ON top.customer_id = tb.customer_id
) 
SELECT 
  month, 
  ROUND(max_diff, 2) AS max_diff 
FROM (
  SELECT 
    month, 
    diff, 
    month_number, 
    MAX(diff) OVER (PARTITION BY month) AS max_diff 
  FROM 
    difference_per_mon
) AS max_per_mon 
WHERE 
  diff = max_diff 
ORDER BY 
  max_diff DESC 
LIMIT 
  1;

```

## local199.sql

```sql
WITH result_table AS (
  SELECT 
    strftime('%Y', RE.RENTAL_DATE) AS YEAR, 
    strftime('%m', RE.RENTAL_DATE) AS RENTAL_MONTH, 
    ST.STORE_ID, 
    COUNT(RE.RENTAL_ID) AS count 
  FROM 
    RENTAL RE 
    JOIN STAFF ST ON RE.STAFF_ID = ST.STAFF_ID 
  GROUP BY 
    YEAR, 
    RENTAL_MONTH, 
    ST.STORE_ID 
), 
monthly_sales AS (
  SELECT 
    YEAR, 
    RENTAL_MONTH, 
    STORE_ID, 
    SUM(count) AS total_rentals 
  FROM 
    result_table 
  GROUP BY 
    YEAR, 
    RENTAL_MONTH, 
    STORE_ID
),
store_max_sales AS (
  SELECT 
    STORE_ID, 
    YEAR, 
    RENTAL_MONTH, 
    total_rentals, 
    MAX(total_rentals) OVER (PARTITION BY STORE_ID) AS max_rentals 
  FROM 
    monthly_sales
)
SELECT 
  STORE_ID, 
  YEAR, 
  RENTAL_MONTH, 
  total_rentals 
FROM 
  store_max_sales 
WHERE 
  total_rentals = max_rentals
ORDER BY 
  STORE_ID;

```

## local210.sql

```sql
WITH february_orders AS (
    SELECT
        h.hub_name AS hub_name,
        COUNT(*) AS orders_february
    FROM 
        orders o 
    LEFT JOIN
        stores s ON o.store_id = s.store_id 
    LEFT JOIN 
        hubs h ON s.hub_id = h.hub_id 
    WHERE o.order_created_month = 2 AND o.order_status = 'FINISHED'
    GROUP BY
        h.hub_name
),
march_orders AS (
    SELECT
        h.hub_name AS hub_name,
        COUNT(*) AS orders_march
    FROM 
        orders o 
    LEFT JOIN
        stores s ON o.store_id = s.store_id 
    LEFT JOIN 
        hubs h ON s.hub_id = h.hub_id 
    WHERE o.order_created_month = 3 AND o.order_status = 'FINISHED'
    GROUP BY
        h.hub_name
)
SELECT
    fo.hub_name
FROM
    february_orders fo
LEFT JOIN 
    march_orders mo ON fo.hub_name = mo.hub_name
WHERE 
    fo.orders_february > 0 AND 
    mo.orders_march > 0 AND
    (CAST((mo.orders_march - fo.orders_february) AS REAL) / CAST(fo.orders_february AS REAL)) > 0.2  -- Filter for hubs with more than a 20% increase
```

## local219.sql

```sql
WITH match_view AS(
SELECT
    M.id,
    L.name AS league,
    M.season,
    M.match_api_id,
    T.team_long_name AS home_team,
    TM.team_long_name AS away_team,
    M.home_team_goal,
    M.away_team_goal,
    P1.player_name AS home_gk,
    P2.player_name AS home_center_back_1,
    P3.player_name AS home_center_back_2,
    P4.player_name AS home_right_back,
    P5.player_name AS home_left_back,
    P6.player_name AS home_midfield_1,
    P7.player_name AS home_midfield_2,
    P8.player_name AS home_midfield_3,
    P9.player_name AS home_midfield_4,
    P10.player_name AS home_second_forward,
    P11.player_name AS home_center_forward,
    P12.player_name AS away_gk,
    P13.player_name AS away_center_back_1,
    P14.player_name AS away_center_back_2,
    P15.player_name AS away_right_back,
    P16.player_name AS away_left_back,
    P17.player_name AS away_midfield_1,
    P18.player_name AS away_midfield_2,
    P19.player_name AS away_midfield_3,
    P20.player_name AS away_midfield_4,
    P21.player_name AS away_second_forward,
    P22.player_name AS away_center_forward,
    M.goal,
    M.card
FROM
    match M
LEFT JOIN
    league L ON M.league_id = L.id
LEFT JOIN
    team T ON M.home_team_api_id = T.team_api_id
LEFT JOIN
    team TM ON M.away_team_api_id = TM.team_api_id
LEFT JOIN
    player P1 ON M.home_player_1 = P1.player_api_id
LEFT JOIN
    player P2 ON M.home_player_2 = P2.player_api_id
LEFT JOIN
    player P3 ON M.home_player_3 = P3.player_api_id
LEFT JOIN
    player P4 ON M.home_player_4 = P4.player_api_id
LEFT JOIN
    player P5 ON M.home_player_5 = P5.player_api_id
LEFT JOIN
    player P6 ON M.home_player_6 = P6.player_api_id
LEFT JOIN
    player P7 ON M.home_player_7 = P7.player_api_id
LEFT JOIN
    player P8 ON M.home_player_8 = P8.player_api_id
LEFT JOIN
    player P9 ON M.home_player_9 = P9.player_api_id
LEFT JOIN
    player P10 ON M.home_player_10 = P10.player_api_id
LEFT JOIN
    player P11 ON M.home_player_11 = P11.player_api_id
LEFT JOIN
    player P12 ON M.away_player_1 = P12.player_api_id
LEFT JOIN
    player P13 ON M.away_player_2 = P13.player_api_id
LEFT JOIN
    player P14 ON M.away_player_3 = P14.player_api_id
LEFT JOIN
    player P15 ON M.away_player_4 = P15.player_api_id
LEFT JOIN
    player P16 ON M.away_player_5 = P16.player_api_id
LEFT JOIN
    player P17 ON M.away_player_6 = P17.player_api_id
LEFT JOIN
    player P18 ON M.away_player_7 = P18.player_api_id
LEFT JOIN
    player P19 ON M.away_player_8 = P19.player_api_id
LEFT JOIN
    player P20 ON M.away_player_9 = P20.player_api_id
LEFT JOIN
    player P21 ON M.away_player_10 = P21.player_api_id
LEFT JOIN
    player P22 ON M.away_player_11 = P22.player_api_id
),
match_score AS
(
    SELECT  -- Displaying teams and their goals as home_team
        id,
        home_team AS team,
        CASE
            WHEN home_team_goal > away_team_goal THEN 1 ELSE 0 END AS Winning_match
    FROM
        match_view

    UNION ALL

    SELECT  -- Displaying teams and their goals as away_team
        id,
        away_team AS team,
        CASE
            WHEN away_team_goal > home_team_goal THEN 1 ELSE 0 END AS Winning_match
    FROM
        match_view
),
winning_matches AS
(
    SELECT  -- Displaying total match wins for each team
        MV.league,
        M.team,
        COUNT(CASE WHEN M.Winning_match = 1 THEN 1 END) AS wins,
        ROW_NUMBER() OVER(PARTITION BY MV.league ORDER BY COUNT(CASE WHEN M.Winning_match = 1 THEN 1 END) ASC) AS rn
    FROM
        match_score M
    JOIN
        match_view MV
    ON
        M.id = MV.id
    GROUP BY
        MV.league,
        team
    ORDER BY
        league,
        wins ASC
)
SELECT
    league,
    team
FROM
    winning_matches
WHERE
    rn = 1  -- Getting the team with the least number of wins in each league
ORDER BY
    league;

```

## local301.sql

```sql
SELECT 
    before_effect,
    after_effect,
    after_effect - before_effect AS change_amount,
    ROUND(((after_effect * 1.0 / before_effect) - 1) * 100, 2) AS percent_change,
    '2018' AS year
FROM (
    SELECT 
        SUM(CASE WHEN delta_weeks BETWEEN 1 AND 4 THEN sales END) AS after_effect,
        SUM(CASE WHEN delta_weeks BETWEEN -3 AND 0 THEN sales END) AS before_effect
    FROM (
        SELECT 
            week_date,
            ROUND((JULIANDAY(week_date) - JULIANDAY('2018-06-15')) / 7.0) + 1 AS delta_weeks,
            sales 
        FROM cleaned_weekly_sales
    ) add_delta_weeks
) AS add_before_after
UNION ALL
SELECT 
    before_effect,
    after_effect,
    after_effect - before_effect AS change_amount,
    ROUND(((after_effect * 1.0 / before_effect) - 1) * 100, 2) AS percent_change,
    '2019' AS year
FROM (
    SELECT 
        SUM(CASE WHEN delta_weeks BETWEEN 1 AND 4 THEN sales END) AS after_effect,
        SUM(CASE WHEN delta_weeks BETWEEN -3 AND 0 THEN sales END) AS before_effect
    FROM (
        SELECT 
            week_date,
            ROUND((JULIANDAY(week_date) - JULIANDAY('2019-06-15')) / 7.0) + 1 AS delta_weeks,
            sales 
        FROM cleaned_weekly_sales
    ) add_delta_weeks
) AS add_before_after
UNION ALL
SELECT 
    before_effect,
    after_effect,
    after_effect - before_effect AS change_amount,
    ROUND(((after_effect * 1.0 / before_effect) - 1) * 100, 2) AS percent_change,
    '2020' AS year
FROM (
    SELECT 
        SUM(CASE WHEN delta_weeks BETWEEN 1 AND 4 THEN sales END) AS after_effect,
        SUM(CASE WHEN delta_weeks BETWEEN -3 AND 0 THEN sales END) AS before_effect
    FROM (
        SELECT 
            week_date,
            ROUND((JULIANDAY(week_date) - JULIANDAY('2020-06-15')) / 7.0) + 1 AS delta_weeks,
            sales 
        FROM cleaned_weekly_sales
    ) add_delta_weeks
) AS add_before_after
ORDER BY year;

```

## local309.sql

```sql
with year_points as (
    select races.year,
           drivers.forename || ' ' || drivers.surname as driver,
           constructors.name as constructor,
           sum(results.points) as points
    from results
    left join races on results.race_id = races.race_id  -- Ensure these columns exist in your schema
    left join drivers on results.driver_id = drivers.driver_id  -- Ensure these columns exist in your schema
    left join constructors on results.constructor_id = constructors.constructor_id  -- Ensure these columns exist in your schema
    group by races.year, driver
    union
    select races.year,
           null as driver,
           constructors.name as constructor,
           sum(results.points) as points
    from results
    left join races on results.race_id = races.race_id  -- Ensure these columns exist in your schema
    left join drivers on results.driver_id = drivers.driver_id  -- Ensure these columns exist in your schema
    left join constructors on results.constructor_id = constructors.constructor_id  -- Ensure these columns exist in your schema
    group by races.year, constructor
),
max_points as (
    select year,
           max(case when driver is not null then points else null end) as max_driver_points,
           max(case when constructor is not null then points else null end) as max_constructor_points
    from year_points
    group by year
)
select max_points.year,
       drivers_year_points.driver,
       constructors_year_points.constructor
from max_points
left join year_points as drivers_year_points on
    max_points.year = drivers_year_points.year and
    max_points.max_driver_points = drivers_year_points.points and
    drivers_year_points.driver is not null
left join year_points as constructors_year_points on
    max_points.year = constructors_year_points.year and
    max_points.max_constructor_points = constructors_year_points.points and
    constructors_year_points.constructor is not null
order by max_points.year;

```

# sf

## sf001.sql

```sql
WITH timestamps AS
(   
    SELECT
        DATE_TRUNC(year,DATEADD(year,-1,DATE '2024-08-29')) AS ref_timestamp,
        LAST_DAY(DATEADD(week,2 + CAST(WEEKISO(ref_timestamp) != 1 AS INTEGER),ref_timestamp),week) AS end_week,
        DATEADD(day, day_num - 7, end_week) AS date_valid_std
    FROM
    (   
        SELECT
            ROW_NUMBER() OVER (ORDER BY SEQ1()) AS day_num
        FROM
            TABLE(GENERATOR(rowcount => 7))
    ) 
)
SELECT
    country,
    postal_code,
    date_valid_std,
    tot_snowfall_in 
FROM 
    GLOBAL_WEATHER__CLIMATE_DATA_FOR_BI.standard_tile.history_day
NATURAL INNER JOIN
    timestamps
WHERE
    country='US' AND
    tot_snowfall_in > 6.0 
ORDER BY 
    postal_code,date_valid_std
;

```

## sf002.sql

```sql
WITH big_banks AS (
    SELECT id_rssd
    FROM FINANCE__ECONOMICS.CYBERSYN.financial_institution_timeseries
    WHERE variable = 'ASSET'
      AND date = '2022-12-31'
      AND value > 1E10
)
SELECT name
FROM FINANCE__ECONOMICS.CYBERSYN.financial_institution_timeseries AS ts
INNER JOIN FINANCE__ECONOMICS.CYBERSYN.financial_institution_attributes AS att ON (ts.variable = att.variable)
INNER JOIN FINANCE__ECONOMICS.CYBERSYN.financial_institution_entities AS ent ON (ts.id_rssd = ent.id_rssd)
INNER JOIN big_banks ON (big_banks.id_rssd = ts.id_rssd)
WHERE ts.date = '2022-12-31'
  AND att.variable_name = '% Insured (Estimated)'
  AND att.frequency = 'Quarterly'
  AND ent.is_active = True
ORDER BY (1 - value) DESC
LIMIT 10;

```

## sf011.sql

```sql
 WITH TractPop AS (
    SELECT
        CG."BlockGroupID",
        FCV."CensusValue",
        CG."StateCountyTractID",
        CG."BlockGroupPolygon"
    FROM
        CENSUS_GALAXY__ZIP_CODE_TO_BLOCK_GROUP_SAMPLE.PUBLIC."Dim_CensusGeography" CG
    JOIN
        CENSUS_GALAXY__ZIP_CODE_TO_BLOCK_GROUP_SAMPLE.PUBLIC."Fact_CensusValues_ACS2021" FCV
        ON CG."BlockGroupID" = FCV."BlockGroupID"
    WHERE
        CG."StateAbbrev" = 'NY'
        AND FCV."MetricID" = 'B01003_001E'
),

TractGroup AS (
    SELECT
        CG."StateCountyTractID",
        SUM(FCV."CensusValue") AS "TotalTractPop"
    FROM
        CENSUS_GALAXY__ZIP_CODE_TO_BLOCK_GROUP_SAMPLE.PUBLIC."Dim_CensusGeography" CG
    JOIN
        CENSUS_GALAXY__ZIP_CODE_TO_BLOCK_GROUP_SAMPLE.PUBLIC."Fact_CensusValues_ACS2021" FCV
        ON CG."BlockGroupID" = FCV."BlockGroupID"
    WHERE
        CG."StateAbbrev" = 'NY'
        AND FCV."MetricID" = 'B01003_001E'
    GROUP BY
        CG."StateCountyTractID"
)

SELECT
    TP."BlockGroupID",
    TP."CensusValue",
    TP."StateCountyTractID",
    TG."TotalTractPop",
    CASE WHEN TG."TotalTractPop" <> 0 THEN TP."CensusValue" / TG."TotalTractPop" ELSE 0 END AS "BlockGroupRatio"
FROM
    TractPop TP
JOIN
    TractGroup TG
    ON TP."StateCountyTractID" = TG."StateCountyTractID";

```

## sf012.sql

```sql
SELECT 
    YEAR(claims.date_of_loss)               AS year_of_loss,
    claims.nfip_community_name,
    SUM(claims.building_damage_amount) AS total_building_damage_amount,
    SUM(claims.contents_damage_amount) AS total_contents_damage_amount
FROM WEATHER__ENVIRONMENT.CYBERSYN.fema_national_flood_insurance_program_claim_index claims
WHERE 
    claims.nfip_community_name = 'City Of New York' 
    AND year_of_loss >=2010 AND year_of_loss <=2019
GROUP BY year_of_loss, claims.nfip_community_name
ORDER BY year_of_loss, claims.nfip_community_name;

```

## sf014.sql

```sql
WITH Commuters AS (
    SELECT
        GE."ZipCode",
        SUM(CASE WHEN M."MetricID" = 'B08303_013E' THEN F."CensusValueByZip" ELSE 0 END +
            CASE WHEN M."MetricID" = 'B08303_012E' THEN F."CensusValueByZip" ELSE 0 END) AS "Num_Commuters_1Hr_Travel_Time"
    FROM
        CENSUS_GALAXY__AIML_MODEL_DATA_ENRICHMENT_SAMPLE.PUBLIC."LU_GeographyExpanded" GE
    JOIN
        CENSUS_GALAXY__AIML_MODEL_DATA_ENRICHMENT_SAMPLE.PUBLIC."Fact_CensusValues_ACS2021_ByZip" F
        ON GE."ZipCode" = F."ZipCode"
    JOIN
        CENSUS_GALAXY__AIML_MODEL_DATA_ENRICHMENT_SAMPLE.PUBLIC."Dim_CensusMetrics" M
        ON F."MetricID" = M."MetricID"
    WHERE
        GE."PreferredStateAbbrev" = 'NY'
        AND (M."MetricID" = 'B08303_013E' OR M."MetricID" = 'B08303_012E') -- Metric IDs for commuters with 1+ hour travel time
    GROUP BY
        GE."ZipCode"
),

StateBenchmark AS (
    SELECT
        SB."StateAbbrev",
        SUM(SB."StateBenchmarkValue") AS "StateBenchmark_Over1HrTravelTime",
        SB."TotalStatePopulation"
    FROM
        CENSUS_GALAXY__AIML_MODEL_DATA_ENRICHMENT_SAMPLE.PUBLIC."Fact_StateBenchmark_ACS2021" SB
    WHERE
        SB."MetricID" IN ('B08303_013E', 'B08303_012E')
        AND SB."StateAbbrev" = 'NY'
    GROUP BY
        SB."StateAbbrev", SB."TotalStatePopulation"
)

SELECT
    C."ZipCode",
    SUM(C."Num_Commuters_1Hr_Travel_Time") AS "Total_Commuters_1Hr_Travel_Time",
    SB."StateBenchmark_Over1HrTravelTime",
    SB."TotalStatePopulation",
FROM
    Commuters C
CROSS JOIN
    StateBenchmark SB
GROUP BY
    C."ZipCode", SB."StateBenchmark_Over1HrTravelTime", SB."TotalStatePopulation"
ORDER BY
    "Total_Commuters_1Hr_Travel_Time" DESC
LIMIT 1;



```

## sf018.sql

```sql
WITH push_send AS (
    SELECT
        id,
        app_group_id,
        user_id,
        campaign_id,
        message_variation_id,
        platform,
        ad_tracking_enabled,
        TO_TIMESTAMP(TIME) AS "TIME",
        'Send' AS "EVENT_TYPE"
    FROM
        BRAZE_USER_EVENT_DEMO_DATASET.PUBLIC.USERS_MESSAGES_PUSHNOTIFICATION_SEND_VIEW
    WHERE
        TO_TIMESTAMP(TIME) BETWEEN '2023-06-01 08:00:00' AND '2023-06-01 09:00:00'
),
push_bounce AS (
    SELECT
        id,
        app_group_id,
        user_id,
        campaign_id,
        message_variation_id,
        platform,
        ad_tracking_enabled,
        TO_TIMESTAMP(TIME) AS "TIME",
        'Bounce' AS "EVENT_TYPE"
    FROM
        BRAZE_USER_EVENT_DEMO_DATASET.PUBLIC.USERS_MESSAGES_PUSHNOTIFICATION_BOUNCE_VIEW
    WHERE
        TO_TIMESTAMP(TIME) BETWEEN '2023-06-01 08:00:00' AND '2023-06-01 09:00:00'
),
push_open AS (
    SELECT
        id,
        app_group_id,
        user_id,
        campaign_id,
        message_variation_id,
        platform,
        ad_tracking_enabled,
        TO_TIMESTAMP(TIME) AS "TIME",
        'Open' AS "EVENT_TYPE",
        carrier,
        browser,
        device_model
    FROM
        BRAZE_USER_EVENT_DEMO_DATASET.PUBLIC.USERS_MESSAGES_PUSHNOTIFICATION_OPEN_VIEW
    WHERE
        TO_TIMESTAMP(TIME) BETWEEN '2023-06-01 08:00:00' AND '2023-06-01 09:00:00'
),
push_open_influence AS (
    SELECT
        id,
        app_group_id,
        user_id,
        campaign_id,
        message_variation_id,
        platform,
        TO_TIMESTAMP(TIME) AS "TIME",
        'Influenced Open' AS "EVENT_TYPE",
        carrier,
        browser,
        device_model
    FROM
        BRAZE_USER_EVENT_DEMO_DATASET.PUBLIC.USERS_MESSAGES_PUSHNOTIFICATION_INFLUENCEDOPEN_VIEW
    WHERE
        TO_TIMESTAMP(TIME) BETWEEN '2023-06-01 08:00:00' AND '2023-06-01 09:00:00'
)
SELECT
    ps.app_group_id,
    ps.campaign_id,
    ps.user_id,
    ps.time,
    po.time push_open_time,
    ps.message_variation_id,
    ps.platform,
    ps.ad_tracking_enabled,
    po.carrier,
    po.browser,
    po.device_model,
    COUNT(
        DISTINCT ps.id
    ) push_notification_sends,
    COUNT(
        DISTINCT ps.user_id
    ) unique_push_notification_sends,
    COUNT(
        DISTINCT pb.id
    ) push_notification_bounced,
    COUNT(
        DISTINCT pb.user_id
    ) unique_push_notification_bounced,
    COUNT(
        DISTINCT po.id
    ) push_notification_open,
    COUNT(
        DISTINCT po.user_id
    ) unique_push_notification_opened,
    COUNT(
        DISTINCT poi.id
    ) push_notification_influenced_open,
    COUNT(
        DISTINCT poi.user_id
    ) unique_push_notification_influenced_open
FROM
    push_send ps
    LEFT JOIN push_bounce pb
    ON ps.message_variation_id = pb.message_variation_id
    AND ps.user_id = pb.user_id
    AND ps.app_group_id = pb.app_group_id
    LEFT JOIN push_open po
    ON ps.message_variation_id = po.message_variation_id
    AND ps.user_id = po.user_id
    AND ps.app_group_id = po.app_group_id
    LEFT JOIN push_open_influence poi
    ON ps.message_variation_id = poi.message_variation_id
    AND ps.user_id = poi.user_id
    AND ps.app_group_id = poi.app_group_id
GROUP BY
    1,2,3,4,5,6,7,8,9,10,11;

```

## sf040.sql

```sql
WITH zip_areas AS (
    SELECT
        geo.geo_id,
        geo.geo_name AS zip,
        states.related_geo_name AS state,
        countries.related_geo_name AS country,
        ST_AREA(TRY_TO_GEOGRAPHY(value)) AS area
    FROM US_ADDRESSES__POI.CYBERSYN.geography_index AS geo
    JOIN US_ADDRESSES__POI.CYBERSYN.geography_relationships AS states
        ON (geo.geo_id = states.geo_id AND states.related_level = 'State')
    JOIN US_ADDRESSES__POI.CYBERSYN.geography_relationships AS countries
        ON (geo.geo_id = countries.geo_id AND countries.related_level = 'Country')
    JOIN US_ADDRESSES__POI.CYBERSYN.geography_characteristics AS chars
        ON (geo.geo_id = chars.geo_id AND chars.relationship_type = 'coordinates_geojson')
    WHERE geo.level = 'CensusZipCodeTabulationArea'
),

zip_area_ranks AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY country, state ORDER BY area DESC, geo_id) AS zip_area_rank
    FROM zip_areas
)

SELECT addr.number, addr.street, addr.street_type
FROM US_ADDRESSES__POI.CYBERSYN.us_addresses AS addr
JOIN zip_area_ranks AS areas
    ON (addr.id_zip = areas.geo_id)
WHERE addr.state = 'FL' AND areas.country = 'United States' AND areas.zip_area_rank = 1
ORDER BY LATITUDE DESC
LIMIT 10;

```

## sf044.sql

```sql
WITH ytd_performance AS (
  SELECT
    ticker,
    MIN(date) OVER (PARTITION BY ticker) AS start_of_year_date,
    FIRST_VALUE(value) OVER (PARTITION BY ticker ORDER BY date ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS start_of_year_price,
    MAX(date) OVER (PARTITION BY ticker) AS latest_date,
    LAST_VALUE(value) OVER (PARTITION BY ticker ORDER BY date ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS latest_price
  FROM FINANCE__ECONOMICS.CYBERSYN.stock_price_timeseries
  WHERE
    ticker IN ('AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'TSLA', 'NVDA')
    AND date BETWEEN DATE '2024-01-01' AND DATE '2024-06-30'  -- Adjusted to cover only from the start of 2024 to the end of June 2024
    AND variable_name = 'Post-Market Close'
)
SELECT
  ticker,
  (latest_price - start_of_year_price) / start_of_year_price * 100 AS percentage_change_ytd
FROM
  ytd_performance
GROUP BY
  ticker, start_of_year_date, start_of_year_price, latest_date, latest_price
ORDER BY percentage_change_ytd DESC;

```

# sf_bq

## sf_bq012.sql

```sql
WITH double_entry_book AS (
  -- Debits
  SELECT 
    "to_address" AS "address",
    "value" AS "value"
  FROM "ETHEREUM_BLOCKCHAIN"."ETHEREUM_BLOCKCHAIN"."TRACES"
  WHERE "to_address" IS NOT NULL
    AND "status" = 1
    AND ("call_type" NOT IN ('delegatecall', 'callcode', 'staticcall') OR "call_type" IS NULL)
  
  UNION ALL
  
  -- Credits
  SELECT 
    "from_address" AS "address",
    - "value" AS "value"
  FROM "ETHEREUM_BLOCKCHAIN"."ETHEREUM_BLOCKCHAIN"."TRACES"
  WHERE "from_address" IS NOT NULL
    AND "status" = 1
    AND ("call_type" NOT IN ('delegatecall', 'callcode', 'staticcall') OR "call_type" IS NULL)
  
  UNION ALL
  
  -- Transaction fees debits
  SELECT 
    "miner" AS "address",
    SUM(CAST("receipt_gas_used" AS NUMBER) * CAST("gas_price" AS NUMBER)) AS "value"
  FROM "ETHEREUM_BLOCKCHAIN"."ETHEREUM_BLOCKCHAIN"."TRANSACTIONS" AS "transactions"
  JOIN "ETHEREUM_BLOCKCHAIN"."ETHEREUM_BLOCKCHAIN"."BLOCKS" AS "blocks"
    ON "blocks"."number" = "transactions"."block_number"
  GROUP BY "blocks"."miner"
  
  UNION ALL
  
  -- Transaction fees credits
  SELECT 
    "from_address" AS "address",
    -(CAST("receipt_gas_used" AS NUMBER) * CAST("gas_price" AS NUMBER)) AS "value"
  FROM "ETHEREUM_BLOCKCHAIN"."ETHEREUM_BLOCKCHAIN"."TRANSACTIONS"
),
top_10_balances AS (
  SELECT
    "address",
    SUM("value") AS "balance"
  FROM double_entry_book
  GROUP BY "address"
  ORDER BY "balance" DESC
  LIMIT 10
)
SELECT 
    ROUND(AVG("balance") / 1e15, 2) AS "average_balance_trillion"
FROM top_10_balances;

```

## sf_bq017.sql

```sql
WITH bounding_area AS (
    SELECT "geometry" AS geometry
    FROM GEO_OPENSTREETMAP.GEO_OPENSTREETMAP.PLANET_FEATURES,
    LATERAL FLATTEN(INPUT => planet_features."all_tags") AS "tag"
    WHERE "feature_type" = 'multipolygons'
      AND "tag".value:"key" = 'wikidata'
      AND "tag".value:"value" = 'Q35'
),

highway_info AS (
    SELECT 
        SUM(ST_LENGTH(
                ST_GEOGRAPHYFROMWKB(planet_features."geometry")
            )
        ) AS highway_length,
        "tag".value:"value" AS highway_type
    FROM 
        GEO_OPENSTREETMAP.GEO_OPENSTREETMAP.PLANET_FEATURES AS planet_features,
        bounding_area
    CROSS JOIN LATERAL FLATTEN(INPUT => planet_features."all_tags") AS "tag"
    WHERE "tag".value:"key" = 'highway'
    AND "feature_type" = 'lines'
    AND ST_DWITHIN(
        ST_GEOGFROMWKB(planet_features."geometry"), 
        ST_GEOGFROMWKB(bounding_area.geometry),
        0.0
    ) 
    GROUP BY highway_type
)

SELECT 
  REPLACE(highway_type, '"', '') AS highway_type
FROM
  highway_info
ORDER BY 
  highway_length DESC
LIMIT 5;

```

## sf_bq028.sql

```sql
WITH HighestReleases AS (
    SELECT
        HR."Name",
        HR."Version"
    FROM (
        SELECT
            "Name",
            "Version",
            ROW_NUMBER() OVER (
                PARTITION BY "Name"
                ORDER BY 
                    TO_NUMBER(PARSE_JSON("VersionInfo"):"Ordinal") DESC
            ) AS RowNumber
        FROM
            DEPS_DEV_V1.DEPS_DEV_V1.PACKAGEVERSIONS
        WHERE
            "System" = 'NPM'
            AND TO_BOOLEAN(PARSE_JSON("VersionInfo"):"IsRelease") = TRUE
    ) AS HR
    WHERE HR.RowNumber = 1
),
PVP AS (
    SELECT
        PVP."Name", 
        PVP."Version", 
        PVP."ProjectType", 
        PVP."ProjectName"
    FROM
        DEPS_DEV_V1.DEPS_DEV_V1.PACKAGEVERSIONTOPROJECT AS PVP
    JOIN
        HighestReleases AS HR
    ON
        PVP."Name" = HR."Name"
        AND PVP."Version" = HR."Version"
    WHERE
        PVP."System" = 'NPM'
        AND PVP."ProjectType" = 'GITHUB'
)
SELECT
    PVP."Name", 
    PVP."Version"
FROM
    PVP
JOIN
    DEPS_DEV_V1.DEPS_DEV_V1.PROJECTS AS P
ON
    PVP."ProjectType" = P."Type" 
    AND PVP."ProjectName" = P."Name"
ORDER BY 
    P."StarsCount" DESC
LIMIT 8;

```

## sf_bq033.sql

```sql
WITH Patent_Matches AS (
    SELECT
      TO_DATE(CAST(ANY_VALUE(patentsdb."filing_date") AS STRING), 'YYYYMMDD') AS Patent_Filing_Date,
      patentsdb."application_number" AS Patent_Application_Number,
      MAX(abstract_info.value:"text") AS Patent_Title,
      MAX(abstract_info.value:"language") AS Patent_Title_Language
    FROM
      PATENTS.PATENTS.PUBLICATIONS AS patentsdb,
      LATERAL FLATTEN(input => patentsdb."abstract_localized") AS abstract_info
    WHERE
      LOWER(abstract_info.value:"text") LIKE '%internet of things%'
      AND patentsdb."country_code" = 'US'
    GROUP BY
      Patent_Application_Number
),

Date_Series_Table AS (
    SELECT
        DATEADD(day, seq4(), DATE '2008-01-01') AS day,
        0 AS Number_of_Patents
    FROM
        TABLE(
            GENERATOR(
                ROWCOUNT => 5479
            )
        )
    ORDER BY
        day
)

SELECT
  TO_CHAR(Date_Series_Table.day, 'YYYY-MM') AS Patent_Date_YearMonth,
  COUNT(Patent_Matches.Patent_Application_Number) AS Number_of_Patent_Applications
FROM
  Date_Series_Table
  LEFT JOIN Patent_Matches
    ON Date_Series_Table.day = Patent_Matches.Patent_Filing_Date
WHERE
    Date_Series_Table.day < DATE '2023-01-01'
GROUP BY
  TO_CHAR(Date_Series_Table.day, 'YYYY-MM')
ORDER BY
  Patent_Date_YearMonth;

```

## sf_bq037.sql

```sql
WITH A AS (
    SELECT
        "reference_bases",
        "start_position"
    FROM
        "HUMAN_GENOME_VARIANTS"."HUMAN_GENOME_VARIANTS"."_1000_GENOMES_PHASE_3_OPTIMIZED_SCHEMA_VARIANTS_20150220"
    WHERE
        "reference_bases" IN ('AT', 'TA')
),
B AS (
    SELECT
        "reference_bases",
        MIN("start_position") AS "min_start_position",
        MAX("start_position") AS "max_start_position",
        COUNT(1) AS "total_count"
    FROM
        A
    GROUP BY
        "reference_bases"
),
min_counts AS (
    SELECT
        A."reference_bases",  -- Explicitly referencing the column from table A
        A."start_position" AS "min_start_position",
        COUNT(1) AS "min_count"
    FROM
        A
    INNER JOIN B 
        ON A."reference_bases" = B."reference_bases"
    WHERE
        A."start_position" = B."min_start_position"
    GROUP BY
        A."reference_bases", A."start_position"
),
max_counts AS (
    SELECT
        A."reference_bases",  -- Explicitly referencing the column from table A
        A."start_position" AS "max_start_position",
        COUNT(1) AS "max_count"
    FROM
        A
    INNER JOIN B
        ON A."reference_bases" = B."reference_bases"
    WHERE
        A."start_position" = B."max_start_position"
    GROUP BY
        A."reference_bases", A."start_position"
)
SELECT
    B."reference_bases",  -- Explicitly referencing the column from table B
    B."min_start_position",
    CAST(min_counts."min_count" AS FLOAT) / B."total_count" AS "min_position_ratio",
    B."max_start_position",
    CAST(max_counts."max_count" AS FLOAT) / B."total_count" AS "max_position_ratio"
FROM
    B
LEFT JOIN
    min_counts ON B."reference_bases" = min_counts."reference_bases" AND B."min_start_position" = min_counts."min_start_position"
LEFT JOIN
    max_counts ON B."reference_bases" = max_counts."reference_bases" AND B."max_start_position" = max_counts."max_start_position"
ORDER BY
    B."reference_bases";

```

## sf_bq043.sql

```sql
SELECT
  genex."case_barcode" AS "case_barcode",
  genex."sample_barcode" AS "sample_barcode",
  genex."aliquot_barcode" AS "aliquot_barcode",
  genex."HGNC_gene_symbol" AS "HGNC_gene_symbol",
  clinical_info."Variant_Type" AS "Variant_Type",
  genex."gene_id" AS "gene_id",
  genex."normalized_count" AS "normalized_count",
  genex."project_short_name" AS "project_short_name",
  clinical_info."demo__gender" AS "gender",
  clinical_info."demo__vital_status" AS "vital_status",
  clinical_info."demo__days_to_death" AS "days_to_death"
FROM ( 
  SELECT
    case_list."Variant_Type" AS "Variant_Type",
    case_list."case_barcode" AS "case_barcode",
    clinical."demo__gender",
    clinical."demo__vital_status",
    clinical."demo__days_to_death"
  FROM
    (SELECT
      mutation."case_barcode",
      mutation."Variant_Type"
    FROM
      "TCGA"."TCGA_VERSIONED"."SOMATIC_MUTATION_HG19_DCC_2017_02" AS mutation
    WHERE
      mutation."Hugo_Symbol" = 'CDKN2A'
      AND mutation."project_short_name" = 'TCGA-BLCA'
    GROUP BY
      mutation."case_barcode",
      mutation."Variant_Type"
    ORDER BY
      mutation."case_barcode"
    ) AS case_list /* end case_list */
  INNER JOIN
    "TCGA"."TCGA_VERSIONED"."CLINICAL_GDC_R39" AS clinical
  ON
    case_list."case_barcode" = clinical."submitter_id" /* end clinical annotation */ ) AS clinical_info
INNER JOIN
  "TCGA"."TCGA_VERSIONED"."RNASEQ_HG19_GDC_2017_02" AS genex
ON
  genex."case_barcode" = clinical_info."case_barcode"
WHERE
  genex."HGNC_gene_symbol" IN ('MDM2', 'TP53', 'CDKN1A','CCNE1')
ORDER BY
  "case_barcode",
  "HGNC_gene_symbol";

```

## sf_bq050.sql

```sql
WITH data AS (
    SELECT
        "ZIPSTARTNAME"."borough" AS "borough_start",
        "ZIPSTARTNAME"."neighborhood" AS "neighborhood_start",
        "ZIPENDNAME"."borough" AS "borough_end",
        "ZIPENDNAME"."neighborhood" AS "neighborhood_end",
        CAST("TRI"."tripduration" / 60 AS NUMERIC) AS "trip_minutes",
        "WEA"."temp" AS "temperature",
        CAST("WEA"."wdsp" AS NUMERIC) AS "wind_speed",
        "WEA"."prcp" AS "precipitation",
        EXTRACT(MONTH FROM DATE("TRI"."starttime")) AS "start_month"
    FROM
        "NEW_YORK_CITIBIKE_1"."NEW_YORK_CITIBIKE"."CITIBIKE_TRIPS" AS "TRI"
    INNER JOIN
        "NEW_YORK_CITIBIKE_1"."GEO_US_BOUNDARIES"."ZIP_CODES" AS "ZIPSTART"
        ON ST_WITHIN(
            ST_POINT("TRI"."start_station_longitude", "TRI"."start_station_latitude"),
            ST_GEOGFROMWKB("ZIPSTART"."zip_code_geom")
        )
    INNER JOIN
        "NEW_YORK_CITIBIKE_1"."GEO_US_BOUNDARIES"."ZIP_CODES" AS "ZIPEND"
        ON ST_WITHIN(
            ST_POINT("TRI"."end_station_longitude", "TRI"."end_station_latitude"),
            ST_GEOGFROMWKB("ZIPEND"."zip_code_geom")
        )
    INNER JOIN
        "NEW_YORK_CITIBIKE_1"."NOAA_GSOD"."GSOD2014" AS "WEA"
        ON TO_DATE(CONCAT("WEA"."year", LPAD("WEA"."mo", 2, '0'), LPAD("WEA"."da", 2, '0')), 'YYYYMMDD') = DATE("TRI"."starttime")
    INNER JOIN
        "NEW_YORK_CITIBIKE_1"."CYCLISTIC"."ZIP_CODES" AS "ZIPSTARTNAME"
        ON "ZIPSTART"."zip_code" = CAST("ZIPSTARTNAME"."zip" AS STRING)
    INNER JOIN
        "NEW_YORK_CITIBIKE_1"."CYCLISTIC"."ZIP_CODES" AS "ZIPENDNAME"
        ON "ZIPEND"."zip_code" = CAST("ZIPENDNAME"."zip" AS STRING)
    WHERE
        "WEA"."wban" = (
            SELECT "wban" 
            FROM "NEW_YORK_CITIBIKE_1"."NOAA_GSOD"."STATIONS"
            WHERE
                "state" = 'NY'
                AND LOWER("name") LIKE LOWER('%New York Central Park%')
            LIMIT 1
        )
        AND EXTRACT(YEAR FROM DATE("TRI"."starttime")) = 2014
),
agg_data AS (
    SELECT
        "borough_start",
        "neighborhood_start",
        "borough_end",
        "neighborhood_end",
        COUNT(*) AS "num_trips",
        ROUND(AVG("trip_minutes"), 1) AS "avg_trip_minutes",
        ROUND(AVG("temperature"), 1) AS "avg_temperature",
        ROUND(AVG("wind_speed"), 1) AS "avg_wind_speed",
        ROUND(AVG("precipitation"), 1) AS "avg_precipitation"
    FROM data
    GROUP BY
        "borough_start",
        "neighborhood_start",
        "borough_end",
        "neighborhood_end"
),
most_common_months AS (
    SELECT
        "borough_start",
        "neighborhood_start",
        "borough_end",
        "neighborhood_end",
        "start_month",
        ROW_NUMBER() OVER (
            PARTITION BY "borough_start", "neighborhood_start", "borough_end", "neighborhood_end" 
            ORDER BY COUNT(*) DESC
        ) AS "row_num"
    FROM data
    GROUP BY
        "borough_start",
        "neighborhood_start",
        "borough_end",
        "neighborhood_end",
        "start_month"
)

SELECT
    a.*,
    m."start_month" AS "most_common_month"
FROM
    agg_data a
JOIN
    most_common_months m
    ON a."borough_start" = m."borough_start" 
    AND a."neighborhood_start" = m."neighborhood_start" 
    AND a."borough_end" = m."borough_end" 
    AND a."neighborhood_end" = m."neighborhood_end" 
    AND m."row_num" = 1
ORDER BY 
    a."neighborhood_start", 
    a."neighborhood_end";

```

## sf_bq052.sql

```sql
SELECT
    app."patent_id" AS "patent_id",
    patent."title",
    app."date" AS "application_date",
    filterData."bkwdCitations_1",
    filterData."fwrdCitations_1",
    summary."text" AS "summary_text"
FROM
    PATENTSVIEW.PATENTSVIEW.BRF_SUM_TEXT AS summary
JOIN
    PATENTSVIEW.PATENTSVIEW.PATENT AS patent
    ON summary."patent_id" = patent."id"
JOIN
    PATENTSVIEW.PATENTSVIEW.APPLICATION AS app
    ON app."patent_id" = summary."patent_id"
JOIN (
    SELECT DISTINCT
        cpc."patent_id",
        IFNULL(citation_1."bkwdCitations_1", 0) AS "bkwdCitations_1",
        IFNULL(citation_1."fwrdCitations_1", 0) AS "fwrdCitations_1"
    FROM
        PATENTSVIEW.PATENTSVIEW.CPC_CURRENT AS cpc
    JOIN (
        SELECT
            b."patent_id",
            b."bkwdCitations_1",
            f."fwrdCitations_1"
        FROM (
            SELECT
                cited."patent_id",
                COUNT(*) AS "fwrdCitations_1"
            FROM
                PATENTSVIEW.PATENTSVIEW.USPATENTCITATION AS cited
            JOIN
                PATENTSVIEW.PATENTSVIEW.APPLICATION AS apps
                ON cited."patent_id" = apps."patent_id"
            WHERE
                apps."country" = 'US'
                AND cited."date" >= apps."date"
                AND TRY_CAST(cited."date" AS DATE) <= DATEADD(MONTH, 1, TRY_CAST(apps."date" AS DATE)) -- Citation within 1 month
            GROUP BY
                cited."patent_id"
        ) AS f
        JOIN (
            SELECT
                cited."patent_id",
                COUNT(*) AS "bkwdCitations_1"
            FROM
                PATENTSVIEW.PATENTSVIEW.USPATENTCITATION AS cited
            JOIN
                PATENTSVIEW.PATENTSVIEW.APPLICATION AS apps
                ON cited."patent_id" = apps."patent_id"
            WHERE
                apps."country" = 'US'
                AND cited."date" < apps."date"
                AND TRY_CAST(cited."date" AS DATE) >= DATEADD(MONTH, -1, TRY_CAST(apps."date" AS DATE)) -- Citation within 1 month before
            GROUP BY
                cited."patent_id"
        ) AS b
        ON b."patent_id" = f."patent_id"
        WHERE
            b."bkwdCitations_1" IS NOT NULL
            AND f."fwrdCitations_1" IS NOT NULL
            AND (b."bkwdCitations_1" > 0 OR f."fwrdCitations_1" > 0)
    ) AS citation_1
    ON cpc."patent_id" = citation_1."patent_id"
    WHERE
        cpc."subsection_id" = 'C05'
        OR cpc."group_id" = 'A01G'
) AS filterData
ON app."patent_id" = filterData."patent_id"
ORDER BY app."date";

```

## sf_bq057.sql

```sql
WITH totals AS (
    -- Aggregate monthly totals for Bitcoin txs, input/output UTXOs,
    -- and input/output values (UTXO stands for Unspent Transaction Output)
    SELECT
        "txs_tot"."block_timestamp_month" AS tx_month,
        COUNT("txs_tot"."hash") AS tx_count,
        SUM("txs_tot"."input_count") AS tx_inputs,
        SUM("txs_tot"."output_count") AS tx_outputs,
        SUM("txs_tot"."input_value") / 100000000 AS tx_input_val,
        SUM("txs_tot"."output_value") / 100000000 AS tx_output_val
    FROM CRYPTO.CRYPTO_BITCOIN.TRANSACTIONS AS "txs_tot"
    WHERE "txs_tot"."block_timestamp_month" BETWEEN CAST('2021-01-01' AS DATE) AND CAST('2021-12-31' AS DATE)
    GROUP BY "txs_tot"."block_timestamp_month"
    ORDER BY "txs_tot"."block_timestamp_month" DESC
),
coinjoinOuts AS (
    -- Builds a table where each row represents an output of a 
    -- potential CoinJoin tx, defined as a tx that had more 
    -- than two outputs and had a total output value less than its
    -- input value, per Adam Fiscor's description in this article: 
    SELECT 
        "txs"."hash",
        "txs"."block_number",
        "txs"."block_timestamp_month",
        "txs"."input_count",
        "txs"."output_count",
        "txs"."input_value",
        "txs"."output_value",
        "o".value:"value" AS "outputs_val"
    FROM CRYPTO.CRYPTO_BITCOIN.TRANSACTIONS AS "txs", 
         LATERAL FLATTEN(INPUT => "txs"."outputs") AS "o"
    WHERE "txs"."output_count" > 2 
      AND "txs"."output_value" <= "txs"."input_value"
      AND "txs"."block_timestamp_month" BETWEEN CAST('2021-01-01' AS DATE) AND CAST('2021-12-31' AS DATE)
    ORDER BY "txs"."block_number", "txs"."hash" DESC
),
coinjoinTxs AS (
    -- Builds a table of just the distinct CoinJoin tx hashes
    -- which had more than one equal-value output.
    SELECT 
        "coinjoinouts"."hash" AS "cjhash",
        "coinjoinouts"."outputs_val" AS outputVal,
        COUNT(*) AS cjOuts
    FROM coinjoinOuts AS "coinjoinouts"
    GROUP BY "coinjoinouts"."hash", "coinjoinouts"."outputs_val"
    HAVING COUNT(*) > 1
),
coinjoinsD AS (
    -- Filter out all potential CoinJoin txs that did not have
    -- more than one equal-value output. Do not list the
    -- outputs themselves, only the distinct tx hashes and
    -- their input/output counts and values.
    SELECT DISTINCT 
        "coinjoinouts"."hash", 
        "coinjoinouts"."block_number", 
        "coinjoinouts"."block_timestamp_month",
        "coinjoinouts"."input_count",
        "coinjoinouts"."output_count",
        "coinjoinouts"."input_value",
        "coinjoinouts"."output_value"
    FROM coinjoinOuts AS "coinjoinouts"
    INNER JOIN coinjoinTxs AS "coinjointxs" 
        ON "coinjoinouts"."hash" = "coinjointxs"."cjhash"
),
coinjoins AS (
    -- Aggregate monthly totals for CoinJoin txs, input/output UTXOs,
    -- and input/output values
    SELECT 
        "cjs"."block_timestamp_month" AS cjs_month,
        COUNT("cjs"."hash") AS cjs_count,
        SUM("cjs"."input_count") AS cjs_inputs,
        SUM("cjs"."output_count") AS cjs_outputs,
        SUM("cjs"."input_value") / 100000000 AS cjs_input_val,
        SUM("cjs"."output_value") / 100000000 AS cjs_output_val
    FROM coinjoinsD AS "cjs"
    GROUP BY "cjs"."block_timestamp_month"
    ORDER BY "cjs"."block_timestamp_month" DESC
)
SELECT EXTRACT(MONTH FROM tx_month) AS month,
    -- Calculate resulting CoinJoin percentages:
    -- tx_percent = percent of monthly Bitcoin txs that were CoinJoins
    ROUND(coinjoins.cjs_count / totals.tx_count * 100, 1) AS tx_percent,
    
    -- utxos_percent = percent of monthly Bitcoin utxos that were CoinJoins
    ROUND((coinjoins.cjs_inputs / totals.tx_inputs + coinjoins.cjs_outputs / totals.tx_outputs) / 2 * 100, 1) AS utxos_percent,
    
    -- value_percent = percent of monthly Bitcoin volume that took place
    -- in CoinJoined transactions
    ROUND(coinjoins.cjs_input_val / totals.tx_input_val * 100, 1) AS value_percent
FROM totals
INNER JOIN coinjoins
    ON totals.tx_month = coinjoins.cjs_month
ORDER BY value_percent DESC
LIMIT 1;

```

## sf_bq068.sql

```sql
WITH double_entry_book AS (
    -- debits
    SELECT
        ARRAY_TO_STRING("inputs".value:addresses, ',') AS "address",  -- Use the correct JSON path notation
        "inputs".value:type AS "type",
        - "inputs".value:value AS "value"
    FROM CRYPTO.CRYPTO_BITCOIN_CASH.TRANSACTIONS,
         LATERAL FLATTEN(INPUT => "inputs") AS "inputs"
    WHERE TO_TIMESTAMP("block_timestamp" / 1000000) >= '2014-03-01' 
      AND TO_TIMESTAMP("block_timestamp" / 1000000) < '2014-04-01'

    UNION ALL
 
    -- credits
    SELECT
        ARRAY_TO_STRING("outputs".value:addresses, ',') AS "address",  -- Use the correct JSON path notation
        "outputs".value:type AS "type",
        "outputs".value:value AS "value"
    FROM CRYPTO.CRYPTO_BITCOIN_CASH.TRANSACTIONS, 
         LATERAL FLATTEN(INPUT => "outputs") AS "outputs"
    WHERE TO_TIMESTAMP("block_timestamp" / 1000000) >= '2014-03-01' 
      AND TO_TIMESTAMP("block_timestamp" / 1000000) < '2014-04-01'
),
address_balances AS (
    SELECT 
        "address",
        "type",
        SUM("value") AS "balance"
    FROM double_entry_book
    GROUP BY "address", "type"
),
max_min_balances AS (
    SELECT
        "type",
        MAX("balance") AS max_balance,
        MIN("balance") AS min_balance
    FROM address_balances
    GROUP BY "type"
)
SELECT
    REPLACE("type", '"', '') AS "type",  -- Replace double quotes with nothing
    max_balance,
    min_balance
FROM max_min_balances
ORDER BY "type";

```

## sf_bq070.sql

```sql
WITH
  sm_images AS (
    SELECT
      "SeriesInstanceUID" AS "digital_slide_id", 
      "StudyInstanceUID" AS "case_id",
      "ContainerIdentifier" AS "physical_slide_id",
      "PatientID" AS "patient_id",
      "TotalPixelMatrixColumns" AS "width", 
      "TotalPixelMatrixRows" AS "height",
      "collection_id",
      "crdc_instance_uuid",
      "gcs_url", 
      CAST(
        "SharedFunctionalGroupsSequence"[0]."PixelMeasuresSequence"[0]."PixelSpacing"[0] AS FLOAT
      ) AS "pixel_spacing", 
      CASE "TransferSyntaxUID"
          WHEN '1.2.840.10008.1.2.4.50' THEN 'jpeg'
          WHEN '1.2.840.10008.1.2.4.91' THEN 'jpeg2000'
          ELSE 'other'
      END AS "compression"
    FROM
      IDC.IDC_V17.DICOM_ALL
    WHERE
      "Modality" = 'SM' 
      AND "ImageType"[2] = 'VOLUME'
  ),

  tissue_types AS (
    SELECT DISTINCT *
    FROM (
      SELECT
        "SeriesInstanceUID" AS "digital_slide_id",
        CASE "steps_unnested2".value:"CodeValue"::STRING
            WHEN '17621005' THEN 'normal' -- meaning: 'Normal' (i.e., non-neoplastic)
            WHEN '86049000' THEN 'tumor'  -- meaning: 'Neoplasm, Primary'
            ELSE 'other'                 -- meaning: 'Neoplasm, Metastatic'
        END AS "tissue_type"
      FROM
        IDC.IDC_V17.DICOM_ALL
        CROSS JOIN
          LATERAL FLATTEN(input => "SpecimenDescriptionSequence"[0]."PrimaryAnatomicStructureSequence") AS "steps_unnested1"
        CROSS JOIN
          LATERAL FLATTEN(input => "steps_unnested1".value:"PrimaryAnatomicStructureModifierSequence") AS "steps_unnested2"
    )
  ),

  specimen_preparation_sequence_items AS (
    SELECT DISTINCT *
    FROM (
      SELECT
        "SeriesInstanceUID" AS "digital_slide_id",
        "steps_unnested2".value:"ConceptNameCodeSequence"[0]."CodeMeaning"::STRING AS "item_name",
        "steps_unnested2".value:"ConceptCodeSequence"[0]."CodeMeaning"::STRING AS "item_value"
      FROM
        IDC.IDC_V17.DICOM_ALL
        CROSS JOIN
          LATERAL FLATTEN(input => "SpecimenDescriptionSequence"[0]."SpecimenPreparationSequence") AS "steps_unnested1"
        CROSS JOIN
          LATERAL FLATTEN(input => "steps_unnested1".value:"SpecimenPreparationStepContentItemSequence") AS "steps_unnested2"
    )
  )

SELECT
  a.*,
  b."tissue_type",
  REPLACE(REPLACE(a."collection_id", 'tcga_luad', 'luad'), 'tcga_lusc', 'lscc') AS "cancer_subtype"
FROM 
  sm_images AS a
  JOIN tissue_types AS b 
    ON b."digital_slide_id" = a."digital_slide_id"
  JOIN specimen_preparation_sequence_items AS c 
    ON c."digital_slide_id" = a."digital_slide_id"
WHERE
  (a."collection_id" = 'tcga_luad' OR a."collection_id" = 'tcga_lusc')
  AND a."compression" != 'other'
  AND (b."tissue_type" = 'normal' OR b."tissue_type" = 'tumor')
  AND (c."item_name" = 'Embedding medium' AND c."item_value" = 'Tissue freezing medium')
ORDER BY 
  a."crdc_instance_uuid";

```

## sf_bq072.sql

```sql
WITH BlackRace AS (
    SELECT CAST("Code" AS INT) AS CODE
    FROM DEATH.DEATH.RACE
    WHERE LOWER("Description") LIKE '%black%'
)
SELECT 
    v."Age", 
    v."Total" AS "Vehicle_Total", 
    v."Black" AS "Vehicle_Black",
    g."Total" AS "Gun_Total", 
    g."Black" AS "Gun_Black"
FROM (
    SELECT 
        "Age", 
        COUNT(*) AS "Total", 
        COUNT_IF("Race" IN (SELECT CODE FROM BlackRace)) AS "Black"
    FROM DEATH.DEATH.DEATHRECORDS d
    JOIN (
        SELECT 
            DISTINCT e."DeathRecordId" AS "id"
        FROM DEATH.DEATH.ENTITYAXISCONDITIONS e
        JOIN (
            SELECT * 
            FROM DEATH.DEATH.ICD10CODE 
            WHERE LOWER("Description") LIKE '%vehicle%'
        ) c 
        ON e."Icd10Code" = c."Code"
    ) f
    ON d."Id" = f."id"
    WHERE "Age" BETWEEN 12 AND 18
    GROUP BY "Age"
) v  -- Vehicle

JOIN (
    SELECT 
        "Age", 
        COUNT(*) AS "Total", 
        COUNT_IF("Race" IN (SELECT CODE FROM BlackRace)) AS "Black"
    FROM DEATH.DEATH.DEATHRECORDS d
    JOIN (
        SELECT 
            DISTINCT e."DeathRecordId" AS "id"
        FROM DEATH.DEATH.ENTITYAXISCONDITIONS e
        JOIN (
            SELECT 
                "Code", "Description" 
            FROM DEATH.DEATH.ICD10CODE
            WHERE "Description" LIKE '%firearm%'
        ) c 
        ON e."Icd10Code" = c."Code"
    ) f
    ON d."Id" = f."id"
    WHERE "Age" BETWEEN 12 AND 18
    GROUP BY "Age"
) g
ON g."Age" = v."Age";

```

## sf_bq083.sql

```sql
SELECT 
  TO_DATE(TO_TIMESTAMP_NTZ("block_timestamp" / 1000000)) AS "Date",  -- 将时间戳转换为日期格式，除以1000000
  TO_CHAR(SUM(
      CASE
          WHEN "input" LIKE '0x40c10f19%' THEN 1
          ELSE -1
      END * 
      CAST(CONCAT('0x', LTRIM(SUBSTRING("input", 
                                       CASE 
                                           WHEN "input" LIKE '0x40c10f19%' THEN 75
                                           ELSE 11
                                       END, 64), '0')) AS FLOAT) / 1000000)
  , '$999,999,999,999') AS "Δ Total Market Value"
FROM 
  "CRYPTO"."CRYPTO_ETHEREUM"."TRANSACTIONS"
WHERE 
  TO_DATE(TO_TIMESTAMP_NTZ("block_timestamp" / 1000000)) BETWEEN '2023-01-01' AND '2023-12-31'
  AND "to_address" = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'  -- USDC Token
  AND ("input" LIKE '0x42966c68%' -- Burn
       OR "input" LIKE '0x40c10f19%' -- Mint
  )
GROUP BY 
  TO_DATE(TO_TIMESTAMP_NTZ("block_timestamp" / 1000000))
ORDER BY 
  "Date" DESC;

```

## sf_bq091.sql

```sql
WITH AA AS (
    SELECT 
        FIRST_VALUE("assignee_harmonized") OVER (PARTITION BY "application_number" ORDER BY "application_number") AS assignee_harmonized,
        FIRST_VALUE("filing_date") OVER (PARTITION BY "application_number" ORDER BY "application_number") AS filing_date,
        "application_number"
    FROM 
        PATENTS.PATENTS.PUBLICATIONS AS pubs
        , LATERAL FLATTEN(input => pubs."cpc") AS c
    WHERE 
        c.value:"code" LIKE 'A61%'
),

PatentApplications AS (
    SELECT 
        ANY_VALUE(assignee_harmonized) as assignee_harmonized,
        ANY_VALUE(filing_date) as filing_date
    FROM AA
    GROUP BY "application_number"
),

AssigneeApplications AS (
SELECT 
    COUNT(*) AS total_applications,
    a.value::STRING AS assignee_name,
    CAST(FLOOR(filing_date / 10000) AS INT) AS filing_year
FROM 
    PatentApplications
    , LATERAL FLATTEN(input => assignee_harmonized) AS a
GROUP BY 
    a.value::STRING, filing_year
),

TotalApplicationsPerAssignee AS (
    SELECT
        assignee_name,
        SUM(total_applications) AS total_applications
    FROM 
        AssigneeApplications
    GROUP BY 
        assignee_name
    ORDER BY 
        total_applications DESC
    LIMIT 1
),

MaxYearForTopAssignee AS (
    SELECT
        aa.assignee_name,
        aa.filing_year,
        aa.total_applications
    FROM 
        AssigneeApplications aa
    INNER JOIN
        TotalApplicationsPerAssignee tapa ON aa.assignee_name = tapa.assignee_name
    ORDER BY 
        aa.total_applications DESC
    LIMIT 1
)

SELECT filing_year
FROM 
    MaxYearForTopAssignee
    

```

## sf_bq093.sql

```sql
WITH double_entry_book AS (
    -- Debits
    SELECT 
        "to_address" AS "address", 
        "value" AS "value"
    FROM 
        CRYPTO.CRYPTO_ETHEREUM_CLASSIC.TRACES
    WHERE 
        "to_address" IS NOT NULL
        AND "status" = 1
        AND ("call_type" NOT IN ('delegatecall', 'callcode', 'staticcall') OR "call_type" IS NULL)
        AND TO_DATE(TO_TIMESTAMP("block_timestamp" / 1000000)) = '2016-10-14'

    UNION ALL
    
    -- Credits
    SELECT 
        "from_address" AS "address", 
        - "value" AS "value"
    FROM 
        CRYPTO.CRYPTO_ETHEREUM_CLASSIC.TRACES
    WHERE 
        "from_address" IS NOT NULL
        AND "status" = 1
        AND ("call_type" NOT IN ('delegatecall', 'callcode', 'staticcall') OR "call_type" IS NULL)
        AND TO_DATE(TO_TIMESTAMP("block_timestamp" / 1000000)) = '2016-10-14'

    UNION ALL

    -- Transaction Fees Debits
    SELECT 
        "miner" AS "address", 
        SUM(CAST("receipt_gas_used" AS NUMERIC) * CAST("gas_price" AS NUMERIC)) AS "value"
    FROM 
        CRYPTO.CRYPTO_ETHEREUM_CLASSIC.TRANSACTIONS AS "transactions"
    JOIN 
        CRYPTO.CRYPTO_ETHEREUM_CLASSIC.BLOCKS AS "blocks" 
        ON "blocks"."number" = "transactions"."block_number"
    WHERE 
        TO_DATE(TO_TIMESTAMP("block_timestamp" / 1000000)) = '2016-10-14'
    GROUP BY 
        "blocks"."miner"

    UNION ALL
    
    -- Transaction Fees Credits
    SELECT 
        "from_address" AS "address", 
        -(CAST("receipt_gas_used" AS NUMERIC) * CAST("gas_price" AS NUMERIC)) AS "value"
    FROM 
        CRYPTO.CRYPTO_ETHEREUM_CLASSIC.TRANSACTIONS
    WHERE 
        TO_DATE(TO_TIMESTAMP("block_timestamp" / 1000000)) = '2016-10-14'
),
net_changes AS (
    SELECT 
        "address",
        SUM("value") AS "net_change"
    FROM 
        double_entry_book
    GROUP BY 
        "address"
)
SELECT 
    MAX("net_change") AS "max_net_change",
    MIN("net_change") AS "min_net_change"
FROM
    net_changes;

```

## sf_bq099.sql

```sql
WITH PatentApplications AS (
   SELECT 
        "assignee_harmonized" AS assignee_harmonized,
        "filing_date" AS filing_date,
        "country_code" AS country_code,
        "application_number" AS application_number
    FROM 
        PATENTS.PATENTS.PUBLICATIONS AS pubs,
        LATERAL FLATTEN(input => pubs."cpc") AS c
    WHERE c.value:"code" LIKE 'A01B3%'

),

AssigneeApplications AS (
    SELECT 
        COUNT(*) AS year_country_cnt,
        a.value:"name" AS assignee_name,
        CAST(FLOOR(filing_date / 10000) AS INT) AS filing_year,
        apps.country_code as country_code
    FROM 
        PatentApplications as apps,
        LATERAL FLATTEN(input => assignee_harmonized) AS a
    GROUP BY 
        assignee_name, filing_year, country_code
),

RankedApplications AS (
    SELECT
        assignee_name,
        filing_year,
        country_code,
        year_country_cnt,
        SUM(year_country_cnt) OVER (PARTITION BY assignee_name, filing_year) AS total_cnt,
        ROW_NUMBER() OVER (PARTITION BY assignee_name, filing_year ORDER BY year_country_cnt DESC) AS rn
    FROM
        AssigneeApplications
),

AggregatedData AS (
    SELECT
        total_cnt AS year_cnt,
        assignee_name,
        filing_year,
        country_code
    FROM
        RankedApplications
    WHERE
        rn = 1
)


SELECT 
    total_count,
    REPLACE(assignee_name, '"', '') AS assignee_name,
    year_cnt,
    filing_year,
    country_code
FROM (
    SELECT 
        year_cnt,
        assignee_name,
        filing_year,
        country_code,
        SUM(year_cnt) OVER (PARTITION BY assignee_name) AS total_count,
        ROW_NUMBER() OVER (PARTITION BY assignee_name ORDER BY year_cnt DESC) AS rn
    FROM
        AggregatedData
    ORDER BY assignee_name
) sub
WHERE rn = 1
ORDER BY total_count
DESC
LIMIT 3
```

## sf_bq104.sql

```sql
WITH LatestWeek AS (
    SELECT
        DATEADD(WEEK, -52, MAX("week")) AS "last_year_week"
    FROM
        GOOGLE_TRENDS.GOOGLE_TRENDS.TOP_RISING_TERMS
),
LatestRefreshDate AS (
    SELECT
        MAX("refresh_date") AS "latest_refresh_date"
    FROM
        GOOGLE_TRENDS.GOOGLE_TRENDS.TOP_RISING_TERMS
),
RankedTerms AS (
    SELECT
        "term",
        "week",
        CASE WHEN "score" IS NULL THEN NULL ELSE "dma_name" END AS "dma_name",
        "rank",
        "score",
        ROW_NUMBER() OVER (
            PARTITION BY "term", "week"
            ORDER BY "score" DESC
        ) AS rn
    FROM
        GOOGLE_TRENDS.GOOGLE_TRENDS.TOP_RISING_TERMS
    WHERE
        "week" = (SELECT "last_year_week" FROM LatestWeek)
        AND "refresh_date" = (SELECT "latest_refresh_date" FROM LatestRefreshDate)
)

SELECT
    "term"
FROM
    RankedTerms
WHERE
    rn = 1
ORDER BY
    "rank"
LIMIT 1;

```

## sf_bq121.sql

```sql
WITH sub AS (
  SELECT 
    "users"."id",
    CAST(TO_TIMESTAMP(MAX("users"."creation_date") / 1000000.0) AS DATE) AS "user_creation_date",  -- 使用 MAX 聚合 creation_date 并转换为 DATE
    MAX("users"."reputation") AS "reputation",  
    SUM(CASE WHEN badges."user_id" IS NULL THEN 0 ELSE 1 END) AS "num_badges"
  FROM "STACKOVERFLOW"."STACKOVERFLOW"."USERS" "users"
  LEFT JOIN "STACKOVERFLOW"."STACKOVERFLOW"."BADGES" badges
    ON "users"."id" = badges."user_id"
  WHERE CAST(TO_TIMESTAMP("users"."creation_date" / 1000000.0) AS DATE) <= DATE '2021-10-01'
  GROUP BY "users"."id"
)

SELECT 
  DATEDIFF(YEAR, "user_creation_date", DATE '2021-10-01') AS "user_tenure",
  COUNT(1) AS "Num_Users",
  AVG("reputation") AS "Avg_Reputation",
  AVG("num_badges") AS "Avg_Num_Badges"
FROM sub
GROUP BY "user_tenure"
ORDER BY "user_tenure";

```

## sf_bq127.sql

```sql
WITH fam AS (
  SELECT DISTINCT
    "family_id"
  FROM
    "PATENTS_GOOGLE"."PATENTS_GOOGLE"."PUBLICATIONS"
),

crossover AS (
  SELECT
    "publication_number",
    "family_id"
  FROM
    "PATENTS_GOOGLE"."PATENTS_GOOGLE"."PUBLICATIONS"
),

pub AS (
  SELECT
    "family_id",
    MIN("publication_date") AS "publication_date",
    LISTAGG("publication_number", ',') WITHIN GROUP (ORDER BY "publication_number") AS "publication_number",
    LISTAGG("country_code", ',') WITHIN GROUP (ORDER BY "country_code") AS "country_code"
  FROM
    "PATENTS_GOOGLE"."PATENTS_GOOGLE"."PUBLICATIONS" AS p
  GROUP BY
    "family_id"
),

tech_class AS (
  SELECT
    p."family_id",
    LISTAGG(DISTINCT cpc.value:"code"::STRING, ',') WITHIN GROUP (ORDER BY cpc.value:"code"::STRING) AS "cpc",
    LISTAGG(DISTINCT ipc.value:"code"::STRING, ',') WITHIN GROUP (ORDER BY ipc.value:"code"::STRING) AS "ipc"
  FROM
    "PATENTS_GOOGLE"."PATENTS_GOOGLE"."PUBLICATIONS" AS p
    CROSS JOIN LATERAL FLATTEN(input => p."cpc") AS cpc
    CROSS JOIN LATERAL FLATTEN(input => p."ipc") AS ipc
  GROUP BY
    p."family_id"
),

cit AS (
  SELECT
    p."family_id",
    LISTAGG(crossover."family_id", ',') WITHIN GROUP (ORDER BY crossover."family_id" ASC) AS "citation"
  FROM
    "PATENTS_GOOGLE"."PATENTS_GOOGLE"."PUBLICATIONS" AS p
    CROSS JOIN LATERAL FLATTEN(input => p."citation") AS citation
    LEFT JOIN
      crossover
    ON
      citation.value:"publication_number"::STRING = crossover."publication_number"
  GROUP BY
    p."family_id"
),

tmp_gpr AS (
  SELECT
    "family_id",
    LISTAGG(crossover."publication_number", ',') AS "cited_by_publication_number"
  FROM
    "PATENTS_GOOGLE"."PATENTS_GOOGLE"."ABS_AND_EMB" AS p
    CROSS JOIN LATERAL FLATTEN(input => p."cited_by") AS cited_by
    LEFT JOIN
      crossover
    ON
      cited_by.value:"publication_number"::STRING = crossover."publication_number"
  GROUP BY
    "family_id"
),

gpr AS (
  SELECT
    tmp_gpr."family_id",
    LISTAGG(crossover."family_id", ',') WITHIN GROUP (ORDER BY crossover."family_id" ASC) AS "cited_by"
  FROM
    tmp_gpr
    CROSS JOIN LATERAL FLATTEN(input => SPLIT(tmp_gpr."cited_by_publication_number", ',')) AS cited_by_publication_number
    LEFT JOIN
      crossover
    ON
      cited_by_publication_number.value::STRING = crossover."publication_number"
  GROUP BY
    tmp_gpr."family_id"
)

SELECT
  fam."family_id",
  pub."publication_date",
  pub."publication_number",
  pub."country_code",
  tech_class."cpc",
  tech_class."ipc",
  cit."citation",
  gpr."cited_by"
FROM
  fam
  LEFT JOIN pub ON fam."family_id" = pub."family_id"
  LEFT JOIN tech_class ON fam."family_id" = tech_class."family_id"
  LEFT JOIN cit ON fam."family_id" = cit."family_id"
  LEFT JOIN gpr ON fam."family_id" = gpr."family_id"
WHERE
  pub."publication_date" BETWEEN 20150101 AND 20150131;

```

## sf_bq128.sql

```sql
SELECT
    patent."title",
    patent."abstract",
    app."date" AS publication_date,
    filterData."bkwdCitations",
    filterData."fwrdCitations_5"
FROM
    "PATENTSVIEW"."PATENTSVIEW"."PATENT" AS patent
JOIN
    "PATENTSVIEW"."PATENTSVIEW"."APPLICATION" AS app
    ON app."patent_id" = patent."id"
JOIN (
    SELECT
        DISTINCT cpc."patent_id",
        IFNULL(citation_5."bkwdCitations", 0) AS "bkwdCitations",
        IFNULL(citation_5."fwrdCitations_5", 0) AS "fwrdCitations_5"
    FROM
        "PATENTSVIEW"."PATENTSVIEW"."CPC_CURRENT" AS cpc
    LEFT JOIN (
        SELECT
            b."patent_id",
            b."bkwdCitations",
            f."fwrdCitations_5"
        FROM (
            SELECT 
                cited."citation_id" AS "patent_id",
                IFNULL(COUNT(*), 0) AS "fwrdCitations_5"
            FROM 
                "PATENTSVIEW"."PATENTSVIEW"."USPATENTCITATION" AS cited
            JOIN
                "PATENTSVIEW"."PATENTSVIEW"."APPLICATION" AS apps
                ON cited."citation_id" = apps."patent_id"
            WHERE
                apps."country" = 'US'
                AND cited."date" >= apps."date"
                AND TRY_CAST(cited."date" AS DATE) <= DATEADD(YEAR, 5, TRY_CAST(apps."date" AS DATE)) -- 5-year citation window
            GROUP BY 
                cited."citation_id"
        ) AS f
        JOIN (
            SELECT 
                cited."patent_id",
                IFNULL(COUNT(*), 0) AS "bkwdCitations"
            FROM 
                "PATENTSVIEW"."PATENTSVIEW"."USPATENTCITATION" AS cited
            JOIN
                "PATENTSVIEW"."PATENTSVIEW"."APPLICATION" AS apps
                ON cited."patent_id" = apps."patent_id"
            WHERE
                apps."country" = 'US'
                AND cited."date" < apps."date" -- backward citation count
            GROUP BY 
                cited."patent_id"
        ) AS b
        ON b."patent_id" = f."patent_id"
        WHERE
            b."bkwdCitations" IS NOT NULL
            AND f."fwrdCitations_5" IS NOT NULL
    ) AS citation_5 
    ON cpc."patent_id" = citation_5."patent_id"
    WHERE 
        cpc."subsection_id" IN ('C05', 'C06', 'C07', 'C08', 'C09', 'C10', 'C11', 'C12', 'C13')
        OR cpc."group_id" IN ('A01G', 'A01H', 'A61K', 'A61P', 'A61Q', 'B01F', 'B01J', 'B81B', 'B82B', 'B82Y', 'G01N', 'G16H')
) AS filterData
ON app."patent_id" = filterData."patent_id"
WHERE
    TRY_CAST(app."date" AS DATE) < '2014-02-01' 
    AND TRY_CAST(app."date" AS DATE) >= '2014-01-01';

```

## sf_bq150.sql

```sql
WITH
cohortExpr AS (
  SELECT
    "sample_barcode",
    LOG(10, "normalized_count") AS "expr"
  FROM
    "TCGA_HG19_DATA_V0"."TCGA_HG19_DATA_V0"."RNASEQ_GENE_EXPRESSION_UNC_RSEM"
  WHERE
    "project_short_name" = 'TCGA-BRCA'
    AND "HGNC_gene_symbol" = 'TP53'
    AND "normalized_count" IS NOT NULL
    AND "normalized_count" > 0
),
cohortVar AS (
  SELECT
    "Variant_Type",
    "sample_barcode_tumor" AS "sample_barcode"
  FROM
    "TCGA_HG19_DATA_V0"."TCGA_HG19_DATA_V0"."SOMATIC_MUTATION_MC3"
  WHERE
    "SYMBOL" = 'TP53'
),
cohort AS (
  SELECT
    e."sample_barcode" AS "sample_barcode",
    v."Variant_Type" AS "group_name",
    e."expr"
  FROM
    cohortExpr e
  JOIN
    cohortVar v
  ON
    e."sample_barcode" = v."sample_barcode"
),
grandMeanTable AS (
  SELECT
    AVG("expr") AS "grand_mean"
  FROM
    cohort
),
groupMeansTable AS (
  SELECT
    AVG("expr") AS "group_mean",
    "group_name",
    COUNT("sample_barcode") AS "n"
  FROM
    cohort
  GROUP BY
    "group_name"
),
ssBetween AS (
  SELECT
    g."group_name",
    g."group_mean",
    gm."grand_mean",
    g."n",
    g."n" * POW(g."group_mean" - gm."grand_mean", 2) AS "n_diff_sq"
  FROM
    groupMeansTable g
  CROSS JOIN
    grandMeanTable gm
),
ssWithin AS (
  SELECT
    c."group_name" AS "group_name",
    c."expr",
    b."group_mean",
    b."n" AS "n",
    POW(c."expr" - b."group_mean", 2) AS "s2"
  FROM
    cohort c
  JOIN
    ssBetween b
  ON
    c."group_name" = b."group_name"
),
numerator AS (
  SELECT
    SUM("n_diff_sq") / (COUNT("group_name") - 1) AS "mean_sq_between"
  FROM
    ssBetween
),
denominator AS (
  SELECT
    COUNT(DISTINCT "group_name") AS "k",
    COUNT("group_name") AS "n",
    SUM("s2") / (COUNT("group_name") - COUNT(DISTINCT "group_name")) AS "mean_sq_within"
  FROM
    ssWithin
)

SELECT
  "n",
  "k",
  "mean_sq_between",
  "mean_sq_within",
  "mean_sq_between" / "mean_sq_within" AS "F"
FROM
  numerator,
  denominator;

```

## sf_bq153.sql

```sql
WITH
    table1 AS (
        SELECT 
            "Symbol" AS "symbol", 
            AVG(LOG(10, "normalized_count" + 1)) AS "data", 
            "ParticipantBarcode"
        FROM 
            PANCANCER_ATLAS_1.PANCANCER_ATLAS_FILTERED.EBPP_ADJUSTPANCAN_ILLUMINAHISEQ_RNASEQV2_GENEXP_FILTERED
        WHERE 
            "Study" = 'LGG' 
            AND "Symbol" = 'IGF2' 
            AND "normalized_count" IS NOT NULL
        GROUP BY 
            "ParticipantBarcode", "symbol"
    ),
    table2 AS (
        SELECT
            "symbol",
            "avgdata" AS "data",
            "ParticipantBarcode"
        FROM (
            SELECT
                'icd_o_3_histology' AS "symbol", 
                "icd_o_3_histology" AS "avgdata",
                "bcr_patient_barcode" AS "ParticipantBarcode"
            FROM 
                PANCANCER_ATLAS_1.PANCANCER_ATLAS_FILTERED.CLINICAL_PANCAN_PATIENT_WITH_FOLLOWUP_FILTERED
            WHERE 
                "acronym" = 'LGG' 
                AND "icd_o_3_histology" IS NOT NULL  
                AND NOT REGEXP_LIKE("icd_o_3_histology", '^(\\[.*\\]$)')
        )
    ),
    table_data AS (
        SELECT 
            n1."data" AS "data1",
            n2."data" AS "data2",
            n1."ParticipantBarcode"
        FROM 
            table1 AS n1
        INNER JOIN 
            table2 AS n2
        ON 
            n1."ParticipantBarcode" = n2."ParticipantBarcode"
    ) 

SELECT 
    "data2" AS "Histology_Type", 
    AVG("data1") AS "Average_Log_Expression"
FROM 
    table_data
GROUP BY 
    "data2";

```

## sf_bq155.sql

```sql
WITH cohort AS (
    SELECT "case_barcode"
    FROM "TCGA_HG38_DATA_V0"."TCGA_BIOCLIN_V0"."CLINICAL"
    WHERE "project_short_name" = 'TCGA-BRCA'
        AND "age_at_diagnosis" <= 80
        AND "pathologic_stage" IN ('Stage I', 'Stage II', 'Stage IIA')
),
table1 AS (
    SELECT
        "symbol",
        "data" AS "rnkdata",
        "ParticipantBarcode"
    FROM (
        SELECT
            "gene_name" AS "symbol", 
            AVG(LOG(10, "HTSeq__Counts" + 1)) AS "data",
            "case_barcode" AS "ParticipantBarcode"
        FROM "TCGA_HG38_DATA_V0"."TCGA_HG38_DATA_V0"."RNASEQ_GENE_EXPRESSION"
        WHERE "case_barcode" IN (SELECT "case_barcode" FROM cohort)
            AND "gene_name" = 'SNORA31'
            AND "HTSeq__Counts" IS NOT NULL
        GROUP BY
            "ParticipantBarcode", "symbol"
    )
),
table2 AS (
    SELECT
        "symbol",
        "data" AS "rnkdata",
        "ParticipantBarcode"
    FROM (
        SELECT
            "mirna_id" AS "symbol", 
            AVG("reads_per_million_miRNA_mapped") AS "data",
            "case_barcode" AS "ParticipantBarcode"
        FROM "TCGA_HG38_DATA_V0"."TCGA_HG38_DATA_V0"."MIRNASEQ_EXPRESSION"
        WHERE "case_barcode" IN (SELECT "case_barcode" FROM cohort)
            AND "mirna_id" IS NOT NULL
            AND "reads_per_million_miRNA_mapped" IS NOT NULL
        GROUP BY
            "ParticipantBarcode", "symbol"
    )
),
summ_table AS (
    SELECT 
        n1."symbol" AS "symbol1",
        n2."symbol" AS "symbol2",
        COUNT(n1."ParticipantBarcode") AS "n",
        CORR(n1."rnkdata", n2."rnkdata") AS "correlation"
    FROM
        table1 AS n1
    INNER JOIN
        table2 AS n2
    ON
        n1."ParticipantBarcode" = n2."ParticipantBarcode"
    GROUP BY
        "symbol1", "symbol2"
)

SELECT 
    "symbol1", 
    "symbol2", 
    ABS("correlation") * SQRT(( "n" - 2 ) / (1 - "correlation" * "correlation")) AS "t"
FROM 
    summ_table
WHERE 
    "n" > 25 
    AND ABS("correlation") >= 0.3 
    AND ABS("correlation") < 1.0;

```

## sf_bq158.sql

```sql
WITH
    table1 AS (
        SELECT
            "histological_type" AS "data1",
            "bcr_patient_barcode" AS "ParticipantBarcode"
        FROM 
            "PANCANCER_ATLAS_1"."PANCANCER_ATLAS_FILTERED"."CLINICAL_PANCAN_PATIENT_WITH_FOLLOWUP_FILTERED"
        WHERE 
            "acronym" = 'BRCA' 
            AND "histological_type" IS NOT NULL      
    ),
    table2 AS (
        SELECT
            "Hugo_Symbol" AS "symbol", 
            "ParticipantBarcode"
        FROM 
            "PANCANCER_ATLAS_1"."PANCANCER_ATLAS_FILTERED"."MC3_MAF_V5_ONE_PER_TUMOR_SAMPLE"
        WHERE 
            "Study" = 'BRCA' 
            AND "Hugo_Symbol" = 'CDH1'
            AND "FILTER" = 'PASS'  
        GROUP BY
            "ParticipantBarcode", "symbol"
    ),
    summ_table AS (
        SELECT 
            n1."data1",
            CASE 
                WHEN n2."ParticipantBarcode" IS NULL THEN 'NO' 
                ELSE 'YES' 
            END AS "data2",
            COUNT(*) AS "Nij"
        FROM
            table1 AS n1
        LEFT JOIN
            table2 AS n2 
            ON n1."ParticipantBarcode" = n2."ParticipantBarcode"
        GROUP BY
            n1."data1", "data2"
    ),
    percentages AS (
        SELECT
            "data1",
            SUM(CASE WHEN "data2" = 'YES' THEN "Nij" ELSE 0 END) AS "mutation_count",
            SUM("Nij") AS "total",
            SUM(CASE WHEN "data2" = 'YES' THEN "Nij" ELSE 0 END) / SUM("Nij") AS "mutation_percentage"
        FROM 
            summ_table
        GROUP BY 
            "data1"
    )
SELECT 
    "data1" AS "Histological_Type"
FROM 
    percentages
ORDER BY 
    "mutation_percentage" DESC
LIMIT 5;

```

## sf_bq159.sql

```sql
WITH
    table1 AS (
        SELECT
            "symbol",
            "avgdata" AS "data",
            "ParticipantBarcode"
        FROM (
            SELECT
                'histological_type' AS "symbol", 
                "histological_type" AS "avgdata",
                "bcr_patient_barcode" AS "ParticipantBarcode"
            FROM 
                "PANCANCER_ATLAS_1"."PANCANCER_ATLAS_FILTERED"."CLINICAL_PANCAN_PATIENT_WITH_FOLLOWUP_FILTERED"
            WHERE 
                "acronym" = 'BRCA' 
                AND "histological_type" IS NOT NULL      
        )
    ),
    table2 AS (
        SELECT
            "symbol",
            "ParticipantBarcode"
        FROM (
            SELECT
                "Hugo_Symbol" AS "symbol", 
                "ParticipantBarcode" AS "ParticipantBarcode"
            FROM 
                "PANCANCER_ATLAS_1"."PANCANCER_ATLAS_FILTERED"."MC3_MAF_V5_ONE_PER_TUMOR_SAMPLE"
            WHERE 
                "Study" = 'BRCA' 
                AND "Hugo_Symbol" = 'CDH1'
                AND "FILTER" = 'PASS'  
            GROUP BY
                "ParticipantBarcode", "symbol"
        )
    ),
    summ_table AS (
        SELECT 
            n1."data" AS "data1",
            CASE 
                WHEN n2."ParticipantBarcode" IS NULL THEN 'NO' 
                ELSE 'YES' 
            END AS "data2",
            COUNT(*) AS "Nij"
        FROM
            table1 AS n1
        LEFT JOIN
            table2 AS n2 
            ON n1."ParticipantBarcode" = n2."ParticipantBarcode"
        GROUP BY
            n1."data", "data2"
    ),
    expected_table AS (
        SELECT 
            "data1", 
            "data2"
        FROM (     
            SELECT 
                "data1", 
                SUM("Nij") AS "Ni"   
            FROM 
                summ_table
            GROUP BY 
                "data1"
        ) AS Ni_table
        CROSS JOIN ( 
            SELECT 
                "data2", 
                SUM("Nij") AS "Nj"
            FROM 
                summ_table
            GROUP BY 
                "data2"
        ) AS Nj_table
        WHERE 
            Ni_table."Ni" > 10 
            AND Nj_table."Nj" > 10
    ),
    contingency_table AS (
        SELECT
            T1."data1",
            T1."data2",
            COALESCE(T2."Nij", 0) AS "Nij",
            (SUM(T2."Nij") OVER (PARTITION BY T1."data1")) * 
            (SUM(T2."Nij") OVER (PARTITION BY T1."data2")) / 
            SUM(T2."Nij") OVER () AS "E_nij"
        FROM
            expected_table AS T1
        LEFT JOIN
            summ_table AS T2
        ON 
            T1."data1" = T2."data1" 
            AND T1."data2" = T2."data2"
    )
SELECT
    SUM( ( "Nij" - "E_nij" ) * ( "Nij" - "E_nij" ) / "E_nij" ) AS "Chi2"
FROM 
    contingency_table;

```

## sf_bq166.sql

```sql
WITH copy AS (
  SELECT 
    "case_barcode", 
    "chromosome", 
    "start_pos", 
    "end_pos", 
    MAX("copy_number") AS "copy_number"
  FROM 
    "TCGA_MITELMAN"."TCGA_VERSIONED"."COPY_NUMBER_SEGMENT_ALLELIC_HG38_GDC_R23" 
  WHERE  
    "project_short_name" = 'TCGA-KIRC'
  GROUP BY 
    "case_barcode", 
    "chromosome", 
    "start_pos", 
    "end_pos"
),
total_cases AS (
  SELECT COUNT(DISTINCT "case_barcode") AS "total"
  FROM copy 
),
cytob AS (
  SELECT 
    "chromosome", 
    "cytoband_name", 
    "hg38_start", 
    "hg38_stop"
  FROM 
    "TCGA_MITELMAN"."PROD"."CYTOBANDS_HG38"
),
joined AS (
  SELECT 
    cytob."chromosome", 
    cytob."cytoband_name", 
    cytob."hg38_start", 
    cytob."hg38_stop",
    copy."case_barcode",
    copy."copy_number"  
  FROM 
    copy
  LEFT JOIN cytob
    ON cytob."chromosome" = copy."chromosome" 
  WHERE 
    (cytob."hg38_start" >= copy."start_pos" AND copy."end_pos" >= cytob."hg38_start")
    OR (copy."start_pos" >= cytob."hg38_start" AND copy."start_pos" <= cytob."hg38_stop")
),
cbands AS (
  SELECT 
    "chromosome", 
    "cytoband_name", 
    "hg38_start", 
    "hg38_stop", 
    "case_barcode",
    MAX("copy_number") AS "copy_number"
  FROM 
    joined
  GROUP BY 
    "chromosome", 
    "cytoband_name", 
    "hg38_start", 
    "hg38_stop", 
    "case_barcode"
),
aberrations AS (
  SELECT
    "chromosome",
    "cytoband_name",
    -- Amplifications: more than two copies for diploid > 4
    SUM( CASE WHEN "copy_number" > 3 THEN 1 ELSE 0 END ) AS "total_amp",
    -- Gains: at most two extra copies
    SUM( CASE WHEN "copy_number" = 3 THEN 1 ELSE 0 END ) AS "total_gain",
    -- Homozygous deletions, or complete deletions
    SUM( CASE WHEN "copy_number" = 0 THEN 1 ELSE 0 END ) AS "total_homodel",
    -- Heterozygous deletions, 1 copy lost
    SUM( CASE WHEN "copy_number" = 1 THEN 1 ELSE 0 END ) AS "total_heterodel",
    -- Normal for Diploid = 2
    SUM( CASE WHEN "copy_number" = 2 THEN 1 ELSE 0 END ) AS "total_normal"
  FROM 
    cbands
  GROUP BY 
    "chromosome", 
    "cytoband_name"
)
SELECT 
  aberrations."chromosome", 
  aberrations."cytoband_name",
  total_cases."total",  
  100 * aberrations."total_amp" / total_cases."total" AS "freq_amp", 
  100 * aberrations."total_gain" / total_cases."total" AS "freq_gain",
  100 * aberrations."total_homodel" / total_cases."total" AS "freq_homodel", 
  100 * aberrations."total_heterodel" / total_cases."total" AS "freq_heterodel", 
  100 * aberrations."total_normal" / total_cases."total" AS "freq_normal"  
FROM 
  aberrations, 
  total_cases
ORDER BY 
  aberrations."chromosome", 
  aberrations."cytoband_name";

```

## sf_bq167.sql

```sql
WITH UserPairUpvotes AS (
  SELECT
    ToUsers."UserName" AS "ToUserName",
    FromUsers."UserName" AS "FromUserName",
    COUNT(DISTINCT "ForumMessageVotes"."Id") AS "UpvoteCount"
  FROM META_KAGGLE.META_KAGGLE.FORUMMESSAGEVOTES AS "ForumMessageVotes"
  INNER JOIN META_KAGGLE.META_KAGGLE.USERS AS FromUsers
    ON FromUsers."Id" = "ForumMessageVotes"."FromUserId"
  INNER JOIN META_KAGGLE.META_KAGGLE.USERS AS ToUsers
    ON ToUsers."Id" = "ForumMessageVotes"."ToUserId"
  GROUP BY
    ToUsers."UserName",
    FromUsers."UserName"
),
TopPairs AS (
  SELECT
    "ToUserName",
    "FromUserName",
    "UpvoteCount",
    ROW_NUMBER() OVER (ORDER BY "UpvoteCount" DESC) AS "Rank"
  FROM UserPairUpvotes
),
ReciprocalUpvotes AS (
  SELECT
    t."ToUserName",
    t."FromUserName",
    t."UpvoteCount" AS "UpvotesReceived",
    COALESCE(u."UpvoteCount", 0) AS "UpvotesGiven"
  FROM TopPairs t
  LEFT JOIN UserPairUpvotes u
    ON t."ToUserName" = u."FromUserName" AND t."FromUserName" = u."ToUserName"
  WHERE t."Rank" = 1
)
SELECT
  "ToUserName" AS "UpvotedUserName",
  "FromUserName" AS "UpvotingUserName",
  "UpvotesReceived" AS "UpvotesReceivedByUpvotedUser",
  "UpvotesGiven" AS "UpvotesGivenByUpvotedUser"
FROM ReciprocalUpvotes
ORDER BY "UpvotesReceived" DESC, "UpvotesGiven" DESC;

```

## sf_bq176.sql

```sql
WITH copy AS (
  SELECT 
    "case_barcode", 
    "chromosome", 
    "start_pos", 
    "end_pos", 
    MAX("copy_number") AS "copy_number"
  FROM 
    "TCGA_MITELMAN"."TCGA_VERSIONED"."COPY_NUMBER_SEGMENT_ALLELIC_HG38_GDC_R23"
  WHERE 
    "project_short_name" = 'TCGA-LAML'
  GROUP BY 
    "case_barcode", 
    "chromosome", 
    "start_pos", 
    "end_pos"
),
total_cases AS (
  SELECT COUNT(DISTINCT "case_barcode") AS "total"
  FROM copy
),
cytob AS (
  SELECT 
    "chromosome", 
    "cytoband_name", 
    "hg38_start", 
    "hg38_stop"
  FROM 
    "TCGA_MITELMAN"."PROD"."CYTOBANDS_HG38"
),
joined AS (
  SELECT 
    cytob."chromosome", 
    cytob."cytoband_name", 
    cytob."hg38_start", 
    cytob."hg38_stop", 
    copy."case_barcode",
    (ABS(cytob."hg38_stop" - cytob."hg38_start") + ABS(copy."end_pos" - copy."start_pos") 
      - ABS(cytob."hg38_stop" - copy."end_pos") - ABS(cytob."hg38_start" - copy."start_pos")) / 2.0 AS "overlap", 
    copy."copy_number"
  FROM 
    copy
  LEFT JOIN 
    cytob
  ON 
    cytob."chromosome" = copy."chromosome"
  WHERE 
    (cytob."hg38_start" >= copy."start_pos" AND copy."end_pos" >= cytob."hg38_start")
    OR (copy."start_pos" >= cytob."hg38_start" AND copy."start_pos" <= cytob."hg38_stop")
),
INFO AS (
  SELECT 
    "chromosome", 
    "cytoband_name", 
    "hg38_start", 
    "hg38_stop", 
    "case_barcode",
    ROUND(SUM("overlap" * "copy_number") / SUM("overlap")) AS "copy_number"
  FROM 
    joined
  GROUP BY 
    "chromosome", "cytoband_name", "hg38_start", "hg38_stop", "case_barcode"
)

SELECT 
  "case_barcode"
FROM 
  INFO
WHERE 
  "chromosome" = 'chr15' 
  AND "cytoband_name" = '15q11'
ORDER BY 
  "copy_number" DESC
LIMIT 1;

```

## sf_bq182.sql

```sql
WITH
  event_data AS (
    SELECT
      "type",
      EXTRACT(YEAR FROM TO_TIMESTAMP("created_at" / 1000000)) AS "year",
      EXTRACT(QUARTER FROM TO_TIMESTAMP("created_at" / 1000000)) AS "quarter",
      REGEXP_REPLACE(
        "repo"::variant:"url"::string,
        'https:\\/\\/github\\.com\\/|https:\\/\\/api\\.github\\.com\\/repos\\/',
        ''
      ) AS "name"
    FROM GITHUB_REPOS_DATE.DAY._20230118
  ),

  repo_languages AS (
    SELECT
      "repo_name" AS "name",
      "lang"
    FROM (
      SELECT
        "repo_name",
        FIRST_VALUE("language") OVER (
          PARTITION BY "repo_name" ORDER BY "bytes" DESC
        ) AS "lang"
      FROM (
        SELECT
          "repo_name",
          "language".value:"name" AS "language",
          "language".value:"bytes" AS "bytes"
        FROM GITHUB_REPOS_DATE.GITHUB_REPOS.LANGUAGES,
        LATERAL FLATTEN(INPUT => "language") AS "language"
      )
    )
    WHERE "lang" IS NOT NULL
    GROUP BY "repo_name", "lang"
  ),

  joined_data AS (
    SELECT
      a."type" AS "type",
      b."lang" AS "language",
      a."year" AS "year",
      a."quarter" AS "quarter"
    FROM event_data a
    JOIN repo_languages b
      ON a."name" = b."name"
  ),

  count_data AS (
    SELECT
      "language",
      "year",
      "quarter",
      "type",
      COUNT(*) AS "count"
    FROM joined_data
    GROUP BY "type", "language", "year", "quarter"
    ORDER BY "year", "quarter", "count" DESC
  )

SELECT
  REPLACE("language", '"', '') AS "language_name",
  "count"
FROM count_data
WHERE "count" >= 5
  AND "type" = 'PullRequestEvent';

```

## sf_bq187.sql

```sql
WITH tokenInfo AS (
    SELECT "address"
    FROM "ETHEREUM_BLOCKCHAIN"."ETHEREUM_BLOCKCHAIN"."TOKENS"
    WHERE "name" = 'BNB'
),

receivedTx AS (
    SELECT "tx"."to_address" AS "addr", 
           "tokens"."name" AS "name", 
           SUM(CAST("tx"."value" AS FLOAT) / POWER(10, 18)) AS "amount_received"
    FROM "ETHEREUM_BLOCKCHAIN"."ETHEREUM_BLOCKCHAIN"."TOKEN_TRANSFERS" AS "tx"
    JOIN tokenInfo ON "tx"."token_address" = tokenInfo."address"
    JOIN "ETHEREUM_BLOCKCHAIN"."ETHEREUM_BLOCKCHAIN"."TOKENS" AS "tokens"
      ON "tx"."token_address" = "tokens"."address"
    WHERE "tx"."to_address" <> '0x0000000000000000000000000000000000000000'
    GROUP BY "tx"."to_address", "tokens"."name"
),

sentTx AS (
    SELECT "tx"."from_address" AS "addr", 
           "tokens"."name" AS "name", 
           SUM(CAST("tx"."value" AS FLOAT) / POWER(10, 18)) AS "amount_sent"
    FROM "ETHEREUM_BLOCKCHAIN"."ETHEREUM_BLOCKCHAIN"."TOKEN_TRANSFERS" AS "tx"
    JOIN tokenInfo ON "tx"."token_address" = tokenInfo."address"
    JOIN "ETHEREUM_BLOCKCHAIN"."ETHEREUM_BLOCKCHAIN"."TOKENS" AS "tokens"
      ON "tx"."token_address" = "tokens"."address"
    WHERE "tx"."from_address" <> '0x0000000000000000000000000000000000000000'
    GROUP BY "tx"."from_address", "tokens"."name"
),

walletBalances AS (
    SELECT r."addr",
           COALESCE(SUM(r."amount_received"), 0) - COALESCE(SUM(s."amount_sent"), 0) AS "balance"
    FROM receivedTx AS r
    LEFT JOIN sentTx AS s
      ON r."addr" = s."addr"
    GROUP BY r."addr"
)

SELECT 
    SUM("balance") AS "circulating_supply"
FROM walletBalances;

```

## sf_bq193.sql

```sql
WITH content_extracted AS (
    SELECT 
        "D"."id" AS "id",
        "repo_name",
        "path",
        SPLIT("content", '\n') AS "lines",
        "language_name"
    FROM 
        (
            SELECT 
                "id",
                "content"
            FROM 
                "GITHUB_REPOS"."GITHUB_REPOS"."SAMPLE_CONTENTS"
        ) AS "D"
    INNER JOIN 
        (
            SELECT 
                "id",
                "C"."repo_name" AS "repo_name",
                "path",
                "language_name"
            FROM 
                (
                    SELECT 
                        "id",
                        "repo_name",
                        "path"
                    FROM 
                        "GITHUB_REPOS"."GITHUB_REPOS"."SAMPLE_FILES"
                    WHERE 
                        LOWER("path") LIKE '%readme.md'
                ) AS "C"
            INNER JOIN 
                (
                    SELECT 
                        "repo_name",
                        "language_struct".value:"name" AS "language_name"
                    FROM 
                        (
                            SELECT 
                                "repo_name", 
                                "language"
                            FROM 
                                "GITHUB_REPOS"."GITHUB_REPOS"."LANGUAGES"
                        )
                    CROSS JOIN 
                        LATERAL FLATTEN(INPUT => "language") AS "language_struct"
                ) AS "F"
            ON 
                "C"."repo_name" = "F"."repo_name"
        ) AS "E"
    ON 
        "E"."id" = "D"."id"
),
non_empty_lines AS (
    SELECT 
        "line".value AS "line_",
        "language_name"
    FROM 
        content_extracted,
        LATERAL FLATTEN(INPUT => "lines") AS "line"
    WHERE 
        TRIM("line".value) != ''
        AND NOT STARTSWITH(TRIM("line".value), '#')
        AND NOT STARTSWITH(TRIM("line".value), '//')
),
aggregated_languages AS (
    SELECT 
        "line_",
        COUNT(*) AS "frequency",
        ARRAY_AGG("language_name") AS "languages"
    FROM 
        non_empty_lines
    GROUP BY 
        "line_"
)

SELECT 
    REGEXP_REPLACE("line_", '^"|"$', '') AS "line",
    "frequency",
    ARRAY_TO_STRING(ARRAY_SORT("languages"), ', ') AS "languages_sorted"
FROM 
    aggregated_languages
ORDER BY 
    "frequency" DESC;


```

## sf_bq209.sql

```sql
WITH patents_sample AS (
    SELECT
        t1."publication_number",
        t1."application_number"
    FROM
        PATENTS.PATENTS.PUBLICATIONS t1
    WHERE
        TO_DATE(
            CASE
                WHEN t1."grant_date" != 0 THEN TO_CHAR(t1."grant_date")
                ELSE NULL
            END, 
            'YYYYMMDD'
        ) BETWEEN TO_DATE('20100101', 'YYYYMMDD') AND TO_DATE('20101231', 'YYYYMMDD')
),
forward_citation AS (
    SELECT
        patents_sample."publication_number",
        COUNT(DISTINCT t3."citing_application_number") AS "forward_citations"
    FROM
        patents_sample
        LEFT JOIN (
            SELECT
                x2."publication_number",
                TO_DATE(
                    CASE
                        WHEN x2."filing_date" != 0 THEN TO_CHAR(x2."filing_date")
                        ELSE NULL
                    END,
                    'YYYYMMDD'
                ) AS "filing_date"
            FROM
                PATENTS.PATENTS.PUBLICATIONS x2
            WHERE
                x2."filing_date" != 0
        ) t2
            ON t2."publication_number" = patents_sample."publication_number"
        LEFT JOIN (
            SELECT
                x3."publication_number" AS "citing_publication_number",
                x3."application_number" AS "citing_application_number",
                TO_DATE(
                    CASE
                        WHEN x3."filing_date" != 0 THEN TO_CHAR(x3."filing_date")
                        ELSE NULL
                    END,
                    'YYYYMMDD'
                ) AS "joined_filing_date",
                cite.value:"publication_number"::STRING AS "cited_publication_number"
            FROM
                PATENTS.PATENTS.PUBLICATIONS x3,
                LATERAL FLATTEN(INPUT => x3."citation") cite
            WHERE
                x3."filing_date" != 0
        ) t3
            ON patents_sample."publication_number" = t3."cited_publication_number"
            AND t3."joined_filing_date" BETWEEN t2."filing_date" AND DATEADD(YEAR, 10, t2."filing_date")
    GROUP BY
        patents_sample."publication_number"
)

SELECT
    COUNT(*)
FROM
    forward_citation
WHERE
    "forward_citations" = 1;

```

## sf_bq210.sql

```sql
WITH patents_sample AS (
  SELECT 
    t1."publication_number" AS publication_number,
    claim.value:"text" AS claims_text
  FROM 
    PATENTS.PATENTS.PUBLICATIONS t1,
    LATERAL FLATTEN(input => t1."claims_localized") AS claim
  WHERE 
    t1."country_code" = 'US'
    AND t1."grant_date" BETWEEN 20080101 AND 20181231
    AND t1."grant_date" != 0
    AND t1."publication_number" LIKE '%B2%'
),
Publication_data AS (
  SELECT
    publication_number,
    COUNT_IF(claims_text NOT LIKE '%claim%') AS nb_indep_claims
  FROM
    patents_sample
  GROUP BY
    publication_number
)

SELECT COUNT(nb_indep_claims)
FROM Publication_data
WHERE nb_indep_claims != 0
```

## sf_bq213.sql

```sql
WITH interim_table as(
SELECT 
    t1."publication_number", 
    SUBSTR(ipc_u.value:"code", 0, 4) as ipc4
FROM 
    PATENTS.PATENTS.PUBLICATIONS t1,
    LATERAL FLATTEN(input => t1."ipc") AS ipc_u
WHERE
"country_code" = 'US'  
AND "grant_date" between 20220601 AND 20220831
  AND "grant_date" != 0
  AND "publication_number" LIKE '%B2%'  
GROUP BY 
    t1."publication_number", 
    ipc4
) 
SELECT 
ipc4
FROM 
interim_table 
GROUP BY ipc4
ORDER BY COUNT("publication_number") DESC
LIMIT 1
```

## sf_bq216.sql

```sql
WITH patents_sample AS (
    SELECT 
        "publication_number", 
        "application_number"
    FROM
        PATENTS_GOOGLE.PATENTS_GOOGLE.PUBLICATIONS
    WHERE
        "publication_number" = 'US-9741766-B2'
),
flattened_t5 AS (
    SELECT
        t5."publication_number",
        f.value AS element_value,
        f.index AS pos
    FROM
        PATENTS_GOOGLE.PATENTS_GOOGLE.ABS_AND_EMB t5,
        LATERAL FLATTEN(input => t5."embedding_v1") AS f
),
flattened_t6 AS (
    SELECT
        t6."publication_number",
        f.value AS element_value,
        f.index AS pos
    FROM
        PATENTS_GOOGLE.PATENTS_GOOGLE.ABS_AND_EMB t6,
        LATERAL FLATTEN(input => t6."embedding_v1") AS f
),
similarities AS (
    SELECT
        t1."publication_number" AS base_publication_number,
        t4."publication_number" AS similar_publication_number,
        SUM(ft5.element_value * ft6.element_value) AS similarity
    FROM
        (SELECT * FROM patents_sample LIMIT 1) t1
    LEFT JOIN (
        SELECT 
            x3."publication_number",
            EXTRACT(YEAR, TO_DATE(CAST(x3."filing_date" AS STRING), 'YYYYMMDD')) AS focal_filing_year
        FROM 
            PATENTS_GOOGLE.PATENTS_GOOGLE.PUBLICATIONS x3
        WHERE 
            x3."filing_date" != 0
    ) t3 ON t3."publication_number" = t1."publication_number"
    LEFT JOIN (
        SELECT 
            x4."publication_number",
            EXTRACT(YEAR, TO_DATE(CAST(x4."filing_date" AS STRING), 'YYYYMMDD')) AS filing_year
        FROM 
            PATENTS_GOOGLE.PATENTS_GOOGLE.PUBLICATIONS x4
        WHERE 
            x4."filing_date" != 0
    ) t4 ON
        t4."publication_number" != t1."publication_number"
        AND t3.focal_filing_year = t4.filing_year
    LEFT JOIN flattened_t5 AS ft5 ON ft5."publication_number" = t1."publication_number"
    LEFT JOIN flattened_t6 AS ft6 ON ft6."publication_number" = t4."publication_number"
    AND ft5.pos = ft6.pos  -- Align vector positions
    GROUP BY
        t1."publication_number", t4."publication_number"
)
SELECT
    s.similar_publication_number,
    s.similarity
FROM (
    SELECT
        s.*,
        ROW_NUMBER() OVER (PARTITION BY s.base_publication_number ORDER BY s.similarity DESC) AS seqnum
    FROM
        similarities s
) s
WHERE
    seqnum <= 5;

```

## sf_bq219.sql

```sql
WITH
MonthlyTotals AS
(
  SELECT
    TO_CHAR("date", 'YYYY-MM') AS "month",
    SUM("volume_sold_gallons") AS "total_monthly_volume"
  FROM
    IOWA_LIQUOR_SALES.IOWA_LIQUOR_SALES."SALES"
  WHERE
    "date" >= '2022-01-01' 
    AND TO_CHAR("date", 'YYYY-MM') < TO_CHAR(CURRENT_DATE(), 'YYYY-MM')
  GROUP BY
    TO_CHAR("date", 'YYYY-MM')
),

MonthCategory AS
(
  SELECT
    TO_CHAR("date", 'YYYY-MM') AS "month",
    "category",
    "category_name",
    SUM("volume_sold_gallons") AS "category_monthly_volume",
    CASE 
      WHEN "total_monthly_volume" != 0 THEN (SUM("volume_sold_gallons") / "total_monthly_volume") * 100
      ELSE NULL
    END AS "category_pct_of_month_volume"
  FROM
    IOWA_LIQUOR_SALES.IOWA_LIQUOR_SALES."SALES" AS Sales
  LEFT JOIN
    MonthlyTotals ON TO_CHAR(Sales."date", 'YYYY-MM') = MonthlyTotals."month"
  WHERE
    Sales."date" >= '2022-01-01' 
    AND TO_CHAR(Sales."date", 'YYYY-MM') < TO_CHAR(CURRENT_DATE(), 'YYYY-MM')
  GROUP BY
    TO_CHAR(Sales."date", 'YYYY-MM'), "category", "category_name", "total_monthly_volume"
),

middle_info AS 
(
  SELECT
    Category1."category" AS "category1",
    Category1."category_name" AS "category_name1",
    Category2."category" AS "category2",
    Category2."category_name" AS "category_name2",
    COUNT(DISTINCT Category1."month") AS "num_months",
    CORR(Category1."category_pct_of_month_volume", Category2."category_pct_of_month_volume") AS "category_corr_across_months",
    AVG(Category1."category_pct_of_month_volume") AS "category1_avg_pct_of_month_volume",
    AVG(Category2."category_pct_of_month_volume") AS "category2_avg_pct_of_month_volume"
  FROM
    MonthCategory Category1
  INNER JOIN
    MonthCategory Category2 
    ON Category1."month" = Category2."month"
  GROUP BY
    Category1."category", Category1."category_name", Category2."category", Category2."category_name"
  HAVING
    "num_months" >= 24
    AND "category1_avg_pct_of_month_volume" >= 1
    AND "category2_avg_pct_of_month_volume" >= 1
)

SELECT 
  "category_name1", 
  "category_name2"
FROM 
  middle_info
ORDER BY 
  "category_corr_across_months"
LIMIT 1;

```

## sf_bq221.sql

```sql
WITH patent_cpcs AS (
    SELECT
        cd."parents",
        CAST(FLOOR("filing_date" / 10000) AS INT) AS "filing_year"
    FROM (
        SELECT
            MAX("cpc") AS "cpc", MAX("filing_date") AS "filing_date"
        FROM
            PATENTS.PATENTS.PUBLICATIONS
        WHERE 
            "application_number" != ''
        GROUP BY
            "application_number"
    ) AS publications
    , LATERAL FLATTEN(INPUT => "cpc") AS cpcs
    JOIN
        PATENTS.PATENTS.CPC_DEFINITION cd ON cd."symbol" = cpcs.value:"code"
    WHERE 
        cpcs.value:"first" = TRUE
          AND "filing_date" > 0

),
yearly_counts AS (
    SELECT
        "cpc_group",
        "filing_year",
        COUNT(*) AS "cnt"
    FROM (
        SELECT
            cpc_parent.value::STRING AS "cpc_group",
            "filing_year"
        FROM patent_cpcs,
             LATERAL FLATTEN(input => patent_cpcs."parents") AS cpc_parent
    )
    GROUP BY "cpc_group", "filing_year"
),
ordered_counts AS (
    SELECT
        "cpc_group",
        "filing_year",
        "cnt",
        ROW_NUMBER() OVER (PARTITION BY "cpc_group" ORDER BY "filing_year" ASC) AS rn
    FROM yearly_counts
),
recursive_ema AS (
    -- Anchor member: first year per cpc_group
    SELECT
        "cpc_group",
        "filing_year",
        "cnt",
        "cnt" * 0.2 + 0 * 0.8 AS "ema",
        rn
    FROM ordered_counts
    WHERE rn = 1

    UNION ALL

    -- Recursive member: subsequent years
    SELECT
        oc."cpc_group",
        oc."filing_year",
        oc."cnt",
        oc."cnt" * 0.2 + re."ema" * 0.8 AS "ema",
        oc.rn
    FROM ordered_counts oc
    JOIN recursive_ema re
        ON oc."cpc_group" = re."cpc_group"
       AND oc.rn = re.rn + 1
),
max_ema AS (
    SELECT
        "cpc_group",
        "filing_year",
        "ema"
    FROM recursive_ema
),
ranked_ema AS (
    SELECT
        me."cpc_group",
        me."filing_year",
        me."ema",
        ROW_NUMBER() OVER (
            PARTITION BY me."cpc_group" 
            ORDER BY me."ema" DESC, me."filing_year" DESC
        ) AS rn_rank
    FROM max_ema me
)
SELECT 
    c."titleFull",
    REPLACE(r."cpc_group", '"', '') AS "cpc_group",
    r."filing_year" AS "best_filing_year"
FROM ranked_ema r
JOIN "PATENTS"."PATENTS"."CPC_DEFINITION" c 
    ON r."cpc_group" = c."symbol"
WHERE 
    c."level" = 5
    AND r.rn_rank = 1
ORDER BY 
    c."titleFull", 
    "cpc_group" ASC;

```

## sf_bq222.sql

```sql
WITH patent_cpcs AS (
    SELECT
        cd."parents",
        CAST(FLOOR("filing_date" / 10000) AS INT) AS "filing_year"
    FROM (
        SELECT MAX("cpc") AS "cpc", MAX("filing_date") AS "filing_date"
        FROM "PATENTS"."PATENTS"."PUBLICATIONS"
        WHERE "application_number" != ''
          AND "country_code" = 'DE'
          AND "grant_date" >= 20161201
          AND "grant_date" <= 20161231
        GROUP BY "application_number"
    ), LATERAL FLATTEN(INPUT => "cpc") AS cpcs
    JOIN "PATENTS"."PATENTS"."CPC_DEFINITION" cd ON cd."symbol" = cpcs.value:"code"
    WHERE cpcs.value:"first" = TRUE
      AND "filing_date" > 0
),
yearly_counts AS (
    SELECT
        "cpc_group",
        "filing_year",
        COUNT(*) AS "cnt"
    FROM (
        SELECT
            cpc_parent.VALUE AS "cpc_group",  -- Corrected reference to flattened "parents"
            "filing_year"
        FROM patent_cpcs,
             LATERAL FLATTEN(INPUT => "parents") AS cpc_parent  -- Corrected reference to flattened "parents"
    )
    GROUP BY "cpc_group", "filing_year"
),
moving_avg AS (
    SELECT
        "cpc_group",
        "filing_year",
        "cnt",
        AVG("cnt") OVER (PARTITION BY "cpc_group" ORDER BY "filing_year" ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS "moving_avg"
    FROM yearly_counts
)
SELECT 
    c."titleFull",  -- Ensure correct column name (check case)
    REPLACE("cpc_group", '"', '') AS "cpc_group",
    MAX("filing_year") AS "best_filing_year"
FROM moving_avg
JOIN "PATENTS"."PATENTS"."CPC_DEFINITION" c ON "cpc_group" = c."symbol"
WHERE c."level" = 4
GROUP BY c."titleFull", "cpc_group"
ORDER BY c."titleFull", "cpc_group" ASC;

```

## sf_bq223.sql

```sql
SELECT
    REPLACE(citing_assignee, '"', '') AS citing_assignee,
    cpcdef."titleFull" AS cpc_title,
    COUNT(*) AS number
FROM (
    SELECT
        pubs."publication_number" AS citing_publication_number,
        cite.value:"publication_number" AS cited_publication_number,
        citing_assignee_s.value:"name" AS citing_assignee,
        SUBSTR(cpcs.value:"code", 1, 4) AS citing_cpc_subclass
    FROM 
        PATENTS.PATENTS.PUBLICATIONS AS pubs
    , LATERAL FLATTEN(input => pubs."citation") AS cite
    , LATERAL FLATTEN(input => pubs."assignee_harmonized") AS citing_assignee_s
    , LATERAL FLATTEN(input => pubs."cpc") AS cpcs
    WHERE
        cpcs.value:"first" = TRUE
) AS pubs
JOIN (
    SELECT
        "publication_number" AS cited_publication_number,
        cited_assignee_s.value:"name" AS cited_assignee
    FROM
        PATENTS.PATENTS.PUBLICATIONS
    , LATERAL FLATTEN(input => "assignee_harmonized") AS cited_assignee_s
) AS refs
    ON pubs.cited_publication_number = refs.cited_publication_number
JOIN
    PATENTS.PATENTS.CPC_DEFINITION AS cpcdef
    ON cpcdef."symbol" = pubs.citing_cpc_subclass
WHERE
    refs.cited_assignee = 'DENSO CORP'
    AND pubs.citing_assignee != 'DENSO CORP'
GROUP BY
    citing_assignee, cpcdef."titleFull"

```

## sf_bq224.sql

```sql
WITH allowed_repos AS (
    SELECT 
        "repo_name",
        "license"
    FROM 
        GITHUB_REPOS_DATE.GITHUB_REPOS.LICENSES
    WHERE 
        "license" IN (
            'gpl-3.0', 'artistic-2.0', 'isc', 'cc0-1.0', 'epl-1.0', 'gpl-2.0',
            'mpl-2.0', 'lgpl-2.1', 'bsd-2-clause', 'apache-2.0', 'mit', 'lgpl-3.0'
        )
),
watch_counts AS (
    SELECT 
        TRY_PARSE_JSON("repo"):"name"::STRING AS "repo",
        COUNT(DISTINCT TRY_PARSE_JSON("actor"):"login"::STRING) AS "watches"
    FROM 
        GITHUB_REPOS_DATE.MONTH._202204
    WHERE 
        "type" = 'WatchEvent'
    GROUP BY 
        TRY_PARSE_JSON("repo"):"name"
),
issue_counts AS (
    SELECT 
        TRY_PARSE_JSON("repo"):"name"::STRING AS "repo",
        COUNT(*) AS "issue_events"
    FROM 
        GITHUB_REPOS_DATE.MONTH._202204
    WHERE 
        "type" = 'IssuesEvent'
    GROUP BY 
        TRY_PARSE_JSON("repo"):"name"
),
fork_counts AS (
    SELECT 
        TRY_PARSE_JSON("repo"):"name"::STRING AS "repo",
        COUNT(*) AS "forks"
    FROM 
        GITHUB_REPOS_DATE.MONTH._202204
    WHERE 
        "type" = 'ForkEvent'
    GROUP BY 
        TRY_PARSE_JSON("repo"):"name"
)
SELECT 
    ar."repo_name"
FROM 
    allowed_repos AS ar
INNER JOIN 
    fork_counts AS fc ON ar."repo_name" = fc."repo"
INNER JOIN 
    issue_counts AS ic ON ar."repo_name" = ic."repo"
INNER JOIN 
    watch_counts AS wc ON ar."repo_name" = wc."repo"
ORDER BY 
    (fc."forks" + ic."issue_events" + wc."watches") DESC
LIMIT 1;

```

## sf_bq233.sql

```sql
WITH extracted_modules AS (
SELECT 
    el."file_id" AS "file_id", 
    el."repo_name", 
    el."path" AS "path_", 
    REPLACE(line.value, '"', '') AS "line_",
    CASE
        WHEN ENDSWITH(el."path", '.py') THEN 'python'
        WHEN ENDSWITH(el."path", '.r') THEN 'r'
        ELSE NULL
    END AS "language",
    CASE
        WHEN ENDSWITH(el."path", '.py') THEN
            ARRAY_CAT(
                ARRAY_CONSTRUCT(REGEXP_SUBSTR(line.value, '\\bimport\\s+(\\w+)', 1, 1, 'e')),
                ARRAY_CONSTRUCT(REGEXP_SUBSTR(line.value, '\\bfrom\\s+(\\w+)', 1, 1, 'e'))
            )
        WHEN ENDSWITH(el."path", '.r') THEN
            ARRAY_CONSTRUCT(REGEXP_SUBSTR(line.value, 'library\\s*\\(\\s*([^\\s)]+)\\s*\\)', 1, 1, 'e'))
        ELSE ARRAY_CONSTRUCT()
    END AS "modules"
FROM (
    SELECT
        ct."id" AS "file_id", 
        fl."repo_name" AS "repo_name", 
        fl."path", 
        SPLIT(REPLACE(ct."content", '\n', ' \n'), '\n') AS "lines"
    FROM 
        GITHUB_REPOS_DATE.GITHUB_REPOS.SAMPLE_FILES AS fl
    JOIN 
        GITHUB_REPOS_DATE.GITHUB_REPOS.SAMPLE_CONTENTS AS ct 
        ON fl."id" = ct."id"
) AS el,
LATERAL FLATTEN(input => el."lines") AS line 
WHERE
    (
        ENDSWITH("path_", '.py') 
        AND 
        (
            "line_" LIKE 'import %' 
            OR 
            "line_" LIKE 'from %'
        )
    )
    OR
    (
        ENDSWITH("path_", '.r') 
        AND 
        "line_" LIKE 'library%('
    )

),
module_counts AS (
    SELECT 
        em."language",
        f.value::STRING AS "module",
        COUNT(*) AS "occurrence_count"
    FROM 
        extracted_modules AS em,
        LATERAL FLATTEN(input => em."modules") AS f
    WHERE 
        em."modules" IS NOT NULL
        AND f.value IS NOT NULL
    GROUP BY 
        em."language", 
        f.value
),
python AS (
    SELECT 
        "language",
        "module",
        "occurrence_count"
    FROM 
        module_counts
    WHERE 
        "language" = 'python'
),
rlanguage AS (
    SELECT 
        "language",
        "module",
        "occurrence_count"
    FROM 
        module_counts AS mc_inner
    WHERE 
        "language" = 'r'
)
SELECT 
    *
FROM 
    python
UNION ALL
SELECT 
    *
FROM 
    rlanguage
ORDER BY 
    "language", 
    "occurrence_count" DESC;

```

## sf_bq236.sql

```sql
SELECT
  CONCAT("city", ', ', "state_name") AS "city",
  "zip_code",
  COUNT("event_id") AS "count_storms"
FROM (
    SELECT *
    FROM NOAA_DATA_PLUS.NOAA_HISTORIC_SEVERE_STORMS.STORMS_2014
    UNION ALL
    SELECT *
    FROM NOAA_DATA_PLUS.NOAA_HISTORIC_SEVERE_STORMS.STORMS_2015
    UNION ALL
    SELECT *
    FROM NOAA_DATA_PLUS.NOAA_HISTORIC_SEVERE_STORMS.STORMS_2016
    UNION ALL
    SELECT *
    FROM NOAA_DATA_PLUS.NOAA_HISTORIC_SEVERE_STORMS.STORMS_2017
    UNION ALL
    SELECT *
    FROM NOAA_DATA_PLUS.NOAA_HISTORIC_SEVERE_STORMS.STORMS_2018
    UNION ALL
    SELECT *
    FROM NOAA_DATA_PLUS.NOAA_HISTORIC_SEVERE_STORMS.STORMS_2019
    UNION ALL
    SELECT *
    FROM NOAA_DATA_PLUS.NOAA_HISTORIC_SEVERE_STORMS.STORMS_2020
    UNION ALL
    SELECT *
    FROM NOAA_DATA_PLUS.NOAA_HISTORIC_SEVERE_STORMS.STORMS_2021
    UNION ALL
    SELECT *
    FROM NOAA_DATA_PLUS.NOAA_HISTORIC_SEVERE_STORMS.STORMS_2022
    UNION ALL
    SELECT *
    FROM NOAA_DATA_PLUS.NOAA_HISTORIC_SEVERE_STORMS.STORMS_2023
    UNION ALL
    SELECT *
    FROM NOAA_DATA_PLUS.NOAA_HISTORIC_SEVERE_STORMS.STORMS_2024
) AS storms
JOIN NOAA_DATA_PLUS.GEO_US_BOUNDARIES.ZIP_CODES
  ON ST_WITHIN(ST_GEOGFROMWKB(storms."event_point"), ST_GEOGFROMWKB("zip_code_geom"))
WHERE
   LOWER(storms."event_type") = 'hail'
GROUP BY
  "zip_code", 
  "city", 
  "state_name"
ORDER BY
  "count_storms" DESC
LIMIT 5;

```

## sf_bq246.sql

```sql
SELECT filterData."fwrdCitations_3"
FROM
  PATENTSVIEW.PATENTSVIEW.APPLICATION AS app
JOIN (
  SELECT DISTINCT 
    cpc."patent_id", 
    IFNULL(citation_3."bkwdCitations_3", 0) AS "bkwdCitations_3", 
    IFNULL(citation_3."fwrdCitations_3", 0) AS "fwrdCitations_3"
  FROM
    PATENTSVIEW.PATENTSVIEW.CPC_CURRENT AS cpc
  LEFT JOIN (
    SELECT 
      b."patent_id", 
      b."bkwdCitations_3", 
      f."fwrdCitations_3"
    FROM 
      (SELECT 
         cited."patent_id",
         COUNT(*) AS "fwrdCitations_3"
       FROM 
         PATENTSVIEW.PATENTSVIEW.USPATENTCITATION AS cited
       JOIN
         PATENTSVIEW.PATENTSVIEW.APPLICATION AS apps
         ON cited."patent_id" = apps."patent_id"
       WHERE
         apps."country" = 'US'
         AND cited."date" >= apps."date"
         AND TRY_CAST(cited."date" AS DATE) <= DATEADD(YEAR, 1, TRY_CAST(apps."date" AS DATE)) -- Citation within 1 year
       GROUP BY 
         cited."patent_id"
      ) AS f
    JOIN (
      SELECT 
        cited."patent_id",
        COUNT(*) AS "bkwdCitations_3"
      FROM 
        PATENTSVIEW.PATENTSVIEW.USPATENTCITATION AS cited
      JOIN
        PATENTSVIEW.PATENTSVIEW.APPLICATION AS apps
        ON cited."patent_id" = apps."patent_id"
      WHERE
        apps."country" = 'US'
        AND cited."date" < apps."date"
        AND TRY_CAST(cited."date" AS DATE) >= DATEADD(YEAR, -1, TRY_CAST(apps."date" AS DATE)) -- Citation within 1 year before
      GROUP BY 
        cited."patent_id"
    ) AS b
    ON b."patent_id" = f."patent_id"
    WHERE 
      b."bkwdCitations_3" IS NOT NULL
      AND f."fwrdCitations_3" IS NOT NULL
  ) AS citation_3 
  ON cpc."patent_id" = citation_3."patent_id"
) AS filterData
ON app."patent_id" = filterData."patent_id"
ORDER BY filterData."bkwdCitations_3" DESC
LIMIT 1;

```

## sf_bq248.sql

```sql
WITH requests AS (
    SELECT 
        D."id",
        D."content",
        E."repo_name",
        E."path"
    FROM 
        (
            SELECT 
                "id",
                "content"
            FROM 
                GITHUB_REPOS.GITHUB_REPOS.SAMPLE_CONTENTS
            GROUP BY 
                "id", "content"
        ) AS D
    INNER JOIN 
        (
            SELECT 
                C."id",
                C."repo_name",
                C."path"
            FROM 
                (
                    SELECT 
                        "id",
                        "repo_name",
                        "path"
                    FROM 
                        GITHUB_REPOS.GITHUB_REPOS.SAMPLE_FILES
                    WHERE 
                        LOWER("path") LIKE '%readme.md'
                    GROUP BY 
                        "path", "id", "repo_name"
                ) AS C
            INNER JOIN 
                (
                    SELECT 
                        "repo_name",
                        language_struct.value:"name"::STRING AS "language_name"
                    FROM 
                        GITHUB_REPOS.GITHUB_REPOS.LANGUAGES,
                        LATERAL FLATTEN(input => "language") AS language_struct
                    WHERE 
                        LOWER(language_struct.value:"name"::STRING) NOT LIKE '%python%'
                    GROUP BY 
                        "language_name", "repo_name"
                ) AS F
            ON 
                C."repo_name" = F."repo_name"
        ) AS E
    ON 
        D."id" = E."id"
)
SELECT 
    (SELECT COUNT(*) FROM requests WHERE "content" LIKE '%Copyright (c)%') / COUNT(*) AS "proportion"
FROM 
    requests;

```

## sf_bq250.sql

```sql
WITH country_name AS (
  SELECT 'Singapore' AS value
),

last_updated AS (
  SELECT
    MAX("last_updated") AS value
  FROM GEO_OPENSTREETMAP_WORLDPOP.WORLDPOP.POPULATION_GRID_1KM AS pop
    INNER JOIN country_name ON (pop."country_name" = country_name.value)
  WHERE "last_updated" < '2023-01-01'
),

aggregated_population AS (
  SELECT
    "geo_id",
    SUM("population") AS sum_population,
    ST_POINT("longitude_centroid", "latitude_centroid") AS centr  -- 计算每个 geo_id 的中心点
  FROM
    GEO_OPENSTREETMAP_WORLDPOP.WORLDPOP.POPULATION_GRID_1KM AS pop
    INNER JOIN country_name ON (pop."country_name" = country_name.value)
    INNER JOIN last_updated ON (pop."last_updated" = last_updated.value)
  GROUP BY "geo_id", "longitude_centroid", "latitude_centroid"
),

population AS (
  SELECT
    SUM(sum_population) AS sum_population,
    ST_ENVELOPE(ST_UNION_AGG(centr)) AS boundingbox  -- 使用 ST_ENVELOPE 来代替 ST_CONVEXHULL
  FROM aggregated_population
),

hospitals AS (
  SELECT
    layer."geometry"
  FROM
    GEO_OPENSTREETMAP_WORLDPOP.GEO_OPENSTREETMAP.PLANET_LAYERS AS layer
    INNER JOIN population ON ST_INTERSECTS(population.boundingbox, ST_GEOGFROMWKB(layer."geometry"))
  WHERE
    layer."layer_code" IN (2110, 2120)
),

distances AS (
  SELECT
    pop."geo_id",
    pop."population",
    MIN(ST_DISTANCE(ST_GEOGFROMWKB(pop."geog"), ST_GEOGFROMWKB(hospitals."geometry"))) AS distance
  FROM
    GEO_OPENSTREETMAP_WORLDPOP.WORLDPOP.POPULATION_GRID_1KM AS pop
    INNER JOIN country_name ON pop."country_name" = country_name.value
    INNER JOIN last_updated ON pop."last_updated" = last_updated.value
    CROSS JOIN hospitals
  WHERE pop."population" > 0
  GROUP BY "geo_id", "population"
)

SELECT
  SUM(pd."population") AS population
FROM
  distances pd
CROSS JOIN population p
GROUP BY distance
ORDER BY distance DESC
LIMIT 1;

```

## sf_bq252.sql

```sql
WITH selected_repos AS (
  SELECT
    f."id",
    f."repo_name" AS "repo_name",
    f."path" AS "path"
  FROM
    GITHUB_REPOS.GITHUB_REPOS.SAMPLE_FILES AS f
),
deduped_files AS (
  SELECT
    f."id",
    MIN(f."repo_name") AS "repo_name",
    MIN(f."path") AS "path"
  FROM
    selected_repos AS f
  GROUP BY
    f."id"
)
SELECT
  f."repo_name"
FROM
  deduped_files AS f
  JOIN GITHUB_REPOS.GITHUB_REPOS.SAMPLE_CONTENTS AS c 
  ON f."id" = c."id"
WHERE
  NOT c."binary"
  AND f."path" LIKE '%.swift'
ORDER BY c."copies" DESC
LIMIT 1;

```

## sf_bq254.sql

```sql
WITH bounding_area AS (
    SELECT "geometry" AS geometry
    FROM GEO_OPENSTREETMAP.GEO_OPENSTREETMAP.PLANET_FEATURES,
    LATERAL FLATTEN(INPUT => "all_tags") AS tag
    WHERE "feature_type" = 'multipolygons'
      AND tag.value:"key" = 'wikidata'
      AND tag.value:"value" = 'Q191'
),
bounding_area_features AS (
    SELECT 
        planet_features."osm_id", 
        planet_features."feature_type", 
        planet_features."geometry", 
        planet_features."all_tags"
    FROM GEO_OPENSTREETMAP.GEO_OPENSTREETMAP.PLANET_FEATURES AS planet_features,
         bounding_area
    WHERE ST_DWITHIN(
        ST_GEOGFROMWKB(planet_features."geometry"), 
        ST_GEOGFROMWKB(bounding_area.geometry), 
        0.0
    )
),
osm_id_with_wikidata AS (
    SELECT DISTINCT
        baf."osm_id"
    FROM bounding_area_features AS baf,
         LATERAL FLATTEN(INPUT => baf."all_tags") AS tag
    WHERE tag.value:"key" = 'wikidata'
),

polygons_wo_wikidata AS (
    SELECT 
        baf."osm_id",
        tag.value:"value" as name,
        baf."geometry" as geometry
    FROM bounding_area_features AS baf
    LEFT JOIN osm_id_with_wikidata AS wd
      ON baf."osm_id" = wd."osm_id",
    LATERAL FLATTEN(INPUT => "all_tags") AS tag
    WHERE wd."osm_id" IS NULL
    AND baf."osm_id" IS NOT NULL
    AND baf."feature_type" = 'multipolygons'
    AND tag.value:"key" = 'name'
)

SELECT 
    TRIM(pww.name) as name
FROM bounding_area_features AS baf
JOIN polygons_wo_wikidata AS pww
    ON ST_DWITHIN(
        ST_GEOGFROMWKB(baf."geometry"), 
        ST_GEOGFROMWKB(pww.geometry), 
        0.0
    )
LEFT JOIN osm_id_with_wikidata AS wd
    ON baf."osm_id" = wd."osm_id"
WHERE wd."osm_id" IS NOT NULL
  AND baf."feature_type" = 'points'
GROUP BY pww.name
ORDER BY COUNT(baf."osm_id") DESC
LIMIT 2




```

## sf_bq255.sql

```sql
SELECT
  COUNT(commits_table."message") AS "num_messages"
FROM (
  SELECT
    L."repo_name",
    language_struct.value:"name"::STRING AS "language_name"
  FROM
    GITHUB_REPOS.GITHUB_REPOS.LANGUAGES AS L,
    LATERAL FLATTEN(input => L."language") AS language_struct
) AS lang_table
JOIN 
  GITHUB_REPOS.GITHUB_REPOS.LICENSES AS license_table
ON 
  license_table."repo_name" = lang_table."repo_name"
JOIN (
  SELECT
    *
  FROM
    GITHUB_REPOS.GITHUB_REPOS.SAMPLE_COMMITS
) AS commits_table
ON 
  commits_table."repo_name" = lang_table."repo_name"
WHERE
  license_table."license" LIKE 'apache-2.0'
  AND lang_table."language_name" LIKE 'Shell'
  AND LENGTH(commits_table."message") > 5
  AND LENGTH(commits_table."message") < 10000
  AND LOWER(commits_table."message") NOT LIKE 'update%'
  AND LOWER(commits_table."message") NOT LIKE 'test%'
  AND LOWER(commits_table."message") NOT LIKE 'merge%';

```

## sf_bq260.sql

```sql
WITH filtered_users AS (
    SELECT 
        "first_name", 
        "last_name", 
        "gender", 
        "age",
        CAST(TO_TIMESTAMP("created_at" / 1000000.0) AS DATE) AS "created_at"
    FROM 
        "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."USERS"
    WHERE 
        CAST(TO_TIMESTAMP("created_at" / 1000000.0) AS DATE) BETWEEN '2019-01-01' AND '2022-04-30'
),
youngest_ages AS (
    SELECT 
        "gender", 
        MIN("age") AS "age"
    FROM 
        filtered_users
    GROUP BY 
        "gender"
),
oldest_ages AS (
    SELECT 
        "gender", 
        MAX("age") AS "age"
    FROM 
        filtered_users
    GROUP BY 
        "gender"
),
youngest_oldest AS (
    SELECT 
        u."first_name", 
        u."last_name", 
        u."gender", 
        u."age", 
        'youngest' AS "tag"
    FROM 
        filtered_users u
    JOIN 
        youngest_ages y
    ON 
        u."gender" = y."gender" AND u."age" = y."age"
    
    UNION ALL
    
    SELECT 
        u."first_name", 
        u."last_name", 
        u."gender", 
        u."age", 
        'oldest' AS "tag"
    FROM 
        filtered_users u
    JOIN 
        oldest_ages o
    ON 
        u."gender" = o."gender" AND u."age" = o."age"
)
SELECT 
    "tag", 
    "gender", 
    COUNT(*) AS "num"
FROM 
    youngest_oldest
GROUP BY 
    "tag", "gender"
ORDER BY 
    "tag", "gender";

```

## sf_bq263.sql

```sql
WITH d AS (
    SELECT
        a."order_id", 
        TO_CHAR(TO_TIMESTAMP(a."created_at" / 1000000.0), 'YYYY-MM') AS "month",  -- 格式化为年月
        TO_CHAR(TO_TIMESTAMP(a."created_at" / 1000000.0), 'YYYY') AS "year",  -- 格式化为年份
        b."product_id", b."sale_price", c."category", c."cost"
    FROM 
        "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."ORDERS" AS a
    JOIN 
        "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."ORDER_ITEMS" AS b
        ON a."order_id" = b."order_id"
    JOIN 
        "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."PRODUCTS" AS c
        ON b."product_id" = c."id"
    WHERE 
        a."status" = 'Complete'
        AND TO_TIMESTAMP(a."created_at" / 1000000.0) BETWEEN TO_TIMESTAMP('2023-01-01') AND TO_TIMESTAMP('2023-12-31')
        AND c."category" = 'Sleep & Lounge'
),

e AS (
    SELECT 
        "month", 
        "year", 
        "sale_price", 
        "category", 
        "cost",
        SUM("sale_price") OVER (PARTITION BY "month", "category") AS "TPV",
        SUM("cost") OVER (PARTITION BY "month", "category") AS "total_cost",
        COUNT(DISTINCT "order_id") OVER (PARTITION BY "month", "category") AS "TPO",
        SUM("sale_price" - "cost") OVER (PARTITION BY "month", "category") AS "total_profit",
        SUM(("sale_price" - "cost") / "cost") OVER (PARTITION BY "month", "category") AS "Profit_to_cost_ratio"
    FROM 
        d
)

SELECT DISTINCT 
    "month", 
    "category", 
    "TPV", 
    "total_cost", 
    "TPO", 
    "total_profit", 
    "Profit_to_cost_ratio"
FROM 
    e
ORDER BY 
    "month";

```

## sf_bq264.sql

```sql
WITH youngest AS (
    SELECT
        "gender", 
        "id", 
        "first_name", 
        "last_name", 
        "age", 
        'youngest' AS "tag"
    FROM 
        "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."USERS"
    WHERE 
        "age" = (SELECT MIN("age") FROM "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."USERS")
        AND TO_TIMESTAMP("created_at" / 1000000.0) BETWEEN TO_TIMESTAMP('2019-01-01') AND TO_TIMESTAMP('2022-04-30')
    GROUP BY 
        "gender", "id", "first_name", "last_name", "age"
    ORDER BY 
        "gender"
),

oldest AS (
    SELECT
        "gender", 
        "id", 
        "first_name", 
        "last_name", 
        "age", 
        'oldest' AS "tag"
    FROM 
        "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."USERS"
    WHERE 
        "age" = (SELECT MAX("age") FROM "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."USERS")
        AND TO_TIMESTAMP("created_at" / 1000000.0) BETWEEN TO_TIMESTAMP('2019-01-01') AND TO_TIMESTAMP('2022-04-30')
    GROUP BY 
        "gender", "id", "first_name", "last_name", "age"
    ORDER BY 
        "gender"
),

TEMP_record AS (
    SELECT * FROM youngest
    UNION ALL
    SELECT * FROM oldest
)

SELECT 
    SUM(CASE WHEN "age" = (SELECT MAX("age") FROM "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."USERS") THEN 1 END) - 
    SUM(CASE WHEN "age" = (SELECT MIN("age") FROM "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."USERS") THEN 1 END) AS "diff"
FROM 
    TEMP_record;

```

## sf_bq265.sql

```sql
WITH
  main AS (
    SELECT
      "id" AS "user_id",
      "email",
      "gender",
      "country",
      "traffic_source"
    FROM
      "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."USERS"
    WHERE
      TO_TIMESTAMP("created_at" / 1000000.0) BETWEEN TO_TIMESTAMP('2019-01-01') AND TO_TIMESTAMP('2019-12-31')
  ),

  daate AS (
    SELECT
      "user_id",
      "order_id",
      CAST(TO_TIMESTAMP("created_at" / 1000000.0) AS DATE) AS "order_date",
      "num_of_item"
    FROM
      "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."ORDERS"
    WHERE
      TO_TIMESTAMP("created_at" / 1000000.0) BETWEEN TO_TIMESTAMP('2019-01-01') AND TO_TIMESTAMP('2019-12-31')
  ),

  orders AS (
    SELECT
      "user_id",
      "order_id",
      "product_id",
      "sale_price",
      "status"
    FROM
      "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."ORDER_ITEMS"
    WHERE
      TO_TIMESTAMP("created_at" / 1000000.0) BETWEEN TO_TIMESTAMP('2019-01-01') AND TO_TIMESTAMP('2019-12-31')
  ),

  nest AS (
    SELECT
      o."user_id",
      o."order_id",
      o."product_id",
      d."order_date",
      d."num_of_item",
      ROUND(o."sale_price", 2) AS "sale_price",
      ROUND(d."num_of_item" * o."sale_price", 2) AS "total_sale"
    FROM
      orders o
    INNER JOIN
      daate d
    ON
      o."order_id" = d."order_id"
    ORDER BY
      o."user_id"
  ),

  type AS (
    SELECT
      "user_id",
      MIN(nest."order_date") AS "cohort_date",
      MAX(nest."order_date") AS "latest_shopping_date",
      DATEDIFF(MONTH, MIN(nest."order_date"), MAX(nest."order_date")) AS "lifespan_months",
      ROUND(SUM("total_sale"), 2) AS "ltv",
      COUNT("order_id") AS "no_of_order"
    FROM
      nest
    GROUP BY
      "user_id"
  ),

  kite AS (
    SELECT
      m."user_id",
      m."email",
      m."gender",
      m."country",
      m."traffic_source",
      EXTRACT(YEAR FROM n."cohort_date") AS "cohort_year",
      n."latest_shopping_date",
      n."lifespan_months",
      n."ltv",
      n."no_of_order",
      ROUND(n."ltv" / n."no_of_order", 2) AS "avg_order_value"
    FROM
      main m
    INNER JOIN
      type n
    ON
      m."user_id" = n."user_id"
  )

SELECT
  "email"
FROM
  kite
ORDER BY
  "avg_order_value" DESC
LIMIT 10;

```

## sf_bq271.sql

```sql
WITH
orders_x_order_items AS (
  SELECT orders.*,
         order_items."inventory_item_id",
         order_items."sale_price"
  FROM "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."ORDERS" AS orders
  LEFT JOIN "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."ORDER_ITEMS" AS order_items
  ON orders."order_id" = order_items."order_id"
  WHERE TO_TIMESTAMP_NTZ(orders."created_at" / 1000000) BETWEEN TO_TIMESTAMP_NTZ('2021-01-01') AND TO_TIMESTAMP_NTZ('2021-12-31')
),

orders_x_inventory AS (
  SELECT orders_x_order_items.*,
         inventory_items."product_category",
         inventory_items."product_department",
         inventory_items."product_retail_price",
         inventory_items."product_distribution_center_id",
         inventory_items."cost",
         distribution_centers."name"
  FROM orders_x_order_items
  LEFT JOIN "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."INVENTORY_ITEMS" AS inventory_items
  ON orders_x_order_items."inventory_item_id" = inventory_items."id"
  LEFT JOIN "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."DISTRIBUTION_CENTERS" AS distribution_centers
  ON inventory_items."product_distribution_center_id" = distribution_centers."id"
  WHERE TO_TIMESTAMP_NTZ(inventory_items."created_at" / 1000000) BETWEEN TO_TIMESTAMP_NTZ('2021-01-01') AND TO_TIMESTAMP_NTZ('2021-12-31')
),

orders_x_users AS (
  SELECT orders_x_inventory.*,
         users."country" AS "users_country"
  FROM orders_x_inventory
  LEFT JOIN "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."USERS" AS users
  ON orders_x_inventory."user_id" = users."id"
  WHERE TO_TIMESTAMP_NTZ(users."created_at" / 1000000) BETWEEN TO_TIMESTAMP_NTZ('2021-01-01') AND TO_TIMESTAMP_NTZ('2021-12-31')
)

SELECT 
  DATE_TRUNC('MONTH', TO_DATE(TO_TIMESTAMP_NTZ(orders_x_users."created_at" / 1000000))) AS "reporting_month",
  orders_x_users."users_country",
  orders_x_users."product_department",
  orders_x_users."product_category",
  COUNT(DISTINCT orders_x_users."order_id") AS "n_order",
  COUNT(DISTINCT orders_x_users."user_id") AS "n_purchasers",
  SUM(orders_x_users."product_retail_price") - SUM(orders_x_users."cost") AS "profit"
FROM orders_x_users
GROUP BY 1, 2, 3, 4
ORDER BY "reporting_month";

```

## sf_bq273.sql

```sql
WITH 
orders AS (
  SELECT
    "order_id", 
    "user_id", 
    "created_at",
    DATE_TRUNC('MONTH', TO_TIMESTAMP_NTZ("delivered_at" / 1000000)) AS "delivery_month",  -- Converting to timestamp
    "status" 
  FROM "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."ORDERS"
),

order_items AS (
  SELECT 
    "order_id", 
    "product_id", 
    "sale_price" 
  FROM "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."ORDER_ITEMS"
),

products AS (
  SELECT 
    "id", 
    "cost"
  FROM "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."PRODUCTS"
),

users AS (
  SELECT
    "id", 
    "traffic_source" 
  FROM "THELOOK_ECOMMERCE"."THELOOK_ECOMMERCE"."USERS"
),

filter_join AS (
  SELECT 
    orders."order_id",
    orders."user_id",
    order_items."product_id",
    orders."delivery_month",
    orders."status",
    order_items."sale_price",
    products."cost",
    users."traffic_source"
  FROM orders
  JOIN order_items ON orders."order_id" = order_items."order_id"
  JOIN products ON order_items."product_id" = products."id"
  JOIN users ON orders."user_id" = users."id"
  WHERE orders."status" = 'Complete' 
    AND users."traffic_source" = 'Facebook'
    AND TO_TIMESTAMP_NTZ(orders."created_at" / 1000000) BETWEEN TO_TIMESTAMP_NTZ('2022-07-01') AND TO_TIMESTAMP_NTZ('2023-11-30')  -- Include July for calculation
),

monthly_sales AS (
  SELECT 
    "delivery_month",
    "traffic_source",
    SUM("sale_price") AS "total_revenue",
    SUM("sale_price") - SUM("cost") AS "total_profit",
    COUNT(DISTINCT "product_id") AS "product_quantity",
    COUNT(DISTINCT "order_id") AS "orders_quantity",
    COUNT(DISTINCT "user_id") AS "users_quantity"
  FROM filter_join
  GROUP BY "delivery_month", "traffic_source"
)

-- Filter to show only 8th month and onwards, but calculate using July
SELECT 
  current_month."delivery_month",
  COALESCE(
    current_month."total_profit" - previous_month."total_profit", 
    0  -- If there is no previous month (i.e. for 8月), return 0
  ) AS "profit_vs_prior_month"
FROM monthly_sales AS current_month
LEFT JOIN monthly_sales AS previous_month
  ON current_month."traffic_source" = previous_month."traffic_source"
  AND current_month."delivery_month" = DATEADD(MONTH, -1, previous_month."delivery_month")  -- Correctly join to previous month
WHERE current_month."delivery_month" >= '2022-08-01'  -- Only show August and later data, but use July for calculation
ORDER BY "profit_vs_prior_month" DESC
LIMIT 5;

```

## sf_bq289.sql

```sql
WITH philadelphia AS (
    SELECT 
        * 
    FROM 
        GEO_OPENSTREETMAP_CENSUS_PLACES.GEO_US_CENSUS_PLACES.PLACES_PENNSYLVANIA
    WHERE 
        "place_name" = 'Philadelphia'
),
amenities AS (
    SELECT 
        features.*, 
        tags.value:"value" AS amenity
    FROM 
        GEO_OPENSTREETMAP_CENSUS_PLACES.GEO_OPENSTREETMAP.PLANET_FEATURES_POINTS AS features
    CROSS JOIN philadelphia
    -- Use FLATTEN on "all_tags" to get the tags and filter by "key"
    , LATERAL FLATTEN(input => features."all_tags") AS tags
    WHERE 
        ST_CONTAINS(ST_GEOGFROMWKB(philadelphia."place_geom"), ST_GEOGFROMWKB(features."geometry"))
    AND 
        tags.value:"key" = 'amenity' 
    AND 
        tags.value:"value" IN ('library', 'place_of_worship', 'community_centre')
),
joiin AS (
    SELECT 
        a1.*, 
        a2."osm_id" AS nearest_osm_id, 
        ST_DISTANCE(ST_GEOGFROMWKB(a1."geometry"), ST_GEOGFROMWKB(a2."geometry")) AS distance, 
        ROW_NUMBER() OVER (PARTITION BY a1."osm_id" ORDER BY ST_DISTANCE(ST_GEOGFROMWKB(a1."geometry"), ST_GEOGFROMWKB(a2."geometry"))) AS row_num
    FROM amenities a1
    CROSS JOIN amenities a2
    WHERE a1."osm_id" < a2."osm_id"
    ORDER BY a1."osm_id", distance
) 
SELECT distance
FROM joiin  
WHERE row_num = 1
ORDER BY distance ASC
LIMIT 1;

```

## sf_bq291.sql

```sql
WITH daily_forecasts AS (
    SELECT
        "TRI"."creation_time",

        CAST(DATEADD(hour, 1, TO_TIMESTAMP_NTZ(TO_NUMBER("forecast".value:"time") / 1000000)) AS DATE) AS "local_forecast_date",
        MAX(
            CASE 
                WHEN "forecast".value:"temperature_2m_above_ground" IS NOT NULL 
                THEN "forecast".value:"temperature_2m_above_ground" 
                ELSE NULL 
            END
        ) AS "max_temp",
        MIN(
            CASE 
                WHEN "forecast".value:"temperature_2m_above_ground" IS NOT NULL 
                THEN "forecast".value:"temperature_2m_above_ground" 
                ELSE NULL 
            END
        ) AS "min_temp",
        AVG(
            CASE 
                WHEN "forecast".value:"temperature_2m_above_ground" IS NOT NULL 
                THEN "forecast".value:"temperature_2m_above_ground" 
                ELSE NULL 
            END
        ) AS "avg_temp",
        SUM(
            CASE 
                WHEN "forecast".value:"total_precipitation_surface" IS NOT NULL 
                THEN "forecast".value:"total_precipitation_surface" 
                ELSE 0 
            END
        ) AS "total_precipitation",
        AVG(
            CASE 
                WHEN CAST(DATEADD(hour, 1, TO_TIMESTAMP_NTZ(TO_NUMBER("forecast".value:"time") / 1000000)    ) AS TIME) BETWEEN '10:00:00' AND '17:00:00'
                     AND "forecast".value:"total_cloud_cover_entire_atmosphere" IS NOT NULL 
                THEN "forecast".value:"total_cloud_cover_entire_atmosphere" 
                ELSE NULL 
            END
        ) AS "avg_cloud_cover",
        CASE
            WHEN AVG("forecast".value:"temperature_2m_above_ground") < 32 THEN 
                SUM(
                    CASE 
                        WHEN "forecast".value:"total_precipitation_surface" IS NOT NULL 
                        THEN "forecast".value:"total_precipitation_surface" 
                        ELSE 0 
                    END
                )
            ELSE 0
        END AS "total_snow",
        CASE
            WHEN AVG("forecast".value:"temperature_2m_above_ground") >= 32 THEN 
                SUM(
                    CASE 
                        WHEN "forecast".value:"total_precipitation_surface" IS NOT NULL 
                        THEN "forecast".value:"total_precipitation_surface" 
                        ELSE 0 
                    END
                )
            ELSE 0
        END AS "total_rain"
    FROM
        "NOAA_GLOBAL_FORECAST_SYSTEM"."NOAA_GLOBAL_FORECAST_SYSTEM"."NOAA_GFS0P25" AS "TRI"
    CROSS JOIN LATERAL FLATTEN(input => "TRI"."forecast") AS "forecast"
    WHERE
        TO_TIMESTAMP_NTZ(TO_NUMBER("TRI"."creation_time") / 1000000) BETWEEN '2019-07-01' AND '2021-07-31'  
        AND ST_DWITHIN(
            ST_GEOGFROMWKB("TRI"."geography"),
            ST_POINT(26.75, 51.5),
            5000
        )
        AND CAST(TO_TIMESTAMP_NTZ(TO_NUMBER("forecast".value:"time") / 1000000) AS DATE) = DATEADD(day, 1, CAST( TO_TIMESTAMP_NTZ(TO_NUMBER("TRI"."creation_time") / 1000000) AS DATE))
    GROUP BY
        "TRI"."creation_time",
        "local_forecast_date"
)

SELECT
    TO_TIMESTAMP_NTZ(TO_NUMBER("creation_time") / 1000000),
    "local_forecast_date" AS "forecast_date",
    "max_temp",
    "min_temp",
    "avg_temp",
    "total_precipitation",
    "avg_cloud_cover",
    "total_snow",
    "total_rain"
FROM
    daily_forecasts
ORDER BY
    "creation_time",
    "forecast_date";

```

## sf_bq294.sql

```sql
SELECT
  "trip_id",
  "duration_sec",
  DATE(TO_TIMESTAMP_LTZ("start_date" / 1000000)) AS "star_date",
  "start_station_name",
  CONCAT("start_station_name", ' - ', "end_station_name") AS "route",
  "bike_number",
  "subscriber_type",
  "member_birth_year",
  (EXTRACT(YEAR FROM CURRENT_DATE()) - "member_birth_year") AS "age",
  CASE
    WHEN (EXTRACT(YEAR FROM CURRENT_DATE()) - "member_birth_year") < 40 THEN 'Young (<40 Y.O)'
    WHEN (EXTRACT(YEAR FROM CURRENT_DATE()) - "member_birth_year") BETWEEN 40 AND 60 THEN 'Adult (40-60 Y.O)'
    ELSE 'Senior Adult (>60 Y.O)'
  END AS "age_class",
  "member_gender",
  c."name" AS "region_name"
FROM "SAN_FRANCISCO_PLUS"."SAN_FRANCISCO_BIKESHARE"."BIKESHARE_TRIPS" a
LEFT JOIN "SAN_FRANCISCO_PLUS"."SAN_FRANCISCO_BIKESHARE"."BIKESHARE_STATION_INFO" b 
  ON a."start_station_id" = b."station_id"
LEFT JOIN "SAN_FRANCISCO_PLUS"."SAN_FRANCISCO_BIKESHARE"."BIKESHARE_REGIONS" c 
  ON b."region_id" = c."region_id"
WHERE TO_TIMESTAMP_LTZ("start_date" / 1000000) BETWEEN '2017-07-01' AND '2017-12-31'
  AND b."station_id" IS NOT NULL
  AND "member_birth_year" IS NOT NULL
  AND "member_gender" IS NOT NULL
ORDER BY "duration_sec" DESC
LIMIT 5;

```

## sf_bq295.sql

```sql
WITH watched_repos AS (
    SELECT
        PARSE_JSON("repo"):"name"::STRING AS "repo"
    FROM 
        GITHUB_REPOS_DATE.MONTH._201701
    WHERE
        "type" = 'WatchEvent'
    UNION ALL
    SELECT
        PARSE_JSON("repo"):"name"::STRING AS "repo"
    FROM 
        GITHUB_REPOS_DATE.MONTH._201702
    WHERE
        "type" = 'WatchEvent'
    UNION ALL
    SELECT
        PARSE_JSON("repo"):"name"::STRING AS "repo"
    FROM 
        GITHUB_REPOS_DATE.MONTH._201703
    WHERE
        "type" = 'WatchEvent'
    UNION ALL
    SELECT
        PARSE_JSON("repo"):"name"::STRING AS "repo"
    FROM 
        GITHUB_REPOS_DATE.MONTH._201704
    WHERE
        "type" = 'WatchEvent'
    UNION ALL
    SELECT
        PARSE_JSON("repo"):"name"::STRING AS "repo"
    FROM 
        GITHUB_REPOS_DATE.MONTH._201705
    WHERE
        "type" = 'WatchEvent'
    UNION ALL
    SELECT
        PARSE_JSON("repo"):"name"::STRING AS "repo"
    FROM 
        GITHUB_REPOS_DATE.MONTH._201706
    WHERE
        "type" = 'WatchEvent'
    UNION ALL
    SELECT
        PARSE_JSON("repo"):"name"::STRING AS "repo"
    FROM 
        GITHUB_REPOS_DATE.MONTH._201707
    WHERE
        "type" = 'WatchEvent'
    UNION ALL
    SELECT
        PARSE_JSON("repo"):"name"::STRING AS "repo"
    FROM 
        GITHUB_REPOS_DATE.MONTH._201708
    WHERE
        "type" = 'WatchEvent'
    UNION ALL
    SELECT
        PARSE_JSON("repo"):"name"::STRING AS "repo"
    FROM 
        GITHUB_REPOS_DATE.MONTH._201709
    WHERE
        "type" = 'WatchEvent'
    UNION ALL
    SELECT
        PARSE_JSON("repo"):"name"::STRING AS "repo"
    FROM 
        GITHUB_REPOS_DATE.MONTH._201710
    WHERE
        "type" = 'WatchEvent'
    UNION ALL
    SELECT
        PARSE_JSON("repo"):"name"::STRING AS "repo"
    FROM 
        GITHUB_REPOS_DATE.MONTH._201711
    WHERE
        "type" = 'WatchEvent'
    UNION ALL
    SELECT
        PARSE_JSON("repo"):"name"::STRING AS "repo"
    FROM 
        GITHUB_REPOS_DATE.MONTH._201712
    WHERE
        "type" = 'WatchEvent'
),

repo_watch_counts AS (
    SELECT
        "repo",
        COUNT(*) AS "watch_count"
    FROM
        watched_repos
    GROUP BY
        "repo"
)

SELECT
    REPLACE(r."repo", '"', '') AS "repo",
    r."watch_count"
FROM
    GITHUB_REPOS_DATE.GITHUB_REPOS.SAMPLE_FILES AS f
JOIN
    GITHUB_REPOS_DATE.GITHUB_REPOS.SAMPLE_CONTENTS AS c
    ON f."id" = c."id"
JOIN 
    repo_watch_counts AS r
    ON f."repo_name" = r."repo"
WHERE
    f."path" LIKE '%.py' 
    AND c."size" < 15000 
    AND POSITION('def ' IN c."content") > 0
GROUP BY
    r."repo", r."watch_count"
ORDER BY
    r."watch_count" DESC
LIMIT 
    3;

```

## sf_bq320.sql

```sql
SELECT
  COUNT(*) AS "total_count"
FROM
  IDC.IDC_V17.DICOM_PIVOT AS "dicom_pivot"
WHERE
  "StudyInstanceUID" IN (
    SELECT
      "StudyInstanceUID"
    FROM
      IDC.IDC_V17.DICOM_PIVOT AS "dicom_pivot"
    WHERE
      "StudyInstanceUID" IN (
        SELECT
          "StudyInstanceUID"
        FROM
          IDC.IDC_V17.DICOM_PIVOT AS "dicom_pivot"
        WHERE
          LOWER("dicom_pivot"."SegmentedPropertyTypeCodeSequence") LIKE LOWER('15825003')
        GROUP BY
          "StudyInstanceUID"
        INTERSECT
        SELECT
          "StudyInstanceUID"
        FROM
          IDC.IDC_V17.DICOM_PIVOT AS "dicom_pivot"
        WHERE
          "dicom_pivot"."collection_id" IN ('Community', 'nsclc_radiomics')
        GROUP BY
          "StudyInstanceUID"
      )
    GROUP BY
      "StudyInstanceUID"
  );

```

## sf_bq321.sql

```sql
WITH relevant_series AS (
  SELECT 
    DISTINCT "StudyInstanceUID"
  FROM 
    IDC.IDC_V17.DICOM_ALL
  WHERE 
    "collection_id" = 'qin_prostate_repeatability'
    AND "SeriesDescription" IN (
      'DWI',
      'T2 Weighted Axial',
      'Apparent Diffusion Coefficient',
      'T2 Weighted Axial Segmentations',
      'Apparent Diffusion Coefficient Segmentations'
    )    
),
t2_seg_lesion_series AS (
  SELECT 
    DISTINCT "StudyInstanceUID"
  FROM 
    IDC.IDC_V17.DICOM_ALL
  CROSS JOIN LATERAL FLATTEN(input => "SegmentSequence") AS segSeq
  WHERE 
    "collection_id" = 'qin_prostate_repeatability'
    AND "SeriesDescription" = 'T2 Weighted Axial Segmentations'
)

SELECT 
    COUNT(DISTINCT "StudyInstanceUID") AS "total_count"
FROM (
  SELECT 
    "StudyInstanceUID" 
  FROM relevant_series
  UNION ALL
  SELECT 
    "StudyInstanceUID"
  FROM t2_seg_lesion_series
);

```

## sf_bq334.sql

```sql
WITH all_transactions AS (
    SELECT 
        TO_TIMESTAMP_NTZ("block_timestamp" / 1000000) AS "timestamp",  -- 将时间戳转换为日期时间格式
        "value",
        'input' AS "type"
    FROM 
        "CRYPTO"."CRYPTO_BITCOIN"."INPUTS"
    UNION ALL
    SELECT 
        TO_TIMESTAMP_NTZ("block_timestamp" / 1000000) AS "timestamp",  -- 将时间戳转换为日期时间格式
        "value",
        'output' AS "type"
    FROM 
        "CRYPTO"."CRYPTO_BITCOIN"."OUTPUTS"
),
filtered_transactions AS (
    SELECT
        EXTRACT(YEAR FROM "timestamp") AS "year",
        "value"
    FROM 
        all_transactions
    WHERE "type" = 'output'
),
average_output_values AS (
    SELECT
        "year",
        AVG("value") AS "avg_value"
    FROM 
        filtered_transactions
    GROUP BY "year"
),
average_transaction_values AS (
    SELECT 
        EXTRACT(YEAR FROM TO_TIMESTAMP_NTZ("block_timestamp" / 1000000)) AS "year",  -- 同样转换时间戳
        AVG("output_value") AS "avg_transaction_value" 
    FROM 
        "CRYPTO"."CRYPTO_BITCOIN"."TRANSACTIONS" 
    GROUP BY "year" 
    ORDER BY "year"
),
common_years AS (
    SELECT
        ao."year",
        ao."avg_value" AS "avg_output_value",
        atv."avg_transaction_value"
    FROM
        average_output_values ao
    JOIN
        average_transaction_values atv 
        ON ao."year" = atv."year"
)

SELECT
    "year",
    "avg_transaction_value" - "avg_output_value" AS "difference"
FROM
    common_years
ORDER BY
    "year";

```

## sf_bq341.sql

```sql
WITH transaction_addresses AS (
    SELECT 
        "from_address", 
        "to_address", 
        CAST("value" AS NUMERIC) / 1000000 AS "value"
    FROM 
        "CRYPTO"."CRYPTO_ETHEREUM"."TOKEN_TRANSFERS"
    WHERE 
        "token_address" = '0xa92a861fc11b99b24296af880011b47f9cafb5ab'
),

out_addresses AS (
    SELECT 
        "from_address", 
        SUM(-1 * "value") AS "total_value"
    FROM 
        transaction_addresses
    GROUP BY 
        "from_address"
),

in_addresses AS (
    SELECT 
        "to_address", 
        SUM("value") AS "total_value"
    FROM 
        transaction_addresses
    GROUP BY 
        "to_address"
),

all_addresses AS (
    SELECT 
        "from_address" AS "address", 
        "total_value"
    FROM 
        out_addresses

    UNION ALL

    SELECT 
        "to_address" AS "address", 
        "total_value"
    FROM 
        in_addresses
)

SELECT 
    "address"
FROM 
    all_addresses
GROUP BY 
    "address"
HAVING 
    SUM("total_value") > 0
ORDER BY 
    SUM("total_value") ASC
LIMIT 3;

```

## sf_bq345.sql

```sql
WITH seg_rtstruct AS (
  SELECT
    "collection_id",
    "StudyInstanceUID",
    "SeriesInstanceUID",
    CONCAT('https://viewer.imaging.datacommons.cancer.gov/viewer/', "StudyInstanceUID") AS "viewer_url",
    "instance_size"
  FROM
    "IDC"."IDC_V17"."DICOM_ALL"
  WHERE
    "Modality" IN ('SEG', 'RTSTRUCT')
    AND "SOPClassUID" = '1.2.840.10008.5.1.4.1.1.66.4'
    AND ARRAY_SIZE("ReferencedSeriesSequence") = 0
    AND ARRAY_SIZE("ReferencedImageSequence") = 0
    AND ARRAY_SIZE("SourceImageSequence") = 0
)

SELECT
  seg_rtstruct."collection_id",
  seg_rtstruct."SeriesInstanceUID",
  seg_rtstruct."StudyInstanceUID",
  seg_rtstruct."viewer_url",
  SUM(seg_rtstruct."instance_size") / 1024 AS "collection_size_KB"
FROM
  seg_rtstruct
GROUP BY
  seg_rtstruct."collection_id",
  seg_rtstruct."SeriesInstanceUID",
  seg_rtstruct."StudyInstanceUID",
  seg_rtstruct."viewer_url"
ORDER BY
  "collection_size_KB" DESC;

```

## sf_bq346.sql

```sql
WITH
  sampled_sops AS (
    SELECT
      "collection_id",
      "SeriesDescription",
      "SeriesInstanceUID",
      "SOPInstanceUID" AS "seg_SOPInstanceUID",
      COALESCE(
        "ReferencedSeriesSequence"[0]."ReferencedInstanceSequence"[0]."ReferencedSOPInstanceUID",
        "ReferencedImageSequence"[0]."ReferencedSOPInstanceUID",
        "SourceImageSequence"[0]."ReferencedSOPInstanceUID"
      ) AS "referenced_sop"
    FROM
      "IDC"."IDC_V17"."DICOM_ALL"
    WHERE
      "Modality" = 'SEG'
      AND "SOPClassUID" = '1.2.840.10008.5.1.4.1.1.66.4'
      AND "access" = 'Public'
  ),
  segmentations_data AS (
    SELECT
      dicom_all."collection_id",
      dicom_all."PatientID",
      dicom_all."SOPInstanceUID",
      REPLACE(segmentations."SegmentedPropertyCategory":CodeMeaning::STRING, '"', '') AS "segmentation_category",
      REPLACE(segmentations."SegmentedPropertyType":CodeMeaning::STRING, '"', '') AS "segmentation_type"
    FROM
      sampled_sops
    JOIN
      "IDC"."IDC_V17"."DICOM_ALL" AS dicom_all
    ON
      sampled_sops."referenced_sop" = dicom_all."SOPInstanceUID"
    JOIN
      "IDC"."IDC_V17"."SEGMENTATIONS" AS segmentations
    ON
      segmentations."SOPInstanceUID" = sampled_sops."seg_SOPInstanceUID"
  )
SELECT
  "segmentation_category",
  COUNT(*) AS "count_"
FROM
  segmentations_data
GROUP BY
  "segmentation_category"
ORDER BY
  "count_" DESC
LIMIT 5;

```

## sf_bq347.sql

```sql
WITH union_mr_seg AS (
  SELECT
    "dicom_all_mr"."SOPInstanceUID",
    '' AS "segPropertyTypeCodeMeaning", 
    '' AS "segPropertyCategoryCodeMeaning"
  FROM
    "IDC"."IDC_V17"."DICOM_ALL" AS "dicom_all_mr"
  WHERE
    "dicom_all_mr"."SeriesInstanceUID" IN ('1.3.6.1.4.1.14519.5.2.1.3671.4754.105976129314091491952445656147')
    
  UNION ALL

  SELECT
    "dicom_all_seg"."SOPInstanceUID",
    "segmentations"."SegmentedPropertyType":"CodeMeaning" AS "segPropertyTypeCodeMeaning",
    "segmentations"."SegmentedPropertyCategory":"CodeMeaning" AS "segPropertyCategoryCodeMeaning"
  FROM
    "IDC"."IDC_V17"."DICOM_ALL" AS "dicom_all_seg"
  JOIN
    "IDC"."IDC_V17"."SEGMENTATIONS" AS "segmentations"
  ON
    "dicom_all_seg"."SOPInstanceUID" = "segmentations"."SOPInstanceUID"
)

SELECT
  "dc_all"."Modality",
  COUNT(*) AS "count_"
FROM 
  "IDC"."IDC_V17"."DICOM_ALL" AS "dc_all"
INNER JOIN
  union_mr_seg
ON 
  "dc_all"."SOPInstanceUID" = union_mr_seg."SOPInstanceUID"
GROUP BY
  "dc_all"."Modality"
ORDER BY
  "count_" DESC
LIMIT 1;

```

## sf_bq349.sql

```sql
WITH bounding_area AS (
    SELECT 
        "osm_id",
        "geometry" AS geometry,
        ST_AREA(ST_GEOGRAPHYFROMWKB("geometry")) AS area
    FROM GEO_OPENSTREETMAP.GEO_OPENSTREETMAP.PLANET_FEATURES,
    LATERAL FLATTEN(INPUT => PLANET_FEATURES."all_tags") AS "tag"
    WHERE 
        "feature_type" = 'multipolygons'
        AND "tag".value:"key" = 'boundary'
        AND "tag".value:"value" = 'administrative'
),

poi AS (
    SELECT 
        nodes."id" AS poi_id,
        nodes."geometry" AS poi_geometry,
        tags.value:"value" AS poitype
    FROM GEO_OPENSTREETMAP.GEO_OPENSTREETMAP.PLANET_NODES AS nodes,
    LATERAL FLATTEN(INPUT => nodes."all_tags") AS tags
    WHERE tags.value:"key" = 'amenity'
),

poi_counts AS (
    SELECT
        ba."osm_id",
        COUNT(poi.poi_id) AS total_pois
    FROM bounding_area ba
    JOIN poi
    ON ST_DWITHIN(
        ST_GEOGRAPHYFROMWKB(ba.geometry), 
        ST_GEOGRAPHYFROMWKB(poi.poi_geometry), 
        0.0
    )
    GROUP BY ba."osm_id"
),

median_value AS (
    SELECT 
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_pois) AS median_pois
    FROM poi_counts
),

closest_to_median AS (
    SELECT
        "osm_id",
        total_pois,
        ABS(total_pois - (SELECT median_pois FROM median_value)) AS diff_from_median
    FROM poi_counts
)

SELECT
    "osm_id"
FROM closest_to_median
ORDER BY diff_from_median
LIMIT 1;

```

## sf_bq358.sql

```sql
SELECT
    "ZIPSTART"."zip_code" AS zip_code_start,
    "ZIPEND"."zip_code" AS zip_code_end
FROM  
    "NEW_YORK_CITIBIKE_1"."NEW_YORK_CITIBIKE"."CITIBIKE_TRIPS" AS "TRI"
INNER JOIN
    "NEW_YORK_CITIBIKE_1"."GEO_US_BOUNDARIES"."ZIP_CODES" AS "ZIPSTART"
    ON ST_WITHIN(
        ST_POINT("TRI"."start_station_longitude", "TRI"."start_station_latitude"),
        ST_GEOGFROMWKB("ZIPSTART"."zip_code_geom")
    )
INNER JOIN
    "NEW_YORK_CITIBIKE_1"."GEO_US_BOUNDARIES"."ZIP_CODES" AS "ZIPEND"
    ON ST_WITHIN(
        ST_POINT("TRI"."end_station_longitude", "TRI"."end_station_latitude"),
        ST_GEOGFROMWKB("ZIPEND"."zip_code_geom")
    )
INNER JOIN
    "NEW_YORK_CITIBIKE_1"."NOAA_GSOD"."GSOD2015" AS "WEA"
    ON TO_DATE(TO_CHAR("WEA"."year") || LPAD(TO_CHAR("WEA"."mo"), 2, '0') || LPAD(TO_CHAR("WEA"."da"), 2, '0'), 'YYYYMMDD') = DATE_TRUNC('DAY', TO_TIMESTAMP_NTZ(TO_NUMBER("TRI"."starttime") / 1000000))
WHERE
    "WEA"."wban" = '94728'
    AND DATE_TRUNC('DAY', TO_TIMESTAMP_NTZ(TO_NUMBER("TRI"."starttime") / 1000000)) = DATE '2015-07-15'
ORDER BY 
    "WEA"."temp" DESC, "ZIPSTART"."zip_code" ASC, "ZIPEND"."zip_code" DESC
LIMIT 1;

```

## sf_bq359.sql

```sql
WITH repositories AS (
    SELECT
        t2."repo_name",
        t2."language"
    FROM (
        SELECT
            t1."repo_name",
            t1."language",
            RANK() OVER (PARTITION BY t1."repo_name" ORDER BY t1."language_bytes" DESC) AS "rank"
        FROM (
            SELECT
                l."repo_name",
                lang.value:"name"::STRING AS "language",
                lang.value:"bytes"::NUMBER AS "language_bytes"
            FROM
                GITHUB_REPOS.GITHUB_REPOS.LANGUAGES AS l,
                LATERAL FLATTEN(input => l."language") AS lang
        ) AS t1
    ) AS t2
    WHERE t2."rank" = 1
),
python_repo AS (
    SELECT
        "repo_name",
        "language"
    FROM
        repositories
    WHERE
        "language" = 'JavaScript'
)
SELECT 
    sc."repo_name", 
    COUNT(sc."commit") AS "num_commits"
FROM 
    GITHUB_REPOS.GITHUB_REPOS.SAMPLE_COMMITS AS sc
INNER JOIN 
    python_repo 
ON 
    python_repo."repo_name" = sc."repo_name"
GROUP BY 
    sc."repo_name"
ORDER BY 
    "num_commits" DESC
LIMIT 2;

```

## sf_bq377.sql

```sql
WITH json_files AS (
  SELECT
    c."id",
    TRY_PARSE_JSON(c."content"):"require" AS "dependencies"
  FROM
    GITHUB_REPOS.GITHUB_REPOS.SAMPLE_CONTENTS c
),
package_names AS (
  SELECT
    f.key AS "package_name"
  FROM
    json_files,
    LATERAL FLATTEN(input => "dependencies") AS f
)
SELECT
  "package_name",
  COUNT(*) AS "count"
FROM
  package_names
WHERE
  "package_name" IS NOT NULL
GROUP BY
  "package_name"
ORDER BY
  "count" DESC;

```

## sf_bq390.sql

```sql
WITH
-- Studies that have MR volumes
"mr_studies" AS (
  SELECT
    "dicom_all_mr"."StudyInstanceUID"
  FROM
    "IDC"."IDC_V17"."DICOM_ALL" AS "dicom_all_mr"
  WHERE
    "Modality" = 'MR'
    AND "collection_id" = 'qin_prostate_repeatability'
    AND CONTAINS("SeriesDescription", 'T2 Weighted Axial')
),

"seg_studies" AS (
  SELECT
    "dicom_all_seg"."StudyInstanceUID"
  FROM
    "IDC"."IDC_V17"."DICOM_ALL" AS "dicom_all_seg"
  JOIN
    "IDC"."IDC_V17"."SEGMENTATIONS" AS "segmentations"
  ON
    "dicom_all_seg"."SOPInstanceUID" = "segmentations"."SOPInstanceUID"
  WHERE
    "collection_id" = 'qin_prostate_repeatability'
    AND CONTAINS("segmentations"."SegmentedPropertyType":"CodeMeaning", 'Peripheral zone')
    AND "segmentations"."SegmentedPropertyCategory":"CodeMeaning" = 'Anatomical Structure'
)

SELECT DISTINCT
  "mr_studies"."StudyInstanceUID"
FROM
  "mr_studies"
JOIN
  "seg_studies"
ON
  "mr_studies"."StudyInstanceUID" = "seg_studies"."StudyInstanceUID";

```

## sf_bq412.sql

```sql
SELECT
    "creative_page_url",
    TO_TIMESTAMP(GET("region_stat".value, 'first_shown')) AS "first_shown",
    TO_TIMESTAMP(GET("region_stat".value, 'last_shown')) AS "last_shown",
    REPLACE(REPLACE("disapproval"[0]."removal_reason", '""', '"'), '"', '') AS "removal_reason", 
    REPLACE(REPLACE("disapproval"[0]."violation_category", '""', '"'), '"', '') AS "violation_category",
    GET("region_stat".value, 'times_shown_lower_bound') AS "times_shown_lower",
    GET("region_stat".value, 'times_shown_upper_bound') AS "times_shown_upper"
FROM
    "GOOGLE_ADS"."GOOGLE_ADS_TRANSPARENCY_CENTER"."REMOVED_CREATIVE_STATS",
    LATERAL FLATTEN(input => "region_stats") AS "region_stat"
WHERE
    GET("region_stat".value, 'region_code') = 'HR' 
    AND GET("region_stat".value, 'times_shown_availability_date') IS NULL 
    AND GET("region_stat".value, 'times_shown_lower_bound') > 10000 
    AND GET("region_stat".value, 'times_shown_upper_bound') < 25000
    AND (
        GET("audience_selection_approach_info", 'demographic_info') != 'CRITERIA_UNUSED' 
        OR GET("audience_selection_approach_info", 'geo_location') != 'CRITERIA_UNUSED' 
        OR GET("audience_selection_approach_info", 'contextual_signals') != 'CRITERIA_UNUSED' 
        OR GET("audience_selection_approach_info", 'customer_lists') != 'CRITERIA_UNUSED' 
        OR GET("audience_selection_approach_info", 'topics_of_interest') != 'CRITERIA_UNUSED'
    )
ORDER BY
    "last_shown" DESC
LIMIT 5;

```

## sf_bq421.sql

```sql
WITH
  SpecimenPreparationSequence_unnested AS (
    SELECT
      d."SOPInstanceUID",
      concept_name_code_sequence.value:"CodeMeaning"::STRING AS "cnc_cm",
      concept_name_code_sequence.value:"CodingSchemeDesignator"::STRING AS "cnc_csd",
      concept_name_code_sequence.value:"CodeValue"::STRING AS "cnc_val",
      concept_code_sequence.value:"CodeMeaning"::STRING AS "ccs_cm",
      concept_code_sequence.value:"CodingSchemeDesignator"::STRING AS "ccs_csd",
      concept_code_sequence.value:"CodeValue"::STRING AS "ccs_val"
    FROM
      "IDC"."IDC_V17"."DICOM_ALL" AS d,
      LATERAL FLATTEN(input => d."SpecimenDescriptionSequence") AS spec_desc,
      LATERAL FLATTEN(input => spec_desc.value:"SpecimenPreparationSequence") AS prep_seq,
      LATERAL FLATTEN(input => prep_seq.value:"SpecimenPreparationStepContentItemSequence") AS prep_step,
      LATERAL FLATTEN(input => prep_step.value:"ConceptNameCodeSequence") AS concept_name_code_sequence,
      LATERAL FLATTEN(input => prep_step.value:"ConceptCodeSequence") AS concept_code_sequence
  ),
  slide_embedding AS (
    SELECT
      "SOPInstanceUID",
      ARRAY_AGG(DISTINCT(CONCAT("ccs_cm", ':', "ccs_csd", ':', "ccs_val"))) AS "embeddingMedium_code_str"
    FROM
      SpecimenPreparationSequence_unnested
    WHERE
      "cnc_csd" = 'SCT' AND "cnc_val" = '430863003' -- CodeMeaning is 'Embedding medium'
    GROUP BY
      "SOPInstanceUID"
  ),
  slide_staining AS (
    SELECT
      "SOPInstanceUID",
      ARRAY_AGG(DISTINCT(CONCAT("ccs_cm", ':', "ccs_csd", ':', "ccs_val"))) AS "staining_usingSubstance_code_str"
    FROM
      SpecimenPreparationSequence_unnested
    WHERE
      "cnc_csd" = 'SCT' AND "cnc_val" = '424361007' -- CodeMeaning is 'Using substance'
    GROUP BY
      "SOPInstanceUID"
  ),
  embedding_data AS (
    SELECT
      d."SOPInstanceUID",
      d."instance_size",
      e."embeddingMedium_code_str",
      s."staining_usingSubstance_code_str"
    FROM
      "IDC"."IDC_V17"."DICOM_ALL" AS d
    LEFT JOIN
      slide_embedding AS e ON d."SOPInstanceUID" = e."SOPInstanceUID"
    LEFT JOIN
      slide_staining AS s ON d."SOPInstanceUID" = s."SOPInstanceUID"
    WHERE
      d."Modality" = 'SM'
  )
SELECT
  SPLIT_PART(embeddingMedium_CodeMeaning_flat.VALUE::STRING, ':', 1) AS "embeddingMedium_CodeMeaning",
  SPLIT_PART(staining_usingSubstance_CodeMeaning_flat.VALUE::STRING, ':', 1) AS "staining_usingSubstance_CodeMeaning",
  COUNT(*) AS "count_"
FROM
  embedding_data
  , LATERAL FLATTEN(input => embedding_data."embeddingMedium_code_str") AS embeddingMedium_CodeMeaning_flat
  , LATERAL FLATTEN(input => embedding_data."staining_usingSubstance_code_str") AS staining_usingSubstance_CodeMeaning_flat
GROUP BY
  SPLIT_PART(embeddingMedium_CodeMeaning_flat.VALUE::STRING, ':', 1),
  SPLIT_PART(staining_usingSubstance_CodeMeaning_flat.VALUE::STRING, ':', 1);

```

## sf_bq422.sql

```sql
WITH
  nonLocalizerRawData AS (
    SELECT
      "SeriesInstanceUID",
      "StudyInstanceUID",
      "PatientID",
      TRY_CAST("Exposure"::STRING AS FLOAT) AS "Exposure",  -- 直接从 bid 获取 Exposure
      TRY_CAST(axes.VALUE::STRING AS FLOAT) AS "zImagePosition",
      LEAD(TRY_CAST(axes.VALUE::STRING AS FLOAT)) OVER (
        PARTITION BY "SeriesInstanceUID" 
        ORDER BY TRY_CAST(axes.VALUE::STRING AS FLOAT)
      ) - TRY_CAST(axes.VALUE::STRING AS FLOAT) AS "slice_interval",
      "instance_size" AS "instanceSize"
    FROM
      "IDC"."IDC_V17"."DICOM_ALL" AS "bid",
      LATERAL FLATTEN(input => "bid"."ImagePositionPatient") AS axes  -- 使用 LATERAL FLATTEN 展开数组
    WHERE
      "collection_id" = 'nlst' 
      AND "Modality" = 'CT' 
  ),
  geometryChecks AS (
    SELECT
      "SeriesInstanceUID",
      "StudyInstanceUID",
      "PatientID",
      ARRAY_AGG(DISTINCT "slice_interval") AS "sliceIntervalDifferences",
      ARRAY_AGG(DISTINCT "Exposure") AS "distinctExposures",
      SUM("instanceSize") / 1024 / 1024 AS "seriesSizeInMB"
    FROM
      nonLocalizerRawData
    GROUP BY
      "SeriesInstanceUID", 
      "StudyInstanceUID",
      "PatientID"
  ),
  patientMetrics AS (
    SELECT
      "PatientID",
      MAX(TRY_CAST(sid.VALUE::STRING AS FLOAT)) AS "maxSliceIntervalDifference",
      MIN(TRY_CAST(sid.VALUE::STRING AS FLOAT)) AS "minSliceIntervalDifference",
      MAX(TRY_CAST(sid.VALUE::STRING AS FLOAT)) - MIN(TRY_CAST(sid.VALUE::STRING AS FLOAT)) AS "sliceIntervalDifferenceTolerance",
      MAX(TRY_CAST(de.VALUE::STRING AS FLOAT)) AS "maxExposure",
      MIN(TRY_CAST(de.VALUE::STRING AS FLOAT)) AS "minExposure",
      MAX(TRY_CAST(de.VALUE::STRING AS FLOAT)) - MIN(TRY_CAST(de.VALUE::STRING AS FLOAT)) AS "maxExposureDifference",
      "seriesSizeInMB"
    FROM
      geometryChecks,
      LATERAL FLATTEN(input => "sliceIntervalDifferences") AS sid,  -- 展开 sliceIntervalDifferences
      LATERAL FLATTEN(input => "distinctExposures") AS de  -- 展开 distinctExposures
    WHERE
      sid.VALUE IS NOT NULL
      AND de.VALUE IS NOT NULL
    GROUP BY
      "PatientID",
      "seriesSizeInMB"
  ),
  top3BySliceInterval AS (
    SELECT
      "PatientID",
      "seriesSizeInMB"
    FROM
      patientMetrics
    ORDER BY
      "sliceIntervalDifferenceTolerance" DESC
    LIMIT 3
  ),
  top3ByMaxExposure AS (
    SELECT
      "PatientID",
      "seriesSizeInMB"
    FROM
      patientMetrics
    ORDER BY
      "maxExposureDifference" DESC
    LIMIT 3
  )
SELECT
  'Top 3 by Slice Interval' AS "MetricGroup",
  AVG("seriesSizeInMB") AS "AverageSeriesSizeInMB"
FROM
  top3BySliceInterval
UNION ALL
SELECT
  'Top 3 by Max Exposure' AS "MetricGroup",
  AVG("seriesSizeInMB") AS "AverageSeriesSizeInMB"
FROM
  top3ByMaxExposure;

```

## sf_bq429.sql

```sql
WITH median_income_diff_by_zipcode AS (
  WITH acs_2018 AS (
    SELECT
      "geo_id",
      "median_income" AS "median_income_2018"
    FROM
      CENSUS_BUREAU_ACS_2.CENSUS_BUREAU_ACS."ZIP_CODES_2018_5YR"
  ),
  acs_2015 AS (
    SELECT
      "geo_id",
      "median_income" AS "median_income_2015"
    FROM
      CENSUS_BUREAU_ACS_2.CENSUS_BUREAU_ACS."ZIP_CODES_2015_5YR"
  ),
  acs_diff AS (
    SELECT
      a18."geo_id",
      (a18."median_income_2018" - a15."median_income_2015") AS "median_income_diff"
    FROM
      acs_2018 a18
    JOIN
      acs_2015 a15 ON a18."geo_id" = a15."geo_id"
  )
  SELECT
    "geo_id",
    AVG("median_income_diff") AS "avg_median_income_diff"
  FROM
    acs_diff
  WHERE
    "median_income_diff" IS NOT NULL
  GROUP BY "geo_id"
),
base_census AS (
  SELECT
    geo."state_name",
    AVG(i."avg_median_income_diff") AS "avg_median_income_diff",
    AVG(
      "employed_wholesale_trade" * 0.38423645320197042 +
      "occupation_natural_resources_construction_maintenance" * 0.48071410777129553 +
      "employed_arts_entertainment_recreation_accommodation_food" * 0.89455676291236841 +
      "employed_information" * 0.31315240083507306 +
      "employed_retail_trade" * 0.51
    ) AS "avg_vulnerable"
  FROM
    CENSUS_BUREAU_ACS_2.CENSUS_BUREAU_ACS."ZIP_CODES_2017_5YR" AS census
  JOIN
    median_income_diff_by_zipcode i ON CAST(census."geo_id" AS STRING) = i."geo_id"
  JOIN
    CENSUS_BUREAU_ACS_2.GEO_US_BOUNDARIES."ZIP_CODES" geo ON census."geo_id" = geo."zip_code"
  GROUP BY geo."state_name"
)

SELECT 
  "state_name",
  "avg_median_income_diff",
  "avg_vulnerable"
FROM 
  base_census
ORDER BY 
  "avg_median_income_diff" DESC
LIMIT 5;

```

## sf_bq444.sql

```sql
WITH parsed_burn_logs AS (
  SELECT
    logs."block_timestamp" AS block_timestamp,
    logs."block_number" AS block_number,
    logs."transaction_hash" AS transaction_hash,
    logs."log_index" AS log_index,
    PARSE_JSON(logs."data") AS data,
    logs."topics"
  FROM CRYPTO.CRYPTO_ETHEREUM.LOGS AS logs
  WHERE logs."address" = '0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8'
    AND logs."topics"[0] = '0x0c396cd989a39f4459b5fa1aed6a9a8dcdbc45908acfd67e028cd568da98982c'
),
parsed_mint_logs AS (
  SELECT
    logs."block_timestamp" AS block_timestamp,
    logs."block_number" AS block_number,
    logs."transaction_hash" AS transaction_hash,
    logs."log_index" AS log_index,
    PARSE_JSON(logs."data") AS data,
    logs."topics"
  FROM CRYPTO.CRYPTO_ETHEREUM.LOGS AS logs
  WHERE logs."address" = '0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8'
    AND logs."topics"[0] = '0x7a53080ba414158be7ec69b987b5fb7d07dee101fe85488f0853ae16239d0bde'
)

SELECT
    block_timestamp,
    block_number,
    transaction_hash
FROM parsed_mint_logs

UNION ALL

SELECT
    block_timestamp,
    block_number,
    transaction_hash
FROM parsed_burn_logs

ORDER BY block_timestamp
LIMIT 5;

```

## sf_bq455.sql

```sql
WITH
  -- Create a common table expression (CTE) named localizerAndJpegCompressedSeries
  localizerAndJpegCompressedSeries AS (
    SELECT 
      "SeriesInstanceUID"
    FROM 
      IDC.IDC_V17."DICOM_ALL" AS bid
    WHERE 
      "ImageType" = 'LOCALIZER' OR
      "TransferSyntaxUID" IN ('1.2.840.10008.1.2.4.70', '1.2.840.10008.1.2.4.51')
  ),
  
  -- Create a common table expression (CTE) for x_vector calculation (first three elements)
  imageOrientation AS (
    SELECT
      "SeriesInstanceUID",
      ARRAY_AGG(CAST(part.value AS FLOAT)) AS "x_vector"
    FROM 
      IDC.IDC_V17."DICOM_ALL" AS bid,
      LATERAL FLATTEN(input => bid."ImageOrientationPatient") AS part
    WHERE
      part.index BETWEEN 0 AND 2
    GROUP BY "SeriesInstanceUID"
  ),
  
  -- Create a common table expression (CTE) for y_vector calculation (next three elements)
  imageOrientationY AS (
    SELECT
      "SeriesInstanceUID",
      ARRAY_AGG(CAST(part.value AS FLOAT)) AS "y_vector"
    FROM 
      IDC.IDC_V17."DICOM_ALL" AS bid,
      LATERAL FLATTEN(input => bid."ImageOrientationPatient") AS part
    WHERE
      part.index BETWEEN 3 AND 5
    GROUP BY "SeriesInstanceUID"
  ),
  
  -- Create a common table expression (CTE) named nonLocalizerRawData
  nonLocalizerRawData AS (
    SELECT
      bid."SeriesInstanceUID",  -- Added table alias bid
      bid."StudyInstanceUID",
      bid."PatientID",
      bid."SOPInstanceUID",
      bid."SliceThickness",
      bid."ImageType",
      bid."TransferSyntaxUID",
      bid."SeriesNumber",
      bid."aws_bucket",
      bid."crdc_series_uuid",
      CAST(bid."Exposure" AS FLOAT) AS "Exposure",  -- Use CAST directly
      CAST(ipp.value AS FLOAT) AS "zImagePosition", -- Use CAST directly
      CONCAT(ipp2.value, '/', ipp3.value) AS "xyImagePosition",
      LEAD(CAST(ipp.value AS FLOAT)) OVER (PARTITION BY bid."SeriesInstanceUID" ORDER BY CAST(ipp.value AS FLOAT)) - CAST(ipp.value AS FLOAT) AS "slice_interval",
      ARRAY_TO_STRING(bid."ImageOrientationPatient", '/') AS "iop",
      bid."PixelSpacing",
      bid."Rows" AS "pixelRows",
      bid."Columns" AS "pixelColumns",
      bid."instance_size" AS "instanceSize"
    FROM
      IDC.IDC_V17."DICOM_ALL" AS bid
    LEFT JOIN LATERAL FLATTEN(input => bid."ImagePositionPatient") AS ipp
    LEFT JOIN LATERAL FLATTEN(input => bid."ImagePositionPatient") AS ipp2
    LEFT JOIN LATERAL FLATTEN(input => bid."ImagePositionPatient") AS ipp3
    WHERE
      bid."collection_id" != 'nlst'
      AND bid."Modality" = 'CT'
      AND ipp.index = 2
      AND ipp2.index = 0
      AND ipp3.index = 1
      AND bid."SeriesInstanceUID" NOT IN (SELECT "SeriesInstanceUID" FROM localizerAndJpegCompressedSeries)
  ),
  
  -- Cross product calculation
  crossProduct AS (
    SELECT
      nld."SOPInstanceUID",  -- Added table alias nld
      nld."SeriesInstanceUID",  -- Added table alias nld
      OBJECT_CONSTRUCT(
        'x', ("x_vector"[1] * "y_vector"[2] - "x_vector"[2] * "y_vector"[1]),
        'y', ("x_vector"[2] * "y_vector"[0] - "x_vector"[0] * "y_vector"[2]),
        'z', ("x_vector"[0] * "y_vector"[1] - "x_vector"[1] * "y_vector"[0])
      ) AS "xyCrossProduct"
    FROM 
      nonLocalizerRawData AS nld  -- Added alias for nonLocalizerRawData
    JOIN imageOrientation AS io ON nld."SeriesInstanceUID" = io."SeriesInstanceUID"
    JOIN imageOrientationY AS ioy ON nld."SeriesInstanceUID" = ioy."SeriesInstanceUID"
  ),
  
  -- Cross product elements extraction and row numbering
  crossProductElements AS (
    SELECT
      cp."SOPInstanceUID",  
      cp."SeriesInstanceUID",  
      elem.value,
      ROW_NUMBER() OVER (PARTITION BY cp."SOPInstanceUID", cp."SeriesInstanceUID" ORDER BY elem.value) AS rn
    FROM 
      crossProduct AS cp  
    -- Use LATERAL FLATTEN to explode the cross product object into individual 'x', 'y', and 'z'
    JOIN LATERAL FLATTEN(input => ARRAY_CONSTRUCT(
          cp."xyCrossProduct"['x'],
          cp."xyCrossProduct"['y'],
          cp."xyCrossProduct"['z']
    )) AS elem -- Simplified 'elem.value' reference here
  ),
  
  -- Dot product calculation
  dotProduct AS (
    SELECT
      cpe."SOPInstanceUID",  
      cpe."SeriesInstanceUID",  
      SUM(
        CASE 
          WHEN cpe.rn = 1 THEN cpe.value * 0  -- x * 0
          WHEN cpe.rn = 2 THEN cpe.value * 0  -- y * 0
          WHEN cpe.rn = 3 THEN cpe.value * 1  -- z * 1
        END
      ) AS "xyDotProduct"
    FROM 
      crossProductElements AS cpe
    GROUP BY 
      cpe."SOPInstanceUID",  
      cpe."SeriesInstanceUID"
  ),
  
  -- Geometry checks for series consistency
  geometryChecks AS (
    SELECT
      gc."SeriesInstanceUID",  -- Added table alias gc
      gc."SeriesNumber",
      gc."aws_bucket",
      gc."crdc_series_uuid",
      gc."StudyInstanceUID",
      gc."PatientID",
      ARRAY_AGG(DISTINCT gc."slice_interval") AS "sliceIntervalDifferences",
      ARRAY_AGG(DISTINCT gc."Exposure") AS "distinctExposures",
      COUNT(DISTINCT gc."iop") AS "iopCount",
      COUNT(DISTINCT gc."PixelSpacing") AS "pixelSpacingCount",
      COUNT(DISTINCT gc."zImagePosition") AS "positionCount",
      COUNT(DISTINCT gc."xyImagePosition") AS "xyPositionCount",
      COUNT(DISTINCT gc."SOPInstanceUID") AS "sopInstanceCount",
      COUNT(DISTINCT gc."SliceThickness") AS "sliceThicknessCount",
      COUNT(DISTINCT gc."Exposure") AS "exposureCount",
      COUNT(DISTINCT gc."pixelRows") AS "pixelRowCount",
      COUNT(DISTINCT gc."pixelColumns") AS "pixelColumnCount",
      dp."xyDotProduct",  -- Added xyDotProduct from dotProduct
      SUM(gc."instanceSize") / 1024 / 1024 AS "seriesSizeInMiB"
    FROM 
      nonLocalizerRawData AS gc  -- Added table alias gc
    JOIN dotProduct AS dp ON gc."SeriesInstanceUID" = dp."SeriesInstanceUID" 
    AND gc."SOPInstanceUID" = dp."SOPInstanceUID"
    GROUP BY
      gc."SeriesInstanceUID", 
      gc."SeriesNumber",
      gc."aws_bucket",
      gc."crdc_series_uuid",
      gc."StudyInstanceUID",
      gc."PatientID",
      dp."xyDotProduct"  -- Include xyDotProduct in GROUP BY
    HAVING
      COUNT(DISTINCT gc."iop") = 1 
      AND COUNT(DISTINCT gc."PixelSpacing") = 1  
      AND COUNT(DISTINCT gc."SOPInstanceUID") = COUNT(DISTINCT gc."zImagePosition") 
      AND COUNT(DISTINCT gc."xyImagePosition") = 1
      AND COUNT(DISTINCT gc."pixelRows") = 1 
      AND COUNT(DISTINCT gc."pixelColumns") = 1 
      AND ABS(dp."xyDotProduct") BETWEEN 0.99 AND 1.01
  )

SELECT
  geometryChecks."SeriesInstanceUID",  -- Added table alias
  geometryChecks."SeriesNumber",  -- Added table alias
  geometryChecks."PatientID",  -- Added table alias
  geometryChecks."seriesSizeInMiB"
FROM
  geometryChecks
ORDER BY
  geometryChecks."seriesSizeInMiB" DESC
LIMIT 5;

```

