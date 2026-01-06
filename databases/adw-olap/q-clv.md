# Customer Lifetime Value and Lifecycle Analysis

# Introduction

This document presents five complex business intelligence questions focused on customer lifetime value (CLV), lifecycle stage progression, and customer value optimization within the AdventureWorks data warehouse. These analyses examine Internet sales customers through multiple lenses including historical value calculation, predictive value modeling, behavioral segmentation, retention patterns, and growth trajectory analysis.

The queries leverage FactInternetSales transaction history along with customer demographic and behavioral attributes from DimCustomer to calculate comprehensive CLV metrics, identify high-value customer segments, predict churn risk, optimize acquisition and retention investments, and enable data-driven customer relationship management strategies. Advanced SQL techniques including cohort analysis, RFM segmentation, lifecycle modeling, and predictive scoring transform raw transaction data into actionable customer intelligence.

---

# Business Question 1: Comprehensive Customer Lifetime Value Calculation and Segmentation

## Intent

Calculate comprehensive customer lifetime value metrics including historical CLV, average order value, purchase frequency, customer tenure, and profitability contribution. Segment customers into value tiers (Platinum, Gold, Silver, Bronze) based on multi-dimensional scoring, and compare CLV across customer demographic segments to identify high-value customer profiles for targeted acquisition and retention strategies.

The query calculates:
- Historical CLV (total revenue and profit per customer)
- Purchase behavior metrics (frequency, recency, average order value)
- Customer tenure and relationship duration
- CLV per year and per month ratios
- Multi-factor customer value scoring and tiering
- Demographic profile analysis by value tier

## SQL Code

```sql
WITH CustomerFirstLastPurchase AS (
    SELECT
        fis.CustomerKey,
        MIN(fis.OrderDate) AS FirstPurchaseDate,
        MAX(fis.OrderDate) AS LastPurchaseDate,
        COUNT(DISTINCT fis.SalesOrderNumber) AS TotalOrders,
        COUNT(*) AS TotalLineItems,
        CAST(JULIANDAY(MAX(fis.OrderDate)) - JULIANDAY(MIN(fis.OrderDate)) AS INTEGER) AS CustomerTenureDays
    FROM FactInternetSales fis
    GROUP BY fis.CustomerKey
),

CustomerLifetimeMetrics AS (
    SELECT
        fis.CustomerKey,
        c.FirstName || ' ' || c.LastName AS CustomerName,
        c.YearlyIncome,
        c.EnglishEducation AS Education,
        c.EnglishOccupation AS Occupation,
        c.Gender,
        c.MaritalStatus,
        c.TotalChildren,
        c.NumberCarsOwned,
        c.HouseOwnerFlag,
        g.EnglishCountryRegionName AS Country,
        g.StateProvinceName AS State,
        g.City,
        st.SalesTerritoryRegion,
        cflp.FirstPurchaseDate,
        cflp.LastPurchaseDate,
        cflp.CustomerTenureDays,
        ROUND(cflp.CustomerTenureDays / 365.25, 2) AS CustomerTenureYears,
        CAST(JULIANDAY('now') - JULIANDAY(cflp.LastPurchaseDate) AS INTEGER) AS DaysSinceLastPurchase,
        cflp.TotalOrders,
        cflp.TotalLineItems,
        COUNT(DISTINCT DATE(fis.OrderDate)) AS UniquePurchaseDays,
        SUM(fis.OrderQuantity) AS TotalUnits,
        ROUND(SUM(fis.SalesAmount), 2) AS LifetimeRevenue,
        ROUND(SUM(fis.SalesAmount - fis.TotalProductCost), 2) AS LifetimeGrossProfit,
        ROUND(100.0 * SUM(fis.SalesAmount - fis.TotalProductCost) / NULLIF(SUM(fis.SalesAmount), 0), 2) AS LifetimeMarginPct,
        ROUND(AVG(fis.SalesAmount), 2) AS AvgLineItemValue,
        ROUND(SUM(fis.SalesAmount) / NULLIF(cflp.TotalOrders, 0), 2) AS AvgOrderValue,
        ROUND(SUM(fis.DiscountAmount), 2) AS TotalDiscounts,
        ROUND(100.0 * SUM(fis.DiscountAmount) / NULLIF(SUM(fis.SalesAmount + fis.DiscountAmount), 0), 2) AS AvgDiscountPct,
        COUNT(DISTINCT pc.EnglishProductCategoryName) AS UniqueCategories,
        COUNT(DISTINCT fis.ProductKey) AS UniqueProducts
    FROM FactInternetSales fis
    INNER JOIN CustomerFirstLastPurchase cflp ON fis.CustomerKey = cflp.CustomerKey
    INNER JOIN DimCustomer c ON fis.CustomerKey = c.CustomerKey
    INNER JOIN DimGeography g ON c.GeographyKey = g.GeographyKey
    INNER JOIN DimSalesTerritory st ON g.SalesTerritoryKey = st.SalesTerritoryKey
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    GROUP BY fis.CustomerKey, c.FirstName, c.LastName, c.YearlyIncome, c.EnglishEducation,
             c.EnglishOccupation, c.Gender, c.MaritalStatus, c.TotalChildren, c.NumberCarsOwned,
             c.HouseOwnerFlag, g.EnglishCountryRegionName, g.StateProvinceName, g.City,
             st.SalesTerritoryRegion, cflp.FirstPurchaseDate, cflp.LastPurchaseDate,
             cflp.CustomerTenureDays, cflp.TotalOrders, cflp.TotalLineItems
),

CustomerValueMetrics AS (
    SELECT
        clm.*,
        -- Annualized metrics
        ROUND(clm.LifetimeRevenue / NULLIF(clm.CustomerTenureYears, 0), 2) AS RevenuePerYear,
        ROUND(clm.LifetimeGrossProfit / NULLIF(clm.CustomerTenureYears, 0), 2) AS ProfitPerYear,
        ROUND(clm.TotalOrders / NULLIF(clm.CustomerTenureYears, 0), 2) AS OrdersPerYear,
        -- Purchase frequency (days between orders)
        ROUND(clm.CustomerTenureDays / NULLIF(clm.TotalOrders - 1, 0), 2) AS AvgDaysBetweenOrders,
        -- Customer activity ratio (purchase days / tenure days)
        ROUND(100.0 * clm.UniquePurchaseDays / NULLIF(clm.CustomerTenureDays, 0), 2) AS ActivityRatioPct,
        -- Recency score (0-100, higher is better/more recent)
        CASE
            WHEN clm.DaysSinceLastPurchase <= 30 THEN 100
            WHEN clm.DaysSinceLastPurchase <= 90 THEN 80
            WHEN clm.DaysSinceLastPurchase <= 180 THEN 60
            WHEN clm.DaysSinceLastPurchase <= 365 THEN 40
            WHEN clm.DaysSinceLastPurchase <= 730 THEN 20
            ELSE 0
        END AS RecencyScore,
        -- Frequency quintile (relative to other customers)
        NTILE(5) OVER (ORDER BY clm.TotalOrders DESC) AS FrequencyQuintile,
        -- Monetary quintile (relative to other customers)
        NTILE(5) OVER (ORDER BY clm.LifetimeRevenue DESC) AS MonetaryQuintile
    FROM CustomerLifetimeMetrics clm
),

CustomerValueScoring AS (
    SELECT
        cvm.*,
        -- Comprehensive value score (0-100)
        ROUND(
            (cvm.MonetaryQuintile * 20) +  -- Revenue contribution (40%)
            (cvm.FrequencyQuintile * 16) +  -- Purchase frequency (32%)
            (cvm.RecencyScore * 0.20) +     -- Recency (20%)
            (CASE WHEN cvm.LifetimeMarginPct > 30 THEN 8 ELSE cvm.LifetimeMarginPct * 0.267 END) -- Profitability (8%)
        , 2) AS CustomerValueScore,
        RANK() OVER (ORDER BY cvm.LifetimeRevenue DESC) AS RevenueRank,
        RANK() OVER (ORDER BY cvm.LifetimeGrossProfit DESC) AS ProfitRank
    FROM CustomerValueMetrics cvm
),

CustomerTiering AS (
    SELECT
        cvs.*,
        CASE
            WHEN cvs.CustomerValueScore >= 80 THEN 'Platinum'
            WHEN cvs.CustomerValueScore >= 60 THEN 'Gold'
            WHEN cvs.CustomerValueScore >= 40 THEN 'Silver'
            ELSE 'Bronze'
        END AS CustomerTier,
        CASE
            WHEN cvs.RevenueRank <= (SELECT COUNT(*) * 0.01 FROM CustomerValueScoring) THEN 'Top 1%'
            WHEN cvs.RevenueRank <= (SELECT COUNT(*) * 0.05 FROM CustomerValueScoring) THEN 'Top 5%'
            WHEN cvs.RevenueRank <= (SELECT COUNT(*) * 0.10 FROM CustomerValueScoring) THEN 'Top 10%'
            WHEN cvs.RevenueRank <= (SELECT COUNT(*) * 0.25 FROM CustomerValueScoring) THEN 'Top 25%'
            ELSE 'Below Top 25%'
        END AS RevenuePercentile
    FROM CustomerValueScoring cvs
),

DemographicByTier AS (
    SELECT
        ct.CustomerTier,
        COUNT(*) AS CustomerCount,
        ROUND(AVG(ct.YearlyIncome), 2) AS AvgYearlyIncome,
        ROUND(AVG(ct.LifetimeRevenue), 2) AS AvgLifetimeRevenue,
        ROUND(AVG(ct.LifetimeGrossProfit), 2) AS AvgLifetimeGrossProfit,
        ROUND(AVG(ct.CustomerTenureYears), 2) AS AvgTenureYears,
        ROUND(AVG(ct.TotalOrders), 2) AS AvgTotalOrders,
        ROUND(AVG(ct.AvgOrderValue), 2) AS AvgOrderValue,
        ROUND(AVG(ct.DaysSinceLastPurchase), 2) AS AvgDaysSinceLastPurchase,
        ROUND(SUM(ct.LifetimeRevenue), 2) AS TotalTierRevenue,
        ROUND(100.0 * SUM(ct.LifetimeRevenue) / (SELECT SUM(LifetimeRevenue) FROM CustomerTiering), 2) AS TierRevenueSharePct,
        MODE() WITHIN GROUP (ORDER BY ct.Education) AS MostCommonEducation,
        MODE() WITHIN GROUP (ORDER BY ct.Occupation) AS MostCommonOccupation
    FROM CustomerTiering ct
    GROUP BY ct.CustomerTier
)

SELECT
    ct.CustomerKey,
    ct.CustomerName,
    ct.CustomerTier,
    ct.RevenuePercentile,
    ct.CustomerValueScore,
    ct.Country,
    ct.State,
    ct.SalesTerritoryRegion,
    ct.YearlyIncome,
    ct.Education,
    ct.Occupation,
    ct.Gender,
    ct.MaritalStatus,
    ct.FirstPurchaseDate,
    ct.LastPurchaseDate,
    ct.CustomerTenureYears,
    ct.DaysSinceLastPurchase,
    ct.TotalOrders,
    ct.LifetimeRevenue,
    ct.LifetimeGrossProfit,
    ct.LifetimeMarginPct,
    ct.AvgOrderValue,
    ct.AvgLineItemValue,
    ct.RevenuePerYear,
    ct.ProfitPerYear,
    ct.OrdersPerYear,
    ct.AvgDaysBetweenOrders,
    ct.TotalDiscounts,
    ct.AvgDiscountPct,
    ct.UniqueCategories,
    ct.UniqueProducts,
    ct.RecencyScore,
    ct.FrequencyQuintile,
    ct.MonetaryQuintile,
    ct.RevenueRank,
    ct.ProfitRank
FROM CustomerTiering ct
ORDER BY ct.CustomerValueScore DESC, ct.LifetimeRevenue DESC;
```

---

# Business Question 2: RFM Segmentation and Targeted Marketing Strategy

## Intent

Implement comprehensive RFM (Recency, Frequency, Monetary) analysis to segment customers into actionable marketing segments. This classic customer segmentation approach identifies Champions, Loyal Customers, At-Risk customers, and Lost customers, enabling targeted retention campaigns, win-back strategies, and loyalty program optimization based on behavioral patterns.

The query calculates:
- RFM scores (1-5 scale for each dimension)
- Combined RFM segments with business labels
- Segment-specific characteristics and profitability
- Recommended marketing actions per segment
- Segment migration opportunities and risks

## SQL Code

```sql
WITH CustomerPurchaseHistory AS (
    SELECT
        fis.CustomerKey,
        MIN(fis.OrderDate) AS FirstPurchaseDate,
        MAX(fis.OrderDate) AS LastPurchaseDate,
        COUNT(DISTINCT fis.SalesOrderNumber) AS TotalOrders,
        CAST(JULIANDAY('now') - JULIANDAY(MAX(fis.OrderDate)) AS INTEGER) AS DaysSinceLastPurchase,
        CAST(JULIANDAY(MAX(fis.OrderDate)) - JULIANDAY(MIN(fis.OrderDate)) AS INTEGER) AS CustomerTenureDays,
        ROUND(SUM(fis.SalesAmount), 2) AS TotalRevenue,
        ROUND(SUM(fis.SalesAmount - fis.TotalProductCost), 2) AS TotalGrossProfit,
        ROUND(AVG(fis.SalesAmount), 2) AS AvgTransactionValue
    FROM FactInternetSales fis
    GROUP BY fis.CustomerKey
),

RFMScores AS (
    SELECT
        cph.CustomerKey,
        c.FirstName || ' ' || c.LastName AS CustomerName,
        c.YearlyIncome,
        c.EnglishEducation AS Education,
        c.EnglishOccupation AS Occupation,
        g.EnglishCountryRegionName AS Country,
        st.SalesTerritoryRegion,
        cph.FirstPurchaseDate,
        cph.LastPurchaseDate,
        cph.DaysSinceLastPurchase,
        cph.CustomerTenureDays,
        cph.TotalOrders,
        cph.TotalRevenue,
        cph.TotalGrossProfit,
        cph.AvgTransactionValue,
        -- Recency Score (1-5, 5 is best/most recent)
        CASE
            WHEN cph.DaysSinceLastPurchase <= 60 THEN 5
            WHEN cph.DaysSinceLastPurchase <= 120 THEN 4
            WHEN cph.DaysSinceLastPurchase <= 240 THEN 3
            WHEN cph.DaysSinceLastPurchase <= 480 THEN 2
            ELSE 1
        END AS RecencyScore,
        -- Frequency Score (1-5, 5 is best/most frequent)
        NTILE(5) OVER (ORDER BY cph.TotalOrders ASC) AS FrequencyScore,
        -- Monetary Score (1-5, 5 is best/highest value)
        NTILE(5) OVER (ORDER BY cph.TotalRevenue ASC) AS MonetaryScore
    FROM CustomerPurchaseHistory cph
    INNER JOIN DimCustomer c ON cph.CustomerKey = c.CustomerKey
    INNER JOIN DimGeography g ON c.GeographyKey = g.GeographyKey
    INNER JOIN DimSalesTerritory st ON g.SalesTerritoryKey = st.SalesTerritoryKey
),

RFMSegmentation AS (
    SELECT
        rfm.*,
        -- Combined RFM score (concatenated for segment definition)
        CAST(rfm.RecencyScore AS TEXT) || CAST(rfm.FrequencyScore AS TEXT) || CAST(rfm.MonetaryScore AS TEXT) AS RFMString,
        -- Average RFM score
        ROUND((rfm.RecencyScore + rfm.FrequencyScore + rfm.MonetaryScore) / 3.0, 2) AS AvgRFMScore,
        -- Segment classification based on RFM patterns
        CASE
            -- Champions: High R, F, M
            WHEN rfm.RecencyScore >= 4 AND rfm.FrequencyScore >= 4 AND rfm.MonetaryScore >= 4 THEN 'Champions'
            -- Loyal Customers: High F, M but moderate R
            WHEN rfm.FrequencyScore >= 4 AND rfm.MonetaryScore >= 4 AND rfm.RecencyScore >= 3 THEN 'Loyal Customers'
            -- Potential Loyalists: Recent, moderate frequency and monetary
            WHEN rfm.RecencyScore >= 4 AND rfm.FrequencyScore >= 3 AND rfm.MonetaryScore >= 3 THEN 'Potential Loyalists'
            -- New Customers: High recency, low frequency
            WHEN rfm.RecencyScore >= 4 AND rfm.FrequencyScore <= 2 THEN 'New Customers'
            -- Promising: Recent, low-moderate F and M
            WHEN rfm.RecencyScore >= 4 AND rfm.FrequencyScore <= 3 AND rfm.MonetaryScore <= 3 THEN 'Promising'
            -- Need Attention: Moderate across board
            WHEN rfm.RecencyScore = 3 AND rfm.FrequencyScore >= 3 AND rfm.MonetaryScore >= 3 THEN 'Need Attention'
            -- About To Sleep: Declining recency, was active
            WHEN rfm.RecencyScore = 2 AND rfm.FrequencyScore >= 3 AND rfm.MonetaryScore >= 3 THEN 'About To Sleep'
            -- At Risk: Low recency, was valuable
            WHEN rfm.RecencyScore <= 2 AND rfm.FrequencyScore >= 4 AND rfm.MonetaryScore >= 4 THEN 'At Risk'
            -- Cannot Lose Them: Lowest recency, high historical value
            WHEN rfm.RecencyScore = 1 AND rfm.FrequencyScore >= 4 AND rfm.MonetaryScore >= 4 THEN 'Cannot Lose Them'
            -- Hibernating: Low recency, moderate F and M
            WHEN rfm.RecencyScore <= 2 AND rfm.FrequencyScore <= 3 AND rfm.MonetaryScore <= 3 THEN 'Hibernating'
            -- Lost: Lowest across all dimensions
            WHEN rfm.RecencyScore = 1 AND rfm.FrequencyScore <= 2 AND rfm.MonetaryScore <= 2 THEN 'Lost'
            ELSE 'Others'
        END AS RFMSegment
    FROM RFMScores rfm
),

SegmentCharacteristics AS (
    SELECT
        rfms.RFMSegment,
        COUNT(*) AS CustomerCount,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM RFMSegmentation), 2) AS SegmentPct,
        ROUND(AVG(rfms.RecencyScore), 2) AS AvgRecencyScore,
        ROUND(AVG(rfms.FrequencyScore), 2) AS AvgFrequencyScore,
        ROUND(AVG(rfms.MonetaryScore), 2) AS AvgMonetaryScore,
        ROUND(AVG(rfms.DaysSinceLastPurchase), 0) AS AvgDaysSinceLastPurchase,
        ROUND(AVG(rfms.TotalOrders), 2) AS AvgTotalOrders,
        ROUND(AVG(rfms.TotalRevenue), 2) AS AvgLifetimeRevenue,
        ROUND(AVG(rfms.TotalGrossProfit), 2) AS AvgLifetimeProfit,
        ROUND(SUM(rfms.TotalRevenue), 2) AS TotalSegmentRevenue,
        ROUND(100.0 * SUM(rfms.TotalRevenue) / (SELECT SUM(TotalRevenue) FROM RFMSegmentation), 2) AS RevenueSharePct,
        ROUND(AVG(rfms.YearlyIncome), 2) AS AvgYearlyIncome,
        MIN(rfms.TotalRevenue) AS MinLifetimeRevenue,
        MAX(rfms.TotalRevenue) AS MaxLifetimeRevenue
    FROM RFMSegmentation rfms
    GROUP BY rfms.RFMSegment
),

MarketingRecommendations AS (
    SELECT
        rfms.CustomerKey,
        rfms.CustomerName,
        rfms.RFMSegment,
        rfms.RecencyScore,
        rfms.FrequencyScore,
        rfms.MonetaryScore,
        rfms.AvgRFMScore,
        rfms.DaysSinceLastPurchase,
        rfms.TotalOrders,
        rfms.TotalRevenue,
        rfms.TotalGrossProfit,
        rfms.Country,
        rfms.SalesTerritoryRegion,
        rfms.YearlyIncome,
        -- Marketing action recommendations
        CASE
            WHEN rfms.RFMSegment = 'Champions' THEN 'Reward with VIP benefits, early access, exclusive offers'
            WHEN rfms.RFMSegment = 'Loyal Customers' THEN 'Upsell premium products, loyalty program, referral incentives'
            WHEN rfms.RFMSegment = 'Potential Loyalists' THEN 'Nurture with membership offers, personalized recommendations'
            WHEN rfms.RFMSegment = 'New Customers' THEN 'Onboarding campaigns, product education, welcome discounts'
            WHEN rfms.RFMSegment = 'Promising' THEN 'Cross-sell campaigns, bundle offers, engagement emails'
            WHEN rfms.RFMSegment = 'Need Attention' THEN 'Re-engagement campaigns, limited-time offers, feedback surveys'
            WHEN rfms.RFMSegment = 'About To Sleep' THEN 'Win-back campaigns, personalized discounts, reminder emails'
            WHEN rfms.RFMSegment = 'At Risk' THEN 'Urgent win-back offers, satisfaction surveys, retention discounts'
            WHEN rfms.RFMSegment = 'Cannot Lose Them' THEN 'HIGH PRIORITY: Executive outreach, special recovery offers'
            WHEN rfms.RFMSegment = 'Hibernating' THEN 'Low-cost reactivation, seasonal promotions, product updates'
            WHEN rfms.RFMSegment = 'Lost' THEN 'Minimal investment, brand awareness only, or exclude from campaigns'
            ELSE 'Standard marketing communications'
        END AS MarketingAction,
        -- Priority level
        CASE
            WHEN rfms.RFMSegment IN ('Champions', 'Loyal Customers', 'Cannot Lose Them') THEN 'High Priority'
            WHEN rfms.RFMSegment IN ('Potential Loyalists', 'At Risk', 'Need Attention') THEN 'Medium Priority'
            WHEN rfms.RFMSegment IN ('New Customers', 'Promising', 'About To Sleep') THEN 'Moderate Priority'
            ELSE 'Low Priority'
        END AS MarketingPriority,
        -- Expected ROI category
        CASE
            WHEN rfms.RFMSegment IN ('Champions', 'Loyal Customers', 'Potential Loyalists') THEN 'High ROI Expected'
            WHEN rfms.RFMSegment IN ('New Customers', 'Promising', 'At Risk', 'Cannot Lose Them') THEN 'Medium ROI Expected'
            ELSE 'Low ROI Expected'
        END AS ExpectedROI
    FROM RFMSegmentation rfms
)

SELECT
    mr.CustomerKey,
    mr.CustomerName,
    mr.RFMSegment,
    mr.RecencyScore,
    mr.FrequencyScore,
    mr.MonetaryScore,
    mr.AvgRFMScore,
    mr.DaysSinceLastPurchase,
    mr.TotalOrders,
    mr.TotalRevenue,
    mr.TotalGrossProfit,
    mr.Country,
    mr.SalesTerritoryRegion,
    mr.YearlyIncome,
    mr.MarketingAction,
    mr.MarketingPriority,
    mr.ExpectedROI
FROM MarketingRecommendations mr
ORDER BY
    CASE mr.RFMSegment
        WHEN 'Champions' THEN 1
        WHEN 'Loyal Customers' THEN 2
        WHEN 'Cannot Lose Them' THEN 3
        WHEN 'At Risk' THEN 4
        WHEN 'Potential Loyalists' THEN 5
        WHEN 'Need Attention' THEN 6
        WHEN 'About To Sleep' THEN 7
        WHEN 'New Customers' THEN 8
        WHEN 'Promising' THEN 9
        WHEN 'Hibernating' THEN 10
        WHEN 'Lost' THEN 11
        ELSE 12
    END,
    mr.TotalRevenue DESC;
```

---

# Business Question 3: Customer Lifecycle Stage Progression and Maturity Analysis

## Intent

Analyze customer progression through lifecycle stages from acquisition to maturity, identifying stage transition patterns, time-to-value metrics, and stage-specific characteristics. This analysis enables lifecycle marketing optimization, identifies bottlenecks in customer development, and reveals opportunities to accelerate customers through the value curve from new buyers to loyal advocates.

The query calculates:
- Lifecycle stage assignment (New, Developing, Growing, Mature, At-Risk, Churned)
- Stage-specific metrics and behaviors
- Time spent in each stage and progression rates
- Stage transition probabilities and patterns
- Revenue and profitability by lifecycle stage

## SQL Code

```sql
WITH CustomerPurchaseTimeline AS (
    SELECT
        fis.CustomerKey,
        fis.OrderDate,
        fis.SalesOrderNumber,
        fis.SalesAmount,
        fis.SalesAmount - fis.TotalProductCost AS GrossProfit,
        ROW_NUMBER() OVER (PARTITION BY fis.CustomerKey ORDER BY fis.OrderDate) AS PurchaseSequence,
        COUNT(DISTINCT fis.SalesOrderNumber) OVER (PARTITION BY fis.CustomerKey ORDER BY fis.OrderDate) AS CumulativeOrders,
        SUM(fis.SalesAmount) OVER (PARTITION BY fis.CustomerKey ORDER BY fis.OrderDate) AS CumulativeRevenue,
        LAG(fis.OrderDate) OVER (PARTITION BY fis.CustomerKey ORDER BY fis.OrderDate) AS PreviousOrderDate,
        CAST(JULIANDAY(fis.OrderDate) - JULIANDAY(LAG(fis.OrderDate) OVER (PARTITION BY fis.CustomerKey ORDER BY fis.OrderDate)) AS INTEGER) AS DaysSincePreviousOrder
    FROM FactInternetSales fis
),

CustomerCurrentState AS (
    SELECT
        cpt.CustomerKey,
        MIN(cpt.OrderDate) AS FirstPurchaseDate,
        MAX(cpt.OrderDate) AS LastPurchaseDate,
        CAST(JULIANDAY('now') - JULIANDAY(MIN(cpt.OrderDate)) AS INTEGER) AS CustomerAgeDays,
        CAST(JULIANDAY('now') - JULIANDAY(MAX(cpt.OrderDate)) AS INTEGER) AS DaysSinceLastPurchase,
        CAST(JULIANDAY(MAX(cpt.OrderDate)) - JULIANDAY(MIN(cpt.OrderDate)) AS INTEGER) AS ActiveLifespanDays,
        COUNT(DISTINCT cpt.SalesOrderNumber) AS TotalOrders,
        MAX(cpt.CumulativeOrders) AS MaxOrders,
        ROUND(SUM(cpt.SalesAmount), 2) AS TotalRevenue,
        ROUND(SUM(cpt.GrossProfit), 2) AS TotalGrossProfit,
        ROUND(AVG(cpt.SalesAmount), 2) AS AvgTransactionValue,
        ROUND(AVG(cpt.DaysSincePreviousOrder), 2) AS AvgDaysBetweenOrders,
        ROUND(CAST(JULIANDAY(MAX(cpt.OrderDate)) - JULIANDAY(MIN(cpt.OrderDate)) AS REAL) / NULLIF(COUNT(DISTINCT cpt.SalesOrderNumber) - 1, 0), 2) AS AvgPurchaseCycleDays
    FROM CustomerPurchaseTimeline cpt
    GROUP BY cpt.CustomerKey
),

LifecycleStageAssignment AS (
    SELECT
        ccs.CustomerKey,
        c.FirstName || ' ' || c.LastName AS CustomerName,
        c.YearlyIncome,
        c.EnglishEducation AS Education,
        c.EnglishOccupation AS Occupation,
        g.EnglishCountryRegionName AS Country,
        st.SalesTerritoryRegion,
        ccs.FirstPurchaseDate,
        ccs.LastPurchaseDate,
        ccs.CustomerAgeDays,
        ROUND(ccs.CustomerAgeDays / 365.25, 2) AS CustomerAgeYears,
        ccs.DaysSinceLastPurchase,
        ccs.ActiveLifespanDays,
        ccs.TotalOrders,
        ccs.TotalRevenue,
        ccs.TotalGrossProfit,
        ccs.AvgTransactionValue,
        ccs.AvgDaysBetweenOrders,
        ccs.AvgPurchaseCycleDays,
        -- Lifecycle Stage Logic
        CASE
            -- Churned: No purchase in over 1 year
            WHEN ccs.DaysSinceLastPurchase > 365 THEN 'Churned'
            -- At-Risk: No purchase in 6-12 months, had been active
            WHEN ccs.DaysSinceLastPurchase > 180 AND ccs.TotalOrders >= 3 THEN 'At-Risk'
            -- New: Less than 90 days old, 1-2 orders
            WHEN ccs.CustomerAgeDays <= 90 AND ccs.TotalOrders <= 2 THEN 'New'
            -- Developing: 90-180 days old OR 2-4 orders
            WHEN (ccs.CustomerAgeDays BETWEEN 91 AND 180) OR (ccs.TotalOrders BETWEEN 2 AND 4) THEN 'Developing'
            -- Growing: 180-365 days old OR 5-10 orders
            WHEN (ccs.CustomerAgeDays BETWEEN 181 AND 365) OR (ccs.TotalOrders BETWEEN 5 AND 10) THEN 'Growing'
            -- Mature: Over 1 year old AND 11+ orders
            WHEN ccs.CustomerAgeDays > 365 AND ccs.TotalOrders >= 11 AND ccs.DaysSinceLastPurchase <= 180 THEN 'Mature'
            -- Inactive: Doesn't fit other categories, low engagement
            ELSE 'Inactive'
        END AS LifecycleStage
    FROM CustomerCurrentState ccs
    INNER JOIN DimCustomer c ON ccs.CustomerKey = c.CustomerKey
    INNER JOIN DimGeography g ON c.GeographyKey = g.GeographyKey
    INNER JOIN DimSalesTerritory st ON g.SalesTerritoryKey = st.SalesTerritoryKey
),

StageCharacteristics AS (
    SELECT
        lsa.LifecycleStage,
        COUNT(*) AS CustomerCount,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM LifecycleStageAssignment), 2) AS StagePct,
        ROUND(AVG(lsa.CustomerAgeYears), 2) AS AvgCustomerAgeYears,
        ROUND(AVG(lsa.DaysSinceLastPurchase), 0) AS AvgDaysSinceLastPurchase,
        ROUND(AVG(lsa.TotalOrders), 2) AS AvgTotalOrders,
        ROUND(AVG(lsa.TotalRevenue), 2) AS AvgLifetimeRevenue,
        ROUND(AVG(lsa.TotalGrossProfit), 2) AS AvgLifetimeProfit,
        ROUND(AVG(lsa.AvgTransactionValue), 2) AS AvgTransactionValue,
        ROUND(AVG(lsa.AvgDaysBetweenOrders), 0) AS AvgDaysBetweenOrders,
        ROUND(SUM(lsa.TotalRevenue), 2) AS TotalStageRevenue,
        ROUND(100.0 * SUM(lsa.TotalRevenue) / (SELECT SUM(TotalRevenue) FROM LifecycleStageAssignment), 2) AS RevenueSharePct,
        ROUND(AVG(lsa.YearlyIncome), 2) AS AvgYearlyIncome
    FROM LifecycleStageAssignment lsa
    GROUP BY lsa.LifecycleStage
),

StageTransitionOpportunities AS (
    SELECT
        lsa.CustomerKey,
        lsa.CustomerName,
        lsa.LifecycleStage,
        lsa.CustomerAgeYears,
        lsa.DaysSinceLastPurchase,
        lsa.TotalOrders,
        lsa.TotalRevenue,
        lsa.TotalGrossProfit,
        lsa.AvgDaysBetweenOrders,
        -- Next stage and requirements
        CASE lsa.LifecycleStage
            WHEN 'New' THEN 'Developing'
            WHEN 'Developing' THEN 'Growing'
            WHEN 'Growing' THEN 'Mature'
            WHEN 'Mature' THEN 'Retain as Mature'
            WHEN 'At-Risk' THEN 'Reactivate to Growing'
            WHEN 'Churned' THEN 'Win Back to New'
            WHEN 'Inactive' THEN 'Activate to Developing'
        END AS NextTargetStage,
        -- Gap to next stage
        CASE lsa.LifecycleStage
            WHEN 'New' THEN CONCAT(GREATEST(0, 3 - lsa.TotalOrders), ' more orders OR ', GREATEST(0, 91 - lsa.CustomerAgeDays), ' more days')
            WHEN 'Developing' THEN CONCAT(GREATEST(0, 5 - lsa.TotalOrders), ' more orders needed for Growing stage')
            WHEN 'Growing' THEN CONCAT(GREATEST(0, 11 - lsa.TotalOrders), ' more orders needed for Mature stage')
            WHEN 'At-Risk' THEN CONCAT('Purchase within ', GREATEST(0, 180 - lsa.DaysSinceLastPurchase), ' days to avoid churn')
            WHEN 'Churned' THEN 'Win-back campaign required'
            ELSE 'N/A'
        END AS StageProgressionGap,
        -- Recommended action
        CASE lsa.LifecycleStage
            WHEN 'New' THEN 'Onboarding campaign: Product education, repeat purchase incentive'
            WHEN 'Developing' THEN 'Engagement campaign: Cross-sell, loyalty program enrollment'
            WHEN 'Growing' THEN 'Expansion campaign: Premium tiers, volume discounts'
            WHEN 'Mature' THEN 'Retention campaign: VIP benefits, exclusive access'
            WHEN 'At-Risk' THEN 'URGENT: Re-engagement campaign, win-back offer'
            WHEN 'Churned' THEN 'Win-back campaign: Reactivation incentive'
            WHEN 'Inactive' THEN 'Activation campaign: Limited-time promotion'
        END AS RecommendedAction,
        RANK() OVER (PARTITION BY lsa.LifecycleStage ORDER BY lsa.TotalRevenue DESC) AS StageRevenueRank
    FROM LifecycleStageAssignment lsa
)

SELECT
    sto.CustomerKey,
    sto.CustomerName,
    sto.LifecycleStage,
    sto.CustomerAgeYears,
    sto.DaysSinceLastPurchase,
    sto.TotalOrders,
    sto.TotalRevenue,
    sto.TotalGrossProfit,
    sto.AvgDaysBetweenOrders,
    sto.NextTargetStage,
    sto.StageProgressionGap,
    sto.RecommendedAction,
    sto.StageRevenueRank,
    CASE
        WHEN sto.LifecycleStage = 'At-Risk' THEN 'High'
        WHEN sto.LifecycleStage IN ('New', 'Developing') THEN 'Medium'
        WHEN sto.LifecycleStage = 'Churned' THEN 'Low'
        ELSE 'Stable'
    END AS InterventionPriority
FROM StageTransitionOpportunities sto
ORDER BY
    CASE sto.LifecycleStage
        WHEN 'At-Risk' THEN 1
        WHEN 'Mature' THEN 2
        WHEN 'Growing' THEN 3
        WHEN 'Developing' THEN 4
        WHEN 'New' THEN 5
        WHEN 'Inactive' THEN 6
        WHEN 'Churned' THEN 7
    END,
    sto.TotalRevenue DESC;
```

---

# Business Question 4: Customer Product Category Affinity and Cross-Sell Opportunity Matrix

## Intent

Analyze customer purchase patterns across product categories to identify category affinity, cross-sell opportunities, and product portfolio expansion potential. This analysis reveals which high-value customers are underpenetrated in specific categories, identifies natural product bundle opportunities, and enables targeted cross-sell campaigns based on demonstrated category preferences and purchase history.

The query calculates:
- Category penetration by customer value tier
- Category affinity and purchase sequence patterns
- Cross-sell opportunity scoring
- Product portfolio completeness index
- Next-best-product recommendations

## SQL Code

```sql
WITH CustomerValueTier AS (
    SELECT
        fis.CustomerKey,
        ROUND(SUM(fis.SalesAmount), 2) AS LifetimeRevenue,
        COUNT(DISTINCT fis.SalesOrderNumber) AS TotalOrders,
        NTILE(4) OVER (ORDER BY SUM(fis.SalesAmount) DESC) AS ValueQuartile,
        CASE
            WHEN NTILE(4) OVER (ORDER BY SUM(fis.SalesAmount) DESC) = 1 THEN 'High Value'
            WHEN NTILE(4) OVER (ORDER BY SUM(fis.SalesAmount) DESC) = 2 THEN 'Medium-High Value'
            WHEN NTILE(4) OVER (ORDER BY SUM(fis.SalesAmount) DESC) = 3 THEN 'Medium-Low Value'
            ELSE 'Low Value'
        END AS ValueTier
    FROM FactInternetSales fis
    GROUP BY fis.CustomerKey
),

CustomerCategoryPurchases AS (
    SELECT
        fis.CustomerKey,
        pc.EnglishProductCategoryName AS CategoryName,
        MIN(fis.OrderDate) AS FirstCategoryPurchaseDate,
        MAX(fis.OrderDate) AS LastCategoryPurchaseDate,
        COUNT(DISTINCT fis.SalesOrderNumber) AS CategoryOrders,
        COUNT(*) AS CategoryLineItems,
        ROUND(SUM(fis.SalesAmount), 2) AS CategoryRevenue,
        ROUND(SUM(fis.SalesAmount - fis.TotalProductCost), 2) AS CategoryGrossProfit,
        COUNT(DISTINCT fis.ProductKey) AS UniqueProductsInCategory
    FROM FactInternetSales fis
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    WHERE pc.EnglishProductCategoryName IS NOT NULL
    GROUP BY fis.CustomerKey, pc.EnglishProductCategoryName
),

AllCategories AS (
    SELECT DISTINCT EnglishProductCategoryName AS CategoryName
    FROM DimProductCategory
    WHERE EnglishProductCategoryName IS NOT NULL
),

CustomerCategoryMatrix AS (
    SELECT
        cvt.CustomerKey,
        cvt.ValueTier,
        cvt.LifetimeRevenue,
        cvt.TotalOrders,
        ac.CategoryName,
        COALESCE(ccp.CategoryOrders, 0) AS CategoryOrders,
        COALESCE(ccp.CategoryRevenue, 0) AS CategoryRevenue,
        COALESCE(ccp.CategoryGrossProfit, 0) AS CategoryGrossProfit,
        CASE WHEN ccp.CustomerKey IS NOT NULL THEN 1 ELSE 0 END AS HasPurchasedCategory,
        ccp.FirstCategoryPurchaseDate,
        ccp.LastCategoryPurchaseDate
    FROM CustomerValueTier cvt
    CROSS JOIN AllCategories ac
    LEFT JOIN CustomerCategoryPurchases ccp
        ON cvt.CustomerKey = ccp.CustomerKey
        AND ac.CategoryName = ccp.CategoryName
),

CustomerCategorySummary AS (
    SELECT
        ccm.CustomerKey,
        c.FirstName || ' ' || c.LastName AS CustomerName,
        ccm.ValueTier,
        ccm.LifetimeRevenue,
        ccm.TotalOrders,
        c.YearlyIncome,
        g.EnglishCountryRegionName AS Country,
        st.SalesTerritoryRegion,
        COUNT(*) AS TotalCategories,
        SUM(ccm.HasPurchasedCategory) AS CategoriesPurchased,
        COUNT(*) - SUM(ccm.HasPurchasedCategory) AS CategoriesNotPurchased,
        ROUND(100.0 * SUM(ccm.HasPurchasedCategory) / COUNT(*), 2) AS CategoryPenetrationPct,
        STRING_AGG(CASE WHEN ccm.HasPurchasedCategory = 1 THEN ccm.CategoryName END, ', ') AS PurchasedCategories,
        STRING_AGG(CASE WHEN ccm.HasPurchasedCategory = 0 THEN ccm.CategoryName END, ', ') AS UnpurchasedCategories
    FROM CustomerCategoryMatrix ccm
    INNER JOIN DimCustomer c ON ccm.CustomerKey = c.CustomerKey
    INNER JOIN DimGeography g ON c.GeographyKey = g.GeographyKey
    INNER JOIN DimSalesTerritory st ON g.SalesTerritoryKey = st.SalesTerritoryKey
    GROUP BY ccm.CustomerKey, c.FirstName, c.LastName, ccm.ValueTier, ccm.LifetimeRevenue,
             ccm.TotalOrders, c.YearlyIncome, g.EnglishCountryRegionName, st.SalesTerritoryRegion
),

CategoryAffinityPatterns AS (
    -- Find which categories are commonly purchased together
    SELECT
        ccp1.CategoryName AS Category1,
        ccp2.CategoryName AS Category2,
        COUNT(DISTINCT ccp1.CustomerKey) AS CustomerCount,
        ROUND(AVG(ccp1.CategoryRevenue + ccp2.CategoryRevenue), 2) AS AvgCombinedRevenue
    FROM CustomerCategoryPurchases ccp1
    INNER JOIN CustomerCategoryPurchases ccp2
        ON ccp1.CustomerKey = ccp2.CustomerKey
        AND ccp1.CategoryName < ccp2.CategoryName
    GROUP BY ccp1.CategoryName, ccp2.CategoryName
    HAVING COUNT(DISTINCT ccp1.CustomerKey) >= 10
),

CrossSellOpportunities AS (
    SELECT
        ccm.CustomerKey,
        ccs.CustomerName,
        ccs.ValueTier,
        ccs.LifetimeRevenue,
        ccs.TotalOrders,
        ccs.YearlyIncome,
        ccs.Country,
        ccs.CategoryPenetrationPct,
        ccm.CategoryName AS OpportunityCategory,
        cap.Category1 AS OwnedCategory,
        cap.CustomerCount AS AffinityStrength,
        cap.AvgCombinedRevenue AS PotentialRevenue,
        RANK() OVER (PARTITION BY ccm.CustomerKey ORDER BY cap.CustomerCount DESC, cap.AvgCombinedRevenue DESC) AS OpportunityRank
    FROM CustomerCategoryMatrix ccm
    INNER JOIN CustomerCategorySummary ccs ON ccm.CustomerKey = ccs.CustomerKey
    INNER JOIN CategoryAffinityPatterns cap
        ON ccm.CategoryName = cap.Category2
        AND ccm.HasPurchasedCategory = 0
    INNER JOIN CustomerCategoryMatrix ccm_owned
        ON ccm.CustomerKey = ccm_owned.CustomerKey
        AND cap.Category1 = ccm_owned.CategoryName
        AND ccm_owned.HasPurchasedCategory = 1
    WHERE ccs.ValueTier IN ('High Value', 'Medium-High Value')
),

TopCrossSellOpportunities AS (
    SELECT
        cso.CustomerKey,
        cso.CustomerName,
        cso.ValueTier,
        cso.LifetimeRevenue,
        cso.TotalOrders,
        cso.YearlyIncome,
        cso.Country,
        cso.CategoryPenetrationPct,
        cso.OpportunityCategory AS RecommendedCategory,
        cso.OwnedCategory AS BasedOnOwnership,
        cso.AffinityStrength,
        cso.PotentialRevenue,
        cso.OpportunityRank,
        CASE
            WHEN cso.OpportunityRank = 1 THEN 'Top Priority'
            WHEN cso.OpportunityRank <= 3 THEN 'High Priority'
            WHEN cso.OpportunityRank <= 5 THEN 'Medium Priority'
            ELSE 'Low Priority'
        END AS CrossSellPriority,
        CASE
            WHEN cso.ValueTier = 'High Value' AND cso.OpportunityRank = 1 THEN 'Personalized outreach with premium offer'
            WHEN cso.ValueTier = 'High Value' THEN 'Targeted email with category-specific benefits'
            WHEN cso.ValueTier = 'Medium-High Value' THEN 'Automated campaign with bundle discount'
            ELSE 'Include in general cross-sell communications'
        END AS RecommendedApproach
    FROM CrossSellOpportunities cso
    WHERE cso.OpportunityRank <= 5
)

SELECT
    tcso.CustomerKey,
    tcso.CustomerName,
    tcso.ValueTier,
    tcso.LifetimeRevenue,
    tcso.TotalOrders,
    tcso.YearlyIncome,
    tcso.Country,
    tcso.CategoryPenetrationPct,
    tcso.RecommendedCategory,
    tcso.BasedOnOwnership,
    tcso.AffinityStrength,
    tcso.PotentialRevenue,
    tcso.OpportunityRank,
    tcso.CrossSellPriority,
    tcso.RecommendedApproach
FROM TopCrossSellOpportunities tcso
ORDER BY tcso.ValueTier, tcso.LifetimeRevenue DESC, tcso.OpportunityRank;
```

---

# Business Question 5: Predictive Customer Churn Risk and Retention Value Prioritization

## Intent

Develop a comprehensive churn risk model that combines behavioral signals, engagement trends, and value metrics to identify customers at risk of churning and prioritize retention investments based on expected value loss. This analysis enables proactive retention campaigns targeted at high-value at-risk customers, optimizes retention spending allocation, and measures the financial impact of potential churn.

The query calculates:
- Multi-factor churn risk scoring (0-100 scale)
- Behavioral churn indicators (recency, declining frequency, engagement trends)
- At-risk customer value quantification
- Retention investment recommendations
- Expected value at risk from churn

## SQL Code

```sql
WITH CustomerPurchaseMetrics AS (
    SELECT
        fis.CustomerKey,
        MIN(fis.OrderDate) AS FirstPurchaseDate,
        MAX(fis.OrderDate) AS LastPurchaseDate,
        COUNT(DISTINCT fis.SalesOrderNumber) AS TotalOrders,
        CAST(JULIANDAY('now') - JULIANDAY(MAX(fis.OrderDate)) AS INTEGER) AS DaysSinceLastPurchase,
        CAST(JULIANDAY(MAX(fis.OrderDate)) - JULIANDAY(MIN(fis.OrderDate)) AS INTEGER) AS CustomerTenureDays,
        ROUND(CAST(JULIANDAY(MAX(fis.OrderDate)) - JULIANDAY(MIN(fis.OrderDate)) AS REAL) / NULLIF(COUNT(DISTINCT fis.SalesOrderNumber) - 1, 0), 2) AS AvgDaysBetweenOrders,
        ROUND(SUM(fis.SalesAmount), 2) AS LifetimeRevenue,
        ROUND(SUM(fis.SalesAmount - fis.TotalProductCost), 2) AS LifetimeGrossProfit,
        ROUND(AVG(fis.SalesAmount), 2) AS AvgTransactionValue,
        ROUND(SUM(fis.DiscountAmount), 2) AS TotalDiscounts
    FROM FactInternetSales fis
    GROUP BY fis.CustomerKey
),

RecentActivityTrends AS (
    -- Compare recent 3 months vs. previous 3 months
    SELECT
        fis.CustomerKey,
        COUNT(DISTINCT CASE WHEN JULIANDAY('now') - JULIANDAY(fis.OrderDate) <= 90 THEN fis.SalesOrderNumber END) AS OrdersLast90Days,
        COUNT(DISTINCT CASE WHEN JULIANDAY('now') - JULIANDAY(fis.OrderDate) BETWEEN 91 AND 180 THEN fis.SalesOrderNumber END) AS OrdersPrevious90Days,
        ROUND(SUM(CASE WHEN JULIANDAY('now') - JULIANDAY(fis.OrderDate) <= 90 THEN fis.SalesAmount ELSE 0 END), 2) AS RevenueLast90Days,
        ROUND(SUM(CASE WHEN JULIANDAY('now') - JULIANDAY(fis.OrderDate) BETWEEN 91 AND 180 THEN fis.SalesAmount ELSE 0 END), 2) AS RevenuePrevious90Days
    FROM FactInternetSales fis
    GROUP BY fis.CustomerKey
),

ChurnRiskFactors AS (
    SELECT
        cpm.CustomerKey,
        c.FirstName || ' ' || c.LastName AS CustomerName,
        c.YearlyIncome,
        c.EnglishEducation AS Education,
        c.EnglishOccupation AS Occupation,
        g.EnglishCountryRegionName AS Country,
        st.SalesTerritoryRegion,
        cpm.FirstPurchaseDate,
        cpm.LastPurchaseDate,
        cpm.DaysSinceLastPurchase,
        cpm.CustomerTenureDays,
        ROUND(cpm.CustomerTenureDays / 365.25, 2) AS CustomerTenureYears,
        cpm.TotalOrders,
        cpm.AvgDaysBetweenOrders,
        cpm.LifetimeRevenue,
        cpm.LifetimeGrossProfit,
        cpm.AvgTransactionValue,
        rat.OrdersLast90Days,
        rat.OrdersPrevious90Days,
        rat.RevenueLast90Days,
        rat.RevenuePrevious90Days,
        -- Risk Factor 1: Recency Risk (0-35 points)
        CASE
            WHEN cpm.DaysSinceLastPurchase > cpm.AvgDaysBetweenOrders * 3 THEN 35
            WHEN cpm.DaysSinceLastPurchase > cpm.AvgDaysBetweenOrders * 2 THEN 25
            WHEN cpm.DaysSinceLastPurchase > cpm.AvgDaysBetweenOrders * 1.5 THEN 15
            WHEN cpm.DaysSinceLastPurchase > cpm.AvgDaysBetweenOrders THEN 5
            ELSE 0
        END AS RecencyRiskScore,
        -- Risk Factor 2: Activity Decline (0-30 points)
        CASE
            WHEN rat.OrdersLast90Days = 0 AND rat.OrdersPrevious90Days > 0 THEN 30
            WHEN rat.OrdersLast90Days < rat.OrdersPrevious90Days * 0.5 THEN 20
            WHEN rat.OrdersLast90Days < rat.OrdersPrevious90Days THEN 10
            ELSE 0
        END AS ActivityDeclineScore,
        -- Risk Factor 3: Revenue Decline (0-20 points)
        CASE
            WHEN rat.RevenueLast90Days = 0 AND rat.RevenuePrevious90Days > 0 THEN 20
            WHEN rat.RevenueLast90Days < rat.RevenuePrevious90Days * 0.5 THEN 15
            WHEN rat.RevenueLast90Days < rat.RevenuePrevious90Days THEN 8
            ELSE 0
        END AS RevenueDeclineScore,
        -- Risk Factor 4: Low Engagement (0-15 points)
        CASE
            WHEN cpm.TotalOrders <= 2 AND cpm.CustomerTenureDays > 365 THEN 15
            WHEN cpm.TotalOrders <= 3 AND cpm.CustomerTenureDays > 180 THEN 10
            WHEN cpm.TotalOrders <= 5 THEN 5
            ELSE 0
        END AS LowEngagementScore
    FROM CustomerPurchaseMetrics cpm
    LEFT JOIN RecentActivityTrends rat ON cpm.CustomerKey = rat.CustomerKey
    INNER JOIN DimCustomer c ON cpm.CustomerKey = c.CustomerKey
    INNER JOIN DimGeography g ON c.GeographyKey = g.GeographyKey
    INNER JOIN DimSalesTerritory st ON g.SalesTerritoryKey = st.SalesTerritoryKey
),

ChurnRiskScoring AS (
    SELECT
        crf.*,
        -- Total Churn Risk Score (0-100)
        crf.RecencyRiskScore + crf.ActivityDeclineScore + crf.RevenueDeclineScore + crf.LowEngagementScore AS TotalChurnRiskScore,
        -- Churn Risk Category
        CASE
            WHEN (crf.RecencyRiskScore + crf.ActivityDeclineScore + crf.RevenueDeclineScore + crf.LowEngagementScore) >= 70 THEN 'Critical Risk'
            WHEN (crf.RecencyRiskScore + crf.ActivityDeclineScore + crf.RevenueDeclineScore + crf.LowEngagementScore) >= 50 THEN 'High Risk'
            WHEN (crf.RecencyRiskScore + crf.ActivityDeclineScore + crf.RevenueDeclineScore + crf.LowEngagementScore) >= 30 THEN 'Moderate Risk'
            WHEN (crf.RecencyRiskScore + crf.ActivityDeclineScore + crf.RevenueDeclineScore + crf.LowEngagementScore) >= 15 THEN 'Low Risk'
            ELSE 'Healthy'
        END AS ChurnRiskCategory,
        -- Value Tier
        NTILE(4) OVER (ORDER BY crf.LifetimeRevenue DESC) AS ValueQuartile,
        CASE
            WHEN NTILE(4) OVER (ORDER BY crf.LifetimeRevenue DESC) = 1 THEN 'High Value'
            WHEN NTILE(4) OVER (ORDER BY crf.LifetimeRevenue DESC) = 2 THEN 'Medium-High Value'
            WHEN NTILE(4) OVER (ORDER BY crf.LifetimeRevenue DESC) = 3 THEN 'Medium-Low Value'
            ELSE 'Low Value'
        END AS ValueTier
    FROM ChurnRiskFactors crf
),

RetentionPrioritization AS (
    SELECT
        crs.CustomerKey,
        crs.CustomerName,
        crs.ValueTier,
        crs.ChurnRiskCategory,
        crs.TotalChurnRiskScore,
        crs.Country,
        crs.SalesTerritoryRegion,
        crs.YearlyIncome,
        crs.FirstPurchaseDate,
        crs.LastPurchaseDate,
        crs.DaysSinceLastPurchase,
        crs.CustomerTenureYears,
        crs.TotalOrders,
        crs.LifetimeRevenue,
        crs.LifetimeGrossProfit,
        crs.AvgTransactionValue,
        crs.OrdersLast90Days,
        crs.OrdersPrevious90Days,
        crs.RevenueLast90Days,
        crs.RevenuePrevious90Days,
        crs.RecencyRiskScore,
        crs.ActivityDeclineScore,
        crs.RevenueDeclineScore,
        crs.LowEngagementScore,
        -- Expected Annual Value (based on historical patterns)
        ROUND(crs.LifetimeRevenue / NULLIF(crs.CustomerTenureYears, 0), 2) AS ExpectedAnnualRevenue,
        -- Value at Risk (what we stand to lose)
        ROUND((crs.LifetimeRevenue / NULLIF(crs.CustomerTenureYears, 0)) * 2, 2) AS TwoYearValueAtRisk,
        -- Retention Priority Score (combines risk and value)
        ROUND(
            (crs.TotalChurnRiskScore * 0.6) +
            (crs.ValueQuartile * 10 * 0.4)
        , 2) AS RetentionPriorityScore,
        -- Recommended retention investment
        CASE
            WHEN crs.ValueTier = 'High Value' AND crs.ChurnRiskCategory IN ('Critical Risk', 'High Risk') THEN 'HIGH: Up to 20% of annual value'
            WHEN crs.ValueTier = 'High Value' AND crs.ChurnRiskCategory = 'Moderate Risk' THEN 'MEDIUM-HIGH: Up to 10% of annual value'
            WHEN crs.ValueTier IN ('High Value', 'Medium-High Value') AND crs.ChurnRiskCategory IN ('Critical Risk', 'High Risk') THEN 'MEDIUM: Up to 15% of annual value'
            WHEN crs.ValueTier = 'Medium-High Value' THEN 'MEDIUM: Up to 8% of annual value'
            WHEN crs.ChurnRiskCategory IN ('Critical Risk', 'High Risk') THEN 'LOW-MEDIUM: Up to 5% of annual value'
            ELSE 'LOW: Standard retention budget'
        END AS RetentionInvestmentRecommendation,
        -- Recommended retention action
        CASE
            WHEN crs.ChurnRiskCategory = 'Critical Risk' AND crs.ValueTier = 'High Value' THEN 'URGENT: Executive outreach, personalized offer, satisfaction survey'
            WHEN crs.ChurnRiskCategory = 'Critical Risk' THEN 'URGENT: Personal call/email, win-back offer, identify issues'
            WHEN crs.ChurnRiskCategory = 'High Risk' AND crs.ValueTier IN ('High Value', 'Medium-High Value') THEN 'HIGH PRIORITY: Personalized re-engagement, special incentive'
            WHEN crs.ChurnRiskCategory = 'High Risk' THEN 'Re-engagement campaign, limited-time offer'
            WHEN crs.ChurnRiskCategory = 'Moderate Risk' THEN 'Proactive outreach, engagement content, reminder campaign'
            WHEN crs.ChurnRiskCategory = 'Low Risk' THEN 'Standard nurture campaign'
            ELSE 'Continue standard customer communications'
        END AS RetentionAction,
        RANK() OVER (ORDER BY
            (crs.TotalChurnRiskScore * 0.6) + (crs.ValueQuartile * 10 * 0.4) DESC,
            crs.LifetimeRevenue DESC
        ) AS RetentionPriorityRank
    FROM ChurnRiskScoring crs
    WHERE crs.TotalChurnRiskScore >= 15  -- Only customers with some risk
)

SELECT
    rp.CustomerKey,
    rp.CustomerName,
    rp.ValueTier,
    rp.ChurnRiskCategory,
    rp.TotalChurnRiskScore,
    rp.RetentionPriorityScore,
    rp.RetentionPriorityRank,
    rp.Country,
    rp.SalesTerritoryRegion,
    rp.YearlyIncome,
    rp.DaysSinceLastPurchase,
    rp.CustomerTenureYears,
    rp.TotalOrders,
    rp.LifetimeRevenue,
    rp.LifetimeGrossProfit,
    rp.ExpectedAnnualRevenue,
    rp.TwoYearValueAtRisk,
    rp.OrdersLast90Days,
    rp.OrdersPrevious90Days,
    rp.RevenueLast90Days,
    rp.RevenuePrevious90Days,
    rp.RecencyRiskScore,
    rp.ActivityDeclineScore,
    rp.RevenueDeclineScore,
    rp.LowEngagementScore,
    rp.RetentionInvestmentRecommendation,
    rp.RetentionAction
FROM RetentionPrioritization rp
WHERE rp.ChurnRiskCategory IN ('Critical Risk', 'High Risk', 'Moderate Risk')
ORDER BY rp.RetentionPriorityScore DESC, rp.LifetimeRevenue DESC;
```

---

# Summary

These five business intelligence questions provide comprehensive insights into customer lifetime value, lifecycle progression, and retention optimization across the AdventureWorks Internet sales channel:

1. **Comprehensive CLV Calculation and Segmentation** - Calculates multi-dimensional customer value metrics with Platinum/Gold/Silver/Bronze tiering based on revenue, frequency, recency, and profitability
2. **RFM Segmentation and Targeted Marketing** - Implements classic RFM analysis to identify Champions, Loyal Customers, At-Risk segments, and Lost customers with actionable marketing recommendations
3. **Customer Lifecycle Stage Progression** - Tracks customers through New, Developing, Growing, Mature, At-Risk, and Churned stages with stage-specific intervention strategies
4. **Product Category Affinity and Cross-Sell Matrix** - Analyzes category penetration and affinity patterns to identify high-value cross-sell opportunities with next-best-product recommendations
5. **Predictive Churn Risk and Retention Prioritization** - Develops multi-factor churn risk scoring (0-100) combining recency, activity decline, and engagement trends with retention investment recommendations

These analyses leverage advanced SQL techniques including cohort analysis, RFM scoring, lifecycle modeling, affinity analysis, and predictive risk scoring to transform transactional data into actionable customer intelligence for acquisition, development, retention, and value maximization strategies.
