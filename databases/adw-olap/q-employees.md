# Employee Performance and Sales Force Effectiveness Analysis

# Introduction

This document presents five complex business intelligence questions focused on employee performance, sales force effectiveness, and workforce optimization within the AdventureWorks data warehouse. These analyses examine sales employees through multiple lenses including quota attainment, territory performance, organizational hierarchy dynamics, tenure and experience effects, and product specialization patterns.

The queries leverage the relationship between employees (DimEmployee), their sales activities (FactResellerSales), quota assignments (FactSalesQuota), and organizational structure (employee hierarchy, territories, departments) to provide actionable insights for sales management, compensation planning, training prioritization, and talent development strategies.

---

# Business Question 1: Sales Employee Quota Attainment and Performance Ranking

## Intent

Analyze individual sales employee performance against assigned quotas across multiple time periods, calculating attainment rates, ranking employees by performance, and identifying top performers, underperformers, and improvement trends. This analysis provides critical input for compensation decisions, performance reviews, and sales coaching prioritization.

The query calculates:
- Actual sales vs. quota by employee and period
- Quota attainment percentage and over/under performance amounts
- Performance ranking and percentile positioning
- Year-over-year performance trends and trajectory analysis
- Territory-adjusted performance benchmarking

## SQL Code

```sql
WITH EmployeeSalesActuals AS (
    SELECT
        frs.EmployeeKey,
        dd.CalendarYear,
        dd.CalendarQuarter,
        COUNT(DISTINCT frs.SalesOrderNumber) AS TotalOrders,
        COUNT(*) AS TotalLineItems,
        SUM(frs.OrderQuantity) AS TotalUnits,
        ROUND(SUM(frs.SalesAmount), 2) AS ActualSalesAmount,
        ROUND(SUM(frs.SalesAmount - frs.TotalProductCost), 2) AS GrossProfit,
        ROUND(100.0 * SUM(frs.SalesAmount - frs.TotalProductCost) / NULLIF(SUM(frs.SalesAmount), 0), 2) AS GrossProfitMarginPct,
        COUNT(DISTINCT frs.ResellerKey) AS ActiveResellers,
        COUNT(DISTINCT frs.ProductKey) AS UniqueProductsSold
    FROM FactResellerSales frs
    INNER JOIN DimDate dd ON frs.OrderDateKey = dd.DateKey
    WHERE frs.EmployeeKey IS NOT NULL
    GROUP BY frs.EmployeeKey, dd.CalendarYear, dd.CalendarQuarter
),

EmployeeQuotas AS (
    SELECT
        fsq.EmployeeKey,
        fsq.CalendarYear,
        fsq.CalendarQuarter,
        ROUND(SUM(fsq.SalesAmountQuota), 2) AS QuotaAmount
    FROM FactSalesQuota fsq
    GROUP BY fsq.EmployeeKey, fsq.CalendarYear, fsq.CalendarQuarter
),

PerformanceMetrics AS (
    SELECT
        eq.EmployeeKey,
        eq.CalendarYear,
        eq.CalendarQuarter,
        e.FirstName || ' ' || e.LastName AS EmployeeName,
        e.Title AS JobTitle,
        e.HireDate,
        e.Status AS EmploymentStatus,
        st.SalesTerritoryRegion,
        st.SalesTerritoryCountry,
        st.SalesTerritoryGroup,
        eq.QuotaAmount,
        COALESCE(esa.ActualSalesAmount, 0) AS ActualSalesAmount,
        COALESCE(esa.GrossProfit, 0) AS GrossProfit,
        COALESCE(esa.GrossProfitMarginPct, 0) AS GrossProfitMarginPct,
        COALESCE(esa.TotalOrders, 0) AS TotalOrders,
        COALESCE(esa.ActiveResellers, 0) AS ActiveResellers,
        COALESCE(esa.UniqueProductsSold, 0) AS UniqueProductsSold,
        ROUND(COALESCE(esa.ActualSalesAmount, 0) - eq.QuotaAmount, 2) AS OverUnderAmount,
        ROUND(100.0 * COALESCE(esa.ActualSalesAmount, 0) / NULLIF(eq.QuotaAmount, 0), 2) AS QuotaAttainmentPct,
        CASE
            WHEN COALESCE(esa.ActualSalesAmount, 0) >= eq.QuotaAmount * 1.20 THEN 'Exceptional (120%+)'
            WHEN COALESCE(esa.ActualSalesAmount, 0) >= eq.QuotaAmount * 1.10 THEN 'Exceeds (110-119%)'
            WHEN COALESCE(esa.ActualSalesAmount, 0) >= eq.QuotaAmount * 1.00 THEN 'Meets (100-109%)'
            WHEN COALESCE(esa.ActualSalesAmount, 0) >= eq.QuotaAmount * 0.90 THEN 'Below (90-99%)'
            WHEN COALESCE(esa.ActualSalesAmount, 0) >= eq.QuotaAmount * 0.75 THEN 'Underperforming (75-89%)'
            ELSE 'Needs Attention (<75%)'
        END AS PerformanceCategory
    FROM EmployeeQuotas eq
    LEFT JOIN EmployeeSalesActuals esa
        ON eq.EmployeeKey = esa.EmployeeKey
        AND eq.CalendarYear = esa.CalendarYear
        AND eq.CalendarQuarter = esa.CalendarQuarter
    INNER JOIN DimEmployee e ON eq.EmployeeKey = e.EmployeeKey
    LEFT JOIN DimSalesTerritory st ON e.SalesTerritoryKey = st.SalesTerritoryKey
),

RankedPerformance AS (
    SELECT
        pm.*,
        RANK() OVER (
            PARTITION BY pm.CalendarYear, pm.CalendarQuarter
            ORDER BY pm.QuotaAttainmentPct DESC
        ) AS PerformanceRank,
        NTILE(10) OVER (
            PARTITION BY pm.CalendarYear, pm.CalendarQuarter
            ORDER BY pm.QuotaAttainmentPct DESC
        ) AS PerformanceDecile,
        ROUND(AVG(pm.QuotaAttainmentPct) OVER (
            PARTITION BY pm.CalendarYear, pm.CalendarQuarter
        ), 2) AS PeriodAvgAttainment,
        ROUND(AVG(pm.QuotaAttainmentPct) OVER (
            PARTITION BY pm.SalesTerritoryRegion, pm.CalendarYear, pm.CalendarQuarter
        ), 2) AS TerritoryAvgAttainment
    FROM PerformanceMetrics pm
),

YearOverYearTrends AS (
    SELECT
        rp.EmployeeKey,
        rp.EmployeeName,
        rp.CalendarYear,
        rp.CalendarQuarter,
        rp.JobTitle,
        rp.SalesTerritoryRegion,
        rp.SalesTerritoryCountry,
        rp.QuotaAmount,
        rp.ActualSalesAmount,
        rp.QuotaAttainmentPct,
        rp.OverUnderAmount,
        rp.GrossProfit,
        rp.GrossProfitMarginPct,
        rp.TotalOrders,
        rp.ActiveResellers,
        rp.PerformanceCategory,
        rp.PerformanceRank,
        rp.PerformanceDecile,
        rp.PeriodAvgAttainment,
        rp.TerritoryAvgAttainment,
        LAG(rp.ActualSalesAmount) OVER (
            PARTITION BY rp.EmployeeKey
            ORDER BY rp.CalendarYear, rp.CalendarQuarter
        ) AS PriorQuarterActualSales,
        LAG(rp.QuotaAttainmentPct) OVER (
            PARTITION BY rp.EmployeeKey
            ORDER BY rp.CalendarYear, rp.CalendarQuarter
        ) AS PriorQuarterAttainmentPct,
        ROUND(rp.ActualSalesAmount - LAG(rp.ActualSalesAmount) OVER (
            PARTITION BY rp.EmployeeKey
            ORDER BY rp.CalendarYear, rp.CalendarQuarter
        ), 2) AS QoQSalesChange,
        ROUND(100.0 * (rp.ActualSalesAmount - LAG(rp.ActualSalesAmount) OVER (
            PARTITION BY rp.EmployeeKey
            ORDER BY rp.CalendarYear, rp.CalendarQuarter
        )) / NULLIF(LAG(rp.ActualSalesAmount) OVER (
            PARTITION BY rp.EmployeeKey
            ORDER BY rp.CalendarYear, rp.CalendarQuarter
        ), 0), 2) AS QoQSalesGrowthPct
    FROM RankedPerformance rp
),

PerformanceTrajectory AS (
    SELECT
        yoy.*,
        CASE
            WHEN yoy.QoQSalesGrowthPct > 10 AND yoy.QuotaAttainmentPct >= 100 THEN 'Rising Star'
            WHEN yoy.QoQSalesGrowthPct > 0 AND yoy.QuotaAttainmentPct >= 100 THEN 'Steady Performer'
            WHEN yoy.QoQSalesGrowthPct < -10 AND yoy.QuotaAttainmentPct < 90 THEN 'At Risk'
            WHEN yoy.QoQSalesGrowthPct < 0 AND yoy.QuotaAttainmentPct < 100 THEN 'Needs Development'
            WHEN yoy.QuotaAttainmentPct >= 100 THEN 'Solid Contributor'
            ELSE 'Monitor Closely'
        END AS PerformanceTrajectory,
        ROUND(yoy.QuotaAttainmentPct - yoy.PeriodAvgAttainment, 2) AS AttainmentVsAvg,
        ROUND(yoy.QuotaAttainmentPct - yoy.TerritoryAvgAttainment, 2) AS AttainmentVsTerritoryAvg
    FROM YearOverYearTrends yoy
)

SELECT
    pt.EmployeeKey,
    pt.EmployeeName,
    pt.JobTitle,
    pt.CalendarYear,
    pt.CalendarQuarter,
    pt.SalesTerritoryRegion,
    pt.SalesTerritoryCountry,
    pt.QuotaAmount,
    pt.ActualSalesAmount,
    pt.QuotaAttainmentPct,
    pt.OverUnderAmount,
    pt.GrossProfit,
    pt.GrossProfitMarginPct,
    pt.TotalOrders,
    pt.ActiveResellers,
    pt.PerformanceCategory,
    pt.PerformanceRank,
    pt.PerformanceDecile,
    pt.PeriodAvgAttainment,
    pt.TerritoryAvgAttainment,
    pt.AttainmentVsAvg,
    pt.AttainmentVsTerritoryAvg,
    pt.PriorQuarterActualSales,
    pt.PriorQuarterAttainmentPct,
    pt.QoQSalesChange,
    pt.QoQSalesGrowthPct,
    pt.PerformanceTrajectory
FROM PerformanceTrajectory pt
ORDER BY pt.CalendarYear DESC, pt.CalendarQuarter DESC, pt.QuotaAttainmentPct DESC;
```

---

# Business Question 2: Territory Performance and Geographic Sales Distribution by Employee

## Intent

Evaluate employee effectiveness across different geographic territories, analyzing revenue concentration, territory penetration, and cross-territory sales patterns. This analysis helps identify territory assignment optimization opportunities, reveals geographic expertise strengths, and supports expansion or realignment strategies.

The query calculates:
- Sales distribution by employee across territories and countries
- Territory revenue concentration and diversification metrics
- Market penetration rates within assigned territories
- Cross-territory selling effectiveness for multi-region employees

## SQL Code

```sql
WITH EmployeeTerritoryBase AS (
    SELECT
        e.EmployeeKey,
        e.FirstName || ' ' || e.LastName AS EmployeeName,
        e.Title AS JobTitle,
        e.Status,
        e.HireDate,
        CAST(JULIANDAY('now') - JULIANDAY(e.HireDate) AS INTEGER) / 365.25 AS TenureYears,
        st_assigned.SalesTerritoryKey AS AssignedTerritoryKey,
        st_assigned.SalesTerritoryRegion AS AssignedTerritoryRegion,
        st_assigned.SalesTerritoryCountry AS AssignedTerritoryCountry,
        st_assigned.SalesTerritoryGroup AS AssignedTerritoryGroup
    FROM DimEmployee e
    LEFT JOIN DimSalesTerritory st_assigned ON e.SalesTerritoryKey = st_assigned.SalesTerritoryKey
    WHERE e.SalesPersonFlag = 1
),

EmployeeSalesByTerritory AS (
    SELECT
        frs.EmployeeKey,
        st.SalesTerritoryKey,
        st.SalesTerritoryRegion,
        st.SalesTerritoryCountry,
        st.SalesTerritoryGroup,
        dd.CalendarYear,
        COUNT(DISTINCT frs.SalesOrderNumber) AS TotalOrders,
        COUNT(DISTINCT frs.ResellerKey) AS UniqueResellers,
        COUNT(DISTINCT frs.ProductKey) AS UniqueProducts,
        SUM(frs.OrderQuantity) AS TotalUnits,
        ROUND(SUM(frs.SalesAmount), 2) AS TotalRevenue,
        ROUND(SUM(frs.SalesAmount - frs.TotalProductCost), 2) AS GrossProfit,
        ROUND(AVG(frs.SalesAmount), 2) AS AvgOrderValue
    FROM FactResellerSales frs
    INNER JOIN DimSalesTerritory st ON frs.SalesTerritoryKey = st.SalesTerritoryKey
    INNER JOIN DimDate dd ON frs.OrderDateKey = dd.DateKey
    WHERE frs.EmployeeKey IS NOT NULL
    GROUP BY frs.EmployeeKey, st.SalesTerritoryKey, st.SalesTerritoryRegion,
             st.SalesTerritoryCountry, st.SalesTerritoryGroup, dd.CalendarYear
),

EmployeeTerritoryPerformance AS (
    SELECT
        etb.EmployeeKey,
        etb.EmployeeName,
        etb.JobTitle,
        etb.TenureYears,
        etb.AssignedTerritoryRegion,
        etb.AssignedTerritoryCountry,
        esbt.SalesTerritoryRegion AS SalesTerritoryRegion,
        esbt.SalesTerritoryCountry AS SalesTerritoryCountry,
        esbt.SalesTerritoryGroup,
        esbt.CalendarYear,
        CASE
            WHEN etb.AssignedTerritoryKey = esbt.SalesTerritoryKey THEN 'Assigned Territory'
            ELSE 'Cross-Territory'
        END AS TerritoryType,
        esbt.TotalOrders,
        esbt.UniqueResellers,
        esbt.UniqueProducts,
        esbt.TotalRevenue,
        esbt.GrossProfit,
        esbt.AvgOrderValue
    FROM EmployeeTerritoryBase etb
    INNER JOIN EmployeeSalesByTerritory esbt ON etb.EmployeeKey = esbt.EmployeeKey
),

EmployeeRevenueDistribution AS (
    SELECT
        etp.EmployeeKey,
        etp.EmployeeName,
        etp.JobTitle,
        etp.CalendarYear,
        etp.SalesTerritoryCountry,
        etp.SalesTerritoryRegion,
        etp.TerritoryType,
        etp.TotalRevenue,
        SUM(etp.TotalRevenue) OVER (
            PARTITION BY etp.EmployeeKey, etp.CalendarYear
        ) AS EmployeeTotalRevenue,
        ROUND(100.0 * etp.TotalRevenue / SUM(etp.TotalRevenue) OVER (
            PARTITION BY etp.EmployeeKey, etp.CalendarYear
        ), 2) AS RevenuePctOfEmployeeTotal,
        SUM(etp.TotalRevenue) OVER (
            PARTITION BY etp.SalesTerritoryCountry, etp.CalendarYear
        ) AS CountryTotalRevenue,
        ROUND(100.0 * etp.TotalRevenue / SUM(etp.TotalRevenue) OVER (
            PARTITION BY etp.SalesTerritoryCountry, etp.CalendarYear
        ), 2) AS RevenuePctOfCountryTotal,
        etp.TotalOrders,
        etp.UniqueResellers,
        etp.GrossProfit,
        RANK() OVER (
            PARTITION BY etp.EmployeeKey, etp.CalendarYear
            ORDER BY etp.TotalRevenue DESC
        ) AS TerritoryRevenueRank
    FROM EmployeeTerritoryPerformance etp
),

TerritoryConcentrationMetrics AS (
    SELECT
        erd.EmployeeKey,
        erd.EmployeeName,
        erd.CalendarYear,
        COUNT(DISTINCT erd.SalesTerritoryCountry) AS CountriesServed,
        COUNT(DISTINCT erd.SalesTerritoryRegion) AS RegionsServed,
        ROUND(SUM(erd.TotalRevenue), 2) AS TotalRevenue,
        ROUND(SUM(erd.GrossProfit), 2) AS TotalGrossProfit,
        SUM(erd.TotalOrders) AS TotalOrders,
        SUM(erd.UniqueResellers) AS TotalResellers,
        -- Herfindahl-Hirschman Index for revenue concentration
        ROUND(SUM(erd.RevenuePctOfEmployeeTotal * erd.RevenuePctOfEmployeeTotal), 2) AS RevenueConcentrationHHI,
        -- Top territory contribution
        MAX(erd.RevenuePctOfEmployeeTotal) AS TopTerritoryRevenuePct,
        MAX(CASE WHEN erd.TerritoryRevenueRank = 1 THEN erd.SalesTerritoryRegion END) AS TopTerritoryRegion,
        MAX(CASE WHEN erd.TerritoryRevenueRank = 1 THEN erd.SalesTerritoryCountry END) AS TopTerritoryCountry,
        -- Cross-territory analysis
        SUM(CASE WHEN erd.TerritoryType = 'Cross-Territory' THEN erd.TotalRevenue ELSE 0 END) AS CrossTerritoryRevenue,
        ROUND(100.0 * SUM(CASE WHEN erd.TerritoryType = 'Cross-Territory' THEN erd.TotalRevenue ELSE 0 END) /
              NULLIF(SUM(erd.TotalRevenue), 0), 2) AS CrossTerritoryRevenuePct
    FROM EmployeeRevenueDistribution erd
    GROUP BY erd.EmployeeKey, erd.EmployeeName, erd.CalendarYear
),

TerritoryDiversificationScoring AS (
    SELECT
        tcm.*,
        CASE
            WHEN tcm.RevenueConcentrationHHI > 5000 THEN 'Highly Concentrated (Single Territory)'
            WHEN tcm.RevenueConcentrationHHI > 3000 THEN 'Concentrated (2-3 Territories)'
            WHEN tcm.RevenueConcentrationHHI > 1500 THEN 'Moderately Diversified'
            ELSE 'Highly Diversified'
        END AS DiversificationLevel,
        CASE
            WHEN tcm.CountriesServed >= 3 AND tcm.CrossTerritoryRevenuePct > 30 THEN 'Global Specialist'
            WHEN tcm.CountriesServed >= 2 AND tcm.CrossTerritoryRevenuePct > 20 THEN 'Regional Specialist'
            WHEN tcm.TopTerritoryRevenuePct > 80 THEN 'Territory Focused'
            ELSE 'Balanced Territory Mix'
        END AS TerritoryExpertiseType,
        RANK() OVER (PARTITION BY tcm.CalendarYear ORDER BY tcm.TotalRevenue DESC) AS RevenueRank,
        RANK() OVER (PARTITION BY tcm.CalendarYear ORDER BY tcm.CountriesServed DESC, tcm.CrossTerritoryRevenuePct DESC) AS DiversificationRank
    FROM TerritoryConcentrationMetrics tcm
)

SELECT
    tds.EmployeeKey,
    tds.EmployeeName,
    tds.CalendarYear,
    tds.CountriesServed,
    tds.RegionsServed,
    tds.TotalRevenue,
    tds.TotalGrossProfit,
    tds.TotalOrders,
    tds.TotalResellers,
    tds.RevenueConcentrationHHI,
    tds.TopTerritoryRevenuePct,
    tds.TopTerritoryRegion,
    tds.TopTerritoryCountry,
    tds.CrossTerritoryRevenue,
    tds.CrossTerritoryRevenuePct,
    tds.DiversificationLevel,
    tds.TerritoryExpertiseType,
    tds.RevenueRank,
    tds.DiversificationRank
FROM TerritoryDiversificationScoring tds
ORDER BY tds.CalendarYear DESC, tds.TotalRevenue DESC;
```

---

# Business Question 3: Employee Hierarchy Performance and Team Effectiveness

## Intent

Analyze organizational hierarchy dynamics by examining how managers and their teams perform, calculating aggregate team metrics, comparing individual contributor performance to team averages, and identifying high-performing management chains versus underperforming organizational pockets. This supports talent management, succession planning, and organizational design decisions.

The query calculates:
- Recursive employee hierarchy traversal from executives to individual contributors
- Aggregate team performance metrics rolled up through management layers
- Individual vs. team performance comparisons
- Management effectiveness scoring based on team outcomes

## SQL Code

```sql
WITH RECURSIVE EmployeeHierarchy AS (
    -- Base case: Top-level employees (no manager)
    SELECT
        e.EmployeeKey,
        e.FirstName || ' ' || e.LastName AS EmployeeName,
        e.Title,
        e.ParentEmployeeKey,
        NULL AS ManagerName,
        e.HireDate,
        e.Status,
        e.SalesPersonFlag,
        st.SalesTerritoryRegion,
        st.SalesTerritoryCountry,
        1 AS HierarchyLevel,
        CAST(e.EmployeeKey AS TEXT) AS HierarchyPath,
        e.FirstName || ' ' || e.LastName AS HierarchyPathNames
    FROM DimEmployee e
    LEFT JOIN DimSalesTerritory st ON e.SalesTerritoryKey = st.SalesTerritoryKey
    WHERE e.ParentEmployeeKey IS NULL
        AND e.Status = 'Current'

    UNION ALL

    -- Recursive case: Employees with managers
    SELECT
        e.EmployeeKey,
        e.FirstName || ' ' || e.LastName AS EmployeeName,
        e.Title,
        e.ParentEmployeeKey,
        eh.EmployeeName AS ManagerName,
        e.HireDate,
        e.Status,
        e.SalesPersonFlag,
        st.SalesTerritoryRegion,
        st.SalesTerritoryCountry,
        eh.HierarchyLevel + 1 AS HierarchyLevel,
        eh.HierarchyPath || ' > ' || CAST(e.EmployeeKey AS TEXT) AS HierarchyPath,
        eh.HierarchyPathNames || ' > ' || e.FirstName || ' ' || e.LastName AS HierarchyPathNames
    FROM DimEmployee e
    INNER JOIN EmployeeHierarchy eh ON e.ParentEmployeeKey = eh.EmployeeKey
    LEFT JOIN DimSalesTerritory st ON e.SalesTerritoryKey = st.SalesTerritoryKey
    WHERE e.Status = 'Current'
),

IndividualSalesPerformance AS (
    SELECT
        frs.EmployeeKey,
        dd.CalendarYear,
        COUNT(DISTINCT frs.SalesOrderNumber) AS TotalOrders,
        COUNT(DISTINCT frs.ResellerKey) AS ActiveResellers,
        ROUND(SUM(frs.SalesAmount), 2) AS TotalRevenue,
        ROUND(SUM(frs.SalesAmount - frs.TotalProductCost), 2) AS GrossProfit,
        ROUND(100.0 * SUM(frs.SalesAmount - frs.TotalProductCost) / NULLIF(SUM(frs.SalesAmount), 0), 2) AS GrossProfitMarginPct
    FROM FactResellerSales frs
    INNER JOIN DimDate dd ON frs.OrderDateKey = dd.DateKey
    WHERE frs.EmployeeKey IS NOT NULL
    GROUP BY frs.EmployeeKey, dd.CalendarYear
),

IndividualQuotaPerformance AS (
    SELECT
        fsq.EmployeeKey,
        fsq.CalendarYear,
        ROUND(SUM(fsq.SalesAmountQuota), 2) AS AnnualQuota,
        ROUND(100.0 * SUM(isp.TotalRevenue) / NULLIF(SUM(fsq.SalesAmountQuota), 0), 2) AS QuotaAttainmentPct
    FROM FactSalesQuota fsq
    LEFT JOIN IndividualSalesPerformance isp
        ON fsq.EmployeeKey = isp.EmployeeKey
        AND fsq.CalendarYear = isp.CalendarYear
    GROUP BY fsq.EmployeeKey, fsq.CalendarYear
),

EmployeeWithPerformance AS (
    SELECT
        eh.EmployeeKey,
        eh.EmployeeName,
        eh.Title,
        eh.ParentEmployeeKey,
        eh.ManagerName,
        eh.HireDate,
        eh.SalesPersonFlag,
        eh.SalesTerritoryRegion,
        eh.SalesTerritoryCountry,
        eh.HierarchyLevel,
        eh.HierarchyPath,
        eh.HierarchyPathNames,
        isp.CalendarYear,
        COALESCE(isp.TotalRevenue, 0) AS IndividualRevenue,
        COALESCE(isp.GrossProfit, 0) AS IndividualGrossProfit,
        COALESCE(isp.GrossProfitMarginPct, 0) AS IndividualMarginPct,
        COALESCE(isp.TotalOrders, 0) AS IndividualOrders,
        COALESCE(isp.ActiveResellers, 0) AS IndividualResellers,
        COALESCE(iqp.AnnualQuota, 0) AS IndividualQuota,
        COALESCE(iqp.QuotaAttainmentPct, 0) AS IndividualQuotaAttainmentPct
    FROM EmployeeHierarchy eh
    LEFT JOIN IndividualSalesPerformance isp ON eh.EmployeeKey = isp.EmployeeKey
    LEFT JOIN IndividualQuotaPerformance iqp
        ON eh.EmployeeKey = iqp.EmployeeKey
        AND isp.CalendarYear = iqp.CalendarYear
),

TeamAggregatePerformance AS (
    -- Calculate aggregate performance for each employee's team (direct and indirect reports)
    SELECT
        manager.EmployeeKey AS ManagerEmployeeKey,
        manager.EmployeeName AS ManagerName,
        manager.Title AS ManagerTitle,
        manager.CalendarYear,
        COUNT(DISTINCT reports.EmployeeKey) AS TotalTeamMembers,
        COUNT(DISTINCT CASE WHEN reports.SalesPersonFlag = 1 THEN reports.EmployeeKey END) AS SalesTeamMembers,
        ROUND(SUM(reports.IndividualRevenue), 2) AS TeamTotalRevenue,
        ROUND(SUM(reports.IndividualGrossProfit), 2) AS TeamTotalGrossProfit,
        ROUND(AVG(CASE WHEN reports.IndividualRevenue > 0 THEN reports.IndividualRevenue END), 2) AS TeamAvgRevenue,
        ROUND(AVG(CASE WHEN reports.IndividualQuotaAttainmentPct > 0 THEN reports.IndividualQuotaAttainmentPct END), 2) AS TeamAvgQuotaAttainment,
        SUM(reports.IndividualOrders) AS TeamTotalOrders,
        COUNT(DISTINCT CASE WHEN reports.IndividualQuotaAttainmentPct >= 100 THEN reports.EmployeeKey END) AS TeamMembersAtOrAboveQuota,
        COUNT(DISTINCT CASE WHEN reports.IndividualQuotaAttainmentPct < 75 THEN reports.EmployeeKey END) AS TeamMembersUnderperforming,
        MAX(reports.IndividualRevenue) AS TopPerformerRevenue,
        MIN(CASE WHEN reports.IndividualRevenue > 0 THEN reports.IndividualRevenue END) AS LowestPerformerRevenue
    FROM EmployeeWithPerformance manager
    INNER JOIN EmployeeWithPerformance reports
        ON reports.HierarchyPath LIKE manager.HierarchyPath || '%'
        AND reports.EmployeeKey != manager.EmployeeKey
        AND reports.CalendarYear = manager.CalendarYear
    WHERE manager.CalendarYear IS NOT NULL
    GROUP BY manager.EmployeeKey, manager.EmployeeName, manager.Title, manager.CalendarYear
),

ManagerEffectivenessScoring AS (
    SELECT
        tap.*,
        -- Include manager's own performance
        ewp.IndividualRevenue AS ManagerIndividualRevenue,
        ewp.IndividualQuotaAttainmentPct AS ManagerIndividualQuotaAttainment,
        -- Combined performance (manager + team)
        ROUND(tap.TeamTotalRevenue + COALESCE(ewp.IndividualRevenue, 0), 2) AS CombinedRevenue,
        -- Team effectiveness metrics
        ROUND(100.0 * tap.TeamMembersAtOrAboveQuota / NULLIF(tap.SalesTeamMembers, 0), 2) AS TeamQuotaSuccessRate,
        ROUND(100.0 * tap.TeamMembersUnderperforming / NULLIF(tap.SalesTeamMembers, 0), 2) AS TeamUnderperformanceRate,
        CASE
            WHEN tap.TopPerformerRevenue > 0 AND tap.LowestPerformerRevenue > 0
            THEN ROUND(tap.TopPerformerRevenue / NULLIF(tap.LowestPerformerRevenue, 0), 2)
            ELSE NULL
        END AS TeamPerformanceSpread,
        -- Management effectiveness score (0-100)
        ROUND(
            (CASE WHEN tap.TeamAvgQuotaAttainment >= 100 THEN 40 ELSE tap.TeamAvgQuotaAttainment * 0.4 END) +
            (CASE WHEN tap.TeamQuotaSuccessRate >= 80 THEN 30 ELSE tap.TeamQuotaSuccessRate * 0.375 END) +
            (CASE WHEN tap.TeamUnderperformanceRate <= 10 THEN 30 ELSE 30 - (tap.TeamUnderperformanceRate * 2) END)
        , 2) AS ManagementEffectivenessScore,
        RANK() OVER (PARTITION BY tap.CalendarYear ORDER BY tap.TeamTotalRevenue DESC) AS TeamRevenueRank,
        RANK() OVER (PARTITION BY tap.CalendarYear ORDER BY tap.TeamAvgQuotaAttainment DESC) AS TeamQuotaAttainmentRank
    FROM TeamAggregatePerformance tap
    LEFT JOIN EmployeeWithPerformance ewp
        ON tap.ManagerEmployeeKey = ewp.EmployeeKey
        AND tap.CalendarYear = ewp.CalendarYear
),

ManagementEffectivenessCategories AS (
    SELECT
        mes.*,
        CASE
            WHEN mes.ManagementEffectivenessScore >= 85 THEN 'Exceptional Manager'
            WHEN mes.ManagementEffectivenessScore >= 70 THEN 'Effective Manager'
            WHEN mes.ManagementEffectivenessScore >= 55 THEN 'Developing Manager'
            ELSE 'Needs Management Support'
        END AS ManagementEffectivenessCategory
    FROM ManagerEffectivenessScoring mes
)

SELECT
    mec.ManagerEmployeeKey,
    mec.ManagerName,
    mec.ManagerTitle,
    mec.CalendarYear,
    mec.TotalTeamMembers,
    mec.SalesTeamMembers,
    mec.TeamTotalRevenue,
    mec.TeamTotalGrossProfit,
    mec.TeamAvgRevenue,
    mec.TeamAvgQuotaAttainment,
    mec.TeamTotalOrders,
    mec.TeamMembersAtOrAboveQuota,
    mec.TeamMembersUnderperforming,
    mec.TeamQuotaSuccessRate,
    mec.TeamUnderperformanceRate,
    mec.TopPerformerRevenue,
    mec.LowestPerformerRevenue,
    mec.TeamPerformanceSpread,
    mec.ManagerIndividualRevenue,
    mec.ManagerIndividualQuotaAttainment,
    mec.CombinedRevenue,
    mec.ManagementEffectivenessScore,
    mec.ManagementEffectivenessCategory,
    mec.TeamRevenueRank,
    mec.TeamQuotaAttainmentRank
FROM ManagementEffectivenessCategories mec
ORDER BY mec.CalendarYear DESC, mec.ManagementEffectivenessScore DESC;
```

---

# Business Question 4: Employee Tenure, Experience, and Performance Correlation

## Intent

Examine the relationship between employee tenure, experience level, and sales performance to identify optimal experience curves, high-potential early-career employees, and potential retention risks among top performers. This analysis informs hiring strategies, training program design, compensation adjustments, and retention initiatives.

The query calculates:
- Tenure cohorts and performance benchmarks by experience level
- Time-to-productivity metrics for newer employees
- Career progression and performance trajectory analysis
- Retention risk scoring for high performers

## SQL Code

```sql
WITH EmployeeBaseline AS (
    SELECT
        e.EmployeeKey,
        e.FirstName || ' ' || e.LastName AS EmployeeName,
        e.Title AS JobTitle,
        e.HireDate,
        e.BirthDate,
        e.Gender,
        e.MaritalStatus,
        e.Status AS EmploymentStatus,
        e.SalesPersonFlag,
        st.SalesTerritoryRegion,
        st.SalesTerritoryCountry,
        CAST(JULIANDAY('now') - JULIANDAY(e.HireDate) AS INTEGER) AS TenureDays,
        ROUND(CAST(JULIANDAY('now') - JULIANDAY(e.HireDate) AS INTEGER) / 365.25, 2) AS TenureYears,
        CAST(JULIANDAY('now') - JULIANDAY(e.BirthDate) AS INTEGER) / 365.25 AS AgeYears,
        CASE
            WHEN CAST(JULIANDAY('now') - JULIANDAY(e.HireDate) AS INTEGER) / 365.25 < 1 THEN '<1 Year'
            WHEN CAST(JULIANDAY('now') - JULIANDAY(e.HireDate) AS INTEGER) / 365.25 < 2 THEN '1-2 Years'
            WHEN CAST(JULIANDAY('now') - JULIANDAY(e.HireDate) AS INTEGER) / 365.25 < 3 THEN '2-3 Years'
            WHEN CAST(JULIANDAY('now') - JULIANDAY(e.HireDate) AS INTEGER) / 365.25 < 5 THEN '3-5 Years'
            WHEN CAST(JULIANDAY('now') - JULIANDAY(e.HireDate) AS INTEGER) / 365.25 < 10 THEN '5-10 Years'
            ELSE '10+ Years'
        END AS TenureCohort
    FROM DimEmployee e
    LEFT JOIN DimSalesTerritory st ON e.SalesTerritoryKey = st.SalesTerritoryKey
    WHERE e.Status = 'Current' AND e.SalesPersonFlag = 1
),

EmployeeAnnualPerformance AS (
    SELECT
        frs.EmployeeKey,
        dd.CalendarYear,
        COUNT(DISTINCT frs.SalesOrderNumber) AS AnnualOrders,
        COUNT(DISTINCT frs.ResellerKey) AS AnnualResellers,
        COUNT(DISTINCT frs.ProductKey) AS AnnualUniqueProducts,
        ROUND(SUM(frs.SalesAmount), 2) AS AnnualRevenue,
        ROUND(SUM(frs.SalesAmount - frs.TotalProductCost), 2) AS AnnualGrossProfit,
        ROUND(100.0 * SUM(frs.SalesAmount - frs.TotalProductCost) / NULLIF(SUM(frs.SalesAmount), 0), 2) AS AnnualMarginPct,
        ROUND(AVG(frs.SalesAmount), 2) AS AvgDealSize
    FROM FactResellerSales frs
    INNER JOIN DimDate dd ON frs.OrderDateKey = dd.DateKey
    WHERE frs.EmployeeKey IS NOT NULL
    GROUP BY frs.EmployeeKey, dd.CalendarYear
),

EmployeeQuotaData AS (
    SELECT
        fsq.EmployeeKey,
        fsq.CalendarYear,
        ROUND(SUM(fsq.SalesAmountQuota), 2) AS AnnualQuota,
        ROUND(100.0 * SUM(eap.AnnualRevenue) / NULLIF(SUM(fsq.SalesAmountQuota), 0), 2) AS QuotaAttainmentPct
    FROM FactSalesQuota fsq
    LEFT JOIN EmployeeAnnualPerformance eap
        ON fsq.EmployeeKey = eap.EmployeeKey
        AND fsq.CalendarYear = eap.CalendarYear
    GROUP BY fsq.EmployeeKey, fsq.CalendarYear
),

EmployeeTenurePerformance AS (
    SELECT
        eb.EmployeeKey,
        eb.EmployeeName,
        eb.JobTitle,
        eb.HireDate,
        eb.TenureYears,
        eb.TenureCohort,
        eb.AgeYears,
        eb.Gender,
        eb.SalesTerritoryRegion,
        eb.SalesTerritoryCountry,
        eap.CalendarYear,
        eap.AnnualRevenue,
        eap.AnnualGrossProfit,
        eap.AnnualMarginPct,
        eap.AnnualOrders,
        eap.AnnualResellers,
        eap.AnnualUniqueProducts,
        eap.AvgDealSize,
        eqd.AnnualQuota,
        eqd.QuotaAttainmentPct,
        -- Calculate years of experience at time of this performance year
        ROUND(CAST(JULIANDAY(CAST(eap.CalendarYear || '-12-31' AS DATE)) - JULIANDAY(eb.HireDate) AS INTEGER) / 365.25, 2) AS ExperienceYearsAtPeriod,
        CASE
            WHEN CAST(JULIANDAY(CAST(eap.CalendarYear || '-12-31' AS DATE)) - JULIANDAY(eb.HireDate) AS INTEGER) / 365.25 < 1 THEN 'Year 1'
            WHEN CAST(JULIANDAY(CAST(eap.CalendarYear || '-12-31' AS DATE)) - JULIANDAY(eb.HireDate) AS INTEGER) / 365.25 < 2 THEN 'Year 2'
            WHEN CAST(JULIANDAY(CAST(eap.CalendarYear || '-12-31' AS DATE)) - JULIANDAY(eb.HireDate) AS INTEGER) / 365.25 < 3 THEN 'Year 3'
            WHEN CAST(JULIANDAY(CAST(eap.CalendarYear || '-12-31' AS DATE)) - JULIANDAY(eb.HireDate) AS INTEGER) / 365.25 < 5 THEN 'Year 3-5'
            ELSE 'Year 5+'
        END AS ExperienceBandAtPeriod
    FROM EmployeeBaseline eb
    LEFT JOIN EmployeeAnnualPerformance eap ON eb.EmployeeKey = eap.EmployeeKey
    LEFT JOIN EmployeeQuotaData eqd
        ON eb.EmployeeKey = eqd.EmployeeKey
        AND eap.CalendarYear = eqd.CalendarYear
    WHERE eap.CalendarYear IS NOT NULL
),

TenureCohortBenchmarks AS (
    SELECT
        ExperienceBandAtPeriod,
        CalendarYear,
        COUNT(DISTINCT EmployeeKey) AS CohortSize,
        ROUND(AVG(AnnualRevenue), 2) AS CohortAvgRevenue,
        ROUND(AVG(QuotaAttainmentPct), 2) AS CohortAvgQuotaAttainment,
        ROUND(AVG(AnnualMarginPct), 2) AS CohortAvgMarginPct,
        ROUND(AVG(AvgDealSize), 2) AS CohortAvgDealSize,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY AnnualRevenue) AS CohortRevenue25thPercentile,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY AnnualRevenue) AS CohortRevenueMedian,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY AnnualRevenue) AS CohortRevenue75thPercentile,
        PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY AnnualRevenue) AS CohortRevenue90thPercentile
    FROM EmployeeTenurePerformance
    WHERE AnnualRevenue > 0
    GROUP BY ExperienceBandAtPeriod, CalendarYear
),

EmployeeVsCohortComparison AS (
    SELECT
        etp.*,
        tcb.CohortSize,
        tcb.CohortAvgRevenue,
        tcb.CohortAvgQuotaAttainment,
        tcb.CohortAvgMarginPct,
        tcb.CohortRevenueMedian,
        tcb.CohortRevenue75thPercentile,
        tcb.CohortRevenue90thPercentile,
        ROUND(etp.AnnualRevenue - tcb.CohortAvgRevenue, 2) AS RevenueVsCohortAvg,
        ROUND(100.0 * (etp.AnnualRevenue - tcb.CohortAvgRevenue) / NULLIF(tcb.CohortAvgRevenue, 0), 2) AS RevenueVsCohortAvgPct,
        CASE
            WHEN etp.AnnualRevenue >= tcb.CohortRevenue90thPercentile THEN 'Top 10% of Cohort'
            WHEN etp.AnnualRevenue >= tcb.CohortRevenue75thPercentile THEN 'Top 25% of Cohort'
            WHEN etp.AnnualRevenue >= tcb.CohortRevenueMedian THEN 'Above Median'
            ELSE 'Below Median'
        END AS CohortPerformanceRating,
        RANK() OVER (
            PARTITION BY etp.ExperienceBandAtPeriod, etp.CalendarYear
            ORDER BY etp.AnnualRevenue DESC
        ) AS CohortRank,
        NTILE(10) OVER (
            PARTITION BY etp.ExperienceBandAtPeriod, etp.CalendarYear
            ORDER BY etp.AnnualRevenue DESC
        ) AS CohortDecile
    FROM EmployeeTenurePerformance etp
    INNER JOIN TenureCohortBenchmarks tcb
        ON etp.ExperienceBandAtPeriod = tcb.ExperienceBandAtPeriod
        AND etp.CalendarYear = tcb.CalendarYear
),

PerformanceTrajectory AS (
    SELECT
        evcc.EmployeeKey,
        evcc.EmployeeName,
        evcc.CalendarYear,
        evcc.AnnualRevenue,
        evcc.QuotaAttainmentPct,
        LAG(evcc.AnnualRevenue, 1) OVER (PARTITION BY evcc.EmployeeKey ORDER BY evcc.CalendarYear) AS PriorYearRevenue,
        LAG(evcc.QuotaAttainmentPct, 1) OVER (PARTITION BY evcc.EmployeeKey ORDER BY evcc.CalendarYear) AS PriorYearQuotaAttainment,
        ROUND(evcc.AnnualRevenue - LAG(evcc.AnnualRevenue, 1) OVER (PARTITION BY evcc.EmployeeKey ORDER BY evcc.CalendarYear), 2) AS YoYRevenueChange,
        ROUND(100.0 * (evcc.AnnualRevenue - LAG(evcc.AnnualRevenue, 1) OVER (PARTITION BY evcc.EmployeeKey ORDER BY evcc.CalendarYear)) /
              NULLIF(LAG(evcc.AnnualRevenue, 1) OVER (PARTITION BY evcc.EmployeeKey ORDER BY evcc.CalendarYear), 0), 2) AS YoYRevenueGrowthPct,
        evcc.CohortPerformanceRating,
        evcc.CohortRank,
        evcc.CohortDecile
    FROM EmployeeVsCohortComparison evcc
),

TalentSegmentation AS (
    SELECT
        evcc.*,
        pt.YoYRevenueGrowthPct,
        CASE
            WHEN evcc.CohortDecile <= 2 AND pt.YoYRevenueGrowthPct > 10 THEN 'High Potential Star'
            WHEN evcc.CohortDecile <= 2 THEN 'Top Performer'
            WHEN evcc.CohortDecile <= 5 AND pt.YoYRevenueGrowthPct > 15 THEN 'Rising Talent'
            WHEN evcc.CohortDecile <= 5 THEN 'Solid Contributor'
            WHEN pt.YoYRevenueGrowthPct < -10 THEN 'Performance Concern'
            ELSE 'Development Needed'
        END AS TalentSegment,
        CASE
            WHEN evcc.TenureYears > 5 AND evcc.CohortDecile <= 2 THEN 'High Risk - Critical Retention'
            WHEN evcc.TenureYears > 3 AND evcc.CohortDecile <= 3 THEN 'Medium Risk - Monitor'
            ELSE 'Low Risk'
        END AS RetentionRisk
    FROM EmployeeVsCohortComparison evcc
    LEFT JOIN PerformanceTrajectory pt
        ON evcc.EmployeeKey = pt.EmployeeKey
        AND evcc.CalendarYear = pt.CalendarYear
)

SELECT
    ts.EmployeeKey,
    ts.EmployeeName,
    ts.JobTitle,
    ts.HireDate,
    ts.TenureYears,
    ts.TenureCohort,
    ts.ExperienceBandAtPeriod,
    ts.CalendarYear,
    ts.AnnualRevenue,
    ts.AnnualGrossProfit,
    ts.AnnualMarginPct,
    ts.QuotaAttainmentPct,
    ts.AnnualOrders,
    ts.AnnualResellers,
    ts.AvgDealSize,
    ts.CohortSize,
    ts.CohortAvgRevenue,
    ts.CohortAvgQuotaAttainment,
    ts.RevenueVsCohortAvg,
    ts.RevenueVsCohortAvgPct,
    ts.CohortPerformanceRating,
    ts.CohortRank,
    ts.CohortDecile,
    ts.YoYRevenueGrowthPct,
    ts.TalentSegment,
    ts.RetentionRisk,
    ts.SalesTerritoryRegion,
    ts.SalesTerritoryCountry
FROM TalentSegmentation ts
ORDER BY ts.CalendarYear DESC, ts.AnnualRevenue DESC;
```

---

# Business Question 5: Employee Product Specialization and Portfolio Diversification

## Intent

Analyze employee expertise and specialization patterns across product categories, identifying product champions with deep category knowledge versus generalists with broad portfolio coverage. This analysis informs territory and account assignments, training needs identification, cross-selling opportunity identification, and optimal team composition for complex sales opportunities.

The query calculates:
- Product category revenue distribution by employee
- Specialization vs. diversification scoring
- Category expertise depth metrics
- Product portfolio complexity and breadth analysis

## SQL Code

```sql
WITH EmployeeProductSales AS (
    SELECT
        frs.EmployeeKey,
        p.ProductKey,
        p.EnglishProductName AS ProductName,
        psc.ProductSubcategoryKey,
        psc.EnglishProductSubcategoryName AS SubcategoryName,
        pc.ProductCategoryKey,
        pc.EnglishProductCategoryName AS CategoryName,
        dd.CalendarYear,
        COUNT(DISTINCT frs.SalesOrderNumber) AS OrderCount,
        SUM(frs.OrderQuantity) AS TotalUnits,
        ROUND(SUM(frs.SalesAmount), 2) AS TotalRevenue,
        ROUND(SUM(frs.SalesAmount - frs.TotalProductCost), 2) AS GrossProfit,
        COUNT(DISTINCT frs.ResellerKey) AS UniqueResellers
    FROM FactResellerSales frs
    INNER JOIN DimProduct p ON frs.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    INNER JOIN DimDate dd ON frs.OrderDateKey = dd.DateKey
    WHERE frs.EmployeeKey IS NOT NULL
        AND pc.EnglishProductCategoryName IS NOT NULL
    GROUP BY frs.EmployeeKey, p.ProductKey, p.EnglishProductName,
             psc.ProductSubcategoryKey, psc.EnglishProductSubcategoryName,
             pc.ProductCategoryKey, pc.EnglishProductCategoryName, dd.CalendarYear
),

EmployeeCategoryPerformance AS (
    SELECT
        eps.EmployeeKey,
        eps.CategoryName,
        eps.CalendarYear,
        COUNT(DISTINCT eps.ProductKey) AS UniqueProductsInCategory,
        COUNT(DISTINCT eps.SubcategoryName) AS UniqueSubcategoriesInCategory,
        SUM(eps.OrderCount) AS CategoryOrderCount,
        SUM(eps.TotalUnits) AS CategoryTotalUnits,
        ROUND(SUM(eps.TotalRevenue), 2) AS CategoryRevenue,
        ROUND(SUM(eps.GrossProfit), 2) AS CategoryGrossProfit,
        ROUND(100.0 * SUM(eps.GrossProfit) / NULLIF(SUM(eps.TotalRevenue), 0), 2) AS CategoryMarginPct,
        COUNT(DISTINCT eps.UniqueResellers) AS CategoryUniqueResellers,
        ROUND(AVG(eps.TotalRevenue), 2) AS AvgRevenuePerProduct
    FROM EmployeeProductSales eps
    GROUP BY eps.EmployeeKey, eps.CategoryName, eps.CalendarYear
),

EmployeeTotalPerformance AS (
    SELECT
        ecp.EmployeeKey,
        ecp.CalendarYear,
        COUNT(DISTINCT ecp.CategoryName) AS TotalCategories,
        ROUND(SUM(ecp.CategoryRevenue), 2) AS TotalRevenue,
        ROUND(SUM(ecp.CategoryGrossProfit), 2) AS TotalGrossProfit,
        SUM(ecp.CategoryOrderCount) AS TotalOrders,
        SUM(ecp.UniqueProductsInCategory) AS TotalUniqueProducts
    FROM EmployeeCategoryPerformance ecp
    GROUP BY ecp.EmployeeKey, ecp.CalendarYear
),

CategoryRevenueShare AS (
    SELECT
        ecp.EmployeeKey,
        ecp.CalendarYear,
        ecp.CategoryName,
        ecp.CategoryRevenue,
        ecp.CategoryGrossProfit,
        ecp.CategoryMarginPct,
        ecp.CategoryOrderCount,
        ecp.UniqueProductsInCategory,
        ecp.UniqueSubcategoriesInCategory,
        etp.TotalRevenue AS EmployeeTotalRevenue,
        etp.TotalCategories,
        etp.TotalUniqueProducts,
        ROUND(100.0 * ecp.CategoryRevenue / NULLIF(etp.TotalRevenue, 0), 2) AS CategoryRevenuePct,
        RANK() OVER (
            PARTITION BY ecp.EmployeeKey, ecp.CalendarYear
            ORDER BY ecp.CategoryRevenue DESC
        ) AS CategoryRevenueRank
    FROM EmployeeCategoryPerformance ecp
    INNER JOIN EmployeeTotalPerformance etp
        ON ecp.EmployeeKey = etp.EmployeeKey
        AND ecp.CalendarYear = etp.CalendarYear
),

SpecializationMetrics AS (
    SELECT
        crs.EmployeeKey,
        crs.CalendarYear,
        e.FirstName || ' ' || e.LastName AS EmployeeName,
        e.Title AS JobTitle,
        st.SalesTerritoryRegion,
        st.SalesTerritoryCountry,
        crs.EmployeeTotalRevenue,
        crs.TotalCategories,
        crs.TotalUniqueProducts,
        -- Top category analysis
        MAX(CASE WHEN crs.CategoryRevenueRank = 1 THEN crs.CategoryName END) AS TopCategory,
        MAX(CASE WHEN crs.CategoryRevenueRank = 1 THEN crs.CategoryRevenue END) AS TopCategoryRevenue,
        MAX(CASE WHEN crs.CategoryRevenueRank = 1 THEN crs.CategoryRevenuePct END) AS TopCategoryRevenuePct,
        MAX(CASE WHEN crs.CategoryRevenueRank = 2 THEN crs.CategoryName END) AS SecondCategory,
        MAX(CASE WHEN crs.CategoryRevenueRank = 2 THEN crs.CategoryRevenuePct END) AS SecondCategoryRevenuePct,
        -- Specialization Index (Herfindahl-Hirschman Index for product categories)
        ROUND(SUM(crs.CategoryRevenuePct * crs.CategoryRevenuePct), 2) AS SpecializationIndexHHI,
        -- Portfolio breadth metrics
        ROUND(AVG(crs.CategoryRevenue), 2) AS AvgCategoryRevenue,
        ROUND(SUM(crs.CategoryRevenue) / crs.TotalCategories, 2) AS RevenuePerCategory,
        ROUND(SUM(crs.UniqueProductsInCategory) / crs.TotalCategories, 2) AS AvgProductsPerCategory
    FROM CategoryRevenueShare crs
    INNER JOIN DimEmployee e ON crs.EmployeeKey = e.EmployeeKey
    LEFT JOIN DimSalesTerritory st ON e.SalesTerritoryKey = st.SalesTerritoryKey
    GROUP BY crs.EmployeeKey, crs.CalendarYear, e.FirstName, e.LastName, e.Title,
             st.SalesTerritoryRegion, st.SalesTerritoryCountry, crs.EmployeeTotalRevenue,
             crs.TotalCategories, crs.TotalUniqueProducts
),

SpecializationClassification AS (
    SELECT
        sm.*,
        CASE
            WHEN sm.SpecializationIndexHHI > 6000 THEN 'Highly Specialized'
            WHEN sm.SpecializationIndexHHI > 4000 THEN 'Category Specialist'
            WHEN sm.SpecializationIndexHHI > 2500 THEN 'Focused Generalist'
            ELSE 'Broad Generalist'
        END AS SpecializationType,
        CASE
            WHEN sm.TopCategoryRevenuePct > 70 THEN 'Single Category Expert'
            WHEN sm.TopCategoryRevenuePct > 50 AND sm.SecondCategoryRevenuePct > 20 THEN 'Dual Category Focus'
            WHEN sm.TotalCategories >= 3 AND sm.TopCategoryRevenuePct < 50 THEN 'Multi-Category Balanced'
            ELSE 'Diversified Portfolio'
        END AS PortfolioStrategy,
        CASE
            WHEN sm.TotalUniqueProducts > 100 THEN 'Extensive Breadth'
            WHEN sm.TotalUniqueProducts > 50 THEN 'Broad Coverage'
            WHEN sm.TotalUniqueProducts > 20 THEN 'Moderate Coverage'
            ELSE 'Limited Product Range'
        END AS ProductBreadth,
        RANK() OVER (PARTITION BY sm.CalendarYear ORDER BY sm.EmployeeTotalRevenue DESC) AS RevenueRank,
        RANK() OVER (PARTITION BY sm.CalendarYear ORDER BY sm.SpecializationIndexHHI DESC) AS SpecializationRank,
        RANK() OVER (PARTITION BY sm.CalendarYear ORDER BY sm.TotalUniqueProducts DESC) AS DiversificationRank
    FROM SpecializationMetrics sm
),

CategoryExpertiseDetail AS (
    -- Detailed breakdown by category for each employee
    SELECT
        crs.EmployeeKey,
        crs.EmployeeName,
        crs.CalendarYear,
        crs.CategoryName,
        crs.CategoryRevenue,
        crs.CategoryGrossProfit,
        crs.CategoryMarginPct,
        crs.CategoryRevenuePct,
        crs.UniqueProductsInCategory,
        crs.UniqueSubcategoriesInCategory,
        crs.CategoryOrderCount,
        crs.CategoryRevenueRank,
        -- Compare to other employees selling same category
        RANK() OVER (
            PARTITION BY crs.CategoryName, crs.CalendarYear
            ORDER BY crs.CategoryRevenue DESC
        ) AS CategoryLeaderboardRank,
        NTILE(4) OVER (
            PARTITION BY crs.CategoryName, crs.CalendarYear
            ORDER BY crs.CategoryRevenue DESC
        ) AS CategoryPerformanceQuartile
    FROM CategoryRevenueShare crs
    INNER JOIN DimEmployee e ON crs.EmployeeKey = e.EmployeeKey
)

SELECT
    sc.EmployeeKey,
    sc.EmployeeName,
    sc.JobTitle,
    sc.CalendarYear,
    sc.SalesTerritoryRegion,
    sc.SalesTerritoryCountry,
    sc.EmployeeTotalRevenue,
    sc.TotalCategories,
    sc.TotalUniqueProducts,
    sc.TopCategory,
    sc.TopCategoryRevenue,
    sc.TopCategoryRevenuePct,
    sc.SecondCategory,
    sc.SecondCategoryRevenuePct,
    sc.SpecializationIndexHHI,
    sc.SpecializationType,
    sc.PortfolioStrategy,
    sc.ProductBreadth,
    sc.AvgCategoryRevenue,
    sc.RevenuePerCategory,
    sc.AvgProductsPerCategory,
    sc.RevenueRank,
    sc.SpecializationRank,
    sc.DiversificationRank
FROM SpecializationClassification sc
ORDER BY sc.CalendarYear DESC, sc.EmployeeTotalRevenue DESC;
```

---

# Summary

These five business intelligence questions provide comprehensive insights into employee performance, sales force effectiveness, and talent management across the AdventureWorks sales organization:

1. **Quota Attainment and Performance Ranking** - Tracks individual performance against targets with year-over-year trends and performance trajectory analysis
2. **Territory Performance and Geographic Distribution** - Analyzes employee effectiveness across territories with concentration and cross-selling metrics
3. **Employee Hierarchy and Team Effectiveness** - Evaluates organizational dynamics through recursive hierarchy analysis and management effectiveness scoring
4. **Tenure, Experience, and Performance Correlation** - Examines career progression patterns with cohort benchmarking and retention risk assessment
5. **Product Specialization and Portfolio Diversification** - Identifies employee expertise patterns and category specialization for optimal assignment strategies

These analyses leverage advanced SQL techniques including recursive CTEs, window functions, statistical aggregations, and multi-dimensional performance scoring to transform employee and sales data into actionable insights for sales leadership, human resources, and strategic workforce planning.
