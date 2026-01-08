# Cretion of SQL exercises
you are a sql and business intelligence specialist
## the following star/snowflake schema ist given
```yaml
tables:
- tablename: Customer
  columns:
  - columnname: Customerid
    type: INTEGER
  - columnname: Lastname
    type: VARCHAR
  - columnname: Firstname
    type: VARCHAR
  - columnname: City
    type: VARCHAR
  - columnname: State
    type: VARCHAR
  - columnname: Country
    type: VARCHAR
  - columnname: Maritalstatus
    type: VARCHAR
  - columnname: Yearlyincome
    type: VARCHAR
  - columnname: Gender
    type: VARCHAR
  - columnname: Education
    type: VARCHAR
  primary_key:
  - Customerid
- tablename: Product
  columns:
  - columnname: Productid
    type: INTEGER
  - columnname: Pname
    type: VARCHAR
  - columnname: Brand
    type: VARCHAR
  - columnname: Subcategory
    type: VARCHAR
  - columnname: Category
    type: VARCHAR
  - columnname: Department
    type: VARCHAR
  - columnname: Family
    type: VARCHAR
  primary_key:
  - Productid
- tablename: Sales
  columns:
  - columnname: Productid
    type: INTEGER
  - columnname: Timeid
    type: INTEGER
  - columnname: Customerid
    type: INTEGER
  - columnname: Storeid
    type: INTEGER
  - columnname: Storesales
    type: DECIMAL(13,2)
  - columnname: Unitsales
    type: INTEGER
  foreign_keys:
  - sourcecolumns:
    - CustomerId
    targettable: Customer
    targetcolumns:
    - CustomerId
  - sourcecolumns:
    - ProductID
    targettable: Product
    targetcolumns:
    - ProductID
  - sourcecolumns:
    - StoreId
    targettable: Store
    targetcolumns:
    - StoreId
  - sourcecolumns:
    - TimeId
    targettable: TimeByDay
    targetcolumns:
    - TimeId
- tablename: Store
  columns:
  - columnname: Storeid
    type: INTEGER
  - columnname: Stype
    type: VARCHAR
  - columnname: Sname
    type: VARCHAR
  - columnname: City
    type: VARCHAR
  - columnname: State
    type: VARCHAR
  - columnname: Country
    type: VARCHAR
  primary_key:
  - Storeid
- tablename: Timebyday
  columns:
  - columnname: Timeid
    type: INTEGER
  - columnname: TMonth
    type: VARCHAR
  - columnname: TYear
    type: INTEGER
  - columnname: TDayofmonth
    type: INTEGER
  - columnname: TMonthnumber
    type: INTEGER
  - columnname: TQuarter
    type: VARCHAR
  primary_key:
  - Timeid
```
# Semantics of schema
## Multidimensional Schema Analysis

### **Fact Table**
- **Sales** - Contains measures (Storesales, Unitsales) and foreign keys to all dimensions

### **Dimension Tables**
- **Customer** - Customer demographics and location
- **Product** - Product hierarchy and classification
- **Store** - Store type and location
- **TimeByDay** - Time/date attributes

### **Hierarchies**

**Customer Dimension:**
- Geographic: Country → State → City
- Demographic: Education, Maritalstatus, Gender, Yearlyincome (flat attributes)

**Product Dimension:**
- Product: Family → Department → Category → Subcategory → Brand → Product

**Store Dimension:**
- Geographic: Country → State → City
- Store Type: Stype (flat attribute)

**Time Dimension:**
- Temporal: TYear → TQuarter → TMonth → TDayofmonth

### **Relationships**
Star schema with Sales (fact) at center connected to:
- Sales → Customer (via Customerid)
- Sales → Product (via Productid)
- Sales → Store (via Storeid)
- Sales → TimeByDay (via Timeid)

All relationships are many-to-one from fact to dimensions.

## Task
- generate SQL exercises for students with moderate knowledge of SQL
- based on the given database schema
- each exercise should consist of a single sentence 
- provide a solution for each exercise
- generate 5 exercises dealing with subqueries including CTEs
- generate 5 exercises dealing with window functions

# Output
the output should be put into a markdown file with name e-foodmart.md in directory databases/foodmart
it should have the following structure
# Exercises on Subqueries
## Exercise 1
### Text
### SQL Code
## Exercise 2
### Text
### SQL Code
## Exercise 3
### Text
### SQL Code
## Exercise 4
### Text
### SQL Code
## Exercise 5
### Text
### SQL Code
# Exercises on Window Functions
## Exercise 1
### Text
### SQL Code
## Exercise 2
### Text
### SQL Code
## Exercise 3
### Text
### SQL Code
## Exercise 4
### Text
### SQL Code
## Exercise 5
### Text
### SQL Code

Think hard.