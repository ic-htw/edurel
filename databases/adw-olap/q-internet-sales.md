# Analysis of Internet Sale Revenue - Business Questions

## Introduction

This document presents a comprehensive analysis of internet sales revenue using the AdventureWorks data warehouse. The analysis leverages a star/snowflake schema with FactInternetSales as the central fact table, connected to multiple dimension tables including DimProduct, DimCustomer, DimDate, DimGeography, DimPromotion, DimCurrency, and DimSalesTerritory.

The following business questions explore various aspects of internet sales performance, including temporal trends, product performance, customer behavior, promotional effectiveness, and geographic distribution. Each question is designed to provide actionable insights for business intelligence and strategic decision-making.

---

# Business Question 1: Product Category Revenue Performance with Year-over-Year Growth Analysis

## Intent

Analyze revenue performance across product categories and subcategories, showing both current year sales and year-over-year growth rates. This helps identify which product lines are growing or declining, enabling strategic inventory and marketing decisions. The analysis includes:
- Total sales amount by product category and subcategory
- Year-over-year revenue comparison
- Growth rate calculations
- Ranking of categories by revenue performance

This complex analysis requires joining through the product hierarchy (Product → ProductSubcategory → ProductCategory) and performing temporal comparisons using the date dimension.

## SQL Code

```sql
WITH CurrentYearSales AS (
    SELECT
        pc.EnglishProductCategoryName AS CategoryName,
        psc.EnglishProductSubcategoryName AS SubcategoryName,
        dd.CalendarYear,
        SUM(fis.SalesAmount) AS TotalRevenue,
        SUM(fis.OrderQuantity) AS TotalQuantity,
        COUNT(DISTINCT fis.SalesOrderNumber) AS OrderCount
    FROM FactInternetSales fis
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    INNER JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    INNER JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    WHERE dd.CalendarYear >= (SELECT MAX(CalendarYear) - 1 FROM DimDate WHERE DateKey IN (SELECT DISTINCT OrderDateKey FROM FactInternetSales))
    GROUP BY pc.EnglishProductCategoryName, psc.EnglishProductSubcategoryName, dd.CalendarYear
),
YoYComparison AS (
    SELECT
        curr.CategoryName,
        curr.SubcategoryName,
        curr.CalendarYear AS CurrentYear,
        curr.TotalRevenue AS CurrentYearRevenue,
        curr.TotalQuantity AS CurrentYearQuantity,
        curr.OrderCount AS CurrentYearOrders,
        prev.TotalRevenue AS PreviousYearRevenue,
        prev.TotalQuantity AS PreviousYearQuantity,
        CASE
            WHEN prev.TotalRevenue IS NOT NULL AND prev.TotalRevenue > 0
            THEN ((curr.TotalRevenue - prev.TotalRevenue) / prev.TotalRevenue) * 100
            ELSE NULL
        END AS RevenueGrowthPct,
        CASE
            WHEN prev.TotalQuantity IS NOT NULL AND prev.TotalQuantity > 0
            THEN ((curr.TotalQuantity - prev.TotalQuantity) / CAST(prev.TotalQuantity AS FLOAT)) * 100
            ELSE NULL
        END AS QuantityGrowthPct
    FROM CurrentYearSales curr
    LEFT JOIN CurrentYearSales prev
        ON curr.CategoryName = prev.CategoryName
        AND curr.SubcategoryName = prev.SubcategoryName
        AND curr.CalendarYear = prev.CalendarYear + 1
)
SELECT
    CategoryName,
    SubcategoryName,
    CurrentYear,
    ROUND(CurrentYearRevenue, 2) AS CurrentYearRevenue,
    CurrentYearQuantity,
    CurrentYearOrders,
    ROUND(PreviousYearRevenue, 2) AS PreviousYearRevenue,
    ROUND(RevenueGrowthPct, 2) AS RevenueGrowthPct,
    ROUND(QuantityGrowthPct, 2) AS QuantityGrowthPct,
    RANK() OVER (PARTITION BY CurrentYear ORDER BY CurrentYearRevenue DESC) AS RevenueRank
FROM YoYComparison
WHERE CurrentYear = (SELECT MAX(CurrentYear) FROM YoYComparison)
ORDER BY CurrentYearRevenue DESC;
```

---

# Business Question 2: Customer Geographic Revenue Distribution with Territory Performance Analysis

## Intent

Identify revenue distribution across geographic regions and sales territories, analyzing customer concentration and average order values by location. This analysis helps:
- Understand which markets generate the most revenue
- Identify high-value customers by region
- Analyze average transaction values across territories
- Determine customer penetration by geography

The query navigates the Customer → Geography → SalesTerritory hierarchy and aggregates sales metrics to provide a comprehensive geographic view of revenue performance.

## SQL Code

```sql
WITH CustomerRevenue AS (
    SELECT
        c.CustomerKey,
        CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
        c.YearlyIncome,
        g.City,
        g.StateProvinceName,
        g.EnglishCountryRegionName AS Country,
        st.SalesTerritoryRegion,
        st.SalesTerritoryCountry,
        st.SalesTerritoryGroup,
        SUM(fis.SalesAmount) AS TotalRevenue,
        SUM(fis.OrderQuantity) AS TotalQuantity,
        COUNT(DISTINCT fis.SalesOrderNumber) AS TotalOrders,
        AVG(fis.SalesAmount) AS AvgOrderValue,
        MIN(dd.FullDateAlternateKey) AS FirstPurchaseDate,
        MAX(dd.FullDateAlternateKey) AS LastPurchaseDate
    FROM FactInternetSales fis
    INNER JOIN DimCustomer c ON fis.CustomerKey = c.CustomerKey
    INNER JOIN DimGeography g ON c.GeographyKey = g.GeographyKey
    INNER JOIN DimSalesTerritory st ON g.SalesTerritoryKey = st.SalesTerritoryKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    GROUP BY
        c.CustomerKey, c.FirstName, c.LastName, c.YearlyIncome,
        g.City, g.StateProvinceName, g.EnglishCountryRegionName,
        st.SalesTerritoryRegion, st.SalesTerritoryCountry, st.SalesTerritoryGroup
),
TerritoryMetrics AS (
    SELECT
        SalesTerritoryGroup,
        SalesTerritoryCountry,
        SalesTerritoryRegion,
        COUNT(DISTINCT CustomerKey) AS CustomerCount,
        SUM(TotalRevenue) AS TerritoryRevenue,
        SUM(TotalOrders) AS TerritoryOrders,
        AVG(TotalRevenue) AS AvgRevenuePerCustomer,
        AVG(AvgOrderValue) AS AvgOrderValue,
        MAX(TotalRevenue) AS TopCustomerRevenue
    FROM CustomerRevenue
    GROUP BY SalesTerritoryGroup, SalesTerritoryCountry, SalesTerritoryRegion
)
SELECT
    tm.SalesTerritoryGroup,
    tm.SalesTerritoryCountry,
    tm.SalesTerritoryRegion,
    tm.CustomerCount,
    ROUND(tm.TerritoryRevenue, 2) AS TerritoryRevenue,
    tm.TerritoryOrders,
    ROUND(tm.AvgRevenuePerCustomer, 2) AS AvgRevenuePerCustomer,
    ROUND(tm.AvgOrderValue, 2) AS AvgOrderValue,
    ROUND(tm.TopCustomerRevenue, 2) AS TopCustomerRevenue,
    ROUND((tm.TerritoryRevenue / SUM(tm.TerritoryRevenue) OVER ()) * 100, 2) AS PctOfTotalRevenue,
    RANK() OVER (ORDER BY tm.TerritoryRevenue DESC) AS TerritoryRevenueRank
FROM TerritoryMetrics tm
ORDER BY tm.TerritoryRevenue DESC;
```

---

# Business Question 3: Promotion Effectiveness and Discount Impact Analysis

## Intent

Evaluate the effectiveness of promotional campaigns by comparing sales performance with and without promotions, analyzing discount impacts on revenue and order volumes. This analysis provides insights into:
- Revenue generated with vs. without promotions
- Average discount percentages and their impact on sales volume
- ROI of promotional campaigns
- Optimal discount levels for maximizing revenue

The query analyzes promotion types, discount levels, and their correlation with sales performance, helping optimize future promotional strategies.

## SQL Code

```sql
WITH PromotionSales AS (
    SELECT
        p.EnglishPromotionName AS PromotionName,
        p.EnglishPromotionType AS PromotionType,
        p.EnglishPromotionCategory AS PromotionCategory,
        p.DiscountPct AS PromotionDiscountPct,
        dd.CalendarYear,
        dd.CalendarQuarter,
        COUNT(DISTINCT fis.SalesOrderNumber) AS OrderCount,
        SUM(fis.OrderQuantity) AS TotalQuantity,
        SUM(fis.SalesAmount) AS TotalRevenue,
        SUM(fis.DiscountAmount) AS TotalDiscountAmount,
        AVG(fis.UnitPriceDiscountPct) AS AvgLineDiscountPct,
        SUM(fis.SalesAmount + fis.DiscountAmount) AS RevenueBeforeDiscount,
        AVG(fis.SalesAmount) AS AvgOrderValue
    FROM FactInternetSales fis
    INNER JOIN DimPromotion p ON fis.PromotionKey = p.PromotionKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    WHERE p.PromotionKey > 1  -- Exclude "No Discount" promotion
    GROUP BY
        p.EnglishPromotionName, p.EnglishPromotionType,
        p.EnglishPromotionCategory, p.DiscountPct,
        dd.CalendarYear, dd.CalendarQuarter
),
NoPromotionSales AS (
    SELECT
        dd.CalendarYear,
        dd.CalendarQuarter,
        COUNT(DISTINCT fis.SalesOrderNumber) AS OrderCount,
        SUM(fis.OrderQuantity) AS TotalQuantity,
        SUM(fis.SalesAmount) AS TotalRevenue,
        AVG(fis.SalesAmount) AS AvgOrderValue
    FROM FactInternetSales fis
    INNER JOIN DimPromotion p ON fis.PromotionKey = p.PromotionKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    WHERE p.PromotionKey = 1  -- "No Discount" promotion
    GROUP BY dd.CalendarYear, dd.CalendarQuarter
),
PromotionEffectiveness AS (
    SELECT
        ps.PromotionName,
        ps.PromotionType,
        ps.PromotionCategory,
        ps.PromotionDiscountPct,
        ps.CalendarYear,
        ps.CalendarQuarter,
        ps.OrderCount AS PromotionOrders,
        ps.TotalRevenue AS PromotionRevenue,
        ps.TotalDiscountAmount,
        ps.AvgOrderValue AS PromotionAvgOrderValue,
        nps.OrderCount AS NoPromotionOrders,
        nps.TotalRevenue AS NoPromotionRevenue,
        nps.AvgOrderValue AS NoPromotionAvgOrderValue,
        CASE
            WHEN nps.AvgOrderValue > 0
            THEN ((ps.AvgOrderValue - nps.AvgOrderValue) / nps.AvgOrderValue) * 100
            ELSE NULL
        END AS AvgOrderValueLiftPct,
        ps.RevenueBeforeDiscount - ps.TotalRevenue AS RevenueImpactOfDiscount,
        CASE
            WHEN ps.TotalDiscountAmount > 0
            THEN (ps.TotalRevenue - ps.TotalDiscountAmount) / ps.TotalDiscountAmount
            ELSE NULL
        END AS PromotionROI
    FROM PromotionSales ps
    LEFT JOIN NoPromotionSales nps
        ON ps.CalendarYear = nps.CalendarYear
        AND ps.CalendarQuarter = nps.CalendarQuarter
)
SELECT
    PromotionName,
    PromotionType,
    PromotionCategory,
    ROUND(PromotionDiscountPct * 100, 2) AS PromotionDiscountPct,
    CalendarYear,
    CalendarQuarter,
    PromotionOrders,
    ROUND(PromotionRevenue, 2) AS PromotionRevenue,
    ROUND(TotalDiscountAmount, 2) AS TotalDiscountAmount,
    ROUND(PromotionAvgOrderValue, 2) AS PromotionAvgOrderValue,
    ROUND(NoPromotionAvgOrderValue, 2) AS NoPromotionAvgOrderValue,
    ROUND(AvgOrderValueLiftPct, 2) AS AvgOrderValueLiftPct,
    ROUND(RevenueImpactOfDiscount, 2) AS RevenueImpactOfDiscount,
    ROUND(PromotionROI, 2) AS PromotionROI,
    RANK() OVER (PARTITION BY CalendarYear ORDER BY PromotionRevenue DESC) AS PromotionRevenueRank
FROM PromotionEffectiveness
WHERE CalendarYear = (SELECT MAX(CalendarYear) FROM PromotionEffectiveness)
ORDER BY PromotionRevenue DESC;
```

---

# Business Question 4: Revenue Seasonality and Monthly Trend Analysis with Moving Averages

## Intent

Analyze revenue patterns across time to identify seasonal trends, peak sales periods, and monthly performance variations. This complex temporal analysis includes:
- Month-over-month revenue comparisons
- 3-month moving averages to smooth out volatility
- Quarter-over-quarter growth rates
- Identification of peak and low sales periods
- Calendar vs. Fiscal year comparisons

This insight helps with demand forecasting, inventory planning, and resource allocation across different time periods.

## SQL Code

```sql
WITH MonthlySales AS (
    SELECT
        dd.CalendarYear,
        dd.CalendarQuarter,
        dd.MonthNumberOfYear,
        dd.EnglishMonthName AS MonthName,
        dd.FiscalYear,
        dd.FiscalQuarter,
        SUM(fis.SalesAmount) AS MonthlyRevenue,
        SUM(fis.OrderQuantity) AS MonthlyQuantity,
        COUNT(DISTINCT fis.SalesOrderNumber) AS MonthlyOrders,
        COUNT(DISTINCT fis.CustomerKey) AS UniqueCustomers,
        AVG(fis.SalesAmount) AS AvgOrderValue
    FROM FactInternetSales fis
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    GROUP BY
        dd.CalendarYear, dd.CalendarQuarter, dd.MonthNumberOfYear,
        dd.EnglishMonthName, dd.FiscalYear, dd.FiscalQuarter
),
MonthlyTrends AS (
    SELECT
        CalendarYear,
        CalendarQuarter,
        MonthNumberOfYear,
        MonthName,
        FiscalYear,
        FiscalQuarter,
        MonthlyRevenue,
        MonthlyQuantity,
        MonthlyOrders,
        UniqueCustomers,
        AvgOrderValue,
        LAG(MonthlyRevenue, 1) OVER (ORDER BY CalendarYear, MonthNumberOfYear) AS PrevMonthRevenue,
        LAG(MonthlyRevenue, 12) OVER (ORDER BY CalendarYear, MonthNumberOfYear) AS SameMonthPrevYearRevenue,
        AVG(MonthlyRevenue) OVER (
            ORDER BY CalendarYear, MonthNumberOfYear
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS ThreeMonthMovingAvg,
        AVG(MonthlyRevenue) OVER (PARTITION BY MonthNumberOfYear) AS HistoricalMonthAvg,
        SUM(MonthlyRevenue) OVER (
            PARTITION BY CalendarYear
            ORDER BY MonthNumberOfYear
        ) AS YearToDateRevenue
    FROM MonthlySales
),
SeasonalityMetrics AS (
    SELECT
        CalendarYear,
        CalendarQuarter,
        MonthNumberOfYear,
        MonthName,
        FiscalYear,
        FiscalQuarter,
        MonthlyRevenue,
        MonthlyOrders,
        UniqueCustomers,
        ROUND(AvgOrderValue, 2) AS AvgOrderValue,
        ROUND(ThreeMonthMovingAvg, 2) AS ThreeMonthMovingAvg,
        CASE
            WHEN PrevMonthRevenue > 0
            THEN ROUND(((MonthlyRevenue - PrevMonthRevenue) / PrevMonthRevenue) * 100, 2)
            ELSE NULL
        END AS MoMGrowthPct,
        CASE
            WHEN SameMonthPrevYearRevenue > 0
            THEN ROUND(((MonthlyRevenue - SameMonthPrevYearRevenue) / SameMonthPrevYearRevenue) * 100, 2)
            ELSE NULL
        END AS YoYGrowthPct,
        ROUND((MonthlyRevenue / HistoricalMonthAvg) * 100, 2) AS SeasonalityIndex,
        ROUND(YearToDateRevenue, 2) AS YearToDateRevenue,
        RANK() OVER (PARTITION BY CalendarYear ORDER BY MonthlyRevenue DESC) AS MonthRevenueRank
    FROM MonthlyTrends
)
SELECT
    CalendarYear,
    CalendarQuarter,
    MonthNumberOfYear,
    MonthName,
    FiscalYear,
    FiscalQuarter,
    ROUND(MonthlyRevenue, 2) AS MonthlyRevenue,
    MonthlyOrders,
    UniqueCustomers,
    AvgOrderValue,
    ThreeMonthMovingAvg,
    MoMGrowthPct,
    YoYGrowthPct,
    SeasonalityIndex,
    YearToDateRevenue,
    MonthRevenueRank
FROM SeasonalityMetrics
WHERE CalendarYear >= (SELECT MAX(CalendarYear) - 2 FROM SeasonalityMetrics)
ORDER BY CalendarYear DESC, MonthNumberOfYear;
```

---

# Business Question 5: Customer Lifetime Value and Purchase Behavior Segmentation

## Intent

Perform comprehensive customer segmentation based on purchasing behavior, lifetime value, and engagement patterns. This analysis enables:
- Identification of high-value customers
- Understanding of customer purchase frequency and recency
- Segmentation into customer tiers (VIP, regular, occasional)
- Analysis of cross-selling opportunities (product diversity)
- Customer retention insights based on purchase patterns

The query uses RFM (Recency, Frequency, Monetary) analysis combined with product purchase diversity to create actionable customer segments for targeted marketing and retention strategies.

## SQL Code

```sql
WITH CustomerPurchases AS (
    SELECT
        c.CustomerKey,
        CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
        c.EmailAddress,
        c.YearlyIncome,
        c.EnglishEducation AS Education,
        c.EnglishOccupation AS Occupation,
        c.Gender,
        c.MaritalStatus,
        c.TotalChildren,
        g.City,
        g.StateProvinceName,
        g.EnglishCountryRegionName AS Country,
        MIN(dd.FullDateAlternateKey) AS FirstPurchaseDate,
        MAX(dd.FullDateAlternateKey) AS LastPurchaseDate,
        COUNT(DISTINCT fis.SalesOrderNumber) AS TotalOrders,
        SUM(fis.SalesAmount) AS TotalRevenue,
        AVG(fis.SalesAmount) AS AvgOrderValue,
        SUM(fis.OrderQuantity) AS TotalQuantity,
        COUNT(DISTINCT p.ProductSubcategoryKey) AS ProductCategoryDiversity,
        COUNT(DISTINCT CAST(dd.CalendarYear AS VARCHAR) || '-' || CAST(dd.CalendarQuarter AS VARCHAR)) AS ActiveQuarters
    FROM FactInternetSales fis
    INNER JOIN DimCustomer c ON fis.CustomerKey = c.CustomerKey
    INNER JOIN DimGeography g ON c.GeographyKey = g.GeographyKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    GROUP BY
        c.CustomerKey, c.FirstName, c.LastName, c.EmailAddress,
        c.YearlyIncome, c.EnglishEducation, c.EnglishOccupation,
        c.Gender, c.MaritalStatus, c.TotalChildren,
        g.City, g.StateProvinceName, g.EnglishCountryRegionName
),
CustomerMetrics AS (
    SELECT
        *,
        CAST(JULIANDAY(DATE('now')) - JULIANDAY(LastPurchaseDate) AS INTEGER) AS DaysSinceLastPurchase,
        CAST(JULIANDAY(LastPurchaseDate) - JULIANDAY(FirstPurchaseDate) AS INTEGER) AS CustomerLifespanDays,
        CASE
            WHEN CAST(JULIANDAY(LastPurchaseDate) - JULIANDAY(FirstPurchaseDate) AS INTEGER) > 0
            THEN TotalOrders / (CAST(JULIANDAY(LastPurchaseDate) - JULIANDAY(FirstPurchaseDate) AS INTEGER) / 365.25)
            ELSE TotalOrders
        END AS OrdersPerYear
    FROM CustomerPurchases
),
RFMScores AS (
    SELECT
        *,
        NTILE(5) OVER (ORDER BY DaysSinceLastPurchase DESC) AS RecencyScore,
        NTILE(5) OVER (ORDER BY TotalOrders) AS FrequencyScore,
        NTILE(5) OVER (ORDER BY TotalRevenue) AS MonetaryScore
    FROM CustomerMetrics
),
CustomerSegmentation AS (
    SELECT
        *,
        RecencyScore + FrequencyScore + MonetaryScore AS RFMScore,
        CASE
            WHEN RecencyScore >= 4 AND FrequencyScore >= 4 AND MonetaryScore >= 4 THEN 'VIP Champions'
            WHEN RecencyScore >= 4 AND FrequencyScore >= 3 THEN 'Loyal Customers'
            WHEN RecencyScore >= 4 AND MonetaryScore >= 4 THEN 'Big Spenders'
            WHEN RecencyScore >= 3 AND FrequencyScore >= 3 AND MonetaryScore >= 3 THEN 'Potential Loyalists'
            WHEN RecencyScore <= 2 AND FrequencyScore >= 4 THEN 'At Risk'
            WHEN RecencyScore <= 2 AND FrequencyScore <= 2 THEN 'Lost Customers'
            WHEN RecencyScore >= 4 AND FrequencyScore <= 2 THEN 'New Customers'
            ELSE 'Regular Customers'
        END AS CustomerSegment
    FROM RFMScores
)
SELECT
    CustomerName,
    EmailAddress,
    Country,
    StateProvinceName,
    City,
    CustomerSegment,
    RFMScore,
    RecencyScore,
    FrequencyScore,
    MonetaryScore,
    ROUND(TotalRevenue, 2) AS LifetimeValue,
    TotalOrders,
    ROUND(AvgOrderValue, 2) AS AvgOrderValue,
    TotalQuantity,
    ProductCategoryDiversity,
    ActiveQuarters,
    DaysSinceLastPurchase,
    ROUND(OrdersPerYear, 2) AS OrdersPerYear,
    FirstPurchaseDate,
    LastPurchaseDate,
    YearlyIncome,
    Education,
    Occupation,
    Gender,
    MaritalStatus,
    TotalChildren,
    RANK() OVER (ORDER BY TotalRevenue DESC) AS RevenueRank,
    RANK() OVER (PARTITION BY CustomerSegment ORDER BY TotalRevenue DESC) AS SegmentRevenueRank
FROM CustomerSegmentation
ORDER BY TotalRevenue DESC;
```

---

## Summary

These five business questions provide a comprehensive framework for analyzing internet sales revenue from multiple perspectives:

1. **Product Performance** - Understanding which products drive revenue and growth
2. **Geographic Distribution** - Identifying key markets and regional opportunities
3. **Promotion Effectiveness** - Optimizing promotional strategies and discount levels
4. **Temporal Patterns** - Leveraging seasonality for better planning and forecasting
5. **Customer Segmentation** - Targeting high-value customers and improving retention

Each query demonstrates advanced SQL techniques including:
- Complex joins across multiple dimension tables
- Window functions (RANK, NTILE, LAG, moving averages)
- Common Table Expressions (CTEs) for query organization
- Aggregate functions with multiple grouping levels
- Calculated metrics and KPIs
- Conditional logic for segmentation and classification

These analyses can be further extended with additional filters, time periods, or dimensional slicing based on specific business requirements.
