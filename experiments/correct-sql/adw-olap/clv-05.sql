WITH CustomerPurchaseMetrics AS (
    SELECT
        fis.CustomerKey,
        MIN(fis.OrderDate) AS FirstPurchaseDate,
        MAX(fis.OrderDate) AS LastPurchaseDate,
        COUNT(DISTINCT fis.SalesOrderNumber) AS TotalOrders,
        (CURRENT_DATE - MAX(fis.OrderDate)::DATE) AS DaysSinceLastPurchase,
        (MAX(fis.OrderDate)::DATE - MIN(fis.OrderDate)::DATE) AS CustomerTenureDays,
        ROUND(CAST((MAX(fis.OrderDate)::DATE - MIN(fis.OrderDate)::DATE) AS DOUBLE) / NULLIF(COUNT(DISTINCT fis.SalesOrderNumber) - 1, 0), 2) AS AvgDaysBetweenOrders,
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
        COUNT(DISTINCT CASE WHEN (CURRENT_DATE - fis.OrderDate::DATE) <= 90 THEN fis.SalesOrderNumber END) AS OrdersLast90Days,
        COUNT(DISTINCT CASE WHEN (CURRENT_DATE - fis.OrderDate::DATE) BETWEEN 91 AND 180 THEN fis.SalesOrderNumber END) AS OrdersPrevious90Days,
        ROUND(SUM(CASE WHEN (CURRENT_DATE - fis.OrderDate::DATE) <= 90 THEN fis.SalesAmount ELSE 0 END), 2) AS RevenueLast90Days,
        ROUND(SUM(CASE WHEN (CURRENT_DATE - fis.OrderDate::DATE) BETWEEN 91 AND 180 THEN fis.SalesAmount ELSE 0 END), 2) AS RevenuePrevious90Days
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
