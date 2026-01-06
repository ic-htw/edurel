# Financial Analysis - Business Questions

## Introduction

Financial analysis is the cornerstone of strategic planning, performance management, and operational control. Through comprehensive analysis of budget versus actual performance, scenario planning, and organizational cost structures, finance teams can identify variances, optimize resource allocation, and guide executive decision-making.

This document presents a comprehensive financial analysis framework using the AdventureWorks data warehouse. The analysis leverages the FactFinance fact table, which captures financial transactions across multiple dimensions:

**Key Dimensions:**
- **DimAccount**: Chart of accounts with hierarchical structure (ParentAccountKey → AccountKey) defining account types and classifications
- **DimOrganization**: Organizational hierarchy (ParentOrganizationKey → OrganizationKey) representing business units and subsidiaries
- **DimDepartmentGroup**: Department structure (ParentDepartmentGroupKey → DepartmentGroupKey) for cost center analysis
- **DimScenario**: Financial scenarios (Actual, Budget, Forecast) for variance and planning analysis
- **DimDate**: Time dimension supporting both calendar and fiscal period analysis
- **DimCurrency**: Multi-currency support for international operations

**Key Metrics:**
- **Amount**: Financial transaction amounts (positive for revenue/assets, negative for expenses/liabilities)

The following business questions explore critical financial analysis areas including:
- Budget variance and performance monitoring
- Scenario comparison and planning accuracy
- Account hierarchy and chart of accounts analysis
- Organizational and departmental cost management
- Temporal trends and period-over-period comparisons
- Fiscal vs calendar year reconciliation

These analyses provide actionable insights for CFOs, finance managers, and business unit leaders to drive financial performance and strategic alignment.

---

# Business Question 1: Budget vs Actual Variance Analysis with Performance Scoring

## Intent

Perform comprehensive budget variance analysis comparing actual financial results against budgeted amounts across organizations, departments, and account types. This analysis provides:
- Absolute and percentage variance from budget by account
- Identification of favorable vs. unfavorable variances
- Organizational and departmental performance against plan
- Account-level variance analysis with revenue/expense classification
- Variance trend tracking over time periods
- Performance scoring and ranking of business units
- Drill-down capability from summary to detailed account level

Understanding budget variances enables proactive financial management, identifies areas requiring corrective action, supports accurate forecasting, and facilitates performance-based accountability. This analysis helps distinguish between operational issues (unfavorable expense variances) and opportunities (favorable revenue variances).

## SQL Code

```sql
WITH ActualAmounts AS (
    SELECT
        ff.AccountKey,
        ff.OrganizationKey,
        ff.DepartmentGroupKey,
        dd.CalendarYear,
        dd.FiscalYear,
        dd.CalendarQuarter,
        dd.FiscalQuarter,
        SUM(ff.Amount) AS ActualAmount
    FROM FactFinance ff
    INNER JOIN DimDate dd ON ff.DateKey = dd.DateKey
    INNER JOIN DimScenario ds ON ff.ScenarioKey = ds.ScenarioKey
    WHERE ds.ScenarioName = 'Actual'
    GROUP BY
        ff.AccountKey, ff.OrganizationKey, ff.DepartmentGroupKey,
        dd.CalendarYear, dd.FiscalYear, dd.CalendarQuarter, dd.FiscalQuarter
),
BudgetAmounts AS (
    SELECT
        ff.AccountKey,
        ff.OrganizationKey,
        ff.DepartmentGroupKey,
        dd.CalendarYear,
        dd.FiscalYear,
        dd.CalendarQuarter,
        dd.FiscalQuarter,
        SUM(ff.Amount) AS BudgetAmount
    FROM FactFinance ff
    INNER JOIN DimDate dd ON ff.DateKey = dd.DateKey
    INNER JOIN DimScenario ds ON ff.ScenarioKey = ds.ScenarioKey
    WHERE ds.ScenarioName = 'Budget'
    GROUP BY
        ff.AccountKey, ff.OrganizationKey, ff.DepartmentGroupKey,
        dd.CalendarYear, dd.FiscalYear, dd.CalendarQuarter, dd.FiscalQuarter
),
VarianceAnalysis AS (
    SELECT
        COALESCE(aa.AccountKey, ba.AccountKey) AS AccountKey,
        COALESCE(aa.OrganizationKey, ba.OrganizationKey) AS OrganizationKey,
        COALESCE(aa.DepartmentGroupKey, ba.DepartmentGroupKey) AS DepartmentGroupKey,
        COALESCE(aa.CalendarYear, ba.CalendarYear) AS CalendarYear,
        COALESCE(aa.FiscalYear, ba.FiscalYear) AS FiscalYear,
        COALESCE(aa.CalendarQuarter, ba.CalendarQuarter) AS CalendarQuarter,
        COALESCE(aa.FiscalQuarter, ba.FiscalQuarter) AS FiscalQuarter,
        COALESCE(aa.ActualAmount, 0) AS ActualAmount,
        COALESCE(ba.BudgetAmount, 0) AS BudgetAmount,
        COALESCE(aa.ActualAmount, 0) - COALESCE(ba.BudgetAmount, 0) AS Variance,
        CASE
            WHEN COALESCE(ba.BudgetAmount, 0) != 0
            THEN ((COALESCE(aa.ActualAmount, 0) - COALESCE(ba.BudgetAmount, 0)) /
                  ABS(COALESCE(ba.BudgetAmount, 0))) * 100
            ELSE NULL
        END AS VariancePct
    FROM ActualAmounts aa
    FULL OUTER JOIN BudgetAmounts ba
        ON aa.AccountKey = ba.AccountKey
        AND aa.OrganizationKey = ba.OrganizationKey
        AND aa.DepartmentGroupKey = ba.DepartmentGroupKey
        AND aa.CalendarYear = ba.CalendarYear
        AND aa.FiscalYear = ba.FiscalYear
        AND aa.CalendarQuarter = ba.CalendarQuarter
        AND aa.FiscalQuarter = ba.FiscalQuarter
),
EnrichedVariance AS (
    SELECT
        va.*,
        da.AccountDescription,
        da.AccountType,
        CASE
            WHEN da.ParentAccountKey IS NOT NULL THEN 'Detail Account'
            ELSE 'Summary Account'
        END AS AccountLevel,
        dorg.OrganizationName,
        dorg.PercentageOfOwnership,
        ddg.DepartmentGroupName,
        ROUND(va.ActualAmount, 2) AS ActualAmountRounded,
        ROUND(va.BudgetAmount, 2) AS BudgetAmountRounded,
        ROUND(va.Variance, 2) AS VarianceRounded,
        ROUND(va.VariancePct, 2) AS VariancePctRounded,
        CASE
            WHEN da.AccountType IN ('Revenue', 'Income', 'Asset') THEN
                CASE
                    WHEN va.Variance > 0 THEN 'Favorable'
                    WHEN va.Variance < 0 THEN 'Unfavorable'
                    ELSE 'On Target'
                END
            WHEN da.AccountType IN ('Expense', 'Cost', 'Liability') THEN
                CASE
                    WHEN va.Variance < 0 THEN 'Favorable'
                    WHEN va.Variance > 0 THEN 'Unfavorable'
                    ELSE 'On Target'
                END
            ELSE 'Neutral'
        END AS VarianceDirection,
        CASE
            WHEN ABS(va.VariancePct) >= 20 THEN 'Critical'
            WHEN ABS(va.VariancePct) >= 10 THEN 'High'
            WHEN ABS(va.VariancePct) >= 5 THEN 'Medium'
            ELSE 'Low'
        END AS VarianceSeverity
    FROM VarianceAnalysis va
    INNER JOIN DimAccount da ON va.AccountKey = da.AccountKey
    INNER JOIN DimOrganization dorg ON va.OrganizationKey = dorg.OrganizationKey
    INNER JOIN DimDepartmentGroup ddg ON va.DepartmentGroupKey = ddg.DepartmentGroupKey
),
OrganizationalSummary AS (
    SELECT
        OrganizationName,
        DepartmentGroupName,
        CalendarYear,
        FiscalYear,
        CalendarQuarter,
        AccountType,
        COUNT(DISTINCT AccountKey) AS AccountCount,
        ROUND(SUM(ActualAmount), 2) AS TotalActual,
        ROUND(SUM(BudgetAmount), 2) AS TotalBudget,
        ROUND(SUM(Variance), 2) AS TotalVariance,
        ROUND((SUM(Variance) / NULLIF(SUM(ABS(BudgetAmount)), 0)) * 100, 2) AS OverallVariancePct,
        SUM(CASE WHEN VarianceDirection = 'Favorable' THEN 1 ELSE 0 END) AS FavorableCount,
        SUM(CASE WHEN VarianceDirection = 'Unfavorable' THEN 1 ELSE 0 END) AS UnfavorableCount,
        SUM(CASE WHEN VarianceSeverity = 'Critical' THEN 1 ELSE 0 END) AS CriticalVarianceCount,
        ROUND(AVG(ABS(VariancePct)), 2) AS AvgAbsVariancePct
    FROM EnrichedVariance
    GROUP BY
        OrganizationName, DepartmentGroupName, CalendarYear,
        FiscalYear, CalendarQuarter, AccountType
),
PerformanceScoring AS (
    SELECT
        *,
        CASE
            WHEN AvgAbsVariancePct <= 5 THEN 100
            WHEN AvgAbsVariancePct <= 10 THEN 90
            WHEN AvgAbsVariancePct <= 15 THEN 75
            WHEN AvgAbsVariancePct <= 20 THEN 60
            ELSE 50
        END AS PerformanceScore,
        RANK() OVER (
            PARTITION BY CalendarYear, CalendarQuarter
            ORDER BY AvgAbsVariancePct ASC
        ) AS PerformanceRank
    FROM OrganizationalSummary
)
SELECT
    'Detail Variance Analysis' AS ReportSection,
    ev.CalendarYear,
    ev.FiscalYear,
    ev.CalendarQuarter,
    ev.FiscalQuarter,
    ev.OrganizationName,
    ev.DepartmentGroupName,
    ev.AccountDescription,
    ev.AccountType,
    ev.AccountLevel,
    ev.ActualAmountRounded AS ActualAmount,
    ev.BudgetAmountRounded AS BudgetAmount,
    ev.VarianceRounded AS Variance,
    ev.VariancePctRounded AS VariancePct,
    ev.VarianceDirection,
    ev.VarianceSeverity,
    NULL AS AccountCount,
    NULL AS FavorableCount,
    NULL AS UnfavorableCount,
    NULL AS CriticalVarianceCount,
    NULL AS PerformanceScore,
    NULL AS PerformanceRank
FROM EnrichedVariance ev
WHERE ev.CalendarYear = (SELECT MAX(CalendarYear) FROM EnrichedVariance)
    AND ev.AccountLevel = 'Detail Account'
    AND ABS(ev.Variance) > 1000  -- Focus on material variances

UNION ALL

SELECT
    'Organizational Summary' AS ReportSection,
    ps.CalendarYear,
    ps.FiscalYear,
    ps.CalendarQuarter,
    NULL AS FiscalQuarter,
    ps.OrganizationName,
    ps.DepartmentGroupName,
    NULL AS AccountDescription,
    ps.AccountType,
    NULL AS AccountLevel,
    ps.TotalActual AS ActualAmount,
    ps.TotalBudget AS BudgetAmount,
    ps.TotalVariance AS Variance,
    ps.OverallVariancePct AS VariancePct,
    NULL AS VarianceDirection,
    NULL AS VarianceSeverity,
    ps.AccountCount,
    ps.FavorableCount,
    ps.UnfavorableCount,
    ps.CriticalVarianceCount,
    ps.PerformanceScore,
    ps.PerformanceRank
FROM PerformanceScoring ps
WHERE ps.CalendarYear = (SELECT MAX(CalendarYear) FROM PerformanceScoring)

ORDER BY ReportSection, PerformanceRank NULLS LAST, ABS(Variance) DESC NULLS LAST;
```

---

# Business Question 2: Multi-Scenario Comparison and Forecast Accuracy Analysis

## Intent

Compare multiple financial scenarios (Actual, Budget, Forecast) to evaluate planning accuracy and identify patterns in forecasting performance. This comprehensive scenario analysis provides:
- Side-by-side comparison of Actual vs Budget vs Forecast amounts
- Budget accuracy metrics (actual vs budget variance)
- Forecast accuracy metrics (actual vs forecast variance)
- Identification of systematic over/under-budgeting or forecasting patterns
- Scenario convergence analysis showing how forecasts evolve
- Department and organization-level planning performance
- Account-specific forecasting challenges

Understanding scenario variances enables improved budgeting and forecasting processes, identifies biases in planning assumptions, supports more accurate future projections, and builds credibility in financial planning through continuous improvement.

## SQL Code

```sql
WITH ScenarioAmounts AS (
    SELECT
        ff.AccountKey,
        ff.OrganizationKey,
        ff.DepartmentGroupKey,
        dd.CalendarYear,
        dd.FiscalYear,
        dd.CalendarQuarter,
        ds.ScenarioName,
        SUM(ff.Amount) AS ScenarioAmount
    FROM FactFinance ff
    INNER JOIN DimDate dd ON ff.DateKey = dd.DateKey
    INNER JOIN DimScenario ds ON ff.ScenarioKey = ds.ScenarioKey
    GROUP BY
        ff.AccountKey, ff.OrganizationKey, ff.DepartmentGroupKey,
        dd.CalendarYear, dd.FiscalYear, dd.CalendarQuarter, ds.ScenarioName
),
PivotedScenarios AS (
    SELECT
        AccountKey,
        OrganizationKey,
        DepartmentGroupKey,
        CalendarYear,
        FiscalYear,
        CalendarQuarter,
        SUM(CASE WHEN ScenarioName = 'Actual' THEN ScenarioAmount ELSE 0 END) AS ActualAmount,
        SUM(CASE WHEN ScenarioName = 'Budget' THEN ScenarioAmount ELSE 0 END) AS BudgetAmount,
        SUM(CASE WHEN ScenarioName = 'Forecast' THEN ScenarioAmount ELSE 0 END) AS ForecastAmount
    FROM ScenarioAmounts
    GROUP BY
        AccountKey, OrganizationKey, DepartmentGroupKey,
        CalendarYear, FiscalYear, CalendarQuarter
),
ScenarioComparison AS (
    SELECT
        ps.*,
        da.AccountDescription,
        da.AccountType,
        dorg.OrganizationName,
        ddg.DepartmentGroupName,
        -- Budget variance
        ps.ActualAmount - ps.BudgetAmount AS BudgetVariance,
        CASE
            WHEN ps.BudgetAmount != 0
            THEN ((ps.ActualAmount - ps.BudgetAmount) / ABS(ps.BudgetAmount)) * 100
            ELSE NULL
        END AS BudgetVariancePct,
        -- Forecast variance
        ps.ActualAmount - ps.ForecastAmount AS ForecastVariance,
        CASE
            WHEN ps.ForecastAmount != 0
            THEN ((ps.ActualAmount - ps.ForecastAmount) / ABS(ps.ForecastAmount)) * 100
            ELSE NULL
        END AS ForecastVariancePct,
        -- Forecast vs Budget variance (how much forecast differs from budget)
        ps.ForecastAmount - ps.BudgetAmount AS ForecastBudgetDelta,
        CASE
            WHEN ps.BudgetAmount != 0
            THEN ((ps.ForecastAmount - ps.BudgetAmount) / ABS(ps.BudgetAmount)) * 100
            ELSE NULL
        END AS ForecastBudgetDeltaPct
    FROM PivotedScenarios ps
    INNER JOIN DimAccount da ON ps.AccountKey = da.AccountKey
    INNER JOIN DimOrganization dorg ON ps.OrganizationKey = dorg.OrganizationKey
    INNER JOIN DimDepartmentGroup ddg ON ps.DepartmentGroupKey = ddg.DepartmentGroupKey
),
ScenarioMetrics AS (
    SELECT
        *,
        ROUND(ActualAmount, 2) AS ActualAmountRounded,
        ROUND(BudgetAmount, 2) AS BudgetAmountRounded,
        ROUND(ForecastAmount, 2) AS ForecastAmountRounded,
        ROUND(BudgetVariance, 2) AS BudgetVarianceRounded,
        ROUND(BudgetVariancePct, 2) AS BudgetVariancePctRounded,
        ROUND(ForecastVariance, 2) AS ForecastVarianceRounded,
        ROUND(ForecastVariancePct, 2) AS ForecastVariancePctRounded,
        ROUND(ForecastBudgetDelta, 2) AS ForecastBudgetDeltaRounded,
        ROUND(ForecastBudgetDeltaPct, 2) AS ForecastBudgetDeltaPctRounded,
        CASE
            WHEN ABS(BudgetVariancePct) < ABS(ForecastVariancePct) THEN 'Budget More Accurate'
            WHEN ABS(ForecastVariancePct) < ABS(BudgetVariancePct) THEN 'Forecast More Accurate'
            ELSE 'Equal Accuracy'
        END AS AccuracyComparison,
        CASE
            WHEN BudgetVariance > 0 AND ForecastVariance > 0 THEN 'Both Under-Estimated'
            WHEN BudgetVariance < 0 AND ForecastVariance < 0 THEN 'Both Over-Estimated'
            WHEN BudgetVariance > 0 AND ForecastVariance < 0 THEN 'Budget Under, Forecast Over'
            WHEN BudgetVariance < 0 AND ForecastVariance > 0 THEN 'Budget Over, Forecast Under'
            ELSE 'Accurate'
        END AS BiasPattern
    FROM ScenarioComparison
),
OrganizationalAccuracy AS (
    SELECT
        OrganizationName,
        DepartmentGroupName,
        AccountType,
        CalendarYear,
        CalendarQuarter,
        COUNT(DISTINCT AccountKey) AS AccountCount,
        ROUND(SUM(ActualAmount), 2) AS TotalActual,
        ROUND(SUM(BudgetAmount), 2) AS TotalBudget,
        ROUND(SUM(ForecastAmount), 2) AS TotalForecast,
        ROUND(SUM(BudgetVariance), 2) AS TotalBudgetVariance,
        ROUND(SUM(ForecastVariance), 2) AS TotalForecastVariance,
        ROUND(AVG(ABS(BudgetVariancePct)), 2) AS AvgAbsBudgetVariancePct,
        ROUND(AVG(ABS(ForecastVariancePct)), 2) AS AvgAbsForecastVariancePct,
        ROUND((SUM(ABS(ForecastVariance)) / NULLIF(SUM(ABS(BudgetVariance)), 0)) * 100, 2) AS ForecastVsBudgetAccuracyRatio,
        SUM(CASE WHEN BiasPattern LIKE '%Under-Estimated%' THEN 1 ELSE 0 END) AS UnderEstimateCount,
        SUM(CASE WHEN BiasPattern LIKE '%Over-Estimated%' THEN 1 ELSE 0 END) AS OverEstimateCount,
        CASE
            WHEN AVG(BudgetVariancePct) > 5 THEN 'Systematic Under-Budgeting'
            WHEN AVG(BudgetVariancePct) < -5 THEN 'Systematic Over-Budgeting'
            ELSE 'Balanced Budgeting'
        END AS BudgetingBias,
        CASE
            WHEN AVG(ForecastVariancePct) > 5 THEN 'Systematic Under-Forecasting'
            WHEN AVG(ForecastVariancePct) < -5 THEN 'Systematic Over-Forecasting'
            ELSE 'Balanced Forecasting'
        END AS ForecastingBias
    FROM ScenarioMetrics
    GROUP BY
        OrganizationName, DepartmentGroupName, AccountType,
        CalendarYear, CalendarQuarter
),
AccuracyScoring AS (
    SELECT
        *,
        CASE
            WHEN AvgAbsBudgetVariancePct <= 5 THEN 'Excellent (<=5%)'
            WHEN AvgAbsBudgetVariancePct <= 10 THEN 'Good (5-10%)'
            WHEN AvgAbsBudgetVariancePct <= 15 THEN 'Fair (10-15%)'
            ELSE 'Poor (>15%)'
        END AS BudgetAccuracyGrade,
        CASE
            WHEN AvgAbsForecastVariancePct <= 5 THEN 'Excellent (<=5%)'
            WHEN AvgAbsForecastVariancePct <= 10 THEN 'Good (5-10%)'
            WHEN AvgAbsForecastVariancePct <= 15 THEN 'Fair (10-15%)'
            ELSE 'Poor (>15%)'
        END AS ForecastAccuracyGrade,
        RANK() OVER (
            PARTITION BY CalendarYear, CalendarQuarter
            ORDER BY AvgAbsBudgetVariancePct ASC
        ) AS BudgetAccuracyRank,
        RANK() OVER (
            PARTITION BY CalendarYear, CalendarQuarter
            ORDER BY AvgAbsForecastVariancePct ASC
        ) AS ForecastAccuracyRank
    FROM OrganizationalAccuracy
)
SELECT
    'Scenario Detail Comparison' AS ReportSection,
    sm.CalendarYear,
    sm.FiscalYear,
    sm.CalendarQuarter,
    sm.OrganizationName,
    sm.DepartmentGroupName,
    sm.AccountDescription,
    sm.AccountType,
    sm.ActualAmountRounded AS ActualAmount,
    sm.BudgetAmountRounded AS BudgetAmount,
    sm.ForecastAmountRounded AS ForecastAmount,
    sm.BudgetVarianceRounded AS BudgetVariance,
    sm.BudgetVariancePctRounded AS BudgetVariancePct,
    sm.ForecastVarianceRounded AS ForecastVariance,
    sm.ForecastVariancePctRounded AS ForecastVariancePct,
    sm.ForecastBudgetDeltaRounded AS ForecastBudgetDelta,
    sm.AccuracyComparison,
    sm.BiasPattern,
    NULL AS BudgetAccuracyGrade,
    NULL AS ForecastAccuracyGrade,
    NULL AS BudgetingBias,
    NULL AS ForecastingBias,
    NULL AS BudgetAccuracyRank,
    NULL AS ForecastAccuracyRank
FROM ScenarioMetrics sm
WHERE sm.CalendarYear = (SELECT MAX(CalendarYear) FROM ScenarioMetrics)
    AND (ABS(sm.BudgetVariance) > 1000 OR ABS(sm.ForecastVariance) > 1000)

UNION ALL

SELECT
    'Organizational Accuracy Analysis' AS ReportSection,
    asc.CalendarYear,
    NULL AS FiscalYear,
    asc.CalendarQuarter,
    asc.OrganizationName,
    asc.DepartmentGroupName,
    NULL AS AccountDescription,
    asc.AccountType,
    asc.TotalActual AS ActualAmount,
    asc.TotalBudget AS BudgetAmount,
    asc.TotalForecast AS ForecastAmount,
    asc.TotalBudgetVariance AS BudgetVariance,
    asc.AvgAbsBudgetVariancePct AS BudgetVariancePct,
    asc.TotalForecastVariance AS ForecastVariance,
    asc.AvgAbsForecastVariancePct AS ForecastVariancePct,
    NULL AS ForecastBudgetDelta,
    NULL AS AccuracyComparison,
    NULL AS BiasPattern,
    asc.BudgetAccuracyGrade,
    asc.ForecastAccuracyGrade,
    asc.BudgetingBias,
    asc.ForecastingBias,
    asc.BudgetAccuracyRank,
    asc.ForecastAccuracyRank
FROM AccuracyScoring asc
WHERE asc.CalendarYear = (SELECT MAX(CalendarYear) FROM AccuracyScoring)

ORDER BY ReportSection, BudgetAccuracyRank NULLS LAST, ABS(BudgetVariance) DESC NULLS LAST;
```

---

# Business Question 3: Account Hierarchy Navigation and Chart of Accounts Analysis

## Intent

Analyze the hierarchical structure of the chart of accounts to understand account relationships, roll-up totals, and account classification patterns. This hierarchical financial analysis provides:
- Parent-child account relationships and dependencies
- Recursive aggregation from detail accounts to summary accounts
- Account hierarchy depth and breadth analysis
- Account usage patterns across organizations
- Leaf-level (detail) vs. rollup (summary) account identification
- Account balance validation and reconciliation
- Orphaned or unused account detection

Understanding the account hierarchy enables proper financial reporting structure, supports consolidation requirements, facilitates drill-down analysis from summary to detail, and ensures consistent account classification across the organization.

## SQL Code

```sql
WITH RECURSIVE AccountHierarchy AS (
    -- Base case: Root accounts (no parent)
    SELECT
        AccountKey,
        ParentAccountKey,
        AccountCodeAlternateKey,
        AccountDescription,
        AccountType,
        ValueType,
        1 AS HierarchyLevel,
        CAST(AccountDescription AS VARCHAR) AS HierarchyPath,
        CAST(AccountKey AS VARCHAR) AS KeyPath
    FROM DimAccount
    WHERE ParentAccountKey IS NULL

    UNION ALL

    -- Recursive case: Child accounts
    SELECT
        da.AccountKey,
        da.ParentAccountKey,
        da.AccountCodeAlternateKey,
        da.AccountDescription,
        da.AccountType,
        da.ValueType,
        ah.HierarchyLevel + 1,
        ah.HierarchyPath || ' > ' || da.AccountDescription,
        ah.KeyPath || '>' || CAST(da.AccountKey AS VARCHAR)
    FROM DimAccount da
    INNER JOIN AccountHierarchy ah ON da.ParentAccountKey = ah.AccountKey
),
AccountBalances AS (
    SELECT
        ff.AccountKey,
        ds.ScenarioName,
        dd.CalendarYear,
        dd.FiscalYear,
        SUM(ff.Amount) AS TotalAmount
    FROM FactFinance ff
    INNER JOIN DimDate dd ON ff.DateKey = dd.DateKey
    INNER JOIN DimScenario ds ON ff.ScenarioKey = ds.ScenarioKey
    WHERE ds.ScenarioName = 'Actual'
    GROUP BY ff.AccountKey, ds.ScenarioName, dd.CalendarYear, dd.FiscalYear
),
EnrichedAccountHierarchy AS (
    SELECT
        ah.*,
        COALESCE(ab.TotalAmount, 0) AS DirectAmount,
        ab.CalendarYear,
        ab.FiscalYear,
        CASE
            WHEN EXISTS (
                SELECT 1 FROM DimAccount da
                WHERE da.ParentAccountKey = ah.AccountKey
            ) THEN 'Parent Account'
            ELSE 'Leaf Account'
        END AS AccountCategory,
        (SELECT COUNT(*) FROM DimAccount da WHERE da.ParentAccountKey = ah.AccountKey) AS ChildCount
    FROM AccountHierarchy ah
    LEFT JOIN AccountBalances ab ON ah.AccountKey = ab.AccountKey
),
HierarchicalRollup AS (
    SELECT
        ah.AccountKey,
        ah.ParentAccountKey,
        ah.AccountDescription,
        ah.AccountType,
        ah.HierarchyLevel,
        ah.HierarchyPath,
        ah.AccountCategory,
        ah.ChildCount,
        ah.DirectAmount,
        ah.CalendarYear,
        -- Recursive sum: current amount + all descendant amounts
        ah.DirectAmount + COALESCE(
            (SELECT SUM(child.DirectAmount)
             FROM EnrichedAccountHierarchy child
             WHERE child.KeyPath LIKE ah.KeyPath || '>%'
               AND child.CalendarYear = ah.CalendarYear),
            0
        ) AS RollupAmount
    FROM EnrichedAccountHierarchy ah
),
AccountUsage AS (
    SELECT
        da.AccountKey,
        da.AccountDescription,
        COUNT(DISTINCT ff.OrganizationKey) AS OrganizationsUsing,
        COUNT(DISTINCT ff.DepartmentGroupKey) AS DepartmentsUsing,
        COUNT(DISTINCT ds.ScenarioName) AS ScenariosUsing,
        COUNT(*) AS TransactionCount,
        MIN(dd.FullDateAlternateKey) AS FirstUsageDate,
        MAX(dd.FullDateAlternateKey) AS LastUsageDate
    FROM DimAccount da
    LEFT JOIN FactFinance ff ON da.AccountKey = ff.AccountKey
    LEFT JOIN DimDate dd ON ff.DateKey = dd.DateKey
    LEFT JOIN DimScenario ds ON ff.ScenarioKey = ds.ScenarioKey
    GROUP BY da.AccountKey, da.AccountDescription
),
AccountAnalytics AS (
    SELECT
        hr.*,
        au.OrganizationsUsing,
        au.DepartmentsUsing,
        au.ScenariosUsing,
        au.TransactionCount,
        au.FirstUsageDate,
        au.LastUsageDate,
        ROUND(hr.DirectAmount, 2) AS DirectAmountRounded,
        ROUND(hr.RollupAmount, 2) AS RollupAmountRounded,
        CASE
            WHEN hr.AccountCategory = 'Parent Account' AND hr.DirectAmount != 0
            THEN 'Warning: Parent with Direct Postings'
            WHEN hr.AccountCategory = 'Leaf Account' AND hr.ChildCount > 0
            THEN 'Error: Leaf with Children'
            WHEN au.TransactionCount = 0
            THEN 'Unused Account'
            ELSE 'Normal'
        END AS AccountStatus,
        CASE
            WHEN hr.AccountCategory = 'Parent Account'
            THEN ROUND(ABS(hr.RollupAmount - hr.DirectAmount), 2)
            ELSE 0
        END AS ChildContribution
    FROM HierarchicalRollup hr
    LEFT JOIN AccountUsage au ON hr.AccountKey = au.AccountKey
),
HierarchySummary AS (
    SELECT
        HierarchyLevel,
        AccountType,
        AccountCategory,
        CalendarYear,
        COUNT(DISTINCT AccountKey) AS AccountCount,
        ROUND(SUM(DirectAmount), 2) AS TotalDirectAmount,
        ROUND(SUM(RollupAmount), 2) AS TotalRollupAmount,
        ROUND(AVG(ChildCount), 2) AS AvgChildrenPerParent,
        SUM(CASE WHEN AccountStatus LIKE '%Warning%' OR AccountStatus LIKE '%Error%' THEN 1 ELSE 0 END) AS IssueCount
    FROM AccountAnalytics
    GROUP BY HierarchyLevel, AccountType, AccountCategory, CalendarYear
)
SELECT
    'Account Detail' AS ReportSection,
    aa.AccountKey,
    aa.AccountDescription,
    aa.AccountType,
    aa.HierarchyLevel,
    aa.AccountCategory,
    aa.HierarchyPath,
    aa.ChildCount,
    aa.CalendarYear,
    aa.DirectAmountRounded AS DirectAmount,
    aa.RollupAmountRounded AS RollupAmount,
    aa.ChildContribution,
    aa.OrganizationsUsing,
    aa.DepartmentsUsing,
    aa.TransactionCount,
    aa.AccountStatus,
    aa.FirstUsageDate,
    aa.LastUsageDate,
    NULL AS AccountCount,
    NULL AS TotalDirectAmount,
    NULL AS TotalRollupAmount,
    NULL AS AvgChildrenPerParent
FROM AccountAnalytics aa
WHERE aa.CalendarYear = (SELECT MAX(CalendarYear) FROM AccountAnalytics WHERE CalendarYear IS NOT NULL)

UNION ALL

SELECT
    'Hierarchy Summary' AS ReportSection,
    NULL AS AccountKey,
    NULL AS AccountDescription,
    hs.AccountType,
    hs.HierarchyLevel,
    hs.AccountCategory,
    NULL AS HierarchyPath,
    NULL AS ChildCount,
    hs.CalendarYear,
    NULL AS DirectAmount,
    NULL AS RollupAmount,
    NULL AS ChildContribution,
    NULL AS OrganizationsUsing,
    NULL AS DepartmentsUsing,
    NULL AS TransactionCount,
    NULL AS AccountStatus,
    NULL AS FirstUsageDate,
    NULL AS LastUsageDate,
    hs.AccountCount,
    hs.TotalDirectAmount,
    hs.TotalRollupAmount,
    hs.AvgChildrenPerParent
FROM HierarchySummary hs
WHERE hs.CalendarYear = (SELECT MAX(CalendarYear) FROM HierarchySummary WHERE CalendarYear IS NOT NULL)

ORDER BY ReportSection, HierarchyLevel NULLS LAST, RollupAmount DESC NULLS LAST;
```

---

# Business Question 4: Organizational and Departmental Performance Analysis

## Intent

Analyze financial performance across the organizational hierarchy and department structure to identify high-performing and underperforming business units. This comprehensive organizational analysis provides:
- Revenue, expense, and profit by organizational unit
- Parent-child organizational relationships and consolidations
- Department-level cost center performance
- Cross-organizational comparisons and benchmarking
- Cost allocation patterns across departments
- Organizational efficiency metrics
- Subsidiary and division contribution analysis

Understanding organizational performance enables targeted management interventions, supports resource reallocation decisions, facilitates performance-based incentives, and identifies structural inefficiencies requiring reorganization or process improvement.

## SQL Code

```sql
WITH OrganizationalFinance AS (
    SELECT
        ff.OrganizationKey,
        ff.DepartmentGroupKey,
        ff.AccountKey,
        ds.ScenarioName,
        da.AccountType,
        dd.CalendarYear,
        dd.FiscalYear,
        dd.CalendarQuarter,
        SUM(ff.Amount) AS Amount
    FROM FactFinance ff
    INNER JOIN DimDate dd ON ff.DateKey = dd.DateKey
    INNER JOIN DimScenario ds ON ff.ScenarioKey = ds.ScenarioKey
    INNER JOIN DimAccount da ON ff.AccountKey = da.AccountKey
    WHERE ds.ScenarioName = 'Actual'
    GROUP BY
        ff.OrganizationKey, ff.DepartmentGroupKey, ff.AccountKey,
        ds.ScenarioName, da.AccountType, dd.CalendarYear,
        dd.FiscalYear, dd.CalendarQuarter
),
OrganizationSummary AS (
    SELECT
        dorg.OrganizationKey,
        dorg.ParentOrganizationKey,
        dorg.OrganizationName,
        dorg.PercentageOfOwnership,
        parent.OrganizationName AS ParentOrganizationName,
        ofin.CalendarYear,
        ofin.CalendarQuarter,
        SUM(CASE WHEN ofin.AccountType IN ('Revenue', 'Income') THEN ofin.Amount ELSE 0 END) AS Revenue,
        SUM(CASE WHEN ofin.AccountType IN ('Expense', 'Cost') THEN ABS(ofin.Amount) ELSE 0 END) AS Expenses,
        SUM(CASE WHEN ofin.AccountType IN ('Revenue', 'Income') THEN ofin.Amount ELSE 0 END) -
        SUM(CASE WHEN ofin.AccountType IN ('Expense', 'Cost') THEN ABS(ofin.Amount) ELSE 0 END) AS NetIncome,
        SUM(CASE WHEN ofin.AccountType = 'Asset' THEN ofin.Amount ELSE 0 END) AS Assets,
        SUM(CASE WHEN ofin.AccountType = 'Liability' THEN ABS(ofin.Amount) ELSE 0 END) AS Liabilities,
        COUNT(DISTINCT ofin.DepartmentGroupKey) AS DepartmentCount,
        COUNT(DISTINCT ofin.AccountKey) AS AccountCount
    FROM OrganizationalFinance ofin
    INNER JOIN DimOrganization dorg ON ofin.OrganizationKey = dorg.OrganizationKey
    LEFT JOIN DimOrganization parent ON dorg.ParentOrganizationKey = parent.OrganizationKey
    GROUP BY
        dorg.OrganizationKey, dorg.ParentOrganizationKey, dorg.OrganizationName,
        dorg.PercentageOfOwnership, parent.OrganizationName,
        ofin.CalendarYear, ofin.CalendarQuarter
),
OrganizationMetrics AS (
    SELECT
        *,
        ROUND(Revenue, 2) AS RevenueRounded,
        ROUND(Expenses, 2) AS ExpensesRounded,
        ROUND(NetIncome, 2) AS NetIncomeRounded,
        ROUND(Assets, 2) AS AssetsRounded,
        ROUND(Liabilities, 2) AS LiabilitiesRounded,
        CASE
            WHEN Revenue > 0
            THEN ROUND((NetIncome / Revenue) * 100, 2)
            ELSE NULL
        END AS ProfitMarginPct,
        CASE
            WHEN Assets > 0
            THEN ROUND((NetIncome / Assets) * 100, 2)
            ELSE NULL
        END AS ROA,
        CASE
            WHEN Revenue > 0
            THEN ROUND(Expenses / Revenue * 100, 2)
            ELSE NULL
        END AS ExpenseRatioPct,
        CASE
            WHEN Assets > 0
            THEN ROUND(Liabilities / Assets * 100, 2)
            ELSE NULL
        END AS LeverageRatioPct,
        CASE
            WHEN ParentOrganizationKey IS NULL THEN 'Parent Organization'
            ELSE 'Subsidiary'
        END AS OrganizationType
    FROM OrganizationSummary
),
DepartmentPerformance AS (
    SELECT
        ddg.DepartmentGroupKey,
        ddg.ParentDepartmentGroupKey,
        ddg.DepartmentGroupName,
        parent_dept.DepartmentGroupName AS ParentDepartmentName,
        dorg.OrganizationName,
        ofin.CalendarYear,
        ofin.CalendarQuarter,
        SUM(CASE WHEN ofin.AccountType IN ('Revenue', 'Income') THEN ofin.Amount ELSE 0 END) AS DeptRevenue,
        SUM(CASE WHEN ofin.AccountType IN ('Expense', 'Cost') THEN ABS(ofin.Amount) ELSE 0 END) AS DeptExpenses,
        SUM(CASE WHEN ofin.AccountType IN ('Revenue', 'Income') THEN ofin.Amount ELSE 0 END) -
        SUM(CASE WHEN ofin.AccountType IN ('Expense', 'Cost') THEN ABS(ofin.Amount) ELSE 0 END) AS DeptNetIncome,
        COUNT(DISTINCT ofin.AccountKey) AS AccountsUsed,
        COUNT(DISTINCT ofin.OrganizationKey) AS OrganizationsServed
    FROM OrganizationalFinance ofin
    INNER JOIN DimDepartmentGroup ddg ON ofin.DepartmentGroupKey = ddg.DepartmentGroupKey
    LEFT JOIN DimDepartmentGroup parent_dept ON ddg.ParentDepartmentGroupKey = parent_dept.DepartmentGroupKey
    INNER JOIN DimOrganization dorg ON ofin.OrganizationKey = dorg.OrganizationKey
    GROUP BY
        ddg.DepartmentGroupKey, ddg.ParentDepartmentGroupKey, ddg.DepartmentGroupName,
        parent_dept.DepartmentGroupName, dorg.OrganizationName,
        ofin.CalendarYear, ofin.CalendarQuarter
),
DepartmentMetrics AS (
    SELECT
        *,
        ROUND(DeptRevenue, 2) AS DeptRevenueRounded,
        ROUND(DeptExpenses, 2) AS DeptExpensesRounded,
        ROUND(DeptNetIncome, 2) AS DeptNetIncomeRounded,
        CASE
            WHEN DeptRevenue > 0
            THEN ROUND((DeptNetIncome / DeptRevenue) * 100, 2)
            ELSE NULL
        END AS DeptProfitMarginPct,
        CASE
            WHEN ParentDepartmentGroupKey IS NULL THEN 'Top-Level Department'
            ELSE 'Sub-Department'
        END AS DepartmentType,
        RANK() OVER (
            PARTITION BY CalendarYear, CalendarQuarter
            ORDER BY DeptNetIncome DESC
        ) AS DeptProfitRank
    FROM DepartmentPerformance
),
OrganizationRankings AS (
    SELECT
        *,
        RANK() OVER (
            PARTITION BY CalendarYear, CalendarQuarter
            ORDER BY NetIncome DESC
        ) AS ProfitRank,
        RANK() OVER (
            PARTITION BY CalendarYear, CalendarQuarter
            ORDER BY ProfitMarginPct DESC
        ) AS MarginRank,
        RANK() OVER (
            PARTITION BY CalendarYear, CalendarQuarter
            ORDER BY ROA DESC
        ) AS ROARank,
        NTILE(4) OVER (
            PARTITION BY CalendarYear, CalendarQuarter
            ORDER BY NetIncome DESC
        ) AS PerformanceQuartile
    FROM OrganizationMetrics
)
SELECT
    'Organization Performance' AS ReportSection,
    orr.OrganizationName,
    orr.ParentOrganizationName,
    orr.OrganizationType,
    orr.CalendarYear,
    orr.CalendarQuarter,
    orr.RevenueRounded AS Revenue,
    orr.ExpensesRounded AS Expenses,
    orr.NetIncomeRounded AS NetIncome,
    orr.AssetsRounded AS Assets,
    orr.LiabilitiesRounded AS Liabilities,
    orr.ProfitMarginPct,
    orr.ROA,
    orr.ExpenseRatioPct,
    orr.LeverageRatioPct,
    orr.DepartmentCount,
    orr.ProfitRank,
    orr.MarginRank,
    orr.PerformanceQuartile,
    NULL AS DepartmentGroupName,
    NULL AS ParentDepartmentName,
    NULL AS DeptProfitRank
FROM OrganizationRankings orr
WHERE orr.CalendarYear = (SELECT MAX(CalendarYear) FROM OrganizationRankings)

UNION ALL

SELECT
    'Department Performance' AS ReportSection,
    dm.OrganizationName,
    NULL AS ParentOrganizationName,
    NULL AS OrganizationType,
    dm.CalendarYear,
    dm.CalendarQuarter,
    dm.DeptRevenueRounded AS Revenue,
    dm.DeptExpensesRounded AS Expenses,
    dm.DeptNetIncomeRounded AS NetIncome,
    NULL AS Assets,
    NULL AS Liabilities,
    dm.DeptProfitMarginPct AS ProfitMarginPct,
    NULL AS ROA,
    NULL AS ExpenseRatioPct,
    NULL AS LeverageRatioPct,
    NULL AS DepartmentCount,
    NULL AS ProfitRank,
    NULL AS MarginRank,
    NULL AS PerformanceQuartile,
    dm.DepartmentGroupName,
    dm.ParentDepartmentName,
    dm.DeptProfitRank
FROM DepartmentMetrics dm
WHERE dm.CalendarYear = (SELECT MAX(CalendarYear) FROM DepartmentMetrics)
    AND dm.DeptNetIncome IS NOT NULL

ORDER BY ReportSection, ProfitRank NULLS LAST, DeptProfitRank NULLS LAST, NetIncome DESC NULLS LAST;
```

---

# Business Question 5: Temporal Financial Trends and Period-Over-Period Analysis

## Intent

Analyze financial performance trends over time with sophisticated period-over-period comparisons to identify patterns, anomalies, and directional changes. This temporal financial analysis provides:
- Month-over-month (MoM) and year-over-year (YoY) growth rates
- Quarter-over-quarter (QoQ) comparisons
- Fiscal vs calendar year reconciliation
- Rolling averages and trend smoothing
- Seasonality identification and indexing
- Cumulative year-to-date tracking
- Identification of inflection points and trend reversals
- Comparative period analysis across multiple years

Understanding temporal patterns enables accurate forecasting, identifies cyclical business patterns, supports strategic planning cycles, facilitates board reporting, and provides early warning signals for financial performance changes requiring management attention.

## SQL Code

```sql
WITH MonthlyFinancials AS (
    SELECT
        dd.CalendarYear,
        dd.MonthNumberOfYear,
        dd.EnglishMonthName AS MonthName,
        dd.FiscalYear,
        dd.FiscalQuarter,
        dd.CalendarQuarter,
        da.AccountType,
        ds.ScenarioName,
        dorg.OrganizationName,
        SUM(ff.Amount) AS MonthlyAmount
    FROM FactFinance ff
    INNER JOIN DimDate dd ON ff.DateKey = dd.DateKey
    INNER JOIN DimAccount da ON ff.AccountKey = da.AccountKey
    INNER JOIN DimScenario ds ON ff.ScenarioKey = ds.ScenarioKey
    INNER JOIN DimOrganization dorg ON ff.OrganizationKey = dorg.OrganizationKey
    WHERE ds.ScenarioName = 'Actual'
    GROUP BY
        dd.CalendarYear, dd.MonthNumberOfYear, dd.EnglishMonthName,
        dd.FiscalYear, dd.FiscalQuarter, dd.CalendarQuarter,
        da.AccountType, ds.ScenarioName, dorg.OrganizationName
),
MonthlyMetrics AS (
    SELECT
        CalendarYear,
        MonthNumberOfYear,
        MonthName,
        FiscalYear,
        FiscalQuarter,
        CalendarQuarter,
        AccountType,
        OrganizationName,
        MonthlyAmount,
        -- Prior period comparisons
        LAG(MonthlyAmount, 1) OVER (
            PARTITION BY AccountType, OrganizationName
            ORDER BY CalendarYear, MonthNumberOfYear
        ) AS PrevMonthAmount,
        LAG(MonthlyAmount, 12) OVER (
            PARTITION BY AccountType, OrganizationName
            ORDER BY CalendarYear, MonthNumberOfYear
        ) AS SameMonthPrevYearAmount,
        LAG(MonthlyAmount, 3) OVER (
            PARTITION BY AccountType, OrganizationName
            ORDER BY CalendarYear, MonthNumberOfYear
        ) AS PrevQuarterMonthAmount,
        -- Moving averages
        AVG(MonthlyAmount) OVER (
            PARTITION BY AccountType, OrganizationName
            ORDER BY CalendarYear, MonthNumberOfYear
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS ThreeMonthMA,
        AVG(MonthlyAmount) OVER (
            PARTITION BY AccountType, OrganizationName
            ORDER BY CalendarYear, MonthNumberOfYear
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS TwelveMonthMA,
        -- Year-to-date cumulative
        SUM(MonthlyAmount) OVER (
            PARTITION BY CalendarYear, AccountType, OrganizationName
            ORDER BY MonthNumberOfYear
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS YTDAmount,
        -- Historical average for seasonality
        AVG(MonthlyAmount) OVER (
            PARTITION BY MonthNumberOfYear, AccountType, OrganizationName
        ) AS HistoricalMonthAvg
    FROM MonthlyFinancials
),
TrendAnalysis AS (
    SELECT
        *,
        ROUND(MonthlyAmount, 2) AS MonthlyAmountRounded,
        ROUND(ThreeMonthMA, 2) AS ThreeMonthMARounded,
        ROUND(TwelveMonthMA, 2) AS TwelveMonthMARounded,
        ROUND(YTDAmount, 2) AS YTDAmountRounded,
        -- MoM growth
        CASE
            WHEN PrevMonthAmount IS NOT NULL AND PrevMonthAmount != 0
            THEN ROUND(((MonthlyAmount - PrevMonthAmount) / ABS(PrevMonthAmount)) * 100, 2)
            ELSE NULL
        END AS MoMGrowthPct,
        -- YoY growth
        CASE
            WHEN SameMonthPrevYearAmount IS NOT NULL AND SameMonthPrevYearAmount != 0
            THEN ROUND(((MonthlyAmount - SameMonthPrevYearAmount) / ABS(SameMonthPrevYearAmount)) * 100, 2)
            ELSE NULL
        END AS YoYGrowthPct,
        -- QoQ growth (comparing to same month in previous quarter)
        CASE
            WHEN PrevQuarterMonthAmount IS NOT NULL AND PrevQuarterMonthAmount != 0
            THEN ROUND(((MonthlyAmount - PrevQuarterMonthAmount) / ABS(PrevQuarterMonthAmount)) * 100, 2)
            ELSE NULL
        END AS QoQGrowthPct,
        -- Seasonality index
        CASE
            WHEN HistoricalMonthAvg IS NOT NULL AND HistoricalMonthAvg != 0
            THEN ROUND((MonthlyAmount / HistoricalMonthAvg) * 100, 2)
            ELSE NULL
        END AS SeasonalityIndex,
        -- Trend direction
        CASE
            WHEN MonthlyAmount > ThreeMonthMA * 1.05 THEN 'Above Trend'
            WHEN MonthlyAmount < ThreeMonthMA * 0.95 THEN 'Below Trend'
            ELSE 'On Trend'
        END AS TrendStatus
    FROM MonthlyMetrics
),
QuarterlyAggregates AS (
    SELECT
        CalendarYear,
        CalendarQuarter,
        FiscalYear,
        FiscalQuarter,
        AccountType,
        OrganizationName,
        SUM(MonthlyAmount) AS QuarterlyAmount,
        COUNT(*) AS MonthsInQuarter,
        ROUND(AVG(MonthlyAmount), 2) AS AvgMonthlyAmount
    FROM MonthlyFinancials
    GROUP BY
        CalendarYear, CalendarQuarter, FiscalYear,
        FiscalQuarter, AccountType, OrganizationName
),
QuarterlyTrends AS (
    SELECT
        *,
        LAG(QuarterlyAmount, 1) OVER (
            PARTITION BY AccountType, OrganizationName
            ORDER BY CalendarYear, CalendarQuarter
        ) AS PrevQuarterAmount,
        LAG(QuarterlyAmount, 4) OVER (
            PARTITION BY AccountType, OrganizationName
            ORDER BY CalendarYear, CalendarQuarter
        ) AS SameQuarterPrevYearAmount,
        ROUND(QuarterlyAmount, 2) AS QuarterlyAmountRounded,
        CASE
            WHEN LAG(QuarterlyAmount, 1) OVER (
                PARTITION BY AccountType, OrganizationName
                ORDER BY CalendarYear, CalendarQuarter
            ) IS NOT NULL AND LAG(QuarterlyAmount, 1) OVER (
                PARTITION BY AccountType, OrganizationName
                ORDER BY CalendarYear, CalendarQuarter
            ) != 0
            THEN ROUND(((QuarterlyAmount - LAG(QuarterlyAmount, 1) OVER (
                PARTITION BY AccountType, OrganizationName
                ORDER BY CalendarYear, CalendarQuarter
            )) / ABS(LAG(QuarterlyAmount, 1) OVER (
                PARTITION BY AccountType, OrganizationName
                ORDER BY CalendarYear, CalendarQuarter
            ))) * 100, 2)
            ELSE NULL
        END AS QoQGrowthPct,
        CASE
            WHEN LAG(QuarterlyAmount, 4) OVER (
                PARTITION BY AccountType, OrganizationName
                ORDER BY CalendarYear, CalendarQuarter
            ) IS NOT NULL AND LAG(QuarterlyAmount, 4) OVER (
                PARTITION BY AccountType, OrganizationName
                ORDER BY CalendarYear, CalendarQuarter
            ) != 0
            THEN ROUND(((QuarterlyAmount - LAG(QuarterlyAmount, 4) OVER (
                PARTITION BY AccountType, OrganizationName
                ORDER BY CalendarYear, CalendarQuarter
            )) / ABS(LAG(QuarterlyAmount, 4) OVER (
                PARTITION BY AccountType, OrganizationName
                ORDER BY CalendarYear, CalendarQuarter
            ))) * 100, 2)
            ELSE NULL
        END AS YoYQuarterGrowthPct
    FROM QuarterlyAggregates
),
YearOverYearComparison AS (
    SELECT
        AccountType,
        OrganizationName,
        CalendarYear,
        SUM(CASE WHEN MonthNumberOfYear <= 12 THEN MonthlyAmount ELSE 0 END) AS FullYearAmount,
        AVG(YoYGrowthPct) AS AvgYoYGrowthPct,
        MAX(MonthlyAmount) AS PeakMonthAmount,
        MIN(MonthlyAmount) AS TroughMonthAmount,
        ROUND(STDEV(MonthlyAmount), 2) AS MonthlyVolatility
    FROM TrendAnalysis
    GROUP BY AccountType, OrganizationName, CalendarYear
)
SELECT
    'Monthly Trends' AS ReportSection,
    ta.CalendarYear,
    ta.MonthNumberOfYear,
    ta.MonthName,
    ta.FiscalYear,
    ta.CalendarQuarter,
    ta.FiscalQuarter,
    ta.AccountType,
    ta.OrganizationName,
    ta.MonthlyAmountRounded AS Amount,
    ta.MoMGrowthPct,
    ta.YoYGrowthPct,
    ta.QoQGrowthPct,
    ta.ThreeMonthMARounded AS ThreeMonthMA,
    ta.TwelveMonthMARounded AS TwelveMonthMA,
    ta.YTDAmountRounded AS YTDAmount,
    ta.SeasonalityIndex,
    ta.TrendStatus,
    NULL AS QuarterlyAmount,
    NULL AS FullYearAmount,
    NULL AS AvgYoYGrowthPct,
    NULL AS MonthlyVolatility
FROM TrendAnalysis ta
WHERE ta.CalendarYear >= (SELECT MAX(CalendarYear) - 1 FROM TrendAnalysis)

UNION ALL

SELECT
    'Quarterly Trends' AS ReportSection,
    qt.CalendarYear,
    NULL AS MonthNumberOfYear,
    NULL AS MonthName,
    qt.FiscalYear,
    qt.CalendarQuarter,
    qt.FiscalQuarter,
    qt.AccountType,
    qt.OrganizationName,
    qt.QuarterlyAmountRounded AS Amount,
    NULL AS MoMGrowthPct,
    qt.YoYQuarterGrowthPct AS YoYGrowthPct,
    qt.QoQGrowthPct,
    NULL AS ThreeMonthMA,
    NULL AS TwelveMonthMA,
    NULL AS YTDAmount,
    NULL AS SeasonalityIndex,
    NULL AS TrendStatus,
    qt.QuarterlyAmountRounded AS QuarterlyAmount,
    NULL AS FullYearAmount,
    NULL AS AvgYoYGrowthPct,
    NULL AS MonthlyVolatility
FROM QuarterlyTrends qt
WHERE qt.CalendarYear >= (SELECT MAX(CalendarYear) - 1 FROM QuarterlyTrends)

UNION ALL

SELECT
    'Annual Summary' AS ReportSection,
    yoy.CalendarYear,
    NULL AS MonthNumberOfYear,
    NULL AS MonthName,
    NULL AS FiscalYear,
    NULL AS CalendarQuarter,
    NULL AS FiscalQuarter,
    yoy.AccountType,
    yoy.OrganizationName,
    ROUND(yoy.FullYearAmount, 2) AS Amount,
    NULL AS MoMGrowthPct,
    NULL AS YoYGrowthPct,
    NULL AS QoQGrowthPct,
    NULL AS ThreeMonthMA,
    NULL AS TwelveMonthMA,
    NULL AS YTDAmount,
    NULL AS SeasonalityIndex,
    NULL AS TrendStatus,
    NULL AS QuarterlyAmount,
    ROUND(yoy.FullYearAmount, 2) AS FullYearAmount,
    yoy.AvgYoYGrowthPct,
    yoy.MonthlyVolatility
FROM YearOverYearComparison yoy

ORDER BY ReportSection, CalendarYear DESC, MonthNumberOfYear NULLS LAST, CalendarQuarter NULLS LAST;
```

---

## Summary

These five business questions provide a comprehensive framework for financial analysis:

1. **Budget vs Actual Variance Analysis** - Monitoring performance against plan with favorable/unfavorable classification and organizational scoring
2. **Multi-Scenario Comparison** - Evaluating Budget and Forecast accuracy to improve planning processes
3. **Account Hierarchy Navigation** - Understanding chart of accounts structure with recursive rollups and validation
4. **Organizational Performance** - Analyzing business unit and department financial results with profitability metrics
5. **Temporal Trends** - Tracking financial performance over time with MoM, QoQ, and YoY comparisons

Each query demonstrates advanced analytical techniques including:
- Complex CTEs for multi-stage analysis
- Window functions (LAG, moving averages, cumulative sums)
- Recursive queries for hierarchical navigation
- Variance calculations and percentage analysis
- Scenario pivoting and comparison
- Ranking and performance scoring
- Time-series analysis with multiple periods
- Fiscal and calendar year reconciliation
- Seasonality indexing
- Statistical measures (standard deviation, volatility)

These analyses enable data-driven decisions for:
- Financial planning and budgeting accuracy
- Performance management and accountability
- Strategic resource allocation
- Organizational restructuring
- Cost control and optimization
- Forecast improvement
- Executive reporting and board presentations
- Compliance and audit support

The insights from financial analysis provide the foundation for sound fiscal management, strategic planning, and stakeholder confidence in financial stewardship.
