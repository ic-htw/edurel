# Call Center Performance Analysis - Business Questions

## Introduction

Call center operations are critical for customer service delivery and direct sales conversion. Effective analysis of call center performance data enables organizations to optimize staffing levels, improve service quality, maximize conversion rates, and identify operational bottlenecks.

This document presents a comprehensive analytical framework for evaluating call center performance using the AdventureWorks data warehouse. The analysis leverages the FactCallCenter fact table combined with the DimDate dimension to examine various operational metrics including:
- Call volume and response patterns
- Operator staffing levels and efficiency
- Service quality grades
- Issue resolution effectiveness
- Order conversion rates
- Shift performance comparisons
- Temporal trends and seasonality

The FactCallCenter table captures daily operational metrics segmented by wage type (hourly/salaried) and shift (AM/PM/Graveyard), including:
- Operator staffing (Level One, Level Two, Total)
- Call volumes and automatic response rates
- Orders generated through calls
- Issues raised and average resolution time
- Service grade scores

The following business questions explore various aspects of call center performance to drive operational improvements, resource optimization, and enhanced customer experience.

---

# Business Question 1: Shift Performance Comparison and Staffing Optimization Analysis

## Intent

Analyze performance differences across shifts to identify optimal staffing patterns and productivity variations by time of day. This comprehensive analysis provides:
- Comparative metrics across shifts (AM, PM, Graveyard)
- Calls-per-operator efficiency ratios
- Order conversion rates by shift
- Service grade performance across shifts
- Optimal staffing level recommendations
- Cost-effectiveness analysis by wage type and shift

Understanding shift-level performance enables better workforce scheduling, identifies training opportunities, and optimizes the balance between service quality and operational costs.

## SQL Code

```sql
WITH ShiftMetrics AS (
    SELECT
        fcc.Shift,
        fcc.WageType,
        dd.CalendarYear,
        dd.CalendarQuarter,
        COUNT(*) AS OperatingDays,
        SUM(fcc.TotalOperators) AS TotalOperatorShifts,
        SUM(fcc.LevelOneOperators) AS TotalLevelOneShifts,
        SUM(fcc.LevelTwoOperators) AS TotalLevelTwoShifts,
        SUM(fcc.Calls) AS TotalCalls,
        SUM(fcc.AutomaticResponses) AS TotalAutomaticResponses,
        SUM(fcc.Orders) AS TotalOrders,
        SUM(fcc.IssuesRaised) AS TotalIssuesRaised,
        AVG(fcc.AverageTimePerIssue) AS AvgTimePerIssue,
        AVG(fcc.ServiceGrade) AS AvgServiceGrade,
        AVG(fcc.TotalOperators) AS AvgOperatorsPerDay,
        AVG(fcc.Calls) AS AvgCallsPerDay
    FROM FactCallCenter fcc
    INNER JOIN DimDate dd ON fcc.DateKey = dd.DateKey
    GROUP BY fcc.Shift, fcc.WageType, dd.CalendarYear, dd.CalendarQuarter
),
ShiftEfficiency AS (
    SELECT
        Shift,
        WageType,
        CalendarYear,
        CalendarQuarter,
        OperatingDays,
        TotalCalls,
        TotalAutomaticResponses,
        TotalOrders,
        TotalIssuesRaised,
        TotalOperatorShifts,
        TotalLevelOneShifts,
        TotalLevelTwoShifts,
        ROUND(AvgTimePerIssue, 2) AS AvgTimePerIssue,
        ROUND(AvgServiceGrade, 4) AS AvgServiceGrade,
        ROUND(AvgOperatorsPerDay, 2) AS AvgOperatorsPerDay,
        ROUND(AvgCallsPerDay, 2) AS AvgCallsPerDay,
        -- Efficiency Metrics
        ROUND(CAST(TotalCalls AS FLOAT) / NULLIF(TotalOperatorShifts, 0), 2) AS CallsPerOperatorShift,
        ROUND(CAST(TotalOrders AS FLOAT) / NULLIF(TotalCalls, 0) * 100, 2) AS ConversionRatePct,
        ROUND(CAST(TotalAutomaticResponses AS FLOAT) / NULLIF(TotalCalls, 0) * 100, 2) AS AutoResponseRatePct,
        ROUND(CAST(TotalIssuesRaised AS FLOAT) / NULLIF(TotalCalls, 0) * 100, 2) AS IssueRatePct,
        ROUND(CAST(TotalOrders AS FLOAT) / NULLIF(TotalOperatorShifts, 0), 2) AS OrdersPerOperatorShift,
        ROUND(CAST(TotalLevelTwoShifts AS FLOAT) / NULLIF(TotalOperatorShifts, 0) * 100, 2) AS Level2OperatorPct
    FROM ShiftMetrics
),
ShiftRankings AS (
    SELECT
        *,
        RANK() OVER (PARTITION BY CalendarYear, CalendarQuarter ORDER BY ConversionRatePct DESC) AS ConversionRank,
        RANK() OVER (PARTITION BY CalendarYear, CalendarQuarter ORDER BY AvgServiceGrade DESC) AS ServiceGradeRank,
        RANK() OVER (PARTITION BY CalendarYear, CalendarQuarter ORDER BY CallsPerOperatorShift DESC) AS EfficiencyRank,
        RANK() OVER (PARTITION BY CalendarYear, CalendarQuarter ORDER BY AvgTimePerIssue ASC) AS IssueResolutionRank
    FROM ShiftEfficiency
)
SELECT
    Shift,
    WageType,
    CalendarYear,
    CalendarQuarter,
    OperatingDays,
    TotalCalls,
    TotalOrders,
    TotalIssuesRaised,
    AvgOperatorsPerDay,
    AvgCallsPerDay,
    CallsPerOperatorShift,
    ConversionRatePct,
    AutoResponseRatePct,
    IssueRatePct,
    OrdersPerOperatorShift,
    AvgTimePerIssue,
    AvgServiceGrade,
    Level2OperatorPct,
    ConversionRank,
    ServiceGradeRank,
    EfficiencyRank,
    IssueResolutionRank,
    CASE
        WHEN ConversionRank = 1 AND ServiceGradeRank <= 2 THEN 'Top Performer'
        WHEN ConversionRank <= 2 OR ServiceGradeRank <= 2 THEN 'Strong Performer'
        WHEN ConversionRank >= 4 AND ServiceGradeRank >= 4 THEN 'Needs Improvement'
        ELSE 'Average Performer'
    END AS PerformanceCategory
FROM ShiftRankings
ORDER BY CalendarYear DESC, CalendarQuarter DESC, ConversionRatePct DESC;
```

---

# Business Question 2: Operator Staffing Level Impact on Service Quality and Conversion

## Intent

Analyze the relationship between operator staffing levels, service quality, and business outcomes to determine optimal staffing configurations. This analysis examines:
- Correlation between total operator count and service metrics
- Impact of Level 1 vs Level 2 operator ratios on performance
- Optimal operator-to-call ratios for service quality
- Staffing efficiency sweet spots that maximize both quality and conversion
- Identification of understaffed and overstaffed periods
- Cost-benefit analysis of different staffing models

This insight enables data-driven workforce planning, identifies when additional senior operators (Level 2) improve outcomes, and helps balance cost constraints with service quality requirements.

## SQL Code

```sql
WITH DailyOperatorMetrics AS (
    SELECT
        dd.FullDateAlternateKey AS Date,
        dd.CalendarYear,
        dd.CalendarQuarter,
        dd.MonthNumberOfYear AS CalendarMonth,
        dd.EnglishDayNameOfWeek AS DayOfWeek,
        fcc.Shift,
        fcc.WageType,
        fcc.TotalOperators,
        fcc.LevelOneOperators,
        fcc.LevelTwoOperators,
        fcc.Calls,
        fcc.AutomaticResponses,
        fcc.Orders,
        fcc.IssuesRaised,
        fcc.AverageTimePerIssue,
        fcc.ServiceGrade,
        -- Calculate ratios
        ROUND(CAST(fcc.Calls AS FLOAT) / NULLIF(fcc.TotalOperators, 0), 2) AS CallsPerOperator,
        ROUND(CAST(fcc.Orders AS FLOAT) / NULLIF(fcc.Calls, 0) * 100, 2) AS ConversionRate,
        ROUND(CAST(fcc.LevelTwoOperators AS FLOAT) / NULLIF(fcc.TotalOperators, 0) * 100, 2) AS SeniorOperatorPct,
        ROUND(CAST(fcc.IssuesRaised AS FLOAT) / NULLIF(fcc.Calls, 0) * 100, 2) AS IssueRate
    FROM FactCallCenter fcc
    INNER JOIN DimDate dd ON fcc.DateKey = dd.DateKey
),
StaffingBuckets AS (
    SELECT
        *,
        CASE
            WHEN TotalOperators <= 5 THEN '1-5 Operators'
            WHEN TotalOperators <= 10 THEN '6-10 Operators'
            WHEN TotalOperators <= 15 THEN '11-15 Operators'
            WHEN TotalOperators <= 20 THEN '16-20 Operators'
            ELSE '21+ Operators'
        END AS StaffingLevel,
        CASE
            WHEN SeniorOperatorPct < 20 THEN 'Low Senior (<20%)'
            WHEN SeniorOperatorPct < 40 THEN 'Medium Senior (20-40%)'
            ELSE 'High Senior (40%+)'
        END AS SeniorMixLevel,
        CASE
            WHEN CallsPerOperator < 50 THEN 'Low Load (<50)'
            WHEN CallsPerOperator < 100 THEN 'Medium Load (50-100)'
            WHEN CallsPerOperator < 150 THEN 'High Load (100-150)'
            ELSE 'Very High Load (150+)'
        END AS WorkloadLevel
    FROM DailyOperatorMetrics
),
StaffingImpactAnalysis AS (
    SELECT
        StaffingLevel,
        SeniorMixLevel,
        WorkloadLevel,
        COUNT(*) AS ObservationCount,
        ROUND(AVG(TotalOperators), 2) AS AvgTotalOperators,
        ROUND(AVG(SeniorOperatorPct), 2) AS AvgSeniorOperatorPct,
        ROUND(AVG(Calls), 2) AS AvgCalls,
        ROUND(AVG(CallsPerOperator), 2) AS AvgCallsPerOperator,
        ROUND(AVG(ConversionRate), 2) AS AvgConversionRate,
        ROUND(AVG(ServiceGrade), 4) AS AvgServiceGrade,
        ROUND(AVG(IssueRate), 2) AS AvgIssueRate,
        ROUND(AVG(AverageTimePerIssue), 2) AS AvgTimePerIssue,
        ROUND(AVG(Orders), 2) AS AvgOrders,
        -- Performance variability
        ROUND(STDDEV_SAMP(ConversionRate), 2) AS StdDevConversionRate,
        ROUND(STDDEV_SAMP(ServiceGrade), 4) AS StdDevServiceGrade,
        -- Min/Max for ranges
        ROUND(MIN(ConversionRate), 2) AS MinConversionRate,
        ROUND(MAX(ConversionRate), 2) AS MaxConversionRate,
        ROUND(MIN(ServiceGrade), 4) AS MinServiceGrade,
        ROUND(MAX(ServiceGrade), 4) AS MaxServiceGrade
    FROM StaffingBuckets
    GROUP BY StaffingLevel, SeniorMixLevel, WorkloadLevel
),
PerformanceScoring AS (
    SELECT
        *,
        -- Composite performance score (higher is better)
        ROUND((AvgConversionRate / 10) + (AvgServiceGrade * 100) - (AvgIssueRate / 2), 2) AS PerformanceScore,
        RANK() OVER (ORDER BY AvgConversionRate DESC, AvgServiceGrade DESC) AS OverallRank
    FROM StaffingImpactAnalysis
    WHERE ObservationCount >= 5  -- Filter out statistically insignificant groups
)
SELECT
    StaffingLevel,
    SeniorMixLevel,
    WorkloadLevel,
    ObservationCount,
    AvgTotalOperators,
    AvgSeniorOperatorPct,
    AvgCalls,
    AvgCallsPerOperator,
    AvgConversionRate,
    AvgServiceGrade,
    AvgIssueRate,
    AvgTimePerIssue,
    AvgOrders,
    StdDevConversionRate,
    StdDevServiceGrade,
    MinConversionRate,
    MaxConversionRate,
    MinServiceGrade,
    MaxServiceGrade,
    PerformanceScore,
    OverallRank,
    CASE
        WHEN OverallRank <= 3 THEN 'Optimal Configuration'
        WHEN OverallRank <= 10 THEN 'Good Configuration'
        WHEN OverallRank <= 20 THEN 'Acceptable Configuration'
        ELSE 'Suboptimal Configuration'
    END AS ConfigurationAssessment
FROM PerformanceScoring
ORDER BY PerformanceScore DESC;
```

---

# Business Question 3: Temporal Performance Trends and Seasonality Analysis

## Intent

Identify temporal patterns, trends, and seasonality in call center performance to enable proactive resource planning and forecasting. This time-series analysis provides:
- Month-over-month and year-over-year trend analysis
- Seasonal patterns in call volume and conversion
- Day-of-week performance variations
- Identification of performance degradation or improvement trends
- Peak and off-peak period characteristics
- Holiday and special event impacts
- Moving averages to smooth volatility

Understanding temporal patterns enables better capacity planning, identifies when performance interventions are needed, and supports accurate demand forecasting for staffing and resource allocation.

## SQL Code

```sql
WITH DailyMetrics AS (
    SELECT
        dd.FullDateAlternateKey AS Date,
        dd.DateKey,
        dd.CalendarYear,
        dd.CalendarQuarter,
        dd.MonthNumberOfYear,
        dd.EnglishMonthName AS MonthName,
        dd.DayNumberOfWeek,
        dd.EnglishDayNameOfWeek AS DayOfWeek,
        dd.WeekNumberOfYear,
        SUM(fcc.TotalOperators) AS TotalOperators,
        SUM(fcc.Calls) AS TotalCalls,
        SUM(fcc.Orders) AS TotalOrders,
        SUM(fcc.IssuesRaised) AS TotalIssues,
        AVG(fcc.ServiceGrade) AS AvgServiceGrade,
        AVG(fcc.AverageTimePerIssue) AS AvgTimePerIssue,
        ROUND(CAST(SUM(fcc.Orders) AS FLOAT) / NULLIF(SUM(fcc.Calls), 0) * 100, 2) AS ConversionRate
    FROM FactCallCenter fcc
    INNER JOIN DimDate dd ON fcc.DateKey = dd.DateKey
    GROUP BY
        dd.FullDateAlternateKey, dd.DateKey, dd.CalendarYear, dd.CalendarQuarter,
        dd.MonthNumberOfYear, dd.EnglishMonthName, dd.DayNumberOfWeek,
        dd.EnglishDayNameOfWeek, dd.WeekNumberOfYear
),
MonthlyAggregates AS (
    SELECT
        CalendarYear,
        MonthNumberOfYear,
        MonthName,
        COUNT(DISTINCT Date) AS OperatingDays,
        SUM(TotalOperators) AS MonthlyOperators,
        SUM(TotalCalls) AS MonthlyCalls,
        SUM(TotalOrders) AS MonthlyOrders,
        SUM(TotalIssues) AS MonthlyIssues,
        AVG(AvgServiceGrade) AS MonthlyServiceGrade,
        AVG(AvgTimePerIssue) AS MonthlyAvgTimePerIssue,
        AVG(ConversionRate) AS MonthlyConversionRate,
        AVG(TotalCalls) AS AvgDailyCalls,
        AVG(TotalOrders) AS AvgDailyOrders
    FROM DailyMetrics
    GROUP BY CalendarYear, MonthNumberOfYear, MonthName
),
MonthlyTrends AS (
    SELECT
        CalendarYear,
        MonthNumberOfYear,
        MonthName,
        OperatingDays,
        MonthlyCalls,
        MonthlyOrders,
        MonthlyIssues,
        ROUND(MonthlyServiceGrade, 4) AS MonthlyServiceGrade,
        ROUND(MonthlyAvgTimePerIssue, 2) AS MonthlyAvgTimePerIssue,
        ROUND(MonthlyConversionRate, 2) AS MonthlyConversionRate,
        ROUND(AvgDailyCalls, 2) AS AvgDailyCalls,
        ROUND(AvgDailyOrders, 2) AS AvgDailyOrders,
        -- Previous month comparison
        LAG(MonthlyCalls, 1) OVER (ORDER BY CalendarYear, MonthNumberOfYear) AS PrevMonthCalls,
        LAG(MonthlyConversionRate, 1) OVER (ORDER BY CalendarYear, MonthNumberOfYear) AS PrevMonthConversionRate,
        -- Same month previous year
        LAG(MonthlyCalls, 12) OVER (ORDER BY CalendarYear, MonthNumberOfYear) AS SameMonthLastYearCalls,
        LAG(MonthlyConversionRate, 12) OVER (ORDER BY CalendarYear, MonthNumberOfYear) AS SameMonthLastYearConversionRate,
        -- Moving averages
        AVG(MonthlyCalls) OVER (
            ORDER BY CalendarYear, MonthNumberOfYear
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS ThreeMonthAvgCalls,
        AVG(MonthlyConversionRate) OVER (
            ORDER BY CalendarYear, MonthNumberOfYear
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS ThreeMonthAvgConversion
    FROM MonthlyAggregates
),
SeasonalityAnalysis AS (
    SELECT
        CalendarYear,
        MonthNumberOfYear,
        MonthName,
        OperatingDays,
        MonthlyCalls,
        MonthlyOrders,
        MonthlyIssues,
        MonthlyServiceGrade,
        MonthlyConversionRate,
        AvgDailyCalls,
        AvgDailyOrders,
        ROUND(ThreeMonthAvgCalls, 2) AS ThreeMonthAvgCalls,
        ROUND(ThreeMonthAvgConversion, 2) AS ThreeMonthAvgConversion,
        -- Month-over-month growth
        CASE
            WHEN PrevMonthCalls > 0
            THEN ROUND(((MonthlyCalls - PrevMonthCalls) / CAST(PrevMonthCalls AS FLOAT)) * 100, 2)
            ELSE NULL
        END AS MoMCallGrowthPct,
        CASE
            WHEN PrevMonthConversionRate > 0
            THEN ROUND(MonthlyConversionRate - PrevMonthConversionRate, 2)
            ELSE NULL
        END AS MoMConversionChange,
        -- Year-over-year growth
        CASE
            WHEN SameMonthLastYearCalls > 0
            THEN ROUND(((MonthlyCalls - SameMonthLastYearCalls) / CAST(SameMonthLastYearCalls AS FLOAT)) * 100, 2)
            ELSE NULL
        END AS YoYCallGrowthPct,
        CASE
            WHEN SameMonthLastYearConversionRate > 0
            THEN ROUND(MonthlyConversionRate - SameMonthLastYearConversionRate, 2)
            ELSE NULL
        END AS YoYConversionChange,
        -- Seasonality index (compared to overall average)
        ROUND((MonthlyCalls / AVG(MonthlyCalls) OVER ()) * 100, 2) AS SeasonalityIndex
    FROM MonthlyTrends
),
DayOfWeekPatterns AS (
    SELECT
        DayOfWeek,
        DayNumberOfWeek,
        COUNT(*) AS ObservationCount,
        ROUND(AVG(TotalCalls), 2) AS AvgCalls,
        ROUND(AVG(TotalOrders), 2) AS AvgOrders,
        ROUND(AVG(ConversionRate), 2) AS AvgConversionRate,
        ROUND(AVG(AvgServiceGrade), 4) AS AvgServiceGrade,
        RANK() OVER (ORDER BY AVG(TotalCalls) DESC) AS CallVolumeRank,
        RANK() OVER (ORDER BY AVG(ConversionRate) DESC) AS ConversionRank
    FROM DailyMetrics
    GROUP BY DayOfWeek, DayNumberOfWeek
)
SELECT
    'Monthly Trends' AS AnalysisType,
    CAST(CalendarYear AS VARCHAR) || '-' || CAST(MonthNumberOfYear AS VARCHAR) AS Period,
    MonthName AS PeriodName,
    MonthlyCalls AS Calls,
    MonthlyOrders AS Orders,
    MonthlyConversionRate AS ConversionRate,
    MonthlyServiceGrade AS ServiceGrade,
    ThreeMonthAvgCalls AS MovingAvgCalls,
    ThreeMonthAvgConversion AS MovingAvgConversion,
    MoMCallGrowthPct AS MoMGrowthPct,
    YoYCallGrowthPct AS YoYGrowthPct,
    SeasonalityIndex,
    NULL AS DayOfWeek,
    NULL AS CallVolumeRank
FROM SeasonalityAnalysis
WHERE CalendarYear >= (SELECT MAX(CalendarYear) - 1 FROM SeasonalityAnalysis)

UNION ALL

SELECT
    'Day of Week Patterns' AS AnalysisType,
    CAST(DayNumberOfWeek AS VARCHAR) AS Period,
    DayOfWeek AS PeriodName,
    AvgCalls AS Calls,
    AvgOrders AS Orders,
    AvgConversionRate AS ConversionRate,
    AvgServiceGrade AS ServiceGrade,
    NULL AS MovingAvgCalls,
    NULL AS MovingAvgConversion,
    NULL AS MoMGrowthPct,
    NULL AS YoYGrowthPct,
    NULL AS SeasonalityIndex,
    DayOfWeek,
    CallVolumeRank
FROM DayOfWeekPatterns

ORDER BY AnalysisType, Period;
```

---

# Business Question 4: Issue Resolution Efficiency and Quality Analysis

## Intent

Analyze issue handling effectiveness to identify opportunities for improving customer satisfaction and operational efficiency. This analysis examines:
- Issue occurrence rates across different operational contexts
- Average time to resolve issues by various factors
- Correlation between issue resolution speed and service grades
- Impact of staffing levels on issue handling
- Identification of high-issue periods requiring intervention
- Relationship between automatic responses and issue rates
- Quality vs. speed trade-offs in issue resolution

Understanding issue resolution patterns enables targeted training, process improvements, and quality assurance initiatives to enhance customer experience and operational efficiency.

## SQL Code

```sql
WITH DailyIssueMetrics AS (
    SELECT
        dd.FullDateAlternateKey AS Date,
        dd.CalendarYear,
        dd.CalendarQuarter,
        dd.MonthNumberOfYear,
        dd.EnglishMonthName AS MonthName,
        dd.EnglishDayNameOfWeek AS DayOfWeek,
        fcc.Shift,
        fcc.WageType,
        fcc.TotalOperators,
        fcc.LevelOneOperators,
        fcc.LevelTwoOperators,
        fcc.Calls,
        fcc.AutomaticResponses,
        fcc.Orders,
        fcc.IssuesRaised,
        fcc.AverageTimePerIssue,
        fcc.ServiceGrade,
        -- Calculated metrics
        ROUND(CAST(fcc.IssuesRaised AS FLOAT) / NULLIF(fcc.Calls, 0) * 100, 2) AS IssueRate,
        ROUND(CAST(fcc.Calls AS FLOAT) / NULLIF(fcc.TotalOperators, 0), 2) AS CallsPerOperator,
        ROUND(CAST(fcc.AutomaticResponses AS FLOAT) / NULLIF(fcc.Calls, 0) * 100, 2) AS AutoResponseRate,
        ROUND(CAST(fcc.LevelTwoOperators AS FLOAT) / NULLIF(fcc.TotalOperators, 0) * 100, 2) AS SeniorOperatorPct
    FROM FactCallCenter fcc
    INNER JOIN DimDate dd ON fcc.DateKey = dd.DateKey
),
IssueSegmentation AS (
    SELECT
        *,
        CASE
            WHEN IssueRate < 5 THEN 'Low Issues (<5%)'
            WHEN IssueRate < 10 THEN 'Medium Issues (5-10%)'
            WHEN IssueRate < 15 THEN 'High Issues (10-15%)'
            ELSE 'Critical Issues (15%+)'
        END AS IssueSeverityLevel,
        CASE
            WHEN AverageTimePerIssue < 300 THEN 'Fast Resolution (<5 min)'
            WHEN AverageTimePerIssue < 600 THEN 'Normal Resolution (5-10 min)'
            WHEN AverageTimePerIssue < 900 THEN 'Slow Resolution (10-15 min)'
            ELSE 'Very Slow Resolution (15+ min)'
        END AS ResolutionSpeedCategory,
        CASE
            WHEN ServiceGrade >= 0.80 THEN 'Excellent Service (80%+)'
            WHEN ServiceGrade >= 0.70 THEN 'Good Service (70-80%)'
            WHEN ServiceGrade >= 0.60 THEN 'Fair Service (60-70%)'
            ELSE 'Poor Service (<60%)'
        END AS ServiceQualityLevel
    FROM DailyIssueMetrics
),
IssueAnalysisByFactors AS (
    SELECT
        Shift,
        WageType,
        IssueSeverityLevel,
        ResolutionSpeedCategory,
        ServiceQualityLevel,
        COUNT(*) AS ObservationCount,
        ROUND(AVG(IssuesRaised), 2) AS AvgIssuesRaised,
        ROUND(AVG(IssueRate), 2) AS AvgIssueRate,
        ROUND(AVG(AverageTimePerIssue), 2) AS AvgResolutionTime,
        ROUND(AVG(ServiceGrade), 4) AS AvgServiceGrade,
        ROUND(AVG(TotalOperators), 2) AS AvgOperators,
        ROUND(AVG(SeniorOperatorPct), 2) AS AvgSeniorPct,
        ROUND(AVG(CallsPerOperator), 2) AS AvgCallsPerOperator,
        ROUND(AVG(AutoResponseRate), 2) AS AvgAutoResponseRate,
        ROUND(AVG(Calls), 2) AS AvgCalls,
        -- Statistical measures
        ROUND(STDDEV(IssueRate), 2) AS StdDevIssueRate,
        ROUND(MIN(IssueRate), 2) AS MinIssueRate,
        ROUND(MAX(IssueRate), 2) AS MaxIssueRate,
        ROUND(MIN(AverageTimePerIssue), 2) AS MinResolutionTime,
        ROUND(MAX(AverageTimePerIssue), 2) AS MaxResolutionTime
    FROM IssueSegmentation
    GROUP BY Shift, WageType, IssueSeverityLevel, ResolutionSpeedCategory, ServiceQualityLevel
),
CorrelationAnalysis AS (
    SELECT
        'Staffing Level Impact' AS AnalysisDimension,
        CASE
            WHEN TotalOperators <= 10 THEN 'Low Staffing (<=10)'
            WHEN TotalOperators <= 15 THEN 'Medium Staffing (11-15)'
            ELSE 'High Staffing (16+)'
        END AS Segment,
        COUNT(*) AS ObservationCount,
        ROUND(AVG(IssueRate), 2) AS AvgIssueRate,
        ROUND(AVG(AverageTimePerIssue), 2) AS AvgResolutionTime,
        ROUND(AVG(ServiceGrade), 4) AS AvgServiceGrade
    FROM DailyIssueMetrics
    GROUP BY
        CASE
            WHEN TotalOperators <= 10 THEN 'Low Staffing (<=10)'
            WHEN TotalOperators <= 15 THEN 'Medium Staffing (11-15)'
            ELSE 'High Staffing (16+)'
        END

    UNION ALL

    SELECT
        'Senior Operator Mix Impact' AS AnalysisDimension,
        CASE
            WHEN SeniorOperatorPct < 25 THEN 'Low Senior Mix (<25%)'
            WHEN SeniorOperatorPct < 40 THEN 'Medium Senior Mix (25-40%)'
            ELSE 'High Senior Mix (40%+)'
        END AS Segment,
        COUNT(*) AS ObservationCount,
        ROUND(AVG(IssueRate), 2) AS AvgIssueRate,
        ROUND(AVG(AverageTimePerIssue), 2) AS AvgResolutionTime,
        ROUND(AVG(ServiceGrade), 4) AS AvgServiceGrade
    FROM DailyIssueMetrics
    GROUP BY
        CASE
            WHEN SeniorOperatorPct < 25 THEN 'Low Senior Mix (<25%)'
            WHEN SeniorOperatorPct < 40 THEN 'Medium Senior Mix (25-40%)'
            ELSE 'High Senior Mix (40%+)'
        END

    UNION ALL

    SELECT
        'Workload Impact' AS AnalysisDimension,
        CASE
            WHEN CallsPerOperator < 75 THEN 'Light Load (<75)'
            WHEN CallsPerOperator < 125 THEN 'Normal Load (75-125)'
            ELSE 'Heavy Load (125+)'
        END AS Segment,
        COUNT(*) AS ObservationCount,
        ROUND(AVG(IssueRate), 2) AS AvgIssueRate,
        ROUND(AVG(AverageTimePerIssue), 2) AS AvgResolutionTime,
        ROUND(AVG(ServiceGrade), 4) AS AvgServiceGrade
    FROM DailyIssueMetrics
    GROUP BY
        CASE
            WHEN CallsPerOperator < 75 THEN 'Light Load (<75)'
            WHEN CallsPerOperator < 125 THEN 'Normal Load (75-125)'
            ELSE 'Heavy Load (125+)'
        END
)
SELECT
    'Detailed Issue Analysis' AS ReportSection,
    Shift,
    WageType,
    IssueSeverityLevel,
    ResolutionSpeedCategory,
    ServiceQualityLevel,
    ObservationCount,
    AvgIssuesRaised,
    AvgIssueRate,
    AvgResolutionTime,
    AvgServiceGrade,
    AvgOperators,
    AvgSeniorPct,
    AvgCallsPerOperator,
    StdDevIssueRate,
    NULL AS AnalysisDimension,
    NULL AS Segment
FROM IssueAnalysisByFactors
WHERE ObservationCount >= 5

UNION ALL

SELECT
    'Correlation Analysis' AS ReportSection,
    NULL AS Shift,
    NULL AS WageType,
    NULL AS IssueSeverityLevel,
    NULL AS ResolutionSpeedCategory,
    NULL AS ServiceQualityLevel,
    ObservationCount,
    NULL AS AvgIssuesRaised,
    AvgIssueRate,
    AvgResolutionTime,
    AvgServiceGrade,
    NULL AS AvgOperators,
    NULL AS AvgSeniorPct,
    NULL AS AvgCallsPerOperator,
    NULL AS StdDevIssueRate,
    AnalysisDimension,
    Segment
FROM CorrelationAnalysis

ORDER BY ReportSection, AvgIssueRate DESC;
```

---

# Business Question 5: Call-to-Order Conversion Funnel and Revenue Impact Analysis

## Intent

Analyze the end-to-end conversion funnel from calls to orders, identifying bottlenecks and optimization opportunities. This comprehensive analysis provides:
- Overall conversion rates across various operational dimensions
- Impact of call handling methods (human vs. automatic response) on conversion
- Identification of high-converting vs. low-converting scenarios
- Factors that influence successful order placement
- Estimated revenue impact of conversion rate improvements
- A/B test insights for different operational configurations
- ROI analysis for operational improvements

Understanding conversion dynamics enables targeted interventions to maximize order volume, identifies best practices for replication, and quantifies the business impact of operational changes.

## SQL Code

```sql
WITH DailyConversionMetrics AS (
    SELECT
        dd.FullDateAlternateKey AS Date,
        dd.CalendarYear,
        dd.CalendarQuarter,
        dd.MonthNumberOfYear,
        dd.EnglishMonthName AS MonthName,
        dd.EnglishDayNameOfWeek AS DayOfWeek,
        fcc.Shift,
        fcc.WageType,
        fcc.TotalOperators,
        fcc.LevelOneOperators,
        fcc.LevelTwoOperators,
        fcc.Calls,
        fcc.AutomaticResponses,
        fcc.Orders,
        fcc.IssuesRaised,
        fcc.ServiceGrade,
        -- Conversion funnel metrics
        fcc.Calls AS FunnelTop,
        fcc.Calls - fcc.AutomaticResponses AS HumanHandledCalls,
        fcc.Orders AS FunnelBottom,
        ROUND(CAST(fcc.Orders AS FLOAT) / NULLIF(fcc.Calls, 0) * 100, 2) AS OverallConversionRate,
        ROUND(CAST(fcc.Orders AS FLOAT) / NULLIF(fcc.Calls - fcc.AutomaticResponses, 0) * 100, 2) AS HumanHandledConversionRate,
        ROUND(CAST(fcc.AutomaticResponses AS FLOAT) / NULLIF(fcc.Calls, 0) * 100, 2) AS AutomationRate,
        ROUND(CAST(fcc.IssuesRaised AS FLOAT) / NULLIF(fcc.Calls, 0) * 100, 2) AS IssueRate,
        ROUND(CAST(fcc.Calls AS FLOAT) / NULLIF(fcc.TotalOperators, 0), 2) AS CallsPerOperator,
        ROUND(CAST(fcc.Orders AS FLOAT) / NULLIF(fcc.TotalOperators, 0), 2) AS OrdersPerOperator,
        ROUND(CAST(fcc.LevelTwoOperators AS FLOAT) / NULLIF(fcc.TotalOperators, 0) * 100, 2) AS SeniorOperatorPct
    FROM FactCallCenter fcc
    INNER JOIN DimDate dd ON fcc.DateKey = dd.DateKey
),
ConversionSegmentation AS (
    SELECT
        *,
        CASE
            WHEN OverallConversionRate < 5 THEN 'Very Low (<5%)'
            WHEN OverallConversionRate < 10 THEN 'Low (5-10%)'
            WHEN OverallConversionRate < 15 THEN 'Medium (10-15%)'
            WHEN OverallConversionRate < 20 THEN 'Good (15-20%)'
            ELSE 'Excellent (20%+)'
        END AS ConversionTier,
        CASE
            WHEN ServiceGrade >= 0.75 THEN 'High Quality (75%+)'
            WHEN ServiceGrade >= 0.65 THEN 'Medium Quality (65-75%)'
            ELSE 'Low Quality (<65%)'
        END AS QualityTier,
        CASE
            WHEN AutomationRate < 30 THEN 'Low Auto (<30%)'
            WHEN AutomationRate < 50 THEN 'Medium Auto (30-50%)'
            ELSE 'High Auto (50%+)'
        END AS AutomationTier
    FROM DailyConversionMetrics
),
ConversionAnalysis AS (
    SELECT
        Shift,
        WageType,
        ConversionTier,
        QualityTier,
        AutomationTier,
        COUNT(*) AS ObservationCount,
        SUM(Calls) AS TotalCalls,
        SUM(HumanHandledCalls) AS TotalHumanHandledCalls,
        SUM(Orders) AS TotalOrders,
        ROUND(AVG(OverallConversionRate), 2) AS AvgOverallConversionRate,
        ROUND(AVG(HumanHandledConversionRate), 2) AS AvgHumanConversionRate,
        ROUND(AVG(AutomationRate), 2) AS AvgAutomationRate,
        ROUND(AVG(ServiceGrade), 4) AS AvgServiceGrade,
        ROUND(AVG(IssueRate), 2) AS AvgIssueRate,
        ROUND(AVG(OrdersPerOperator), 2) AS AvgOrdersPerOperator,
        ROUND(AVG(SeniorOperatorPct), 2) AS AvgSeniorOperatorPct,
        -- Variability metrics
        ROUND(STDDEV(OverallConversionRate), 2) AS StdDevConversionRate,
        ROUND(MIN(OverallConversionRate), 2) AS MinConversionRate,
        ROUND(MAX(OverallConversionRate), 2) AS MaxConversionRate
    FROM ConversionSegmentation
    GROUP BY Shift, WageType, ConversionTier, QualityTier, AutomationTier
),
MonthlyConversionTrends AS (
    SELECT
        CalendarYear,
        MonthNumberOfYear,
        MonthName,
        SUM(Calls) AS MonthlyCalls,
        SUM(Orders) AS MonthlyOrders,
        ROUND(CAST(SUM(Orders) AS FLOAT) / NULLIF(SUM(Calls), 0) * 100, 2) AS MonthlyConversionRate,
        LAG(ROUND(CAST(SUM(Orders) AS FLOAT) / NULLIF(SUM(Calls), 0) * 100, 2), 1)
            OVER (ORDER BY CalendarYear, MonthNumberOfYear) AS PrevMonthConversionRate,
        AVG(ServiceGrade) AS AvgServiceGrade
    FROM DailyConversionMetrics
    GROUP BY CalendarYear, MonthNumberOfYear, MonthName
),
ImpactProjections AS (
    SELECT
        Shift,
        WageType,
        ConversionTier,
        TotalCalls,
        TotalOrders,
        AvgOverallConversionRate,
        AvgServiceGrade,
        -- Project impact of 1% conversion improvement
        ROUND(TotalCalls * 0.01, 0) AS AdditionalOrdersFrom1PctImprovement,
        -- Benchmark gap to top performers
        (SELECT MAX(AvgOverallConversionRate) FROM ConversionAnalysis) AS BestConversionRate,
        ROUND((SELECT MAX(AvgOverallConversionRate) FROM ConversionAnalysis) - AvgOverallConversionRate, 2) AS GapToBest,
        ROUND(TotalCalls * ((SELECT MAX(AvgOverallConversionRate) FROM ConversionAnalysis) - AvgOverallConversionRate) / 100, 0) AS PotentialAdditionalOrders
    FROM ConversionAnalysis
    WHERE ObservationCount >= 10
)
SELECT
    'Conversion by Operational Factors' AS ReportSection,
    Shift,
    WageType,
    ConversionTier,
    QualityTier,
    AutomationTier,
    ObservationCount,
    TotalCalls,
    TotalOrders,
    AvgOverallConversionRate,
    AvgHumanConversionRate,
    AvgAutomationRate,
    AvgServiceGrade,
    AvgIssueRate,
    AvgOrdersPerOperator,
    StdDevConversionRate,
    MinConversionRate,
    MaxConversionRate,
    NULL AS MonthlyCalls,
    NULL AS MonthlyConversionRate,
    NULL AS PrevMonthConversionRate,
    NULL AS AdditionalOrdersFrom1PctImprovement,
    NULL AS GapToBest,
    NULL AS PotentialAdditionalOrders
FROM ConversionAnalysis
WHERE ObservationCount >= 5

UNION ALL

SELECT
    'Monthly Conversion Trends' AS ReportSection,
    NULL AS Shift,
    NULL AS WageType,
    NULL AS ConversionTier,
    NULL AS QualityTier,
    NULL AS AutomationTier,
    NULL AS ObservationCount,
    NULL AS TotalCalls,
    NULL AS TotalOrders,
    NULL AS AvgOverallConversionRate,
    NULL AS AvgHumanConversionRate,
    NULL AS AvgAutomationRate,
    ROUND(AvgServiceGrade, 4) AS AvgServiceGrade,
    NULL AS AvgIssueRate,
    NULL AS AvgOrdersPerOperator,
    NULL AS StdDevConversionRate,
    NULL AS MinConversionRate,
    NULL AS MaxConversionRate,
    MonthlyCalls,
    MonthlyConversionRate,
    PrevMonthConversionRate,
    NULL AS AdditionalOrdersFrom1PctImprovement,
    NULL AS GapToBest,
    NULL AS PotentialAdditionalOrders
FROM MonthlyConversionTrends

UNION ALL

SELECT
    'Improvement Impact Projections' AS ReportSection,
    Shift,
    WageType,
    ConversionTier,
    NULL AS QualityTier,
    NULL AS AutomationTier,
    NULL AS ObservationCount,
    TotalCalls,
    TotalOrders,
    AvgOverallConversionRate,
    NULL AS AvgHumanConversionRate,
    NULL AS AvgAutomationRate,
    AvgServiceGrade,
    NULL AS AvgIssueRate,
    NULL AS AvgOrdersPerOperator,
    NULL AS StdDevConversionRate,
    NULL AS MinConversionRate,
    NULL AS MaxConversionRate,
    NULL AS MonthlyCalls,
    NULL AS MonthlyConversionRate,
    NULL AS PrevMonthConversionRate,
    AdditionalOrdersFrom1PctImprovement,
    GapToBest,
    PotentialAdditionalOrders
FROM ImpactProjections

ORDER BY ReportSection, AvgOverallConversionRate DESC NULLS LAST;
```

---

## Summary

These five business questions provide a comprehensive framework for call center performance analysis:

1. **Shift Performance Comparison** - Identifying optimal staffing patterns and productivity variations across AM/PM/Graveyard shifts
2. **Operator Staffing Impact** - Understanding the relationship between staffing levels, operator mix, and performance outcomes
3. **Temporal Trends** - Analyzing seasonality, day-of-week patterns, and long-term trends for forecasting
4. **Issue Resolution Efficiency** - Evaluating quality of issue handling and identifying improvement opportunities
5. **Conversion Funnel Analysis** - Optimizing call-to-order conversion and quantifying revenue impact

Each query demonstrates advanced analytical techniques including:
- Complex CTEs for multi-stage analysis
- Window functions (LAG, RANK, moving averages)
- Correlation analysis across multiple dimensions
- Statistical measures (standard deviation, percentiles)
- Segmentation and bucketing strategies
- Performance scoring and ranking
- Trend analysis with MoM and YoY comparisons
- Impact projections and ROI calculations

These analyses enable data-driven decisions for:
- Workforce optimization and scheduling
- Training and quality improvement programs
- Resource allocation across shifts
- Performance benchmarking and goal setting
- Process improvement initiatives
- Revenue optimization through conversion improvements
- Capacity planning and demand forecasting

The insights derived from these queries provide actionable intelligence for call center management, operational excellence, and strategic planning to enhance both customer experience and business outcomes.
