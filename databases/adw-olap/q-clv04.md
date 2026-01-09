# Cross-Sell Opportunity Analysis - KPI Documentation

This document provides a comprehensive analysis of all Key Performance Indicators (KPIs) calculated in the cross-sell opportunity SQL query. The query uses product category affinity patterns to identify targeted cross-sell opportunities for high-value customers.

---

# KPI 1: LifetimeRevenue

## Definition
**LifetimeRevenue** sums the total sales amount across all purchases for each customer, representing their total monetary contribution to the business.

**SQL Expression:**
```sql
ROUND(SUM(fis.SalesAmount), 2) AS LifetimeRevenue
```

**Mathematical Formula:**
$$\text{LifetimeRevenue} = \sum_{i=1}^{n} \text{SalesAmount}_i$$

where $n$ is the total number of transactions for the customer.

**Business Purpose:** Primary customer value metric used for segmentation and prioritization of cross-sell efforts.

## Examples
- Customer A: $75,000 lifetime revenue → high-value target
- Customer B: $12,000 lifetime revenue → medium-value target
- Customer C: $2,500 lifetime revenue → low-value target

---

# KPI 2: TotalOrders

## Definition
**TotalOrders** counts the number of distinct orders a customer has placed over their lifetime, measuring purchase frequency.

**SQL Expression:**
```sql
COUNT(DISTINCT fis.SalesOrderNumber) AS TotalOrders
```

**Mathematical Formula:**
$$\text{TotalOrders} = |\{\text{SalesOrderNumber}_i : i \in \text{all transactions}\}|$$

**Business Purpose:** Indicates customer engagement level and purchasing habits. Higher order counts suggest more established relationships.

## Examples
- Customer A: 45 orders → highly engaged
- Customer B: 8 orders → moderately engaged
- Customer C: 2 orders → early stage customer

---

# KPI 3: ValueQuartile

## Definition
**ValueQuartile** divides all customers into four equal groups (quartiles) based on lifetime revenue, with 1 being the top 25% highest-value customers and 4 being the bottom 25%.

**SQL Expression:**
```sql
NTILE(4) OVER (ORDER BY SUM(fis.SalesAmount) DESC) AS ValueQuartile
```

**Mathematical Formula:**
$$\text{ValueQuartile} = \text{NTILE}_4(\text{LifetimeRevenue}_{\text{desc}})$$

This divides customers into 4 equal-sized groups ranked by revenue (descending).

**Values:** 1, 2, 3, 4 where:
- 1 = Top quartile (top 25%, highest revenue)
- 2 = Second quartile (25th-50th percentile)
- 3 = Third quartile (50th-75th percentile)
- 4 = Bottom quartile (bottom 25%, lowest revenue)

**Business Purpose:** Enables quartile-based analysis and targeting. Focuses cross-sell efforts on top quartiles with highest value potential.

## Examples
With 10,000 customers and $50M total revenue:
- **Quartile 1**: 2,500 customers with highest revenue (~$30M, avg $12K per customer)
- **Quartile 2**: 2,500 customers ($12M, avg $4.8K per customer)
- **Quartile 3**: 2,500 customers ($6M, avg $2.4K per customer)
- **Quartile 4**: 2,500 customers with lowest revenue ($2M, avg $800 per customer)

---

# KPI 4: ValueTier

## Definition
**ValueTier** translates the ValueQuartile into descriptive customer value segments with business-friendly labels for easier communication and targeting.

**SQL Expression:**
```sql
CASE
    WHEN NTILE(4) OVER (ORDER BY SUM(fis.SalesAmount) DESC) = 1 THEN 'High Value'
    WHEN NTILE(4) OVER (ORDER BY SUM(fis.SalesAmount) DESC) = 2 THEN 'Medium-High Value'
    WHEN NTILE(4) OVER (ORDER BY SUM(fis.SalesAmount) DESC) = 3 THEN 'Medium-Low Value'
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

**Tier Characteristics:**

### High Value (Q1)
- Top 25% of customers by revenue
- Highest cross-sell potential
- Warrant personalized attention
- Premium targeting strategies

### Medium-High Value (Q2)
- 25th-50th percentile
- Solid value contributors
- Good cross-sell candidates
- Targeted automated campaigns

### Medium-Low Value (Q3)
- 50th-75th percentile
- Moderate value
- Selective cross-sell efforts
- General promotional campaigns

### Low Value (Q4)
- Bottom 25% by revenue
- Limited cross-sell focus
- Minimal investment
- Mass marketing only

**Business Purpose:** Provides intuitive segmentation for campaign design and resource allocation. Cross-sell analysis focuses primarily on High Value and Medium-High Value tiers.

## Examples
- Customer with $75,000 lifetime revenue → Quartile 1 → "High Value"
- Customer with $12,000 lifetime revenue → Quartile 2 → "Medium-High Value"
- Customer with $3,500 lifetime revenue → Quartile 3 → "Medium-Low Value"
- Customer with $800 lifetime revenue → Quartile 4 → "Low Value"

---

# KPI 5: CategoryName

## Definition
**CategoryName** identifies the product category (from DimProductCategory) for which purchases are being analyzed. This is the primary dimension for cross-sell analysis.

**SQL Expression:**
```sql
pc.EnglishProductCategoryName AS CategoryName
```

**Business Purpose:** Enables category-level purchase behavior analysis and cross-sell recommendations based on category affinity patterns.

## Examples
For a bike retailer, categories might include:
- "Bikes"
- "Clothing"
- "Accessories"
- "Components"

---

# KPI 6: FirstCategoryPurchaseDate

## Definition
**FirstCategoryPurchaseDate** records the date when a customer first purchased from a specific product category, establishing category adoption timeline.

**SQL Expression:**
```sql
MIN(fis.OrderDate) AS FirstCategoryPurchaseDate
```

**Mathematical Formula:**
$$\text{FirstCategoryPurchaseDate}_c = \min_{i \in \text{category } c}(\text{OrderDate}_i)$$

**Business Purpose:** Tracks category adoption patterns and identifies time elapsed since category entry, useful for understanding cross-category purchase sequencing.

## Examples
Customer A's category timeline:
- Bikes: First purchase 2023-01-15 (entry category)
- Accessories: First purchase 2023-02-20 (35 days after Bikes)
- Clothing: First purchase 2023-06-10 (146 days after Bikes)
- Components: Never purchased → NULL

**Insight:** Accessories typically purchased within 30-60 days of bike purchase.

---

# KPI 7: LastCategoryPurchaseDate

## Definition
**LastCategoryPurchaseDate** records the date of the customer's most recent purchase within a specific category, indicating category recency.

**SQL Expression:**
```sql
MAX(fis.OrderDate) AS LastCategoryPurchaseDate
```

**Mathematical Formula:**
$$\text{LastCategoryPurchaseDate}_c = \max_{i \in \text{category } c}(\text{OrderDate}_i)$$

**Business Purpose:** Identifies active vs. dormant category relationships, useful for category-specific reactivation campaigns.

## Examples
Customer B's category recency:
- Bikes: Last purchase 2024-11-15 (recent, active)
- Accessories: Last purchase 2023-06-20 (18 months ago, dormant)
- Clothing: Last purchase 2024-12-01 (very recent)

**Application:** Customer B is a candidate for accessories reactivation campaign.

---

# KPI 8: CategoryOrders

## Definition
**CategoryOrders** counts the number of distinct orders a customer has placed within a specific product category, measuring category-specific engagement.

**SQL Expression:**
```sql
COUNT(DISTINCT fis.SalesOrderNumber) AS CategoryOrders
```

**Mathematical Formula:**
$$\text{CategoryOrders}_c = |\{\text{SalesOrderNumber}_i : i \in \text{category } c\}|$$

**Business Purpose:** Indicates category loyalty and depth of engagement within specific product lines.

## Examples
Customer C's category order distribution:
- Bikes: 3 orders (occasional bike upgrader)
- Accessories: 25 orders (highly engaged with accessories)
- Clothing: 8 orders (moderate engagement)
- Components: 0 orders (no engagement)

**Insight:** Customer C is an accessories enthusiast, prime candidate for new accessory launches.

---

# KPI 9: CategoryLineItems

## Definition
**CategoryLineItems** counts the total number of individual line items (products) purchased within a category, indicating purchase volume at the most granular level.

**SQL Expression:**
```sql
COUNT(*) AS CategoryLineItems
```

**Mathematical Formula:**
$$\text{CategoryLineItems}_c = \sum_{i \in \text{category } c} 1$$

**Relationship:**
$$\text{CategoryLineItems} \geq \text{CategoryOrders}$$

Equality holds when customer always buys exactly one item per category order.

**Business Purpose:** Measures basket size within categories. High line items relative to orders indicates multi-item category purchases.

## Examples
Customer D's category purchase patterns:
- Bikes: 3 orders, 3 line items → 1.0 items/order (single bike per order)
- Accessories: 15 orders, 75 line items → 5.0 items/order (multi-item baskets)
- Clothing: 8 orders, 20 line items → 2.5 items/order (moderate baskets)

**Insight:** Customer D buys accessories in bulk but bikes individually.

---

# KPI 10: CategoryRevenue

## Definition
**CategoryRevenue** sums the total sales amount within a specific product category for each customer, showing category-specific value contribution.

**SQL Expression:**
```sql
ROUND(SUM(fis.SalesAmount), 2) AS CategoryRevenue
```

**Mathematical Formula:**
$$\text{CategoryRevenue}_c = \sum_{i \in \text{category } c} \text{SalesAmount}_i$$

**Relationship:**
$$\sum_{\text{all categories } c} \text{CategoryRevenue}_c = \text{LifetimeRevenue}$$

**Business Purpose:** Identifies which categories drive customer value. Enables category contribution analysis and wallet share estimation.

## Examples
Customer E's category revenue breakdown (Total: $50,000):
- Bikes: $35,000 (70% of wallet) → primary category
- Accessories: $8,000 (16%)
- Clothing: $5,000 (10%)
- Components: $2,000 (4%)

**Share of Wallet Analysis:** 70% in Bikes suggests limited category diversification opportunity.

---

# KPI 11: CategoryGrossProfit

## Definition
**CategoryGrossProfit** calculates the total gross profit (revenue minus product costs) within a category for each customer, showing category-specific margin contribution.

**SQL Expression:**
```sql
ROUND(SUM(fis.SalesAmount - fis.TotalProductCost), 2) AS CategoryGrossProfit
```

**Mathematical Formula:**
$$\text{CategoryGrossProfit}_c = \sum_{i \in \text{category } c} (\text{SalesAmount}_i - \text{TotalProductCost}_i)$$

**Business Purpose:** More accurate than revenue for assessing category value, accounting for margin differences across categories.

## Examples
Customer F's category profit distribution (Total: $20,000 profit):
- Bikes: $8,000 profit on $35,000 revenue → 22.9% margin
- Accessories: $6,000 profit on $8,000 revenue → 75% margin (high-margin!)
- Clothing: $4,000 profit on $5,000 revenue → 80% margin (highest margin!)
- Components: $2,000 profit on $2,000 revenue → 100% margin (unlikely, may be error)

**Strategic Insight:** Accessories and Clothing generate more profit than their revenue share suggests. Prioritize cross-selling these high-margin categories.

---

# KPI 12: UniqueProductsInCategory

## Definition
**UniqueProductsInCategory** counts the number of distinct products (SKUs) a customer has purchased within a specific category, measuring product diversity within the category.

**SQL Expression:**
```sql
COUNT(DISTINCT fis.ProductKey) AS UniqueProductsInCategory
```

**Mathematical Formula:**
$$\text{UniqueProductsInCategory}_c = |\{\text{ProductKey}_i : i \in \text{category } c\}|$$

**Business Purpose:** Indicates breadth of exploration within a category. Low values suggest opportunity for within-category expansion.

## Examples
Bikes category (assume 50 SKUs available):
- Customer A: 1 unique product → 2% penetration (single bike owner)
- Customer B: 3 unique products → 6% penetration (bike collector)
- Customer C: 8 unique products → 16% penetration (enthusiast/reseller?)

Accessories category (assume 200 SKUs available):
- Customer A: 5 unique products → 2.5% penetration (narrow accessory use)
- Customer B: 45 unique products → 22.5% penetration (diverse accessory buyer)

---

# KPI 13: HasPurchasedCategory

## Definition
**HasPurchasedCategory** is a binary flag (0 or 1) indicating whether a customer has ever purchased from a specific category. This is fundamental to cross-sell opportunity identification.

**SQL Expression:**
```sql
CASE WHEN ccp.CustomerKey IS NOT NULL THEN 1 ELSE 0 END AS HasPurchasedCategory
```

**Mathematical Formula:**
$$\text{HasPurchasedCategory}_c = \begin{cases}
1 & \text{if customer has purchased from category } c \\
0 & \text{if customer has never purchased from category } c
\end{cases}$$

**Business Purpose:** Core metric for identifying cross-sell gaps. Categories with 0 represent expansion opportunities.

## Examples
Customer G's category purchase matrix:
- Bikes: HasPurchasedCategory = 1 ✓
- Accessories: HasPurchasedCategory = 1 ✓
- Clothing: HasPurchasedCategory = 0 ✗ (cross-sell opportunity!)
- Components: HasPurchasedCategory = 0 ✗ (cross-sell opportunity!)

**Targeting:** Customer G should receive Clothing and Components cross-sell campaigns.

---

# KPI 14: TotalCategories

## Definition
**TotalCategories** counts the total number of distinct product categories available in the catalog that could be purchased.

**SQL Expression:**
```sql
COUNT(*) AS TotalCategories
```

**Mathematical Formula:**
$$\text{TotalCategories} = |\text{AllCategories}|$$

This is constant for all customers in a given analysis period.

**Business Purpose:** Denominator for penetration calculations. Defines the full opportunity space.

## Examples
- Bike retailer with 4 categories: TotalCategories = 4
- Electronics retailer with 15 categories: TotalCategories = 15
- Department store with 50 categories: TotalCategories = 50

---

# KPI 15: CategoriesPurchased

## Definition
**CategoriesPurchased** counts how many distinct product categories a customer has purchased from, measuring cross-category engagement breadth.

**SQL Expression:**
```sql
SUM(ccm.HasPurchasedCategory) AS CategoriesPurchased
```

**Mathematical Formula:**
$$\text{CategoriesPurchased} = \sum_{c \in \text{all categories}} \text{HasPurchasedCategory}_c$$

**Relationship:**
$$0 \leq \text{CategoriesPurchased} \leq \text{TotalCategories}$$

**Business Purpose:** Key indicator of customer engagement breadth. Higher values indicate deeper product range adoption and lower churn risk.

## Examples
Retailer with 4 categories (Bikes, Accessories, Clothing, Components):
- Customer A: Purchased from all 4 categories → CategoriesPurchased = 4 (full engagement)
- Customer B: Purchased from 2 categories → CategoriesPurchased = 2 (partial engagement)
- Customer C: Purchased from 1 category → CategoriesPurchased = 1 (single-category buyer)

**Research Finding:** Customers who purchase from 3+ categories have 60% lower churn than single-category buyers.

---

# KPI 16: CategoriesNotPurchased

## Definition
**CategoriesNotPurchased** counts how many product categories a customer has NOT yet purchased from, representing the untapped expansion opportunity.

**SQL Expression:**
```sql
COUNT(*) - SUM(ccm.HasPurchasedCategory) AS CategoriesNotPurchased
```

**Mathematical Formula:**
$$\text{CategoriesNotPurchased} = \text{TotalCategories} - \text{CategoriesPurchased}$$

**Relationship:**
$$\text{CategoriesPurchased} + \text{CategoriesNotPurchased} = \text{TotalCategories}$$

**Business Purpose:** Quantifies cross-sell opportunity size. High values in high-value customers represent significant revenue potential.

## Examples
Retailer with 4 categories:
- Customer A (CategoriesPurchased = 1): CategoriesNotPurchased = 3 (large opportunity)
- Customer B (CategoriesPurchased = 3): CategoriesNotPurchased = 1 (small opportunity)
- Customer C (CategoriesPurchased = 4): CategoriesNotPurchased = 0 (saturated, no cross-sell opportunity)

**Prioritization:** High-value customers with high CategoriesNotPurchased are top cross-sell targets.

---

# KPI 17: CategoryPenetrationPct

## Definition
**CategoryPenetrationPct** calculates the percentage of available product categories from which a customer has purchased, measuring catalog adoption completeness.

**SQL Expression:**
```sql
ROUND(100.0 * SUM(ccm.HasPurchasedCategory) / COUNT(*), 2) AS CategoryPenetrationPct
```

**Mathematical Formula:**
$$\text{CategoryPenetrationPct} = \frac{\text{CategoriesPurchased}}{\text{TotalCategories}} \times 100$$

**Range:** 0% to 100%

**Business Purpose:** Normalized measure of cross-category engagement that's comparable across different catalog sizes.

## Examples
Retailer with 4 categories:
- Customer A purchased from 4 categories → 100% penetration (complete)
- Customer B purchased from 3 categories → 75% penetration (high)
- Customer C purchased from 2 categories → 50% penetration (medium)
- Customer D purchased from 1 category → 25% penetration (low, high opportunity)

**Benchmark Targets:**
- Excellent: >75% penetration
- Good: 50-75% penetration
- Needs Improvement: 25-50% penetration
- High Opportunity: <25% penetration

**Strategic Goal:** Move high-value customers from low penetration to >50% penetration.

---

# KPI 18: PurchasedCategories

## Definition
**PurchasedCategories** creates a comma-separated list of all product categories from which the customer has purchased, providing a quick overview of category engagement.

**SQL Expression:**
```sql
STRING_AGG(CASE WHEN ccm.HasPurchasedCategory = 1 THEN ccm.CategoryName END, ', ') AS PurchasedCategories
```

**Business Purpose:** Human-readable summary of customer's category portfolio for segmentation and campaign personalization.

## Examples
- Customer A: "Bikes, Accessories, Clothing, Components" (full engagement)
- Customer B: "Bikes, Accessories" (bike-focused)
- Customer C: "Accessories, Clothing" (non-bike customer, interesting segment!)
- Customer D: "Bikes" (single-category buyer)

**Segmentation Use:**
- "Bikes" only → Bike purist segment
- "Accessories, Clothing" → Lifestyle/apparel segment
- All categories → Complete customer segment

---

# KPI 19: UnpurchasedCategories

## Definition
**UnpurchasedCategories** creates a comma-separated list of product categories the customer has NOT purchased from, highlighting specific cross-sell opportunities.

**SQL Expression:**
```sql
STRING_AGG(CASE WHEN ccm.HasPurchasedCategory = 0 THEN ccm.CategoryName END, ', ') AS UnpurchasedCategories
```

**Business Purpose:** Directly identifies cross-sell targets for personalized campaigns. Enables category-specific messaging.

## Examples
- Customer A: NULL or empty (has purchased from all categories)
- Customer B: "Clothing, Components" → Target with clothing and components campaigns
- Customer C: "Bikes" → Target with bike campaigns (despite having accessories/clothing)
- Customer D: "Accessories, Clothing, Components" → Multi-category opportunity

**Campaign Application:**
- Customer B message: "You've enjoyed our bikes and accessories. Discover our premium cycling apparel!"
- Customer C message: "Ready to upgrade your ride? Explore our bike collection."

---

# KPI 20: Category1 & Category2 (Affinity Pairs)

## Definition
**Category1** and **Category2** represent a pair of product categories that are frequently purchased together by customers, forming an affinity relationship.

**SQL Expression:**
```sql
ccp1.CategoryName AS Category1,
ccp2.CategoryName AS Category2
```

**Constraint:**
```sql
ccp1.CategoryName < ccp2.CategoryName
```

This ensures each category pair appears only once (avoiding duplicates like "A,B" and "B,A").

**Business Purpose:** Identifies natural product relationships and cross-sell patterns based on actual customer behavior.

## Examples
Strong affinity pairs:
- Category1: "Bikes", Category2: "Accessories" (bike buyers often buy accessories)
- Category1: "Bikes", Category2: "Components" (bike buyers upgrade components)
- Category1: "Accessories", Category2: "Clothing" (gear buyers also buy apparel)

Weak affinity pairs:
- Category1: "Bikes", Category2: "Clothing" (less common together)

---

# KPI 21: CustomerCount (Affinity Strength)

## Definition
**CustomerCount** in the CategoryAffinityPatterns CTE counts how many distinct customers have purchased from both categories in an affinity pair, quantifying the strength of the category relationship.

**SQL Expression:**
```sql
COUNT(DISTINCT ccp1.CustomerKey) AS CustomerCount
```

**Mathematical Formula:**
$$\text{CustomerCount}_{(c_1, c_2)} = |\{k : k \text{ purchased from both } c_1 \text{ and } c_2\}|$$

**Minimum Threshold:**
```sql
HAVING COUNT(DISTINCT ccp1.CustomerKey) >= 10
```

Only pairs with 10+ customers are considered significant.

**Business Purpose:** Measures affinity strength. Higher counts indicate stronger cross-sell relationships and more reliable recommendations.

## Examples
Category affinity analysis with 5,000 total customers:
- Bikes + Accessories: 2,500 customers (50% of customers, very strong affinity)
- Bikes + Components: 1,200 customers (24%, strong affinity)
- Accessories + Clothing: 1,800 customers (36%, strong affinity)
- Bikes + Clothing: 800 customers (16%, moderate affinity)
- Components + Clothing: 150 customers (3%, weak affinity)

**Recommendation Priority:**
1. Bikes → Accessories (strongest, 50% adoption rate)
2. Accessories → Clothing (strong, 36% adoption rate)
3. Bikes → Components (strong, 24% adoption rate)

---

# KPI 22: AvgCombinedRevenue

## Definition
**AvgCombinedRevenue** calculates the average total revenue generated from both categories in an affinity pair across customers who purchased from both, indicating the revenue potential of the category combination.

**SQL Expression:**
```sql
ROUND(AVG(ccp1.CategoryRevenue + ccp2.CategoryRevenue), 2) AS AvgCombinedRevenue
```

**Mathematical Formula:**
$$\text{AvgCombinedRevenue}_{(c_1, c_2)} = \frac{1}{n}\sum_{k \in \text{both}} (\text{CategoryRevenue}_{k,c_1} + \text{CategoryRevenue}_{k,c_2})$$

where $n$ is the number of customers who purchased from both categories.

**Business Purpose:** Estimates revenue uplift potential from successfully cross-selling the category pair. Helps prioritize high-value affinity relationships.

## Examples
Category pair revenue analysis:
- **Bikes + Accessories**: 2,500 customers, $8,500 avg combined revenue
  - Interpretation: Customers who buy both spend avg $8,500 across these categories
- **Bikes + Components**: 1,200 customers, $12,000 avg combined revenue
  - Interpretation: Component buyers are high-value (upgrades/enthusiasts)
- **Accessories + Clothing**: 1,800 customers, $3,000 avg combined revenue
  - Interpretation: Lower value but high volume opportunity

**Strategic Prioritization:**
- High CustomerCount + High AvgCombinedRevenue = Top priority (Bikes + Accessories)
- High CustomerCount + Lower AvgCombinedRevenue = Volume opportunity (Accessories + Clothing)
- Lower CustomerCount + High AvgCombinedRevenue = Niche/specialist (Bikes + Components)

---

# KPI 23: OpportunityCategory

## Definition
**OpportunityCategory** identifies a specific product category that represents a cross-sell opportunity for a customer—a category they haven't purchased from but that shows strong affinity with categories they own.

**SQL Expression:**
```sql
ccm.CategoryName AS OpportunityCategory
```

**Constraint:**
```sql
ccm.HasPurchasedCategory = 0
```

The customer has NOT purchased from this category.

**Business Purpose:** Pinpoints specific categories to recommend in cross-sell campaigns.

## Examples
Customer H owns: Bikes, Accessories
- **OpportunityCategory**: "Clothing" (has affinity with Accessories which customer owns)
- **OpportunityCategory**: "Components" (has affinity with Bikes which customer owns)

Customer H does NOT own: Clothing, Components
- These become cross-sell targets

---

# KPI 24: OwnedCategory

## Definition
**OwnedCategory** identifies a product category the customer has already purchased from, which forms the basis for the cross-sell recommendation through its affinity relationship.

**SQL Expression:**
```sql
cap.Category1 AS OwnedCategory
```

**Constraint:**
```sql
ccm_owned.HasPurchasedCategory = 1
```

The customer HAS purchased from this category.

**Business Purpose:** Provides context for the recommendation. Enables messaging like "Since you bought [OwnedCategory], you'll love [OpportunityCategory]."

## Examples
Customer I recommendation chain:
- **OwnedCategory**: "Bikes"
- **OpportunityCategory**: "Accessories"
- **Message**: "Since you bought a bike, you'll need these essential accessories!"

Customer J recommendation chain:
- **OwnedCategory**: "Accessories"
- **OpportunityCategory**: "Clothing"
- **Message**: "Accessory lovers like you also enjoy our performance cycling apparel!"

---

# KPI 25: AffinityStrength

## Definition
**AffinityStrength** represents the number of customers who have purchased both the owned category and the opportunity category, serving as a confidence measure for the cross-sell recommendation.

**SQL Expression:**
```sql
cap.CustomerCount AS AffinityStrength
```

This is the same as CustomerCount from CategoryAffinityPatterns, but contextualized as a recommendation confidence score.

**Mathematical Formula:**
$$\text{AffinityStrength} = |\{\text{customers who bought both categories}\}|$$

**Business Purpose:** Higher values indicate more reliable recommendations based on broader customer behavior patterns. Low values suggest speculative or niche opportunities.

## Examples
Recommendation confidence levels:
- AffinityStrength = 2,500: Very high confidence (50% of 5,000 customers)
- AffinityStrength = 500: High confidence (10% of customers)
- AffinityStrength = 50: Moderate confidence (1% of customers)
- AffinityStrength = 10: Low confidence (minimum threshold, 0.2%)

**Usage in Messaging:**
- High strength (1000+): "Thousands of bike owners also love our accessories!"
- Medium strength (100-999): "Hundreds of customers have discovered this combination!"
- Low strength (10-99): "Customers like you have found value in this pairing!"

---

# KPI 26: PotentialRevenue

## Definition
**PotentialRevenue** estimates the expected revenue from a successful cross-sell, based on the average combined revenue from customers who have purchased both categories in the affinity pair.

**SQL Expression:**
```sql
cap.AvgCombinedRevenue AS PotentialRevenue
```

This is the same as AvgCombinedRevenue from CategoryAffinityPatterns, but contextualized as a revenue opportunity estimate.

**Mathematical Formula:**
$$\text{PotentialRevenue} = \text{AvgCombinedRevenue of affinity pair}$$

**Business Purpose:** Quantifies the revenue opportunity, enabling ROI-based prioritization of cross-sell campaigns. Helps determine appropriate campaign investment levels.

## Examples
Cross-sell ROI analysis:

**Opportunity A:**
- Customer owns: Bikes ($3,500 spent)
- Recommend: Accessories
- PotentialRevenue: $8,500 (combined average)
- Expected incremental revenue: ~$5,000
- Campaign cost: $50 per customer
- Expected ROI: $5,000 / $50 = 100x (if 100% conversion, 10x if 10% conversion)

**Opportunity B:**
- Customer owns: Accessories ($800 spent)
- Recommend: Clothing
- PotentialRevenue: $3,000 (combined average)
- Expected incremental revenue: ~$2,200
- Campaign cost: $20 per customer
- Expected ROI: $2,200 / $20 = 110x (if 100% conversion)

**Investment Decision:** Both opportunities justify investment, but Opportunity A has higher absolute potential.

---

# KPI 27: OpportunityRank

## Definition
**OpportunityRank** ranks cross-sell opportunities for each customer based on affinity strength and revenue potential, with rank 1 being the best opportunity for that customer.

**SQL Expression:**
```sql
RANK() OVER (PARTITION BY ccm.CustomerKey ORDER BY cap.CustomerCount DESC, cap.AvgCombinedRevenue DESC) AS OpportunityRank
```

**Mathematical Formula:**
For customer $k$:
$$\text{OpportunityRank}_k = \text{RANK}(\text{opportunities ordered by AffinityStrength desc, then PotentialRevenue desc})$$

**Ranking Logic:**
1. Primary sort: AffinityStrength (higher is better)
2. Secondary sort: PotentialRevenue (higher is better)

**Business Purpose:** Prioritizes which categories to recommend first for each customer. Limits campaign fatigue by focusing on top opportunities.

## Examples
Customer K's ranked opportunities:
1. **Rank 1**: Accessories (AffinityStrength: 2,500, PotentialRevenue: $8,500) → Top priority
2. **Rank 2**: Components (AffinityStrength: 1,200, PotentialRevenue: $12,000) → Second priority
3. **Rank 3**: Clothing (AffinityStrength: 800, PotentialRevenue: $5,000) → Third priority

**Campaign Strategy:**
- Send Rank 1 opportunity immediately
- Send Rank 2 opportunity 2 weeks later if no response
- Send Rank 3 opportunity 4 weeks later if no response
- Do not send Ranks 4+ to avoid over-communication

---

# KPI 28: RecommendedCategory

## Definition
**RecommendedCategory** is the final cross-sell recommendation—the specific product category to promote to the customer based on top-ranked affinity opportunities.

**SQL Expression:**
```sql
cso.OpportunityCategory AS RecommendedCategory
```

**Business Purpose:** The actionable output for marketing campaigns. This category becomes the focus of personalized product recommendations and targeted promotions.

## Examples
Personalized cross-sell campaigns:

**Customer L** (High Value, owns Bikes):
- RecommendedCategory: "Accessories"
- Campaign: Email showcasing bike accessories with 15% discount
- Subject: "Complete Your Ride: Essential Accessories for Your Bike"

**Customer M** (High Value, owns Bikes + Accessories):
- RecommendedCategory: "Clothing"
- Campaign: Personalized lookbook of cycling apparel
- Subject: "Upgrade Your Style: Premium Cycling Apparel Just for You"

**Customer N** (Medium-High Value, owns Accessories):
- RecommendedCategory: "Bikes"
- Campaign: Entry-level bike promotion with trade-in offer
- Subject: "Ready to Ride? Special Offer on Your First Bike"

---

# KPI 29: BasedOnOwnership

## Definition
**BasedOnOwnership** shows which category the customer already owns that forms the basis for the cross-sell recommendation, providing the rationale for the suggestion.

**SQL Expression:**
```sql
cso.OwnedCategory AS BasedOnOwnership
```

**Business Purpose:** Enables contextual, relevance-based messaging that connects the recommendation to the customer's existing purchases.

## Examples
Recommendation justification:

**Recommendation 1:**
- RecommendedCategory: "Accessories"
- BasedOnOwnership: "Bikes"
- Message: "Since you purchased a bike, these accessories will enhance your riding experience..."

**Recommendation 2:**
- RecommendedCategory: "Clothing"
- BasedOnOwnership: "Accessories"
- Message: "Accessory enthusiasts like you appreciate quality. Check out our cycling apparel..."

**Recommendation 3:**
- RecommendedCategory: "Components"
- BasedOnOwnership: "Bikes"
- Message: "Upgrade your bike's performance with these premium components..."

**Personalization Power:** Increases conversion rates by demonstrating relevance and understanding of customer's existing interests.

---

# KPI 30: CrossSellPriority

## Definition
**CrossSellPriority** assigns a priority level (Top/High/Medium/Low) to each cross-sell opportunity based on its OpportunityRank, guiding campaign timing and investment levels.

**SQL Expression:**
```sql
CASE
    WHEN cso.OpportunityRank = 1 THEN 'Top Priority'
    WHEN cso.OpportunityRank <= 3 THEN 'High Priority'
    WHEN cso.OpportunityRank <= 5 THEN 'Medium Priority'
    ELSE 'Low Priority'
END AS CrossSellPriority
```

**Mathematical Formula:**
$$\text{CrossSellPriority} = \begin{cases}
\text{Top Priority} & \text{if OpportunityRank} = 1 \\
\text{High Priority} & \text{if } 1 < \text{OpportunityRank} \leq 3 \\
\text{Medium Priority} & \text{if } 3 < \text{OpportunityRank} \leq 5 \\
\text{Low Priority} & \text{if OpportunityRank} > 5
\end{cases}$$

**Priority Definitions:**

### Top Priority (Rank 1)
- Best opportunity for this customer
- Highest affinity strength
- Immediate action warranted
- Maximum investment justified
- Personalized outreach for high-value customers

### High Priority (Ranks 2-3)
- Strong opportunities
- Secondary recommendations
- Send if Rank 1 fails or after conversion
- Targeted campaigns
- Good ROI expected

### Medium Priority (Ranks 4-5)
- Moderate opportunities
- Tertiary recommendations
- Include in broader campaigns
- Lower investment
- Acceptable ROI

### Low Priority (Ranks 6+)
- Weakest opportunities (filtered out by query)
- Include only in mass campaigns
- Minimal investment
- Low expected ROI

**Business Purpose:** Structures campaign workflows and resource allocation. Prevents over-communication while maximizing opportunity capture.

## Examples
Customer O's cross-sell campaign schedule:

**Week 1: Top Priority**
- RecommendedCategory: Accessories
- Priority: Top Priority
- Action: Personalized email + product recommendations on website

**Week 3: High Priority (if no conversion)**
- RecommendedCategory: Components
- Priority: High Priority
- Action: Targeted email with discount code

**Week 6: High Priority (if still no conversion)**
- RecommendedCategory: Clothing
- Priority: High Priority
- Action: Retargeting ads + email

**Week 9: Medium Priority**
- Lower priorities included in general promotional emails

---

# KPI 31: RecommendedApproach

## Definition
**RecommendedApproach** provides specific tactical guidance for how to execute the cross-sell campaign, varying by customer ValueTier and OpportunityRank to optimize conversion and ROI.

**SQL Expression:**
```sql
CASE
    WHEN cso.ValueTier = 'High Value' AND cso.OpportunityRank = 1 THEN 'Personalized outreach with premium offer'
    WHEN cso.ValueTier = 'High Value' THEN 'Targeted email with category-specific benefits'
    WHEN cso.ValueTier = 'Medium-High Value' THEN 'Automated campaign with bundle discount'
    ELSE 'Include in general cross-sell communications'
END AS RecommendedApproach
```

**Decision Matrix:**

### Personalized Outreach with Premium Offer
**Criteria:** High Value + Rank 1 opportunity

**Tactics:**
- Personal email from account manager or founder
- Phone call for ultra-high-value customers
- Premium offer: 20-25% discount + free shipping + extended return period
- Custom product selection based on owned category
- White-glove service mention
- Exclusive access to limited editions

**Investment Level:** High ($50-100 per customer)
**Expected Conversion:** 25-40%
**ROI:** High (due to high customer value)

**Example:**
"Hi [Name], as one of our most valued bike customers spending $50K+, I wanted to personally introduce you to our premium accessories line. Here's an exclusive 25% discount and free premium shipping..."

### Targeted Email with Category-Specific Benefits
**Criteria:** High Value + Ranks 2-5 opportunities

**Tactics:**
- Personalized email with customer name
- Showcase specific products from recommended category
- Highlight benefits relevant to owned category
- 15-20% discount
- Customer testimonials from similar buyers
- Free shipping threshold

**Investment Level:** Medium ($20-30 per customer)
**Expected Conversion:** 15-25%
**ROI:** High

**Example:**
"Hi [Name], since you love our bikes, we thought you'd appreciate these top-rated accessories. Our bike customers rate them 4.8/5 stars. Here's 20% off your first accessories order..."

### Automated Campaign with Bundle Discount
**Criteria:** Medium-High Value customers

**Tactics:**
- Automated email series (3-5 emails over 4 weeks)
- Category bundle offers (e.g., "Bike + Accessory Starter Pack")
- 10-15% bundle discount
- Dynamic product recommendations
- Social proof (bestsellers, trending)
- Abandoned browse recovery

**Investment Level:** Low ($5-10 per customer)
**Expected Conversion:** 8-15%
**ROI:** Medium-High

**Example:**
"You've enjoyed our [Owned Category]. Now save 15% when you bundle with these popular [Recommended Category] items. Complete your setup!"

### Include in General Cross-Sell Communications
**Criteria:** All other customers (filtered out in this query's WHERE clause, but shown for completeness)

**Tactics:**
- Mass email campaigns
- Website category suggestions
- Retargeting ads
- Minimal personalization
- Standard promotions (5-10% off)
- Seasonal campaigns

**Investment Level:** Minimal ($1-3 per customer)
**Expected Conversion:** 2-5%
**ROI:** Low-Medium

**Business Purpose:** Ensures campaign tactics match customer value and opportunity strength, optimizing both conversion rates and marketing efficiency.

## Examples

**Scenario 1: Ultra-High-Value Customer**
- Customer: High Value ($75,000 lifetime)
- RecommendedCategory: Accessories
- OpportunityRank: 1
- RecommendedApproach: "Personalized outreach with premium offer"
- **Execution:** Account manager calls customer, offers 25% off entire accessories catalog + free premium shipping forever + early access to new releases

**Scenario 2: High-Value Customer**
- Customer: High Value ($25,000 lifetime)
- RecommendedCategory: Clothing
- OpportunityRank: 2
- RecommendedApproach: "Targeted email with category-specific benefits"
- **Execution:** Personalized email showcasing performance cycling apparel, 20% discount, testimonials from other bike customers

**Scenario 3: Medium-High-Value Customer**
- Customer: Medium-High Value ($8,000 lifetime)
- RecommendedCategory: Components
- OpportunityRank: 1
- RecommendedApproach: "Automated campaign with bundle discount"
- **Execution:** 4-email series over 3 weeks: (1) Introduction, (2) Product benefits, (3) Bundle offer 15% off, (4) Last chance reminder

---

# Summary: Cross-Sell Opportunity Framework

## Query Structure
The query builds cross-sell recommendations through seven progressive CTEs:

### CTE Flow:
1. **CustomerValueTier** → Segment customers by revenue quartile (KPI 1-4)
2. **CustomerCategoryPurchases** → Aggregate category-level purchase behavior (KPI 5-12)
3. **AllCategories** → List all available categories
4. **CustomerCategoryMatrix** → Create customer × category matrix (KPI 13)
5. **CustomerCategorySummary** → Calculate category penetration metrics (KPI 14-19)
6. **CategoryAffinityPatterns** → Identify category pairs frequently purchased together (KPI 20-22)
7. **CrossSellOpportunities** → Match customer gaps with affinity patterns (KPI 23-27)
8. **TopCrossSellOpportunities** → Rank and prioritize opportunities (KPI 28-31)

## Cross-Sell Methodology

### Core Concepts:

**1. Category Penetration**
- Measures how many of available categories each customer has purchased
- Low penetration = high cross-sell opportunity
- Formula: CategoriesPurchased / TotalCategories

**2. Affinity Analysis**
- Identifies category pairs frequently purchased together
- Based on actual customer behavior patterns
- Minimum threshold: 10+ customers for statistical significance

**3. Gap Analysis**
- Finds categories customer hasn't purchased (HasPurchasedCategory = 0)
- Matches gaps with strong affinity patterns
- Creates targeted recommendations

**4. Value-Based Prioritization**
- Focuses on High Value and Medium-High Value tiers
- Ranks opportunities by affinity strength and revenue potential
- Limits recommendations to top 5 per customer

## Business Applications

### 1. Personalized Product Recommendations
- **Website**: "Customers who bought [OwnedCategory] also bought [RecommendedCategory]"
- **Email**: Personalized product carousels based on affinity patterns
- **App**: Push notifications with category-specific offers

### 2. Campaign Segmentation
**High Value + Rank 1:**
- Personal outreach
- Premium offers (20-25% off)
- Account manager contact
- Expected conversion: 25-40%

**High Value + Ranks 2-5:**
- Targeted emails
- Category-specific benefits
- 15-20% discounts
- Expected conversion: 15-25%

**Medium-High Value:**
- Automated campaigns
- Bundle discounts (10-15% off)
- Email series
- Expected conversion: 8-15%

### 3. Revenue Expansion Strategies
**Depth (Within-Category):**
- Increase UniqueProductsInCategory
- Promote variety within owned categories

**Breadth (Cross-Category):**
- Increase CategoryPenetrationPct
- Move customers from 25% to 50% to 75% penetration

**Wallet Share:**
- Increase CategoryRevenue in underutilized categories
- Target high-affinity, low-revenue categories

### 4. Inventory and Merchandising
**Bundle Creation:**
- Create product bundles based on highest-affinity pairs
- "Bikes + Accessories Starter Pack"
- "Cycling Enthusiast Bundle (Accessories + Clothing + Components)"

**Store Layout:**
- Physical stores: Co-locate high-affinity categories
- E-commerce: Cross-link category pages based on affinity

**Assortment Planning:**
- Ensure adequate inventory of high-affinity pairs
- Coordinate promotions across affinity categories

### 5. Customer Lifecycle Management
**New Customer Onboarding:**
- First purchase in Category A → Trigger email for Category B (if high affinity)
- Accelerate path to multi-category buyer

**Churn Prevention:**
- Single-category buyers have higher churn risk
- Proactive cross-sell to increase stickiness
- Target: Move to 3+ categories within 90 days

**Reactivation:**
- Lapsed customers: Recommend new categories to spark interest
- "Haven't seen you in a while—check out our new [Category] line!"

## Key Metrics for Executive Dashboard

### Category Engagement Metrics:
- **Avg CategoryPenetrationPct**: Target 50%+ for high-value customers
- **% Customers with 1 Category**: Risk segment, target <30%
- **% Customers with 3+ Categories**: Loyal segment, target >40%

### Cross-Sell Performance:
- **Cross-Sell Conversion Rate** by ValueTier and Priority
  - High Value + Top Priority: Target 25-40%
  - Medium-High Value: Target 8-15%
- **Revenue from Cross-Sell**: Track incremental revenue from campaigns
- **Time to 2nd Category**: Days from first purchase to first cross-category purchase

### Affinity Insights:
- **Top Affinity Pairs** by CustomerCount
  - Example: 50% of customers buy Bikes + Accessories
- **High-Value Affinity Pairs** by AvgCombinedRevenue
  - Example: Bikes + Components = $12K average
- **Untapped Affinities**: Strong affinity, low current penetration = opportunity

### Campaign Economics:
- **Cost per Acquisition** (CPA) by approach
  - Personalized: $50-100 per customer
  - Targeted: $20-30 per customer
  - Automated: $5-10 per customer
- **ROI by ValueTier**
  - High Value: 10-20x ROI
  - Medium-High Value: 5-10x ROI
- **Lifetime Value Uplift**: Multi-category buyers vs. single-category

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)
1. Build category purchase data mart
2. Calculate category penetration metrics
3. Identify affinity patterns
4. Create customer segmentation

### Phase 2: Targeting (Weeks 5-8)
1. Generate cross-sell opportunity lists
2. Develop campaign templates by priority
3. Create personalized messaging framework
4. Set up tracking and attribution

### Phase 3: Execution (Weeks 9-12)
1. Launch High Value + Top Priority campaigns (personalized)
2. Launch High Value + High Priority campaigns (targeted emails)
3. Launch Medium-High Value campaigns (automated)
4. Monitor conversion and iterate

### Phase 4: Optimization (Ongoing)
1. A/B test messaging and offers
2. Refine affinity thresholds
3. Adjust ValueTier definitions
4. Expand to additional customer segments

This cross-sell framework provides a complete, data-driven system for identifying and executing product category expansion opportunities based on natural customer behavior patterns and value segmentation.
