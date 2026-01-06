# Shipment Performance and Logistics Analysis

# Introduction

This document presents five complex business intelligence questions focused on shipment performance, logistics efficiency, and delivery optimization within the AdventureWorks data warehouse. These analyses leverage both Internet and Reseller sales channels to examine critical supply chain metrics including on-time delivery rates, shipping lead times, freight cost efficiency, product-specific logistics complexity, and seasonal capacity planning requirements.

The queries utilize advanced SQL techniques including Common Table Expressions (CTEs), window functions, date arithmetic, and multi-dimensional aggregations to provide actionable insights for supply chain optimization, cost reduction, and customer satisfaction improvement.

---

# Business Question 1: On-Time Delivery Performance and Delay Analysis

## Intent

Analyze on-time delivery performance across both Internet and Reseller channels, identifying patterns in shipping delays, calculating delay severity, and segmenting orders by delivery performance. This analysis helps identify problematic territories, product categories, or time periods where shipping performance degrades, enabling targeted operational improvements and better customer service.

The query calculates:
- On-time delivery rate by channel and territory
- Average delay days for late shipments
- Distribution of orders by delivery status (Early, On-Time, Late, Severely Late)
- Delay severity scoring and problem area identification

## SQL Code

```sql
WITH AllShipments AS (
    -- Internet Sales Shipments
    SELECT
        fis.SalesOrderNumber,
        fis.SalesOrderLineNumber,
        'Internet' AS Channel,
        fis.OrderDate,
        fis.DueDate,
        fis.ShipDate,
        fis.SalesAmount,
        fis.Freight,
        st.SalesTerritoryRegion,
        st.SalesTerritoryCountry,
        p.EnglishProductName AS ProductName,
        psc.EnglishProductSubcategoryName AS SubcategoryName,
        pc.EnglishProductCategoryName AS CategoryName,
        g.City,
        g.StateProvinceName,
        dd_ship.CalendarYear AS ShipYear,
        dd_ship.CalendarQuarter AS ShipQuarter,
        dd_ship.EnglishMonthName AS ShipMonth
    FROM FactInternetSales fis
    INNER JOIN DimSalesTerritory st ON fis.SalesTerritoryKey = st.SalesTerritoryKey
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimCustomer c ON fis.CustomerKey = c.CustomerKey
    INNER JOIN DimGeography g ON c.GeographyKey = g.GeographyKey
    INNER JOIN DimDate dd_ship ON fis.ShipDateKey = dd_ship.DateKey
    WHERE fis.ShipDate IS NOT NULL AND fis.DueDate IS NOT NULL

    UNION ALL

    -- Reseller Sales Shipments
    SELECT
        frs.SalesOrderNumber,
        frs.SalesOrderLineNumber,
        'Reseller' AS Channel,
        frs.OrderDate,
        frs.DueDate,
        frs.ShipDate,
        frs.SalesAmount,
        frs.Freight,
        st.SalesTerritoryRegion,
        st.SalesTerritoryCountry,
        p.EnglishProductName AS ProductName,
        psc.EnglishProductSubcategoryName AS SubcategoryName,
        pc.EnglishProductCategoryName AS CategoryName,
        g.City,
        g.StateProvinceName,
        dd_ship.CalendarYear AS ShipYear,
        dd_ship.CalendarQuarter AS ShipQuarter,
        dd_ship.EnglishMonthName AS ShipMonth
    FROM FactResellerSales frs
    INNER JOIN DimSalesTerritory st ON frs.SalesTerritoryKey = st.SalesTerritoryKey
    INNER JOIN DimProduct p ON frs.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimReseller r ON frs.ResellerKey = r.ResellerKey
    INNER JOIN DimGeography g ON r.GeographyKey = g.GeographyKey
    INNER JOIN DimDate dd_ship ON frs.ShipDateKey = dd_ship.DateKey
    WHERE frs.ShipDate IS NOT NULL AND frs.DueDate IS NOT NULL
),

ShipmentMetrics AS (
    SELECT
        *,
        CAST(JULIANDAY(ShipDate) - JULIANDAY(DueDate) AS INTEGER) AS DaysFromDue,
        CASE
            WHEN ShipDate < DueDate THEN 'Early'
            WHEN ShipDate = DueDate THEN 'On-Time'
            WHEN CAST(JULIANDAY(ShipDate) - JULIANDAY(DueDate) AS INTEGER) BETWEEN 1 AND 3 THEN 'Slightly Late'
            WHEN CAST(JULIANDAY(ShipDate) - JULIANDAY(DueDate) AS INTEGER) BETWEEN 4 AND 7 THEN 'Late'
            ELSE 'Severely Late'
        END AS DeliveryStatus,
        CASE
            WHEN ShipDate <= DueDate THEN 1
            ELSE 0
        END AS OnTimeFlag,
        CASE
            WHEN ShipDate > DueDate THEN CAST(JULIANDAY(ShipDate) - JULIANDAY(DueDate) AS INTEGER)
            ELSE 0
        END AS DelayDays
    FROM AllShipments
),

TerritoryPerformance AS (
    SELECT
        Channel,
        SalesTerritoryCountry,
        SalesTerritoryRegion,
        COUNT(*) AS TotalShipments,
        SUM(OnTimeFlag) AS OnTimeShipments,
        ROUND(100.0 * SUM(OnTimeFlag) / COUNT(*), 2) AS OnTimeDeliveryPct,
        ROUND(AVG(CASE WHEN DelayDays > 0 THEN DelayDays END), 2) AS AvgDelayDays,
        SUM(CASE WHEN DeliveryStatus = 'Early' THEN 1 ELSE 0 END) AS EarlyCount,
        SUM(CASE WHEN DeliveryStatus = 'On-Time' THEN 1 ELSE 0 END) AS OnTimeCount,
        SUM(CASE WHEN DeliveryStatus = 'Slightly Late' THEN 1 ELSE 0 END) AS SlightlyLateCount,
        SUM(CASE WHEN DeliveryStatus = 'Late' THEN 1 ELSE 0 END) AS LateCount,
        SUM(CASE WHEN DeliveryStatus = 'Severely Late' THEN 1 ELSE 0 END) AS SeverelyLateCount,
        ROUND(SUM(SalesAmount), 2) AS TotalRevenue,
        ROUND(SUM(CASE WHEN DeliveryStatus IN ('Late', 'Severely Late') THEN SalesAmount ELSE 0 END), 2) AS RevenueAtRisk
    FROM ShipmentMetrics
    GROUP BY Channel, SalesTerritoryCountry, SalesTerritoryRegion
),

CategoryPerformance AS (
    SELECT
        CategoryName,
        Channel,
        COUNT(*) AS TotalShipments,
        ROUND(100.0 * SUM(OnTimeFlag) / COUNT(*), 2) AS OnTimeDeliveryPct,
        ROUND(AVG(DelayDays), 2) AS AvgDelayDays,
        ROUND(AVG(CASE WHEN DelayDays > 0 THEN DelayDays END), 2) AS AvgDelayDaysWhenLate
    FROM ShipmentMetrics
    WHERE CategoryName IS NOT NULL
    GROUP BY CategoryName, Channel
)

SELECT
    tp.Channel,
    tp.SalesTerritoryCountry,
    tp.SalesTerritoryRegion,
    tp.TotalShipments,
    tp.OnTimeShipments,
    tp.OnTimeDeliveryPct,
    tp.AvgDelayDays,
    tp.EarlyCount,
    tp.OnTimeCount,
    tp.SlightlyLateCount,
    tp.LateCount,
    tp.SeverelyLateCount,
    tp.TotalRevenue,
    tp.RevenueAtRisk,
    ROUND(100.0 * tp.RevenueAtRisk / NULLIF(tp.TotalRevenue, 0), 2) AS RevenueAtRiskPct,
    RANK() OVER (PARTITION BY tp.Channel ORDER BY tp.OnTimeDeliveryPct DESC) AS PerformanceRank
FROM TerritoryPerformance tp
ORDER BY tp.Channel, tp.OnTimeDeliveryPct ASC, tp.TotalShipments DESC;
```

---

# Business Question 2: Shipping Lead Time Analysis by Channel, Geography, and Product

## Intent

Examine end-to-end shipping lead times (from order date to ship date) across different channels, geographic regions, and product categories to identify operational bottlenecks and optimize fulfillment processes. This analysis reveals which combinations of channel, location, and product type result in longer processing times, enabling targeted process improvements and realistic customer expectation setting.

The query calculates:
- Average, median, and percentile lead times by channel and territory
- Lead time variance and consistency metrics
- Product category complexity factors affecting lead times
- Year-over-year lead time trend analysis

## SQL Code

```sql
WITH AllOrders AS (
    -- Internet Sales Orders
    SELECT
        fis.SalesOrderNumber,
        fis.SalesOrderLineNumber,
        'Internet' AS Channel,
        fis.OrderDate,
        fis.ShipDate,
        fis.OrderQuantity,
        fis.SalesAmount,
        st.SalesTerritoryRegion,
        st.SalesTerritoryCountry,
        st.SalesTerritoryGroup,
        p.EnglishProductName AS ProductName,
        psc.EnglishProductSubcategoryName AS SubcategoryName,
        pc.EnglishProductCategoryName AS CategoryName,
        g.City,
        g.StateProvinceName,
        g.EnglishCountryRegionName AS CountryName,
        dd_order.CalendarYear AS OrderYear,
        dd_order.CalendarQuarter AS OrderQuarter
    FROM FactInternetSales fis
    INNER JOIN DimSalesTerritory st ON fis.SalesTerritoryKey = st.SalesTerritoryKey
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimCustomer c ON fis.CustomerKey = c.CustomerKey
    INNER JOIN DimGeography g ON c.GeographyKey = g.GeographyKey
    INNER JOIN DimDate dd_order ON fis.OrderDateKey = dd_order.DateKey
    WHERE fis.ShipDate IS NOT NULL AND fis.OrderDate IS NOT NULL

    UNION ALL

    -- Reseller Sales Orders
    SELECT
        frs.SalesOrderNumber,
        frs.SalesOrderLineNumber,
        'Reseller' AS Channel,
        frs.OrderDate,
        frs.ShipDate,
        frs.OrderQuantity,
        frs.SalesAmount,
        st.SalesTerritoryRegion,
        st.SalesTerritoryCountry,
        st.SalesTerritoryGroup,
        p.EnglishProductName AS ProductName,
        psc.EnglishProductSubcategoryName AS SubcategoryName,
        pc.EnglishProductCategoryName AS CategoryName,
        g.City,
        g.StateProvinceName,
        g.EnglishCountryRegionName AS CountryName,
        dd_order.CalendarYear AS OrderYear,
        dd_order.CalendarQuarter AS OrderQuarter
    FROM FactResellerSales frs
    INNER JOIN DimSalesTerritory st ON frs.SalesTerritoryKey = st.SalesTerritoryKey
    INNER JOIN DimProduct p ON frs.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimReseller r ON frs.ResellerKey = r.ResellerKey
    INNER JOIN DimGeography g ON r.GeographyKey = g.GeographyKey
    INNER JOIN DimDate dd_order ON frs.OrderDateKey = dd_order.DateKey
    WHERE frs.ShipDate IS NOT NULL AND frs.OrderDate IS NOT NULL
),

LeadTimeCalculations AS (
    SELECT
        *,
        CAST(JULIANDAY(ShipDate) - JULIANDAY(OrderDate) AS INTEGER) AS LeadTimeDays,
        CASE
            WHEN CAST(JULIANDAY(ShipDate) - JULIANDAY(OrderDate) AS INTEGER) <= 1 THEN 'Same/Next Day'
            WHEN CAST(JULIANDAY(ShipDate) - JULIANDAY(OrderDate) AS INTEGER) BETWEEN 2 AND 3 THEN '2-3 Days'
            WHEN CAST(JULIANDAY(ShipDate) - JULIANDAY(OrderDate) AS INTEGER) BETWEEN 4 AND 7 THEN '4-7 Days'
            WHEN CAST(JULIANDAY(ShipDate) - JULIANDAY(OrderDate) AS INTEGER) BETWEEN 8 AND 14 THEN '1-2 Weeks'
            ELSE 'Over 2 Weeks'
        END AS LeadTimeBucket
    FROM AllOrders
),

ChannelTerritoryLeadTime AS (
    SELECT
        Channel,
        SalesTerritoryGroup,
        SalesTerritoryCountry,
        SalesTerritoryRegion,
        COUNT(*) AS TotalOrders,
        ROUND(AVG(LeadTimeDays), 2) AS AvgLeadTimeDays,
        MIN(LeadTimeDays) AS MinLeadTimeDays,
        MAX(LeadTimeDays) AS MaxLeadTimeDays,
        ROUND(AVG(LeadTimeDays) * AVG(LeadTimeDays) - AVG(LeadTimeDays * LeadTimeDays), 2) AS LeadTimeVariance,
        SUM(CASE WHEN LeadTimeBucket = 'Same/Next Day' THEN 1 ELSE 0 END) AS SameNextDayCount,
        SUM(CASE WHEN LeadTimeBucket = '2-3 Days' THEN 1 ELSE 0 END) AS Days2_3Count,
        SUM(CASE WHEN LeadTimeBucket = '4-7 Days' THEN 1 ELSE 0 END) AS Days4_7Count,
        SUM(CASE WHEN LeadTimeBucket = '1-2 Weeks' THEN 1 ELSE 0 END) AS Weeks1_2Count,
        SUM(CASE WHEN LeadTimeBucket = 'Over 2 Weeks' THEN 1 ELSE 0 END) AS Over2WeeksCount,
        ROUND(100.0 * SUM(CASE WHEN LeadTimeDays <= 3 THEN 1 ELSE 0 END) / COUNT(*), 2) AS Within3DaysPct,
        ROUND(100.0 * SUM(CASE WHEN LeadTimeDays <= 7 THEN 1 ELSE 0 END) / COUNT(*), 2) AS Within1WeekPct
    FROM LeadTimeCalculations
    GROUP BY Channel, SalesTerritoryGroup, SalesTerritoryCountry, SalesTerritoryRegion
),

CategoryLeadTime AS (
    SELECT
        CategoryName,
        Channel,
        COUNT(*) AS TotalOrders,
        ROUND(AVG(LeadTimeDays), 2) AS AvgLeadTimeDays,
        ROUND(100.0 * SUM(CASE WHEN LeadTimeDays <= 3 THEN 1 ELSE 0 END) / COUNT(*), 2) AS Within3DaysPct,
        RANK() OVER (PARTITION BY Channel ORDER BY AVG(LeadTimeDays) DESC) AS ComplexityRank
    FROM LeadTimeCalculations
    WHERE CategoryName IS NOT NULL
    GROUP BY CategoryName, Channel
),

YearOverYearTrend AS (
    SELECT
        OrderYear,
        Channel,
        COUNT(*) AS TotalOrders,
        ROUND(AVG(LeadTimeDays), 2) AS AvgLeadTimeDays,
        LAG(ROUND(AVG(LeadTimeDays), 2)) OVER (PARTITION BY Channel ORDER BY OrderYear) AS PrevYearAvgLeadTime,
        ROUND(AVG(LeadTimeDays) - LAG(AVG(LeadTimeDays)) OVER (PARTITION BY Channel ORDER BY OrderYear), 2) AS YoYLeadTimeChange
    FROM LeadTimeCalculations
    GROUP BY OrderYear, Channel
)

SELECT
    ctl.Channel,
    ctl.SalesTerritoryGroup,
    ctl.SalesTerritoryCountry,
    ctl.SalesTerritoryRegion,
    ctl.TotalOrders,
    ctl.AvgLeadTimeDays,
    ctl.MinLeadTimeDays,
    ctl.MaxLeadTimeDays,
    ctl.LeadTimeVariance,
    ctl.SameNextDayCount,
    ctl.Days2_3Count,
    ctl.Days4_7Count,
    ctl.Weeks1_2Count,
    ctl.Over2WeeksCount,
    ctl.Within3DaysPct,
    ctl.Within1WeekPct,
    RANK() OVER (PARTITION BY ctl.Channel ORDER BY ctl.AvgLeadTimeDays ASC) AS SpeedRank,
    RANK() OVER (PARTITION BY ctl.Channel ORDER BY ctl.LeadTimeVariance ASC) AS ConsistencyRank
FROM ChannelTerritoryLeadTime ctl
ORDER BY ctl.Channel, ctl.AvgLeadTimeDays ASC;
```

---

# Business Question 3: Freight Cost Efficiency and Optimization Opportunities

## Intent

Analyze freight costs relative to order value, weight, distance, and shipping speed to identify cost optimization opportunities and evaluate carrier efficiency. This analysis helps procurement teams negotiate better shipping rates, operations teams optimize packaging and routing decisions, and finance teams understand the profitability impact of logistics costs.

The query calculates:
- Freight cost as percentage of sales amount by channel and territory
- Cost per shipment and cost per unit metrics
- High-cost shipping scenarios requiring attention
- Freight efficiency scoring and benchmark comparisons

## SQL Code

```sql
WITH AllShipmentsWithFreight AS (
    -- Internet Sales with Freight
    SELECT
        fis.SalesOrderNumber,
        fis.SalesOrderLineNumber,
        'Internet' AS Channel,
        fis.OrderDate,
        fis.ShipDate,
        fis.OrderQuantity,
        fis.SalesAmount,
        fis.Freight,
        fis.TaxAmt,
        st.SalesTerritoryRegion,
        st.SalesTerritoryCountry,
        st.SalesTerritoryGroup,
        p.EnglishProductName AS ProductName,
        p.Weight AS ProductWeight,
        psc.EnglishProductSubcategoryName AS SubcategoryName,
        pc.EnglishProductCategoryName AS CategoryName,
        g.City AS DestinationCity,
        g.StateProvinceName AS DestinationState,
        g.EnglishCountryRegionName AS DestinationCountry,
        dd_order.CalendarYear AS OrderYear,
        dd_order.CalendarQuarter AS OrderQuarter
    FROM FactInternetSales fis
    INNER JOIN DimSalesTerritory st ON fis.SalesTerritoryKey = st.SalesTerritoryKey
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimCustomer c ON fis.CustomerKey = c.CustomerKey
    INNER JOIN DimGeography g ON c.GeographyKey = g.GeographyKey
    INNER JOIN DimDate dd_order ON fis.OrderDateKey = dd_order.DateKey
    WHERE fis.Freight IS NOT NULL AND fis.Freight > 0

    UNION ALL

    -- Reseller Sales with Freight
    SELECT
        frs.SalesOrderNumber,
        frs.SalesOrderLineNumber,
        'Reseller' AS Channel,
        frs.OrderDate,
        frs.ShipDate,
        frs.OrderQuantity,
        frs.SalesAmount,
        frs.Freight,
        frs.TaxAmt,
        st.SalesTerritoryRegion,
        st.SalesTerritoryCountry,
        st.SalesTerritoryGroup,
        p.EnglishProductName AS ProductName,
        p.Weight AS ProductWeight,
        psc.EnglishProductSubcategoryName AS SubcategoryName,
        pc.EnglishProductCategoryName AS CategoryName,
        g.City AS DestinationCity,
        g.StateProvinceName AS DestinationState,
        g.EnglishCountryRegionName AS DestinationCountry,
        dd_order.CalendarYear AS OrderYear,
        dd_order.CalendarQuarter AS OrderQuarter
    FROM FactResellerSales frs
    INNER JOIN DimSalesTerritory st ON frs.SalesTerritoryKey = st.SalesTerritoryKey
    INNER JOIN DimProduct p ON frs.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimReseller r ON frs.ResellerKey = r.ResellerKey
    INNER JOIN DimGeography g ON r.GeographyKey = g.GeographyKey
    INNER JOIN DimDate dd_order ON frs.OrderDateKey = dd_order.DateKey
    WHERE frs.Freight IS NOT NULL AND frs.Freight > 0
),

FreightMetrics AS (
    SELECT
        *,
        CAST(JULIANDAY(ShipDate) - JULIANDAY(OrderDate) AS INTEGER) AS LeadTimeDays,
        ROUND(100.0 * Freight / NULLIF(SalesAmount, 0), 2) AS FreightAsPercentOfSales,
        ROUND(Freight / NULLIF(OrderQuantity, 0), 2) AS FreightPerUnit,
        CASE
            WHEN ProductWeight IS NOT NULL AND ProductWeight > 0
            THEN ROUND(Freight / (ProductWeight * OrderQuantity), 2)
            ELSE NULL
        END AS FreightPerPound,
        CASE
            WHEN 100.0 * Freight / NULLIF(SalesAmount, 0) > 20 THEN 'Very High Cost'
            WHEN 100.0 * Freight / NULLIF(SalesAmount, 0) BETWEEN 10 AND 20 THEN 'High Cost'
            WHEN 100.0 * Freight / NULLIF(SalesAmount, 0) BETWEEN 5 AND 10 THEN 'Moderate Cost'
            ELSE 'Low Cost'
        END AS FreightCostCategory
    FROM AllShipmentsWithFreight
),

TerritoryFreightAnalysis AS (
    SELECT
        Channel,
        SalesTerritoryGroup,
        SalesTerritoryCountry,
        SalesTerritoryRegion,
        COUNT(*) AS TotalShipments,
        ROUND(SUM(SalesAmount), 2) AS TotalRevenue,
        ROUND(SUM(Freight), 2) AS TotalFreightCost,
        ROUND(AVG(Freight), 2) AS AvgFreightPerShipment,
        ROUND(AVG(FreightAsPercentOfSales), 2) AS AvgFreightPctOfSales,
        ROUND(AVG(FreightPerUnit), 2) AS AvgFreightPerUnit,
        MIN(FreightAsPercentOfSales) AS MinFreightPct,
        MAX(FreightAsPercentOfSales) AS MaxFreightPct,
        SUM(CASE WHEN FreightCostCategory = 'Very High Cost' THEN 1 ELSE 0 END) AS VeryHighCostCount,
        SUM(CASE WHEN FreightCostCategory = 'High Cost' THEN 1 ELSE 0 END) AS HighCostCount,
        SUM(CASE WHEN FreightCostCategory = 'Moderate Cost' THEN 1 ELSE 0 END) AS ModerateCostCount,
        SUM(CASE WHEN FreightCostCategory = 'Low Cost' THEN 1 ELSE 0 END) AS LowCostCount,
        ROUND(SUM(CASE WHEN FreightCostCategory IN ('Very High Cost', 'High Cost') THEN Freight ELSE 0 END), 2) AS HighCostFreightTotal,
        ROUND(100.0 * SUM(CASE WHEN FreightCostCategory IN ('Very High Cost', 'High Cost') THEN Freight ELSE 0 END) / NULLIF(SUM(Freight), 0), 2) AS HighCostFreightPct
    FROM FreightMetrics
    GROUP BY Channel, SalesTerritoryGroup, SalesTerritoryCountry, SalesTerritoryRegion
),

CategoryFreightAnalysis AS (
    SELECT
        CategoryName,
        Channel,
        COUNT(*) AS TotalShipments,
        ROUND(SUM(Freight), 2) AS TotalFreightCost,
        ROUND(AVG(Freight), 2) AS AvgFreightPerShipment,
        ROUND(AVG(FreightAsPercentOfSales), 2) AS AvgFreightPctOfSales,
        ROUND(AVG(CASE WHEN ProductWeight IS NOT NULL AND ProductWeight > 0 THEN FreightPerPound END), 2) AS AvgFreightPerPound,
        ROUND(AVG(ProductWeight * OrderQuantity), 2) AS AvgTotalWeightLbs
    FROM FreightMetrics
    WHERE CategoryName IS NOT NULL
    GROUP BY CategoryName, Channel
),

LeadTimeFreightCorrelation AS (
    SELECT
        Channel,
        CASE
            WHEN LeadTimeDays <= 1 THEN 'Same/Next Day'
            WHEN LeadTimeDays BETWEEN 2 AND 3 THEN '2-3 Days'
            WHEN LeadTimeDays BETWEEN 4 AND 7 THEN '4-7 Days'
            ELSE 'Over 1 Week'
        END AS LeadTimeBucket,
        COUNT(*) AS ShipmentCount,
        ROUND(AVG(Freight), 2) AS AvgFreight,
        ROUND(AVG(FreightAsPercentOfSales), 2) AS AvgFreightPctOfSales
    FROM FreightMetrics
    GROUP BY Channel, LeadTimeBucket
),

FreightEfficiencyScore AS (
    SELECT
        tfa.*,
        NTILE(4) OVER (PARTITION BY tfa.Channel ORDER BY tfa.AvgFreightPctOfSales ASC) AS EfficiencyQuartile,
        RANK() OVER (PARTITION BY tfa.Channel ORDER BY tfa.AvgFreightPctOfSales ASC) AS EfficiencyRank
    FROM TerritoryFreightAnalysis tfa
)

SELECT
    fes.Channel,
    fes.SalesTerritoryGroup,
    fes.SalesTerritoryCountry,
    fes.SalesTerritoryRegion,
    fes.TotalShipments,
    fes.TotalRevenue,
    fes.TotalFreightCost,
    fes.AvgFreightPerShipment,
    fes.AvgFreightPctOfSales,
    fes.AvgFreightPerUnit,
    fes.MinFreightPct,
    fes.MaxFreightPct,
    fes.VeryHighCostCount,
    fes.HighCostCount,
    fes.ModerateCostCount,
    fes.LowCostCount,
    fes.HighCostFreightTotal,
    fes.HighCostFreightPct,
    fes.EfficiencyQuartile,
    fes.EfficiencyRank,
    CASE
        WHEN fes.EfficiencyQuartile = 1 THEN 'Highly Efficient'
        WHEN fes.EfficiencyQuartile = 2 THEN 'Efficient'
        WHEN fes.EfficiencyQuartile = 3 THEN 'Below Average'
        ELSE 'Requires Optimization'
    END AS EfficiencyRating
FROM FreightEfficiencyScore fes
ORDER BY fes.Channel, fes.AvgFreightPctOfSales DESC;
```

---

# Business Question 4: Product Category Shipping Complexity and Service Level Analysis

## Intent

Evaluate shipping complexity and service level requirements by product category, identifying which products require special handling, have longer fulfillment cycles, or generate higher shipping costs. This analysis enables better inventory positioning, packaging optimization, and service level agreement (SLA) design based on product characteristics and customer expectations.

The query calculates:
- Category-specific shipping patterns and complexity scores
- Product weight and handling characteristics impact on shipping
- Category fulfillment consistency and reliability metrics
- Special handling requirements and cost implications

## SQL Code

```sql
WITH ProductShipmentData AS (
    -- Internet Sales Product Shipments
    SELECT
        p.ProductKey,
        p.EnglishProductName AS ProductName,
        p.Weight AS ProductWeight,
        p.Color,
        p.Size,
        p.StandardCost,
        p.ListPrice,
        psc.EnglishProductSubcategoryName AS SubcategoryName,
        pc.EnglishProductCategoryName AS CategoryName,
        fis.SalesOrderNumber,
        fis.SalesOrderLineNumber,
        'Internet' AS Channel,
        fis.OrderDate,
        fis.ShipDate,
        fis.DueDate,
        fis.OrderQuantity,
        fis.SalesAmount,
        fis.Freight,
        st.SalesTerritoryRegion
    FROM FactInternetSales fis
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimSalesTerritory st ON fis.SalesTerritoryKey = st.SalesTerritoryKey
    WHERE fis.ShipDate IS NOT NULL AND fis.OrderDate IS NOT NULL

    UNION ALL

    -- Reseller Sales Product Shipments
    SELECT
        p.ProductKey,
        p.EnglishProductName AS ProductName,
        p.Weight AS ProductWeight,
        p.Color,
        p.Size,
        p.StandardCost,
        p.ListPrice,
        psc.EnglishProductSubcategoryName AS SubcategoryName,
        pc.EnglishProductCategoryName AS CategoryName,
        frs.SalesOrderNumber,
        frs.SalesOrderLineNumber,
        'Reseller' AS Channel,
        frs.OrderDate,
        frs.ShipDate,
        frs.DueDate,
        frs.OrderQuantity,
        frs.SalesAmount,
        frs.Freight,
        st.SalesTerritoryRegion
    FROM FactResellerSales frs
    INNER JOIN DimProduct p ON frs.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimSalesTerritory st ON frs.SalesTerritoryKey = st.SalesTerritoryKey
    WHERE frs.ShipDate IS NOT NULL AND frs.OrderDate IS NOT NULL
),

ShipmentCalculations AS (
    SELECT
        *,
        CAST(JULIANDAY(ShipDate) - JULIANDAY(OrderDate) AS INTEGER) AS LeadTimeDays,
        CAST(JULIANDAY(ShipDate) - JULIANDAY(DueDate) AS INTEGER) AS DaysFromDue,
        CASE WHEN ShipDate <= DueDate THEN 1 ELSE 0 END AS OnTimeFlag,
        ROUND(Freight / NULLIF(OrderQuantity, 0), 2) AS FreightPerUnit,
        CASE
            WHEN ProductWeight IS NOT NULL AND ProductWeight > 0
            THEN ROUND((ProductWeight * OrderQuantity), 2)
            ELSE NULL
        END AS TotalShipmentWeight
    FROM ProductShipmentData
),

CategoryComplexityMetrics AS (
    SELECT
        CategoryName,
        Channel,
        COUNT(DISTINCT ProductKey) AS UniqueProducts,
        COUNT(*) AS TotalShipments,
        ROUND(AVG(LeadTimeDays), 2) AS AvgLeadTimeDays,
        ROUND(AVG(CASE WHEN LeadTimeDays > 0 THEN LeadTimeDays END) *
              AVG(CASE WHEN LeadTimeDays > 0 THEN LeadTimeDays END) -
              AVG(CASE WHEN LeadTimeDays > 0 THEN LeadTimeDays * LeadTimeDays END), 2) AS LeadTimeVariance,
        MIN(LeadTimeDays) AS MinLeadTime,
        MAX(LeadTimeDays) AS MaxLeadTime,
        ROUND(100.0 * SUM(OnTimeFlag) / COUNT(*), 2) AS OnTimeDeliveryPct,
        ROUND(AVG(CASE WHEN DaysFromDue > 0 THEN DaysFromDue END), 2) AS AvgDelayWhenLate,
        ROUND(AVG(Freight), 2) AS AvgFreightCost,
        ROUND(AVG(FreightPerUnit), 2) AS AvgFreightPerUnit,
        ROUND(100.0 * AVG(Freight) / NULLIF(AVG(SalesAmount), 0), 2) AS AvgFreightPctOfSales,
        ROUND(AVG(TotalShipmentWeight), 2) AS AvgShipmentWeight,
        ROUND(SUM(SalesAmount), 2) AS TotalRevenue,
        ROUND(SUM(Freight), 2) AS TotalFreightCost
    FROM ShipmentCalculations
    WHERE CategoryName IS NOT NULL
    GROUP BY CategoryName, Channel
),

SubcategoryDetail AS (
    SELECT
        CategoryName,
        SubcategoryName,
        Channel,
        COUNT(*) AS TotalShipments,
        ROUND(AVG(LeadTimeDays), 2) AS AvgLeadTimeDays,
        ROUND(100.0 * SUM(OnTimeFlag) / COUNT(*), 2) AS OnTimeDeliveryPct,
        ROUND(AVG(TotalShipmentWeight), 2) AS AvgShipmentWeight,
        ROUND(AVG(FreightPerUnit), 2) AS AvgFreightPerUnit
    FROM ShipmentCalculations
    WHERE CategoryName IS NOT NULL AND SubcategoryName IS NOT NULL
    GROUP BY CategoryName, SubcategoryName, Channel
),

ComplexityScoring AS (
    SELECT
        ccm.*,
        -- Complexity Score Components (normalized to 0-100 scale)
        -- Higher lead time = higher complexity
        NTILE(10) OVER (PARTITION BY ccm.Channel ORDER BY ccm.AvgLeadTimeDays DESC) * 10 AS LeadTimeComplexityScore,
        -- Higher variance = higher complexity
        NTILE(10) OVER (PARTITION BY ccm.Channel ORDER BY ccm.LeadTimeVariance DESC) * 10 AS VarianceComplexityScore,
        -- Lower on-time rate = higher complexity
        NTILE(10) OVER (PARTITION BY ccm.Channel ORDER BY ccm.OnTimeDeliveryPct ASC) * 10 AS ReliabilityComplexityScore,
        -- Higher freight cost = higher complexity
        NTILE(10) OVER (PARTITION BY ccm.Channel ORDER BY ccm.AvgFreightPctOfSales DESC) * 10 AS FreightComplexityScore
    FROM CategoryComplexityMetrics ccm
),

FinalComplexityScore AS (
    SELECT
        cs.*,
        -- Overall Complexity Score (weighted average)
        ROUND((cs.LeadTimeComplexityScore * 0.30 +
               cs.VarianceComplexityScore * 0.25 +
               cs.ReliabilityComplexityScore * 0.25 +
               cs.FreightComplexityScore * 0.20), 2) AS OverallComplexityScore,
        CASE
            WHEN (cs.LeadTimeComplexityScore * 0.30 +
                  cs.VarianceComplexityScore * 0.25 +
                  cs.ReliabilityComplexityScore * 0.25 +
                  cs.FreightComplexityScore * 0.20) >= 75 THEN 'Very High Complexity'
            WHEN (cs.LeadTimeComplexityScore * 0.30 +
                  cs.VarianceComplexityScore * 0.25 +
                  cs.ReliabilityComplexityScore * 0.25 +
                  cs.FreightComplexityScore * 0.20) >= 50 THEN 'High Complexity'
            WHEN (cs.LeadTimeComplexityScore * 0.30 +
                  cs.VarianceComplexityScore * 0.25 +
                  cs.ReliabilityComplexityScore * 0.25 +
                  cs.FreightComplexityScore * 0.20) >= 25 THEN 'Moderate Complexity'
            ELSE 'Low Complexity'
        END AS ComplexityCategory
    FROM ComplexityScoring cs
)

SELECT
    fcs.CategoryName,
    fcs.Channel,
    fcs.UniqueProducts,
    fcs.TotalShipments,
    fcs.AvgLeadTimeDays,
    fcs.LeadTimeVariance,
    fcs.MinLeadTime,
    fcs.MaxLeadTime,
    fcs.OnTimeDeliveryPct,
    fcs.AvgDelayWhenLate,
    fcs.AvgFreightCost,
    fcs.AvgFreightPerUnit,
    fcs.AvgFreightPctOfSales,
    fcs.AvgShipmentWeight,
    fcs.TotalRevenue,
    fcs.TotalFreightCost,
    fcs.LeadTimeComplexityScore,
    fcs.VarianceComplexityScore,
    fcs.ReliabilityComplexityScore,
    fcs.FreightComplexityScore,
    fcs.OverallComplexityScore,
    fcs.ComplexityCategory,
    RANK() OVER (PARTITION BY fcs.Channel ORDER BY fcs.OverallComplexityScore DESC) AS ComplexityRank
FROM FinalComplexityScore fcs
ORDER BY fcs.Channel, fcs.OverallComplexityScore DESC;
```

---

# Business Question 5: Seasonal Shipping Patterns and Capacity Planning

## Intent

Analyze seasonal patterns in shipping volume, lead times, and on-time performance to inform capacity planning, workforce scheduling, and carrier contract negotiations. This analysis identifies peak shipping periods, seasonal stress points in the logistics network, and opportunities to smooth demand through proactive planning and customer communication.

The query calculates:
- Monthly and quarterly shipping volume trends
- Seasonal variations in lead time and on-time delivery rates
- Year-over-year seasonal pattern comparisons
- Capacity utilization indicators and bottleneck identification

## SQL Code

```sql
WITH AllSeasonalShipments AS (
    -- Internet Sales Seasonal Data
    SELECT
        fis.SalesOrderNumber,
        fis.SalesOrderLineNumber,
        'Internet' AS Channel,
        fis.OrderDate,
        fis.ShipDate,
        fis.DueDate,
        fis.OrderQuantity,
        fis.SalesAmount,
        fis.Freight,
        dd_order.CalendarYear AS OrderYear,
        dd_order.CalendarQuarter AS OrderQuarter,
        dd_order.MonthNumberOfYear AS OrderMonth,
        dd_order.EnglishMonthName AS OrderMonthName,
        dd_order.WeekNumberOfYear AS OrderWeekNumber,
        dd_order.DayNumberOfWeek AS OrderDayOfWeek,
        dd_order.EnglishDayNameOfWeek AS OrderDayName,
        dd_ship.CalendarYear AS ShipYear,
        dd_ship.CalendarQuarter AS ShipQuarter,
        dd_ship.MonthNumberOfYear AS ShipMonth,
        dd_ship.EnglishMonthName AS ShipMonthName,
        st.SalesTerritoryRegion,
        st.SalesTerritoryCountry,
        pc.EnglishProductCategoryName AS CategoryName
    FROM FactInternetSales fis
    INNER JOIN DimDate dd_order ON fis.OrderDateKey = dd_order.DateKey
    INNER JOIN DimDate dd_ship ON fis.ShipDateKey = dd_ship.DateKey
    INNER JOIN DimSalesTerritory st ON fis.SalesTerritoryKey = st.SalesTerritoryKey
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    WHERE fis.ShipDate IS NOT NULL AND fis.OrderDate IS NOT NULL

    UNION ALL

    -- Reseller Sales Seasonal Data
    SELECT
        frs.SalesOrderNumber,
        frs.SalesOrderLineNumber,
        'Reseller' AS Channel,
        frs.OrderDate,
        frs.ShipDate,
        frs.DueDate,
        frs.OrderQuantity,
        frs.SalesAmount,
        frs.Freight,
        dd_order.CalendarYear AS OrderYear,
        dd_order.CalendarQuarter AS OrderQuarter,
        dd_order.MonthNumberOfYear AS OrderMonth,
        dd_order.EnglishMonthName AS OrderMonthName,
        dd_order.WeekNumberOfYear AS OrderWeekNumber,
        dd_order.DayNumberOfWeek AS OrderDayOfWeek,
        dd_order.EnglishDayNameOfWeek AS OrderDayName,
        dd_ship.CalendarYear AS ShipYear,
        dd_ship.CalendarQuarter AS ShipQuarter,
        dd_ship.MonthNumberOfYear AS ShipMonth,
        dd_ship.EnglishMonthName AS ShipMonthName,
        st.SalesTerritoryRegion,
        st.SalesTerritoryCountry,
        pc.EnglishProductCategoryName AS CategoryName
    FROM FactResellerSales frs
    INNER JOIN DimDate dd_order ON frs.OrderDateKey = dd_order.DateKey
    INNER JOIN DimDate dd_ship ON frs.ShipDateKey = dd_ship.DateKey
    INNER JOIN DimSalesTerritory st ON frs.SalesTerritoryKey = st.SalesTerritoryKey
    INNER JOIN DimProduct p ON frs.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    WHERE frs.ShipDate IS NOT NULL AND frs.OrderDate IS NOT NULL
),

ShipmentMetrics AS (
    SELECT
        *,
        CAST(JULIANDAY(ShipDate) - JULIANDAY(OrderDate) AS INTEGER) AS LeadTimeDays,
        CAST(JULIANDAY(ShipDate) - JULIANDAY(DueDate) AS INTEGER) AS DaysFromDue,
        CASE WHEN ShipDate <= DueDate THEN 1 ELSE 0 END AS OnTimeFlag
    FROM AllSeasonalShipments
),

MonthlyTrends AS (
    SELECT
        Channel,
        OrderYear,
        OrderMonth,
        OrderMonthName,
        COUNT(*) AS TotalShipments,
        SUM(OrderQuantity) AS TotalUnitsShipped,
        ROUND(SUM(SalesAmount), 2) AS TotalRevenue,
        ROUND(SUM(Freight), 2) AS TotalFreightCost,
        ROUND(AVG(LeadTimeDays), 2) AS AvgLeadTimeDays,
        ROUND(100.0 * SUM(OnTimeFlag) / COUNT(*), 2) AS OnTimeDeliveryPct,
        ROUND(AVG(CASE WHEN DaysFromDue > 0 THEN DaysFromDue END), 2) AS AvgDelayWhenLate,
        COUNT(DISTINCT SalesOrderNumber) AS UniqueOrders,
        ROUND(AVG(OrderQuantity), 2) AS AvgUnitsPerShipment
    FROM ShipmentMetrics
    GROUP BY Channel, OrderYear, OrderMonth, OrderMonthName
),

QuarterlyTrends AS (
    SELECT
        Channel,
        OrderYear,
        OrderQuarter,
        COUNT(*) AS TotalShipments,
        SUM(OrderQuantity) AS TotalUnitsShipped,
        ROUND(SUM(SalesAmount), 2) AS TotalRevenue,
        ROUND(AVG(LeadTimeDays), 2) AS AvgLeadTimeDays,
        ROUND(100.0 * SUM(OnTimeFlag) / COUNT(*), 2) AS OnTimeDeliveryPct
    FROM ShipmentMetrics
    GROUP BY Channel, OrderYear, OrderQuarter
),

SeasonalPatterns AS (
    SELECT
        Channel,
        OrderMonth,
        OrderMonthName,
        COUNT(*) AS TotalShipmentsAllYears,
        ROUND(AVG(TotalShipments), 2) AS AvgShipmentsPerYear,
        MIN(TotalShipments) AS MinYearShipments,
        MAX(TotalShipments) AS MaxYearShipments,
        ROUND(AVG(AvgLeadTimeDays), 2) AS AvgLeadTimeDays,
        ROUND(AVG(OnTimeDeliveryPct), 2) AS AvgOnTimeDeliveryPct
    FROM MonthlyTrends
    GROUP BY Channel, OrderMonth, OrderMonthName
),

WeeklyPatterns AS (
    SELECT
        Channel,
        OrderDayOfWeek,
        OrderDayName,
        COUNT(*) AS TotalShipments,
        ROUND(AVG(LeadTimeDays), 2) AS AvgLeadTimeDays,
        ROUND(100.0 * SUM(OnTimeFlag) / COUNT(*), 2) AS OnTimeDeliveryPct
    FROM ShipmentMetrics
    GROUP BY Channel, OrderDayOfWeek, OrderDayName
),

YearOverYearComparison AS (
    SELECT
        mt.Channel,
        mt.OrderMonth,
        mt.OrderMonthName,
        mt.OrderYear,
        mt.TotalShipments,
        mt.AvgLeadTimeDays,
        mt.OnTimeDeliveryPct,
        LAG(mt.TotalShipments) OVER (PARTITION BY mt.Channel, mt.OrderMonth ORDER BY mt.OrderYear) AS PrevYearShipments,
        LAG(mt.AvgLeadTimeDays) OVER (PARTITION BY mt.Channel, mt.OrderMonth ORDER BY mt.OrderYear) AS PrevYearAvgLeadTime,
        LAG(mt.OnTimeDeliveryPct) OVER (PARTITION BY mt.Channel, mt.OrderMonth ORDER BY mt.OrderYear) AS PrevYearOnTimePct,
        mt.TotalShipments - LAG(mt.TotalShipments) OVER (PARTITION BY mt.Channel, mt.OrderMonth ORDER BY mt.OrderYear) AS YoYShipmentChange,
        ROUND(100.0 * (mt.TotalShipments - LAG(mt.TotalShipments) OVER (PARTITION BY mt.Channel, mt.OrderMonth ORDER BY mt.OrderYear)) /
              NULLIF(LAG(mt.TotalShipments) OVER (PARTITION BY mt.Channel, mt.OrderMonth ORDER BY mt.OrderYear), 0), 2) AS YoYShipmentGrowthPct,
        ROUND(mt.AvgLeadTimeDays - LAG(mt.AvgLeadTimeDays) OVER (PARTITION BY mt.Channel, mt.OrderMonth ORDER BY mt.OrderYear), 2) AS YoYLeadTimeChange
    FROM MonthlyTrends mt
),

PeakPeriodIdentification AS (
    SELECT
        sp.Channel,
        sp.OrderMonth,
        sp.OrderMonthName,
        sp.AvgShipmentsPerYear,
        sp.AvgLeadTimeDays,
        sp.AvgOnTimeDeliveryPct,
        NTILE(4) OVER (PARTITION BY sp.Channel ORDER BY sp.AvgShipmentsPerYear DESC) AS VolumeQuartile,
        CASE
            WHEN NTILE(4) OVER (PARTITION BY sp.Channel ORDER BY sp.AvgShipmentsPerYear DESC) = 1 THEN 'Peak Season'
            WHEN NTILE(4) OVER (PARTITION BY sp.Channel ORDER BY sp.AvgShipmentsPerYear DESC) = 2 THEN 'High Season'
            WHEN NTILE(4) OVER (PARTITION BY sp.Channel ORDER BY sp.AvgShipmentsPerYear DESC) = 3 THEN 'Moderate Season'
            ELSE 'Low Season'
        END AS SeasonalCategory,
        RANK() OVER (PARTITION BY sp.Channel ORDER BY sp.AvgShipmentsPerYear DESC) AS VolumeRank
    FROM SeasonalPatterns sp
)

SELECT
    ppi.Channel,
    ppi.OrderMonth,
    ppi.OrderMonthName,
    ppi.AvgShipmentsPerYear,
    ppi.AvgLeadTimeDays,
    ppi.AvgOnTimeDeliveryPct,
    ppi.VolumeQuartile,
    ppi.SeasonalCategory,
    ppi.VolumeRank,
    -- Calculate capacity stress indicators
    CASE
        WHEN ppi.VolumeQuartile = 1 AND ppi.AvgOnTimeDeliveryPct < 90 THEN 'High Capacity Stress'
        WHEN ppi.VolumeQuartile = 1 AND ppi.AvgOnTimeDeliveryPct BETWEEN 90 AND 95 THEN 'Moderate Capacity Stress'
        WHEN ppi.VolumeQuartile = 1 THEN 'Within Capacity'
        ELSE 'No Stress'
    END AS CapacityStressIndicator,
    -- Identify months needing additional capacity
    CASE
        WHEN ppi.VolumeQuartile = 1 THEN 'Consider Additional Capacity'
        WHEN ppi.VolumeQuartile = 2 THEN 'Monitor Closely'
        ELSE 'Normal Operations'
    END AS CapacityRecommendation
FROM PeakPeriodIdentification ppi
ORDER BY ppi.Channel, ppi.OrderMonth;
```

---

# Summary

These five business intelligence questions provide comprehensive insights into shipment performance, logistics efficiency, and supply chain optimization opportunities within the AdventureWorks data warehouse:

1. **On-Time Delivery Performance** - Identifies delivery reliability issues by territory and channel, enabling targeted operational improvements
2. **Shipping Lead Time Analysis** - Reveals fulfillment speed patterns across geographies and product categories for process optimization
3. **Freight Cost Efficiency** - Highlights cost optimization opportunities through detailed freight analysis and efficiency benchmarking
4. **Product Category Complexity** - Quantifies shipping complexity by category to inform service level design and inventory positioning
5. **Seasonal Patterns** - Enables proactive capacity planning through identification of peak periods and seasonal stress points

These analyses leverage advanced SQL techniques to transform raw shipment data into actionable insights for supply chain management, cost optimization, and customer satisfaction improvement.
