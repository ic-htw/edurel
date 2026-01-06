# Cost Analysis - Business Questions

## Introduction

Cost analysis is fundamental to understanding business profitability, operational efficiency, and strategic pricing decisions. By examining costs across multiple dimensions—products, channels, time periods, and geographies—organizations can identify opportunities for margin improvement, cost reduction, and competitive positioning.

This document presents a comprehensive cost analysis framework using the AdventureWorks data warehouse. The analysis leverages multiple fact tables including FactInternetSales, FactResellerSales, and FactProductInventory, combined with dimension tables to examine cost structures and profitability from various perspectives.

Key cost-related data available in the schema includes:
- **Product costs**: StandardCost, TotalProductCost in sales transactions
- **Sales revenue**: SalesAmount for profitability calculations
- **Inventory costs**: UnitCost in inventory movements
- **Pricing data**: UnitPrice, ListPrice, DealerPrice for margin analysis
- **Discounting**: DiscountAmount, UnitPriceDiscountPct for promotional cost impact

The following business questions explore various aspects of cost management including:
- Product-level profitability and margin analysis
- Channel cost structure comparisons (Internet vs. Reseller)
- Temporal cost trends and variance analysis
- Inventory carrying costs and efficiency
- Geographic cost-to-serve and territory profitability

These analyses enable data-driven decisions for pricing strategy, product portfolio management, channel optimization, and operational cost control.

---

# Business Question 1: Product Profitability Analysis with Margin Segmentation

## Intent

Analyze product-level profitability by calculating gross profit margins and segmenting products into profitability tiers. This comprehensive analysis provides:
- Gross profit (revenue - cost) and gross margin percentage by product
- Product ranking by total profit contribution
- Identification of high-margin vs. low-margin products
- Volume vs. margin analysis to identify strategic product segments
- Category and subcategory profitability rollups
- Comparison of standard costs vs. actual costs
- Identification of loss-making or marginally profitable products

Understanding product profitability enables strategic decisions about product portfolio management, pricing adjustments, promotional strategies, and resource allocation. This analysis helps identify which products drive profit despite potentially lower revenue, and which high-revenue products may have thin margins.

## SQL Code

```sql
WITH ProductCosts AS (
    SELECT
        p.ProductKey,
        p.EnglishProductName AS ProductName,
        psc.EnglishProductSubcategoryName AS Subcategory,
        pc.EnglishProductCategoryName AS Category,
        p.StandardCost,
        p.ListPrice,
        SUM(fis.OrderQuantity) AS TotalQuantitySold,
        SUM(fis.SalesAmount) AS TotalRevenue,
        SUM(fis.TotalProductCost) AS TotalCost,
        AVG(fis.UnitPrice) AS AvgSellingPrice,
        AVG(fis.ProductStandardCost) AS AvgCostPerUnit,
        SUM(fis.DiscountAmount) AS TotalDiscounts,
        COUNT(DISTINCT fis.SalesOrderNumber) AS OrderCount
    FROM FactInternetSales fis
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    INNER JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    INNER JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    GROUP BY
        p.ProductKey, p.EnglishProductName, psc.EnglishProductSubcategoryName,
        pc.EnglishProductCategoryName, p.StandardCost, p.ListPrice
),
ProductProfitability AS (
    SELECT
        ProductKey,
        ProductName,
        Subcategory,
        Category,
        TotalQuantitySold,
        OrderCount,
        ROUND(TotalRevenue, 2) AS TotalRevenue,
        ROUND(TotalCost, 2) AS TotalCost,
        ROUND(TotalRevenue - TotalCost, 2) AS GrossProfit,
        ROUND(((TotalRevenue - TotalCost) / NULLIF(TotalRevenue, 0)) * 100, 2) AS GrossMarginPct,
        ROUND(AvgSellingPrice, 2) AS AvgSellingPrice,
        ROUND(AvgCostPerUnit, 2) AS AvgCostPerUnit,
        ROUND(AvgSellingPrice - AvgCostPerUnit, 2) AS UnitProfit,
        ROUND(((AvgSellingPrice - AvgCostPerUnit) / NULLIF(AvgSellingPrice, 0)) * 100, 2) AS UnitMarginPct,
        ROUND(TotalDiscounts, 2) AS TotalDiscounts,
        ROUND((TotalDiscounts / NULLIF(TotalRevenue + TotalDiscounts, 0)) * 100, 2) AS DiscountPct,
        StandardCost,
        ListPrice,
        ROUND((ListPrice - StandardCost) / NULLIF(ListPrice, 0) * 100, 2) AS ListPriceMarginPct
    FROM ProductCosts
),
ProductSegmentation AS (
    SELECT
        *,
        CASE
            WHEN GrossMarginPct >= 50 THEN 'Premium Margin (50%+)'
            WHEN GrossMarginPct >= 35 THEN 'High Margin (35-50%)'
            WHEN GrossMarginPct >= 20 THEN 'Medium Margin (20-35%)'
            WHEN GrossMarginPct >= 10 THEN 'Low Margin (10-20%)'
            WHEN GrossMarginPct >= 0 THEN 'Minimal Margin (0-10%)'
            ELSE 'Loss Making'
        END AS MarginTier,
        CASE
            WHEN TotalRevenue >= (SELECT PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY TotalRevenue)
                                  FROM ProductProfitability) THEN 'High Volume'
            WHEN TotalRevenue >= (SELECT PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY TotalRevenue)
                                  FROM ProductProfitability) THEN 'Medium Volume'
            ELSE 'Low Volume'
        END AS VolumeSegment,
        NTILE(10) OVER (ORDER BY GrossProfit DESC) AS ProfitDecile,
        RANK() OVER (ORDER BY GrossProfit DESC) AS ProfitRank,
        RANK() OVER (ORDER BY GrossMarginPct DESC) AS MarginRank,
        RANK() OVER (PARTITION BY Category ORDER BY GrossProfit DESC) AS CategoryProfitRank
    FROM ProductProfitability
),
CategorySummary AS (
    SELECT
        Category,
        Subcategory,
        COUNT(DISTINCT ProductKey) AS ProductCount,
        SUM(TotalQuantitySold) AS CategoryQuantity,
        ROUND(SUM(TotalRevenue), 2) AS CategoryRevenue,
        ROUND(SUM(TotalCost), 2) AS CategoryCost,
        ROUND(SUM(GrossProfit), 2) AS CategoryProfit,
        ROUND((SUM(TotalRevenue - TotalCost) / NULLIF(SUM(TotalRevenue), 0)) * 100, 2) AS CategoryMarginPct,
        ROUND(AVG(GrossMarginPct), 2) AS AvgProductMargin
    FROM ProductSegmentation
    GROUP BY Category, Subcategory
)
SELECT
    'Product Detail' AS ReportSection,
    ps.ProductKey,
    ps.ProductName,
    ps.Category,
    ps.Subcategory,
    ps.MarginTier,
    ps.VolumeSegment,
    ps.TotalQuantitySold,
    ps.OrderCount,
    ps.TotalRevenue,
    ps.TotalCost,
    ps.GrossProfit,
    ps.GrossMarginPct,
    ps.AvgSellingPrice,
    ps.AvgCostPerUnit,
    ps.UnitProfit,
    ps.UnitMarginPct,
    ps.TotalDiscounts,
    ps.DiscountPct,
    ps.ProfitRank,
    ps.MarginRank,
    ps.CategoryProfitRank,
    NULL AS ProductCount,
    NULL AS CategoryQuantity,
    NULL AS CategoryProfit,
    NULL AS CategoryMarginPct,
    NULL AS AvgProductMargin
FROM ProductSegmentation ps
WHERE ps.ProfitRank <= 100  -- Top 100 products by profit

UNION ALL

SELECT
    'Category Summary' AS ReportSection,
    NULL AS ProductKey,
    NULL AS ProductName,
    cs.Category,
    cs.Subcategory,
    NULL AS MarginTier,
    NULL AS VolumeSegment,
    NULL AS TotalQuantitySold,
    NULL AS OrderCount,
    cs.CategoryRevenue AS TotalRevenue,
    cs.CategoryCost AS TotalCost,
    cs.CategoryProfit AS GrossProfit,
    cs.CategoryMarginPct AS GrossMarginPct,
    NULL AS AvgSellingPrice,
    NULL AS AvgCostPerUnit,
    NULL AS UnitProfit,
    NULL AS UnitMarginPct,
    NULL AS TotalDiscounts,
    NULL AS DiscountPct,
    NULL AS ProfitRank,
    NULL AS MarginRank,
    NULL AS CategoryProfitRank,
    cs.ProductCount,
    cs.CategoryQuantity,
    cs.CategoryProfit,
    cs.CategoryMarginPct,
    cs.AvgProductMargin
FROM CategorySummary cs

ORDER BY ReportSection, GrossProfit DESC NULLS LAST;
```

---

# Business Question 2: Channel Cost Structure and Profitability Comparison

## Intent

Compare cost structures and profitability between Internet sales (direct) and Reseller sales (indirect) channels to identify the most profitable distribution strategy. This analysis provides:
- Revenue, cost, and profit metrics by channel
- Gross margin comparison between channels
- Average transaction sizes and unit economics
- Volume distribution across channels
- Cost-per-order analysis
- Identification of products that perform better in specific channels
- Channel preference patterns over time

Understanding channel economics enables strategic decisions about channel investment, pricing differentiation, customer steering, and resource allocation. This analysis reveals whether the direct channel (internet) or indirect channel (resellers) delivers better margins, and which products are suited for each channel.

## SQL Code

```sql
WITH InternetSalesMetrics AS (
    SELECT
        'Internet Sales' AS Channel,
        p.ProductKey,
        p.EnglishProductName AS ProductName,
        psc.EnglishProductSubcategoryName AS Subcategory,
        pc.EnglishProductCategoryName AS Category,
        dd.CalendarYear,
        dd.CalendarQuarter,
        COUNT(DISTINCT fis.SalesOrderNumber) AS OrderCount,
        SUM(fis.OrderQuantity) AS TotalQuantity,
        SUM(fis.SalesAmount) AS TotalRevenue,
        SUM(fis.TotalProductCost) AS TotalCost,
        SUM(fis.DiscountAmount) AS TotalDiscounts,
        SUM(fis.TaxAmt) AS TotalTax,
        SUM(fis.Freight) AS TotalFreight,
        AVG(fis.UnitPrice) AS AvgUnitPrice,
        AVG(fis.ProductStandardCost) AS AvgUnitCost
    FROM FactInternetSales fis
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    INNER JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    INNER JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    GROUP BY
        p.ProductKey, p.EnglishProductName, psc.EnglishProductSubcategoryName,
        pc.EnglishProductCategoryName, dd.CalendarYear, dd.CalendarQuarter
),
ResellerSalesMetrics AS (
    SELECT
        'Reseller Sales' AS Channel,
        p.ProductKey,
        p.EnglishProductName AS ProductName,
        psc.EnglishProductSubcategoryName AS Subcategory,
        pc.EnglishProductCategoryName AS Category,
        dd.CalendarYear,
        dd.CalendarQuarter,
        COUNT(DISTINCT frs.SalesOrderNumber) AS OrderCount,
        SUM(frs.OrderQuantity) AS TotalQuantity,
        SUM(frs.SalesAmount) AS TotalRevenue,
        SUM(frs.TotalProductCost) AS TotalCost,
        SUM(frs.DiscountAmount) AS TotalDiscounts,
        SUM(frs.TaxAmt) AS TotalTax,
        SUM(frs.Freight) AS TotalFreight,
        AVG(frs.UnitPrice) AS AvgUnitPrice,
        AVG(frs.ProductStandardCost) AS AvgUnitCost
    FROM FactResellerSales frs
    INNER JOIN DimProduct p ON frs.ProductKey = p.ProductKey
    INNER JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    INNER JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimDate dd ON frs.OrderDateKey = dd.DateKey
    GROUP BY
        p.ProductKey, p.EnglishProductName, psc.EnglishProductSubcategoryName,
        pc.EnglishProductCategoryName, dd.CalendarYear, dd.CalendarQuarter
),
CombinedChannelMetrics AS (
    SELECT * FROM InternetSalesMetrics
    UNION ALL
    SELECT * FROM ResellerSalesMetrics
),
ChannelProfitability AS (
    SELECT
        Channel,
        ProductKey,
        ProductName,
        Subcategory,
        Category,
        CalendarYear,
        CalendarQuarter,
        OrderCount,
        TotalQuantity,
        ROUND(TotalRevenue, 2) AS TotalRevenue,
        ROUND(TotalCost, 2) AS TotalCost,
        ROUND(TotalRevenue - TotalCost, 2) AS GrossProfit,
        ROUND(((TotalRevenue - TotalCost) / NULLIF(TotalRevenue, 0)) * 100, 2) AS GrossMarginPct,
        ROUND(TotalDiscounts, 2) AS TotalDiscounts,
        ROUND(TotalFreight, 2) AS TotalFreight,
        ROUND(TotalRevenue / NULLIF(OrderCount, 0), 2) AS AvgRevenuePerOrder,
        ROUND(TotalCost / NULLIF(OrderCount, 0), 2) AS AvgCostPerOrder,
        ROUND((TotalRevenue - TotalCost) / NULLIF(OrderCount, 0), 2) AS AvgProfitPerOrder,
        ROUND(TotalRevenue / NULLIF(TotalQuantity, 0), 2) AS AvgRevenuePerUnit,
        ROUND(TotalCost / NULLIF(TotalQuantity, 0), 2) AS AvgCostPerUnit,
        ROUND(AvgUnitPrice, 2) AS AvgUnitPrice,
        ROUND(AvgUnitCost, 2) AS AvgUnitCost,
        ROUND(AvgUnitPrice - AvgUnitCost, 2) AS UnitProfit
    FROM CombinedChannelMetrics
),
ChannelComparison AS (
    SELECT
        Channel,
        Category,
        CalendarYear,
        CalendarQuarter,
        COUNT(DISTINCT ProductKey) AS UniqueProducts,
        SUM(OrderCount) AS TotalOrders,
        SUM(TotalQuantity) AS TotalUnits,
        ROUND(SUM(TotalRevenue), 2) AS ChannelRevenue,
        ROUND(SUM(TotalCost), 2) AS ChannelCost,
        ROUND(SUM(GrossProfit), 2) AS ChannelProfit,
        ROUND((SUM(TotalRevenue - TotalCost) / NULLIF(SUM(TotalRevenue), 0)) * 100, 2) AS ChannelMarginPct,
        ROUND(AVG(GrossMarginPct), 2) AS AvgProductMargin,
        ROUND(SUM(TotalDiscounts), 2) AS ChannelDiscounts,
        ROUND((SUM(TotalDiscounts) / NULLIF(SUM(TotalRevenue + TotalDiscounts), 0)) * 100, 2) AS DiscountRatePct,
        ROUND(AVG(AvgRevenuePerOrder), 2) AS AvgOrderValue,
        ROUND(AVG(AvgProfitPerOrder), 2) AS AvgProfitPerOrder,
        ROUND(SUM(TotalRevenue) / NULLIF(SUM(OrderCount), 0), 2) AS RevenuePerOrder,
        ROUND(SUM(GrossProfit) / NULLIF(SUM(OrderCount), 0), 2) AS ProfitPerOrder
    FROM ChannelProfitability
    GROUP BY Channel, Category, CalendarYear, CalendarQuarter
),
ProductChannelPreference AS (
    SELECT
        ProductKey,
        ProductName,
        Category,
        Subcategory,
        Channel,
        SUM(TotalRevenue) AS ProductChannelRevenue,
        SUM(GrossProfit) AS ProductChannelProfit,
        AVG(GrossMarginPct) AS ProductChannelMargin
    FROM ChannelProfitability
    GROUP BY ProductKey, ProductName, Category, Subcategory, Channel
),
ProductChannelAnalysis AS (
    SELECT
        pcp1.ProductKey,
        pcp1.ProductName,
        pcp1.Category,
        pcp1.Subcategory,
        ROUND(pcp1.ProductChannelRevenue, 2) AS InternetRevenue,
        ROUND(pcp2.ProductChannelRevenue, 2) AS ResellerRevenue,
        ROUND(pcp1.ProductChannelProfit, 2) AS InternetProfit,
        ROUND(pcp2.ProductChannelProfit, 2) AS ResellerProfit,
        ROUND(pcp1.ProductChannelMargin, 2) AS InternetMargin,
        ROUND(pcp2.ProductChannelMargin, 2) AS ResellerMargin,
        ROUND(pcp1.ProductChannelRevenue + COALESCE(pcp2.ProductChannelRevenue, 0), 2) AS TotalRevenue,
        CASE
            WHEN pcp1.ProductChannelRevenue > COALESCE(pcp2.ProductChannelRevenue, 0) * 2
            THEN 'Internet Dominant'
            WHEN COALESCE(pcp2.ProductChannelRevenue, 0) > pcp1.ProductChannelRevenue * 2
            THEN 'Reseller Dominant'
            ELSE 'Balanced'
        END AS ChannelPreference
    FROM ProductChannelPreference pcp1
    LEFT JOIN ProductChannelPreference pcp2
        ON pcp1.ProductKey = pcp2.ProductKey
        AND pcp1.Channel = 'Internet Sales'
        AND pcp2.Channel = 'Reseller Sales'
    WHERE pcp1.Channel = 'Internet Sales'
)
SELECT
    'Channel Summary' AS ReportSection,
    cc.Channel,
    cc.Category,
    cc.CalendarYear,
    cc.CalendarQuarter,
    cc.UniqueProducts,
    cc.TotalOrders,
    cc.TotalUnits,
    cc.ChannelRevenue,
    cc.ChannelCost,
    cc.ChannelProfit,
    cc.ChannelMarginPct,
    cc.ChannelDiscounts,
    cc.DiscountRatePct,
    cc.AvgOrderValue,
    cc.ProfitPerOrder,
    NULL AS ProductName,
    NULL AS InternetRevenue,
    NULL AS ResellerRevenue,
    NULL AS InternetProfit,
    NULL AS ResellerProfit,
    NULL AS InternetMargin,
    NULL AS ResellerMargin,
    NULL AS ChannelPreference
FROM ChannelComparison cc
WHERE cc.CalendarYear = (SELECT MAX(CalendarYear) FROM ChannelComparison)

UNION ALL

SELECT
    'Product Channel Analysis' AS ReportSection,
    NULL AS Channel,
    pca.Category,
    NULL AS CalendarYear,
    NULL AS CalendarQuarter,
    NULL AS UniqueProducts,
    NULL AS TotalOrders,
    NULL AS TotalUnits,
    NULL AS ChannelRevenue,
    NULL AS ChannelCost,
    NULL AS ChannelProfit,
    NULL AS ChannelMarginPct,
    NULL AS ChannelDiscounts,
    NULL AS DiscountRatePct,
    NULL AS AvgOrderValue,
    NULL AS ProfitPerOrder,
    pca.ProductName,
    pca.InternetRevenue,
    pca.ResellerRevenue,
    pca.InternetProfit,
    pca.ResellerProfit,
    pca.InternetMargin,
    pca.ResellerMargin,
    pca.ChannelPreference
FROM ProductChannelAnalysis pca
WHERE pca.TotalRevenue > (SELECT PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY TotalRevenue)
                          FROM ProductChannelAnalysis)

ORDER BY ReportSection, ChannelRevenue DESC NULLS LAST, TotalRevenue DESC NULLS LAST;
```

---

# Business Question 3: Cost Trend Analysis and Variance Over Time

## Intent

Analyze how product costs change over time to identify cost inflation, deflation, and variance patterns that impact margins. This temporal cost analysis provides:
- Month-over-month and year-over-year cost changes
- Cost variance between standard costs and actual costs
- Identification of products with increasing vs. decreasing costs
- Impact of cost changes on gross margins
- Correlation between cost changes and sales volumes
- Early warning indicators for margin compression
- Seasonal cost patterns

Understanding cost trends enables proactive margin management, supports pricing strategy adjustments, identifies supplier negotiation opportunities, and helps forecast future profitability under different cost scenarios.

## SQL Code

```sql
WITH MonthlyCosts AS (
    SELECT
        dd.CalendarYear,
        dd.MonthNumberOfYear,
        dd.EnglishMonthName AS MonthName,
        CAST(dd.CalendarYear AS VARCHAR) || '-' ||
            CASE WHEN dd.MonthNumberOfYear < 10
                 THEN '0' || CAST(dd.MonthNumberOfYear AS VARCHAR)
                 ELSE CAST(dd.MonthNumberOfYear AS VARCHAR)
            END AS YearMonth,
        p.ProductKey,
        p.EnglishProductName AS ProductName,
        psc.EnglishProductSubcategoryName AS Subcategory,
        pc.EnglishProductCategoryName AS Category,
        p.StandardCost AS ProductStandardCost,
        SUM(fis.OrderQuantity) AS MonthlyQuantity,
        SUM(fis.SalesAmount) AS MonthlyRevenue,
        SUM(fis.TotalProductCost) AS MonthlyActualCost,
        AVG(fis.ProductStandardCost) AS AvgStandardCostInSales,
        AVG(fis.UnitPrice) AS AvgSellingPrice,
        COUNT(DISTINCT fis.SalesOrderNumber) AS OrderCount
    FROM FactInternetSales fis
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    INNER JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    INNER JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    GROUP BY
        dd.CalendarYear, dd.MonthNumberOfYear, dd.EnglishMonthName,
        p.ProductKey, p.EnglishProductName, psc.EnglishProductSubcategoryName,
        pc.EnglishProductCategoryName, p.StandardCost
),
CostMetrics AS (
    SELECT
        CalendarYear,
        MonthNumberOfYear,
        MonthName,
        YearMonth,
        ProductKey,
        ProductName,
        Subcategory,
        Category,
        MonthlyQuantity,
        ROUND(MonthlyRevenue, 2) AS MonthlyRevenue,
        ROUND(MonthlyActualCost, 2) AS MonthlyActualCost,
        ROUND(MonthlyRevenue - MonthlyActualCost, 2) AS MonthlyGrossProfit,
        ROUND(((MonthlyRevenue - MonthlyActualCost) / NULLIF(MonthlyRevenue, 0)) * 100, 2) AS GrossMarginPct,
        ROUND(MonthlyActualCost / NULLIF(MonthlyQuantity, 0), 2) AS ActualUnitCost,
        ROUND(AvgStandardCostInSales, 2) AS StandardUnitCost,
        ROUND(AvgSellingPrice, 2) AS AvgSellingPrice,
        ROUND(MonthlyActualCost / NULLIF(MonthlyQuantity, 0) - AvgStandardCostInSales, 2) AS CostVariance,
        ROUND(((MonthlyActualCost / NULLIF(MonthlyQuantity, 0) - AvgStandardCostInSales) /
               NULLIF(AvgStandardCostInSales, 0)) * 100, 2) AS CostVariancePct,
        OrderCount
    FROM MonthlyCosts
),
CostTrends AS (
    SELECT
        *,
        LAG(ActualUnitCost, 1) OVER (
            PARTITION BY ProductKey
            ORDER BY CalendarYear, MonthNumberOfYear
        ) AS PrevMonthUnitCost,
        LAG(ActualUnitCost, 12) OVER (
            PARTITION BY ProductKey
            ORDER BY CalendarYear, MonthNumberOfYear
        ) AS SameMonthLastYearUnitCost,
        LAG(GrossMarginPct, 1) OVER (
            PARTITION BY ProductKey
            ORDER BY CalendarYear, MonthNumberOfYear
        ) AS PrevMonthMargin,
        AVG(ActualUnitCost) OVER (
            PARTITION BY ProductKey
            ORDER BY CalendarYear, MonthNumberOfYear
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS ThreeMonthAvgCost,
        AVG(GrossMarginPct) OVER (
            PARTITION BY ProductKey
            ORDER BY CalendarYear, MonthNumberOfYear
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS ThreeMonthAvgMargin
    FROM CostMetrics
),
CostChanges AS (
    SELECT
        CalendarYear,
        MonthNumberOfYear,
        MonthName,
        YearMonth,
        ProductKey,
        ProductName,
        Subcategory,
        Category,
        MonthlyQuantity,
        MonthlyRevenue,
        MonthlyActualCost,
        MonthlyGrossProfit,
        GrossMarginPct,
        ActualUnitCost,
        StandardUnitCost,
        AvgSellingPrice,
        CostVariance,
        CostVariancePct,
        ROUND(ThreeMonthAvgCost, 2) AS ThreeMonthAvgCost,
        ROUND(ThreeMonthAvgMargin, 2) AS ThreeMonthAvgMargin,
        CASE
            WHEN PrevMonthUnitCost > 0
            THEN ROUND(((ActualUnitCost - PrevMonthUnitCost) / PrevMonthUnitCost) * 100, 2)
            ELSE NULL
        END AS MoMCostChangePct,
        CASE
            WHEN SameMonthLastYearUnitCost > 0
            THEN ROUND(((ActualUnitCost - SameMonthLastYearUnitCost) / SameMonthLastYearUnitCost) * 100, 2)
            ELSE NULL
        END AS YoYCostChangePct,
        ROUND(GrossMarginPct - PrevMonthMargin, 2) AS MoMMarginChange,
        CASE
            WHEN PrevMonthUnitCost > 0
            THEN ROUND(ActualUnitCost - PrevMonthUnitCost, 2)
            ELSE NULL
        END AS MoMCostChange,
        CASE
            WHEN SameMonthLastYearUnitCost > 0
            THEN ROUND(ActualUnitCost - SameMonthLastYearUnitCost, 2)
            ELSE NULL
        END AS YoYCostChange
    FROM CostTrends
),
ProductCostProfile AS (
    SELECT
        ProductKey,
        ProductName,
        Category,
        Subcategory,
        COUNT(*) AS MonthsTracked,
        ROUND(AVG(ActualUnitCost), 2) AS AvgUnitCost,
        ROUND(STDEV(ActualUnitCost), 2) AS StdDevUnitCost,
        ROUND(MIN(ActualUnitCost), 2) AS MinUnitCost,
        ROUND(MAX(ActualUnitCost), 2) AS MaxUnitCost,
        ROUND(AVG(GrossMarginPct), 2) AS AvgGrossMargin,
        ROUND(AVG(MoMCostChangePct), 2) AS AvgMoMCostChange,
        ROUND(AVG(CostVariancePct), 2) AS AvgCostVariance,
        SUM(MonthlyQuantity) AS TotalQuantity,
        ROUND(SUM(MonthlyRevenue), 2) AS TotalRevenue,
        CASE
            WHEN AVG(MoMCostChangePct) > 2 THEN 'Rising Costs (2%+ per month)'
            WHEN AVG(MoMCostChangePct) > 0 THEN 'Slight Cost Increase'
            WHEN AVG(MoMCostChangePct) > -2 THEN 'Stable Costs'
            ELSE 'Decreasing Costs'
        END AS CostTrendCategory
    FROM CostChanges
    WHERE MoMCostChangePct IS NOT NULL
    GROUP BY ProductKey, ProductName, Category, Subcategory
),
CategoryCostTrends AS (
    SELECT
        Category,
        CalendarYear,
        MonthNumberOfYear,
        MonthName,
        YearMonth,
        COUNT(DISTINCT ProductKey) AS ProductCount,
        SUM(MonthlyQuantity) AS CategoryQuantity,
        ROUND(SUM(MonthlyRevenue), 2) AS CategoryRevenue,
        ROUND(SUM(MonthlyActualCost), 2) AS CategoryCost,
        ROUND(SUM(MonthlyGrossProfit), 2) AS CategoryProfit,
        ROUND((SUM(MonthlyGrossProfit) / NULLIF(SUM(MonthlyRevenue), 0)) * 100, 2) AS CategoryMarginPct,
        ROUND(AVG(ActualUnitCost), 2) AS AvgCategoryUnitCost,
        ROUND(AVG(MoMCostChangePct), 2) AS AvgMoMCostChange,
        ROUND(AVG(YoYCostChangePct), 2) AS AvgYoYCostChange
    FROM CostChanges
    GROUP BY Category, CalendarYear, MonthNumberOfYear, MonthName, YearMonth
)
SELECT
    'Product Cost Trends' AS ReportSection,
    cc.YearMonth,
    cc.ProductName,
    cc.Category,
    cc.Subcategory,
    cc.ActualUnitCost,
    cc.StandardUnitCost,
    cc.CostVariance,
    cc.CostVariancePct,
    cc.MoMCostChangePct,
    cc.YoYCostChangePct,
    cc.GrossMarginPct,
    cc.MoMMarginChange,
    cc.ThreeMonthAvgCost,
    cc.MonthlyQuantity,
    cc.MonthlyRevenue,
    NULL AS MonthsTracked,
    NULL AS StdDevUnitCost,
    NULL AS AvgMoMCostChange,
    NULL AS CostTrendCategory,
    NULL AS CategoryQuantity,
    NULL AS CategoryProfit,
    NULL AS CategoryMarginPct
FROM CostChanges cc
WHERE cc.CalendarYear >= (SELECT MAX(CalendarYear) - 1 FROM CostChanges)
    AND cc.MonthlyQuantity >= 10  -- Filter low-volume months

UNION ALL

SELECT
    'Product Cost Profile' AS ReportSection,
    NULL AS YearMonth,
    pcp.ProductName,
    pcp.Category,
    pcp.Subcategory,
    pcp.AvgUnitCost AS ActualUnitCost,
    NULL AS StandardUnitCost,
    NULL AS CostVariance,
    pcp.AvgCostVariance AS CostVariancePct,
    pcp.AvgMoMCostChange AS MoMCostChangePct,
    NULL AS YoYCostChangePct,
    pcp.AvgGrossMargin AS GrossMarginPct,
    NULL AS MoMMarginChange,
    NULL AS ThreeMonthAvgCost,
    pcp.TotalQuantity AS MonthlyQuantity,
    pcp.TotalRevenue AS MonthlyRevenue,
    pcp.MonthsTracked,
    pcp.StdDevUnitCost,
    pcp.AvgMoMCostChange,
    pcp.CostTrendCategory,
    NULL AS CategoryQuantity,
    NULL AS CategoryProfit,
    NULL AS CategoryMarginPct
FROM ProductCostProfile pcp
WHERE pcp.TotalQuantity >= 100  -- Focus on significant products

UNION ALL

SELECT
    'Category Cost Trends' AS ReportSection,
    cct.YearMonth,
    NULL AS ProductName,
    cct.Category,
    NULL AS Subcategory,
    cct.AvgCategoryUnitCost AS ActualUnitCost,
    NULL AS StandardUnitCost,
    NULL AS CostVariance,
    NULL AS CostVariancePct,
    cct.AvgMoMCostChange AS MoMCostChangePct,
    cct.AvgYoYCostChange AS YoYCostChangePct,
    cct.CategoryMarginPct AS GrossMarginPct,
    NULL AS MoMMarginChange,
    NULL AS ThreeMonthAvgCost,
    cct.CategoryQuantity AS MonthlyQuantity,
    cct.CategoryRevenue AS MonthlyRevenue,
    NULL AS MonthsTracked,
    NULL AS StdDevUnitCost,
    NULL AS AvgMoMCostChange,
    NULL AS CostTrendCategory,
    cct.CategoryQuantity,
    cct.CategoryProfit,
    cct.CategoryMarginPct
FROM CategoryCostTrends cct
WHERE cct.CalendarYear >= (SELECT MAX(CalendarYear) - 1 FROM CategoryCostTrends)

ORDER BY ReportSection, YearMonth DESC NULLS LAST, MonthlyRevenue DESC NULLS LAST;
```

---

# Business Question 4: Inventory Carrying Cost Analysis and Turnover Efficiency

## Intent

Analyze inventory costs and turnover rates to identify slow-moving products, calculate carrying costs, and optimize inventory levels. This analysis provides:
- Current inventory balances and unit costs by product
- Inventory value (quantity × unit cost) by product and category
- Inventory turnover rates (sales velocity vs. inventory levels)
- Identification of slow-moving, dead stock, and fast-moving products
- Days of inventory on hand
- Carrying cost implications of excess inventory
- Comparison of inventory costs vs. sales performance

Understanding inventory economics enables better working capital management, identifies obsolescence risks, supports SKU rationalization decisions, and optimizes stock levels to balance availability with carrying costs.

## SQL Code

```sql
WITH LatestInventory AS (
    SELECT
        fpi.ProductKey,
        MAX(dd.FullDateAlternateKey) AS LatestInventoryDate,
        MAX(fpi.DateKey) AS LatestDateKey
    FROM FactProductInventory fpi
    INNER JOIN DimDate dd ON fpi.DateKey = dd.DateKey
    GROUP BY fpi.ProductKey
),
CurrentInventoryLevels AS (
    SELECT
        li.ProductKey,
        li.LatestInventoryDate,
        fpi.UnitCost,
        fpi.UnitsBalance AS CurrentInventory,
        fpi.UnitsIn AS RecentUnitsIn,
        fpi.UnitsOut AS RecentUnitsOut
    FROM LatestInventory li
    INNER JOIN FactProductInventory fpi
        ON li.ProductKey = fpi.ProductKey
        AND li.LatestDateKey = fpi.DateKey
),
RecentSales AS (
    SELECT
        fis.ProductKey,
        SUM(fis.OrderQuantity) AS Last90DaysSales,
        SUM(fis.SalesAmount) AS Last90DaysRevenue,
        SUM(fis.TotalProductCost) AS Last90DaysCost,
        COUNT(DISTINCT fis.SalesOrderNumber) AS Last90DaysOrders,
        AVG(fis.UnitPrice) AS AvgSellingPrice
    FROM FactInternetSales fis
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    WHERE dd.FullDateAlternateKey >= DATE('now', '-90 days')
    GROUP BY fis.ProductKey
),
ProductInventoryAnalysis AS (
    SELECT
        p.ProductKey,
        p.EnglishProductName AS ProductName,
        psc.EnglishProductSubcategoryName AS Subcategory,
        pc.EnglishProductCategoryName AS Category,
        p.StandardCost,
        p.ListPrice,
        cil.LatestInventoryDate,
        cil.CurrentInventory,
        ROUND(cil.UnitCost, 2) AS CurrentUnitCost,
        ROUND(cil.CurrentInventory * cil.UnitCost, 2) AS InventoryValue,
        COALESCE(rs.Last90DaysSales, 0) AS Last90DaysSales,
        ROUND(COALESCE(rs.Last90DaysRevenue, 0), 2) AS Last90DaysRevenue,
        ROUND(COALESCE(rs.Last90DaysCost, 0), 2) AS Last90DaysCost,
        COALESCE(rs.Last90DaysOrders, 0) AS Last90DaysOrders,
        ROUND(COALESCE(rs.AvgSellingPrice, 0), 2) AS AvgSellingPrice,
        -- Inventory turnover calculations
        CASE
            WHEN COALESCE(rs.Last90DaysSales, 0) > 0
            THEN ROUND(cil.CurrentInventory / (CAST(rs.Last90DaysSales AS FLOAT) / 90), 1)
            ELSE 999
        END AS DaysOfInventory,
        CASE
            WHEN cil.CurrentInventory > 0
            THEN ROUND((CAST(COALESCE(rs.Last90DaysSales, 0) AS FLOAT) / 90) / cil.CurrentInventory * 365, 2)
            ELSE 0
        END AS AnnualTurnoverRate,
        CASE
            WHEN COALESCE(rs.Last90DaysSales, 0) > 0
            THEN ROUND(CAST(COALESCE(rs.Last90DaysSales, 0) AS FLOAT) / 90, 2)
            ELSE 0
        END AS AvgDailySales,
        cil.RecentUnitsIn,
        cil.RecentUnitsOut
    FROM CurrentInventoryLevels cil
    INNER JOIN DimProduct p ON cil.ProductKey = p.ProductKey
    INNER JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    INNER JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    LEFT JOIN RecentSales rs ON cil.ProductKey = rs.ProductKey
),
InventorySegmentation AS (
    SELECT
        *,
        CASE
            WHEN DaysOfInventory <= 30 THEN 'Fast Moving (<=30 days)'
            WHEN DaysOfInventory <= 60 THEN 'Normal (30-60 days)'
            WHEN DaysOfInventory <= 90 THEN 'Slow Moving (60-90 days)'
            WHEN DaysOfInventory <= 180 THEN 'Very Slow (90-180 days)'
            ELSE 'Dead Stock (180+ days)'
        END AS InventoryCategory,
        CASE
            WHEN AnnualTurnoverRate >= 12 THEN 'Excellent (12+ turns/year)'
            WHEN AnnualTurnoverRate >= 6 THEN 'Good (6-12 turns/year)'
            WHEN AnnualTurnoverRate >= 3 THEN 'Fair (3-6 turns/year)'
            WHEN AnnualTurnoverRate >= 1 THEN 'Poor (1-3 turns/year)'
            ELSE 'Critical (<1 turn/year)'
        END AS TurnoverRating,
        -- Estimated carrying cost (assume 25% annual carrying cost rate)
        ROUND(InventoryValue * 0.25, 2) AS EstimatedAnnualCarryingCost,
        -- Excess inventory calculation (anything over 60 days)
        CASE
            WHEN DaysOfInventory > 60
            THEN ROUND((DaysOfInventory - 60) * AvgDailySales, 0)
            ELSE 0
        END AS ExcessInventoryUnits,
        CASE
            WHEN DaysOfInventory > 60
            THEN ROUND((DaysOfInventory - 60) * AvgDailySales * CurrentUnitCost, 2)
            ELSE 0
        END AS ExcessInventoryValue
    FROM ProductInventoryAnalysis
),
CategoryInventorySummary AS (
    SELECT
        Category,
        COUNT(DISTINCT ProductKey) AS ProductCount,
        SUM(CurrentInventory) AS TotalInventoryUnits,
        ROUND(SUM(InventoryValue), 2) AS TotalInventoryValue,
        ROUND(SUM(EstimatedAnnualCarryingCost), 2) AS TotalCarryingCost,
        ROUND(SUM(ExcessInventoryValue), 2) AS TotalExcessInventoryValue,
        ROUND(AVG(DaysOfInventory), 1) AS AvgDaysOfInventory,
        ROUND(AVG(AnnualTurnoverRate), 2) AS AvgTurnoverRate,
        SUM(Last90DaysSales) AS CategorySales,
        ROUND(SUM(Last90DaysRevenue), 2) AS CategoryRevenue
    FROM InventorySegmentation
    GROUP BY Category
),
InventoryRiskAnalysis AS (
    SELECT
        InventoryCategory,
        TurnoverRating,
        COUNT(DISTINCT ProductKey) AS ProductCount,
        SUM(CurrentInventory) AS TotalUnits,
        ROUND(SUM(InventoryValue), 2) AS TotalValue,
        ROUND(AVG(DaysOfInventory), 1) AS AvgDaysOfInventory,
        ROUND(SUM(ExcessInventoryValue), 2) AS ExcessValue,
        ROUND(SUM(EstimatedAnnualCarryingCost), 2) AS CarryingCost
    FROM InventorySegmentation
    GROUP BY InventoryCategory, TurnoverRating
)
SELECT
    'Product Inventory Detail' AS ReportSection,
    inv.ProductName,
    inv.Category,
    inv.Subcategory,
    inv.InventoryCategory,
    inv.TurnoverRating,
    inv.CurrentInventory,
    inv.CurrentUnitCost,
    inv.InventoryValue,
    inv.DaysOfInventory,
    inv.AnnualTurnoverRate,
    inv.AvgDailySales,
    inv.Last90DaysSales,
    inv.Last90DaysRevenue,
    inv.EstimatedAnnualCarryingCost,
    inv.ExcessInventoryUnits,
    inv.ExcessInventoryValue,
    NULL AS ProductCount,
    NULL AS TotalInventoryUnits,
    NULL AS TotalInventoryValue,
    NULL AS TotalCarryingCost,
    NULL AS CategorySales
FROM InventorySegmentation inv
WHERE inv.InventoryValue > 1000  -- Focus on significant inventory items

UNION ALL

SELECT
    'Category Inventory Summary' AS ReportSection,
    NULL AS ProductName,
    cis.Category,
    NULL AS Subcategory,
    NULL AS InventoryCategory,
    NULL AS TurnoverRating,
    NULL AS CurrentInventory,
    NULL AS CurrentUnitCost,
    NULL AS InventoryValue,
    cis.AvgDaysOfInventory AS DaysOfInventory,
    cis.AvgTurnoverRate AS AnnualTurnoverRate,
    NULL AS AvgDailySales,
    NULL AS Last90DaysSales,
    NULL AS Last90DaysRevenue,
    NULL AS EstimatedAnnualCarryingCost,
    NULL AS ExcessInventoryUnits,
    NULL AS ExcessInventoryValue,
    cis.ProductCount,
    cis.TotalInventoryUnits,
    cis.TotalInventoryValue,
    cis.TotalCarryingCost,
    cis.CategorySales
FROM CategoryInventorySummary cis

UNION ALL

SELECT
    'Inventory Risk Analysis' AS ReportSection,
    NULL AS ProductName,
    NULL AS Category,
    NULL AS Subcategory,
    ira.InventoryCategory,
    ira.TurnoverRating,
    NULL AS CurrentInventory,
    NULL AS CurrentUnitCost,
    ira.TotalValue AS InventoryValue,
    ira.AvgDaysOfInventory AS DaysOfInventory,
    NULL AS AnnualTurnoverRate,
    NULL AS AvgDailySales,
    NULL AS Last90DaysSales,
    NULL AS Last90DaysRevenue,
    ira.CarryingCost AS EstimatedAnnualCarryingCost,
    NULL AS ExcessInventoryUnits,
    ira.ExcessValue AS ExcessInventoryValue,
    ira.ProductCount,
    ira.TotalUnits AS TotalInventoryUnits,
    NULL AS TotalInventoryValue,
    NULL AS TotalCarryingCost,
    NULL AS CategorySales
FROM InventoryRiskAnalysis ira

ORDER BY ReportSection, InventoryValue DESC NULLS LAST, TotalInventoryValue DESC NULLS LAST;
```

---

# Business Question 5: Geographic Cost-to-Serve and Territory Profitability Analysis

## Intent

Analyze cost structures and profitability across geographic territories to identify the most profitable regions and understand regional cost variations. This analysis provides:
- Revenue, cost, and profit by sales territory and geography
- Cost-to-serve metrics by region (including freight and delivery costs)
- Margin differences across territories
- Territory ranking by profitability
- Geographic patterns in discounting and costs
- Identification of high-cost vs. low-cost regions
- Customer density and average order profitability by territory

Understanding geographic profitability enables territory resource allocation, pricing adjustments by region, identification of expansion opportunities, and targeted cost reduction initiatives in underperforming markets.

## SQL Code

```sql
WITH GeographicSales AS (
    SELECT
        st.SalesTerritoryKey,
        st.SalesTerritoryRegion AS Territory,
        st.SalesTerritoryCountry AS Country,
        st.SalesTerritoryGroup AS TerritoryGroup,
        g.StateProvinceName AS StateProvince,
        g.City,
        c.CustomerKey,
        fis.SalesOrderNumber,
        fis.OrderQuantity,
        fis.SalesAmount,
        fis.TotalProductCost,
        fis.DiscountAmount,
        fis.Freight,
        fis.TaxAmt,
        dd.CalendarYear,
        dd.CalendarQuarter,
        p.EnglishProductName AS ProductName,
        pc.EnglishProductCategoryName AS Category
    FROM FactInternetSales fis
    INNER JOIN DimCustomer c ON fis.CustomerKey = c.CustomerKey
    INNER JOIN DimGeography g ON c.GeographyKey = g.GeographyKey
    INNER JOIN DimSalesTerritory st ON g.SalesTerritoryKey = st.SalesTerritoryKey
    INNER JOIN DimDate dd ON fis.OrderDateKey = dd.DateKey
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    INNER JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    INNER JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
),
TerritoryMetrics AS (
    SELECT
        Territory,
        Country,
        TerritoryGroup,
        StateProvince,
        City,
        CalendarYear,
        CalendarQuarter,
        Category,
        COUNT(DISTINCT CustomerKey) AS UniqueCustomers,
        COUNT(DISTINCT SalesOrderNumber) AS TotalOrders,
        SUM(OrderQuantity) AS TotalUnits,
        SUM(SalesAmount) AS TotalRevenue,
        SUM(TotalProductCost) AS TotalProductCost,
        SUM(Freight) AS TotalFreight,
        SUM(TaxAmt) AS TotalTax,
        SUM(DiscountAmount) AS TotalDiscounts,
        AVG(SalesAmount) AS AvgOrderValue,
        AVG(TotalProductCost) AS AvgOrderCost,
        AVG(Freight) AS AvgFreightPerOrder
    FROM GeographicSales
    GROUP BY
        Territory, Country, TerritoryGroup, StateProvince, City,
        CalendarYear, CalendarQuarter, Category
),
TerritoryProfitability AS (
    SELECT
        Territory,
        Country,
        TerritoryGroup,
        StateProvince,
        City,
        CalendarYear,
        CalendarQuarter,
        Category,
        UniqueCustomers,
        TotalOrders,
        TotalUnits,
        ROUND(TotalRevenue, 2) AS TotalRevenue,
        ROUND(TotalProductCost, 2) AS TotalProductCost,
        ROUND(TotalFreight, 2) AS TotalFreight,
        ROUND(TotalTax, 2) AS TotalTax,
        ROUND(TotalDiscounts, 2) AS TotalDiscounts,
        -- Cost structure
        ROUND(TotalProductCost + TotalFreight, 2) AS TotalCostToServe,
        ROUND(TotalRevenue - (TotalProductCost + TotalFreight), 2) AS GrossProfit,
        ROUND(((TotalRevenue - (TotalProductCost + TotalFreight)) / NULLIF(TotalRevenue, 0)) * 100, 2) AS GrossMarginPct,
        -- Unit economics
        ROUND(TotalRevenue / NULLIF(UniqueCustomers, 0), 2) AS RevenuePerCustomer,
        ROUND((TotalRevenue - TotalProductCost - TotalFreight) / NULLIF(UniqueCustomers, 0), 2) AS ProfitPerCustomer,
        ROUND(TotalRevenue / NULLIF(TotalOrders, 0), 2) AS AvgOrderValue,
        ROUND((TotalRevenue - TotalProductCost - TotalFreight) / NULLIF(TotalOrders, 0), 2) AS ProfitPerOrder,
        ROUND(TotalFreight / NULLIF(TotalOrders, 0), 2) AS FreightPerOrder,
        ROUND((TotalFreight / NULLIF(TotalRevenue, 0)) * 100, 2) AS FreightCostPct,
        ROUND((TotalDiscounts / NULLIF(TotalRevenue + TotalDiscounts, 0)) * 100, 2) AS DiscountRatePct,
        -- Product cost as % of revenue
        ROUND((TotalProductCost / NULLIF(TotalRevenue, 0)) * 100, 2) AS ProductCostPct,
        -- Total cost as % of revenue
        ROUND(((TotalProductCost + TotalFreight) / NULLIF(TotalRevenue, 0)) * 100, 2) AS TotalCostPct
    FROM TerritoryMetrics
),
TerritoryRankings AS (
    SELECT
        *,
        RANK() OVER (PARTITION BY CalendarYear, CalendarQuarter ORDER BY GrossProfit DESC) AS ProfitRank,
        RANK() OVER (PARTITION BY CalendarYear, CalendarQuarter ORDER BY GrossMarginPct DESC) AS MarginRank,
        RANK() OVER (PARTITION BY CalendarYear, CalendarQuarter ORDER BY TotalRevenue DESC) AS RevenueRank,
        RANK() OVER (PARTITION BY CalendarYear, CalendarQuarter ORDER BY TotalCostToServe DESC) AS CostRank
    FROM TerritoryProfitability
),
TerritoryAggregates AS (
    SELECT
        Territory,
        Country,
        TerritoryGroup,
        CalendarYear,
        COUNT(DISTINCT CASE WHEN StateProvince IS NOT NULL THEN StateProvince END) AS StateCount,
        COUNT(DISTINCT CASE WHEN City IS NOT NULL THEN City END) AS CityCount,
        SUM(UniqueCustomers) AS TerritoryCustomers,
        SUM(TotalOrders) AS TerritoryOrders,
        ROUND(SUM(TotalRevenue), 2) AS TerritoryRevenue,
        ROUND(SUM(TotalProductCost), 2) AS TerritoryProductCost,
        ROUND(SUM(TotalFreight), 2) AS TerritoryFreight,
        ROUND(SUM(GrossProfit), 2) AS TerritoryProfit,
        ROUND(AVG(GrossMarginPct), 2) AS AvgMarginPct,
        ROUND(AVG(FreightCostPct), 2) AS AvgFreightCostPct,
        ROUND(AVG(DiscountRatePct), 2) AS AvgDiscountRate,
        ROUND(SUM(TotalRevenue) / NULLIF(SUM(UniqueCustomers), 0), 2) AS RevenuePerCustomer,
        ROUND(SUM(GrossProfit) / NULLIF(SUM(UniqueCustomers), 0), 2) AS ProfitPerCustomer,
        ROUND(SUM(TotalCostToServe) / NULLIF(SUM(TotalOrders), 0), 2) AS AvgCostPerOrder
    FROM TerritoryProfitability
    GROUP BY Territory, Country, TerritoryGroup, CalendarYear
),
CostDriverAnalysis AS (
    SELECT
        Territory,
        TerritoryGroup,
        CASE
            WHEN FreightCostPct >= 5 THEN 'High Freight Cost (5%+)'
            WHEN FreightCostPct >= 3 THEN 'Medium Freight Cost (3-5%)'
            ELSE 'Low Freight Cost (<3%)'
        END AS FreightCostCategory,
        CASE
            WHEN GrossMarginPct >= 40 THEN 'High Margin (40%+)'
            WHEN GrossMarginPct >= 30 THEN 'Medium Margin (30-40%)'
            ELSE 'Low Margin (<30%)'
        END AS MarginCategory,
        COUNT(DISTINCT StateProvince || '-' || City) AS LocationCount,
        SUM(UniqueCustomers) AS CustomerCount,
        ROUND(SUM(TotalRevenue), 2) AS SegmentRevenue,
        ROUND(SUM(GrossProfit), 2) AS SegmentProfit,
        ROUND(AVG(GrossMarginPct), 2) AS AvgMargin,
        ROUND(AVG(FreightPerOrder), 2) AS AvgFreightPerOrder,
        ROUND(AVG(ProfitPerCustomer), 2) AS AvgProfitPerCustomer
    FROM TerritoryProfitability
    WHERE CalendarYear = (SELECT MAX(CalendarYear) FROM TerritoryProfitability)
    GROUP BY
        Territory, TerritoryGroup,
        CASE
            WHEN FreightCostPct >= 5 THEN 'High Freight Cost (5%+)'
            WHEN FreightCostPct >= 3 THEN 'Medium Freight Cost (3-5%)'
            ELSE 'Low Freight Cost (<3%)'
        END,
        CASE
            WHEN GrossMarginPct >= 40 THEN 'High Margin (40%+)'
            WHEN GrossMarginPct >= 30 THEN 'Medium Margin (30-40%)'
            ELSE 'Low Margin (<30%)'
        END
)
SELECT
    'Territory Detail' AS ReportSection,
    tr.Territory,
    tr.Country,
    tr.TerritoryGroup,
    tr.StateProvince,
    tr.City,
    tr.Category,
    tr.CalendarYear,
    tr.CalendarQuarter,
    tr.UniqueCustomers,
    tr.TotalOrders,
    tr.TotalRevenue,
    tr.TotalProductCost,
    tr.TotalFreight,
    tr.TotalCostToServe,
    tr.GrossProfit,
    tr.GrossMarginPct,
    tr.RevenuePerCustomer,
    tr.ProfitPerCustomer,
    tr.ProfitPerOrder,
    tr.FreightPerOrder,
    tr.FreightCostPct,
    tr.DiscountRatePct,
    tr.ProfitRank,
    tr.MarginRank,
    NULL AS StateCount,
    NULL AS TerritoryCustomers,
    NULL AS TerritoryProfit,
    NULL AS FreightCostCategory,
    NULL AS MarginCategory
FROM TerritoryRankings tr
WHERE tr.CalendarYear = (SELECT MAX(CalendarYear) FROM TerritoryRankings)
    AND tr.ProfitRank <= 50  -- Top 50 profitable territory-category combinations

UNION ALL

SELECT
    'Territory Aggregate' AS ReportSection,
    ta.Territory,
    ta.Country,
    ta.TerritoryGroup,
    NULL AS StateProvince,
    NULL AS City,
    NULL AS Category,
    ta.CalendarYear,
    NULL AS CalendarQuarter,
    ta.TerritoryCustomers AS UniqueCustomers,
    ta.TerritoryOrders AS TotalOrders,
    ta.TerritoryRevenue AS TotalRevenue,
    ta.TerritoryProductCost AS TotalProductCost,
    ta.TerritoryFreight AS TotalFreight,
    ta.TerritoryProductCost + ta.TerritoryFreight AS TotalCostToServe,
    ta.TerritoryProfit AS GrossProfit,
    ta.AvgMarginPct AS GrossMarginPct,
    ta.RevenuePerCustomer,
    ta.ProfitPerCustomer,
    NULL AS ProfitPerOrder,
    NULL AS FreightPerOrder,
    ta.AvgFreightCostPct AS FreightCostPct,
    ta.AvgDiscountRate AS DiscountRatePct,
    NULL AS ProfitRank,
    NULL AS MarginRank,
    ta.StateCount,
    ta.TerritoryCustomers,
    ta.TerritoryProfit,
    NULL AS FreightCostCategory,
    NULL AS MarginCategory
FROM TerritoryAggregates ta
WHERE ta.CalendarYear = (SELECT MAX(CalendarYear) FROM TerritoryAggregates)

UNION ALL

SELECT
    'Cost Driver Analysis' AS ReportSection,
    cda.Territory,
    NULL AS Country,
    cda.TerritoryGroup,
    NULL AS StateProvince,
    NULL AS City,
    NULL AS Category,
    NULL AS CalendarYear,
    NULL AS CalendarQuarter,
    cda.CustomerCount AS UniqueCustomers,
    NULL AS TotalOrders,
    cda.SegmentRevenue AS TotalRevenue,
    NULL AS TotalProductCost,
    NULL AS TotalFreight,
    NULL AS TotalCostToServe,
    cda.SegmentProfit AS GrossProfit,
    cda.AvgMargin AS GrossMarginPct,
    NULL AS RevenuePerCustomer,
    cda.AvgProfitPerCustomer AS ProfitPerCustomer,
    NULL AS ProfitPerOrder,
    cda.AvgFreightPerOrder AS FreightPerOrder,
    NULL AS FreightCostPct,
    NULL AS DiscountRatePct,
    NULL AS ProfitRank,
    NULL AS MarginRank,
    NULL AS StateCount,
    NULL AS TerritoryCustomers,
    NULL AS TerritoryProfit,
    cda.FreightCostCategory,
    cda.MarginCategory
FROM CostDriverAnalysis cda

ORDER BY ReportSection, GrossProfit DESC NULLS LAST, TotalRevenue DESC NULLS LAST;
```

---

## Summary

These five business questions provide a comprehensive framework for cost analysis:

1. **Product Profitability Analysis** - Understanding which products deliver the best margins and identifying portfolio optimization opportunities
2. **Channel Cost Structure Comparison** - Comparing Internet vs. Reseller economics to optimize channel strategy
3. **Cost Trend Analysis** - Tracking cost changes over time to manage margin compression and identify cost volatility
4. **Inventory Carrying Cost Analysis** - Optimizing working capital by identifying slow-moving inventory and excess stock
5. **Geographic Cost-to-Serve** - Understanding regional profitability differences to guide territory investment and pricing

Each query demonstrates advanced analytical techniques including:
- Multi-dimensional cost aggregations
- Gross profit and margin calculations
- Cost variance and trend analysis
- Segmentation strategies (margin tiers, volume segments, cost categories)
- Ranking and comparative analysis
- Unit economics calculations (cost per order, profit per customer)
- Time-series analysis with MoM and YoY comparisons
- Inventory turnover and carrying cost modeling
- Channel and geography profitability comparisons

These analyses enable data-driven decisions for:
- Pricing strategy optimization
- Product portfolio management
- Cost reduction initiatives
- Channel resource allocation
- Inventory optimization
- Territory investment prioritization
- Margin improvement programs
- Strategic sourcing and procurement

The insights from cost analysis provide the foundation for profitability management and competitive advantage through operational efficiency.
