# Churn Risk Prediction & Retention Prioritization - KPI Documentation

This document provides a comprehensive analysis of all Key Performance Indicators (KPIs) calculated in the churn risk prediction and retention prioritization SQL query. The query uses multiple risk factors to predict customer churn and prioritize retention investments.

---

# KPI 1: FirstPurchaseDate

## Definition
**FirstPurchaseDate** identifies the date of a customer's first purchase, establishing the beginning of the customer relationship timeline.

**SQL Expression:**
```sql
MIN(fis.OrderDate) AS FirstPurchaseDate
```

**Mathematical Formula:**
$$\text{FirstPurchaseDate} = \min_{i}(\text{OrderDate}_i)$$

**Business Purpose:** Establishes customer tenure baseline and enables cohort analysis.

## Examples
- Customer A: First purchase 2020-03-15 → ~4 year tenure if analyzed 2024-03
- Customer B: First purchase 2023-11-20 → recent customer, <6 months tenure
- Customer C: First purchase 2018-01-10 → veteran customer, 6+ years tenure

---

# KPI 2: LastPurchaseDate

## Definition
**LastPurchaseDate** identifies the date of a customer's most recent purchase, critical for recency analysis and churn risk assessment.

**SQL Expression:**
```sql
MAX(fis.OrderDate) AS LastPurchaseDate
```

**Mathematical Formula:**
$$\text{LastPurchaseDate} = \max_{i}(\text{OrderDate}_i)$$

**Business Purpose:** Primary input for churn risk calculation. Recent purchases indicate active engagement; old last purchase dates signal churn risk.

## Examples
- Customer A: Last purchase 2024-03-10 (15 days ago) → active
- Customer B: Last purchase 2023-09-15 (6 months ago) → at risk
- Customer C: Last purchase 2022-01-20 (2+ years ago) → likely churned

---

# KPI 3: TotalOrders

## Definition
**TotalOrders** counts the total number of distinct orders placed by a customer over their lifetime, measuring purchase frequency and engagement depth.

**SQL Expression:**
```sql
COUNT(DISTINCT fis.SalesOrderNumber) AS TotalOrders
```

**Mathematical Formula:**
$$\text{TotalOrders} = |\{\text{SalesOrderNumber}_i : i \in \text{all transactions}\}|$$

**Business Purpose:** Low order counts combined with long tenure indicate low engagement, a churn risk factor.

## Examples
- Customer A: 2 orders over 3 years → low engagement risk
- Customer B: 30 orders over 2 years → highly engaged
- Customer C: 1 order ever → one-time buyer, churn candidate

---

# KPI 4: DaysSinceLastPurchase

## Definition
**DaysSinceLastPurchase** calculates the number of days from the customer's last purchase to the current date, the primary recency metric for churn risk.

**SQL Expression:**
```sql
(CURRENT_DATE - MAX(fis.OrderDate)::DATE) AS DaysSinceLastPurchase
```

**Mathematical Formula:**
$$\text{DaysSinceLastPurchase} = \text{CURRENT\_DATE} - \text{LastPurchaseDate}$$

**Business Purpose:** Core input for RecencyRiskScore. Compared against customer's normal purchase cycle to detect abnormal delays.

## Examples
- Customer normally orders every 30 days, last purchase 90 days ago → 3x normal cycle, high risk
- Customer normally orders every 60 days, last purchase 45 days ago → within normal range, low risk
- Customer last purchased 400 days ago → extremely high risk

---

# KPI 5: CustomerTenureDays

## Definition
**CustomerTenureDays** measures the span of days between a customer's first and last purchase, representing the duration of their active purchasing period.

**SQL Expression:**
```sql
(MAX(fis.OrderDate)::DATE - MIN(fis.OrderDate)::DATE) AS CustomerTenureDays
```

**Mathematical Formula:**
$$\text{CustomerTenureDays} = \text{LastPurchaseDate} - \text{FirstPurchaseDate}$$

**Business Purpose:** Contextualizes engagement. Low orders over long tenure indicates disengagement risk.

## Examples
- Customer A: 5 orders over 1825 days (5 years) → 0.27% activity rate, low engagement
- Customer B: 50 orders over 730 days (2 years) → 6.8% activity rate, high engagement
- Customer C: 1 order over 0 days → new single-purchase customer

---

# KPI 6: AvgDaysBetweenOrders

## Definition
**AvgDaysBetweenOrders** calculates the typical number of days between consecutive orders, establishing the customer's natural purchase cycle baseline.

**SQL Expression:**
```sql
ROUND(CAST((MAX(fis.OrderDate)::DATE - MIN(fis.OrderDate)::DATE) AS DOUBLE) / NULLIF(COUNT(DISTINCT fis.SalesOrderNumber) - 1, 0), 2) AS AvgDaysBetweenOrders
```

**Mathematical Formula:**
$$\text{AvgDaysBetweenOrders} = \frac{\text{CustomerTenureDays}}{\text{TotalOrders} - 1}$$

For $n$ orders spanning a time period, there are $n-1$ intervals.

**Business Purpose:** Critical baseline for RecencyRiskScore. DaysSinceLastPurchase is compared against this to detect abnormal delays.

## Examples
- Customer A: 365 days tenure, 13 orders → 365/(13-1) = 30.4 days average
  - If last purchase was 90 days ago, that's 3x normal → high risk
- Customer B: 730 days tenure, 25 orders → 730/(25-1) = 30.4 days average
  - If last purchase was 40 days ago, that's 1.3x normal → moderate risk
- Customer C: Single order → NULL (no interval data)

---

# KPI 7: LifetimeRevenue

## Definition
**LifetimeRevenue** sums all sales amounts across all customer purchases, representing total monetary contribution.

**SQL Expression:**
```sql
ROUND(SUM(fis.SalesAmount), 2) AS LifetimeRevenue
```

**Mathematical Formula:**
$$\text{LifetimeRevenue} = \sum_{i=1}^{n} \text{SalesAmount}_i$$

**Business Purpose:** Primary value metric. High-value customers at risk justify higher retention investments.

## Examples
- Customer A: $75,000 lifetime revenue → high-value, justify aggressive retention
- Customer B: $5,000 lifetime revenue → moderate-value
- Customer C: $500 lifetime revenue → low-value, minimal retention investment

---

# KPI 8: LifetimeGrossProfit

## Definition
**LifetimeGrossProfit** calculates total gross profit (revenue minus product costs) generated by the customer, representing true margin contribution.

**SQL Expression:**
```sql
ROUND(SUM(fis.SalesAmount - fis.TotalProductCost), 2) AS LifetimeGrossProfit
```

**Mathematical Formula:**
$$\text{LifetimeGrossProfit} = \sum_{i=1}^{n} (\text{SalesAmount}_i - \text{TotalProductCost}_i)$$

**Business Purpose:** More accurate value assessment than revenue. Determines economically justified retention spend.

## Examples
- Customer A: $75,000 revenue, $30,000 profit (40% margin)
- Customer B: $50,000 revenue, $5,000 profit (10% margin, low-margin buyer)
- Retention investment should be based on profit, not revenue

---

# KPI 9: AvgTransactionValue

## Definition
**AvgTransactionValue** calculates the mean sales amount per transaction line item, indicating typical purchase size.

**SQL Expression:**
```sql
ROUND(AVG(fis.SalesAmount), 2) AS AvgTransactionValue
```

**Mathematical Formula:**
$$\text{AvgTransactionValue} = \frac{1}{n}\sum_{i=1}^{n} \text{SalesAmount}_i$$

**Business Purpose:** Characterizes spending patterns. Helps tailor retention offers to customer's typical spend level.

## Examples
- Customer A: $250 average → premium buyer, offer high-value incentives
- Customer B: $50 average → value buyer, offer percentage discounts
- Customer C: $15 average → discount buyer, offer bundle deals

---

# KPI 10: TotalDiscounts

## Definition
**TotalDiscounts** sums all discount amounts applied to a customer's purchases over their lifetime, indicating price sensitivity and promotional dependency.

**SQL Expression:**
```sql
ROUND(SUM(fis.DiscountAmount), 2) AS TotalDiscounts
```

**Mathematical Formula:**
$$\text{TotalDiscounts} = \sum_{i=1}^{n} \text{DiscountAmount}_i$$

**Business Purpose:** Identifies discount-dependent customers. Informs retention offer design (discount-driven vs. value-driven).

## Examples
- Customer A: $5,000 discounts on $25,000 revenue → 20% discount rate, promotion-driven
- Customer B: $500 discounts on $25,000 revenue → 2% discount rate, full-price buyer
- Customer C: $15,000 discounts on $20,000 revenue → 75% discount rate, extreme dependency

---

# KPI 11: OrdersLast90Days

## Definition
**OrdersLast90Days** counts the number of distinct orders placed in the most recent 90-day period, measuring current activity level.

**SQL Expression:**
```sql
COUNT(DISTINCT CASE WHEN (CURRENT_DATE - fis.OrderDate::DATE) <= 90 THEN fis.SalesOrderNumber END) AS OrdersLast90Days
```

**Mathematical Formula:**
$$\text{OrdersLast90Days} = |\{o : \text{CURRENT\_DATE} - \text{OrderDate}(o) \leq 90\}|$$

**Business Purpose:** Recent activity indicator. Compared with OrdersPrevious90Days to detect activity decline.

## Examples
- Customer A: 8 orders in last 90 days → very active
- Customer B: 2 orders in last 90 days → moderately active
- Customer C: 0 orders in last 90 days → inactive, risk signal

---

# KPI 12: OrdersPrevious90Days

## Definition
**OrdersPrevious90Days** counts orders placed in the 90-day period prior to the last 90 days (days 91-180 ago), providing a historical activity baseline for trend comparison.

**SQL Expression:**
```sql
COUNT(DISTINCT CASE WHEN (CURRENT_DATE - fis.OrderDate::DATE) BETWEEN 91 AND 180 THEN fis.SalesOrderNumber END) AS OrdersPrevious90Days
```

**Mathematical Formula:**
$$\text{OrdersPrevious90Days} = |\{o : 91 \leq \text{CURRENT\_DATE} - \text{OrderDate}(o) \leq 180\}|$$

**Business Purpose:** Baseline for detecting activity decline. Enables trend analysis (increasing, stable, declining).

## Examples
- Customer A: Previous period 10 orders, last period 8 orders → slight decline
- Customer B: Previous period 5 orders, last period 10 orders → growth (healthy)
- Customer C: Previous period 8 orders, last period 0 orders → sharp decline (critical risk)

---

# KPI 13: RevenueLast90Days

## Definition
**RevenueLast90Days** sums revenue generated in the most recent 90-day period, measuring current monetary contribution.

**SQL Expression:**
```sql
ROUND(SUM(CASE WHEN (CURRENT_DATE - fis.OrderDate::DATE) <= 90 THEN fis.SalesAmount ELSE 0 END), 2) AS RevenueLast90Days
```

**Mathematical Formula:**
$$\text{RevenueLast90Days} = \sum_{i : \text{age}(i) \leq 90} \text{SalesAmount}_i$$

where $\text{age}(i) = \text{CURRENT\_DATE} - \text{OrderDate}_i$.

**Business Purpose:** Recent value contribution. Compared with previous period to detect revenue decline, a churn risk signal.

## Examples
- Customer A: $12,000 in last 90 days → high recent value
- Customer B: $1,500 in last 90 days → moderate recent value
- Customer C: $0 in last 90 days → no recent revenue, high risk

---

# KPI 14: RevenuePrevious90Days

## Definition
**RevenuePrevious90Days** sums revenue from the prior 90-day period (days 91-180 ago), providing a historical revenue baseline for trend comparison.

**SQL Expression:**
```sql
ROUND(SUM(CASE WHEN (CURRENT_DATE - fis.OrderDate::DATE) BETWEEN 91 AND 180 THEN fis.SalesAmount ELSE 0 END), 2) AS RevenuePrevious90Days
```

**Mathematical Formula:**
$$\text{RevenuePrevious90Days} = \sum_{i : 91 \leq \text{age}(i) \leq 180} \text{SalesAmount}_i$$

**Business Purpose:** Baseline for revenue trend analysis. Detects revenue decline independent of order count changes.

## Examples
- **Scenario A - Sharp Decline:**
  - Previous: $10,000, Last: $1,000 → 90% decline, critical risk
- **Scenario B - Growth:**
  - Previous: $5,000, Last: $8,000 → 60% growth, healthy
- **Scenario C - Complete Stop:**
  - Previous: $8,000, Last: $0 → 100% decline, critical risk

---

# KPI 15: CustomerTenureYears

## Definition
**CustomerTenureYears** converts CustomerTenureDays into years for more intuitive understanding of customer relationship duration.

**SQL Expression:**
```sql
ROUND(cpm.CustomerTenureDays / 365.25, 2) AS CustomerTenureYears
```

**Mathematical Formula:**
$$\text{CustomerTenureYears} = \frac{\text{CustomerTenureDays}}{365.25}$$

**Business Purpose:** Human-readable tenure metric. Used to calculate annualized value metrics and contextualize engagement levels.

## Examples
- 1095 days → 3.00 years
- 730 days → 2.00 years
- 90 days → 0.25 years (3 months, new customer)

---

# KPI 16: RecencyRiskScore

## Definition
**RecencyRiskScore** quantifies churn risk based on how long it's been since the last purchase relative to the customer's normal purchase cycle. Scores range from 0 (no risk) to 35 (maximum risk), contributing up to 35% of total churn risk.

**SQL Expression:**
```sql
CASE
    WHEN cpm.DaysSinceLastPurchase > cpm.AvgDaysBetweenOrders * 3 THEN 35
    WHEN cpm.DaysSinceLastPurchase > cpm.AvgDaysBetweenOrders * 2 THEN 25
    WHEN cpm.DaysSinceLastPurchase > cpm.AvgDaysBetweenOrders * 1.5 THEN 15
    WHEN cpm.DaysSinceLastPurchase > cpm.AvgDaysBetweenOrders THEN 5
    ELSE 0
END AS RecencyRiskScore
```

**Mathematical Formula:**
$$\text{RecencyRiskScore} = \begin{cases}
35 & \text{if } \text{DaysSince} > 3 \times \text{AvgCycle} \\
25 & \text{if } 2 \times \text{AvgCycle} < \text{DaysSince} \leq 3 \times \text{AvgCycle} \\
15 & \text{if } 1.5 \times \text{AvgCycle} < \text{DaysSince} \leq 2 \times \text{AvgCycle} \\
5 & \text{if } \text{AvgCycle} < \text{DaysSince} \leq 1.5 \times \text{AvgCycle} \\
0 & \text{if } \text{DaysSince} \leq \text{AvgCycle}
\end{cases}$$

where $\text{DaysSince} = \text{DaysSinceLastPurchase}$ and $\text{AvgCycle} = \text{AvgDaysBetweenOrders}$.

**Risk Levels:**
- **35 points (Critical):** 3x+ overdue - Customer is severely overdue for next purchase
- **25 points (High):** 2-3x overdue - Significantly past normal cycle
- **15 points (Moderate):** 1.5-2x overdue - Starting to delay
- **5 points (Low):** 1-1.5x overdue - Slightly overdue
- **0 points (None):** On schedule or early

**Business Purpose:** Most important churn predictor. Personalizes risk assessment to each customer's behavior pattern rather than using universal thresholds.

## Examples

**Example 1: High-Frequency Buyer**
- AvgDaysBetweenOrders: 15 days (orders every 2 weeks)
- DaysSinceLastPurchase: 50 days
- Ratio: 50/15 = 3.33x
- **RecencyRiskScore: 35** (critical risk)
- Interpretation: Normally orders biweekly, hasn't ordered in 50 days → urgent intervention needed

**Example 2: Monthly Buyer - Moderate Risk**
- AvgDaysBetweenOrders: 30 days
- DaysSinceLastPurchase: 55 days
- Ratio: 55/30 = 1.83x
- **RecencyRiskScore: 15** (moderate risk)
- Interpretation: Normally orders monthly, at 55 days → monitor closely

**Example 3: Quarterly Buyer - On Track**
- AvgDaysBetweenOrders: 90 days
- DaysSinceLastPurchase: 60 days
- Ratio: 60/90 = 0.67x
- **RecencyRiskScore: 0** (no risk)
- Interpretation: Normally orders every 3 months, only been 2 months → healthy

**Example 4: Annual Buyer - High Risk**
- AvgDaysBetweenOrders: 180 days
- DaysSinceLastPurchase: 400 days
- Ratio: 400/180 = 2.22x
- **RecencyRiskScore: 25** (high risk)
- Interpretation: Normally orders every 6 months, hasn't ordered in 13 months → likely churned

---

# KPI 17: ActivityDeclineScore

## Definition
**ActivityDeclineScore** quantifies churn risk based on declining order frequency by comparing recent 90-day activity to the previous 90-day period. Scores range from 0 to 30, contributing up to 30% of total churn risk.

**SQL Expression:**
```sql
CASE
    WHEN rat.OrdersLast90Days = 0 AND rat.OrdersPrevious90Days > 0 THEN 30
    WHEN rat.OrdersLast90Days < rat.OrdersPrevious90Days * 0.5 THEN 20
    WHEN rat.OrdersLast90Days < rat.OrdersPrevious90Days THEN 10
    ELSE 0
END AS ActivityDeclineScore
```

**Mathematical Formula:**
$$\text{ActivityDeclineScore} = \begin{cases}
30 & \text{if } O_{last} = 0 \text{ and } O_{prev} > 0 \\
20 & \text{if } O_{last} < 0.5 \times O_{prev} \\
10 & \text{if } 0.5 \times O_{prev} \leq O_{last} < O_{prev} \\
0 & \text{if } O_{last} \geq O_{prev}
\end{cases}$$

where $O_{last} = \text{OrdersLast90Days}$ and $O_{prev} = \text{OrdersPrevious90Days}$.

**Risk Levels:**
- **30 points (Critical):** Complete activity stop - Was active, now zero orders
- **20 points (Severe):** 50%+ decline - Orders dropped by more than half
- **10 points (Moderate):** Any decline - Some reduction in order frequency
- **0 points (Healthy):** Stable/growing - Activity maintained or increased

**Business Purpose:** Detects behavioral change signaling disengagement. Early warning system before customer becomes completely inactive.

## Examples

**Example 1: Complete Stop (Critical)**
- OrdersPrevious90Days: 8 orders
- OrdersLast90Days: 0 orders
- Change: -100% (complete stop)
- **ActivityDeclineScore: 30**
- Interpretation: Customer went from 8 orders to zero → urgent intervention required

**Example 2: Severe Decline**
- OrdersPrevious90Days: 10 orders
- OrdersLast90Days: 3 orders
- Change: -70% decline (3 is 30% of 10, less than 50% threshold)
- **ActivityDeclineScore: 20**
- Interpretation: Significant drop from 10 to 3 orders → high risk

**Example 3: Moderate Decline**
- OrdersPrevious90Days: 8 orders
- OrdersLast90Days: 6 orders
- Change: -25% decline
- **ActivityDeclineScore: 10**
- Interpretation: Slight reduction → monitor trend

**Example 4: Healthy Growth**
- OrdersPrevious90Days: 5 orders
- OrdersLast90Days: 8 orders
- Change: +60% growth
- **ActivityDeclineScore: 0**
- Interpretation: Increasing engagement → no risk

**Example 5: Stable Activity**
- OrdersPrevious90Days: 6 orders
- OrdersLast90Days: 6 orders
- Change: 0%
- **ActivityDeclineScore: 0**
- Interpretation: Maintained activity level → healthy

---

# KPI 18: RevenueDeclineScore

## Definition
**RevenueDeclineScore** quantifies churn risk based on declining monetary contribution, comparing recent 90-day revenue to the previous 90-day period. Scores range from 0 to 20, contributing up to 20% of total churn risk.

**SQL Expression:**
```sql
CASE
    WHEN rat.RevenueLast90Days = 0 AND rat.RevenuePrevious90Days > 0 THEN 20
    WHEN rat.RevenueLast90Days < rat.RevenuePrevious90Days * 0.5 THEN 15
    WHEN rat.RevenueLast90Days < rat.RevenuePrevious90Days THEN 8
    ELSE 0
END AS RevenueDeclineScore
```

**Mathematical Formula:**
$$\text{RevenueDeclineScore} = \begin{cases}
20 & \text{if } R_{last} = 0 \text{ and } R_{prev} > 0 \\
15 & \text{if } R_{last} < 0.5 \times R_{prev} \\
8 & \text{if } 0.5 \times R_{prev} \leq R_{last} < R_{prev} \\
0 & \text{if } R_{last} \geq R_{prev}
\end{cases}$$

where $R_{last} = \text{RevenueLast90Days}$ and $R_{prev} = \text{RevenuePrevious90Days}$.

**Risk Levels:**
- **20 points (Critical):** Revenue stopped - Was spending, now zero
- **15 points (High):** 50%+ revenue decline - Spending dropped significantly
- **8 points (Moderate):** Any revenue decline - Some reduction in spending
- **0 points (Healthy):** Stable/growing revenue

**Business Purpose:** Detects declining customer value independent of order frequency. A customer might maintain order count but reduce basket size (downgrading).

## Examples

**Example 1: Revenue Stopped**
- RevenuePrevious90Days: $15,000
- RevenueLast90Days: $0
- Change: -100%
- **RevenueDeclineScore: 20**
- Interpretation: Customer stopped spending entirely → critical risk

**Example 2: Severe Decline**
- RevenuePrevious90Days: $20,000
- RevenueLast90Days: $8,000
- Change: -60% (8K is 40% of 20K, below 50% threshold)
- **RevenueDeclineScore: 15**
- Interpretation: Major spending reduction → high risk

**Example 3: Moderate Decline**
- RevenuePrevious90Days: $10,000
- RevenueLast90Days: $7,000
- Change: -30%
- **RevenueDeclineScore: 8**
- Interpretation: Some reduction → monitor

**Example 4: Growth**
- RevenuePrevious90Days: $8,000
- RevenueLast90Days: $12,000
- Change: +50%
- **RevenueDeclineScore: 0**
- Interpretation: Increased spending → healthy

**Scenario: Declining Value Despite Stable Orders**
- OrdersPrevious90Days: 10, OrdersLast90Days: 10 (stable)
- RevenuePrevious90Days: $10,000 ($1,000/order)
- RevenueLast90Days: $4,000 ($400/order)
- ActivityDeclineScore: 0 (orders stable)
- **RevenueDeclineScore: 15** (revenue declined 60%)
- Interpretation: Customer downgrading purchases - buying cheaper items or smaller quantities → risk signal

---

# KPI 19: LowEngagementScore

## Definition
**LowEngagementScore** quantifies churn risk based on low lifetime order count relative to customer tenure, identifying customers who never developed strong engagement. Scores range from 0 to 15, contributing up to 15% of total churn risk.

**SQL Expression:**
```sql
CASE
    WHEN cpm.TotalOrders <= 2 AND cpm.CustomerTenureDays > 365 THEN 15
    WHEN cpm.TotalOrders <= 3 AND cpm.CustomerTenureDays > 180 THEN 10
    WHEN cpm.TotalOrders <= 5 THEN 5
    ELSE 0
END AS LowEngagementScore
```

**Mathematical Formula:**
$$\text{LowEngagementScore} = \begin{cases}
15 & \text{if } O \leq 2 \text{ and } T > 365 \\
10 & \text{if } O \leq 3 \text{ and } T > 180 \\
5 & \text{if } O \leq 5 \\
0 & \text{if } O > 5
\end{cases}$$

where $O = \text{TotalOrders}$ and $T = \text{CustomerTenureDays}$.

**Risk Levels:**
- **15 points (Critical):** ≤2 orders over >1 year - Long-term non-engager
- **10 points (High):** ≤3 orders over >6 months - Failed to develop habit
- **5 points (Moderate):** ≤5 orders total - Low engagement
- **0 points (Healthy):** 6+ orders - Established pattern

**Business Purpose:** Identifies customers who never formed a purchasing habit. Different from recency/decline risks—these customers were never highly engaged.

## Examples

**Example 1: Long-Term Non-Engager**
- TotalOrders: 2
- CustomerTenureDays: 1095 (3 years)
- **LowEngagementScore: 15**
- Interpretation: Only 2 orders in 3 years → never developed loyalty, high churn risk
- Profile: Tried product, made one repeat purchase, didn't stick

**Example 2: New Customer Failed Onboarding**
- TotalOrders: 3
- CustomerTenureDays: 200 days (6.5 months)
- **LowEngagementScore: 10**
- Interpretation: Only 3 orders in 6+ months → onboarding failure
- Profile: Initial interest didn't convert to habit

**Example 3: Very Low Engagement**
- TotalOrders: 4
- CustomerTenureDays: 90 days
- **LowEngagementScore: 5**
- Interpretation: Few orders overall → early-stage low engagement
- Profile: Needs nurturing to increase frequency

**Example 4: Established Customer**
- TotalOrders: 25
- CustomerTenureDays: 730 days (2 years)
- **LowEngagementScore: 0**
- Interpretation: Strong engagement pattern → no risk from this factor
- Profile: Regular buyer, established habit

**Example 5: Edge Case - Recent Customer**
- TotalOrders: 2
- CustomerTenureDays: 30 days
- **LowEngagementScore: 15**
- Interpretation: While score is 15, this is a new customer still in evaluation phase
- Note: LowEngagementScore may overstate risk for very new customers; other factors (like recency) will balance it

---

# KPI 20: TotalChurnRiskScore

## Definition
**TotalChurnRiskScore** combines all four churn risk factors into a single composite score ranging from 0 to 100, providing an overall churn risk assessment.

**SQL Expression:**
```sql
crf.RecencyRiskScore + crf.ActivityDeclineScore + crf.RevenueDeclineScore + crf.LowEngagementScore AS TotalChurnRiskScore
```

**Mathematical Formula:**
$$\text{TotalChurnRiskScore} = R_{recency} + R_{activity} + R_{revenue} + R_{engagement}$$

where:
- $R_{recency} \in [0, 35]$ (35% weight)
- $R_{activity} \in [0, 30]$ (30% weight)
- $R_{revenue} \in [0, 20]$ (20% weight)
- $R_{engagement} \in [0, 15]$ (15% weight)

**Total Range:** 0 to 100

**Weighting Rationale:**
- **Recency (35%):** Most predictive single factor
- **Activity Decline (30%):** Strong behavioral signal
- **Revenue Decline (20%):** Economic impact indicator
- **Low Engagement (15%):** Structural risk factor

**Business Purpose:** Single unified churn risk metric for prioritization and intervention triggering.

## Examples

**Example 1: Critical Risk Customer**
- RecencyRiskScore: 35 (3x+ overdue)
- ActivityDeclineScore: 30 (complete stop)
- RevenueDeclineScore: 20 (revenue stopped)
- LowEngagementScore: 10 (historically low engagement)
- **TotalChurnRiskScore: 95** (critical)
- Profile: Customer who was never highly engaged, now completely inactive

**Example 2: High Risk - Recent Decline**
- RecencyRiskScore: 25 (2x overdue)
- ActivityDeclineScore: 20 (50%+ decline)
- RevenueDeclineScore: 15 (severe revenue drop)
- LowEngagementScore: 0 (historically engaged)
- **TotalChurnRiskScore: 60** (high risk)
- Profile: Previously good customer experiencing sharp recent decline

**Example 3: Moderate Risk - Mixed Signals**
- RecencyRiskScore: 15 (1.5x overdue)
- ActivityDeclineScore: 10 (some decline)
- RevenueDeclineScore: 8 (moderate revenue decline)
- LowEngagementScore: 5 (low-moderate engagement)
- **TotalChurnRiskScore: 38** (moderate risk)
- Profile: Customer showing multiple mild warning signs

**Example 4: Low Risk - Single Factor**
- RecencyRiskScore: 5 (slightly overdue)
- ActivityDeclineScore: 0 (stable)
- RevenueDeclineScore: 0 (stable)
- LowEngagementScore: 10 (low engagement but stable)
- **TotalChurnRiskScore: 15** (low risk)
- Profile: Low-frequency customer maintaining their pattern

**Example 5: Healthy Customer**
- RecencyRiskScore: 0 (on schedule)
- ActivityDeclineScore: 0 (growing)
- RevenueDeclineScore: 0 (growing)
- LowEngagementScore: 0 (highly engaged)
- **TotalChurnRiskScore: 0** (healthy)
- Profile: Strong, engaged, growing customer

---

# KPI 21: ChurnRiskCategory

## Definition
**ChurnRiskCategory** translates the TotalChurnRiskScore into descriptive risk categories for easier communication and action triggering.

**SQL Expression:**
```sql
CASE
    WHEN (crf.RecencyRiskScore + crf.ActivityDeclineScore + crf.RevenueDeclineScore + crf.LowEngagementScore) >= 70 THEN 'Critical Risk'
    WHEN (crf.RecencyRiskScore + crf.ActivityDeclineScore + crf.RevenueDeclineScore + crf.LowEngagementScore) >= 50 THEN 'High Risk'
    WHEN (crf.RecencyRiskScore + crf.ActivityDeclineScore + crf.RevenueDeclineScore + crf.LowEngagementScore) >= 30 THEN 'Moderate Risk'
    WHEN (crf.RecencyRiskScore + crf.ActivityDeclineScore + crf.RevenueDeclineScore + crf.LowEngagementScore) >= 15 THEN 'Low Risk'
    ELSE 'Healthy'
END AS ChurnRiskCategory
```

**Mathematical Formula:**
$$\text{ChurnRiskCategory} = \begin{cases}
\text{Critical Risk} & \text{if Score} \geq 70 \\
\text{High Risk} & \text{if } 50 \leq \text{Score} < 70 \\
\text{Moderate Risk} & \text{if } 30 \leq \text{Score} < 50 \\
\text{Low Risk} & \text{if } 15 \leq \text{Score} < 30 \\
\text{Healthy} & \text{if Score} < 15
\end{cases}$$

**Category Definitions:**

### Critical Risk (70-100 points)
**Characteristics:**
- Multiple severe risk factors present
- Likely experiencing 3x+ recency delay AND activity/revenue decline
- Immediate churn imminent without intervention

**Typical Profile:**
- Previously active customer now completely inactive, OR
- Never-engaged customer now completely dormant

**Action Required:** URGENT intervention within 24-48 hours

### High Risk (50-69 points)
**Characteristics:**
- Strong risk signals across multiple factors
- Significant delays, declines, or low engagement
- High probability of churn within 30-60 days

**Typical Profile:**
- Good customer experiencing sharp decline, OR
- Moderate customer with multiple warning signs

**Action Required:** Proactive outreach within 1 week

### Moderate Risk (30-49 points)
**Characteristics:**
- Some risk factors present
- Early warning signs or structural concerns
- Elevated churn probability within 90-180 days

**Typical Profile:**
- Mild delays or declines, OR
- Low-engagement customers maintaining pattern

**Action Required:** Re-engagement campaign within 2 weeks

### Low Risk (15-29 points)
**Characteristics:**
- Minor risk factors only
- Slight delays or low baseline engagement
- Some monitoring warranted

**Typical Profile:**
- Slight deviation from normal pattern, OR
- Inherently low-frequency customers on track

**Action Required:** Standard nurture communication

### Healthy (<15 points)
**Characteristics:**
- No significant risk factors
- Active, engaged, on-schedule
- Growing or maintaining strong patterns

**Typical Profile:**
- Regular purchasers maintaining habits

**Action Required:** Standard customer communication, no special intervention

**Business Purpose:** Enables quick risk assessment and triggers appropriate urgency levels for retention actions.

## Examples

**Example 1: Critical Risk**
- TotalChurnRiskScore: 85
- Category: "Critical Risk"
- Profile: Customer with avg 30-day cycle, last purchased 120 days ago (35 pts), had 8 orders previous period now 0 (30 pts), revenue dropped from $10K to $0 (20 pts)
- Action: Executive outreach within 24 hours

**Example 2: High Risk**
- TotalChurnRiskScore: 55
- Category: "High Risk"
- Profile: Good customer (15 historical orders) showing 2x recency delay (25 pts), 50% activity decline (20 pts), 40% revenue decline (8 pts)
- Action: Personal call/email within 1 week

**Example 3: Moderate Risk**
- TotalChurnRiskScore: 38
- Category: "Moderate Risk"
- Profile: Customer with 1.5x recency delay (15 pts), some order decline (10 pts), some revenue decline (8 pts), low engagement history (5 pts)
- Action: Re-engagement email campaign

**Example 4: Low Risk**
- TotalChurnRiskScore: 20
- Category: "Low Risk"
- Profile: Quarterly buyer slightly overdue (5 pts) with historically low engagement (10 pts) but maintaining revenue (0 pts) and order count (0 pts)
- Action: Standard nurture emails

**Example 5: Healthy**
- TotalChurnRiskScore: 5
- Category: "Healthy"
- Profile: Monthly buyer slightly overdue (5 pts) but otherwise strong metrics
- Action: Continue standard communications

---

# KPI 22: ValueQuartile

## Definition
**ValueQuartile** divides customers into four equal groups based on lifetime revenue, with 1 being the top 25% highest-value customers.

**SQL Expression:**
```sql
NTILE(4) OVER (ORDER BY crf.LifetimeRevenue DESC) AS ValueQuartile
```

**Mathematical Formula:**
$$\text{ValueQuartile} = \text{NTILE}_4(\text{LifetimeRevenue}_{\text{desc}})$$

**Values:** 1, 2, 3, 4
- 1 = Top quartile (top 25%, highest revenue)
- 4 = Bottom quartile (bottom 25%, lowest revenue)

**Business Purpose:** Segments customers by value to calibrate retention investment levels. High-risk customers in ValueQuartile 1 justify the highest retention spend.

## Examples
With 10,000 at-risk customers:
- **Quartile 1**: 2,500 customers, $30M lifetime revenue (~$12K avg) → top priority
- **Quartile 2**: 2,500 customers, $8M lifetime revenue (~$3.2K avg)
- **Quartile 3**: 2,500 customers, $3M lifetime revenue (~$1.2K avg)
- **Quartile 4**: 2,500 customers, $1M lifetime revenue (~$400 avg) → minimal retention investment

---

# KPI 23: ValueTier

## Definition
**ValueTier** translates ValueQuartile into descriptive customer value segments.

**SQL Expression:**
```sql
CASE
    WHEN NTILE(4) OVER (ORDER BY crf.LifetimeRevenue DESC) = 1 THEN 'High Value'
    WHEN NTILE(4) OVER (ORDER BY crf.LifetimeRevenue DESC) = 2 THEN 'Medium-High Value'
    WHEN NTILE(4) OVER (ORDER BY crf.LifetimeRevenue DESC) = 3 THEN 'Medium-Low Value'
    ELSE 'Low Value'
END AS ValueTier
```

**Mathematical Formula:**
$$\text{ValueTier} = \begin{cases}
\text{High Value} & \text{if ValueQuartile} = 1 \\
\text{Medium-High Value} & \text{if ValueQuartile} = 2 \\
\text{Medium-Low Value} & \text{if ValueQuartile} = 3 \\
\text{Low Value} & \text{if ValueQuartile} = 4
\end{cases}$$

**Business Purpose:** Business-friendly labels for value segmentation. Combines with ChurnRiskCategory to determine retention approach.

## Examples
- "High Value" + "Critical Risk" → Maximum retention investment
- "Medium-High Value" + "High Risk" → Significant retention investment
- "Low Value" + "Moderate Risk" → Standard retention efforts

---

# KPI 24: ExpectedAnnualRevenue

## Definition
**ExpectedAnnualRevenue** estimates the annual revenue a customer would generate based on their historical patterns, representing future value at risk of loss.

**SQL Expression:**
```sql
ROUND(crs.LifetimeRevenue / NULLIF(crs.CustomerTenureYears, 0), 2) AS ExpectedAnnualRevenue
```

**Mathematical Formula:**
$$\text{ExpectedAnnualRevenue} = \frac{\text{LifetimeRevenue}}{\text{CustomerTenureYears}}$$

**Business Purpose:** Quantifies annual revenue at risk of churn. Used to calculate economically justified retention investment and Value at Risk metrics.

## Examples
- Customer A: $50,000 lifetime over 5 years → $10,000 expected annual revenue
- Customer B: $12,000 lifetime over 2 years → $6,000 expected annual revenue
- Customer C: $30,000 lifetime over 10 years → $3,000 expected annual revenue

**Note:** Customer B, despite lower total revenue, has higher annual value than Customer C.

---

# KPI 25: TwoYearValueAtRisk

## Definition
**TwoYearValueAtRisk** estimates the total revenue that would be lost over a 2-year period if the customer churns, quantifying the financial impact of churn.

**SQL Expression:**
```sql
ROUND((crs.LifetimeRevenue / NULLIF(crs.CustomerTenureYears, 0)) * 2, 2) AS TwoYearValueAtRisk
```

**Mathematical Formula:**
$$\text{TwoYearValueAtRisk} = \text{ExpectedAnnualRevenue} \times 2$$

$$= \frac{\text{LifetimeRevenue}}{\text{CustomerTenureYears}} \times 2$$

**Business Purpose:** Quantifies the financial opportunity cost of losing a customer. Helps justify retention investment by showing what's at stake over a reasonable time horizon.

## Examples

**Example 1: High-Value Customer**
- LifetimeRevenue: $100,000 over 5 years
- ExpectedAnnualRevenue: $20,000
- **TwoYearValueAtRisk: $40,000**
- Interpretation: Losing this customer costs $40K in revenue over next 2 years
- Justified retention spend: Up to $8,000 (20% of $40K) could be economically justified

**Example 2: Medium-Value Customer**
- LifetimeRevenue: $24,000 over 4 years
- ExpectedAnnualRevenue: $6,000
- **TwoYearValueAtRisk: $12,000**
- Interpretation: $12K at risk
- Justified retention spend: Up to $1,200 (10% of $12K)

**Example 3: Low-Value Customer**
- LifetimeRevenue: $2,000 over 2 years
- ExpectedAnnualRevenue: $1,000
- **TwoYearValueAtRisk: $2,000**
- Interpretation: Only $2K at risk
- Justified retention spend: Up to $200 (10% of $2K), minimal investment

**Why 2 Years?**
- Long enough to capture significant value
- Short enough to be reliable (customer behavior may change beyond 2 years)
- Standard time horizon for CLV calculations
- Practical for business planning cycles

---

# KPI 26: RetentionPriorityScore

## Definition
**RetentionPriorityScore** combines churn risk (60% weight) and customer value (40% weight) into a single prioritization metric, indicating which customers should receive retention attention first.

**SQL Expression:**
```sql
ROUND(
    (crs.TotalChurnRiskScore * 0.6) +
    (crs.ValueQuartile * 10 * 0.4)
, 2) AS RetentionPriorityScore
```

**Mathematical Formula:**
$$\text{RetentionPriorityScore} = 0.6 \times \text{TotalChurnRiskScore} + 0.4 \times (10 \times \text{ValueQuartile})$$

**Components:**
- **Churn Risk (60%):** Urgency factor - how likely to churn
- **Value (40%):** Impact factor - what's at stake if they churn

**Range:**
- Minimum: $0.6 \times 0 + 0.4 \times (10 \times 4) = 16$ (low risk, low value)
- Maximum: $0.6 \times 100 + 0.4 \times (10 \times 1) = 64$ (critical risk, high value)

**Note:** Counter-intuitively, ValueQuartile 1 (highest value) gets score of 10, while Quartile 4 (lowest) gets 40 in the formula as written. This appears to be intentional to create a priority score where higher = higher priority. However, the DESC sort on this score means lower values appear first. Let me recalculate based on the actual intent.

Actually, looking at the ORDER BY: `ORDER BY RetentionPriorityScore DESC` suggests higher scores are higher priority. So the formula creates:
- High risk (100) + High value (Q1=1, so 10) = 60 + 4 = 64 points (highest priority)
- Low risk (0) + Low value (Q4=4, so 40) = 0 + 16 = 16 points (lowest priority)

**Business Purpose:** Single metric to rank ALL at-risk customers for retention resource allocation. Answers: "Which customer should we contact first?"

## Examples

**Example 1: Highest Priority**
- TotalChurnRiskScore: 90 (critical risk)
- ValueQuartile: 1 (top 25%, high value)
- **RetentionPriorityScore: $0.6 \times 90 + 0.4 \times 10 = 54 + 4 = 58$**
- Interpretation: Critical risk + high value = highest priority for immediate intervention

**Example 2: High Priority - High Risk, Medium Value**
- TotalChurnRiskScore: 80 (critical risk)
- ValueQuartile: 2 (medium-high value)
- **RetentionPriorityScore: $0.6 \times 80 + 0.4 \times 20 = 48 + 8 = 56$**
- Interpretation: Very high risk offsets moderate value

**Example 3: Medium Priority - Moderate Risk, High Value**
- TotalChurnRiskScore: 40 (moderate risk)
- ValueQuartile: 1 (high value)
- **RetentionPriorityScore: $0.6 \times 40 + 0.4 \times 10 = 24 + 4 = 28$**
- Interpretation: High value but lower urgency

**Example 4: Lower Priority - High Risk, Low Value**
- TotalChurnRiskScore: 70 (critical risk)
- ValueQuartile: 4 (low value)
- **RetentionPriorityScore: $0.6 \times 70 + 0.4 \times 40 = 42 + 16 = 58$**
- Interpretation: High urgency but low economic impact

**Example 5: Lowest Priority - Low Risk, Low Value**
- TotalChurnRiskScore: 20 (low risk)
- ValueQuartile: 4 (low value)
- **RetentionPriorityScore: $0.6 \times 20 + 0.4 \times 40 = 12 + 16 = 28$**
- Interpretation: Neither urgent nor valuable

**Prioritization Logic:**
The 60/40 weighting means:
- **Urgency matters more (60%):** Prevents critical-risk customers from being ignored
- **Value still matters (40%):** High-value customers get appropriate attention
- **Balance:** Prevents exclusively focusing on high-value OR high-risk alone

---

# KPI 27: RetentionInvestmentRecommendation

## Definition
**RetentionInvestmentRecommendation** provides specific guidance on how much to invest in retaining each customer, expressed as a percentage of their expected annual revenue.

**SQL Expression:**
```sql
CASE
    WHEN crs.ValueTier = 'High Value' AND crs.ChurnRiskCategory IN ('Critical Risk', 'High Risk') THEN 'HIGH: Up to 20% of annual value'
    WHEN crs.ValueTier = 'High Value' AND crs.ChurnRiskCategory = 'Moderate Risk' THEN 'MEDIUM-HIGH: Up to 10% of annual value'
    WHEN crs.ValueTier IN ('High Value', 'Medium-High Value') AND crs.ChurnRiskCategory IN ('Critical Risk', 'High Risk') THEN 'MEDIUM: Up to 15% of annual value'
    WHEN crs.ValueTier = 'Medium-High Value' THEN 'MEDIUM: Up to 8% of annual value'
    WHEN crs.ChurnRiskCategory IN ('Critical Risk', 'High Risk') THEN 'LOW-MEDIUM: Up to 5% of annual value'
    ELSE 'LOW: Standard retention budget'
END AS RetentionInvestmentRecommendation
```

**Investment Guidelines Matrix:**

| Value Tier | Critical/High Risk | Moderate Risk | Low Risk/Healthy |
|------------|-------------------|---------------|------------------|
| High Value | 20% of annual value | 10% of annual value | Standard |
| Medium-High Value | 15% of annual value | 8% of annual value | Standard |
| Medium-Low Value | 5% of annual value | Standard | Standard |
| Low Value | 5% of annual value | Standard | Standard |

**Calculation Examples:**

### HIGH: Up to 20% of annual value
**Criteria:** High Value + (Critical OR High Risk)

**Example:**
- ExpectedAnnualRevenue: $50,000
- **Maximum retention investment: $10,000** (20% of $50K)
- Justified tactics: Executive outreach, premium discounts (30-50%), personalized service recovery, account manager assignment

### MEDIUM-HIGH: Up to 10% of annual value
**Criteria:** High Value + Moderate Risk

**Example:**
- ExpectedAnnualRevenue: $40,000
- **Maximum retention investment: $4,000** (10% of $40K)
- Justified tactics: Personalized campaigns, significant discounts (15-25%), phone outreach

### MEDIUM: Up to 15% of annual value
**Criteria:** (High Value OR Medium-High Value) + (Critical OR High Risk)

**Example:**
- ExpectedAnnualRevenue: $15,000
- **Maximum retention investment: $2,250** (15% of $15K)
- Justified tactics: Targeted campaigns, moderate discounts (10-20%), email/phone mix

### MEDIUM: Up to 8% of annual value
**Criteria:** Medium-High Value (any risk level not covered above)

**Example:**
- ExpectedAnnualRevenue: $10,000
- **Maximum retention investment: $800** (8% of $10K)
- Justified tactics: Automated campaigns with personalization, standard discounts (10-15%)

### LOW-MEDIUM: Up to 5% of annual value
**Criteria:** (Any tier with Critical/High Risk) not covered by higher tiers

**Example:**
- ExpectedAnnualRevenue: $2,000
- **Maximum retention investment: $100** (5% of $2K)
- Justified tactics: Automated campaigns, minimal discounts (5-10%)

### LOW: Standard retention budget
**Criteria:** All others (low value and/or low risk)

**Example:**
- Fixed minimal amount per customer (e.g., $10-20)
- Justified tactics: Mass email campaigns, no special discounts

**Business Purpose:** Provides clear, economically justified spending limits for retention activities. Prevents over-investment in low-value customers or under-investment in high-value ones.

## Examples

**Example 1: Maximum Investment Justified**
- Customer: High Value, Critical Risk
- ExpectedAnnualRevenue: $100,000
- Recommendation: "HIGH: Up to 20% of annual value"
- **Maximum spend: $20,000**
- Tactics: Executive visit, customized solution, 50% discount on next $40K purchase, dedicated account manager for 1 year
- ROI: If 50% retention probability, expected value = $50K, cost = $20K, ROI = 2.5x

**Example 2: Moderate Investment**
- Customer: Medium-High Value, High Risk
- ExpectedAnnualRevenue: $15,000
- Recommendation: "MEDIUM: Up to 15% of annual value"
- **Maximum spend: $2,250**
- Tactics: Personal phone call, 25% discount ($3,750 value to customer), satisfaction survey, 3-month account review
- Budget allocation: $500 labor + $1,750 discount

**Example 3: Minimal Investment**
- Customer: Low Value, High Risk
- ExpectedAnnualRevenue: $1,000
- Recommendation: "LOW-MEDIUM: Up to 5% of annual value"
- **Maximum spend: $50**
- Tactics: Automated win-back email series (3 emails), 10% discount offer
- Budget: Fully automated, negligible labor cost

---

# KPI 28: RetentionAction

## Definition
**RetentionAction** provides specific tactical recommendations for how to approach customer retention based on their risk level and value tier.

**SQL Expression:**
```sql
CASE
    WHEN crs.ChurnRiskCategory = 'Critical Risk' AND crs.ValueTier = 'High Value' THEN 'URGENT: Executive outreach, personalized offer, satisfaction survey'
    WHEN crs.ChurnRiskCategory = 'Critical Risk' THEN 'URGENT: Personal call/email, win-back offer, identify issues'
    WHEN crs.ChurnRiskCategory = 'High Risk' AND crs.ValueTier IN ('High Value', 'Medium-High Value') THEN 'HIGH PRIORITY: Personalized re-engagement, special incentive'
    WHEN crs.ChurnRiskCategory = 'High Risk' THEN 'Re-engagement campaign, limited-time offer'
    WHEN crs.ChurnRiskCategory = 'Moderate Risk' THEN 'Proactive outreach, engagement content, reminder campaign'
    WHEN crs.ChurnRiskCategory = 'Low Risk' THEN 'Standard nurture campaign'
    ELSE 'Continue standard customer communications'
END AS RetentionAction
```

**Action Playbook:**

### URGENT: Executive outreach, personalized offer, satisfaction survey
**Criteria:** Critical Risk + High Value

**Tactics:**
- **Executive involvement:** VP or C-level reach out within 24 hours
- **Personalized offer:** Custom incentive designed for this specific customer (30-50% discount, special terms, product bundle)
- **Satisfaction survey:** In-depth interview to understand issues
- **Service recovery:** Fix any problems immediately
- **Account management:** Assign dedicated manager

**Timeline:** 24-48 hours

**Example:** "Hi [Name], this is [CEO]. I noticed you haven't ordered in a while. I'd like to personally understand any concerns and make things right. Can we schedule 15 minutes this week? As a gesture, here's 40% off your next purchase..."

### URGENT: Personal call/email, win-back offer, identify issues
**Criteria:** Critical Risk (all other value tiers)

**Tactics:**
- **Personal contact:** Account manager or senior sales representative calls/emails within 48 hours
- **Win-back offer:** Significant discount (20-30%) or special bundle
- **Problem identification:** Understand barriers to repurchase
- **Re-engagement:** Clear path back to active status

**Timeline:** 48-72 hours

**Example:** "Hi [Name], I'm your account manager. I noticed you haven't ordered recently and wanted to check in. Is there anything we can improve? Here's 25% off to welcome you back..."

### HIGH PRIORITY: Personalized re-engagement, special incentive
**Criteria:** High Risk + (High Value OR Medium-High Value)

**Tactics:**
- **Personalized campaigns:** Targeted emails addressing customer's specific purchase history
- **Special incentive:** 15-25% discount or exclusive offer
- **Multiple touchpoints:** 3-4 contacts over 2 weeks (email, retargeting ads, possible call)
- **Product recommendations:** Based on past purchases

**Timeline:** 1 week

**Example:** "Hi [Name], we miss you! Based on your past purchases of [products], we thought you'd love [new products]. Here's an exclusive 20% discount just for you..."

### Re-engagement campaign, limited-time offer
**Criteria:** High Risk (lower value tiers)

**Tactics:**
- **Automated campaigns:** 2-3 email sequence over 2 weeks
- **Limited-time offer:** 10-15% discount with deadline
- **Social proof:** Highlight popular products or reviews
- **Urgency:** Clear expiration date

**Timeline:** 1-2 weeks

**Example:** "We haven't seen you in a while! Here's 15% off any purchase, valid for the next 7 days. Don't miss out on our bestsellers..."

### Proactive outreach, engagement content, reminder campaign
**Criteria:** Moderate Risk

**Tactics:**
- **Educational content:** Send value-adding content (how-tos, tips, use cases)
- **Gentle reminders:** "Time to restock?" or "New products you might like"
- **Soft offers:** 5-10% discount or free shipping
- **2-3 touchpoints:** Over 3-4 weeks

**Timeline:** 2-4 weeks

**Example:** "Hi [Name], we created this guide on [topic related to past purchases]. Thought you might find it useful. By the way, here's 10% off your next order..."

### Standard nurture campaign
**Criteria:** Low Risk

**Tactics:**
- **Regular communications:** Newsletter, product updates
- **Standard offers:** Normal promotional cadence
- **No special treatment:** Part of regular customer base

**Timeline:** Ongoing, standard schedule

**Example:** Standard email newsletter with new products and promotions

### Continue standard customer communications
**Criteria:** Healthy customers

**Tactics:**
- **No intervention needed:** Customer is healthy
- **Standard communications:** Continue normal marketing
- **Monitor:** Watch for any status changes

**Timeline:** Ongoing

**Business Purpose:** Provides clear, actionable playbook for retention team. Ensures appropriate level of attention and investment for each customer scenario.

## Examples

**Scenario 1: VIP Emergency**
- Customer: High Value ($50K annual), Critical Risk (score 85)
- Action: "URGENT: Executive outreach, personalized offer, satisfaction survey"
- **Execution:**
  - Day 1: CEO sends personal email
  - Day 2: CEO calls if no response
  - Offer: 40% off next purchase + dedicated account manager + priority support
  - Survey: 30-minute call to understand issues
- **Investment:** $10,000 (20% of annual value)

**Scenario 2: High-Value Recovery**
- Customer: High Value ($30K annual), High Risk (score 60)
- Action: "HIGH PRIORITY: Personalized re-engagement, special incentive"
- **Execution:**
  - Week 1: Personalized email with 25% discount
  - Week 1: Retargeting ads
  - Week 2: Follow-up email with product recommendations
  - Week 2: Phone call if no response
- **Investment:** $3,000 (10% of annual value)

**Scenario 3: Standard Re-engagement**
- Customer: Medium-Low Value ($4K annual), High Risk (score 55)
- Action: "Re-engagement campaign, limited-time offer"
- **Execution:**
  - Email 1: "We miss you" with 15% discount (7-day expiration)
  - Email 2 (Day 4): Reminder about discount expiring
  - Email 3 (Day 6): Final 24-hour reminder
- **Investment:** $200 (5% of annual value)

**Scenario 4: Proactive Prevention**
- Customer: Medium-High Value ($12K annual), Moderate Risk (score 35)
- Action: "Proactive outreach, engagement content, reminder campaign"
- **Execution:**
  - Week 1: Educational content email
  - Week 2: Product update with 10% off
  - Week 3: "Time to restock?" reminder
- **Investment:** $960 (8% of annual value)

---

# KPI 29: RetentionPriorityRank

## Definition
**RetentionPriorityRank** assigns each at-risk customer a rank based on their RetentionPriorityScore, with rank 1 being the highest priority customer requiring immediate attention.

**SQL Expression:**
```sql
RANK() OVER (ORDER BY
    (crs.TotalChurnRiskScore * 0.6) + (crs.ValueQuartile * 10 * 0.4) DESC,
    crs.LifetimeRevenue DESC
) AS RetentionPriorityRank
```

**Mathematical Formula:**
$$\text{RetentionPriorityRank} = \text{RANK}(\text{customers ordered by RetentionPriorityScore desc, then LifetimeRevenue desc})$$

**Ranking Logic:**
1. **Primary sort:** RetentionPriorityScore (descending) - highest score first
2. **Tiebreaker:** LifetimeRevenue (descending) - higher revenue wins ties

**Business Purpose:** Creates an ordered queue for retention outreach. Answers "Who should we contact first, second, third...?"

## Examples

**Retention Queue (Top 10):**

1. **Rank 1:**
   - Customer: High Value ($100K lifetime)
   - TotalChurnRiskScore: 95 (critical)
   - RetentionPriorityScore: 61
   - Action: CEO calls today

2. **Rank 2:**
   - Customer: High Value ($80K lifetime)
   - TotalChurnRiskScore: 90
   - RetentionPriorityScore: 58
   - Action: VP calls today

3. **Rank 3:**
   - Customer: High Value ($75K lifetime)
   - TotalChurnRiskScore: 90
   - RetentionPriorityScore: 58 (tied with Rank 2)
   - Tiebreaker: Lower revenue than Rank 2, so Rank 3
   - Action: VP calls today

4-10. Additional customers in descending priority...

**Operational Use:**
- **Ranks 1-50:** Assign to senior sales team for immediate personal outreach
- **Ranks 51-200:** Assign to account managers for outreach this week
- **Ranks 201-500:** Automated personalized campaigns
- **Ranks 501+:** Standard re-engagement campaigns

---

# Summary: Churn Risk Prediction Framework

## Query Structure
The query builds churn risk assessment through five progressive CTEs:

### CTE Flow:
1. **CustomerPurchaseMetrics** → Basic customer metrics (KPI 1-10)
2. **RecentActivityTrends** → 90-day trend analysis (KPI 11-14)
3. **ChurnRiskFactors** → Calculate 4 risk factor scores + demographics (KPI 15-19)
4. **ChurnRiskScoring** → Combine risk factors, categorize, segment by value (KPI 20-23)
5. **RetentionPrioritization** → Prioritize and recommend actions (KPI 24-29)

## Churn Risk Methodology

### Risk Factor Model (4 Factors):

**1. RecencyRiskScore (0-35 points, 35% weight)**
- Based on deviation from customer's normal purchase cycle
- Personalized to each customer's behavior
- Most predictive single factor

**2. ActivityDeclineScore (0-30 points, 30% weight)**
- Compares recent 90 days vs previous 90 days
- Detects behavioral change
- Early warning system

**3. RevenueDeclineScore (0-20 points, 20% weight)**
- Tracks monetary decline independent of order count
- Identifies downgrading behavior
- Economic impact indicator

**4. LowEngagementScore (0-15 points, 15% weight)**
- Identifies customers who never formed habit
- Structural risk factor
- Different from recent decline

### Risk Categories:
- **Critical Risk (70-100):** Immediate action required
- **High Risk (50-69):** Proactive intervention needed
- **Moderate Risk (30-49):** Re-engagement campaign
- **Low Risk (15-29):** Standard nurture
- **Healthy (<15):** No intervention

### Value Segmentation:
- **High Value (Q1):** Top 25% by revenue
- **Medium-High Value (Q2):** 25th-50th percentile
- **Medium-Low Value (Q3):** 50th-75th percentile
- **Low Value (Q4):** Bottom 25%

## Business Applications

### 1. Retention Prioritization Matrix

| Risk Category | High Value | Medium-High | Medium-Low | Low Value |
|---------------|------------|-------------|------------|-----------|
| Critical | Rank 1-10, Executive outreach, $10K+ investment | Rank 20-50, Personal outreach, $2K investment | Rank 100-200, Automated personalized, $200 investment | Rank 500+, Mass campaign, $50 investment |
| High | Rank 11-30, Senior sales, $5K investment | Rank 51-100, Account manager, $1K investment | Rank 201-400, Automated, $150 investment | Rank 600+, Mass campaign, $30 investment |
| Moderate | Rank 31-60, Personalized campaign, $2K investment | Rank 101-200, Targeted campaign, $500 investment | Rank 401-600, Standard campaign, $80 investment | Rank 700+, Mass email, $10 investment |

### 2. Investment Economics

**ROI Calculation Framework:**
- **Expected Value at Risk:** ExpectedAnnualRevenue × 2 years
- **Maximum Investment:** Up to 5-20% of Expected Value at Risk
- **Break-even:** If retention rate > (Investment / Value at Risk)

**Example:**
- Customer: $50K annual revenue
- TwoYearValueAtRisk: $100K
- Max investment (20%): $20K
- If 30% retention probability: Expected value saved = $30K
- ROI: ($30K - $20K) / $20K = 50% return

### 3. Campaign Execution Workflow

**Day 1 (Critical Risk):**
- Ranks 1-50: Executive/senior sales personal outreach
- Goal: Contact within 24 hours
- Offer: Premium discounts (30-50%)

**Week 1 (High Risk):**
- Ranks 51-200: Account manager outreach
- Goal: Contact within 1 week
- Offer: Significant discounts (15-25%)

**Week 2-3 (Moderate Risk):**
- Ranks 201-500: Automated personalized campaigns
- Goal: 3-email sequence
- Offer: Standard discounts (10-15%)

**Ongoing (Low Risk):**
- All others: Standard nurture campaigns
- Goal: Monthly touchpoints
- Offer: Regular promotions (5-10%)

### 4. Success Metrics

**Retention Metrics:**
- **Retention Rate by Category:** % of customers who make another purchase within 90 days
  - Critical Risk target: 25-40%
  - High Risk target: 40-60%
  - Moderate Risk target: 60-75%

**Economic Metrics:**
- **Cost per Retention:** Total spend / customers retained
- **ROI:** (Value retained - Cost) / Cost
- **Payback Period:** Months to recover retention investment

**Predictive Model Accuracy:**
- **Churn Rate by Score Band:** Validate that high scores correlate with actual churn
- **Model Calibration:** Adjust score thresholds based on actual outcomes

### 5. Operational Process

**Weekly Retention Meeting:**
- Review top 100 by RetentionPriorityRank
- Assign ownership for outreach
- Track outreach completion and outcomes
- Adjust tactics based on results

**Monthly Analysis:**
- Churn rate by risk category
- Retention ROI by value tier
- Model accuracy assessment
- Campaign effectiveness review

**Quarterly Strategy:**
- Review risk factor weights
- Adjust score thresholds
- Update investment guidelines
- Refine action playbooks

## Key Metrics for Executive Dashboard

### Overall Health:
- **Total At-Risk Customers:** Count in Critical/High/Moderate categories
- **Revenue at Risk:** Sum of TwoYearValueAtRisk for all at-risk customers
- **Priority Customer Count:** Customers in top 100 RetentionPriorityRank

### Risk Distribution:
- **By Category:** % in Critical, High, Moderate, Low, Healthy
- **By Value Tier:** Distribution of risk across value segments
- **Trend:** Month-over-month change in at-risk population

### Retention Performance:
- **Retention Rate:** % of at-risk customers who return to active status
- **ROI by Tier:** Return on retention investment by value segment
- **Cost Efficiency:** Cost per customer retained
- **Value Saved:** Total revenue retained through interventions

### Model Performance:
- **Prediction Accuracy:** Do high-risk scores actually churn?
- **False Positive Rate:** Customers flagged as risk who were fine
- **False Negative Rate:** Customers who churned despite low risk scores

This churn risk framework provides a complete, data-driven system for predicting customer churn, prioritizing retention efforts, and economically justifying retention investments based on customer value and risk level.
