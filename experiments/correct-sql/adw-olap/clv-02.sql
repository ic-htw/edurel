WITH CustomerPurchaseHistory AS (
    SELECT
        fis.CustomerKey,
        MIN(fis.OrderDate) AS FirstPurchaseDate,
        MAX(fis.OrderDate) AS LastPurchaseDate,
        COUNT(DISTINCT fis.SalesOrderNumber) AS TotalOrders,
        (CURRENT_DATE - MAX(fis.OrderDate)::DATE) AS DaysSinceLastPurchase,
        (MAX(fis.OrderDate)::DATE - MIN(fis.OrderDate)::DATE) AS CustomerTenureDays,
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
