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
        (fis.OrderDate::DATE - (LAG(fis.OrderDate) OVER (PARTITION BY fis.CustomerKey ORDER BY fis.OrderDate))::DATE) AS DaysSincePreviousOrder
    FROM FactInternetSales fis
),

CustomerCurrentState AS (
    SELECT
        cpt.CustomerKey,
        MIN(cpt.OrderDate) AS FirstPurchaseDate,
        MAX(cpt.OrderDate) AS LastPurchaseDate,
        (CURRENT_DATE - MIN(cpt.OrderDate)::DATE) AS CustomerAgeDays,
        (CURRENT_DATE - MAX(cpt.OrderDate)::DATE) AS DaysSinceLastPurchase,
        (MAX(cpt.OrderDate)::DATE - MIN(cpt.OrderDate)::DATE) AS ActiveLifespanDays,
        COUNT(DISTINCT cpt.SalesOrderNumber) AS TotalOrders,
        MAX(cpt.CumulativeOrders) AS MaxOrders,
        ROUND(SUM(cpt.SalesAmount), 2) AS TotalRevenue,
        ROUND(SUM(cpt.GrossProfit), 2) AS TotalGrossProfit,
        ROUND(AVG(cpt.SalesAmount), 2) AS AvgTransactionValue,
        ROUND(AVG(cpt.DaysSincePreviousOrder), 2) AS AvgDaysBetweenOrders,
        ROUND(CAST((MAX(cpt.OrderDate)::DATE - MIN(cpt.OrderDate)::DATE) AS DOUBLE) / NULLIF(COUNT(DISTINCT cpt.SalesOrderNumber) - 1, 0), 2) AS AvgPurchaseCycleDays
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
