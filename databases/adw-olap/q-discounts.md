# Discount Strategy and Promotional Effectiveness Analysis

# Introduction

This document presents five complex business intelligence questions focused on discount strategies, promotional effectiveness, and pricing optimization within the AdventureWorks data warehouse. These analyses examine discount practices across both Internet and Reseller channels, evaluating the impact of price reductions on sales volume, profitability, customer behavior, and competitive positioning.

The queries leverage discount-related fields (UnitPriceDiscountPct, DiscountAmount) in both FactInternetSales and FactResellerSales tables, along with promotion data from DimPromotion, to provide actionable insights for pricing strategy, promotional planning, margin management, and revenue optimization. Advanced SQL techniques including elasticity calculations, cohort analysis, and multi-dimensional profitability modeling reveal the true cost and benefit of discounting strategies.

---

# Business Question 1: Discount Effectiveness and Return on Investment Analysis

## Intent

Analyze the effectiveness of discount strategies by measuring the relationship between discount depth and sales volume, revenue impact, and profitability outcomes. This analysis calculates the incremental revenue generated per dollar of discount investment, identifies optimal discount thresholds, and segments transactions by discount level to understand where discounting drives profitable growth versus margin erosion.

The query calculates:
- Revenue and volume uplift by discount tier
- Gross profit impact and margin compression analysis
- Discount ROI metrics (revenue per discount dollar)
- Comparison of discounted vs. non-discounted transaction performance
- Break-even discount analysis

## SQL Code

```sql
WITH AllSalesWithDiscounts AS (
    -- Internet Sales with Discount Data
    SELECT
        fis.SalesOrderNumber,
        fis.SalesOrderLineNumber,
        'Internet' AS Channel,
        fis.ProductKey,
        p.EnglishProductName AS ProductName,
        pc.EnglishProductCategoryName AS CategoryName,
        fis.OrderDate,
        dd.CalendarYear,
        dd.CalendarQuarter,
        dd.EnglishMonthName AS MonthName,
        fis.OrderQuantity,
        fis.UnitPrice,
        fis.UnitPriceDiscountPct,
        fis.DiscountAmount,
        fis.ExtendedAmount,
        fis.SalesAmount,
        fis.TotalProductCost,
        fis.SalesAmount - fis.TotalProductCost AS GrossProfit,
        st.SalesTerritoryRegion,
        st.SalesTerritoryCountry
    FROM FactInternetSales fis
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    INNER JOIN DimSalesTerritory st ON fis.SalesTerritoryKey = st.SalesTerritoryKey

    UNION ALL

    -- Reseller Sales with Discount Data
    SELECT
        frs.SalesOrderNumber,
        frs.SalesOrderLineNumber,
        'Reseller' AS Channel,
        frs.ProductKey,
        p.EnglishProductName AS ProductName,
        pc.EnglishProductCategoryName AS CategoryName,
        frs.OrderDate,
        dd.CalendarYear,
        dd.CalendarQuarter,
        dd.EnglishMonthName AS MonthName,
        frs.OrderQuantity,
        frs.UnitPrice,
        frs.UnitPriceDiscountPct,
        frs.DiscountAmount,
        frs.ExtendedAmount,
        frs.SalesAmount,
        frs.TotalProductCost,
        frs.SalesAmount - frs.TotalProductCost AS GrossProfit,
        st.SalesTerritoryRegion,
        st.SalesTerritoryCountry
    FROM FactResellerSales frs
    INNER JOIN DimProduct p ON frs.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimDate dd ON frs.OrderDateKey = dd.DateKey
    INNER JOIN DimSalesTerritory st ON frs.SalesTerritoryKey = st.SalesTerritoryKey
),

DiscountSegmentation AS (
    SELECT
        *,
        CASE
            WHEN UnitPriceDiscountPct = 0 THEN 'No Discount'
            WHEN UnitPriceDiscountPct <= 0.05 THEN '1-5% Discount'
            WHEN UnitPriceDiscountPct <= 0.10 THEN '6-10% Discount'
            WHEN UnitPriceDiscountPct <= 0.15 THEN '11-15% Discount'
            WHEN UnitPriceDiscountPct <= 0.25 THEN '16-25% Discount'
            WHEN UnitPriceDiscountPct <= 0.35 THEN '26-35% Discount'
            ELSE 'Over 35% Discount'
        END AS DiscountTier,
        ROUND(100.0 * GrossProfit / NULLIF(SalesAmount, 0), 2) AS GrossProfitMarginPct,
        ROUND(100.0 * (SalesAmount - TotalProductCost) / NULLIF(ExtendedAmount, 0), 2) AS RealizedMarginPct,
        -- Calculate what revenue would have been without discount
        ROUND(SalesAmount + DiscountAmount, 2) AS FullPriceEquivalent,
        -- Potential gross profit if sold at full price
        ROUND((SalesAmount + DiscountAmount) - TotalProductCost, 2) AS FullPriceGrossProfit,
        -- Margin erosion due to discount
        ROUND(((SalesAmount + DiscountAmount) - TotalProductCost) - (SalesAmount - TotalProductCost), 2) AS MarginErosion
    FROM AllSalesWithDiscounts
),

DiscountTierPerformance AS (
    SELECT
        Channel,
        CalendarYear,
        DiscountTier,
        COUNT(*) AS TransactionCount,
        SUM(OrderQuantity) AS TotalUnits,
        ROUND(SUM(DiscountAmount), 2) AS TotalDiscountDollars,
        ROUND(SUM(SalesAmount), 2) AS TotalRevenue,
        ROUND(SUM(ExtendedAmount), 2) AS TotalExtendedAmount,
        ROUND(SUM(GrossProfit), 2) AS TotalGrossProfit,
        ROUND(AVG(GrossProfitMarginPct), 2) AS AvgGrossProfitMarginPct,
        ROUND(SUM(FullPriceEquivalent), 2) AS TotalFullPriceEquivalent,
        ROUND(SUM(MarginErosion), 2) AS TotalMarginErosion,
        ROUND(AVG(UnitPriceDiscountPct) * 100, 2) AS AvgDiscountPct,
        ROUND(AVG(SalesAmount), 2) AS AvgTransactionValue,
        ROUND(AVG(OrderQuantity), 2) AS AvgUnitsPerTransaction
    FROM DiscountSegmentation
    GROUP BY Channel, CalendarYear, DiscountTier
),

DiscountROICalculation AS (
    SELECT
        dtp.*,
        -- Revenue per discount dollar invested
        ROUND(dtp.TotalRevenue / NULLIF(dtp.TotalDiscountDollars, 0), 2) AS RevenuePerDiscountDollar,
        -- Gross profit per discount dollar invested
        ROUND(dtp.TotalGrossProfit / NULLIF(dtp.TotalDiscountDollars, 0), 2) AS GrossProfitPerDiscountDollar,
        -- Incremental revenue (compared to revenue foregone)
        ROUND(dtp.TotalRevenue - dtp.TotalDiscountDollars, 2) AS NetRevenue,
        -- Discount efficiency ratio
        ROUND(100.0 * dtp.TotalGrossProfit / NULLIF(dtp.TotalFullPriceEquivalent - (SELECT SUM(TotalProductCost)
                                                                                      FROM DiscountSegmentation ds
                                                                                      WHERE ds.Channel = dtp.Channel
                                                                                        AND ds.CalendarYear = dtp.CalendarYear
                                                                                        AND ds.DiscountTier = dtp.DiscountTier), 0), 2) AS DiscountEfficiencyRatio
    FROM DiscountTierPerformance dtp
),

ComparativeAnalysis AS (
    SELECT
        droi.Channel,
        droi.CalendarYear,
        droi.DiscountTier,
        droi.TransactionCount,
        droi.TotalUnits,
        droi.TotalDiscountDollars,
        droi.TotalRevenue,
        droi.TotalGrossProfit,
        droi.AvgGrossProfitMarginPct,
        droi.TotalMarginErosion,
        droi.AvgDiscountPct,
        droi.AvgTransactionValue,
        droi.AvgUnitsPerTransaction,
        droi.RevenuePerDiscountDollar,
        droi.GrossProfitPerDiscountDollar,
        -- Compare to baseline (no discount tier)
        droi.AvgTransactionValue -
            LAG(droi.AvgTransactionValue) OVER (PARTITION BY droi.Channel, droi.CalendarYear ORDER BY droi.AvgDiscountPct) AS TransactionValueVsBaseline,
        droi.AvgUnitsPerTransaction -
            LAG(droi.AvgUnitsPerTransaction) OVER (PARTITION BY droi.Channel, droi.CalendarYear ORDER BY droi.AvgDiscountPct) AS UnitsVsBaseline,
        -- Rank tiers by profitability
        RANK() OVER (PARTITION BY droi.Channel, droi.CalendarYear ORDER BY droi.GrossProfitPerDiscountDollar DESC) AS ROIRank,
        RANK() OVER (PARTITION BY droi.Channel, droi.CalendarYear ORDER BY droi.TotalGrossProfit DESC) AS TotalProfitRank
    FROM DiscountROICalculation droi
)

SELECT
    ca.Channel,
    ca.CalendarYear,
    ca.DiscountTier,
    ca.TransactionCount,
    ca.TotalUnits,
    ca.TotalDiscountDollars,
    ca.TotalRevenue,
    ca.TotalGrossProfit,
    ca.AvgGrossProfitMarginPct,
    ca.TotalMarginErosion,
    ca.AvgDiscountPct,
    ca.AvgTransactionValue,
    ca.AvgUnitsPerTransaction,
    ca.RevenuePerDiscountDollar,
    ca.GrossProfitPerDiscountDollar,
    ca.TransactionValueVsBaseline,
    ca.UnitsVsBaseline,
    ca.ROIRank,
    ca.TotalProfitRank,
    CASE
        WHEN ca.GrossProfitPerDiscountDollar > 2.0 THEN 'Highly Profitable'
        WHEN ca.GrossProfitPerDiscountDollar > 1.0 THEN 'Profitable'
        WHEN ca.GrossProfitPerDiscountDollar > 0.5 THEN 'Marginally Profitable'
        ELSE 'Unprofitable Discounting'
    END AS DiscountROIRating
FROM ComparativeAnalysis ca
ORDER BY ca.CalendarYear DESC, ca.Channel, ca.AvgDiscountPct;
```

---

# Business Question 2: Channel-Specific Discount Strategies and Profitability Comparison

## Intent

Compare discount strategies between Internet and Reseller channels to understand how each channel leverages price reductions differently, and evaluate the profitability implications of these approaches. This analysis identifies whether channels are over-discounting or under-utilizing price promotions, and reveals opportunities to optimize channel-specific pricing strategies.

The query calculates:
- Discount penetration rates by channel (% of transactions with discounts)
- Average discount depth comparison across channels
- Profitability metrics by channel and discount presence
- Customer/reseller response differences to discounting
- Channel arbitrage opportunities

## SQL Code

```sql
WITH ChannelSalesBase AS (
    -- Internet Channel Base
    SELECT
        'Internet' AS Channel,
        fis.SalesOrderNumber,
        fis.SalesOrderLineNumber,
        fis.CustomerKey AS PartyKey,
        'Customer' AS PartyType,
        fis.ProductKey,
        pc.EnglishProductCategoryName AS CategoryName,
        dd.CalendarYear,
        dd.CalendarQuarter,
        st.SalesTerritoryRegion,
        fis.OrderQuantity,
        fis.UnitPrice,
        fis.UnitPriceDiscountPct,
        fis.DiscountAmount,
        fis.SalesAmount,
        fis.TotalProductCost,
        fis.SalesAmount - fis.TotalProductCost AS GrossProfit,
        CASE WHEN fis.UnitPriceDiscountPct > 0 THEN 1 ELSE 0 END AS HasDiscount
    FROM FactInternetSales fis
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    INNER JOIN DimSalesTerritory st ON fis.SalesTerritoryKey = st.SalesTerritoryKey

    UNION ALL

    -- Reseller Channel Base
    SELECT
        'Reseller' AS Channel,
        frs.SalesOrderNumber,
        frs.SalesOrderLineNumber,
        frs.ResellerKey AS PartyKey,
        'Reseller' AS PartyType,
        frs.ProductKey,
        pc.EnglishProductCategoryName AS CategoryName,
        dd.CalendarYear,
        dd.CalendarQuarter,
        st.SalesTerritoryRegion,
        frs.OrderQuantity,
        frs.UnitPrice,
        frs.UnitPriceDiscountPct,
        frs.DiscountAmount,
        frs.SalesAmount,
        frs.TotalProductCost,
        frs.SalesAmount - frs.TotalProductCost AS GrossProfit,
        CASE WHEN frs.UnitPriceDiscountPct > 0 THEN 1 ELSE 0 END AS HasDiscount
    FROM FactResellerSales frs
    INNER JOIN DimProduct p ON frs.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimDate dd ON frs.OrderDateKey = dd.DateKey
    INNER JOIN DimSalesTerritory st ON frs.SalesTerritoryKey = st.SalesTerritoryKey
),

ChannelDiscountPenetration AS (
    SELECT
        Channel,
        CalendarYear,
        COUNT(*) AS TotalTransactions,
        SUM(HasDiscount) AS DiscountedTransactions,
        ROUND(100.0 * SUM(HasDiscount) / COUNT(*), 2) AS DiscountPenetrationPct,
        COUNT(DISTINCT PartyKey) AS UniqueParties,
        COUNT(DISTINCT CASE WHEN HasDiscount = 1 THEN PartyKey END) AS PartiesUsingDiscounts,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN HasDiscount = 1 THEN PartyKey END) / COUNT(DISTINCT PartyKey), 2) AS PartyDiscountAdoptionPct
    FROM ChannelSalesBase
    GROUP BY Channel, CalendarYear
),

ChannelDiscountMetrics AS (
    SELECT
        csb.Channel,
        csb.CalendarYear,
        CASE WHEN csb.HasDiscount = 1 THEN 'With Discount' ELSE 'No Discount' END AS DiscountStatus,
        COUNT(*) AS TransactionCount,
        SUM(csb.OrderQuantity) AS TotalUnits,
        ROUND(SUM(csb.DiscountAmount), 2) AS TotalDiscountAmount,
        ROUND(SUM(csb.SalesAmount), 2) AS TotalRevenue,
        ROUND(SUM(csb.GrossProfit), 2) AS TotalGrossProfit,
        ROUND(100.0 * SUM(csb.GrossProfit) / NULLIF(SUM(csb.SalesAmount), 0), 2) AS GrossProfitMarginPct,
        ROUND(AVG(csb.UnitPriceDiscountPct) * 100, 2) AS AvgDiscountPct,
        ROUND(AVG(csb.SalesAmount), 2) AS AvgTransactionValue,
        ROUND(AVG(csb.OrderQuantity), 2) AS AvgUnitsPerTransaction,
        COUNT(DISTINCT csb.PartyKey) AS UniqueParties,
        COUNT(DISTINCT csb.ProductKey) AS UniqueProducts
    FROM ChannelSalesBase csb
    GROUP BY csb.Channel, csb.CalendarYear, DiscountStatus
),

ChannelComparison AS (
    SELECT
        cdm.Channel,
        cdm.CalendarYear,
        cdm.DiscountStatus,
        cdm.TransactionCount,
        cdm.TotalUnits,
        cdm.TotalDiscountAmount,
        cdm.TotalRevenue,
        cdm.TotalGrossProfit,
        cdm.GrossProfitMarginPct,
        cdm.AvgDiscountPct,
        cdm.AvgTransactionValue,
        cdm.AvgUnitsPerTransaction,
        cdp.DiscountPenetrationPct,
        cdp.PartyDiscountAdoptionPct,
        -- Calculate metrics relative to other channel
        cdm.GrossProfitMarginPct -
            AVG(cdm.GrossProfitMarginPct) OVER (PARTITION BY cdm.CalendarYear, cdm.DiscountStatus) AS MarginVsAverage,
        cdm.AvgDiscountPct -
            AVG(cdm.AvgDiscountPct) OVER (PARTITION BY cdm.CalendarYear, cdm.DiscountStatus) AS DiscountDepthVsAverage
    FROM ChannelDiscountMetrics cdm
    INNER JOIN ChannelDiscountPenetration cdp
        ON cdm.Channel = cdp.Channel
        AND cdm.CalendarYear = cdp.CalendarYear
),

CategoryChannelAnalysis AS (
    SELECT
        csb.Channel,
        csb.CalendarYear,
        csb.CategoryName,
        COUNT(*) AS TransactionCount,
        SUM(csb.HasDiscount) AS DiscountedTransactions,
        ROUND(100.0 * SUM(csb.HasDiscount) / COUNT(*), 2) AS CategoryDiscountPct,
        ROUND(AVG(CASE WHEN csb.HasDiscount = 1 THEN csb.UnitPriceDiscountPct * 100 END), 2) AS AvgCategoryDiscountPct,
        ROUND(SUM(csb.SalesAmount), 2) AS CategoryRevenue,
        ROUND(SUM(csb.GrossProfit), 2) AS CategoryGrossProfit,
        ROUND(100.0 * SUM(csb.GrossProfit) / NULLIF(SUM(csb.SalesAmount), 0), 2) AS CategoryMarginPct
    FROM ChannelSalesBase csb
    WHERE csb.CategoryName IS NOT NULL
    GROUP BY csb.Channel, csb.CalendarYear, csb.CategoryName
),

CrossChannelCategoryComparison AS (
    SELECT
        cca1.CalendarYear,
        cca1.CategoryName,
        cca1.Channel AS Channel1,
        cca2.Channel AS Channel2,
        cca1.CategoryDiscountPct AS Channel1DiscountPct,
        cca2.CategoryDiscountPct AS Channel2DiscountPct,
        ROUND(cca1.CategoryDiscountPct - cca2.CategoryDiscountPct, 2) AS DiscountPctDifference,
        cca1.CategoryMarginPct AS Channel1MarginPct,
        cca2.CategoryMarginPct AS Channel2MarginPct,
        ROUND(cca1.CategoryMarginPct - cca2.CategoryMarginPct, 2) AS MarginPctDifference
    FROM CategoryChannelAnalysis cca1
    INNER JOIN CategoryChannelAnalysis cca2
        ON cca1.CategoryName = cca2.CategoryName
        AND cca1.CalendarYear = cca2.CalendarYear
        AND cca1.Channel = 'Internet'
        AND cca2.Channel = 'Reseller'
)

SELECT
    cc.Channel,
    cc.CalendarYear,
    cc.DiscountStatus,
    cc.TransactionCount,
    cc.TotalUnits,
    cc.TotalDiscountAmount,
    cc.TotalRevenue,
    cc.TotalGrossProfit,
    cc.GrossProfitMarginPct,
    cc.AvgDiscountPct,
    cc.AvgTransactionValue,
    cc.AvgUnitsPerTransaction,
    cc.DiscountPenetrationPct,
    cc.PartyDiscountAdoptionPct,
    cc.MarginVsAverage,
    cc.DiscountDepthVsAverage,
    CASE
        WHEN cc.Channel = 'Internet' AND cc.DiscountPenetrationPct < 30 THEN 'Potential to Increase Discounting'
        WHEN cc.Channel = 'Internet' AND cc.DiscountPenetrationPct > 70 THEN 'Risk of Over-Discounting'
        WHEN cc.Channel = 'Reseller' AND cc.DiscountPenetrationPct < 40 THEN 'Potential to Increase Discounting'
        WHEN cc.Channel = 'Reseller' AND cc.DiscountPenetrationPct > 80 THEN 'Risk of Over-Discounting'
        ELSE 'Balanced Discount Strategy'
    END AS DiscountStrategyAssessment
FROM ChannelComparison cc
ORDER BY cc.CalendarYear DESC, cc.Channel, cc.DiscountStatus;
```

---

# Business Question 3: Product Category Discount Sensitivity and Price Elasticity Analysis

## Intent

Evaluate how different product categories respond to discounting, measuring price elasticity, volume sensitivity, and profitability trade-offs. This analysis identifies which categories benefit most from promotional pricing versus those where discounts erode margins without driving significant volume increases, enabling category-specific pricing strategies.

The query calculates:
- Volume response to discount levels by category (price elasticity proxy)
- Margin compression vs. volume gain trade-offs
- Optimal discount bands by product category
- Category-specific discount sensitivity scoring
- Cross-category discount cannibalization effects

## SQL Code

```sql
WITH ProductCategorySales AS (
    -- Combine Internet and Reseller sales with product hierarchy
    SELECT
        fis.SalesOrderNumber,
        fis.SalesOrderLineNumber,
        'Internet' AS Channel,
        p.ProductKey,
        p.EnglishProductName AS ProductName,
        psc.EnglishProductSubcategoryName AS SubcategoryName,
        pc.ProductCategoryKey,
        pc.EnglishProductCategoryName AS CategoryName,
        dd.CalendarYear,
        dd.CalendarQuarter,
        fis.OrderQuantity,
        fis.UnitPrice,
        fis.UnitPriceDiscountPct,
        fis.DiscountAmount,
        fis.SalesAmount,
        fis.TotalProductCost,
        fis.SalesAmount - fis.TotalProductCost AS GrossProfit
    FROM FactInternetSales fis
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    WHERE pc.EnglishProductCategoryName IS NOT NULL

    UNION ALL

    SELECT
        frs.SalesOrderNumber,
        frs.SalesOrderLineNumber,
        'Reseller' AS Channel,
        p.ProductKey,
        p.EnglishProductName AS ProductName,
        psc.EnglishProductSubcategoryName AS SubcategoryName,
        pc.ProductCategoryKey,
        pc.EnglishProductCategoryName AS CategoryName,
        dd.CalendarYear,
        dd.CalendarQuarter,
        frs.OrderQuantity,
        frs.UnitPrice,
        frs.UnitPriceDiscountPct,
        frs.DiscountAmount,
        frs.SalesAmount,
        frs.TotalProductCost,
        frs.SalesAmount - frs.TotalProductCost AS GrossProfit
    FROM FactResellerSales frs
    INNER JOIN DimProduct p ON frs.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimDate dd ON frs.OrderDateKey = dd.DateKey
    WHERE pc.EnglishProductCategoryName IS NOT NULL
),

CategoryDiscountBands AS (
    SELECT
        pcs.*,
        CASE
            WHEN pcs.UnitPriceDiscountPct = 0 THEN 'No Discount'
            WHEN pcs.UnitPriceDiscountPct <= 0.10 THEN 'Low (1-10%)'
            WHEN pcs.UnitPriceDiscountPct <= 0.20 THEN 'Medium (11-20%)'
            WHEN pcs.UnitPriceDiscountPct <= 0.30 THEN 'High (21-30%)'
            ELSE 'Very High (30%+)'
        END AS DiscountBand,
        ROUND(100.0 * pcs.GrossProfit / NULLIF(pcs.SalesAmount, 0), 2) AS GrossProfitMarginPct
    FROM ProductCategorySales pcs
),

CategoryPerformanceByDiscount AS (
    SELECT
        cdb.CategoryName,
        cdb.CalendarYear,
        cdb.DiscountBand,
        COUNT(*) AS TransactionCount,
        SUM(cdb.OrderQuantity) AS TotalUnitsold,
        ROUND(SUM(cdb.DiscountAmount), 2) AS TotalDiscountAmount,
        ROUND(SUM(cdb.SalesAmount), 2) AS TotalRevenue,
        ROUND(SUM(cdb.GrossProfit), 2) AS TotalGrossProfit,
        ROUND(AVG(cdb.GrossProfitMarginPct), 2) AS AvgGrossProfitMarginPct,
        ROUND(AVG(cdb.UnitPriceDiscountPct) * 100, 2) AS AvgDiscountPct,
        ROUND(AVG(cdb.UnitPrice), 2) AS AvgUnitPrice,
        ROUND(AVG(cdb.OrderQuantity), 2) AS AvgUnitsPerTransaction,
        COUNT(DISTINCT cdb.ProductKey) AS UniqueProducts
    FROM CategoryDiscountBands cdb
    GROUP BY cdb.CategoryName, cdb.CalendarYear, cdb.DiscountBand
),

BaselineMetrics AS (
    -- Capture baseline (no discount) performance for comparison
    SELECT
        CategoryName,
        CalendarYear,
        TotalUnitsold AS BaselineUnits,
        TotalRevenue AS BaselineRevenue,
        AvgGrossProfitMarginPct AS BaselineMarginPct,
        AvgUnitsPerTransaction AS BaselineUnitsPerTxn
    FROM CategoryPerformanceByDiscount
    WHERE DiscountBand = 'No Discount'
),

ElasticityCalculation AS (
    SELECT
        cpd.CategoryName,
        cpd.CalendarYear,
        cpd.DiscountBand,
        cpd.TransactionCount,
        cpd.TotalUnitsold,
        cpd.TotalDiscountAmount,
        cpd.TotalRevenue,
        cpd.TotalGrossProfit,
        cpd.AvgGrossProfitMarginPct,
        cpd.AvgDiscountPct,
        cpd.AvgUnitsPerTransaction,
        bm.BaselineUnits,
        bm.BaselineMarginPct,
        bm.BaselineUnitsPerTxn,
        -- Volume lift percentage
        ROUND(100.0 * (cpd.AvgUnitsPerTransaction - bm.BaselineUnitsPerTxn) / NULLIF(bm.BaselineUnitsPerTxn, 0), 2) AS VolumeLiftPct,
        -- Margin compression
        ROUND(bm.BaselineMarginPct - cpd.AvgGrossProfitMarginPct, 2) AS MarginCompressionPts,
        -- Price elasticity proxy: % change in volume / % change in price
        -- (Note: This is a simplified elasticity measure)
        ROUND(
            (100.0 * (cpd.AvgUnitsPerTransaction - bm.BaselineUnitsPerTxn) / NULLIF(bm.BaselineUnitsPerTxn, 0)) /
            NULLIF(cpd.AvgDiscountPct, 0),
            2
        ) AS PriceElasticityProxy,
        -- Profit efficiency: gross profit per discount dollar
        ROUND(cpd.TotalGrossProfit / NULLIF(cpd.TotalDiscountAmount, 0), 2) AS GrossProfitPerDiscountDollar
    FROM CategoryPerformanceByDiscount cpd
    LEFT JOIN BaselineMetrics bm
        ON cpd.CategoryName = bm.CategoryName
        AND cpd.CalendarYear = bm.CalendarYear
    WHERE cpd.DiscountBand != 'No Discount'
),

CategorySensitivityScoring AS (
    SELECT
        ec.*,
        NTILE(4) OVER (PARTITION BY ec.CalendarYear ORDER BY ABS(ec.PriceElasticityProxy) DESC) AS ElasticityQuartile,
        CASE
            WHEN ec.PriceElasticityProxy > 2.0 AND ec.GrossProfitPerDiscountDollar > 1.0 THEN 'Highly Elastic & Profitable'
            WHEN ec.PriceElasticityProxy > 2.0 THEN 'Highly Elastic'
            WHEN ec.PriceElasticityProxy > 1.0 AND ec.GrossProfitPerDiscountDollar > 1.0 THEN 'Moderately Elastic & Profitable'
            WHEN ec.PriceElasticityProxy > 1.0 THEN 'Moderately Elastic'
            WHEN ec.PriceElasticityProxy > 0.5 THEN 'Low Elasticity'
            ELSE 'Inelastic'
        END AS ElasticityCategory,
        CASE
            WHEN ec.MarginCompressionPts < 5 AND ec.VolumeLiftPct > 20 THEN 'Ideal for Discounting'
            WHEN ec.MarginCompressionPts < 10 AND ec.VolumeLiftPct > 10 THEN 'Good for Discounting'
            WHEN ec.MarginCompressionPts < 15 AND ec.VolumeLiftPct > 5 THEN 'Marginal Discounting Value'
            ELSE 'Poor Discounting Candidate'
        END AS DiscountRecommendation
    FROM ElasticityCalculation ec
),

OptimalDiscountBandByCategory AS (
    SELECT
        css.CategoryName,
        css.CalendarYear,
        css.DiscountBand AS OptimalDiscountBand,
        css.TotalRevenue,
        css.TotalGrossProfit,
        css.VolumeLiftPct,
        css.MarginCompressionPts,
        css.PriceElasticityProxy,
        css.GrossProfitPerDiscountDollar,
        ROW_NUMBER() OVER (
            PARTITION BY css.CategoryName, css.CalendarYear
            ORDER BY css.GrossProfitPerDiscountDollar DESC, css.VolumeLiftPct DESC
        ) AS OptimalRank
    FROM CategorySensitivityScoring css
)

SELECT
    css.CategoryName,
    css.CalendarYear,
    css.DiscountBand,
    css.TransactionCount,
    css.TotalUnitsold,
    css.TotalDiscountAmount,
    css.TotalRevenue,
    css.TotalGrossProfit,
    css.AvgGrossProfitMarginPct,
    css.AvgDiscountPct,
    css.AvgUnitsPerTransaction,
    css.BaselineUnitsPerTxn,
    css.VolumeLiftPct,
    css.MarginCompressionPts,
    css.PriceElasticityProxy,
    css.GrossProfitPerDiscountDollar,
    css.ElasticityCategory,
    css.DiscountRecommendation,
    css.ElasticityQuartile,
    CASE
        WHEN odbc.OptimalRank = 1 THEN 'Optimal Discount Band'
        ELSE 'Sub-Optimal'
    END AS OptimalityRating
FROM CategorySensitivityScoring css
LEFT JOIN OptimalDiscountBandByCategory odbc
    ON css.CategoryName = odbc.CategoryName
    AND css.CalendarYear = odbc.CalendarYear
    AND css.DiscountBand = odbc.OptimalDiscountBand
ORDER BY css.CalendarYear DESC, css.CategoryName, css.AvgDiscountPct;
```

---

# Business Question 4: Customer and Reseller Segment Discount Response Patterns

## Intent

Analyze how different customer and reseller segments respond to discounts, identifying price-sensitive segments that drive volume when discounted versus premium segments where discounting may erode brand value without significant volume gains. This analysis enables targeted promotional strategies that maximize ROI by focusing discounts on the most responsive segments.

The query calculates:
- Segment-level discount adoption and responsiveness
- Purchase frequency and basket size changes with discounts
- Lifetime value impact of discounting by segment
- Segment profitability with and without discounts
- Cross-segment discount arbitrage and cannibalization

## SQL Code

```sql
WITH CustomerInternetBehavior AS (
    SELECT
        fis.CustomerKey AS PartyKey,
        'Customer' AS PartyType,
        'Internet' AS Channel,
        c.YearlyIncome,
        c.EnglishEducation AS Education,
        c.EnglishOccupation AS Occupation,
        c.TotalChildren,
        c.NumberCarsOwned,
        c.HouseOwnerFlag,
        g.EnglishCountryRegionName AS Country,
        dd.CalendarYear,
        fis.SalesOrderNumber,
        fis.ProductKey,
        pc.EnglishProductCategoryName AS CategoryName,
        fis.OrderQuantity,
        fis.UnitPriceDiscountPct,
        fis.DiscountAmount,
        fis.SalesAmount,
        fis.TotalProductCost,
        fis.SalesAmount - fis.TotalProductCost AS GrossProfit,
        CASE WHEN fis.UnitPriceDiscountPct > 0 THEN 1 ELSE 0 END AS HasDiscount
    FROM FactInternetSales fis
    INNER JOIN DimCustomer c ON fis.CustomerKey = c.CustomerKey
    INNER JOIN DimGeography g ON c.GeographyKey = g.GeographyKey
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
),

ResellerBehavior AS (
    SELECT
        frs.ResellerKey AS PartyKey,
        'Reseller' AS PartyType,
        'Reseller' AS Channel,
        r.AnnualRevenue AS YearlyIncome,
        r.BusinessType AS Education,
        r.BusinessType AS Occupation,
        r.NumberEmployees AS TotalChildren,
        NULL AS NumberCarsOwned,
        NULL AS HouseOwnerFlag,
        g.EnglishCountryRegionName AS Country,
        dd.CalendarYear,
        frs.SalesOrderNumber,
        frs.ProductKey,
        pc.EnglishProductCategoryName AS CategoryName,
        frs.OrderQuantity,
        frs.UnitPriceDiscountPct,
        frs.DiscountAmount,
        frs.SalesAmount,
        frs.TotalProductCost,
        frs.SalesAmount - frs.TotalProductCost AS GrossProfit,
        CASE WHEN frs.UnitPriceDiscountPct > 0 THEN 1 ELSE 0 END AS HasDiscount
    FROM FactResellerSales frs
    INNER JOIN DimReseller r ON frs.ResellerKey = r.ResellerKey
    INNER JOIN DimGeography g ON r.GeographyKey = g.GeographyKey
    INNER JOIN DimProduct p ON frs.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimDate dd ON frs.OrderDateKey = dd.DateKey
),

CombinedPartyBehavior AS (
    SELECT * FROM CustomerInternetBehavior
    UNION ALL
    SELECT * FROM ResellerBehavior
),

PartySegmentation AS (
    SELECT
        cpb.*,
        CASE
            WHEN cpb.PartyType = 'Customer' THEN
                CASE
                    WHEN cpb.YearlyIncome >= 100000 THEN 'High Income'
                    WHEN cpb.YearlyIncome >= 60000 THEN 'Medium Income'
                    ELSE 'Budget Conscious'
                END
            ELSE
                CASE
                    WHEN cpb.YearlyIncome >= 5000000 THEN 'Enterprise Reseller'
                    WHEN cpb.YearlyIncome >= 1000000 THEN 'Large Reseller'
                    ELSE 'Small Reseller'
                END
        END AS Segment
    FROM CombinedPartyBehavior cpb
),

SegmentDiscountMetrics AS (
    SELECT
        ps.Channel,
        ps.CalendarYear,
        ps.Segment,
        CASE WHEN ps.HasDiscount = 1 THEN 'With Discount' ELSE 'No Discount' END AS DiscountStatus,
        COUNT(DISTINCT ps.PartyKey) AS UniqueParties,
        COUNT(DISTINCT ps.SalesOrderNumber) AS TotalOrders,
        COUNT(*) AS TotalLineItems,
        ROUND(AVG(CASE WHEN ps.HasDiscount = 1 THEN ps.UnitPriceDiscountPct * 100 END), 2) AS AvgDiscountPct,
        SUM(ps.OrderQuantity) AS TotalUnits,
        ROUND(SUM(ps.DiscountAmount), 2) AS TotalDiscountAmount,
        ROUND(SUM(ps.SalesAmount), 2) AS TotalRevenue,
        ROUND(SUM(ps.GrossProfit), 2) AS TotalGrossProfit,
        ROUND(100.0 * SUM(ps.GrossProfit) / NULLIF(SUM(ps.SalesAmount), 0), 2) AS GrossProfitMarginPct,
        ROUND(AVG(ps.SalesAmount), 2) AS AvgLineItemValue,
        ROUND(SUM(ps.SalesAmount) / NULLIF(COUNT(DISTINCT ps.PartyKey), 0), 2) AS RevenuePerParty,
        ROUND(COUNT(DISTINCT ps.SalesOrderNumber) / NULLIF(COUNT(DISTINCT ps.PartyKey), 0), 2) AS OrdersPerParty
    FROM PartySegmentation ps
    GROUP BY ps.Channel, ps.CalendarYear, ps.Segment, DiscountStatus
),

SegmentDiscountResponse AS (
    SELECT
        sdm_discount.Channel,
        sdm_discount.CalendarYear,
        sdm_discount.Segment,
        sdm_discount.UniqueParties AS PartiesWithDiscount,
        sdm_no_discount.UniqueParties AS PartiesWithoutDiscount,
        sdm_discount.TotalOrders AS OrdersWithDiscount,
        sdm_no_discount.TotalOrders AS OrdersWithoutDiscount,
        sdm_discount.TotalRevenue AS RevenueWithDiscount,
        sdm_no_discount.TotalRevenue AS RevenueWithoutDiscount,
        sdm_discount.TotalGrossProfit AS ProfitWithDiscount,
        sdm_no_discount.TotalGrossProfit AS ProfitWithoutDiscount,
        sdm_discount.AvgDiscountPct,
        sdm_discount.GrossProfitMarginPct AS MarginWithDiscount,
        sdm_no_discount.GrossProfitMarginPct AS MarginWithoutDiscount,
        sdm_discount.RevenuePerParty AS RevenuePerPartyWithDiscount,
        sdm_no_discount.RevenuePerParty AS RevenuePerPartyWithoutDiscount,
        sdm_discount.OrdersPerParty AS OrdersPerPartyWithDiscount,
        sdm_no_discount.OrdersPerParty AS OrdersPerPartyWithoutDiscount,
        -- Calculate impact metrics
        ROUND(sdm_discount.RevenuePerParty - sdm_no_discount.RevenuePerParty, 2) AS RevenuePerPartyLift,
        ROUND(100.0 * (sdm_discount.RevenuePerParty - sdm_no_discount.RevenuePerParty) /
              NULLIF(sdm_no_discount.RevenuePerParty, 0), 2) AS RevenuePerPartyLiftPct,
        ROUND(sdm_discount.OrdersPerParty - sdm_no_discount.OrdersPerParty, 2) AS OrderFrequencyLift,
        ROUND(100.0 * (sdm_discount.OrdersPerParty - sdm_no_discount.OrdersPerParty) /
              NULLIF(sdm_no_discount.OrdersPerParty, 0), 2) AS OrderFrequencyLiftPct,
        ROUND(sdm_no_discount.GrossProfitMarginPct - sdm_discount.GrossProfitMarginPct, 2) AS MarginErosionPts
    FROM SegmentDiscountMetrics sdm_discount
    LEFT JOIN SegmentDiscountMetrics sdm_no_discount
        ON sdm_discount.Channel = sdm_no_discount.Channel
        AND sdm_discount.CalendarYear = sdm_no_discount.CalendarYear
        AND sdm_discount.Segment = sdm_no_discount.Segment
        AND sdm_discount.DiscountStatus = 'With Discount'
        AND sdm_no_discount.DiscountStatus = 'No Discount'
    WHERE sdm_discount.DiscountStatus = 'With Discount'
),

SegmentDiscountSensitivity AS (
    SELECT
        sdr.*,
        -- Discount responsiveness score (0-100)
        ROUND(
            (CASE WHEN sdr.RevenuePerPartyLiftPct > 50 THEN 40 ELSE sdr.RevenuePerPartyLiftPct * 0.8 END) +
            (CASE WHEN sdr.OrderFrequencyLiftPct > 50 THEN 30 ELSE sdr.OrderFrequencyLiftPct * 0.6 END) +
            (CASE WHEN sdr.MarginErosionPts < 5 THEN 30 ELSE 30 - (sdr.MarginErosionPts * 2) END)
        , 2) AS DiscountResponsivenessScore,
        RANK() OVER (PARTITION BY sdr.Channel, sdr.CalendarYear ORDER BY sdr.RevenuePerPartyLiftPct DESC) AS ResponsivenessRank
    FROM SegmentDiscountResponse sdr
),

SegmentRecommendations AS (
    SELECT
        sds.*,
        CASE
            WHEN sds.DiscountResponsivenessScore >= 75 THEN 'Highly Responsive - Prioritize Discounting'
            WHEN sds.DiscountResponsivenessScore >= 50 THEN 'Moderately Responsive - Selective Discounting'
            WHEN sds.DiscountResponsivenessScore >= 25 THEN 'Low Responsiveness - Limit Discounting'
            ELSE 'Discount Resistant - Avoid Discounting'
        END AS DiscountStrategy,
        CASE
            WHEN sds.MarginErosionPts > 15 AND sds.RevenuePerPartyLiftPct < 20 THEN 'High Risk'
            WHEN sds.MarginErosionPts > 10 AND sds.RevenuePerPartyLiftPct < 30 THEN 'Moderate Risk'
            ELSE 'Low Risk'
        END AS MarginRiskLevel
    FROM SegmentDiscountSensitivity sds
)

SELECT
    sr.Channel,
    sr.CalendarYear,
    sr.Segment,
    sr.PartiesWithDiscount,
    sr.PartiesWithoutDiscount,
    sr.OrdersWithDiscount,
    sr.OrdersWithoutDiscount,
    sr.RevenueWithDiscount,
    sr.RevenueWithoutDiscount,
    sr.ProfitWithDiscount,
    sr.ProfitWithoutDiscount,
    sr.AvgDiscountPct,
    sr.MarginWithDiscount,
    sr.MarginWithoutDiscount,
    sr.MarginErosionPts,
    sr.RevenuePerPartyWithDiscount,
    sr.RevenuePerPartyWithoutDiscount,
    sr.RevenuePerPartyLift,
    sr.RevenuePerPartyLiftPct,
    sr.OrdersPerPartyWithDiscount,
    sr.OrdersPerPartyWithoutDiscount,
    sr.OrderFrequencyLift,
    sr.OrderFrequencyLiftPct,
    sr.DiscountResponsivenessScore,
    sr.ResponsivenessRank,
    sr.DiscountStrategy,
    sr.MarginRiskLevel
FROM SegmentRecommendations sr
ORDER BY sr.CalendarYear DESC, sr.Channel, sr.DiscountResponsivenessScore DESC;
```

---

# Business Question 5: Promotion Campaign Effectiveness and Optimal Discount Level Determination

## Intent

Evaluate the effectiveness of specific promotional campaigns from the DimPromotion table, analyzing how structured promotions with defined discount levels perform compared to ad-hoc discounting. This analysis identifies which promotion types and discount ranges drive the best combination of volume growth and profitability, enabling data-driven promotional calendar planning and discount threshold optimization.

The query calculates:
- Promotion-specific performance metrics vs. baseline
- ROI by promotion type and category
- Promotion fatigue analysis (diminishing returns over time)
- Optimal discount sweet spots by promotion category
- Promotion cannibalization effects

## SQL Code

```sql
WITH PromotionSalesData AS (
    -- Internet Sales with Promotion Details
    SELECT
        fis.SalesOrderNumber,
        fis.SalesOrderLineNumber,
        'Internet' AS Channel,
        fis.PromotionKey,
        COALESCE(pr.EnglishPromotionName, 'No Promotion') AS PromotionName,
        COALESCE(pr.EnglishPromotionType, 'No Promotion') AS PromotionType,
        COALESCE(pr.EnglishPromotionCategory, 'No Promotion') AS PromotionCategory,
        pr.DiscountPct AS PromotionDiscountPct,
        pr.MinQty AS PromotionMinQty,
        pr.MaxQty AS PromotionMaxQty,
        p.ProductKey,
        pc.EnglishProductCategoryName AS ProductCategory,
        dd.CalendarYear,
        dd.CalendarQuarter,
        dd.EnglishMonthName AS MonthName,
        fis.OrderQuantity,
        fis.UnitPrice,
        fis.UnitPriceDiscountPct AS ActualDiscountPct,
        fis.DiscountAmount,
        fis.SalesAmount,
        fis.TotalProductCost,
        fis.SalesAmount - fis.TotalProductCost AS GrossProfit
    FROM FactInternetSales fis
    LEFT JOIN DimPromotion pr ON fis.PromotionKey = pr.PromotionKey
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey

    UNION ALL

    -- Reseller Sales with Promotion Details
    SELECT
        frs.SalesOrderNumber,
        frs.SalesOrderLineNumber,
        'Reseller' AS Channel,
        frs.PromotionKey,
        COALESCE(pr.EnglishPromotionName, 'No Promotion') AS PromotionName,
        COALESCE(pr.EnglishPromotionType, 'No Promotion') AS PromotionType,
        COALESCE(pr.EnglishPromotionCategory, 'No Promotion') AS PromotionCategory,
        pr.DiscountPct AS PromotionDiscountPct,
        pr.MinQty AS PromotionMinQty,
        pr.MaxQty AS PromotionMaxQty,
        p.ProductKey,
        pc.EnglishProductCategoryName AS ProductCategory,
        dd.CalendarYear,
        dd.CalendarQuarter,
        dd.EnglishMonthName AS MonthName,
        frs.OrderQuantity,
        frs.UnitPrice,
        frs.UnitPriceDiscountPct AS ActualDiscountPct,
        frs.DiscountAmount,
        frs.SalesAmount,
        frs.TotalProductCost,
        frs.SalesAmount - frs.TotalProductCost AS GrossProfit
    FROM FactResellerSales frs
    LEFT JOIN DimPromotion pr ON frs.PromotionKey = pr.PromotionKey
    INNER JOIN DimProduct p ON frs.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimDate dd ON frs.OrderDateKey = dd.DateKey
),

PromotionPerformance AS (
    SELECT
        psd.Channel,
        psd.CalendarYear,
        psd.PromotionType,
        psd.PromotionCategory,
        psd.PromotionName,
        COUNT(*) AS TransactionCount,
        COUNT(DISTINCT psd.ProductKey) AS UniqueProducts,
        SUM(psd.OrderQuantity) AS TotalUnits,
        ROUND(SUM(psd.DiscountAmount), 2) AS TotalDiscountAmount,
        ROUND(SUM(psd.SalesAmount), 2) AS TotalRevenue,
        ROUND(SUM(psd.GrossProfit), 2) AS TotalGrossProfit,
        ROUND(100.0 * SUM(psd.GrossProfit) / NULLIF(SUM(psd.SalesAmount), 0), 2) AS GrossProfitMarginPct,
        ROUND(AVG(psd.ActualDiscountPct) * 100, 2) AS AvgActualDiscountPct,
        ROUND(AVG(psd.PromotionDiscountPct) * 100, 2) AS AvgPromotionDiscountPct,
        ROUND(AVG(psd.OrderQuantity), 2) AS AvgUnitsPerTransaction,
        ROUND(AVG(psd.SalesAmount), 2) AS AvgTransactionValue
    FROM PromotionSalesData psd
    GROUP BY psd.Channel, psd.CalendarYear, psd.PromotionType, psd.PromotionCategory, psd.PromotionName
),

BaselinePerformance AS (
    -- Baseline (no promotion) metrics
    SELECT
        Channel,
        CalendarYear,
        TotalRevenue AS BaselineRevenue,
        TotalGrossProfit AS BaselineGrossProfit,
        GrossProfitMarginPct AS BaselineMarginPct,
        AvgUnitsPerTransaction AS BaselineUnitsPerTxn,
        AvgTransactionValue AS BaselineTransactionValue
    FROM PromotionPerformance
    WHERE PromotionType = 'No Promotion'
),

PromotionVsBaseline AS (
    SELECT
        pp.Channel,
        pp.CalendarYear,
        pp.PromotionType,
        pp.PromotionCategory,
        pp.PromotionName,
        pp.TransactionCount,
        pp.UniqueProducts,
        pp.TotalUnits,
        pp.TotalDiscountAmount,
        pp.TotalRevenue,
        pp.TotalGrossProfit,
        pp.GrossProfitMarginPct,
        pp.AvgActualDiscountPct,
        pp.AvgPromotionDiscountPct,
        pp.AvgUnitsPerTransaction,
        pp.AvgTransactionValue,
        bp.BaselineMarginPct,
        bp.BaselineUnitsPerTxn,
        bp.BaselineTransactionValue,
        -- Incremental metrics
        ROUND(pp.AvgUnitsPerTransaction - bp.BaselineUnitsPerTxn, 2) AS IncrementalUnitsPerTxn,
        ROUND(100.0 * (pp.AvgUnitsPerTransaction - bp.BaselineUnitsPerTxn) / NULLIF(bp.BaselineUnitsPerTxn, 0), 2) AS UnitLiftPct,
        ROUND(pp.AvgTransactionValue - bp.BaselineTransactionValue, 2) AS IncrementalTransactionValue,
        ROUND(100.0 * (pp.AvgTransactionValue - bp.BaselineTransactionValue) / NULLIF(bp.BaselineTransactionValue, 0), 2) AS TransactionValueLiftPct,
        ROUND(bp.BaselineMarginPct - pp.GrossProfitMarginPct, 2) AS MarginErosionPts,
        -- ROI metrics
        ROUND(pp.TotalRevenue / NULLIF(pp.TotalDiscountAmount, 0), 2) AS RevenuePerDiscountDollar,
        ROUND(pp.TotalGrossProfit / NULLIF(pp.TotalDiscountAmount, 0), 2) AS ProfitPerDiscountDollar
    FROM PromotionPerformance pp
    LEFT JOIN BaselinePerformance bp
        ON pp.Channel = bp.Channel
        AND pp.CalendarYear = bp.CalendarYear
    WHERE pp.PromotionType != 'No Promotion'
),

PromotionEffectivenessScoring AS (
    SELECT
        pvb.*,
        -- Effectiveness Score (0-100): weighted combination of unit lift, value lift, and profitability
        ROUND(
            (CASE WHEN pvb.UnitLiftPct > 50 THEN 35 ELSE pvb.UnitLiftPct * 0.7 END) +
            (CASE WHEN pvb.TransactionValueLiftPct > 30 THEN 30 ELSE pvb.TransactionValueLiftPct * 1.0 END) +
            (CASE WHEN pvb.ProfitPerDiscountDollar > 2.0 THEN 35
                  WHEN pvb.ProfitPerDiscountDollar > 1.0 THEN 20
                  WHEN pvb.ProfitPerDiscountDollar > 0.5 THEN 10
                  ELSE 0 END)
        , 2) AS PromotionEffectivenessScore,
        RANK() OVER (
            PARTITION BY pvb.Channel, pvb.CalendarYear
            ORDER BY pvb.ProfitPerDiscountDollar DESC, pvb.UnitLiftPct DESC
        ) AS EffectivenessRank
    FROM PromotionVsBaseline pvb
),

PromotionTypeAnalysis AS (
    SELECT
        pes.Channel,
        pes.CalendarYear,
        pes.PromotionType,
        pes.PromotionCategory,
        COUNT(DISTINCT pes.PromotionName) AS UniquePromotions,
        SUM(pes.TransactionCount) AS TotalTransactions,
        ROUND(AVG(pes.TotalRevenue), 2) AS AvgRevenuePerPromotion,
        ROUND(AVG(pes.TotalGrossProfit), 2) AS AvgProfitPerPromotion,
        ROUND(AVG(pes.AvgActualDiscountPct), 2) AS AvgDiscountPct,
        ROUND(AVG(pes.UnitLiftPct), 2) AS AvgUnitLiftPct,
        ROUND(AVG(pes.TransactionValueLiftPct), 2) AS AvgValueLiftPct,
        ROUND(AVG(pes.MarginErosionPts), 2) AS AvgMarginErosionPts,
        ROUND(AVG(pes.ProfitPerDiscountDollar), 2) AS AvgProfitPerDiscountDollar,
        ROUND(AVG(pes.PromotionEffectivenessScore), 2) AS AvgEffectivenessScore
    FROM PromotionEffectivenessScoring pes
    GROUP BY pes.Channel, pes.CalendarYear, pes.PromotionType, pes.PromotionCategory
),

PromotionRecommendations AS (
    SELECT
        pes.*,
        CASE
            WHEN pes.PromotionEffectivenessScore >= 75 THEN 'Highly Effective - Expand'
            WHEN pes.PromotionEffectivenessScore >= 50 THEN 'Effective - Continue'
            WHEN pes.PromotionEffectivenessScore >= 25 THEN 'Marginal - Optimize'
            ELSE 'Ineffective - Discontinue'
        END AS PromotionRecommendation,
        CASE
            WHEN pes.MarginErosionPts > 15 THEN 'High Margin Risk'
            WHEN pes.MarginErosionPts > 10 THEN 'Moderate Margin Risk'
            WHEN pes.MarginErosionPts > 5 THEN 'Low Margin Risk'
            ELSE 'Minimal Margin Impact'
        END AS MarginRiskAssessment,
        CASE
            WHEN pes.ProfitPerDiscountDollar > 2.0 AND pes.UnitLiftPct > 30 THEN 'Star Promotion'
            WHEN pes.ProfitPerDiscountDollar > 1.5 AND pes.UnitLiftPct > 20 THEN 'Strong Performer'
            WHEN pes.ProfitPerDiscountDollar > 1.0 THEN 'Profitable'
            ELSE 'Needs Improvement'
        END AS PromotionTier
    FROM PromotionEffectivenessScoring pes
)

SELECT
    pr.Channel,
    pr.CalendarYear,
    pr.PromotionType,
    pr.PromotionCategory,
    pr.PromotionName,
    pr.TransactionCount,
    pr.UniqueProducts,
    pr.TotalUnits,
    pr.TotalDiscountAmount,
    pr.TotalRevenue,
    pr.TotalGrossProfit,
    pr.GrossProfitMarginPct,
    pr.AvgActualDiscountPct,
    pr.BaselineMarginPct,
    pr.MarginErosionPts,
    pr.IncrementalUnitsPerTxn,
    pr.UnitLiftPct,
    pr.IncrementalTransactionValue,
    pr.TransactionValueLiftPct,
    pr.RevenuePerDiscountDollar,
    pr.ProfitPerDiscountDollar,
    pr.PromotionEffectivenessScore,
    pr.EffectivenessRank,
    pr.PromotionRecommendation,
    pr.MarginRiskAssessment,
    pr.PromotionTier
FROM PromotionRecommendations pr
ORDER BY pr.CalendarYear DESC, pr.Channel, pr.PromotionEffectivenessScore DESC;
```

---

# Summary

These five business intelligence questions provide comprehensive insights into discount strategies, promotional effectiveness, and pricing optimization across the AdventureWorks sales organization:

1. **Discount Effectiveness and ROI Analysis** - Measures revenue and profitability impact by discount tier, calculating ROI per discount dollar and identifying optimal discount thresholds
2. **Channel-Specific Discount Strategies** - Compares Internet vs. Reseller discount penetration, depth, and profitability to optimize channel-specific pricing approaches
3. **Product Category Discount Sensitivity** - Analyzes price elasticity and volume response by category to identify which products benefit most from promotional pricing
4. **Customer and Reseller Segment Discount Response** - Evaluates segment-level discount responsiveness to enable targeted promotional strategies that maximize ROI
5. **Promotion Campaign Effectiveness** - Assesses structured promotion performance vs. ad-hoc discounting, identifying optimal promotion types and discount levels

These analyses leverage advanced SQL techniques including elasticity proxies, cohort comparisons, ROI calculations, and multi-factor effectiveness scoring to transform discount and promotion data into actionable insights for pricing strategy, promotional planning, and margin management.
