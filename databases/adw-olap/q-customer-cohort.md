# Customer Cohort Analysis - Business Questions

## Introduction

Customer cohort analysis is a powerful analytical technique that groups customers based on shared characteristics or experiences within a defined time period, typically their first purchase date. By tracking these cohorts over time, businesses can gain deep insights into customer behavior, retention patterns, lifetime value, and the effectiveness of acquisition strategies.

This document presents a comprehensive cohort analysis framework using the AdventureWorks data warehouse. The analysis leverages FactInternetSales combined with DimCustomer, DimDate, DimProduct, and other dimension tables to examine customer purchasing patterns across different acquisition periods.

The following business questions explore various aspects of cohort behavior including:
- Retention rates and purchase frequency over time
- Lifetime value progression by cohort
- Product preferences and cross-selling opportunities
- Demographic patterns in successful cohorts
- Churn and reactivation patterns

These analyses enable data-driven decision-making for customer acquisition, retention strategies, and personalized marketing campaigns.

---

# Business Question 1: Monthly Customer Cohort Retention Analysis with Purchase Frequency

## Intent

Analyze customer retention by monthly acquisition cohorts, tracking how many customers from each cohort make repeat purchases in subsequent months. This classic cohort analysis provides insights into:
- Customer retention rates over time by acquisition month
- Purchase frequency patterns for each cohort
- Identification of strong vs. weak cohorts
- Time-to-second-purchase and ongoing engagement
- Cohort maturity curves showing how retention stabilizes

The analysis creates cohorts based on the month of first purchase, then tracks each cohort's activity in subsequent months (Month 0, Month 1, Month 2, etc.). This helps identify optimal retention strategies and expected customer lifecycle patterns.

## SQL Code

```sql
WITH CustomerFirstPurchase AS (
    SELECT
        c.CustomerKey,
        CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
        MIN(dd.FullDateAlternateKey) AS FirstPurchaseDate,
        MIN(dd.CalendarYear) AS CohortYear,
        MIN(dd.MonthNumberOfYear) AS CohortMonth,
        MIN(CAST(dd.CalendarYear AS VARCHAR) || '-' ||
            CASE WHEN dd.MonthNumberOfYear < 10
                 THEN '0' || CAST(dd.MonthNumberOfYear AS VARCHAR)
                 ELSE CAST(dd.MonthNumberOfYear AS VARCHAR)
            END) AS CohortPeriod
    FROM FactInternetSales fis
    INNER JOIN DimCustomer c ON fis.CustomerKey = c.CustomerKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    GROUP BY c.CustomerKey, c.FirstName, c.LastName
),
CustomerPurchaseActivity AS (
    SELECT
        cfp.CustomerKey,
        cfp.CohortPeriod,
        dd.CalendarYear,
        dd.MonthNumberOfYear,
        CAST(dd.CalendarYear AS VARCHAR) || '-' ||
            CASE WHEN dd.MonthNumberOfYear < 10
                 THEN '0' || CAST(dd.MonthNumberOfYear AS VARCHAR)
                 ELSE CAST(dd.MonthNumberOfYear AS VARCHAR)
            END AS ActivityPeriod,
        COUNT(DISTINCT fis.SalesOrderNumber) AS OrderCount,
        SUM(fis.SalesAmount) AS PeriodRevenue
    FROM CustomerFirstPurchase cfp
    INNER JOIN FactInternetSales fis ON cfp.CustomerKey = fis.CustomerKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    GROUP BY
        cfp.CustomerKey, cfp.CohortPeriod, dd.CalendarYear,
        dd.MonthNumberOfYear
),
CohortMonthsFromStart AS (
    SELECT
        cpa.CohortPeriod,
        cpa.CustomerKey,
        cpa.ActivityPeriod,
        cpa.OrderCount,
        cpa.PeriodRevenue,
        (cpa.CalendarYear - cfp.CohortYear) * 12 +
        (cpa.MonthNumberOfYear - cfp.CohortMonth) AS MonthsFromCohortStart
    FROM CustomerPurchaseActivity cpa
    INNER JOIN CustomerFirstPurchase cfp
        ON cpa.CustomerKey = cfp.CustomerKey
),
CohortRetention AS (
    SELECT
        CohortPeriod,
        MonthsFromCohortStart,
        COUNT(DISTINCT CustomerKey) AS ActiveCustomers,
        SUM(OrderCount) AS TotalOrders,
        SUM(PeriodRevenue) AS TotalRevenue,
        AVG(OrderCount) AS AvgOrdersPerCustomer,
        AVG(PeriodRevenue) AS AvgRevenuePerCustomer
    FROM CohortMonthsFromStart
    GROUP BY CohortPeriod, MonthsFromCohortStart
),
CohortSize AS (
    SELECT
        CohortPeriod,
        COUNT(DISTINCT CustomerKey) AS CohortSize,
        SUM(PeriodRevenue) AS Month0Revenue
    FROM CohortMonthsFromStart
    WHERE MonthsFromCohortStart = 0
    GROUP BY CohortPeriod
)
SELECT
    cr.CohortPeriod,
    cs.CohortSize,
    cr.MonthsFromCohortStart,
    cr.ActiveCustomers,
    ROUND((CAST(cr.ActiveCustomers AS FLOAT) / cs.CohortSize) * 100, 2) AS RetentionPct,
    cr.TotalOrders,
    ROUND(cr.TotalRevenue, 2) AS TotalRevenue,
    ROUND(cr.AvgOrdersPerCustomer, 2) AS AvgOrdersPerCustomer,
    ROUND(cr.AvgRevenuePerCustomer, 2) AS AvgRevenuePerCustomer,
    ROUND(cr.TotalRevenue / cs.Month0Revenue * 100, 2) AS RevenueVsMonth0Pct
FROM CohortRetention cr
INNER JOIN CohortSize cs ON cr.CohortPeriod = cs.CohortPeriod
WHERE cr.MonthsFromCohortStart <= 12  -- First 12 months of cohort life
ORDER BY cr.CohortPeriod, cr.MonthsFromCohortStart;
```

---

# Business Question 2: Cohort Lifetime Value Progression and Revenue Contribution Analysis

## Intent

Track cumulative revenue (customer lifetime value) by cohort over time and analyze how different acquisition periods contribute to total revenue. This analysis provides:
- Cumulative LTV curves for each cohort showing revenue accumulation over time
- Comparison of cohort quality by acquisition period
- Revenue contribution analysis showing which cohorts drive the most business
- Average customer value by cohort
- Time to breakeven and payback period insights
- Identification of high-performing vs. underperforming cohorts

This helps evaluate marketing campaign effectiveness, seasonal acquisition patterns, and long-term customer value by acquisition timing.

## SQL Code

```sql
WITH CustomerFirstPurchase AS (
    SELECT
        c.CustomerKey,
        MIN(dd.FullDateAlternateKey) AS FirstPurchaseDate,
        MIN(dd.CalendarYear) AS CohortYear,
        MIN(dd.CalendarQuarter) AS CohortQuarter,
        MIN(CAST(dd.CalendarYear AS VARCHAR) || '-Q' ||
            CAST(dd.CalendarQuarter AS VARCHAR)) AS CohortPeriod
    FROM FactInternetSales fis
    INNER JOIN DimCustomer c ON fis.CustomerKey = c.CustomerKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    GROUP BY c.CustomerKey
),
CustomerRevenue AS (
    SELECT
        cfp.CustomerKey,
        cfp.CohortPeriod,
        cfp.CohortYear,
        cfp.CohortQuarter,
        dd.CalendarYear,
        dd.CalendarQuarter,
        SUM(fis.SalesAmount) AS Revenue,
        COUNT(DISTINCT fis.SalesOrderNumber) AS OrderCount
    FROM CustomerFirstPurchase cfp
    INNER JOIN FactInternetSales fis ON cfp.CustomerKey = fis.CustomerKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    GROUP BY
        cfp.CustomerKey, cfp.CohortPeriod, cfp.CohortYear,
        cfp.CohortQuarter, dd.CalendarYear, dd.CalendarQuarter
),
QuartersFromCohort AS (
    SELECT
        cr.CohortPeriod,
        cr.CustomerKey,
        (cr.CalendarYear - cr.CohortYear) * 4 +
        (cr.CalendarQuarter - cr.CohortQuarter) AS QuartersFromStart,
        cr.Revenue,
        cr.OrderCount
    FROM CustomerRevenue cr
),
CumulativeRevenue AS (
    SELECT
        CohortPeriod,
        CustomerKey,
        QuartersFromStart,
        Revenue,
        OrderCount,
        SUM(Revenue) OVER (
            PARTITION BY CohortPeriod, CustomerKey
            ORDER BY QuartersFromStart
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS CumulativeLTV
    FROM QuartersFromCohort
),
CohortMetrics AS (
    SELECT
        CohortPeriod,
        QuartersFromStart,
        COUNT(DISTINCT CustomerKey) AS ActiveCustomers,
        SUM(Revenue) AS QuarterRevenue,
        AVG(CumulativeLTV) AS AvgCumulativeLTV,
        MIN(CumulativeLTV) AS MinLTV,
        MAX(CumulativeLTV) AS MaxLTV,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CumulativeLTV) AS MedianLTV,
        SUM(OrderCount) AS TotalOrders
    FROM CumulativeRevenue
    GROUP BY CohortPeriod, QuartersFromStart
),
CohortSize AS (
    SELECT
        CohortPeriod,
        COUNT(DISTINCT CustomerKey) AS TotalCustomers,
        SUM(Revenue) AS TotalCohortRevenue
    FROM QuartersFromCohort
    GROUP BY CohortPeriod
),
OverallRevenue AS (
    SELECT SUM(Revenue) AS TotalRevenue
    FROM QuartersFromCohort
)
SELECT
    cm.CohortPeriod,
    cs.TotalCustomers AS CohortSize,
    cm.QuartersFromStart,
    cm.ActiveCustomers,
    ROUND(cm.QuarterRevenue, 2) AS QuarterRevenue,
    ROUND(cm.AvgCumulativeLTV, 2) AS AvgCumulativeLTV,
    ROUND(cm.MedianLTV, 2) AS MedianLTV,
    ROUND(cm.MinLTV, 2) AS MinLTV,
    ROUND(cm.MaxLTV, 2) AS MaxLTV,
    cm.TotalOrders,
    ROUND(cs.TotalCohortRevenue, 2) AS TotalCohortRevenue,
    ROUND((cs.TotalCohortRevenue / (SELECT TotalRevenue FROM OverallRevenue)) * 100, 2) AS PctOfTotalRevenue,
    ROUND(cs.TotalCohortRevenue / cs.TotalCustomers, 2) AS AvgLifetimeValuePerCustomer
FROM CohortMetrics cm
INNER JOIN CohortSize cs ON cm.CohortPeriod = cs.CohortPeriod
WHERE cm.QuartersFromStart <= 8  -- First 8 quarters (2 years)
ORDER BY cm.CohortPeriod, cm.QuartersFromStart;
```

---

# Business Question 3: Cross-Cohort Product Category Affinity and Evolution Analysis

## Intent

Analyze how product preferences and purchasing patterns differ across customer cohorts and evolve over their lifecycle. This provides insights into:
- Which product categories drive initial purchases for each cohort
- How product mix changes as cohorts mature
- Cross-selling and upselling opportunities by cohort stage
- Category affinity differences between acquisition periods
- Product adoption curves for new vs. established customers

Understanding these patterns helps tailor product recommendations, inventory planning, and marketing strategies to specific cohort stages and characteristics.

## SQL Code

```sql
WITH CustomerFirstPurchase AS (
    SELECT
        c.CustomerKey,
        MIN(dd.FullDateAlternateKey) AS FirstPurchaseDate,
        CAST(MIN(dd.CalendarYear) AS VARCHAR) || '-Q' ||
            CAST(MIN(dd.CalendarQuarter) AS VARCHAR) AS CohortPeriod,
        MIN(dd.CalendarYear) AS CohortYear,
        MIN(dd.CalendarQuarter) AS CohortQuarter
    FROM FactInternetSales fis
    INNER JOIN DimCustomer c ON fis.CustomerKey = c.CustomerKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    GROUP BY c.CustomerKey
),
CohortProductPurchases AS (
    SELECT
        cfp.CohortPeriod,
        cfp.CustomerKey,
        (dd.CalendarYear - cfp.CohortYear) * 4 +
        (dd.CalendarQuarter - cfp.CohortQuarter) AS QuartersFromStart,
        pc.EnglishProductCategoryName AS ProductCategory,
        psc.EnglishProductSubcategoryName AS ProductSubcategory,
        COUNT(DISTINCT fis.SalesOrderNumber) AS OrderCount,
        SUM(fis.OrderQuantity) AS QuantitySold,
        SUM(fis.SalesAmount) AS Revenue,
        COUNT(DISTINCT cfp.CustomerKey) AS UniqueCustomers
    FROM CustomerFirstPurchase cfp
    INNER JOIN FactInternetSales fis ON cfp.CustomerKey = fis.CustomerKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    INNER JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    INNER JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    GROUP BY
        cfp.CohortPeriod, cfp.CustomerKey,
        (dd.CalendarYear - cfp.CohortYear) * 4 + (dd.CalendarQuarter - cfp.CohortQuarter),
        pc.EnglishProductCategoryName, psc.EnglishProductSubcategoryName
),
CohortCategoryMetrics AS (
    SELECT
        CohortPeriod,
        QuartersFromStart,
        ProductCategory,
        ProductSubcategory,
        COUNT(DISTINCT CustomerKey) AS CustomersWhoBoug ht,
        SUM(OrderCount) AS TotalOrders,
        SUM(QuantitySold) AS TotalQuantity,
        SUM(Revenue) AS CategoryRevenue,
        AVG(Revenue) AS AvgRevenuePerCustomer
    FROM CohortProductPurchases
    GROUP BY CohortPeriod, QuartersFromStart, ProductCategory, ProductSubcategory
),
CohortTotals AS (
    SELECT
        CohortPeriod,
        QuartersFromStart,
        COUNT(DISTINCT CustomerKey) AS TotalActiveCustomers,
        SUM(Revenue) AS TotalPeriodRevenue
    FROM CohortProductPurchases
    GROUP BY CohortPeriod, QuartersFromStart
),
CategoryPenetration AS (
    SELECT
        ccm.CohortPeriod,
        ccm.QuartersFromStart,
        ccm.ProductCategory,
        ccm.ProductSubcategory,
        ccm.CustomersWhoBought,
        ct.TotalActiveCustomers,
        ROUND((CAST(ccm.CustomersWhoBought AS FLOAT) / ct.TotalActiveCustomers) * 100, 2) AS PenetrationPct,
        ccm.TotalOrders,
        ccm.TotalQuantity,
        ccm.CategoryRevenue,
        ROUND((ccm.CategoryRevenue / ct.TotalPeriodRevenue) * 100, 2) AS RevenueSharePct,
        ROUND(ccm.AvgRevenuePerCustomer, 2) AS AvgRevenuePerCustomer
    FROM CohortCategoryMetrics ccm
    INNER JOIN CohortTotals ct
        ON ccm.CohortPeriod = ct.CohortPeriod
        AND ccm.QuartersFromStart = ct.QuartersFromStart
)
SELECT
    CohortPeriod,
    QuartersFromStart,
    ProductCategory,
    ProductSubcategory,
    CustomersWhoBought,
    TotalActiveCustomers,
    PenetrationPct,
    TotalOrders,
    TotalQuantity,
    ROUND(CategoryRevenue, 2) AS CategoryRevenue,
    RevenueSharePct,
    AvgRevenuePerCustomer,
    RANK() OVER (
        PARTITION BY CohortPeriod, QuartersFromStart
        ORDER BY CategoryRevenue DESC
    ) AS CategoryRevenueRank
FROM CategoryPenetration
WHERE QuartersFromStart <= 6  -- First 6 quarters
ORDER BY CohortPeriod, QuartersFromStart, CategoryRevenue DESC;
```

---

# Business Question 4: Cohort Demographic and Behavioral Pattern Analysis

## Intent

Identify demographic and behavioral characteristics that define successful cohorts and high-value customer segments within cohorts. This comprehensive analysis examines:
- Demographic composition (income, education, occupation, geography) by cohort
- Correlation between customer attributes and lifetime value
- Identification of high-value customer profiles within each cohort
- Behavioral patterns including purchase frequency and basket characteristics
- Geographic concentration and sales territory performance by cohort

This insight enables targeted acquisition strategies, personalized marketing, and identification of ideal customer profiles for future campaigns.

## SQL Code

```sql
WITH CustomerFirstPurchase AS (
    SELECT
        c.CustomerKey,
        MIN(dd.FullDateAlternateKey) AS FirstPurchaseDate,
        CAST(MIN(dd.CalendarYear) AS VARCHAR) || '-Q' ||
            CAST(MIN(dd.CalendarQuarter) AS VARCHAR) AS CohortPeriod
    FROM FactInternetSales fis
    INNER JOIN DimCustomer c ON fis.CustomerKey = c.CustomerKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    GROUP BY c.CustomerKey
),
CustomerLifetimeMetrics AS (
    SELECT
        c.CustomerKey,
        cfp.CohortPeriod,
        c.Gender,
        c.MaritalStatus,
        c.YearlyIncome,
        c.EnglishEducation AS Education,
        c.EnglishOccupation AS Occupation,
        c.TotalChildren,
        c.NumberChildrenAtHome,
        c.HouseOwnerFlag,
        c.NumberCarsOwned,
        c.CommuteDistance,
        g.City,
        g.StateProvinceName,
        g.EnglishCountryRegionName AS Country,
        st.SalesTerritoryRegion,
        st.SalesTerritoryCountry,
        st.SalesTerritoryGroup,
        COUNT(DISTINCT fis.SalesOrderNumber) AS TotalOrders,
        SUM(fis.SalesAmount) AS LifetimeValue,
        AVG(fis.SalesAmount) AS AvgOrderValue,
        SUM(fis.OrderQuantity) AS TotalQuantity,
        COUNT(DISTINCT p.ProductSubcategoryKey) AS ProductDiversity,
        MIN(dd.FullDateAlternateKey) AS FirstOrderDate,
        MAX(dd.FullDateAlternateKey) AS LastOrderDate,
        COUNT(DISTINCT CAST(dd.CalendarYear AS VARCHAR) || '-' ||
              CAST(dd.CalendarQuarter AS VARCHAR)) AS ActiveQuarters
    FROM CustomerFirstPurchase cfp
    INNER JOIN DimCustomer c ON cfp.CustomerKey = c.CustomerKey
    INNER JOIN DimGeography g ON c.GeographyKey = g.GeographyKey
    INNER JOIN DimSalesTerritory st ON g.SalesTerritoryKey = st.SalesTerritoryKey
    INNER JOIN FactInternetSales fis ON c.CustomerKey = fis.CustomerKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    GROUP BY
        c.CustomerKey, cfp.CohortPeriod, c.Gender, c.MaritalStatus, c.YearlyIncome,
        c.EnglishEducation, c.EnglishOccupation, c.TotalChildren, c.NumberChildrenAtHome,
        c.HouseOwnerFlag, c.NumberCarsOwned, c.CommuteDistance,
        g.City, g.StateProvinceName, g.EnglishCountryRegionName,
        st.SalesTerritoryRegion, st.SalesTerritoryCountry, st.SalesTerritoryGroup
),
CustomerSegmentation AS (
    SELECT
        *,
        NTILE(4) OVER (PARTITION BY CohortPeriod ORDER BY LifetimeValue) AS LTVQuartile,
        NTILE(4) OVER (PARTITION BY CohortPeriod ORDER BY TotalOrders) AS FrequencyQuartile,
        CASE
            WHEN LifetimeValue >= (SELECT PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY LifetimeValue)
                                   FROM CustomerLifetimeMetrics)
            THEN 'High Value'
            WHEN LifetimeValue >= (SELECT PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY LifetimeValue)
                                   FROM CustomerLifetimeMetrics)
            THEN 'Medium Value'
            ELSE 'Low Value'
        END AS ValueSegment
    FROM CustomerLifetimeMetrics
),
CohortDemographicProfile AS (
    SELECT
        CohortPeriod,
        ValueSegment,
        COUNT(DISTINCT CustomerKey) AS CustomerCount,

        -- Revenue Metrics
        ROUND(AVG(LifetimeValue), 2) AS AvgLifetimeValue,
        ROUND(SUM(LifetimeValue), 2) AS TotalRevenue,
        ROUND(AVG(AvgOrderValue), 2) AS AvgOrderValue,
        ROUND(AVG(TotalOrders), 2) AS AvgOrdersPerCustomer,
        ROUND(AVG(ProductDiversity), 2) AS AvgProductDiversity,
        ROUND(AVG(ActiveQuarters), 2) AS AvgActiveQuarters,

        -- Demographics
        ROUND(AVG(CASE WHEN YearlyIncome IS NOT NULL THEN YearlyIncome ELSE 0 END), 2) AS AvgYearlyIncome,
        ROUND(SUM(CASE WHEN Gender = 'M' THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 2) AS PctMale,
        ROUND(SUM(CASE WHEN MaritalStatus = 'M' THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 2) AS PctMarried,
        ROUND(SUM(CASE WHEN HouseOwnerFlag = 'Y' THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 2) AS PctHomeowners,
        ROUND(AVG(CAST(TotalChildren AS FLOAT)), 2) AS AvgChildren,
        ROUND(AVG(CAST(NumberCarsOwned AS FLOAT)), 2) AS AvgCarsOwned,

        -- Top Demographics
        (SELECT Education FROM CustomerSegmentation cs2
         WHERE cs2.CohortPeriod = cs1.CohortPeriod AND cs2.ValueSegment = cs1.ValueSegment
         GROUP BY Education ORDER BY COUNT(*) DESC LIMIT 1) AS TopEducation,
        (SELECT Occupation FROM CustomerSegmentation cs2
         WHERE cs2.CohortPeriod = cs1.CohortPeriod AND cs2.ValueSegment = cs1.ValueSegment
         GROUP BY Occupation ORDER BY COUNT(*) DESC LIMIT 1) AS TopOccupation,
        (SELECT Country FROM CustomerSegmentation cs2
         WHERE cs2.CohortPeriod = cs1.CohortPeriod AND cs2.ValueSegment = cs1.ValueSegment
         GROUP BY Country ORDER BY COUNT(*) DESC LIMIT 1) AS TopCountry,
        (SELECT SalesTerritoryRegion FROM CustomerSegmentation cs2
         WHERE cs2.CohortPeriod = cs1.CohortPeriod AND cs2.ValueSegment = cs1.ValueSegment
         GROUP BY SalesTerritoryRegion ORDER BY COUNT(*) DESC LIMIT 1) AS TopSalesRegion

    FROM CustomerSegmentation cs1
    GROUP BY CohortPeriod, ValueSegment
)
SELECT
    CohortPeriod,
    ValueSegment,
    CustomerCount,
    TotalRevenue,
    AvgLifetimeValue,
    AvgOrderValue,
    AvgOrdersPerCustomer,
    AvgProductDiversity,
    AvgActiveQuarters,
    AvgYearlyIncome,
    PctMale,
    PctMarried,
    PctHomeowners,
    AvgChildren,
    AvgCarsOwned,
    TopEducation,
    TopOccupation,
    TopCountry,
    TopSalesRegion,
    RANK() OVER (PARTITION BY CohortPeriod ORDER BY TotalRevenue DESC) AS ValueSegmentRank
FROM CohortDemographicProfile
ORDER BY CohortPeriod, TotalRevenue DESC;
```

---

# Business Question 5: Cohort Churn, Reactivation, and Purchase Interval Analysis

## Intent

Analyze customer activity patterns within cohorts to identify churn risk, reactivation opportunities, and optimal engagement timing. This sophisticated temporal analysis provides:
- Identification of churned customers (no purchases in X months) by cohort
- Reactivation rates showing customers who return after periods of inactivity
- Average purchase interval (time between orders) by cohort and lifecycle stage
- Churn prediction signals based on increasing purchase intervals
- Win-back campaign opportunities and timing
- Cohort health scores based on activity patterns

Understanding these patterns enables proactive retention efforts, optimized remarketing campaigns, and improved customer lifecycle management strategies.

## SQL Code

```sql
WITH CustomerFirstPurchase AS (
    SELECT
        c.CustomerKey,
        MIN(dd.FullDateAlternateKey) AS FirstPurchaseDate,
        CAST(MIN(dd.CalendarYear) AS VARCHAR) || '-Q' ||
            CAST(MIN(dd.CalendarQuarter) AS VARCHAR) AS CohortPeriod
    FROM FactInternetSales fis
    INNER JOIN DimCustomer c ON fis.CustomerKey = c.CustomerKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    GROUP BY c.CustomerKey
),
CustomerPurchases AS (
    SELECT
        cfp.CustomerKey,
        cfp.CohortPeriod,
        cfp.FirstPurchaseDate,
        dd.FullDateAlternateKey AS PurchaseDate,
        fis.SalesOrderNumber,
        fis.SalesAmount,
        ROW_NUMBER() OVER (PARTITION BY cfp.CustomerKey ORDER BY dd.FullDateAlternateKey) AS PurchaseSequence
    FROM CustomerFirstPurchase cfp
    INNER JOIN FactInternetSales fis ON cfp.CustomerKey = fis.CustomerKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
),
PurchaseIntervals AS (
    SELECT
        cp1.CustomerKey,
        cp1.CohortPeriod,
        cp1.PurchaseSequence,
        cp1.PurchaseDate,
        cp2.PurchaseDate AS NextPurchaseDate,
        CAST(JULIANDAY(cp2.PurchaseDate) - JULIANDAY(cp1.PurchaseDate) AS INTEGER) AS DaysBetweenPurchases,
        cp1.SalesAmount
    FROM CustomerPurchases cp1
    LEFT JOIN CustomerPurchases cp2
        ON cp1.CustomerKey = cp2.CustomerKey
        AND cp2.PurchaseSequence = cp1.PurchaseSequence + 1
),
CustomerActivityMetrics AS (
    SELECT
        CustomerKey,
        CohortPeriod,
        COUNT(*) AS TotalPurchases,
        AVG(DaysBetweenPurchases) AS AvgDaysBetweenPurchases,
        MIN(DaysBetweenPurchases) AS MinDaysBetweenPurchases,
        MAX(DaysBetweenPurchases) AS MaxDaysBetweenPurchases,
        STDEV(DaysBetweenPurchases) AS StdDevDaysBetweenPurchases,
        MAX(PurchaseDate) AS LastPurchaseDate,
        MIN(PurchaseDate) AS FirstPurchaseDate,
        SUM(SalesAmount) AS TotalRevenue,
        CAST(JULIANDAY(DATE('now')) - JULIANDAY(MAX(PurchaseDate)) AS INTEGER) AS DaysSinceLastPurchase,
        CAST(JULIANDAY(MAX(PurchaseDate)) - JULIANDAY(MIN(PurchaseDate)) AS INTEGER) AS CustomerLifespanDays,
        -- Identify reactivations (purchases after 90+ day gaps)
        SUM(CASE WHEN DaysBetweenPurchases >= 90 THEN 1 ELSE 0 END) AS ReactivationCount
    FROM PurchaseIntervals
    WHERE DaysBetweenPurchases IS NOT NULL
    GROUP BY CustomerKey, CohortPeriod
),
CustomerStatus AS (
    SELECT
        *,
        CASE
            WHEN DaysSinceLastPurchase > 180 THEN 'Churned'
            WHEN DaysSinceLastPurchase > 90 THEN 'At Risk'
            WHEN DaysSinceLastPurchase > 60 THEN 'Cooling'
            ELSE 'Active'
        END AS CustomerStatus,
        CASE
            WHEN TotalPurchases = 1 THEN 'One-Time Buyer'
            WHEN TotalPurchases BETWEEN 2 AND 3 THEN 'Occasional'
            WHEN TotalPurchases BETWEEN 4 AND 10 THEN 'Regular'
            ELSE 'Frequent'
        END AS PurchaseFrequencySegment
    FROM CustomerActivityMetrics
),
CohortChurnAnalysis AS (
    SELECT
        CohortPeriod,
        CustomerStatus,
        PurchaseFrequencySegment,
        COUNT(DISTINCT CustomerKey) AS CustomerCount,
        ROUND(AVG(TotalPurchases), 2) AS AvgPurchaseCount,
        ROUND(AVG(AvgDaysBetweenPurchases), 2) AS AvgDaysBetweenPurchases,
        ROUND(AVG(MinDaysBetweenPurchases), 2) AS AvgMinInterval,
        ROUND(AVG(MaxDaysBetweenPurchases), 2) AS AvgMaxInterval,
        ROUND(AVG(DaysSinceLastPurchase), 2) AS AvgDaysSinceLastPurchase,
        ROUND(AVG(CustomerLifespanDays), 2) AS AvgCustomerLifespanDays,
        ROUND(SUM(TotalRevenue), 2) AS TotalRevenue,
        ROUND(AVG(TotalRevenue), 2) AS AvgRevenuePerCustomer,
        SUM(ReactivationCount) AS TotalReactivations,
        ROUND(AVG(CAST(ReactivationCount AS FLOAT)), 2) AS AvgReactivationsPerCustomer
    FROM CustomerStatus
    GROUP BY CohortPeriod, CustomerStatus, PurchaseFrequencySegment
),
CohortTotals AS (
    SELECT
        CohortPeriod,
        COUNT(DISTINCT CustomerKey) AS TotalCohortCustomers,
        SUM(TotalRevenue) AS TotalCohortRevenue
    FROM CustomerStatus
    GROUP BY CohortPeriod
)
SELECT
    cca.CohortPeriod,
    cca.CustomerStatus,
    cca.PurchaseFrequencySegment,
    cca.CustomerCount,
    ct.TotalCohortCustomers,
    ROUND((CAST(cca.CustomerCount AS FLOAT) / ct.TotalCohortCustomers) * 100, 2) AS PctOfCohort,
    cca.AvgPurchaseCount,
    cca.AvgDaysBetweenPurchases,
    cca.AvgMinInterval,
    cca.AvgMaxInterval,
    cca.AvgDaysSinceLastPurchase,
    cca.AvgCustomerLifespanDays,
    cca.TotalRevenue,
    ROUND((cca.TotalRevenue / ct.TotalCohortRevenue) * 100, 2) AS PctOfCohortRevenue,
    cca.AvgRevenuePerCustomer,
    cca.TotalReactivations,
    cca.AvgReactivationsPerCustomer,
    CASE
        WHEN cca.CustomerStatus = 'Churned' THEN 'High Priority - Win-Back Campaign'
        WHEN cca.CustomerStatus = 'At Risk' THEN 'Medium Priority - Retention Campaign'
        WHEN cca.CustomerStatus = 'Cooling' THEN 'Low Priority - Re-Engagement'
        ELSE 'Maintain Engagement'
    END AS RecommendedAction
FROM CohortChurnAnalysis cca
INNER JOIN CohortTotals ct ON cca.CohortPeriod = ct.CohortPeriod
ORDER BY cca.CohortPeriod, cca.TotalRevenue DESC;
```

---

## Summary

These five business questions provide a comprehensive framework for customer cohort analysis:

1. **Monthly Cohort Retention** - Understanding how cohorts perform over time with retention curves
2. **Lifetime Value Progression** - Tracking revenue accumulation and identifying high-value cohorts
3. **Product Category Affinity** - Analyzing product preferences and cross-selling opportunities by cohort stage
4. **Demographic Patterns** - Identifying characteristics of successful customer segments
5. **Churn and Reactivation** - Detecting at-risk customers and optimization engagement timing

Each query demonstrates advanced analytical techniques including:
- Cohort construction based on first purchase date
- Time-series analysis tracking cohort behavior over multiple periods
- Window functions for cumulative calculations and rankings
- Statistical aggregations (percentiles, standard deviations)
- Customer lifecycle stage identification
- Retention rate calculations
- Churn prediction and reactivation analysis

These analyses enable data-driven strategies for:
- Customer acquisition optimization (identifying ideal cohort characteristics)
- Retention program development (understanding when customers churn)
- Personalized marketing (tailoring messages by cohort stage)
- Lifetime value optimization (identifying high-value customer profiles)
- Product strategy (understanding evolving preferences)
- Resource allocation (focusing on high-performing cohorts)

The insights from cohort analysis provide a foundation for customer-centric business decisions and long-term growth strategies.
