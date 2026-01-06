# Reseller Performance Analysis - Business Questions

## Introduction

Reseller channel management is critical for indirect sales success, requiring sophisticated analysis of partner performance, relationship health, and strategic alignment. Effective reseller analytics enables organizations to optimize channel partner selection, incentive programs, territory assignments, and support investments to maximize channel revenue and profitability.

This document presents a comprehensive reseller analysis framework using the AdventureWorks data warehouse. The analysis leverages the FactResellerSales fact table combined with the DimReseller dimension and related tables to examine reseller performance from multiple perspectives.

**Key DimReseller Attributes:**
- **Business characteristics**: BusinessType, NumberEmployees, ProductLine
- **Order patterns**: OrderFrequency, OrderMonth, FirstOrderYear, LastOrderYear
- **Financial profile**: AnnualSales, AnnualRevenue, MinPaymentType, MinPaymentAmount
- **Company information**: YearOpened, BankName
- **Geography**: GeographyKey → DimGeography → DimSalesTerritory

**FactResellerSales Metrics:**
- **Sales volume**: OrderQuantity, SalesAmount, ExtendedAmount
- **Costs and margins**: TotalProductCost, ProductStandardCost, UnitPrice
- **Discounts**: DiscountAmount, UnitPriceDiscountPct
- **Relationships**: EmployeeKey (sales rep), ProductKey, SalesTerritoryKey

The following business questions explore critical reseller channel analysis areas including:
- Reseller performance ranking and segmentation
- Business type and characteristic analysis
- Product portfolio and category preferences
- Sales representative effectiveness
- Reseller lifecycle and growth trends
- Geographic and territory optimization

These analyses provide actionable insights for channel managers, sales leadership, and partner development teams to drive channel excellence and mutual profitability.

---

# Business Question 1: Reseller Performance Ranking and Tiering Analysis

## Intent

Analyze and rank reseller partners by performance to create strategic tiers for differentiated support and incentive programs. This comprehensive reseller performance analysis provides:
- Revenue, order volume, and profitability rankings by reseller
- Multi-dimensional performance scoring across key metrics
- Reseller segmentation into strategic tiers (Platinum, Gold, Silver, Bronze)
- Growth trajectory and momentum indicators
- Product diversity and cross-selling metrics
- Territory coverage and geographic concentration
- Performance consistency and volatility measures

Understanding reseller tiers enables strategic resource allocation, tailored support programs, differentiated incentives, and focused partner development investments. This analysis identifies top performers deserving premium treatment and underperformers requiring intervention or exit.

## SQL Code

```sql
WITH ResellerSalesMetrics AS (
    SELECT
        dr.ResellerKey,
        dr.ResellerName,
        dr.BusinessType,
        dr.NumberEmployees,
        dr.OrderFrequency,
        dr.AnnualSales AS ResellerDeclaredSales,
        dr.AnnualRevenue AS ResellerDeclaredRevenue,
        dr.FirstOrderYear,
        dr.LastOrderYear,
        dr.YearOpened,
        g.StateProvinceName,
        g.EnglishCountryRegionName AS Country,
        st.SalesTerritoryRegion,
        dd.CalendarYear,
        dd.CalendarQuarter,
        COUNT(DISTINCT frs.SalesOrderNumber) AS TotalOrders,
        SUM(frs.OrderQuantity) AS TotalQuantity,
        SUM(frs.SalesAmount) AS TotalRevenue,
        SUM(frs.TotalProductCost) AS TotalCost,
        SUM(frs.DiscountAmount) AS TotalDiscounts,
        AVG(frs.UnitPrice) AS AvgUnitPrice,
        AVG(frs.SalesAmount) AS AvgOrderValue,
        COUNT(DISTINCT frs.ProductKey) AS UniqueProducts,
        COUNT(DISTINCT frs.EmployeeKey) AS SalesRepsServing,
        COUNT(DISTINCT pc.ProductCategoryKey) AS ProductCategories
    FROM FactResellerSales frs
    INNER JOIN DimReseller dr ON frs.ResellerKey = dr.ResellerKey
    INNER JOIN DimGeography g ON dr.GeographyKey = g.GeographyKey
    INNER JOIN DimSalesTerritory st ON g.SalesTerritoryKey = st.SalesTerritoryKey
    INNER JOIN DimDate dd ON frs.OrderDateKey = dd.DateKey
    INNER JOIN DimProduct p ON frs.ProductKey = p.ProductKey
    INNER JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    INNER JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    GROUP BY
        dr.ResellerKey, dr.ResellerName, dr.BusinessType, dr.NumberEmployees,
        dr.OrderFrequency, dr.AnnualSales, dr.AnnualRevenue,
        dr.FirstOrderYear, dr.LastOrderYear, dr.YearOpened,
        g.StateProvinceName, g.EnglishCountryRegionName,
        st.SalesTerritoryRegion, dd.CalendarYear, dd.CalendarQuarter
),
ResellerProfitability AS (
    SELECT
        rsm.*,
        rsm.TotalRevenue - rsm.TotalCost AS GrossProfit,
        ROUND(((rsm.TotalRevenue - rsm.TotalCost) / NULLIF(rsm.TotalRevenue, 0)) * 100, 2) AS GrossMarginPct,
        ROUND(rsm.TotalRevenue / NULLIF(rsm.TotalOrders, 0), 2) AS RevenuePerOrder,
        ROUND((rsm.TotalRevenue - rsm.TotalCost) / NULLIF(rsm.TotalOrders, 0), 2) AS ProfitPerOrder,
        ROUND(rsm.TotalDiscounts / NULLIF(rsm.TotalRevenue + rsm.TotalDiscounts, 0) * 100, 2) AS DiscountRatePct,
        ROUND(rsm.TotalRevenue / NULLIF(rsm.NumberEmployees, 0), 2) AS RevenuePerEmployee,
        rsm.CalendarYear - rsm.YearOpened AS YearsInBusiness,
        rsm.CalendarYear - rsm.FirstOrderYear AS YearsAsPartner
    FROM ResellerSalesMetrics rsm
),
AnnualResellerSummary AS (
    SELECT
        ResellerKey,
        ResellerName,
        BusinessType,
        NumberEmployees,
        OrderFrequency,
        Country,
        SalesTerritoryRegion,
        CalendarYear,
        YearsInBusiness,
        YearsAsPartner,
        SUM(TotalOrders) AS AnnualOrders,
        SUM(TotalQuantity) AS AnnualQuantity,
        ROUND(SUM(TotalRevenue), 2) AS AnnualRevenue,
        ROUND(SUM(GrossProfit), 2) AS AnnualProfit,
        ROUND(AVG(GrossMarginPct), 2) AS AvgGrossMarginPct,
        ROUND(AVG(RevenuePerOrder), 2) AS AvgRevenuePerOrder,
        MAX(UniqueProducts) AS UniqueProducts,
        MAX(ProductCategories) AS ProductCategories,
        MAX(SalesRepsServing) AS SalesRepsServing,
        ROUND(AVG(DiscountRatePct), 2) AS AvgDiscountRate,
        LAG(SUM(TotalRevenue), 1) OVER (
            PARTITION BY ResellerKey ORDER BY CalendarYear
        ) AS PrevYearRevenue
    FROM ResellerProfitability
    GROUP BY
        ResellerKey, ResellerName, BusinessType, NumberEmployees,
        OrderFrequency, Country, SalesTerritoryRegion,
        CalendarYear, YearsInBusiness, YearsAsPartner
),
ResellerGrowth AS (
    SELECT
        *,
        CASE
            WHEN PrevYearRevenue IS NOT NULL AND PrevYearRevenue > 0
            THEN ROUND(((AnnualRevenue - PrevYearRevenue) / PrevYearRevenue) * 100, 2)
            ELSE NULL
        END AS YoYGrowthPct,
        ROUND(STDEV(AnnualRevenue) OVER (
            PARTITION BY ResellerKey
            ORDER BY CalendarYear
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 2) AS RevenueVolatility
    FROM AnnualResellerSummary
),
CurrentYearMetrics AS (
    SELECT
        ResellerKey,
        ResellerName,
        BusinessType,
        NumberEmployees,
        OrderFrequency,
        Country,
        SalesTerritoryRegion,
        YearsInBusiness,
        YearsAsPartner,
        AnnualOrders,
        AnnualRevenue,
        AnnualProfit,
        AvgGrossMarginPct,
        AvgRevenuePerOrder,
        UniqueProducts,
        ProductCategories,
        YoYGrowthPct,
        RevenueVolatility,
        -- Performance scoring components
        NTILE(5) OVER (ORDER BY AnnualRevenue DESC) AS RevenueQuintile,
        NTILE(5) OVER (ORDER BY AnnualProfit DESC) AS ProfitQuintile,
        NTILE(5) OVER (ORDER BY YoYGrowthPct DESC) AS GrowthQuintile,
        NTILE(5) OVER (ORDER BY AvgGrossMarginPct DESC) AS MarginQuintile,
        NTILE(5) OVER (ORDER BY UniqueProducts DESC) AS DiversityQuintile
    FROM ResellerGrowth
    WHERE CalendarYear = (SELECT MAX(CalendarYear) FROM ResellerGrowth)
),
PerformanceScoring AS (
    SELECT
        *,
        -- Composite performance score (lower quintiles are better)
        (6 - RevenueQuintile) * 3 +  -- Revenue weighted 3x
        (6 - ProfitQuintile) * 2 +   -- Profit weighted 2x
        (6 - GrowthQuintile) * 2 +   -- Growth weighted 2x
        (6 - MarginQuintile) * 1 +   -- Margin weighted 1x
        (6 - DiversityQuintile) * 1  -- Diversity weighted 1x
        AS PerformanceScore,
        RANK() OVER (ORDER BY AnnualRevenue DESC) AS RevenueRank,
        RANK() OVER (ORDER BY AnnualProfit DESC) AS ProfitRank,
        RANK() OVER (ORDER BY YoYGrowthPct DESC) AS GrowthRank
    FROM CurrentYearMetrics
),
ResellerTiering AS (
    SELECT
        *,
        CASE
            WHEN PerformanceScore >= 36 THEN 'Platinum Partner'
            WHEN PerformanceScore >= 27 THEN 'Gold Partner'
            WHEN PerformanceScore >= 18 THEN 'Silver Partner'
            WHEN PerformanceScore >= 9 THEN 'Bronze Partner'
            ELSE 'Standard Partner'
        END AS PartnerTier,
        CASE
            WHEN YoYGrowthPct >= 20 THEN 'High Growth'
            WHEN YoYGrowthPct >= 5 THEN 'Growing'
            WHEN YoYGrowthPct >= -5 THEN 'Stable'
            WHEN YoYGrowthPct >= -20 THEN 'Declining'
            ELSE 'At Risk'
        END AS GrowthStatus,
        CASE
            WHEN YearsAsPartner >= 5 THEN 'Established'
            WHEN YearsAsPartner >= 2 THEN 'Mature'
            WHEN YearsAsPartner >= 1 THEN 'Growing'
            ELSE 'New Partner'
        END AS PartnerMaturity
    FROM PerformanceScoring
),
TierSummary AS (
    SELECT
        PartnerTier,
        BusinessType,
        COUNT(DISTINCT ResellerKey) AS ResellerCount,
        ROUND(SUM(AnnualRevenue), 2) AS TierRevenue,
        ROUND(SUM(AnnualProfit), 2) AS TierProfit,
        ROUND(AVG(AnnualRevenue), 2) AS AvgRevenuePerReseller,
        ROUND(AVG(AvgGrossMarginPct), 2) AS AvgMargin,
        ROUND(AVG(YoYGrowthPct), 2) AS AvgGrowth,
        ROUND(AVG(PerformanceScore), 2) AS AvgPerformanceScore
    FROM ResellerTiering
    GROUP BY PartnerTier, BusinessType
)
SELECT
    'Reseller Performance Detail' AS ReportSection,
    rt.ResellerName,
    rt.BusinessType,
    rt.Country,
    rt.SalesTerritoryRegion,
    rt.PartnerTier,
    rt.PartnerMaturity,
    rt.GrowthStatus,
    rt.NumberEmployees,
    rt.YearsInBusiness,
    rt.YearsAsPartner,
    rt.AnnualOrders,
    rt.AnnualRevenue,
    rt.AnnualProfit,
    rt.AvgGrossMarginPct,
    rt.AvgRevenuePerOrder,
    rt.UniqueProducts,
    rt.ProductCategories,
    rt.YoYGrowthPct,
    rt.PerformanceScore,
    rt.RevenueRank,
    rt.ProfitRank,
    rt.GrowthRank,
    NULL AS ResellerCount,
    NULL AS TierRevenue,
    NULL AS AvgRevenuePerReseller
FROM ResellerTiering rt
WHERE rt.RevenueRank <= 100  -- Top 100 resellers

UNION ALL

SELECT
    'Tier Summary' AS ReportSection,
    NULL AS ResellerName,
    ts.BusinessType,
    NULL AS Country,
    NULL AS SalesTerritoryRegion,
    ts.PartnerTier,
    NULL AS PartnerMaturity,
    NULL AS GrowthStatus,
    NULL AS NumberEmployees,
    NULL AS YearsInBusiness,
    NULL AS YearsAsPartner,
    NULL AS AnnualOrders,
    NULL AS AnnualRevenue,
    NULL AS AnnualProfit,
    ts.AvgMargin AS AvgGrossMarginPct,
    NULL AS AvgRevenuePerOrder,
    NULL AS UniqueProducts,
    NULL AS ProductCategories,
    ts.AvgGrowth AS YoYGrowthPct,
    ts.AvgPerformanceScore AS PerformanceScore,
    NULL AS RevenueRank,
    NULL AS ProfitRank,
    NULL AS GrowthRank,
    ts.ResellerCount,
    ts.TierRevenue,
    ts.AvgRevenuePerReseller
FROM TierSummary ts

ORDER BY ReportSection, PartnerTier, RevenueRank NULLS LAST, TierRevenue DESC NULLS LAST;
```

---

# Business Question 2: Reseller Business Type and Characteristic Analysis

## Intent

Analyze reseller performance patterns by business type and operational characteristics to identify ideal partner profiles and inform recruitment strategies. This analysis provides:
- Performance comparison across business types (Specialty Store, Value Added Reseller, Warehouse, etc.)
- Correlation between company size (NumberEmployees) and performance
- Order frequency patterns and their impact on revenue
- Product line alignment and specialization effects
- Geographic distribution by business type
- Optimal partner profile identification
- Business type-specific success factors

Understanding business type dynamics enables targeted partner recruitment, customized support programs by segment, realistic performance expectations, and strategic channel mix optimization.

## SQL Code

```sql
WITH ResellerCharacteristics AS (
    SELECT
        dr.ResellerKey,
        dr.ResellerName,
        dr.BusinessType,
        dr.NumberEmployees,
        dr.OrderFrequency,
        dr.ProductLine AS PreferredProductLine,
        dr.AnnualSales,
        dr.YearOpened,
        g.EnglishCountryRegionName AS Country,
        st.SalesTerritoryRegion,
        dd.CalendarYear,
        SUM(frs.SalesAmount) AS TotalRevenue,
        SUM(frs.TotalProductCost) AS TotalCost,
        SUM(frs.OrderQuantity) AS TotalQuantity,
        COUNT(DISTINCT frs.SalesOrderNumber) AS OrderCount,
        AVG(frs.SalesAmount) AS AvgOrderValue,
        COUNT(DISTINCT frs.ProductKey) AS UniqueProducts,
        COUNT(DISTINCT pc.ProductCategoryKey) AS ProductCategories
    FROM FactResellerSales frs
    INNER JOIN DimReseller dr ON frs.ResellerKey = dr.ResellerKey
    INNER JOIN DimGeography g ON dr.GeographyKey = g.GeographyKey
    INNER JOIN DimSalesTerritory st ON g.SalesTerritoryKey = st.SalesTerritoryKey
    INNER JOIN DimDate dd ON frs.OrderDateKey = dd.DateKey
    INNER JOIN DimProduct p ON frs.ProductKey = p.ProductKey
    INNER JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    INNER JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    GROUP BY
        dr.ResellerKey, dr.ResellerName, dr.BusinessType, dr.NumberEmployees,
        dr.OrderFrequency, dr.ProductLine, dr.AnnualSales, dr.YearOpened,
        g.EnglishCountryRegionName, st.SalesTerritoryRegion, dd.CalendarYear
),
ResellerMetrics AS (
    SELECT
        *,
        TotalRevenue - TotalCost AS GrossProfit,
        ROUND(((TotalRevenue - TotalCost) / NULLIF(TotalRevenue, 0)) * 100, 2) AS GrossMarginPct,
        ROUND(TotalRevenue / NULLIF(NumberEmployees, 0), 2) AS RevenuePerEmployee,
        ROUND((TotalRevenue - TotalCost) / NULLIF(NumberEmployees, 0), 2) AS ProfitPerEmployee,
        CASE
            WHEN NumberEmployees <= 10 THEN 'Micro (1-10)'
            WHEN NumberEmployees <= 50 THEN 'Small (11-50)'
            WHEN NumberEmployees <= 250 THEN 'Medium (51-250)'
            ELSE 'Large (251+)'
        END AS CompanySize,
        CalendarYear - YearOpened AS YearsInBusiness
    FROM ResellerCharacteristics
    WHERE CalendarYear = (SELECT MAX(CalendarYear) FROM ResellerCharacteristics WHERE CalendarYear IS NOT NULL)
),
BusinessTypeAnalysis AS (
    SELECT
        BusinessType,
        COUNT(DISTINCT ResellerKey) AS ResellerCount,
        ROUND(SUM(TotalRevenue), 2) AS TotalRevenue,
        ROUND(SUM(GrossProfit), 2) AS TotalProfit,
        ROUND(AVG(TotalRevenue), 2) AS AvgRevenuePerReseller,
        ROUND(AVG(GrossProfit), 2) AS AvgProfitPerReseller,
        ROUND(AVG(GrossMarginPct), 2) AS AvgMargin,
        ROUND(AVG(OrderCount), 2) AS AvgOrders,
        ROUND(AVG(AvgOrderValue), 2) AS AvgOrderValue,
        ROUND(AVG(NumberEmployees), 2) AS AvgEmployees,
        ROUND(AVG(RevenuePerEmployee), 2) AS AvgRevenuePerEmployee,
        ROUND(AVG(UniqueProducts), 2) AS AvgProductDiversity,
        ROUND(AVG(YearsInBusiness), 2) AS AvgYearsInBusiness,
        ROUND(SUM(TotalRevenue) / SUM(SUM(TotalRevenue)) OVER () * 100, 2) AS PctOfTotalRevenue,
        RANK() OVER (ORDER BY SUM(TotalRevenue) DESC) AS RevenueRank
    FROM ResellerMetrics
    GROUP BY BusinessType
),
SizeAnalysis AS (
    SELECT
        CompanySize,
        BusinessType,
        COUNT(DISTINCT ResellerKey) AS ResellerCount,
        ROUND(SUM(TotalRevenue), 2) AS TotalRevenue,
        ROUND(AVG(TotalRevenue), 2) AS AvgRevenue,
        ROUND(AVG(GrossMarginPct), 2) AS AvgMargin,
        ROUND(AVG(RevenuePerEmployee), 2) AS AvgRevenuePerEmployee,
        ROUND(AVG(UniqueProducts), 2) AS AvgProductDiversity
    FROM ResellerMetrics
    GROUP BY CompanySize, BusinessType
),
FrequencyAnalysis AS (
    SELECT
        OrderFrequency,
        BusinessType,
        COUNT(DISTINCT ResellerKey) AS ResellerCount,
        ROUND(SUM(TotalRevenue), 2) AS TotalRevenue,
        ROUND(AVG(TotalRevenue), 2) AS AvgRevenue,
        ROUND(AVG(OrderCount), 2) AS AvgOrders,
        ROUND(AVG(AvgOrderValue), 2) AS AvgOrderValue,
        ROUND(AVG(GrossMarginPct), 2) AS AvgMargin
    FROM ResellerMetrics
    GROUP BY OrderFrequency, BusinessType
),
GeographicDistribution AS (
    SELECT
        BusinessType,
        Country,
        SalesTerritoryRegion,
        COUNT(DISTINCT ResellerKey) AS ResellerCount,
        ROUND(SUM(TotalRevenue), 2) AS TotalRevenue,
        ROUND(AVG(TotalRevenue), 2) AS AvgRevenue
    FROM ResellerMetrics
    GROUP BY BusinessType, Country, SalesTerritoryRegion
),
ProductLineAlignment AS (
    SELECT
        PreferredProductLine,
        BusinessType,
        COUNT(DISTINCT ResellerKey) AS ResellerCount,
        ROUND(SUM(TotalRevenue), 2) AS TotalRevenue,
        ROUND(AVG(TotalRevenue), 2) AS AvgRevenue,
        ROUND(AVG(GrossMarginPct), 2) AS AvgMargin,
        ROUND(AVG(UniqueProducts), 2) AS AvgProductDiversity
    FROM ResellerMetrics
    WHERE PreferredProductLine IS NOT NULL
    GROUP BY PreferredProductLine, BusinessType
)
SELECT
    'Business Type Performance' AS ReportSection,
    bta.BusinessType,
    bta.ResellerCount,
    bta.TotalRevenue,
    bta.TotalProfit,
    bta.AvgRevenuePerReseller,
    bta.AvgProfitPerReseller,
    bta.AvgMargin,
    bta.AvgOrders,
    bta.AvgOrderValue,
    bta.AvgEmployees,
    bta.AvgRevenuePerEmployee,
    bta.AvgProductDiversity,
    bta.AvgYearsInBusiness,
    bta.PctOfTotalRevenue,
    bta.RevenueRank,
    NULL AS CompanySize,
    NULL AS OrderFrequency,
    NULL AS Country,
    NULL AS PreferredProductLine
FROM BusinessTypeAnalysis bta

UNION ALL

SELECT
    'Size Analysis' AS ReportSection,
    sa.BusinessType,
    sa.ResellerCount,
    sa.TotalRevenue,
    NULL AS TotalProfit,
    sa.AvgRevenue AS AvgRevenuePerReseller,
    NULL AS AvgProfitPerReseller,
    sa.AvgMargin,
    NULL AS AvgOrders,
    NULL AS AvgOrderValue,
    NULL AS AvgEmployees,
    sa.AvgRevenuePerEmployee,
    sa.AvgProductDiversity,
    NULL AS AvgYearsInBusiness,
    NULL AS PctOfTotalRevenue,
    NULL AS RevenueRank,
    sa.CompanySize,
    NULL AS OrderFrequency,
    NULL AS Country,
    NULL AS PreferredProductLine
FROM SizeAnalysis sa

UNION ALL

SELECT
    'Frequency Analysis' AS ReportSection,
    fa.BusinessType,
    fa.ResellerCount,
    fa.TotalRevenue,
    NULL AS TotalProfit,
    fa.AvgRevenue AS AvgRevenuePerReseller,
    NULL AS AvgProfitPerReseller,
    fa.AvgMargin,
    fa.AvgOrders,
    fa.AvgOrderValue,
    NULL AS AvgEmployees,
    NULL AS AvgRevenuePerEmployee,
    NULL AS AvgProductDiversity,
    NULL AS AvgYearsInBusiness,
    NULL AS PctOfTotalRevenue,
    NULL AS RevenueRank,
    NULL AS CompanySize,
    fa.OrderFrequency,
    NULL AS Country,
    NULL AS PreferredProductLine
FROM FrequencyAnalysis fa

UNION ALL

SELECT
    'Product Line Alignment' AS ReportSection,
    pla.BusinessType,
    pla.ResellerCount,
    pla.TotalRevenue,
    NULL AS TotalProfit,
    pla.AvgRevenue AS AvgRevenuePerReseller,
    NULL AS AvgProfitPerReseller,
    pla.AvgMargin,
    NULL AS AvgOrders,
    NULL AS AvgOrderValue,
    NULL AS AvgEmployees,
    NULL AS AvgRevenuePerEmployee,
    pla.AvgProductDiversity,
    NULL AS AvgYearsInBusiness,
    NULL AS PctOfTotalRevenue,
    NULL AS RevenueRank,
    NULL AS CompanySize,
    NULL AS OrderFrequency,
    NULL AS Country,
    pla.PreferredProductLine
FROM ProductLineAlignment pla

ORDER BY ReportSection, TotalRevenue DESC NULLS LAST;
```

---

# Business Question 3: Reseller Product Portfolio and Category Affinity Analysis

## Intent

Analyze product purchasing patterns by reseller to identify category specialization, cross-selling opportunities, and portfolio optimization strategies. This analysis provides:
- Product category mix and concentration by reseller
- Identification of specialized vs. generalist resellers
- Category revenue contribution and profitability
- Cross-selling penetration rates
- Product category correlation and complementary sales
- Under-penetrated categories representing opportunities
- Portfolio diversity metrics and risk assessment

Understanding product affinity enables targeted product training, optimized inventory recommendations, category-specific incentives, and identification of white-space opportunities for account development.

## SQL Code

```sql
WITH ResellerProductSales AS (
    SELECT
        dr.ResellerKey,
        dr.ResellerName,
        dr.BusinessType,
        pc.EnglishProductCategoryName AS ProductCategory,
        psc.EnglishProductSubcategoryName AS ProductSubcategory,
        dd.CalendarYear,
        COUNT(DISTINCT frs.SalesOrderNumber) AS CategoryOrders,
        SUM(frs.OrderQuantity) AS CategoryQuantity,
        SUM(frs.SalesAmount) AS CategoryRevenue,
        SUM(frs.TotalProductCost) AS CategoryCost,
        COUNT(DISTINCT frs.ProductKey) AS UniqueProducts,
        AVG(frs.UnitPrice) AS AvgUnitPrice
    FROM FactResellerSales frs
    INNER JOIN DimReseller dr ON frs.ResellerKey = dr.ResellerKey
    INNER JOIN DimProduct p ON frs.ProductKey = p.ProductKey
    INNER JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    INNER JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimDate dd ON frs.OrderDateKey = dd.DateKey
    GROUP BY
        dr.ResellerKey, dr.ResellerName, dr.BusinessType,
        pc.EnglishProductCategoryName, psc.EnglishProductSubcategoryName,
        dd.CalendarYear
),
ResellerTotalSales AS (
    SELECT
        ResellerKey,
        ResellerName,
        BusinessType,
        CalendarYear,
        SUM(CategoryRevenue) AS TotalRevenue,
        SUM(CategoryCost) AS TotalCost,
        SUM(CategoryOrders) AS TotalOrders,
        COUNT(DISTINCT ProductCategory) AS TotalCategories,
        COUNT(DISTINCT ProductSubcategory) AS TotalSubcategories
    FROM ResellerProductSales
    GROUP BY ResellerKey, ResellerName, BusinessType, CalendarYear
),
ResellerCategoryMetrics AS (
    SELECT
        rps.ResellerKey,
        rps.ResellerName,
        rps.BusinessType,
        rps.ProductCategory,
        rps.ProductSubcategory,
        rps.CalendarYear,
        rps.CategoryRevenue,
        rps.CategoryCost,
        rps.CategoryRevenue - rps.CategoryCost AS CategoryProfit,
        ROUND(((rps.CategoryRevenue - rps.CategoryCost) / NULLIF(rps.CategoryRevenue, 0)) * 100, 2) AS CategoryMarginPct,
        rps.CategoryOrders,
        rps.UniqueProducts,
        rts.TotalRevenue,
        rts.TotalCategories,
        rts.TotalSubcategories,
        ROUND((rps.CategoryRevenue / NULLIF(rts.TotalRevenue, 0)) * 100, 2) AS CategoryRevenueSharePct,
        ROUND((rps.CategoryOrders / NULLIF(rts.TotalOrders, 0)) * 100, 2) AS CategoryOrderSharePct
    FROM ResellerProductSales rps
    INNER JOIN ResellerTotalSales rts
        ON rps.ResellerKey = rts.ResellerKey
        AND rps.CalendarYear = rts.CalendarYear
),
ResellerSpecialization AS (
    SELECT
        ResellerKey,
        ResellerName,
        BusinessType,
        CalendarYear,
        TotalRevenue,
        TotalCategories,
        TotalSubcategories,
        -- Find dominant category
        (SELECT ProductCategory
         FROM ResellerCategoryMetrics rcm2
         WHERE rcm2.ResellerKey = rcm1.ResellerKey
           AND rcm2.CalendarYear = rcm1.CalendarYear
         ORDER BY CategoryRevenue DESC
         LIMIT 1) AS DominantCategory,
        -- Calculate concentration (max category share)
        MAX(CategoryRevenueSharePct) AS MaxCategoryShare,
        -- Calculate HHI (Herfindahl-Hirschman Index) for concentration
        ROUND(SUM(CategoryRevenueSharePct * CategoryRevenueSharePct), 2) AS ConcentrationIndex,
        CASE
            WHEN MAX(CategoryRevenueSharePct) >= 70 THEN 'Specialist'
            WHEN MAX(CategoryRevenueSharePct) >= 50 THEN 'Focused'
            WHEN MAX(CategoryRevenueSharePct) >= 35 THEN 'Diversified'
            ELSE 'Generalist'
        END AS SpecializationType,
        ROUND(AVG(CategoryMarginPct), 2) AS AvgMarginPct
    FROM ResellerCategoryMetrics rcm1
    GROUP BY ResellerKey, ResellerName, BusinessType, CalendarYear, TotalRevenue, TotalCategories, TotalSubcategories
),
CategoryPenetration AS (
    SELECT
        ProductCategory,
        CalendarYear,
        COUNT(DISTINCT ResellerKey) AS ResellersSelling,
        ROUND(SUM(CategoryRevenue), 2) AS TotalCategoryRevenue,
        ROUND(AVG(CategoryRevenue), 2) AS AvgRevenuePerReseller,
        ROUND(AVG(CategoryMarginPct), 2) AS AvgCategoryMargin
    FROM ResellerCategoryMetrics
    GROUP BY ProductCategory, CalendarYear
),
CrossCategoryOpportunities AS (
    SELECT
        r1.ResellerKey,
        r1.ResellerName,
        r1.BusinessType,
        r1.ProductCategory AS CurrentCategory,
        r2.ProductCategory AS OpportunityCategory,
        r1.CalendarYear,
        ROUND(r1.CategoryRevenue, 2) AS CurrentCategoryRevenue,
        ROUND(r2.CategoryRevenue, 2) AS AvgCompetitorRevenue,
        ROUND(r2.CategoryRevenue - r1.CategoryRevenue, 2) AS RevenueGap
    FROM ResellerCategoryMetrics r1
    CROSS JOIN (
        SELECT
            ProductCategory,
            CalendarYear,
            AVG(CategoryRevenue) AS CategoryRevenue
        FROM ResellerCategoryMetrics
        GROUP BY ProductCategory, CalendarYear
    ) r2
    WHERE r1.CalendarYear = r2.CalendarYear
      AND r1.ProductCategory != r2.ProductCategory
      AND r2.CategoryRevenue > r1.CategoryRevenue * 1.5
),
ResellerPortfolioScore AS (
    SELECT
        rs.*,
        CASE
            WHEN TotalCategories >= 3 THEN 'Full Portfolio'
            WHEN TotalCategories = 2 THEN 'Limited Portfolio'
            ELSE 'Single Category'
        END AS PortfolioScope,
        RANK() OVER (PARTITION BY CalendarYear ORDER BY TotalRevenue DESC) AS RevenueRank,
        RANK() OVER (PARTITION BY CalendarYear ORDER BY ConcentrationIndex DESC) AS ConcentrationRank
    FROM ResellerSpecialization rs
)
SELECT
    'Reseller Specialization' AS ReportSection,
    rps.ResellerName,
    rps.BusinessType,
    rps.SpecializationType,
    rps.PortfolioScope,
    rps.DominantCategory,
    rps.CalendarYear,
    ROUND(rps.TotalRevenue, 2) AS TotalRevenue,
    rps.TotalCategories,
    rps.TotalSubcategories,
    rps.MaxCategoryShare,
    rps.ConcentrationIndex,
    rps.AvgMarginPct,
    rps.RevenueRank,
    NULL AS ProductCategory,
    NULL AS CategoryRevenue,
    NULL AS CategoryMarginPct,
    NULL AS CategoryRevenueSharePct,
    NULL AS ResellersSelling,
    NULL AS OpportunityCategory,
    NULL AS RevenueGap
FROM ResellerPortfolioScore rps
WHERE rps.CalendarYear = (SELECT MAX(CalendarYear) FROM ResellerPortfolioScore)
    AND rps.RevenueRank <= 50

UNION ALL

SELECT
    'Category Detail by Reseller' AS ReportSection,
    rcm.ResellerName,
    rcm.BusinessType,
    NULL AS SpecializationType,
    NULL AS PortfolioScope,
    NULL AS DominantCategory,
    rcm.CalendarYear,
    NULL AS TotalRevenue,
    NULL AS TotalCategories,
    NULL AS TotalSubcategories,
    NULL AS MaxCategoryShare,
    NULL AS ConcentrationIndex,
    NULL AS AvgMarginPct,
    NULL AS RevenueRank,
    rcm.ProductCategory,
    ROUND(rcm.CategoryRevenue, 2) AS CategoryRevenue,
    rcm.CategoryMarginPct,
    rcm.CategoryRevenueSharePct,
    NULL AS ResellersSelling,
    NULL AS OpportunityCategory,
    NULL AS RevenueGap
FROM ResellerCategoryMetrics rcm
WHERE rcm.CalendarYear = (SELECT MAX(CalendarYear) FROM ResellerCategoryMetrics)
    AND rcm.CategoryRevenue > 10000

UNION ALL

SELECT
    'Category Penetration Analysis' AS ReportSection,
    NULL AS ResellerName,
    NULL AS BusinessType,
    NULL AS SpecializationType,
    NULL AS PortfolioScope,
    NULL AS DominantCategory,
    cp.CalendarYear,
    NULL AS TotalRevenue,
    NULL AS TotalCategories,
    NULL AS TotalSubcategories,
    NULL AS MaxCategoryShare,
    NULL AS ConcentrationIndex,
    NULL AS AvgMarginPct,
    NULL AS RevenueRank,
    cp.ProductCategory,
    cp.TotalCategoryRevenue AS CategoryRevenue,
    cp.AvgCategoryMargin AS CategoryMarginPct,
    NULL AS CategoryRevenueSharePct,
    cp.ResellersSelling,
    NULL AS OpportunityCategory,
    NULL AS RevenueGap
FROM CategoryPenetration cp
WHERE cp.CalendarYear = (SELECT MAX(CalendarYear) FROM CategoryPenetration)

ORDER BY ReportSection, RevenueRank NULLS LAST, CategoryRevenue DESC NULLS LAST, TotalRevenue DESC NULLS LAST;
```

---

# Business Question 4: Sales Representative Effectiveness with Reseller Accounts

## Intent

Analyze sales representative performance in managing reseller relationships to identify top performers and optimization opportunities. This employee-focused reseller analysis provides:
- Revenue and profitability by sales rep and reseller assignment
- Account portfolio size and complexity metrics
- Revenue per reseller (account productivity)
- Reseller satisfaction proxies (growth, retention)
- Territory coverage and span of control analysis
- Top performer identification and best practices
- Workload balance and capacity utilization

Understanding sales rep effectiveness enables performance management, territory optimization, training prioritization, compensation alignment, and strategic account assignment decisions to maximize channel productivity.

## SQL Code

```sql
WITH EmployeeResellerRelationships AS (
    SELECT
        de.EmployeeKey,
        CONCAT(de.FirstName, ' ', de.LastName) AS EmployeeName,
        de.Title AS JobTitle,
        de.DepartmentName,
        st.SalesTerritoryRegion AS Territory,
        dr.ResellerKey,
        dr.ResellerName,
        dr.BusinessType,
        dd.CalendarYear,
        dd.CalendarQuarter,
        COUNT(DISTINCT frs.SalesOrderNumber) AS Orders,
        SUM(frs.OrderQuantity) AS Quantity,
        SUM(frs.SalesAmount) AS Revenue,
        SUM(frs.TotalProductCost) AS Cost,
        AVG(frs.SalesAmount) AS AvgOrderValue,
        MIN(dd.FullDateAlternateKey) AS FirstSaleDate,
        MAX(dd.FullDateAlternateKey) AS LastSaleDate
    FROM FactResellerSales frs
    INNER JOIN DimEmployee de ON frs.EmployeeKey = de.EmployeeKey
    INNER JOIN DimSalesTerritory st ON de.SalesTerritoryKey = st.SalesTerritoryKey
    INNER JOIN DimReseller dr ON frs.ResellerKey = dr.ResellerKey
    INNER JOIN DimDate dd ON frs.OrderDateKey = dd.DateKey
    GROUP BY
        de.EmployeeKey, de.FirstName, de.LastName, de.Title,
        de.DepartmentName, st.SalesTerritoryRegion,
        dr.ResellerKey, dr.ResellerName, dr.BusinessType,
        dd.CalendarYear, dd.CalendarQuarter
),
EmployeePerformance AS (
    SELECT
        EmployeeKey,
        EmployeeName,
        JobTitle,
        DepartmentName,
        Territory,
        CalendarYear,
        COUNT(DISTINCT ResellerKey) AS ActiveResellers,
        SUM(Orders) AS TotalOrders,
        ROUND(SUM(Revenue), 2) AS TotalRevenue,
        ROUND(SUM(Cost), 2) AS TotalCost,
        ROUND(SUM(Revenue) - SUM(Cost), 2) AS GrossProfit,
        ROUND(((SUM(Revenue) - SUM(Cost)) / NULLIF(SUM(Revenue), 0)) * 100, 2) AS GrossMarginPct,
        ROUND(AVG(AvgOrderValue), 2) AS AvgOrderValue,
        ROUND(SUM(Revenue) / NULLIF(COUNT(DISTINCT ResellerKey), 0), 2) AS RevenuePerReseller,
        ROUND(SUM(Orders) / NULLIF(COUNT(DISTINCT ResellerKey), 0), 2) AS OrdersPerReseller,
        COUNT(DISTINCT BusinessType) AS BusinessTypesDiversity
    FROM EmployeeResellerRelationships
    GROUP BY
        EmployeeKey, EmployeeName, JobTitle, DepartmentName,
        Territory, CalendarYear
),
EmployeeRankings AS (
    SELECT
        *,
        RANK() OVER (PARTITION BY CalendarYear ORDER BY TotalRevenue DESC) AS RevenueRank,
        RANK() OVER (PARTITION BY CalendarYear ORDER BY GrossProfit DESC) AS ProfitRank,
        RANK() OVER (PARTITION BY CalendarYear ORDER BY RevenuePerReseller DESC) AS EfficiencyRank,
        RANK() OVER (PARTITION BY CalendarYear ORDER BY ActiveResellers DESC) AS PortfolioSizeRank,
        NTILE(4) OVER (PARTITION BY CalendarYear ORDER BY TotalRevenue DESC) AS PerformanceQuartile
    FROM EmployeePerformance
),
ResellerAccountHealth AS (
    SELECT
        err.EmployeeKey,
        err.EmployeeName,
        err.ResellerKey,
        err.ResellerName,
        err.BusinessType,
        err.CalendarYear,
        err.Revenue AS CurrentYearRevenue,
        LAG(err.Revenue, 1) OVER (
            PARTITION BY err.EmployeeKey, err.ResellerKey
            ORDER BY err.CalendarYear
        ) AS PrevYearRevenue,
        CASE
            WHEN LAG(err.Revenue, 1) OVER (
                PARTITION BY err.EmployeeKey, err.ResellerKey
                ORDER BY err.CalendarYear
            ) IS NOT NULL
            THEN ROUND(((err.Revenue - LAG(err.Revenue, 1) OVER (
                PARTITION BY err.EmployeeKey, err.ResellerKey
                ORDER BY err.CalendarYear
            )) / LAG(err.Revenue, 1) OVER (
                PARTITION BY err.EmployeeKey, err.ResellerKey
                ORDER BY err.CalendarYear
            )) * 100, 2)
            ELSE NULL
        END AS AccountGrowthPct,
        CAST(JULIANDAY(err.LastSaleDate) - JULIANDAY(err.FirstSaleDate) AS INTEGER) AS RelationshipDays
    FROM EmployeeResellerRelationships err
),
AccountHealthSummary AS (
    SELECT
        EmployeeKey,
        EmployeeName,
        CalendarYear,
        COUNT(DISTINCT ResellerKey) AS TotalAccounts,
        SUM(CASE WHEN AccountGrowthPct > 0 THEN 1 ELSE 0 END) AS GrowingAccounts,
        SUM(CASE WHEN AccountGrowthPct < 0 THEN 1 ELSE 0 END) AS DecliningAccounts,
        ROUND(AVG(AccountGrowthPct), 2) AS AvgAccountGrowth,
        ROUND(AVG(RelationshipDays), 0) AS AvgRelationshipDays,
        ROUND(AVG(CurrentYearRevenue), 2) AS AvgAccountRevenue
    FROM ResellerAccountHealth
    WHERE PrevYearRevenue IS NOT NULL
    GROUP BY EmployeeKey, EmployeeName, CalendarYear
),
TopAccountsByEmployee AS (
    SELECT
        EmployeeKey,
        EmployeeName,
        ResellerName,
        BusinessType,
        CalendarYear,
        ROUND(SUM(Revenue), 2) AS AccountRevenue,
        ROUND((SUM(Revenue) - SUM(Cost)), 2) AS AccountProfit,
        RANK() OVER (
            PARTITION BY EmployeeKey, CalendarYear
            ORDER BY SUM(Revenue) DESC
        ) AS AccountRank
    FROM EmployeeResellerRelationships
    GROUP BY
        EmployeeKey, EmployeeName, ResellerName,
        BusinessType, CalendarYear
)
SELECT
    'Employee Performance Summary' AS ReportSection,
    er.EmployeeName,
    er.JobTitle,
    er.Territory,
    er.CalendarYear,
    er.ActiveResellers,
    er.TotalOrders,
    er.TotalRevenue,
    er.GrossProfit,
    er.GrossMarginPct,
    er.RevenuePerReseller,
    er.OrdersPerReseller,
    er.BusinessTypesDiversity,
    er.RevenueRank,
    er.EfficiencyRank,
    er.PerformanceQuartile,
    ahs.GrowingAccounts,
    ahs.DecliningAccounts,
    ahs.AvgAccountGrowth,
    ahs.AvgRelationshipDays,
    NULL AS ResellerName,
    NULL AS BusinessType,
    NULL AS AccountRevenue,
    NULL AS AccountRank
FROM EmployeeRankings er
LEFT JOIN AccountHealthSummary ahs
    ON er.EmployeeKey = ahs.EmployeeKey
    AND er.CalendarYear = ahs.CalendarYear
WHERE er.CalendarYear = (SELECT MAX(CalendarYear) FROM EmployeeRankings)
    AND er.RevenueRank <= 20

UNION ALL

SELECT
    'Top Accounts by Employee' AS ReportSection,
    tae.EmployeeName,
    NULL AS JobTitle,
    NULL AS Territory,
    tae.CalendarYear,
    NULL AS ActiveResellers,
    NULL AS TotalOrders,
    NULL AS TotalRevenue,
    NULL AS GrossProfit,
    NULL AS GrossMarginPct,
    NULL AS RevenuePerReseller,
    NULL AS OrdersPerReseller,
    NULL AS BusinessTypesDiversity,
    NULL AS RevenueRank,
    NULL AS EfficiencyRank,
    NULL AS PerformanceQuartile,
    NULL AS GrowingAccounts,
    NULL AS DecliningAccounts,
    NULL AS AvgAccountGrowth,
    NULL AS AvgRelationshipDays,
    tae.ResellerName,
    tae.BusinessType,
    tae.AccountRevenue,
    tae.AccountRank
FROM TopAccountsByEmployee tae
WHERE tae.CalendarYear = (SELECT MAX(CalendarYear) FROM TopAccountsByEmployee)
    AND tae.AccountRank <= 5

ORDER BY ReportSection, RevenueRank NULLS LAST, AccountRank NULLS LAST;
```

---

# Business Question 5: Reseller Lifecycle and Growth Trajectory Analysis

## Intent

Analyze reseller partner lifecycle patterns from onboarding through maturity to identify growth phases, predict churn risk, and optimize partner development investments. This temporal reseller analysis provides:
- Partner age and lifecycle stage identification
- Revenue growth trajectories over partnership lifetime
- New partner onboarding success rates
- Partner maturity curves and revenue ramp patterns
- At-risk partner identification (declining, dormant)
- Churn prediction indicators
- Optimal investment timing by lifecycle stage
- Reactivation opportunity identification

Understanding lifecycle dynamics enables proactive partner management, staged support programs, early intervention for at-risk partners, strategic exit decisions, and evidence-based partner acquisition ROI models.

## SQL Code

```sql
WITH ResellerFirstLast AS (
    SELECT
        dr.ResellerKey,
        dr.ResellerName,
        dr.BusinessType,
        dr.FirstOrderYear,
        dr.LastOrderYear,
        dr.YearOpened,
        MIN(dd.FullDateAlternateKey) AS ActualFirstOrderDate,
        MAX(dd.FullDateAlternateKey) AS ActualLastOrderDate,
        COUNT(DISTINCT dd.CalendarYear) AS ActiveYears
    FROM DimReseller dr
    LEFT JOIN FactResellerSales frs ON dr.ResellerKey = frs.ResellerKey
    LEFT JOIN DimDate dd ON frs.OrderDateKey = dd.DateKey
    GROUP BY
        dr.ResellerKey, dr.ResellerName, dr.BusinessType,
        dr.FirstOrderYear, dr.LastOrderYear, dr.YearOpened
),
ResellerYearlyMetrics AS (
    SELECT
        dr.ResellerKey,
        dr.ResellerName,
        dr.BusinessType,
        rfl.ActualFirstOrderDate,
        rfl.ActiveYears,
        dd.CalendarYear,
        dd.CalendarYear - CAST(SUBSTR(rfl.ActualFirstOrderDate, 1, 4) AS INTEGER) AS YearsSinceFirstOrder,
        SUM(frs.SalesAmount) AS YearRevenue,
        SUM(frs.TotalProductCost) AS YearCost,
        COUNT(DISTINCT frs.SalesOrderNumber) AS YearOrders,
        COUNT(DISTINCT frs.ProductKey) AS UniqueProducts
    FROM FactResellerSales frs
    INNER JOIN DimReseller dr ON frs.ResellerKey = dr.ResellerKey
    INNER JOIN ResellerFirstLast rfl ON dr.ResellerKey = rfl.ResellerKey
    INNER JOIN DimDate dd ON frs.OrderDateKey = dd.DateKey
    GROUP BY
        dr.ResellerKey, dr.ResellerName, dr.BusinessType,
        rfl.ActualFirstOrderDate, rfl.ActiveYears,
        dd.CalendarYear
),
ResellerGrowthMetrics AS (
    SELECT
        *,
        LAG(YearRevenue, 1) OVER (
            PARTITION BY ResellerKey ORDER BY CalendarYear
        ) AS PrevYearRevenue,
        CASE
            WHEN LAG(YearRevenue, 1) OVER (
                PARTITION BY ResellerKey ORDER BY CalendarYear
            ) IS NOT NULL AND LAG(YearRevenue, 1) OVER (
                PARTITION BY ResellerKey ORDER BY CalendarYear
            ) > 0
            THEN ROUND(((YearRevenue - LAG(YearRevenue, 1) OVER (
                PARTITION BY ResellerKey ORDER BY CalendarYear
            )) / LAG(YearRevenue, 1) OVER (
                PARTITION BY ResellerKey ORDER BY CalendarYear
            )) * 100, 2)
            ELSE NULL
        END AS YoYGrowthPct,
        SUM(YearRevenue) OVER (
            PARTITION BY ResellerKey
            ORDER BY CalendarYear
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS CumulativeRevenue,
        AVG(YearRevenue) OVER (
            PARTITION BY ResellerKey
            ORDER BY CalendarYear
            ROWS BETWEEN 1 PRECEDING AND CURRENT ROW
        ) AS TwoYearAvgRevenue
    FROM ResellerYearlyMetrics
),
LifecycleStaging AS (
    SELECT
        rgm.*,
        rfl.ActualLastOrderDate,
        CAST(JULIANDAY(DATE('now')) - JULIANDAY(rfl.ActualLastOrderDate) AS INTEGER) AS DaysSinceLastOrder,
        CASE
            WHEN rgm.YearsSinceFirstOrder = 0 THEN 'New Partner (Year 1)'
            WHEN rgm.YearsSinceFirstOrder = 1 THEN 'Developing (Year 2)'
            WHEN rgm.YearsSinceFirstOrder <= 3 THEN 'Growing (Years 3-4)'
            WHEN rgm.YearsSinceFirstOrder <= 5 THEN 'Established (Years 5-6)'
            ELSE 'Mature (7+ Years)'
        END AS LifecycleStage,
        CASE
            WHEN CAST(JULIANDAY(DATE('now')) - JULIANDAY(rfl.ActualLastOrderDate) AS INTEGER) > 365 THEN 'Dormant'
            WHEN rgm.YoYGrowthPct < -20 THEN 'Declining'
            WHEN rgm.YoYGrowthPct < 0 THEN 'Contracting'
            WHEN rgm.YoYGrowthPct IS NULL THEN 'Stable'
            WHEN rgm.YoYGrowthPct < 10 THEN 'Modest Growth'
            WHEN rgm.YoYGrowthPct < 30 THEN 'Strong Growth'
            ELSE 'High Growth'
        END AS GrowthStatus,
        CASE
            WHEN CAST(JULIANDAY(DATE('now')) - JULIANDAY(rfl.ActualLastOrderDate) AS INTEGER) > 365 THEN 'High'
            WHEN rgm.YoYGrowthPct < -20 THEN 'High'
            WHEN rgm.YoYGrowthPct < -10 THEN 'Medium'
            WHEN CAST(JULIANDAY(DATE('now')) - JULIANDAY(rfl.ActualLastOrderDate) AS INTEGER) > 180 THEN 'Medium'
            ELSE 'Low'
        END AS ChurnRisk
    FROM ResellerGrowthMetrics rgm
    INNER JOIN ResellerFirstLast rfl ON rgm.ResellerKey = rfl.ResellerKey
),
LifecycleSummary AS (
    SELECT
        LifecycleStage,
        GrowthStatus,
        BusinessType,
        COUNT(DISTINCT ResellerKey) AS ResellerCount,
        ROUND(SUM(YearRevenue), 2) AS TotalRevenue,
        ROUND(AVG(YearRevenue), 2) AS AvgRevenue,
        ROUND(AVG(YoYGrowthPct), 2) AS AvgGrowthPct,
        ROUND(AVG(DaysSinceLastOrder), 0) AS AvgDaysSinceLastOrder,
        SUM(CASE WHEN ChurnRisk = 'High' THEN 1 ELSE 0 END) AS HighRiskCount,
        SUM(CASE WHEN ChurnRisk = 'Medium' THEN 1 ELSE 0 END) AS MediumRiskCount
    FROM LifecycleStaging
    WHERE CalendarYear = (SELECT MAX(CalendarYear) FROM LifecycleStaging)
    GROUP BY LifecycleStage, GrowthStatus, BusinessType
),
CohortAnalysis AS (
    SELECT
        CAST(SUBSTR(ActualFirstOrderDate, 1, 4) AS INTEGER) AS CohortYear,
        YearsSinceFirstOrder,
        COUNT(DISTINCT ResellerKey) AS CohortSize,
        ROUND(AVG(YearRevenue), 2) AS AvgRevenue,
        ROUND(AVG(YoYGrowthPct), 2) AS AvgGrowth,
        ROUND(AVG(CumulativeRevenue), 2) AS AvgCumulativeRevenue
    FROM ResellerGrowthMetrics
    WHERE YearsSinceFirstOrder <= 5
    GROUP BY
        CAST(SUBSTR(ActualFirstOrderDate, 1, 4) AS INTEGER),
        YearsSinceFirstOrder
),
ResellerTrajectory AS (
    SELECT
        ResellerKey,
        ResellerName,
        BusinessType,
        LifecycleStage,
        GrowthStatus,
        ChurnRisk,
        CalendarYear,
        YearsSinceFirstOrder,
        ROUND(YearRevenue, 2) AS YearRevenue,
        YoYGrowthPct,
        ROUND(CumulativeRevenue, 2) AS CumulativeRevenue,
        YearOrders,
        UniqueProducts,
        DaysSinceLastOrder,
        RANK() OVER (
            PARTITION BY LifecycleStage
            ORDER BY YearRevenue DESC
        ) AS StageRevenueRank
    FROM LifecycleStaging
    WHERE CalendarYear = (SELECT MAX(CalendarYear) FROM LifecycleStaging)
)
SELECT
    'Reseller Trajectory' AS ReportSection,
    rt.ResellerName,
    rt.BusinessType,
    rt.LifecycleStage,
    rt.GrowthStatus,
    rt.ChurnRisk,
    rt.CalendarYear,
    rt.YearsSinceFirstOrder,
    rt.YearRevenue,
    rt.YoYGrowthPct,
    rt.CumulativeRevenue,
    rt.YearOrders,
    rt.UniqueProducts,
    rt.DaysSinceLastOrder,
    rt.StageRevenueRank,
    NULL AS ResellerCount,
    NULL AS TotalRevenue,
    NULL AS AvgRevenue,
    NULL AS AvgGrowthPct,
    NULL AS HighRiskCount,
    NULL AS CohortYear
FROM ResellerTrajectory rt
WHERE rt.StageRevenueRank <= 10

UNION ALL

SELECT
    'Lifecycle Summary' AS ReportSection,
    NULL AS ResellerName,
    ls.BusinessType,
    ls.LifecycleStage,
    ls.GrowthStatus,
    NULL AS ChurnRisk,
    NULL AS CalendarYear,
    NULL AS YearsSinceFirstOrder,
    NULL AS YearRevenue,
    NULL AS YoYGrowthPct,
    NULL AS CumulativeRevenue,
    NULL AS YearOrders,
    NULL AS UniqueProducts,
    CAST(ls.AvgDaysSinceLastOrder AS INTEGER) AS DaysSinceLastOrder,
    NULL AS StageRevenueRank,
    ls.ResellerCount,
    ls.TotalRevenue,
    ls.AvgRevenue,
    ls.AvgGrowthPct,
    ls.HighRiskCount,
    NULL AS CohortYear
FROM LifecycleSummary ls

UNION ALL

SELECT
    'Cohort Analysis' AS ReportSection,
    NULL AS ResellerName,
    NULL AS BusinessType,
    NULL AS LifecycleStage,
    NULL AS GrowthStatus,
    NULL AS ChurnRisk,
    NULL AS CalendarYear,
    ca.YearsSinceFirstOrder,
    NULL AS YearRevenue,
    NULL AS YoYGrowthPct,
    ca.AvgCumulativeRevenue AS CumulativeRevenue,
    NULL AS YearOrders,
    NULL AS UniqueProducts,
    NULL AS DaysSinceLastOrder,
    NULL AS StageRevenueRank,
    ca.CohortSize AS ResellerCount,
    NULL AS TotalRevenue,
    ca.AvgRevenue,
    ca.AvgGrowth AS AvgGrowthPct,
    NULL AS HighRiskCount,
    ca.CohortYear
FROM CohortAnalysis ca

ORDER BY ReportSection, LifecycleStage, StageRevenueRank NULLS LAST, TotalRevenue DESC NULLS LAST;
```

---

## Summary

These five business questions provide a comprehensive framework for reseller channel analysis:

1. **Reseller Performance Ranking and Tiering** - Strategic segmentation into Platinum/Gold/Silver/Bronze tiers with performance scoring
2. **Business Type and Characteristic Analysis** - Understanding optimal partner profiles by business type, size, and operational patterns
3. **Product Portfolio and Category Affinity** - Identifying specialization patterns and cross-selling opportunities
4. **Sales Representative Effectiveness** - Evaluating employee performance in managing reseller relationships
5. **Reseller Lifecycle and Growth Trajectory** - Tracking partner development from onboarding through maturity with churn prediction

Each query demonstrates advanced analytical techniques including:
- Multi-dimensional performance scoring and ranking
- Partner segmentation and tiering strategies
- Window functions for growth calculations and trends
- Lifecycle stage identification
- Concentration analysis (HHI index)
- Cohort analysis for partner development patterns
- Churn risk assessment
- Account health scoring
- Time-series analysis with YoY comparisons
- Statistical measures (standard deviation, volatility)

These analyses enable data-driven decisions for:
- Partner recruitment and selection
- Tiered support program design
- Account assignment optimization
- Sales compensation and incentives
- Product training prioritization
- Territory planning
- Churn prevention initiatives
- Strategic account management
- Partner development investments
- Channel capacity planning

The insights from reseller analysis provide the foundation for building a high-performing indirect sales channel that drives mutual profitability and sustainable growth.
