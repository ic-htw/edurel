# Exercises on Subqueries

## Exercise 1

### Text
Find all customers who have made purchases with total store sales greater than the average store sales across all transactions.

### SQL Code
```sql
SELECT DISTINCT c.Customerid, c.Firstname, c.Lastname
FROM Customer c
JOIN Sales s ON c.Customerid = s.Customerid
WHERE s.Storesales > (SELECT AVG(Storesales) FROM Sales)
ORDER BY c.Lastname, c.Firstname;
```

### Result
```
┌────────────┬───────────┬────────────┐
│ Customerid │ Firstname │  Lastname  │
│   int32    │  varchar  │  varchar   │
├────────────┼───────────┼────────────┤
│       2724 │ Catherine │ Abahamdeh  │
│       3872 │ John      │ Abalos     │
│       6979 │ Glen      │ Abbassi    │
│       4881 │ Carroll   │ Abbate     │
│       9163 │ Rusty     │ Abbey      │
│       8288 │ Bonnie    │ Abbott     │
│        278 │ Eric      │ Abbott     │
│       8862 │ Patrick   │ Abbott     │
│       6049 │ Sherry    │ Abbott     │
│       1972 │ Muffy     │ Abbruzzese │
│         ·  │   ·       │    ·       │
│         ·  │   ·       │    ·       │
│         ·  │   ·       │    ·       │
│       4490 │ Roland    │ Zumsteg    │
│       5613 │ Joyce     │ Zuniga     │
│       8630 │ Shirley   │ Zuniga     │
│       2049 │ Elizabeth │ Zuvich     │
│       5721 │ Harriett  │ Zvibleman  │
│       6632 │ Ramona    │ Zvibleman  │
│       1469 │ Todd      │ Zweifel    │
│       3855 │ Julieanna │ Zwier      │
│       3801 │ Jeanne    │ Zysko      │
│       5486 │ Mark      │ Zywicki    │
├────────────┴───────────┴────────────┤
│ 8075 rows (20 shown)      3 columns │
└─────────────────────────────────────┘
```


## Exercise 2

### Text
List all products that have never been sold.

### SQL Code
```sql
SELECT p.Productid, p.Pname, p.Brand, p.Category
FROM Product p
WHERE p.Productid NOT IN (SELECT DISTINCT Productid FROM Sales)
ORDER BY p.Category, p.Pname;
```

### Result
```
┌───────────┬─────────────────┬─────────┬──────────────────┐
│ Productid │      Pname      │  Brand  │     Category     │
│   int32   │     varchar     │ varchar │     varchar      │
├───────────┼─────────────────┼─────────┼──────────────────┤
│      1560 │ CDR Grape Jelly │ CDR     │ Jams and Jellies │
└───────────┴─────────────────┴─────────┴──────────────────┘
```


## Exercise 3

### Text
Using a CTE, find the top 3 countries by total store sales and then list all stores in those countries.

### SQL Code
```sql
WITH TopCountries AS (
    SELECT st.Country, SUM(s.Storesales) as TotalSales
    FROM Store st
    JOIN Sales s ON st.Storeid = s.Storeid
    GROUP BY st.Country
    ORDER BY TotalSales DESC
    LIMIT 3
)
SELECT s.Storeid, s.Sname, s.City, s.State, s.Country
FROM Store s
WHERE s.Country IN (SELECT Country FROM TopCountries)
ORDER BY s.Country, s.Sname;
```

### Result
```
┌─────────┬──────────┬───────────────┬───────────┬─────────┐
│ Storeid │  Sname   │     City      │   State   │ Country │
│  int32  │ varchar  │    varchar    │  varchar  │ varchar │
├─────────┼──────────┼───────────────┼───────────┼─────────┤
│      19 │ Store 19 │ Vancouver     │ BC        │ Canada  │
│      20 │ Store 20 │ Victoria      │ BC        │ Canada  │
│       1 │ Store 1  │ Acapulco      │ Guerrero  │ Mexico  │
│      10 │ Store 10 │ Orizaba       │ Veracruz  │ Mexico  │
│      12 │ Store 12 │ Hidalgo       │ Zacatecas │ Mexico  │
│      18 │ Store 18 │ Hidalgo       │ Zacatecas │ Mexico  │
│      21 │ Store 21 │ San Andres    │ DF        │ Mexico  │
│       4 │ Store 4  │ Camacho       │ Zacatecas │ Mexico  │
│       5 │ Store 5  │ Guadalajara   │ Jalisco   │ Mexico  │
│       8 │ Store 8  │ Merida        │ Yucatan   │ Mexico  │
│       · │    ·     │   ·           │ ·         │  ·      │
│       · │    ·     │   ·           │ ·         │  ·      │
│       · │    ·     │   ·           │ ·         │  ·      │
│      15 │ Store 15 │ Seattle       │ WA        │ USA     │
│      16 │ Store 16 │ Spokane       │ WA        │ USA     │
│      17 │ Store 17 │ Tacoma        │ WA        │ USA     │
│       2 │ Store 2  │ Bellingham    │ WA        │ USA     │
│      22 │ Store 22 │ Walla Walla   │ WA        │ USA     │
│      23 │ Store 23 │ Yakima        │ WA        │ USA     │
│      24 │ Store 24 │ San Diego     │ CA        │ USA     │
│       3 │ Store 3  │ Bremerton     │ WA        │ USA     │
│       6 │ Store 6  │ Beverly Hills │ CA        │ USA     │
│       7 │ Store 7  │ Los Angeles   │ CA        │ USA     │
├─────────┴──────────┴───────────────┴───────────┴─────────┤
│ 25 rows (20 shown)                             5 columns │
└──────────────────────────────────────────────────────────┘
```


## Exercise 4

### Text
Using a CTE, calculate the total sales per product category and then find all products in categories where total sales exceed 100000.

### SQL Code
```sql
WITH CategorySales AS (
    SELECT p.Category, SUM(s.Storesales) as TotalSales
    FROM Product p
    JOIN Sales s ON p.Productid = s.Productid
    GROUP BY p.Category
)
SELECT p.Productid, p.Pname, p.Category, cs.TotalSales
FROM Product p
JOIN CategorySales cs ON p.Category = cs.Category
WHERE cs.TotalSales > 100000
ORDER BY cs.TotalSales DESC, p.Pname;
```

### Result
```
┌───────────┬────────────────────────────────┬────────────┬───────────────┐
│ Productid │             Pname              │  Category  │  TotalSales   │
│   int32   │            varchar             │  varchar   │ decimal(38,2) │
├───────────┼────────────────────────────────┼────────────┼───────────────┤
│       327 │ Better Canned Beets            │ Vegetables │     206070.44 │
│       339 │ Better Canned Peas             │ Vegetables │     206070.44 │
│       329 │ Better Canned String Beans     │ Vegetables │     206070.44 │
│       333 │ Better Canned Tomatos          │ Vegetables │     206070.44 │
│       331 │ Better Canned Yams             │ Vegetables │     206070.44 │
│       328 │ Better Creamed Corn            │ Vegetables │     206070.44 │
│       400 │ Big Time Fajita French Fries   │ Vegetables │     206070.44 │
│       417 │ Big Time Frozen Broccoli       │ Vegetables │     206070.44 │
│       406 │ Big Time Frozen Carrots        │ Vegetables │     206070.44 │
│       416 │ Big Time Frozen Cauliflower    │ Vegetables │     206070.44 │
│        ·  │              ·                 │   ·        │         ·     │
│        ·  │              ·                 │   ·        │         ·     │
│        ·  │              ·                 │   ·        │         ·     │
│       665 │ Gorilla Low Fat Cottage Cheese │ Dairy      │     108634.29 │
│       666 │ Gorilla Low Fat Sour Cream     │ Dairy      │     108634.29 │
│       671 │ Gorilla Low Fat String Cheese  │ Dairy      │     108634.29 │
│       676 │ Gorilla Mild Cheddar Cheese    │ Dairy      │     108634.29 │
│       669 │ Gorilla Muenster Cheese        │ Dairy      │     108634.29 │
│       675 │ Gorilla Sharp Cheddar Cheese   │ Dairy      │     108634.29 │
│       667 │ Gorilla Sour Cream             │ Dairy      │     108634.29 │
│       683 │ Gorilla Strawberry Yogurt      │ Dairy      │     108634.29 │
│       670 │ Gorilla String Cheese          │ Dairy      │     108634.29 │
│       682 │ Gorilla Whole Milk             │ Dairy      │     108634.29 │
├───────────┴────────────────────────────────┴────────────┴───────────────┤
│ 470 rows (20 shown)                                           4 columns │
└─────────────────────────────────────────────────────────────────────────┘
```


## Exercise 5

### Text
Find customers whose total yearly purchases are greater than the average total purchases of all customers in their state.

### SQL Code
```sql
WITH CustomerTotals AS (
    SELECT c.Customerid, c.State, SUM(s.Storesales) as TotalPurchases
    FROM Customer c
    JOIN Sales s ON c.Customerid = s.Customerid
    GROUP BY c.Customerid, c.State
),
StateAverages AS (
    SELECT State, AVG(TotalPurchases) as AvgPurchases
    FROM CustomerTotals
    GROUP BY State
)
SELECT c.Customerid, c.Firstname, c.Lastname, c.State, ct.TotalPurchases, sa.AvgPurchases
FROM Customer c
JOIN CustomerTotals ct ON c.Customerid = ct.Customerid
JOIN StateAverages sa ON c.State = sa.State
WHERE ct.TotalPurchases > sa.AvgPurchases
ORDER BY c.State, ct.TotalPurchases DESC;
```

### Result
```
┌────────────┬───────────┬───────────┬───────────┬────────────────┬───────────────────┐
│ Customerid │ Firstname │ Lastname  │   State   │ TotalPurchases │   AvgPurchases    │
│   int32    │  varchar  │  varchar  │  varchar  │ decimal(38,2)  │      double       │
├────────────┼───────────┼───────────┼───────────┼────────────────┼───────────────────┤
│       5465 │ Dorothy   │ Ahmari    │ BC        │         342.21 │ 73.77386004514673 │
│       1769 │ Joyce     │ Minsky    │ BC        │         291.13 │ 73.77386004514673 │
│       6821 │ Katherine │ Worlay    │ BC        │         282.91 │ 73.77386004514673 │
│         59 │ Elizabeth │ Moss      │ BC        │         277.51 │ 73.77386004514673 │
│        943 │ David     │ Chavez    │ BC        │         267.34 │ 73.77386004514673 │
│       5283 │ Jack      │ Moore     │ BC        │         254.28 │ 73.77386004514673 │
│       2730 │ Helen     │ Wright    │ BC        │         250.25 │ 73.77386004514673 │
│       8716 │ Gregory   │ Wood      │ BC        │         249.03 │ 73.77386004514673 │
│       1777 │ Mary      │ Hall      │ BC        │         248.28 │ 73.77386004514673 │
│      10281 │ Samuel    │ Cartney   │ BC        │         246.90 │ 73.77386004514673 │
│         ·  │   ·       │    ·      │ ·         │            ·   │         ·         │
│         ·  │   ·       │    ·      │ ·         │            ·   │         ·         │
│         ·  │   ·       │    ·      │ ·         │            ·   │         ·         │
│       2023 │ Kimberly  │ Primack   │ Zacatecas │         870.25 │ 794.4078835978836 │
│       4932 │ Zelda     │ Stone     │ Zacatecas │         867.72 │ 794.4078835978836 │
│       5712 │ Ralph     │ Campbell  │ Zacatecas │         861.83 │ 794.4078835978836 │
│       4571 │ David     │ Bernahola │ Zacatecas │         844.68 │ 794.4078835978836 │
│       8522 │ Erelyn    │ Stephens  │ Zacatecas │         837.50 │ 794.4078835978836 │
│       3317 │ Aleah     │ Elmore    │ Zacatecas │         834.04 │ 794.4078835978836 │
│       2310 │ John      │ Guzzetti  │ Zacatecas │         825.58 │ 794.4078835978836 │
│       2510 │ Leslie    │ Rainosek  │ Zacatecas │         824.96 │ 794.4078835978836 │
│       8697 │ Gina      │ Kerbel    │ Zacatecas │         802.97 │ 794.4078835978836 │
│       2528 │ Ed        │ Bias      │ Zacatecas │         795.47 │ 794.4078835978836 │
├────────────┴───────────┴───────────┴───────────┴────────────────┴───────────────────┤
│ 3633 rows (20 shown)                                                      6 columns │
└─────────────────────────────────────────────────────────────────────────────────────┘
```


# Exercises on Window Functions

## Exercise 1

### Text
Rank products within each category by their total unit sales, showing the top 5 products per category.

### SQL Code
```sql
WITH ProductSales AS (
    SELECT
        p.Category,
        p.Pname,
        SUM(s.Unitsales) as TotalUnits,
        RANK() OVER (PARTITION BY p.Category ORDER BY SUM(s.Unitsales) DESC) as CategoryRank
    FROM Product p
    JOIN Sales s ON p.Productid = s.Productid
    GROUP BY p.Category, p.Pname
)
SELECT Category, Pname, TotalUnits, CategoryRank
FROM ProductSales
WHERE CategoryRank <= 5
ORDER BY Category, CategoryRank;
```

### Result
```
┌───────────────────┬────────────────────────────────────────────┬────────────┬──────────────┐
│     Category      │                   Pname                    │ TotalUnits │ CategoryRank │
│      varchar      │                  varchar                   │   int128   │    int64     │
├───────────────────┼────────────────────────────────────────────┼────────────┼──────────────┤
│ Baking Goods      │ BBB Best White Sugar                       │        561 │            1 │
│ Baking Goods      │ BBB Best Sesame Oil                        │        549 │            2 │
│ Baking Goods      │ BBB Best Pepper                            │        547 │            3 │
│ Baking Goods      │ Super White Sugar                          │        546 │            4 │
│ Baking Goods      │ Super Salt                                 │        542 │            5 │
│ Bathroom Products │ Hilltop Mint Mouthwash                     │        622 │            1 │
│ Bathroom Products │ Hilltop Silky Smooth Hair Conditioner      │        611 │            2 │
│ Bathroom Products │ Sunset Economy Toilet Brush                │        600 │            3 │
│ Bathroom Products │ Consolidated Silky Smooth Hair Conditioner │        562 │            4 │
│ Bathroom Products │ Hilltop Extra Moisture Shampoo             │        554 │            5 │
│       ·           │         ·                                  │         ·  │            · │
│       ·           │         ·                                  │         ·  │            · │
│       ·           │         ·                                  │         ·  │            · │
│ Starchy Foods     │ Monarch Rice Medly                         │        600 │            1 │
│ Starchy Foods     │ Monarch Manicotti                          │        593 │            2 │
│ Starchy Foods     │ Shady Lake Rice Medly                      │        552 │            3 │
│ Starchy Foods     │ Colossal Manicotti                         │        548 │            4 │
│ Starchy Foods     │ Monarch Spaghetti                          │        547 │            5 │
│ Vegetables        │ Tell Tale Fresh Lima Beans                 │        645 │            1 │
│ Vegetables        │ Hermanos Green Pepper                      │        614 │            2 │
│ Vegetables        │ Hermanos Potatos                           │        606 │            3 │
│ Vegetables        │ Hermanos Elephant Garlic                   │        594 │            4 │
│ Vegetables        │ Ebony Fresh Lima Beans                     │        593 │            5 │
├───────────────────┴────────────────────────────────────────────┴────────────┴──────────────┤
│ 226 rows (20 shown)                                                              4 columns │
└────────────────────────────────────────────────────────────────────────────────────────────┘
```


## Exercise 2

### Text
Calculate the running total of store sales for each store ordered by time, showing the cumulative sales over time.

### SQL Code
```sql
SELECT
    s.Storeid,
    st.Sname,
    t.TYear,
    t.TMonth,
    SUM(s.Storesales) as MonthlySales,
    SUM(SUM(s.Storesales)) OVER (
        PARTITION BY s.Storeid
        ORDER BY t.TYear, t.TMonthnumber
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as RunningTotal
FROM Sales s
JOIN Store st ON s.Storeid = st.Storeid
JOIN TimeByDay t ON s.Timeid = t.Timeid
GROUP BY s.Storeid, st.Sname, t.TYear, t.TMonth, t.TMonthnumber
ORDER BY s.Storeid, t.TYear, t.TMonthnumber;
```

### Result
```
┌─────────┬──────────┬───────┬───────────┬───────────────┬───────────────┐
│ Storeid │  Sname   │ TYear │  TMonth   │ MonthlySales  │ RunningTotal  │
│  int32  │ varchar  │ int32 │  varchar  │ decimal(38,2) │ decimal(38,2) │
├─────────┼──────────┼───────┼───────────┼───────────────┼───────────────┤
│       1 │ Store 1  │  2015 │ January   │       5668.27 │       5668.27 │
│       1 │ Store 1  │  2015 │ February  │       4212.25 │       9880.52 │
│       1 │ Store 1  │  2015 │ March     │       5182.62 │      15063.14 │
│       1 │ Store 1  │  2015 │ April     │       4604.30 │      19667.44 │
│       1 │ Store 1  │  2015 │ May       │       4312.83 │      23980.27 │
│       1 │ Store 1  │  2015 │ June      │       3384.40 │      27364.67 │
│       1 │ Store 1  │  2015 │ July      │       4396.12 │      31760.79 │
│       1 │ Store 1  │  2015 │ August    │       3686.99 │      35447.78 │
│       1 │ Store 1  │  2015 │ September │       4672.65 │      40120.43 │
│       1 │ Store 1  │  2015 │ October   │       4301.57 │      44422.00 │
│       · │    ·     │    ·  │    ·      │          ·    │          ·    │
│       · │    ·     │    ·  │    ·      │          ·    │          ·    │
│       · │    ·     │    ·  │    ·      │          ·    │          ·    │
│      24 │ Store 24 │  2015 │ February  │       3940.47 │      63101.32 │
│      24 │ Store 24 │  2015 │ March     │       5258.59 │      68359.91 │
│      24 │ Store 24 │  2015 │ April     │       4169.44 │      72529.35 │
│      24 │ Store 24 │  2015 │ May       │       4536.13 │      77065.48 │
│      24 │ Store 24 │  2015 │ June      │       4866.19 │      81931.67 │
│      24 │ Store 24 │  2015 │ July      │       4394.82 │      86326.49 │
│      24 │ Store 24 │  2015 │ August    │       3938.25 │      90264.74 │
│      24 │ Store 24 │  2015 │ September │       4808.90 │      95073.64 │
│      24 │ Store 24 │  2015 │ October   │       4252.11 │      99325.75 │
│      24 │ Store 24 │  2015 │ November  │       6725.79 │     106051.54 │
├─────────┴──────────┴───────┴───────────┴───────────────┴───────────────┤
│ 420 rows (20 shown)                                          6 columns │
└────────────────────────────────────────────────────────────────────────┘
```


## Exercise 3

### Text
For each customer, show their purchase amount alongside the previous and next purchase amounts ordered by date.

### SQL Code
```sql
SELECT
    c.Customerid,
    c.Firstname,
    c.Lastname,
    t.TYear,
    t.TMonth,
    t.TDayofmonth,
    s.Storesales,
    LAG(s.Storesales) OVER (PARTITION BY c.Customerid ORDER BY t.TYear, t.TMonthnumber, t.TDayofmonth) as PreviousPurchase,
    LEAD(s.Storesales) OVER (PARTITION BY c.Customerid ORDER BY t.TYear, t.TMonthnumber, t.TDayofmonth) as NextPurchase
FROM Customer c
JOIN Sales s ON c.Customerid = s.Customerid
JOIN TimeByDay t ON s.Timeid = t.Timeid
ORDER BY c.Customerid, t.TYear, t.TMonthnumber, t.TDayofmonth;
```

### Result
```
┌────────────┬───────────┬──────────┬───────┬──────────┬─────────────┬───────────────┬──────────────────┬───────────────┐
│ Customerid │ Firstname │ Lastname │ TYear │  TMonth  │ TDayofmonth │  Storesales   │ PreviousPurchase │ NextPurchase  │
│   int32    │  varchar  │ varchar  │ int32 │ varchar  │    int32    │ decimal(13,2) │  decimal(13,2)   │ decimal(13,2) │
├────────────┼───────────┼──────────┼───────┼──────────┼─────────────┼───────────────┼──────────────────┼───────────────┤
│          3 │ Jeanne    │ Derry    │  2014 │ April    │          27 │          4.46 │             NULL │          6.84 │
│          3 │ Jeanne    │ Derry    │  2014 │ April    │          27 │          6.84 │             4.46 │          6.81 │
│          3 │ Jeanne    │ Derry    │  2014 │ April    │          27 │          6.81 │             6.84 │          4.26 │
│          3 │ Jeanne    │ Derry    │  2014 │ April    │          27 │          4.26 │             6.81 │          2.79 │
│          3 │ Jeanne    │ Derry    │  2014 │ April    │          27 │          2.79 │             4.26 │          5.56 │
│          3 │ Jeanne    │ Derry    │  2014 │ April    │          27 │          5.56 │             2.79 │          2.76 │
│          3 │ Jeanne    │ Derry    │  2014 │ April    │          27 │          2.76 │             5.56 │          8.88 │
│          3 │ Jeanne    │ Derry    │  2014 │ October  │          22 │          8.88 │             2.76 │          6.39 │
│          3 │ Jeanne    │ Derry    │  2014 │ October  │          22 │          6.39 │             8.88 │          3.36 │
│          3 │ Jeanne    │ Derry    │  2014 │ October  │          22 │          3.36 │             6.39 │          8.91 │
│          · │   ·       │   ·      │    ·  │    ·     │           · │            ·  │               ·  │            ·  │
│          · │   ·       │   ·      │    ·  │    ·     │           · │            ·  │               ·  │            ·  │
│          · │   ·       │   ·      │    ·  │    ·     │           · │            ·  │               ·  │            ·  │
│        509 │ William   │ Conner   │  2015 │ February │          21 │          3.04 │             NULL │          7.68 │
│        509 │ William   │ Conner   │  2015 │ February │          21 │          7.68 │             3.04 │          4.92 │
│        509 │ William   │ Conner   │  2015 │ February │          21 │          4.92 │             7.68 │         13.76 │
│        509 │ William   │ Conner   │  2015 │ February │          21 │         13.76 │             4.92 │          5.73 │
│        509 │ William   │ Conner   │  2015 │ February │          21 │          5.73 │            13.76 │          5.26 │
│        509 │ William   │ Conner   │  2015 │ February │          21 │          5.26 │             5.73 │          8.96 │
│        509 │ William   │ Conner   │  2015 │ July     │          28 │          8.96 │             5.26 │          8.22 │
│        509 │ William   │ Conner   │  2015 │ July     │          28 │          8.22 │             8.96 │         10.68 │
│        509 │ William   │ Conner   │  2015 │ July     │          28 │         10.68 │             8.22 │          NULL │
│        510 │ Ciro      │ Bauer    │  2015 │ January  │          17 │          6.84 │             NULL │          2.82 │
├────────────┴───────────┴──────────┴───────┴──────────┴─────────────┴───────────────┴──────────────────┴───────────────┤
│ ? rows (>9999 rows, 20 shown)                                                                               9 columns │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```


## Exercise 4

### Text
Calculate the percentage contribution of each product's sales to its department's total sales.

### SQL Code
```sql
SELECT
    p.Department,
    p.Pname,
    SUM(s.Storesales) as ProductSales,
    SUM(SUM(s.Storesales)) OVER (PARTITION BY p.Department) as DepartmentSales,
    ROUND(100.0 * SUM(s.Storesales) / SUM(SUM(s.Storesales)) OVER (PARTITION BY p.Department), 2) as PercentageContribution
FROM Product p
JOIN Sales s ON p.Productid = s.Productid
GROUP BY p.Department, p.Pname
ORDER BY p.Department, ProductSales DESC;
```

### Result
```
┌─────────────────────┬────────────────────────────┬───────────────┬─────────────────┬────────────────────────┐
│     Department      │           Pname            │ ProductSales  │ DepartmentSales │ PercentageContribution │
│       varchar       │          varchar           │ decimal(38,2) │  decimal(38,2)  │         double         │
├─────────────────────┼────────────────────────────┼───────────────┼─────────────────┼────────────────────────┤
│ Alcoholic Beverages │ Portsmouth Light Beer      │       1989.75 │        41137.07 │                   4.84 │
│ Alcoholic Beverages │ Good White Zinfandel Wine  │       1951.09 │        41137.07 │                   4.74 │
│ Alcoholic Beverages │ Portsmouth Chardonnay Wine │       1824.76 │        41137.07 │                   4.44 │
│ Alcoholic Beverages │ Top Measure Light Wine     │       1710.24 │        41137.07 │                   4.16 │
│ Alcoholic Beverages │ Walrus Chardonnay          │       1702.40 │        41137.07 │                   4.14 │
│ Alcoholic Beverages │ Top Measure Chablis Wine   │       1612.16 │        41137.07 │                   3.92 │
│ Alcoholic Beverages │ Good Chablis Wine          │       1550.64 │        41137.07 │                   3.77 │
│ Alcoholic Beverages │ Pearl Chablis Wine         │       1511.52 │        41137.07 │                   3.67 │
│ Alcoholic Beverages │ Portsmouth Merlot Wine     │       1469.44 │        41137.07 │                   3.57 │
│ Alcoholic Beverages │ Walrus Merlot Wine         │       1468.28 │        41137.07 │                   3.57 │
│       ·             │         ·                  │           ·   │            ·    │                     ·  │
│       ·             │         ·                  │           ·   │            ·    │                     ·  │
│       ·             │         ·                  │           ·   │            ·    │                     ·  │
│ Starchy Foods       │ Discover Manicotti         │        827.54 │        33891.81 │                   2.44 │
│ Starchy Foods       │ Monarch Spaghetti          │        754.86 │        33891.81 │                   2.23 │
│ Starchy Foods       │ Medalist Manicotti         │        692.78 │        33891.81 │                   2.04 │
│ Starchy Foods       │ Colossal Rice Medly        │        692.04 │        33891.81 │                   2.04 │
│ Starchy Foods       │ Jardon Manicotti           │        596.40 │        33891.81 │                   1.76 │
│ Starchy Foods       │ Jardon Ravioli             │        503.04 │        33891.81 │                   1.48 │
│ Starchy Foods       │ Discover Ravioli           │        402.16 │        33891.81 │                   1.19 │
│ Starchy Foods       │ Shady Lake Rice Medly      │        386.40 │        33891.81 │                   1.14 │
│ Starchy Foods       │ Jardon Rice Medly          │        259.26 │        33891.81 │                   0.76 │
│ Starchy Foods       │ Jardon Spaghetti           │        235.44 │        33891.81 │                   0.69 │
├─────────────────────┴────────────────────────────┴───────────────┴─────────────────┴────────────────────────┤
│ 1559 rows (20 shown)                                                                              5 columns │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```


## Exercise 5

### Text
Assign quartiles to customers based on their total yearly income within each education level, grouping customers into four equal groups.

### SQL Code
```sql
WITH CustomerSales AS (
    SELECT
        c.Customerid,
        c.Firstname,
        c.Lastname,
        c.Education,
        c.Yearlyincome,
        SUM(s.Storesales) as TotalSpent
    FROM Customer c
    JOIN Sales s ON c.Customerid = s.Customerid
    GROUP BY c.Customerid, c.Firstname, c.Lastname, c.Education, c.Yearlyincome
)
SELECT
    Customerid,
    Firstname,
    Lastname,
    Education,
    Yearlyincome,
    TotalSpent,
    NTILE(4) OVER (PARTITION BY Education ORDER BY TotalSpent) as SpendingQuartile
FROM CustomerSales
ORDER BY Education, SpendingQuartile, TotalSpent DESC;
```

### Result
```
┌────────────┬───────────┬────────────┬─────────────────────┬───────────────┬───────────────┬──────────────────┐
│ Customerid │ Firstname │  Lastname  │      Education      │ Yearlyincome  │  TotalSpent   │ SpendingQuartile │
│   int32    │  varchar  │  varchar   │       varchar       │    varchar    │ decimal(38,2) │      int64       │
├────────────┼───────────┼────────────┼─────────────────────┼───────────────┼───────────────┼──────────────────┤
│       3425 │ Joseph    │ Fernandez  │ Bachelors Degree    │ $150K +       │         55.31 │                1 │
│       9786 │ Bruce     │ Berg       │ Bachelors Degree    │ $50K - $70K   │         55.11 │                1 │
│       6038 │ Erica     │ Wall       │ Bachelors Degree    │ $30K - $50K   │         55.07 │                1 │
│       1950 │ Kathaleen │ Cohen      │ Bachelors Degree    │ $50K - $70K   │         55.05 │                1 │
│       7555 │ Debbie    │ Smiglewski │ Bachelors Degree    │ $70K - $90K   │         55.01 │                1 │
│       8371 │ Harold    │ Cohen      │ Bachelors Degree    │ $50K - $70K   │         54.98 │                1 │
│       2685 │ Myrna     │ Brauer     │ Bachelors Degree    │ $50K - $70K   │         54.95 │                1 │
│       9859 │ Genevieve │ Russo      │ Bachelors Degree    │ $70K - $90K   │         54.92 │                1 │
│       5012 │ Wayne     │ Thomas     │ Bachelors Degree    │ $50K - $70K   │         54.80 │                1 │
│       8101 │ Robert    │ Nelson     │ Bachelors Degree    │ $130K - $150K │         54.72 │                1 │
│         ·  │   ·       │   ·        │        ·            │      ·        │           ·   │                · │
│         ·  │   ·       │   ·        │        ·            │      ·        │           ·   │                · │
│         ·  │   ·       │   ·        │        ·            │      ·        │           ·   │                · │
│       9574 │ Willie    │ Zamora     │ Partial High School │ $10K - $30K   │        224.13 │                4 │
│       6570 │ Christine │ Avila      │ Partial High School │ $10K - $30K   │        224.03 │                4 │
│       7731 │ Helen     │ Villa      │ Partial High School │ $10K - $30K   │        223.61 │                4 │
│       8247 │ Elizabeth │ Carter     │ Partial High School │ $50K - $70K   │        222.66 │                4 │
│       8730 │ Richard   │ Parsley    │ Partial High School │ $10K - $30K   │        222.21 │                4 │
│       7383 │ Steve     │ Vizcarra   │ Partial High School │ $10K - $30K   │        221.85 │                4 │
│       1511 │ Kimberly  │ Ketchum    │ Partial High School │ $10K - $30K   │        221.70 │                4 │
│       2736 │ Kathleen  │ Sgambati   │ Partial High School │ $10K - $30K   │        221.54 │                4 │
│       3277 │ Diane     │ Waterhouse │ Partial High School │ $10K - $30K   │        221.46 │                4 │
│      10222 │ Kathleen  │ Cantu      │ Partial High School │ $10K - $30K   │        221.45 │                4 │
├────────────┴───────────┴────────────┴─────────────────────┴───────────────┴───────────────┴──────────────────┤
│ 8736 rows (20 shown)                                                                               7 columns │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

