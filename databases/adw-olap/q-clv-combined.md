# Integrated Customer Lifetime Value (CLV) Analytics Framework - Comprehensive KPI Documentation

## Introduction

This document provides a unified reference for all Key Performance Indicators (KPIs) across five complementary customer analytics frameworks:

1. **CLV Scoring** (q-clv01): Comprehensive customer value assessment with multi-dimensional scoring
2. **RFM Segmentation** (q-clv02): Recency-Frequency-Monetary analysis for marketing segmentation
3. **Lifecycle Stage Analysis** (q-clv03): Customer journey progression and maturity tracking
4. **Cross-Sell Opportunity** (q-clv04): Category penetration and affinity-based recommendations
5. **Churn Risk Prediction** (q-clv05): Multi-factor churn scoring and retention prioritization

This integrated framework encompasses **158 individual KPI calculations** (deduplicated to **95 unique metrics**) that work together to provide a complete view of customer behavior, value, risk, and opportunity. Each KPI entry below indicates which analysis uses it via tags: [CLV01], [CLV02], [CLV03], [CLV04], [CLV05].

### KPI Organization

KPIs are organized into logical families:
- **Temporal Metrics** (KPI 1-8): Time-based relationship measurements
- **Transaction Volume Metrics** (KPI 9-11): Purchase frequency and activity
- **Financial Value Metrics** (KPI 12-20): Revenue, profit, and spending patterns
- **Discount and Margin Metrics** (KPI 21-23): Pricing and profitability
- **Product Diversity Metrics** (KPI 24-25): Category and SKU breadth
- **Annualized Metrics** (KPI 26-30): Normalized year-over-year rates
- **RFM Scoring Metrics** (KPI 31-37): Recency-Frequency-Monetary dimensions
- **Composite Scoring Metrics** (KPI 38-42): Integrated customer value scores
- **Ranking Metrics** (KPI 43-45): Customer position and percentile
- **Segmentation Metrics** (KPI 46-48): Tier and segment classification
- **RFM Segment Analytics** (KPI 49-62): Detailed segment characteristics
- **Lifecycle Metrics** (KPI 63-75): Journey stage and progression tracking
- **Cross-Sell Metrics** (KPI 76-85): Category affinity and opportunity identification
- **Churn Risk Metrics** (KPI 86-95): Multi-dimensional risk assessment

### Analytical Approach

All five analyses use progressive CTE (Common Table Expression) structures that build from basic transaction data to sophisticated behavioral insights:
- **Foundation Layer**: Aggregate raw transaction data into customer-level summaries
- **Enrichment Layer**: Calculate derived metrics, rates, and ratios
- **Scoring Layer**: Apply scoring algorithms and quintile rankings
- **Segmentation Layer**: Classify customers into actionable segments
- **Recommendation Layer**: Generate specific business actions and priorities

This architecture enables both operational execution (individual customer recommendations) and strategic analysis (segment-level trends and distributions).

---

# KPI 1: FirstPurchaseDate

**Used in:** [CLV01] [CLV02] [CLV03]

## Definition
**FirstPurchaseDate** represents the date of a customer's very first purchase transaction in the system. This establishes the beginning of the customer relationship timeline and serves as the anchor point for cohort analysis, tenure calculations, and customer lifecycle tracking.

**SQL Expression:**
```sql
MIN(fis.OrderDate) AS FirstPurchaseDate
```

**Mathematical Formula:**
$$\text{FirstPurchaseDate} = \min_{i}(\text{OrderDate}_i) \text{ for all orders } i \text{ of customer}$$

**Business Purpose:**
- Identifies customer acquisition date for cohort analysis
- Enables calculation of customer age and lifecycle stage
- Foundation for tenure-based metrics and comparisons
- Critical for understanding customer maturity and growth trajectories

## Examples
- Customer A: First purchase on 2020-01-15 → 4-year customer (as of 2024)
- Customer B: First purchase on 2023-11-20 → New customer (<2 years)
- Customer C: First purchase on 2015-06-10 → Veteran customer (9+ years)

**Cross-Reference:** Used to calculate CustomerTenureDays (KPI 5), CustomerTenureYears (KPI 6), and influences LifecycleStage classification (KPI 69).

---

# KPI 2: LastPurchaseDate

**Used in:** [CLV01] [CLV02] [CLV03]

## Definition
**LastPurchaseDate** represents the date of a customer's most recent purchase transaction. This is the foundation for all recency analysis and the single most predictive metric for future purchase behavior.

**SQL Expression:**
```sql
MAX(fis.OrderDate) AS LastPurchaseDate
```

**Mathematical Formula:**
$$\text{LastPurchaseDate} = \max_{i}(\text{OrderDate}_i) \text{ for all orders } i \text{ of customer}$$

**Business Purpose:**
- Primary input for recency scoring (strongest predictor in RFM)
- Identifies active vs. dormant vs. churned customers
- Triggers for reactivation campaigns and churn prevention
- Foundation for lifecycle stage transitions

## Examples
- Customer A: Last purchased 2024-12-15 → Active customer (recent)
- Customer B: Last purchased 2023-06-20 → At-risk customer (18 months dormant)
- Customer C: Last purchased 2021-03-10 → Likely churned (3+ years dormant)

**Critical Thresholds:**
- 0-30 days: Highly active
- 31-90 days: Active/engaged
- 91-180 days: Warming/declining
- 181-365 days: At-risk
- 365+ days: Churned/lost

**Cross-Reference:** Used to calculate DaysSinceLastPurchase (KPI 7), RecencyScore (KPI 31), and influences ChurnRiskScore (KPI 90).

---

# KPI 3: TotalOrders

**Used in:** [CLV01] [CLV02] [CLV03] [CLV05]

## Definition
**TotalOrders** counts the number of distinct purchase orders a customer has placed over their entire relationship with the business. This is the primary measure of purchase frequency and forms the "Frequency" dimension in RFM analysis.

**SQL Expression:**
```sql
COUNT(DISTINCT fis.SalesOrderNumber) AS TotalOrders
```

**Mathematical Formula:**
$$\text{TotalOrders} = |\{\text{SalesOrderNumber}_i : i \in \text{all transactions}\}|$$

where $|\cdot|$ denotes the cardinality (count) of unique order numbers.

**Relationships:**
$$\text{UniquePurchaseDays} \leq \text{TotalOrders} \leq \text{TotalLineItems}$$

**Business Purpose:**
- Measures customer engagement frequency and loyalty
- Foundation for frequency scoring in RFM segmentation
- Indicates repeat purchase behavior and habit formation
- Used in churn prediction (declining order frequency signals risk)

## Examples
- Customer A: 45 orders over 3 years → 15 orders/year (highly engaged, monthly buyer)
- Customer B: 2 orders over 5 years → 0.4 orders/year (low engagement, casual buyer)
- Customer C: 150 orders over 2 years → 75 orders/year (champion customer, weekly buyer)

**Distribution Characteristics:**
- Typically follows power-law distribution
- Top 20% of customers often account for 60-80% of total orders
- Single-order customers ("one-and-done") typically 40-60% of customer base

**Cross-Reference:** Used in FrequencyScore (KPI 33), OrdersPerYear (KPI 28), ActivityDeclineScore (KPI 87), and LifecycleStage (KPI 69).

---

# KPI 4: TotalLineItems

**Used in:** [CLV01]

## Definition
**TotalLineItems** counts the total number of individual product line items purchased across all orders. This differs from TotalOrders as a single order can contain multiple line items (products).

**SQL Expression:**
```sql
COUNT(*) AS TotalLineItems
```

**Mathematical Formula:**
$$\text{TotalLineItems} = \sum_{i=1}^{n} 1 \text{ for all line items } i$$

**Derived Metric:**
$$\text{Items Per Order} = \frac{\text{TotalLineItems}}{\text{TotalOrders}}$$

This ratio indicates average basket size.

**Business Purpose:**
- Measures total transaction volume at granular level
- Basket size indicator (items per order)
- Cross-selling effectiveness measure
- Denominator for average line item value calculations

## Examples
- Customer with 10 orders, 10 line items → 1.0 items/order (single-item buyer)
- Customer with 10 orders, 50 line items → 5.0 items/order (basket buyer, strong cross-sell)
- Customer with 10 orders, 100 line items → 10.0 items/order (bulk/wholesale behavior)

**Business Insight:** High items-per-order ratio suggests:
- Successful cross-selling
- Bulk/wholesale purchasing behavior
- High product discovery and engagement
- Better revenue per transaction

---

# KPI 5: CustomerTenureDays

**Used in:** [CLV01] [CLV02] [CLV03]

## Definition
**CustomerTenureDays** calculates the number of days between a customer's first and last purchase, representing the span of their active relationship with the business.

**SQL Expression:**
```sql
(MAX(fis.OrderDate)::DATE - MIN(fis.OrderDate)::DATE) AS CustomerTenureDays
```

**Mathematical Formula:**
$$\text{CustomerTenureDays} = \text{LastPurchaseDate} - \text{FirstPurchaseDate}$$

where dates are treated as integers (days since epoch).

**Special Case:** For customers with only one order, this value is 0.

**Business Purpose:**
- Measures duration of customer relationship
- Foundation for annualizing metrics (revenue per year, orders per year)
- Customer lifecycle stage indicator
- Distinguishes new customers from veteran customers

## Examples
- Customer A: First 2020-01-01, Last 2024-01-01 → 1461 days (4.0 years)
- Customer B: First 2023-12-01, Last 2024-01-01 → 31 days (new customer)
- Customer C: First 2018-06-15, Last 2024-12-31 → 2390 days (6.5 years, veteran)
- Customer D: First 2024-01-01, Last 2024-01-01 → 0 days (single purchase)

**Interpretation Guidelines:**
- 0-90 days: New customer (onboarding phase)
- 91-365 days: Developing customer (first year)
- 366-730 days: Established customer (year 2)
- 731+ days: Mature customer (3+ years)

**Cross-Reference:** Used to calculate CustomerTenureYears (KPI 6), AvgDaysBetweenOrders (KPI 30), ActivityRatioPct (KPI 29), and influences LifecycleStage (KPI 69).

---

# KPI 6: CustomerTenureYears

**Used in:** [CLV01]

## Definition
**CustomerTenureYears** converts CustomerTenureDays into years using the precise astronomical year length (365.25 days to account for leap years). This provides a human-readable tenure measure.

**SQL Expression:**
```sql
ROUND(CustomerTenureDays / 365.25, 2) AS CustomerTenureYears
```

**Mathematical Formula:**
$$\text{CustomerTenureYears} = \frac{\text{CustomerTenureDays}}{365.25}$$

**Business Purpose:**
- Human-readable relationship duration
- Denominator for all annualized metrics
- Cohort analysis and customer age comparisons
- Fair comparison between new and longstanding customers

## Examples
- 1461 days → 4.00 years
- 730 days → 2.00 years
- 183 days → 0.50 years (6 months)
- 0 days → 0.00 years (single-order customer)
- 2921 days → 8.00 years (long-tenure veteran)

**Usage in Annualized Metrics:**
- RevenuePerYear = LifetimeRevenue / CustomerTenureYears
- ProfitPerYear = LifetimeGrossProfit / CustomerTenureYears
- OrdersPerYear = TotalOrders / CustomerTenureYears

**Note:** For single-order customers (tenure = 0), annualized calculations typically return NULL or infinity, handled via NULLIF() in SQL.

---

# KPI 7: DaysSinceLastPurchase

**Used in:** [CLV01] [CLV02] [CLV03] [CLV05]

## Definition
**DaysSinceLastPurchase** calculates the number of days from the customer's last purchase to the current date. This is the raw recency metric and the single strongest predictor of future purchase probability in customer analytics.

**SQL Expression:**
```sql
(CURRENT_DATE - LastPurchaseDate::DATE) AS DaysSinceLastPurchase
```

**Mathematical Formula:**
$$\text{DaysSinceLastPurchase} = \text{CURRENT\_DATE} - \text{LastPurchaseDate}$$

**Business Purpose:**
- Primary recency metric for RFM analysis
- Strongest single predictor of future purchase (more predictive than frequency or monetary)
- Foundation for churn prediction and risk scoring
- Triggers for reactivation campaigns and retention interventions

## Examples
- Customer A: Last purchased 15 days ago → Score: Highly active (hot lead)
- Customer B: Last purchased 180 days ago → Score: At-risk (needs attention)
- Customer C: Last purchased 730 days ago → Score: Churned (likely lost)
- Customer D: Last purchased 45 days ago → Score: Active (engaged)

**Interpretation Frameworks:**

**Framework 1 - CLV01 Thresholds:**
- ≤30 days: RecencyScore = 100 (excellent)
- 31-90 days: RecencyScore = 80 (good)
- 91-180 days: RecencyScore = 60 (moderate)
- 181-365 days: RecencyScore = 40 (declining)
- 366-730 days: RecencyScore = 20 (at-risk)
- >730 days: RecencyScore = 0 (churned)

**Framework 2 - CLV02 Thresholds:**
- ≤60 days: RecencyScore = 5 (most recent)
- 61-120 days: RecencyScore = 4 (recent)
- 121-240 days: RecencyScore = 3 (moderate)
- 241-480 days: RecencyScore = 2 (declining)
- >480 days: RecencyScore = 1 (churned)

**Framework 3 - CLV05 Churn Risk:**
- Compared against customer's personal AvgDaysBetweenOrders
- Deviation drives RecencyRiskScore (35% of churn score)

**Cross-Reference:** Foundation for RecencyScore (KPI 31), RecencyRiskScore (KPI 86), RFMSegment (KPI 48), and ChurnRiskCategory (KPI 91).

---

# KPI 8: UniquePurchaseDays

**Used in:** [CLV01]

## Definition
**UniquePurchaseDays** counts the number of distinct calendar days on which a customer made at least one purchase. This measures purchase day diversity and activity concentration.

**SQL Expression:**
```sql
COUNT(DISTINCT DATE(fis.OrderDate)) AS UniquePurchaseDays
```

**Mathematical Formula:**
$$\text{UniquePurchaseDays} = |\{\text{DATE}(\text{OrderDate}_i) : i \in \text{all orders}\}|$$

**Relationship:**
$$\text{UniquePurchaseDays} \leq \text{TotalOrders} \leq \text{TotalLineItems}$$

Equality holds when customer never places multiple orders on same day.

**Business Purpose:**
- Differentiates bulk buyers (multiple orders/day) from regular buyers (one order/day)
- Measures activity spread vs. concentration
- Indicates shopping behavior patterns
- Used in ActivityRatioPct calculation (KPI 29)

## Examples
- Customer with 10 orders on 10 different days → UniquePurchaseDays = 10 (spread shopping)
- Customer with 10 orders all on same day → UniquePurchaseDays = 1 (bulk buyer)
- Customer with 10 orders over 5 days → UniquePurchaseDays = 5 (averages 2 orders per shopping session)

**Behavioral Insights:**
- **Ratio = 1.0 (UniqueDays = TotalOrders):** One order per shopping day (typical consumer)
- **Ratio < 1.0 (UniqueDays < TotalOrders):** Multiple orders per day (bulk, wholesale, or split orders)
- **Low UniqueDays + High Orders:** Concentrated purchasing (seasonal bulk buyer)
- **High UniqueDays:** Regular, habitual purchaser

---

# KPI 9: TotalUnits

**Used in:** [CLV01]

## Definition
**TotalUnits** represents the total quantity of product units purchased by the customer across all transactions, regardless of product type or category. This is a volume-based metric distinct from revenue or order count.

**SQL Expression:**
```sql
SUM(fis.OrderQuantity) AS TotalUnits
```

**Mathematical Formula:**
$$\text{TotalUnits} = \sum_{i=1}^{n} \text{OrderQuantity}_i$$

where $n$ is the total number of line items.

**Derived Metrics:**
$$\text{Units Per Order} = \frac{\text{TotalUnits}}{\text{TotalOrders}}$$
$$\text{Units Per Line Item} = \frac{\text{TotalUnits}}{\text{TotalLineItems}}$$

**Business Purpose:**
- Measures total volume consumption
- Indicates wholesale vs. retail buying behavior
- Inventory forecasting and demand planning
- Identifies bulk purchasers and resellers

## Examples
- Customer A: 500 units over 10 orders → 50 units/order (possible reseller or bulk buyer)
- Customer B: 25 units over 25 orders → 1 unit/order (typical retail consumer)
- Customer C: 1,000 units in single order → Bulk/wholesale buyer or business account
- Customer D: 200 units over 50 orders → 4 units/order (moderate basket size)

**Interpretation by Units Per Order:**
- **1-2 units/order:** Individual consumer (retail)
- **3-10 units/order:** Family/household buyer
- **10-50 units/order:** Small business or bulk buyer
- **50+ units/order:** Wholesale, reseller, or B2B account

**Business Applications:**
- Segment customers by volume tier for special pricing
- Identify reseller accounts for B2B programs
- Forecast demand based on historical unit consumption
- Optimize inventory for high-volume customers

---

# KPI 10: PurchaseSequence

**Used in:** [CLV03]

## Definition
**PurchaseSequence** assigns a sequential order number to each purchase made by a customer, numbered from 1 (first purchase) to N (most recent purchase). This enables analysis of behavior changes across the customer journey.

**SQL Expression:**
```sql
ROW_NUMBER() OVER (PARTITION BY CustomerKey ORDER BY OrderDate) AS PurchaseSequence
```

**Mathematical Formula:**
$$\text{PurchaseSequence}(o) = |\{o' : \text{OrderDate}(o') < \text{OrderDate}(o)\}| + 1$$

for order $o$ of a given customer.

**Range:** 1 to TotalOrders

**Business Purpose:**
- Tracks customer journey progression
- Enables cohort-based behavior analysis (e.g., "orders 1-3" vs. "orders 10+")
- Identifies patterns in early vs. late purchases
- Foundation for lifecycle stage classification
- Used with LAG/LEAD functions to calculate inter-purchase intervals

## Examples
- Customer A, Order made on 2020-01-15 → PurchaseSequence = 1 (first order)
- Customer A, Order made on 2020-03-10 → PurchaseSequence = 2 (second order)
- Customer A, Order made on 2024-12-01 → PurchaseSequence = 45 (most recent)

**Analytical Applications:**

**Early Journey Analysis (Sequence 1-3):**
- Onboarding effectiveness
- New customer acquisition quality
- Product-market fit validation
- Repeat purchase conversion rate

**Mid Journey Analysis (Sequence 4-10):**
- Habit formation success
- Category expansion patterns
- Loyalty development

**Late Journey Analysis (Sequence 11+):**
- Mature customer behavior
- Lifetime value trajectory
- Retention stability

**Cross-Reference:** Used in calculating CumulativeOrders (KPI 66), CumulativeRevenue (KPI 67), PreviousOrderDate (KPI 63), and LifecycleStage (KPI 69).

---

# KPI 11: CumulativeOrders

**Used in:** [CLV03]

## Definition
**CumulativeOrders** calculates the running total of orders a customer has placed up to and including each specific order. This provides a journey-based view of engagement growth.

**SQL Expression:**
```sql
COUNT(*) OVER (
    PARTITION BY CustomerKey
    ORDER BY OrderDate
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
) AS CumulativeOrders
```

**Mathematical Formula:**
$$\text{CumulativeOrders}(o_i) = |\{o_j : j \leq i\}| = i$$

where orders are indexed in chronological sequence.

**Relationship:**
$$\text{CumulativeOrders} = \text{PurchaseSequence}$$

(These are mathematically equivalent.)

**Business Purpose:**
- Tracks engagement accumulation over time
- Enables milestone-based rewards (e.g., "10th order discount")
- Visualizes customer growth trajectories
- Identifies acceleration or deceleration in purchase frequency

## Examples
- Purchase 1: CumulativeOrders = 1
- Purchase 5: CumulativeOrders = 5
- Purchase 10: CumulativeOrders = 10 (milestone reached)
- Purchase 50: CumulativeOrders = 50 (highly engaged customer)

**Growth Pattern Analysis:**

**Linear Growth:** Steady increase, predictable repurchase
- Example: Orders at days 30, 60, 90, 120 (every 30 days)

**Accelerating Growth:** Increasing purchase frequency over time
- Example: Orders at days 90, 110, 120, 125 (intervals shrinking)

**Decelerating Growth:** Decreasing purchase frequency
- Example: Orders at days 30, 90, 180, 365 (intervals expanding) → Churn risk signal

---

# KPI 12: LifetimeRevenue / TotalRevenue

**Used in:** [CLV01] as LifetimeRevenue, [CLV02] [CLV03] [CLV04] [CLV05] as TotalRevenue

## Definition
**LifetimeRevenue** (or **TotalRevenue**) is the total sales amount generated by a customer across all their purchases. This is the most fundamental customer value metric, representing the top-line contribution of a customer to the business.

**SQL Expression:**
```sql
ROUND(SUM(fis.SalesAmount), 2) AS LifetimeRevenue
-- OR
ROUND(SUM(fis.SalesAmount), 2) AS TotalRevenue
```

**Mathematical Formula:**
$$\text{LifetimeRevenue} = \sum_{i=1}^{n} \text{SalesAmount}_i$$

where $\text{SalesAmount}_i$ is the revenue from line item $i$, and $n$ is the total number of line items.

**Business Purpose:**
- Primary metric for customer ranking and value assessment
- Foundation for "Monetary" dimension in RFM segmentation
- Used in Pareto analysis (80/20 rule identification)
- Customer tiering and VIP program qualification
- Revenue forecasting and customer portfolio analysis

## Examples
- Customer A: $50,000 lifetime revenue → High-value customer
- Customer B: $500 lifetime revenue → Low-value customer
- Customer C: $250,000 lifetime revenue → VIP/whale customer (top 1%)
- Customer D: $5,000 lifetime revenue → Average customer

**Distribution Characteristics:**
- Typically follows Pareto distribution
- Top 20% of customers often generate 70-80% of revenue
- Median customer value usually 3-5x lower than mean (right-skewed distribution)

**Cross-Reference:** Used in MonetaryScore (KPI 35), RevenuePerYear (KPI 26), CustomerValueScore (KPI 38), ValueQuartile (KPI 76), and RevenueDeclineScore (KPI 88).

---

# KPI 13: LifetimeGrossProfit / TotalGrossProfit

**Used in:** [CLV01] as LifetimeGrossProfit, [CLV02] [CLV03] as TotalGrossProfit

## Definition
**LifetimeGrossProfit** (or **TotalGrossProfit**) calculates the total gross profit (revenue minus product cost) generated by a customer over their lifetime. This represents the actual margin contribution before operating expenses and is a more accurate value metric than revenue alone.

**SQL Expression:**
```sql
ROUND(SUM(fis.SalesAmount - fis.TotalProductCost), 2) AS LifetimeGrossProfit
-- OR
ROUND(SUM(fis.SalesAmount - fis.TotalProductCost), 2) AS TotalGrossProfit
```

**Mathematical Formula:**
$$\text{LifetimeGrossProfit} = \sum_{i=1}^{n} (\text{SalesAmount}_i - \text{TotalProductCost}_i)$$

$$= \text{LifetimeRevenue} - \sum_{i=1}^{n} \text{TotalProductCost}_i$$

**Business Purpose:**
- More accurate customer value assessment than revenue
- Accounts for product mix and margin differences
- Critical for profitability-based segmentation
- Foundation for customer acquisition cost (CAC) payback calculations
- Identifies high-margin vs. low-margin customers

## Examples
- Customer A: $50,000 revenue, $30,000 costs → $20,000 profit (40% margin)
- Customer B: $100,000 revenue, $95,000 costs → $5,000 profit (5% margin, low-margin buyer)
- Customer C: $20,000 revenue, $8,000 costs → $12,000 profit (60% margin, high-margin buyer)

**Key Insight:** Customer C is more profitable than Customer B despite having 5x lower revenue. Profit-based rankings often differ significantly from revenue-based rankings.

**Industry Context:**
- Luxury goods: 60-80% gross margin typical
- Electronics: 5-15% gross margin typical
- Grocery/retail: 2-5% gross margin typical
- SaaS/software: 80-95% gross margin typical

**Cross-Reference:** Used in ProfitPerYear (KPI 27), ProfitRank (KPI 45), LifetimeMarginPct (KPI 14), and CustomerValueScore (KPI 38).

---

# KPI 14: LifetimeMarginPct

**Used in:** [CLV01]

## Definition
**LifetimeMarginPct** expresses the gross profit margin as a percentage of revenue, indicating the profitability rate of a customer's purchases. This normalizes profitability across different revenue levels.

**SQL Expression:**
```sql
ROUND(100.0 * SUM(fis.SalesAmount - fis.TotalProductCost) / NULLIF(SUM(fis.SalesAmount), 0), 2) AS LifetimeMarginPct
```

**Mathematical Formula:**
$$\text{LifetimeMarginPct} = \frac{\text{LifetimeGrossProfit}}{\text{LifetimeRevenue}} \times 100$$

$$= \frac{\sum (\text{SalesAmount}_i - \text{TotalProductCost}_i)}{\sum \text{SalesAmount}_i} \times 100$$

**Range:** 0% to 100% (higher is better)

**Business Purpose:**
- Identifies customers who buy high-margin vs. low-margin products
- Guides targeted promotions and product recommendations
- Customer segmentation by margin profile
- Component of CustomerValueScore (8% weight)

## Examples
- Customer A: $10,000 revenue, $4,000 profit → 40% margin (excellent)
- Customer B: $100,000 revenue, $5,000 profit → 5% margin (poor, discount buyer)
- Customer C: $50,000 revenue, $15,000 profit → 30% margin (good)
- Customer D: $5,000 revenue, $4,000 profit → 80% margin (exceptional, luxury buyer)

**Strategic Applications:**

**High-Margin Customers (>40%):**
- Premium/luxury product buyers
- Full-price purchasers
- Target for upselling higher-tier products
- Protect from discount conditioning

**Low-Margin Customers (<15%):**
- Discount-driven or commodity buyers
- May be unprofitable after marketing costs
- Consider whether to serve or adjust strategy
- Evaluate lifetime value vs. acquisition cost

**Cross-Reference:** Component of CustomerValueScore (KPI 38), used to identify profitable customers in retention strategies.

---

# KPI 15: GrossProfit (per transaction)

**Used in:** [CLV03]

## Definition
**GrossProfit** calculates the gross profit (revenue minus cost) for each individual transaction or line item, enabling transaction-level profitability analysis.

**SQL Expression:**
```sql
(fis.SalesAmount - fis.TotalProductCost) AS GrossProfit
```

**Mathematical Formula:**
$$\text{GrossProfit}_i = \text{SalesAmount}_i - \text{TotalProductCost}_i$$

**Business Purpose:**
- Transaction-level profitability tracking
- Identifies which specific purchases were most/least profitable
- Used in lifecycle stage analysis to detect profitability trends
- Enables cumulative profit calculations along customer journey

## Examples
- Transaction 1: $100 revenue, $60 cost → $40 gross profit
- Transaction 2: $500 revenue, $450 cost → $50 gross profit (lower margin)
- Transaction 3: $200 revenue, $50 cost → $150 gross profit (high margin)

**Behavioral Analysis:**
- Increasing GrossProfit over time → Customer maturing toward premium products
- Decreasing GrossProfit over time → Customer shifting to discounts or commodities
- Volatile GrossProfit → Diverse product mix exploration

---

# KPI 16: CumulativeRevenue

**Used in:** [CLV03]

## Definition
**CumulativeRevenue** calculates the running total of revenue a customer has generated up to and including each specific order, providing a journey-based view of value accumulation.

**SQL Expression:**
```sql
SUM(fis.SalesAmount) OVER (
    PARTITION BY fis.CustomerKey
    ORDER BY fis.OrderDate
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
) AS CumulativeRevenue
```

**Mathematical Formula:**
$$\text{CumulativeRevenue}(o_i) = \sum_{j=1}^{i} \text{SalesAmount}_j$$

where orders are indexed in chronological sequence.

**Business Purpose:**
- Tracks customer value growth trajectory
- Identifies value acceleration or deceleration patterns
- Milestone-based reward triggers (e.g., "$10K lifetime club")
- Lifecycle stage transitions based on cumulative value thresholds
- Visualizes customer lifetime value curves

## Examples
- Purchase 1: $500 → CumulativeRevenue = $500
- Purchase 5: $300 → CumulativeRevenue = $2,100
- Purchase 10: $450 → CumulativeRevenue = $5,000 (milestone)
- Purchase 25: $600 → CumulativeRevenue = $15,000

**Growth Trajectory Analysis:**

**Accelerating Value:** Revenue per order increasing over time
- Pattern: $100, $150, $250, $400 → Customer expanding basket size

**Steady Value:** Consistent revenue per order
- Pattern: $200, $210, $190, $205 → Stable, predictable customer

**Decelerating Value:** Revenue per order decreasing
- Pattern: $500, $400, $200, $100 → Potential churn signal or product fit decline

---

# KPI 17: AvgLineItemValue / AvgTransactionValue

**Used in:** [CLV01] as AvgLineItemValue, [CLV02] as AvgTransactionValue

## Definition
**AvgLineItemValue** (or **AvgTransactionValue**) calculates the average sales amount per individual line item (product) purchased. This indicates typical transaction size at the most granular level and reveals price point preferences.

**SQL Expression:**
```sql
ROUND(AVG(fis.SalesAmount), 2) AS AvgLineItemValue
-- OR
ROUND(AVG(fis.SalesAmount), 2) AS AvgTransactionValue
```

**Mathematical Formula:**
$$\text{AvgLineItemValue} = \frac{1}{n}\sum_{i=1}^{n} \text{SalesAmount}_i = \frac{\text{LifetimeRevenue}}{\text{TotalLineItems}}$$

where $n$ is the total number of line items.

**Business Purpose:**
- Indicates price point preference (premium vs. value vs. discount)
- Customer economic segmentation
- Product recommendation targeting
- Identifies wallet share potential

## Examples
- Customer A: $10,000 revenue, 100 line items → $100 avg (mid-market buyer)
- Customer B: $10,000 revenue, 20 line items → $500 avg (premium buyer)
- Customer C: $10,000 revenue, 500 line items → $20 avg (discount/value buyer)
- Customer D: $10,000 revenue, 10 line items → $1,000 avg (luxury buyer)

**Segmentation by Price Point:**
- **<$25:** Value/discount segment
- **$25-$100:** Mass market segment
- **$100-$500:** Premium segment
- **>$500:** Luxury/high-end segment

**Cross-Reference:** Related to AvgOrderValue (KPI 18), influences product recommendation strategies.

---

# KPI 18: AvgOrderValue (AOV)

**Used in:** [CLV01]

## Definition
**AvgOrderValue (AOV)** calculates the average total sales amount per order (not per line item). This is a critical e-commerce and retail metric indicating typical basket size and cross-selling effectiveness.

**SQL Expression:**
```sql
ROUND(SUM(fis.SalesAmount) / NULLIF(TotalOrders, 0), 2) AS AvgOrderValue
```

**Mathematical Formula:**
$$\text{AvgOrderValue} = \frac{\text{LifetimeRevenue}}{\text{TotalOrders}}$$

**Relationship:**
$$\text{AvgOrderValue} = \text{AvgLineItemValue} \times \frac{\text{TotalLineItems}}{\text{TotalOrders}}$$

$$\text{AvgOrderValue} = \text{AvgLineItemValue} \times \text{Items Per Order}$$

**Business Purpose:**
- Key metric for cross-selling and upselling effectiveness
- Reduces transaction costs when increased (fewer orders for same revenue)
- Basket optimization target
- Customer economic value indicator

## Examples
- Customer A: $50,000 revenue, 100 orders → $500 AOV (strong basket size)
- Customer B: $50,000 revenue, 500 orders → $100 AOV (frequent small purchases)
- Customer C: $50,000 revenue, 10 orders → $5,000 AOV (bulk/wholesale buyer)

**Strategic Insight:** Increasing AOV by 10% is often easier and more profitable than increasing customer count by 10% (lower acquisition cost per dollar of revenue).

**Industry Benchmarks:**
- Grocery/convenience: $20-$50
- Apparel: $50-$150
- Electronics: $200-$800
- Furniture: $500-$2,000
- B2B wholesale: $5,000+

---

# KPI 19: TotalDiscounts

**Used in:** [CLV01]

## Definition
**TotalDiscounts** sums all discount amounts applied to a customer's purchases over their lifetime, representing the total price reduction granted to incentivize purchases.

**SQL Expression:**
```sql
ROUND(SUM(fis.DiscountAmount), 2) AS TotalDiscounts
```

**Mathematical Formula:**
$$\text{TotalDiscounts} = \sum_{i=1}^{n} \text{DiscountAmount}_i$$

**Business Purpose:**
- Measures customer's sensitivity to promotions
- Quantifies cost of acquiring/retaining the customer through discounts
- Identifies discount-dependent vs. full-price customers
- Margin erosion tracking

## Examples
- Customer A: $50,000 revenue, $5,000 discounts → 10% discount rate (promotional buyer)
- Customer B: $50,000 revenue, $500 discounts → 1% discount rate (full-price buyer)
- Customer C: $10,000 revenue, $8,000 discounts → 80% discount rate (extreme dependency)

**Strategic Implications:**

**Low Discount Customers (<5% rate):**
- Brand loyal, values quality over price
- Higher margin contribution
- Less churn risk from competitor promotions

**High Discount Customers (>20% rate):**
- Promotional dependency established
- Trained to wait for sales
- Lower margin contribution
- Higher churn risk to better offers

---

# KPI 20: AvgDiscountPct

**Used in:** [CLV01]

## Definition
**AvgDiscountPct** calculates the average discount rate as a percentage of the original price (before discount). This normalizes discount behavior across different purchase sizes.

**SQL Expression:**
```sql
ROUND(100.0 * SUM(fis.DiscountAmount) / NULLIF(SUM(fis.SalesAmount + fis.DiscountAmount), 0), 2) AS AvgDiscountPct
```

**Mathematical Formula:**
$$\text{AvgDiscountPct} = \frac{\sum \text{DiscountAmount}_i}{\sum (\text{SalesAmount}_i + \text{DiscountAmount}_i)} \times 100$$

$$= \frac{\text{TotalDiscounts}}{\text{Original Price Before Discounts}} \times 100$$

**Range:** 0% to 100%

**Business Purpose:**
- Identifies promotional dependency patterns
- Customer price sensitivity segmentation
- Targeted discount strategy optimization
- Margin impact assessment

## Examples
- Customer A: $10,000 final, $0 discounts → 0% (full-price buyer, premium)
- Customer B: $10,000 final, $1,111 discounts → 10% average discount (occasional promotional)
- Customer C: $10,000 final, $5,000 discounts → 33% average discount (highly promotional)
- Customer D: $10,000 final, $10,000 discounts → 50% average discount (extreme dependency)

**Segmentation Strategy:**
- **0-5%:** Full-price segment → Protect from discount conditioning
- **5-15%:** Selective promotional → Moderate discount targeting
- **15-30%:** Promotion-driven → Heavy discount expectation
- **>30%:** Discount-dependent → May be unprofitable, reconsider strategy

---

# KPI 21: UniqueCategories

**Used in:** [CLV01] [CLV04]

## Definition
**UniqueCategories** counts the number of distinct product categories a customer has purchased from, measuring product diversity at the category level.

**SQL Expression:**
```sql
COUNT(DISTINCT pc.EnglishProductCategoryName) AS UniqueCategories
```

**Mathematical Formula:**
$$\text{UniqueCategories} = |\{\text{ProductCategory}_i : i \in \text{all purchases}\}|$$

**Business Purpose:**
- Measures cross-category engagement
- Share-of-wallet indicator
- Cross-sell opportunity identification
- Loyalty depth assessment (broader engagement = stronger loyalty)

## Examples
- Customer A: Purchased from 1 category (Bikes only) → Specialist buyer, cross-sell opportunity
- Customer B: Purchased from 4 categories (Bikes, Clothing, Accessories, Components) → Diverse buyer, high engagement
- If total categories = 4, Customer B is a full-catalog customer

**Strategic Applications:**

**Low Category Penetration (1-2 categories):**
- High cross-sell potential
- Category-specific loyalty
- Risk of churn if category needs change
- Target with complementary category offers

**High Category Penetration (3+ categories):**
- Stronger overall loyalty
- Lower churn risk
- Higher share-of-wallet
- Broader relationship with brand

**Cross-Reference:** Used in CategoryPenetrationPct (KPI 78), cross-sell opportunity analysis, and customer engagement scoring.

---

# KPI 22: UniqueProducts

**Used in:** [CLV01]

## Definition
**UniqueProducts** counts the number of distinct products (SKUs) a customer has purchased, measuring product diversity at the most granular level.

**SQL Expression:**
```sql
COUNT(DISTINCT fis.ProductKey) AS UniqueProducts
```

**Mathematical Formula:**
$$\text{UniqueProducts} = |\{\text{ProductKey}_i : i \in \text{all purchases}\}|$$

**Relationship:**
$$\text{UniqueProducts} \leq \text{TotalLineItems}$$

Equality holds when customer never repurchases the same product.

**Business Purpose:**
- Indicates variety-seeking vs. repeat-buying behavior
- Product discovery and exploration measurement
- Repurchase rate calculation
- Consumable vs. durable purchase patterns

## Examples
- Customer A: 100 line items, 100 unique products → 100% variety (explorer, never repurchases)
- Customer B: 100 line items, 10 unique products → 10% variety (high loyalty, averages 10 units per SKU)
- Customer C: 100 line items, 50 unique products → 50% variety (balanced mix)

**Repurchase Rate:**
$$\text{Repurchase Rate} = 1 - \frac{\text{UniqueProducts}}{\text{TotalLineItems}}$$

**Behavior Patterns:**
- **High variety (>70%):** Explorer, low repurchase, suitable for discovery-based recommendations
- **Low variety (<30%):** Loyalist, high repurchase, suitable for subscription/auto-replenish
- **Moderate variety (30-70%):** Balanced, both discovery and loyalty present

---

# KPI 23-30: Annualized Metrics

**Used in:** [CLV01]

These metrics normalize customer behavior by tenure to enable fair comparison between new and veteran customers.

## KPI 26: RevenuePerYear
**Formula:** $\text{RevenuePerYear} = \frac{\text{LifetimeRevenue}}{\text{CustomerTenureYears}}$

Annualized revenue enables comparison: a 1-year customer with $10K revenue = a 5-year customer with $50K revenue (both $10K/year rate).

## KPI 27: ProfitPerYear
**Formula:** $\text{ProfitPerYear} = \frac{\text{LifetimeGrossProfit}}{\text{CustomerTenureYears}}$

More accurate than revenue for CAC payback: if CAC = $2,000 and ProfitPerYear = $8,000, payback = 3 months.

## KPI 28: OrdersPerYear
**Formula:** $\text{OrdersPerYear} = \frac{\text{TotalOrders}}{\text{CustomerTenureYears}}$

Indicates purchase frequency rate: 12 orders/year = monthly buyer, 52 = weekly, 2 = biannual.

## KPI 29: ActivityRatioPct
**Formula:** $\text{ActivityRatioPct} = \frac{\text{UniquePurchaseDays}}{\text{CustomerTenureDays}} \times 100$

Percentage of days with purchases. Even loyal customers rarely exceed 10%. >20% suggests business/reseller account.

## KPI 30: AvgDaysBetweenOrders
**Formula:** $\text{AvgDaysBetweenOrders} = \frac{\text{CustomerTenureDays}}{\text{TotalOrders} - 1}$

Customer's natural purchase cycle. If typically 30 days but now 60 days → trigger reactivation.

---

# KPI 31-37: RFM Scoring Metrics

## KPI 31: RecencyScore

**Used in:** [CLV01] [CLV02] [CLV05]

### Definition
**RecencyScore** quantifies how recently a customer purchased, with different thresholds across analyses.

**CLV01 (0-100 scale):**
```sql
CASE
    WHEN DaysSinceLastPurchase <= 30 THEN 100
    WHEN DaysSinceLastPurchase <= 90 THEN 80
    WHEN DaysSinceLastPurchase <= 180 THEN 60
    WHEN DaysSinceLastPurchase <= 365 THEN 40
    WHEN DaysSinceLastPurchase <= 730 THEN 20
    ELSE 0
END
```

**CLV02 (1-5 scale):**
```sql
CASE
    WHEN DaysSinceLastPurchase <= 60 THEN 5
    WHEN DaysSinceLastPurchase <= 120 THEN 4
    WHEN DaysSinceLastPurchase <= 240 THEN 3
    WHEN DaysSinceLastPurchase <= 480 THEN 2
    ELSE 1
END
```

Recency is the strongest predictor of future purchase in all RFM analyses.

## KPI 33: FrequencyScore

**Used in:** [CLV02]

**Formula:** $\text{FrequencyScore} = \text{NTILE}_5(\text{TotalOrders}_{\text{asc}})$

Quintile ranking (1-5) based on order frequency. Score 5 = top 20% most frequent purchasers.

## KPI 35: MonetaryScore

**Used in:** [CLV02]

**Formula:** $\text{MonetaryScore} = \text{NTILE}_5(\text{TotalRevenue}_{\text{asc}})$

Quintile ranking (1-5) based on lifetime revenue. Score 5 = top 20% highest spenders. Often reveals Pareto: top 20% = 70-80% revenue.

## KPI 36: RFMString

**Used in:** [CLV02]

**Formula:** $\text{RFMString} = \text{concat}(R, F, M)$ where $R, F, M \in \{1,2,3,4,5\}$

3-digit identifier (e.g., "555" = champion, "111" = lost). 125 possible combinations enable granular segmentation.

## KPI 37: AvgRFMScore

**Used in:** [CLV02]

**Formula:** $\text{AvgRFMScore} = \frac{R + F + M}{3}$

Simple composite (range 1.00-5.00). Quick ranking but less nuanced than segment-based classification.

---

# KPI 38-42: Composite Scoring Metrics

## KPI 38: CustomerValueScore

**Used in:** [CLV01]

### Definition
Composite 0-100+ score combining: monetary (40%), frequency (32%), recency (20%), profitability (8%).

**SQL Expression:**
```sql
ROUND(
    (MonetaryQuintile * 20) +      -- 40% weight
    (FrequencyQuintile * 16) +     -- 32% weight
    (RecencyScore * 0.20) +        -- 20% weight
    (CASE WHEN LifetimeMarginPct > 30 THEN 8
          ELSE LifetimeMarginPct * 0.267 END)  -- 8% weight
, 2)
```

**Range:** ~20-208 (maximum: 20×5 + 16×5 + 0.20×100 + 8 = 208)

### Examples
- Champion: M=5, F=5, R=100, P=8 → Score = 208
- Loyal Regular: M=4, F=4, R=80, P=6 → Score = 166
- At-Risk High-Value: M=5, F=3, R=20, P=5 → Score = 153
- Low-Value Churned: M=1, F=1, R=0, P=1 → Score = 37

Single unified metric for customer ranking and resource allocation.

---

# KPI 43-45: Ranking Metrics

## KPI 43: RevenueRank

**Used in:** [CLV01]

**Formula:** $\text{RevenueRank}(c) = |\{c' : \text{Revenue}(c') > \text{Revenue}(c)\}| + 1$

Rank 1 = highest revenue. Identifies top contributors for VIP treatment.

## KPI 44: ValueRank

**Used in:** [CLV04]

Similar to RevenueRank but used in cross-sell context for value-based targeting.

## KPI 45: ProfitRank

**Used in:** [CLV01]

Rank by gross profit. More accurate than revenue for true value (high-margin customer with lower revenue may rank higher).

---

# KPI 46-48: Segmentation Classification

## KPI 46: CustomerTier

**Used in:** [CLV01]

**Classification:**
```sql
CASE
    WHEN CustomerValueScore >= 80 THEN 'Platinum'
    WHEN CustomerValueScore >= 60 THEN 'Gold'
    WHEN CustomerValueScore >= 40 THEN 'Silver'
    ELSE 'Bronze'
END
```

Simplified 4-tier segmentation for loyalty programs and service levels.

## KPI 47: RevenuePercentile

**Used in:** [CLV01]

**Classification:** Top 1%, Top 5%, Top 10%, Top 25%, Below Top 25%

Operationalizes Pareto: Top 1% (~100 customers per 10K) often = 30-50% of revenue.

## KPI 48: RFMSegment

**Used in:** [CLV02]

### Definition
11 strategic marketing segments based on RFM patterns:

1. **Champions** (R≥4, F≥4, M≥4): Best customers
2. **Loyal Customers** (F≥4, M≥4, R≥3): Frequent valuable customers
3. **Potential Loyalists** (R≥4, F≥3, M≥3): Recent with loyalty potential
4. **New Customers** (R≥4, F≤2): Recent but low frequency
5. **Promising** (R≥4, F≤3, M≤3): Recent moderate engagement
6. **Need Attention** (R=3, F≥3, M≥3): Starting to decline
7. **About To Sleep** (R=2, F≥3, M≥3): Declining but valuable
8. **At Risk** (R≤2, F≥4, M≥4): High-value churn risk
9. **Cannot Lose Them** (R=1, F≥4, M≥4): Critical recovery priority
10. **Hibernating** (R≤2, F≤3, M≤3): Dormant low-value
11. **Lost** (R=1, F≤2, M≤2): Effectively churned

Each segment has specific marketing actions and priorities.

---

# KPI 49-62: RFM Segment Analytics

**Used in:** [CLV02]

Aggregate statistics by RFMSegment:

- **CustomerCount**: Size of each segment
- **SegmentPct**: % of total customer base
- **AvgRecencyScore**: Validates segment recency patterns
- **AvgFrequencyScore**: Validates frequency patterns
- **AvgMonetaryScore**: Validates value patterns
- **AvgDaysSinceLastPurchase**: Concrete time metrics
- **AvgTotalOrders**: Typical engagement level
- **AvgLifetimeRevenue**: Average customer value
- **AvgLifetimeProfit**: Margin-adjusted value
- **TotalSegmentRevenue**: Absolute contribution
- **RevenueSharePct**: Proportional value (often Pareto)
- **AvgYearlyIncome**: Demographic patterns
- **Min/MaxLifetimeRevenue**: Internal variance
- **MarketingAction**: Specific recommended tactics
- **MarketingPriority**: Resource allocation level (High/Medium/Moderate/Low)
- **ExpectedROI**: Campaign return expectations (High/Medium/Low)

### Example Insights
- Champions (5% of customers) → 35% of revenue → High Priority → 5:1-20:1 ROI expected
- At Risk (4% of customers) → 15% of revenue → Medium Priority → Urgent intervention needed
- Lost (12% of customers) → 2% of revenue → Low Priority → Exclude from campaigns

---

# KPI 63-75: Lifecycle Stage Metrics

**Used in:** [CLV03]

## KPI 63: PreviousOrderDate

**SQL:** `LAG(OrderDate) OVER (PARTITION BY CustomerKey ORDER BY OrderDate)`

Date of previous order, enables inter-purchase interval calculation.

## KPI 64: DaysSincePreviousOrder

**Formula:** $\text{OrderDate} - \text{PreviousOrderDate}$

Time between consecutive orders. Lengthening intervals = early churn signal.

## KPI 69: LifecycleStage

### Definition
7-stage customer journey classification:

1. **New** (1-3 orders, <90 days tenure): Onboarding phase
2. **Developing** (4-10 orders, increasing frequency): Habit formation
3. **Growing** (11-25 orders, consistent engagement): Established loyalty
4. **Mature** (26+ orders, stable high value): Peak relationship
5. **At-Risk** (declining frequency, increasing intervals): Intervention needed
6. **Churned** (no orders >365 days): Lost customer
7. **Inactive** (no orders >730 days): Write-off candidate

**Business Purpose:** Lifecycle-appropriate interventions (onboarding vs. retention vs. win-back).

## KPI 70: NextTargetStage

Next logical lifecycle stage customer should progress toward.

## KPI 71: StageProgressionGap

Indicates how far customer is from next milestone.

## KPI 72: InterventionPriority

**Classification:** High, Medium, Low, Stable

At-Risk customers with high historical value = High priority intervention.

---

# KPI 76-85: Cross-Sell Opportunity Metrics

**Used in:** [CLV04]

## KPI 76: ValueQuartile

**Formula:** $\text{NTILE}_4(\text{LifetimeRevenue}_{\text{desc}})$

4-tier value segmentation (1=bottom 25%, 4=top 25%). Determines cross-sell investment level.

## KPI 77: ValueTier

**Classification:** High Value (Q4), Medium Value (Q3), Moderate Value (Q2), Low Value (Q1)

Business-friendly labels for ValueQuartile.

## KPI 78: CategoryPenetrationPct

**Formula:** $\frac{\text{UniqueCategories}}{\text{TotalAvailableCategories}} \times 100$

Percentage of categories purchased. Low penetration = high cross-sell opportunity.

## KPI 79: CategoryRevenue

Revenue from specific category, enables category-level value assessment.

## KPI 80: HasPurchasedCategory

Binary flag (1/0) indicating if customer has purchased from given category. Used for gap analysis.

## KPI 81: Category Affinity Patterns

**Metrics:** Category1, Category2, CustomerCount, AvgCombinedRevenue

Identifies which category pairs frequently co-occur. Example: "Bikes + Accessories" purchased together by 500 customers averaging $2,000.

## KPI 82: OpportunityCategory

Category customer hasn't purchased but has high affinity with their owned categories.

## KPI 83: OwnedCategory

Categories customer has already purchased from, used as basis for affinity matching.

## KPI 84: CrossSellPriority

**Classification:** Top, High, Medium, Low

Based on: ValueTier + CategoryPenetration + Affinity strength. High-value + low-penetration = Top priority.

## KPI 85: RecommendedApproach

Specific tactic by value tier:
- **High Value:** Personal outreach, curated bundles, VIP preview
- **Medium Value:** Email campaigns, dynamic recommendations
- **Moderate/Low Value:** Automated suggestions, mass promotions

---

# KPI 86-95: Churn Risk Prediction Metrics

**Used in:** [CLV05]

## KPI 86: RecencyRiskScore

**Range:** 0-35 points (35% of total risk)

**Formula:** Personalized to customer's AvgDaysBetweenOrders
```sql
CASE
    WHEN DaysSinceLastPurchase > AvgDaysBetweenOrders * 3.0 THEN 35
    WHEN DaysSinceLastPurchase > AvgDaysBetweenOrders * 2.0 THEN 25
    WHEN DaysSinceLastPurchase > AvgDaysBetweenOrders * 1.5 THEN 15
    WHEN DaysSinceLastPurchase > AvgDaysBetweenOrders * 1.0 THEN 5
    ELSE 0
END
```

Personalized recency risk: customer who usually orders every 30 days is at-risk at 45 days, but customer who orders every 90 days is normal at 45 days.

## KPI 87: ActivityDeclineScore

**Range:** 0-30 points (30% of total risk)

**Method:** Compares last 90 days order count to average 90-day periods. Declining activity = churn signal.

## KPI 88: RevenueDeclineScore

**Range:** 0-20 points (20% of total risk)

**Method:** Compares recent revenue to historical average. Spending decline = risk factor.

## KPI 89: LowEngagementScore

**Range:** 0-15 points (15% of total risk)

**Factors:** Low category penetration, low order frequency, single-category dependency. Structural engagement weaknesses.

## KPI 90: TotalChurnRiskScore

**Formula:** Sum of 4 components

$$\text{TotalChurnRiskScore} = \text{RecencyRisk} + \text{ActivityDecline} + \text{RevenueDecline} + \text{LowEngagement}$$

**Range:** 0-100 (100 = maximum risk)

Multi-dimensional churn prediction superior to recency alone.

## KPI 91: ChurnRiskCategory

**Classification:**
- **Critical** (80-100): Imminent churn, urgent action
- **High** (60-79): Significant risk, proactive intervention
- **Moderate** (40-59): Early warning, monitoring needed
- **Low** (20-39): Minimal risk, standard engagement
- **Healthy** (0-19): No risk, focus on growth

## KPI 92: TwoYearValueAtRisk

**Formula:** $\text{RevenuePerYear} \times 2$

Quantifies potential revenue loss if customer churns. Justifies retention investment.

Example: Customer with $50K/year → $100K value at risk over 2 years → Justify $5K-$10K retention spend.

## KPI 93: RetentionPriorityScore

**Formula:** $0.60 \times \text{ChurnRiskScore} + 0.40 \times \text{NormalizedValue}$

Balances risk urgency (60%) with customer value (40%). Prioritizes high-value at-risk customers over low-value at-risk.

## KPI 94: RetentionInvestmentRecommendation

**Calculation:** 5-20% of annual customer value, based on risk level and historical profitability.

Example: $10K/year customer at Critical risk → Recommend $1,000-$2,000 retention investment.

## KPI 95: RetentionAction

Specific playbooks by risk level:
- **Critical:** Executive outreach, deep discount, service recovery
- **High:** Personal call, special offer, satisfaction survey
- **Moderate:** Automated re-engagement, reminder emails
- **Low:** Standard communication
- **Healthy:** Growth campaigns, upsell opportunities

---

# Integrated Summary

## Framework Integration

This comprehensive CLV analytics framework combines five complementary approaches into a unified customer intelligence system:

### 1. Value Assessment (CLV01)
**Purpose:** Quantify and rank customer value
**Key Outputs:** CustomerValueScore, CustomerTier, Revenue/ProfitRank
**Decision Support:** Resource allocation, VIP program qualification, investment prioritization

### 2. Behavioral Segmentation (CLV02)
**Purpose:** Group customers by actionable behavior patterns
**Key Outputs:** RFMSegment (11 segments), MarketingAction, MarketingPriority
**Decision Support:** Campaign targeting, message personalization, channel selection

### 3. Journey Stage Analysis (CLV03)
**Purpose:** Track customer maturity and progression
**Key Outputs:** LifecycleStage (7 stages), InterventionPriority, NextTargetStage
**Decision Support:** Lifecycle-appropriate interventions, milestone programs, maturity tracking

### 4. Revenue Expansion (CLV04)
**Purpose:** Identify cross-sell and upsell opportunities
**Key Outputs:** CategoryPenetration, AffinityPatterns, CrossSellPriority, RecommendedApproach
**Decision Support:** Product recommendations, bundle design, category expansion

### 5. Churn Prevention (CLV05)
**Purpose:** Predict and prevent customer churn
**Key Outputs:** TotalChurnRiskScore (4 factors), ChurnRiskCategory, RetentionAction, ValueAtRisk
**Decision Support:** Proactive retention, intervention timing, retention ROI justification

## Analytical Architecture

### Progressive CTE Structure
All five analyses follow similar patterns:
1. **Foundation Layer:** Aggregate transaction data → customer summaries
2. **Enrichment Layer:** Calculate derived metrics, rates, ratios
3. **Scoring Layer:** Apply algorithms, rankings, quintiles
4. **Classification Layer:** Assign segments, tiers, categories
5. **Action Layer:** Generate specific recommendations

This enables both **operational execution** (individual actions) and **strategic analysis** (portfolio trends).

## Key Business Applications

### Customer Portfolio Management
- **Pareto Analysis:** Top 20% customers typically = 70-80% revenue
- **Risk Concentration:** Identify value-at-risk in declining segments
- **Growth Opportunity:** Low-penetration high-value customers
- **Efficiency:** Focus resources on high-ROI segments

### Predictive Interventions
- **Churn Prevention:** Multi-factor risk scoring enables proactive retention
- **Lifecycle Progression:** Accelerate New → Loyal transitions
- **Win-Back Economics:** Calculate max acceptable retention spend
- **Cross-Sell Timing:** Target high-affinity categories to engaged customers

### Resource Optimization
- **Marketing Budget:** Allocate by ExpectedROI and segment value
- **Service Levels:** Tier-based experiences (Platinum vs. Bronze)
- **Retention Investment:** Risk-adjusted spending (5-20% of annual value)
- **Channel Selection:** High-value = personal, Low-value = automated

### Strategic Planning
- **Cohort Analysis:** Track acquisition quality by FirstPurchaseDate
- **Trend Detection:** Monitor segment migrations (Champions → At Risk = alert)
- **Product Strategy:** High-margin customers guide assortment
- **Economic Modeling:** CAC payback via ProfitPerYear, CLV forecasting

## Critical Success Metrics

### Health Indicators
- **Champions + Loyal %:** Target 12-20% of customer base
- **At-Risk + Cannot Lose %:** Red flag if >10%
- **New Customer %:** Acquisition health indicator (15-25% ideal)
- **Lost Customer %:** Churn rate proxy (minimize)

### Value Concentration
- **Top 1% Revenue Share:** Typically 30-50% (monitor dependence)
- **Top 10% Revenue Share:** Typically 60-75%
- **At-Risk Segment Revenue:** Quantifies immediate risk
- **Average Revenue per Segment:** Validates targeting strategy

### Engagement Quality
- **Avg Days Since Last Purchase by Segment:** Recency validation
- **Segment Migration Rates:** Champions → At Risk = critical issue
- **Category Penetration Distribution:** Cross-sell potential
- **Lifecycle Stage Distribution:** Journey health check

## Implementation Priorities

### Phase 1: Foundation
1. Implement CLV01 (Value Scoring) for basic segmentation
2. Establish baseline metrics and benchmarks
3. Deploy CustomerTier classification for service differentiation

### Phase 2: Targeting
1. Add CLV02 (RFM Segmentation) for marketing campaigns
2. Implement segment-specific messaging and offers
3. Track campaign performance by segment

### Phase 3: Prevention
1. Deploy CLV05 (Churn Risk) for proactive retention
2. Establish retention playbooks by risk level
3. Calculate retention ROI and optimize spend

### Phase 4: Growth
1. Integrate CLV04 (Cross-Sell) for revenue expansion
2. Build affinity-based recommendation engine
3. Target high-value low-penetration customers

### Phase 5: Maturity
1. Add CLV03 (Lifecycle Stages) for journey optimization
2. Implement lifecycle-specific interventions
3. Track progression rates and optimize transitions

## Framework Advantages

### Holistic View
No single metric tells the complete story. This framework provides:
- **Value:** How much are they worth? (CLV01)
- **Behavior:** What patterns do they show? (CLV02)
- **Stage:** Where are they in the journey? (CLV03)
- **Opportunity:** What can we sell them? (CLV04)
- **Risk:** Will we lose them? (CLV05)

### Predictive Power
Multi-dimensional analysis superior to single-factor:
- Churn prediction: 4 factors (Recency + Activity + Revenue + Engagement) > recency alone
- Value scoring: Monetary + Frequency + Recency + Profitability > revenue alone
- Segmentation: 11 behavioral segments > simple quartiles

### Actionability
Every metric ties to specific business actions:
- Segments → Marketing tactics
- Risk scores → Retention playbooks
- Lifecycle stages → Appropriate interventions
- Cross-sell scores → Product recommendations
- Tiers → Service levels

### Measurability
Framework enables closed-loop optimization:
- Track segment migrations over time
- Measure intervention effectiveness
- Calculate retention ROI
- Optimize resource allocation
- Validate predictions against actual outcomes

## Technical Considerations

### Data Requirements
- **Minimum:** CustomerKey, OrderDate, SalesAmount, ProductKey
- **Recommended:** TotalProductCost (for margin), DiscountAmount, ProductCategory
- **Optional:** CustomerDemographics (YearlyIncome, etc.)

### Refresh Frequency
- **Daily:** Churn risk scores (time-sensitive)
- **Weekly:** RFM segments, lifecycle stages
- **Monthly:** Value scores, cross-sell recommendations
- **Quarterly:** Strategic portfolio analysis

### Scalability
- All queries use window functions and CTEs (efficient for OLAP databases)
- Indexed on CustomerKey, OrderDate enables fast computation
- Can process millions of customers and transactions
- Suitable for both batch (overnight) and near-real-time (streaming)

---

**This integrated framework provides a complete, actionable customer analytics system that enables data-driven decisions across acquisition, engagement, retention, and growth initiatives.**
