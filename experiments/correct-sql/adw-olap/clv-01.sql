WITH CustomerFirstLastPurchase AS (
    SELECT
        fis.CustomerKey,
        MIN(fis.OrderDate) AS FirstPurchaseDate,
        MAX(fis.OrderDate) AS LastPurchaseDate,
        COUNT(DISTINCT fis.SalesOrderNumber) AS TotalOrders,
        COUNT(*) AS TotalLineItems,
        (MAX(fis.OrderDate)::DATE - MIN(fis.OrderDate)::DATE) AS CustomerTenureDays
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
        (CURRENT_DATE - cflp.LastPurchaseDate::DATE) AS DaysSinceLastPurchase,
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
        MODE(ct.Education) AS MostCommonEducation,
        MODE(ct.Occupation) AS MostCommonOccupation
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
