# Bug Fixing in SQL Query
you are a sql specialist
## the following star/snowflake schema ist given
```yaml
tables:
- tablename: DimAccount
  columns:
  - columnname: AccountKey
    type: INTEGER
  - columnname: ParentAccountKey
    type: INTEGER
  - columnname: AccountCodeAlternateKey
    type: INTEGER
  - columnname: ParentAccountCodeAlternateKey
    type: INTEGER
  - columnname: AccountDescription
    type: VARCHAR
  - columnname: AccountType
    type: VARCHAR
  - columnname: Operator
    type: VARCHAR
  - columnname: CustomMembers
    type: VARCHAR
  - columnname: ValueType
    type: VARCHAR
  - columnname: CustomMemberOptions
    type: VARCHAR
  primary_key:
  - AccountKey
  foreign_keys:
  - sourcecolumns:
    - ParentAccountKey
    targettable: DimAccount
    targetcolumns:
    - AccountKey
- tablename: DimCurrency
  columns:
  - columnname: CurrencyKey
    type: INTEGER
  - columnname: CurrencyAlternateKey
    type: VARCHAR
  - columnname: CurrencyName
    type: VARCHAR
  primary_key:
  - CurrencyKey
- tablename: DimCustomer
  columns:
  - columnname: CustomerKey
    type: INTEGER
  - columnname: GeographyKey
    type: INTEGER
  - columnname: CustomerAlternateKey
    type: VARCHAR
  - columnname: Title
    type: VARCHAR
  - columnname: FirstName
    type: VARCHAR
  - columnname: MiddleName
    type: VARCHAR
  - columnname: LastName
    type: VARCHAR
  - columnname: NameStyle
    type: BIT
  - columnname: BirthDate
    type: DATE
  - columnname: MaritalStatus
    type: VARCHAR
  - columnname: Suffix
    type: VARCHAR
  - columnname: Gender
    type: VARCHAR
  - columnname: EmailAddress
    type: VARCHAR
  - columnname: YearlyIncome
    type: DECIMAL(13,2)
  - columnname: TotalChildren
    type: INTEGER
  - columnname: NumberChildrenAtHome
    type: INTEGER
  - columnname: EnglishEducation
    type: VARCHAR
  - columnname: SpanishEducation
    type: VARCHAR
  - columnname: FrenchEducation
    type: VARCHAR
  - columnname: EnglishOccupation
    type: VARCHAR
  - columnname: SpanishOccupation
    type: VARCHAR
  - columnname: FrenchOccupation
    type: VARCHAR
  - columnname: HouseOwnerFlag
    type: VARCHAR
  - columnname: NumberCarsOwned
    type: INTEGER
  - columnname: AddressLine1
    type: VARCHAR
  - columnname: AddressLine2
    type: VARCHAR
  - columnname: Phone
    type: VARCHAR
  - columnname: DateFirstPurchase
    type: DATE
  - columnname: CommuteDistance
    type: VARCHAR
  primary_key:
  - CustomerKey
  foreign_keys:
  - sourcecolumns:
    - GeographyKey
    targettable: DimGeography
    targetcolumns:
    - GeographyKey
- tablename: DimDate
  columns:
  - columnname: DateKey
    type: INTEGER
  - columnname: FullDateAlternateKey
    type: DATE
  - columnname: DayNumberOfWeek
    type: INTEGER
  - columnname: EnglishDayNameOfWeek
    type: VARCHAR
  - columnname: SpanishDayNameOfWeek
    type: VARCHAR
  - columnname: FrenchDayNameOfWeek
    type: VARCHAR
  - columnname: DayNumberOfMonth
    type: INTEGER
  - columnname: DayNumberOfYear
    type: INTEGER
  - columnname: WeekNumberOfYear
    type: INTEGER
  - columnname: EnglishMonthName
    type: VARCHAR
  - columnname: SpanishMonthName
    type: VARCHAR
  - columnname: FrenchMonthName
    type: VARCHAR
  - columnname: MonthNumberOfYear
    type: INTEGER
  - columnname: CalendarQuarter
    type: INTEGER
  - columnname: CalendarYear
    type: INTEGER
  - columnname: CalendarSemester
    type: INTEGER
  - columnname: FiscalQuarter
    type: INTEGER
  - columnname: FiscalYear
    type: INTEGER
  - columnname: FiscalSemester
    type: INTEGER
  primary_key:
  - DateKey
- tablename: DimDepartmentGroup
  columns:
  - columnname: DepartmentGroupKey
    type: INTEGER
  - columnname: ParentDepartmentGroupKey
    type: INTEGER
  - columnname: DepartmentGroupName
    type: VARCHAR
  primary_key:
  - DepartmentGroupKey
  foreign_keys:
  - sourcecolumns:
    - ParentDepartmentGroupKey
    targettable: DimDepartmentGroup
    targetcolumns:
    - DepartmentGroupKey
- tablename: DimEmployee
  columns:
  - columnname: EmployeeKey
    type: INTEGER
  - columnname: ParentEmployeeKey
    type: INTEGER
  - columnname: EmployeeNationalIDAlternateKey
    type: VARCHAR
  - columnname: ParentEmployeeNationalIDAlternateKey
    type: VARCHAR
  - columnname: SalesTerritoryKey
    type: INTEGER
  - columnname: FirstName
    type: VARCHAR
  - columnname: LastName
    type: VARCHAR
  - columnname: MiddleName
    type: VARCHAR
  - columnname: NameStyle
    type: BIT
  - columnname: Title
    type: VARCHAR
  - columnname: HireDate
    type: DATE
  - columnname: BirthDate
    type: DATE
  - columnname: LoginID
    type: VARCHAR
  - columnname: EmailAddress
    type: VARCHAR
  - columnname: Phone
    type: VARCHAR
  - columnname: MaritalStatus
    type: VARCHAR
  - columnname: EmergencyContactName
    type: VARCHAR
  - columnname: EmergencyContactPhone
    type: VARCHAR
  - columnname: SalariedFlag
    type: BIT
  - columnname: Gender
    type: VARCHAR
  - columnname: PayFrequency
    type: INTEGER
  - columnname: BaseRate
    type: DECIMAL(13,2)
  - columnname: VacationHours
    type: INTEGER
  - columnname: SickLeaveHours
    type: INTEGER
  - columnname: CurrentFlag
    type: BIT
  - columnname: SalesPersonFlag
    type: BIT
  - columnname: DepartmentName
    type: VARCHAR
  - columnname: StartDate
    type: DATE
  - columnname: EndDate
    type: DATE
  - columnname: Status
    type: VARCHAR
  - columnname: EmployeePhoto
    type: VARCHAR
  primary_key:
  - EmployeeKey
  foreign_keys:
  - sourcecolumns:
    - SalesTerritoryKey
    targettable: DimSalesTerritory
    targetcolumns:
    - SalesTerritoryKey
  - sourcecolumns:
    - ParentEmployeeKey
    targettable: DimEmployee
    targetcolumns:
    - EmployeeKey
- tablename: DimGeography
  columns:
  - columnname: GeographyKey
    type: INTEGER
  - columnname: City
    type: VARCHAR
  - columnname: StateProvinceCode
    type: VARCHAR
  - columnname: StateProvinceName
    type: VARCHAR
  - columnname: CountryRegionCode
    type: VARCHAR
  - columnname: EnglishCountryRegionName
    type: VARCHAR
  - columnname: SpanishCountryRegionName
    type: VARCHAR
  - columnname: FrenchCountryRegionName
    type: VARCHAR
  - columnname: PostalCode
    type: VARCHAR
  - columnname: SalesTerritoryKey
    type: INTEGER
  - columnname: IpAddressLocator
    type: VARCHAR
  primary_key:
  - GeographyKey
  foreign_keys:
  - sourcecolumns:
    - SalesTerritoryKey
    targettable: DimSalesTerritory
    targetcolumns:
    - SalesTerritoryKey
- tablename: DimOrganization
  columns:
  - columnname: OrganizationKey
    type: INTEGER
  - columnname: ParentOrganizationKey
    type: INTEGER
  - columnname: PercentageOfOwnership
    type: VARCHAR
  - columnname: OrganizationName
    type: VARCHAR
  - columnname: CurrencyKey
    type: INTEGER
  primary_key:
  - OrganizationKey
  foreign_keys:
  - sourcecolumns:
    - CurrencyKey
    targettable: DimCurrency
    targetcolumns:
    - CurrencyKey
  - sourcecolumns:
    - ParentOrganizationKey
    targettable: DimOrganization
    targetcolumns:
    - OrganizationKey
- tablename: DimProduct
  columns:
  - columnname: ProductKey
    type: INTEGER
  - columnname: ProductAlternateKey
    type: VARCHAR
  - columnname: ProductSubcategoryKey
    type: INTEGER
  - columnname: WeightUnitMeasureCode
    type: VARCHAR
  - columnname: SizeUnitMeasureCode
    type: VARCHAR
  - columnname: EnglishProductName
    type: VARCHAR
  - columnname: SpanishProductName
    type: VARCHAR
  - columnname: FrenchProductName
    type: VARCHAR
  - columnname: StandardCost
    type: DECIMAL(13,2)
  - columnname: FinishedGoodsFlag
    type: BIT
  - columnname: Color
    type: VARCHAR
  - columnname: SafetyStockLevel
    type: INTEGER
  - columnname: ReorderPoint
    type: INTEGER
  - columnname: ListPrice
    type: DECIMAL(13,2)
  - columnname: Size
    type: VARCHAR
  - columnname: SizeRange
    type: VARCHAR
  - columnname: Weight
    type: FLOAT
  - columnname: DaysToManufacture
    type: INTEGER
  - columnname: ProductLine
    type: VARCHAR
  - columnname: DealerPrice
    type: DECIMAL(13,2)
  - columnname: Class
    type: VARCHAR
  - columnname: Style
    type: VARCHAR
  - columnname: ModelName
    type: VARCHAR
  - columnname: LargePhoto
    type: VARCHAR
  - columnname: EnglishDescription
    type: VARCHAR
  - columnname: FrenchDescription
    type: VARCHAR
  - columnname: ChineseDescription
    type: VARCHAR
  - columnname: ArabicDescription
    type: VARCHAR
  - columnname: HebrewDescription
    type: VARCHAR
  - columnname: ThaiDescription
    type: VARCHAR
  - columnname: GermanDescription
    type: VARCHAR
  - columnname: JapaneseDescription
    type: VARCHAR
  - columnname: TurkishDescription
    type: VARCHAR
  - columnname: StartDate
    type: TIMESTAMP
  - columnname: EndDate
    type: TIMESTAMP
  - columnname: Status
    type: VARCHAR
  primary_key:
  - ProductKey
  foreign_keys:
  - sourcecolumns:
    - ProductSubcategoryKey
    targettable: DimProductSubcategory
    targetcolumns:
    - ProductSubcategoryKey
- tablename: DimProductCategory
  columns:
  - columnname: ProductCategoryKey
    type: INTEGER
  - columnname: ProductCategoryAlternateKey
    type: INTEGER
  - columnname: EnglishProductCategoryName
    type: VARCHAR
  - columnname: SpanishProductCategoryName
    type: VARCHAR
  - columnname: FrenchProductCategoryName
    type: VARCHAR
  primary_key:
  - ProductCategoryKey
- tablename: DimProductSubcategory
  columns:
  - columnname: ProductSubcategoryKey
    type: INTEGER
  - columnname: ProductSubcategoryAlternateKey
    type: INTEGER
  - columnname: EnglishProductSubcategoryName
    type: VARCHAR
  - columnname: SpanishProductSubcategoryName
    type: VARCHAR
  - columnname: FrenchProductSubcategoryName
    type: VARCHAR
  - columnname: ProductCategoryKey
    type: INTEGER
  primary_key:
  - ProductSubcategoryKey
  foreign_keys:
  - sourcecolumns:
    - ProductCategoryKey
    targettable: DimProductCategory
    targetcolumns:
    - ProductCategoryKey
- tablename: DimPromotion
  columns:
  - columnname: PromotionKey
    type: INTEGER
  - columnname: PromotionAlternateKey
    type: INTEGER
  - columnname: EnglishPromotionName
    type: VARCHAR
  - columnname: SpanishPromotionName
    type: VARCHAR
  - columnname: FrenchPromotionName
    type: VARCHAR
  - columnname: DiscountPct
    type: FLOAT
  - columnname: EnglishPromotionType
    type: VARCHAR
  - columnname: SpanishPromotionType
    type: VARCHAR
  - columnname: FrenchPromotionType
    type: VARCHAR
  - columnname: EnglishPromotionCategory
    type: VARCHAR
  - columnname: SpanishPromotionCategory
    type: VARCHAR
  - columnname: FrenchPromotionCategory
    type: VARCHAR
  - columnname: StartDate
    type: TIMESTAMP
  - columnname: EndDate
    type: TIMESTAMP
  - columnname: MinQty
    type: INTEGER
  - columnname: MaxQty
    type: INTEGER
  primary_key:
  - PromotionKey
- tablename: DimReseller
  columns:
  - columnname: ResellerKey
    type: INTEGER
  - columnname: GeographyKey
    type: INTEGER
  - columnname: ResellerAlternateKey
    type: VARCHAR
  - columnname: Phone
    type: VARCHAR
  - columnname: BusinessType
    type: VARCHAR
  - columnname: ResellerName
    type: VARCHAR
  - columnname: NumberEmployees
    type: INTEGER
  - columnname: OrderFrequency
    type: VARCHAR
  - columnname: OrderMonth
    type: INTEGER
  - columnname: FirstOrderYear
    type: INTEGER
  - columnname: LastOrderYear
    type: INTEGER
  - columnname: ProductLine
    type: VARCHAR
  - columnname: AddressLine1
    type: VARCHAR
  - columnname: AddressLine2
    type: VARCHAR
  - columnname: AnnualSales
    type: DECIMAL(13,2)
  - columnname: BankName
    type: VARCHAR
  - columnname: MinPaymentType
    type: INTEGER
  - columnname: MinPaymentAmount
    type: DECIMAL(13,2)
  - columnname: AnnualRevenue
    type: DECIMAL(13,2)
  - columnname: YearOpened
    type: INTEGER
  primary_key:
  - ResellerKey
  foreign_keys:
  - sourcecolumns:
    - GeographyKey
    targettable: DimGeography
    targetcolumns:
    - GeographyKey
- tablename: DimSalesReason
  columns:
  - columnname: SalesReasonKey
    type: INTEGER
  - columnname: SalesReasonAlternateKey
    type: INTEGER
  - columnname: SalesReasonName
    type: VARCHAR
  - columnname: SalesReasonReasonType
    type: VARCHAR
  primary_key:
  - SalesReasonKey
- tablename: DimSalesTerritory
  columns:
  - columnname: SalesTerritoryKey
    type: INTEGER
  - columnname: SalesTerritoryAlternateKey
    type: INTEGER
  - columnname: SalesTerritoryRegion
    type: VARCHAR
  - columnname: SalesTerritoryCountry
    type: VARCHAR
  - columnname: SalesTerritoryGroup
    type: VARCHAR
  - columnname: SalesTerritoryImage
    type: VARCHAR
  primary_key:
  - SalesTerritoryKey
- tablename: DimScenario
  columns:
  - columnname: ScenarioKey
    type: INTEGER
  - columnname: ScenarioName
    type: VARCHAR
  primary_key:
  - ScenarioKey
- tablename: FactCallCenter
  columns:
  - columnname: FactCallCenterID
    type: INTEGER
  - columnname: DateKey
    type: INTEGER
  - columnname: WageType
    type: VARCHAR
  - columnname: Shift
    type: VARCHAR
  - columnname: LevelOneOperators
    type: INTEGER
  - columnname: LevelTwoOperators
    type: INTEGER
  - columnname: TotalOperators
    type: INTEGER
  - columnname: Calls
    type: INTEGER
  - columnname: AutomaticResponses
    type: INTEGER
  - columnname: Orders
    type: INTEGER
  - columnname: IssuesRaised
    type: INTEGER
  - columnname: AverageTimePerIssue
    type: INTEGER
  - columnname: ServiceGrade
    type: FLOAT
  - columnname: Date
    type: TIMESTAMP
  foreign_keys:
  - sourcecolumns:
    - DateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
- tablename: FactCurrencyRate
  columns:
  - columnname: CurrencyKey
    type: INTEGER
  - columnname: DateKey
    type: INTEGER
  - columnname: AverageRate
    type: FLOAT
  - columnname: EndOfDayRate
    type: FLOAT
  - columnname: Date
    type: TIMESTAMP
  foreign_keys:
  - sourcecolumns:
    - DateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - CurrencyKey
    targettable: DimCurrency
    targetcolumns:
    - CurrencyKey
- tablename: FactFinance
  columns:
  - columnname: FinanceKey
    type: INTEGER
  - columnname: DateKey
    type: INTEGER
  - columnname: OrganizationKey
    type: INTEGER
  - columnname: DepartmentGroupKey
    type: INTEGER
  - columnname: ScenarioKey
    type: INTEGER
  - columnname: AccountKey
    type: INTEGER
  - columnname: Amount
    type: FLOAT
  - columnname: Date
    type: TIMESTAMP
  foreign_keys:
  - sourcecolumns:
    - ScenarioKey
    targettable: DimScenario
    targetcolumns:
    - ScenarioKey
  - sourcecolumns:
    - OrganizationKey
    targettable: DimOrganization
    targetcolumns:
    - OrganizationKey
  - sourcecolumns:
    - DepartmentGroupKey
    targettable: DimDepartmentGroup
    targetcolumns:
    - DepartmentGroupKey
  - sourcecolumns:
    - DateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - AccountKey
    targettable: DimAccount
    targetcolumns:
    - AccountKey
- tablename: FactInternetSales
  columns:
  - columnname: ProductKey
    type: INTEGER
  - columnname: OrderDateKey
    type: INTEGER
  - columnname: DueDateKey
    type: INTEGER
  - columnname: ShipDateKey
    type: INTEGER
  - columnname: CustomerKey
    type: INTEGER
  - columnname: PromotionKey
    type: INTEGER
  - columnname: CurrencyKey
    type: INTEGER
  - columnname: SalesTerritoryKey
    type: INTEGER
  - columnname: SalesOrderNumber
    type: VARCHAR
  - columnname: SalesOrderLineNumber
    type: INTEGER
  - columnname: RevisionNumber
    type: INTEGER
  - columnname: OrderQuantity
    type: INTEGER
  - columnname: UnitPrice
    type: DECIMAL(13,2)
  - columnname: ExtendedAmount
    type: DECIMAL(13,2)
  - columnname: UnitPriceDiscountPct
    type: FLOAT
  - columnname: DiscountAmount
    type: FLOAT
  - columnname: ProductStandardCost
    type: DECIMAL(13,2)
  - columnname: TotalProductCost
    type: DECIMAL(13,2)
  - columnname: SalesAmount
    type: DECIMAL(13,2)
  - columnname: TaxAmt
    type: DECIMAL(13,2)
  - columnname: Freight
    type: DECIMAL(13,2)
  - columnname: CarrierTrackingNumber
    type: VARCHAR
  - columnname: CustomerPONumber
    type: VARCHAR
  - columnname: OrderDate
    type: TIMESTAMP
  - columnname: DueDate
    type: TIMESTAMP
  - columnname: ShipDate
    type: TIMESTAMP
  primary_key:
  - SalesOrderNumber
  - SalesOrderLineNumber
  foreign_keys:
  - sourcecolumns:
    - CurrencyKey
    targettable: DimCurrency
    targetcolumns:
    - CurrencyKey
  - sourcecolumns:
    - CustomerKey
    targettable: DimCustomer
    targetcolumns:
    - CustomerKey
  - sourcecolumns:
    - OrderDateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - DueDateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - ShipDateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - ProductKey
    targettable: DimProduct
    targetcolumns:
    - ProductKey
  - sourcecolumns:
    - PromotionKey
    targettable: DimPromotion
    targetcolumns:
    - PromotionKey
  - sourcecolumns:
    - SalesTerritoryKey
    targettable: DimSalesTerritory
    targetcolumns:
    - SalesTerritoryKey
- tablename: FactInternetSalesReason
  columns:
  - columnname: SalesOrderNumber
    type: VARCHAR
  - columnname: SalesOrderLineNumber
    type: INTEGER
  - columnname: SalesReasonKey
    type: INTEGER
  foreign_keys:
  - sourcecolumns:
    - SalesOrderNumber
    - SalesOrderLineNumber
    targettable: FactInternetSales
    targetcolumns:
    - SalesOrderNumber
    - SalesOrderLineNumber
  - sourcecolumns:
    - SalesReasonKey
    targettable: DimSalesReason
    targetcolumns:
    - SalesReasonKey
- tablename: FactProductInventory
  columns:
  - columnname: ProductKey
    type: INTEGER
  - columnname: DateKey
    type: INTEGER
  - columnname: MovementDate
    type: DATE
  - columnname: UnitCost
    type: DECIMAL(13,2)
  - columnname: UnitsIn
    type: INTEGER
  - columnname: UnitsOut
    type: INTEGER
  - columnname: UnitsBalance
    type: INTEGER
  foreign_keys:
  - sourcecolumns:
    - DateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - ProductKey
    targettable: DimProduct
    targetcolumns:
    - ProductKey
- tablename: FactResellerSales
  columns:
  - columnname: ProductKey
    type: INTEGER
  - columnname: OrderDateKey
    type: INTEGER
  - columnname: DueDateKey
    type: INTEGER
  - columnname: ShipDateKey
    type: INTEGER
  - columnname: ResellerKey
    type: INTEGER
  - columnname: EmployeeKey
    type: INTEGER
  - columnname: PromotionKey
    type: INTEGER
  - columnname: CurrencyKey
    type: INTEGER
  - columnname: SalesTerritoryKey
    type: INTEGER
  - columnname: SalesOrderNumber
    type: VARCHAR
  - columnname: SalesOrderLineNumber
    type: INTEGER
  - columnname: RevisionNumber
    type: INTEGER
  - columnname: OrderQuantity
    type: INTEGER
  - columnname: UnitPrice
    type: DECIMAL(13,2)
  - columnname: ExtendedAmount
    type: DECIMAL(13,2)
  - columnname: UnitPriceDiscountPct
    type: FLOAT
  - columnname: DiscountAmount
    type: FLOAT
  - columnname: ProductStandardCost
    type: DECIMAL(13,2)
  - columnname: TotalProductCost
    type: DECIMAL(13,2)
  - columnname: SalesAmount
    type: DECIMAL(13,2)
  - columnname: TaxAmt
    type: DECIMAL(13,2)
  - columnname: Freight
    type: DECIMAL(13,2)
  - columnname: CarrierTrackingNumber
    type: VARCHAR
  - columnname: CustomerPONumber
    type: VARCHAR
  - columnname: OrderDate
    type: TIMESTAMP
  - columnname: DueDate
    type: TIMESTAMP
  - columnname: ShipDate
    type: TIMESTAMP
  foreign_keys:
  - sourcecolumns:
    - CurrencyKey
    targettable: DimCurrency
    targetcolumns:
    - CurrencyKey
  - sourcecolumns:
    - OrderDateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - DueDateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - ShipDateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - EmployeeKey
    targettable: DimEmployee
    targetcolumns:
    - EmployeeKey
  - sourcecolumns:
    - ProductKey
    targettable: DimProduct
    targetcolumns:
    - ProductKey
  - sourcecolumns:
    - PromotionKey
    targettable: DimPromotion
    targetcolumns:
    - PromotionKey
  - sourcecolumns:
    - ResellerKey
    targettable: DimReseller
    targetcolumns:
    - ResellerKey
  - sourcecolumns:
    - SalesTerritoryKey
    targettable: DimSalesTerritory
    targetcolumns:
    - SalesTerritoryKey
- tablename: FactSalesQuota
  columns:
  - columnname: SalesQuotaKey
    type: INTEGER
  - columnname: EmployeeKey
    type: INTEGER
  - columnname: DateKey
    type: INTEGER
  - columnname: CalendarYear
    type: INTEGER
  - columnname: CalendarQuarter
    type: INTEGER
  - columnname: SalesAmountQuota
    type: DECIMAL(13,2)
  - columnname: Date
    type: TIMESTAMP
  foreign_keys:
  - sourcecolumns:
    - EmployeeKey
    targettable: DimEmployee
    targetcolumns:
    - EmployeeKey
  - sourcecolumns:
    - DateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
- tablename: FactSurveyResponse
  columns:
  - columnname: SurveyResponseKey
    type: INTEGER
  - columnname: DateKey
    type: INTEGER
  - columnname: CustomerKey
    type: INTEGER
  - columnname: ProductCategoryKey
    type: INTEGER
  - columnname: EnglishProductCategoryName
    type: VARCHAR
  - columnname: ProductSubcategoryKey
    type: INTEGER
  - columnname: EnglishProductSubcategoryName
    type: VARCHAR
  - columnname: Date
    type: TIMESTAMP
  foreign_keys:
  - sourcecolumns:
    - DateKey
    targettable: DimDate
    targetcolumns:
    - DateKey
  - sourcecolumns:
    - CustomerKey
    targettable: DimCustomer
    targetcolumns:
    - CustomerKey
```
# Semantics of schema
## Fact Tables, Dimensions, Hirarchies
### **Fact Tables** (contain metrics/measures)
1. **FactInternetSales** - Internet sales transactions
2. **FactResellerSales** - Reseller sales transactions
3. **FactFinance** - Financial data
4. **FactCallCenter** - Call center operations
5. **FactCurrencyRate** - Currency exchange rates
6. **FactProductInventory** - Product inventory movements
7. **FactSalesQuota** - Sales quotas for employees
8. **FactSurveyResponse** - Customer survey responses
9. **FactInternetSalesReason** - Bridge table linking sales to reasons

### **Dimension Tables** (contain descriptive attributes)
- **DimDate** - Time dimension
- **DimProduct** - Product information
- **DimCustomer** - Customer details
- **DimEmployee** - Employee information
- **DimReseller** - Reseller details
- **DimGeography** - Geographic locations
- **DimCurrency** - Currency information
- **DimPromotion** - Promotion details
- **DimSalesTerritory** - Sales territory data
- **DimSalesReason** - Sales reason categories
- **DimAccount** - Account information
- **DimOrganization** - Organization structure
- **DimDepartmentGroup** - Department groups
- **DimScenario** - Scenario planning
- **DimProductCategory** - Product categories
- **DimProductSubcategory** - Product subcategories

### **Hierarchies**

**Product Hierarchy:**
- DimProduct → DimProductSubcategory → DimProductCategory

**Geography Hierarchy:**
- DimGeography: City → StateProvince → Country → SalesTerritory

**Time Hierarchy:**
- DimDate: Day → Week → Month → Quarter → Semester → Year (both Calendar and Fiscal)

**Employee Hierarchy:**
- DimEmployee (ParentEmployeeKey → EmployeeKey) - organizational reporting structure

**Account Hierarchy:**
- DimAccount (ParentAccountKey → AccountKey) - chart of accounts structure

**Organization Hierarchy:**
- DimOrganization (ParentOrganizationKey → OrganizationKey) - corporate structure

**Department Hierarchy:**
- DimDepartmentGroup (ParentDepartmentGroupKey → DepartmentGroupKey)

**Customer-Geography:**
- DimCustomer → DimGeography → DimSalesTerritory

This is a classic **star/snowflake schema** for enterprise sales and financial analytics.

## Fact Table Relationships

### **FactInternetSales**
- **DimProduct** - What was sold
- **DimCustomer** - Who bought it
- **DimDate** (3x) - OrderDateKey, DueDateKey, ShipDateKey (when ordered/due/shipped)
- **DimPromotion** - Which promotion applied
- **DimCurrency** - Transaction currency
- **DimSalesTerritory** - Sales region

### **FactResellerSales**
- **DimProduct** - What was sold
- **DimReseller** - Which reseller made the sale
- **DimEmployee** - Employee who handled the sale
- **DimDate** (3x) - OrderDateKey, DueDateKey, ShipDateKey
- **DimPromotion** - Promotion applied
- **DimCurrency** - Transaction currency
- **DimSalesTerritory** - Sales region

### **FactFinance**
- **DimDate** - Financial period
- **DimOrganization** - Which organizational unit
- **DimDepartmentGroup** - Which department
- **DimScenario** - Budget/Actual/Forecast scenario
- **DimAccount** - Chart of accounts (revenue/expense type)

### **FactCallCenter**
- **DimDate** - Date of call center metrics

### **FactCurrencyRate**
- **DimDate** - Date of exchange rate
- **DimCurrency** - Which currency

### **FactProductInventory**
- **DimProduct** - Which product
- **DimDate** - Date of inventory movement

### **FactSalesQuota**
- **DimEmployee** - Employee with quota
- **DimDate** - Quota period

### **FactSurveyResponse**
- **DimDate** - Survey date
- **DimCustomer** - Customer responding
- **DimProductCategory** - (denormalized reference)
- **DimProductSubcategory** - (denormalized reference)

### **FactInternetSalesReason** (Bridge Table)
- **FactInternetSales** - Links to sales transaction
- **DimSalesReason** - Reason for purchase (many-to-many relationship)

## Query
```sql
WITH CustomerFirstLastPurchase AS (
    SELECT
        fis.CustomerKey,
        MIN(fis.OrderDate) AS FirstPurchaseDate,
        MAX(fis.OrderDate) AS LastPurchaseDate,
        COUNT(DISTINCT fis.SalesOrderNumber) AS TotalOrders,
        COUNT(*) AS TotalLineItems,
        CAST(JULIANDAY(MAX(fis.OrderDate)) - JULIANDAY(MIN(fis.OrderDate)) AS INTEGER) AS CustomerTenureDays
    FROM FactInternetSales fis
    GROUP BY fis.CustomerKey
),

CustomerLifetimeMetrics AS (
    SELECT
        fis.CustomerKey,
        c.FirstName || ' ' || c.LastName AS CustomerName,
        c.YearlyIncome,
        c.EnglishEducation AS Education,
        c.EnglishOccupation AS Occupation,
        c.Gender,
        c.MaritalStatus,
        c.TotalChildren,
        c.NumberCarsOwned,
        c.HouseOwnerFlag,
        g.EnglishCountryRegionName AS Country,
        g.StateProvinceName AS State,
        g.City,
        st.SalesTerritoryRegion,
        cflp.FirstPurchaseDate,
        cflp.LastPurchaseDate,
        cflp.CustomerTenureDays,
        ROUND(cflp.CustomerTenureDays / 365.25, 2) AS CustomerTenureYears,
        CAST(JULIANDAY('now') - JULIANDAY(cflp.LastPurchaseDate) AS INTEGER) AS DaysSinceLastPurchase,
        cflp.TotalOrders,
        cflp.TotalLineItems,
        COUNT(DISTINCT DATE(fis.OrderDate)) AS UniquePurchaseDays,
        SUM(fis.OrderQuantity) AS TotalUnits,
        ROUND(SUM(fis.SalesAmount), 2) AS LifetimeRevenue,
        ROUND(SUM(fis.SalesAmount - fis.TotalProductCost), 2) AS LifetimeGrossProfit,
        ROUND(100.0 * SUM(fis.SalesAmount - fis.TotalProductCost) / NULLIF(SUM(fis.SalesAmount), 0), 2) AS LifetimeMarginPct,
        ROUND(AVG(fis.SalesAmount), 2) AS AvgLineItemValue,
        ROUND(SUM(fis.SalesAmount) / NULLIF(cflp.TotalOrders, 0), 2) AS AvgOrderValue,
        ROUND(SUM(fis.DiscountAmount), 2) AS TotalDiscounts,
        ROUND(100.0 * SUM(fis.DiscountAmount) / NULLIF(SUM(fis.SalesAmount + fis.DiscountAmount), 0), 2) AS AvgDiscountPct,
        COUNT(DISTINCT pc.EnglishProductCategoryName) AS UniqueCategories,
        COUNT(DISTINCT fis.ProductKey) AS UniqueProducts
    FROM FactInternetSales fis
    INNER JOIN CustomerFirstLastPurchase cflp ON fis.CustomerKey = cflp.CustomerKey
    INNER JOIN DimCustomer c ON fis.CustomerKey = c.CustomerKey
    INNER JOIN DimGeography g ON c.GeographyKey = g.GeographyKey
    INNER JOIN DimSalesTerritory st ON g.SalesTerritoryKey = st.SalesTerritoryKey
    INNER JOIN DimProduct p ON fis.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory psc ON p.ProductSubcategoryKey = psc.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc ON psc.ProductCategoryKey = pc.ProductCategoryKey
    GROUP BY fis.CustomerKey, c.FirstName, c.LastName, c.YearlyIncome, c.EnglishEducation,
             c.EnglishOccupation, c.Gender, c.MaritalStatus, c.TotalChildren, c.NumberCarsOwned,
             c.HouseOwnerFlag, g.EnglishCountryRegionName, g.StateProvinceName, g.City,
             st.SalesTerritoryRegion, cflp.FirstPurchaseDate, cflp.LastPurchaseDate,
             cflp.CustomerTenureDays, cflp.TotalOrders, cflp.TotalLineItems
),

CustomerValueMetrics AS (
    SELECT
        clm.*,
        -- Annualized metrics
        ROUND(clm.LifetimeRevenue / NULLIF(clm.CustomerTenureYears, 0), 2) AS RevenuePerYear,
        ROUND(clm.LifetimeGrossProfit / NULLIF(clm.CustomerTenureYears, 0), 2) AS ProfitPerYear,
        ROUND(clm.TotalOrders / NULLIF(clm.CustomerTenureYears, 0), 2) AS OrdersPerYear,
        -- Purchase frequency (days between orders)
        ROUND(clm.CustomerTenureDays / NULLIF(clm.TotalOrders - 1, 0), 2) AS AvgDaysBetweenOrders,
        -- Customer activity ratio (purchase days / tenure days)
        ROUND(100.0 * clm.UniquePurchaseDays / NULLIF(clm.CustomerTenureDays, 0), 2) AS ActivityRatioPct,
        -- Recency score (0-100, higher is better/more recent)
        CASE
            WHEN clm.DaysSinceLastPurchase <= 30 THEN 100
            WHEN clm.DaysSinceLastPurchase <= 90 THEN 80
            WHEN clm.DaysSinceLastPurchase <= 180 THEN 60
            WHEN clm.DaysSinceLastPurchase <= 365 THEN 40
            WHEN clm.DaysSinceLastPurchase <= 730 THEN 20
            ELSE 0
        END AS RecencyScore,
        -- Frequency quintile (relative to other customers)
        NTILE(5) OVER (ORDER BY clm.TotalOrders DESC) AS FrequencyQuintile,
        -- Monetary quintile (relative to other customers)
        NTILE(5) OVER (ORDER BY clm.LifetimeRevenue DESC) AS MonetaryQuintile
    FROM CustomerLifetimeMetrics clm
),

CustomerValueScoring AS (
    SELECT
        cvm.*,
        -- Comprehensive value score (0-100)
        ROUND(
            (cvm.MonetaryQuintile * 20) +  -- Revenue contribution (40%)
            (cvm.FrequencyQuintile * 16) +  -- Purchase frequency (32%)
            (cvm.RecencyScore * 0.20) +     -- Recency (20%)
            (CASE WHEN cvm.LifetimeMarginPct > 30 THEN 8 ELSE cvm.LifetimeMarginPct * 0.267 END) -- Profitability (8%)
        , 2) AS CustomerValueScore,
        RANK() OVER (ORDER BY cvm.LifetimeRevenue DESC) AS RevenueRank,
        RANK() OVER (ORDER BY cvm.LifetimeGrossProfit DESC) AS ProfitRank
    FROM CustomerValueMetrics cvm
),

CustomerTiering AS (
    SELECT
        cvs.*,
        CASE
            WHEN cvs.CustomerValueScore >= 80 THEN 'Platinum'
            WHEN cvs.CustomerValueScore >= 60 THEN 'Gold'
            WHEN cvs.CustomerValueScore >= 40 THEN 'Silver'
            ELSE 'Bronze'
        END AS CustomerTier,
        CASE
            WHEN cvs.RevenueRank <= (SELECT COUNT(*) * 0.01 FROM CustomerValueScoring) THEN 'Top 1%'
            WHEN cvs.RevenueRank <= (SELECT COUNT(*) * 0.05 FROM CustomerValueScoring) THEN 'Top 5%'
            WHEN cvs.RevenueRank <= (SELECT COUNT(*) * 0.10 FROM CustomerValueScoring) THEN 'Top 10%'
            WHEN cvs.RevenueRank <= (SELECT COUNT(*) * 0.25 FROM CustomerValueScoring) THEN 'Top 25%'
            ELSE 'Below Top 25%'
        END AS RevenuePercentile
    FROM CustomerValueScoring cvs
),

DemographicByTier AS (
    SELECT
        ct.CustomerTier,
        COUNT(*) AS CustomerCount,
        ROUND(AVG(ct.YearlyIncome), 2) AS AvgYearlyIncome,
        ROUND(AVG(ct.LifetimeRevenue), 2) AS AvgLifetimeRevenue,
        ROUND(AVG(ct.LifetimeGrossProfit), 2) AS AvgLifetimeGrossProfit,
        ROUND(AVG(ct.CustomerTenureYears), 2) AS AvgTenureYears,
        ROUND(AVG(ct.TotalOrders), 2) AS AvgTotalOrders,
        ROUND(AVG(ct.AvgOrderValue), 2) AS AvgOrderValue,
        ROUND(AVG(ct.DaysSinceLastPurchase), 2) AS AvgDaysSinceLastPurchase,
        ROUND(SUM(ct.LifetimeRevenue), 2) AS TotalTierRevenue,
        ROUND(100.0 * SUM(ct.LifetimeRevenue) / (SELECT SUM(LifetimeRevenue) FROM CustomerTiering), 2) AS TierRevenueSharePct,
        MODE() WITHIN GROUP (ORDER BY ct.Education) AS MostCommonEducation,
        MODE() WITHIN GROUP (ORDER BY ct.Occupation) AS MostCommonOccupation
    FROM CustomerTiering ct
    GROUP BY ct.CustomerTier
)

SELECT
    ct.CustomerKey,
    ct.CustomerName,
    ct.CustomerTier,
    ct.RevenuePercentile,
    ct.CustomerValueScore,
    ct.Country,
    ct.State,
    ct.SalesTerritoryRegion,
    ct.YearlyIncome,
    ct.Education,
    ct.Occupation,
    ct.Gender,
    ct.MaritalStatus,
    ct.FirstPurchaseDate,
    ct.LastPurchaseDate,
    ct.CustomerTenureYears,
    ct.DaysSinceLastPurchase,
    ct.TotalOrders,
    ct.LifetimeRevenue,
    ct.LifetimeGrossProfit,
    ct.LifetimeMarginPct,
    ct.AvgOrderValue,
    ct.AvgLineItemValue,
    ct.RevenuePerYear,
    ct.ProfitPerYear,
    ct.OrdersPerYear,
    ct.AvgDaysBetweenOrders,
    ct.TotalDiscounts,
    ct.AvgDiscountPct,
    ct.UniqueCategories,
    ct.UniqueProducts,
    ct.RecencyScore,
    ct.FrequencyQuintile,
    ct.MonetaryQuintile,
    ct.RevenueRank,
    ct.ProfitRank
FROM CustomerTiering ct
ORDER BY ct.CustomerValueScore DESC, ct.LifetimeRevenue DESC;
```


## Task
- fix bugs in the given query 
- provide correct code for duckdb database system 
- fix wrong column names
- fix wrong function names
- the following error messages were given:
  - Scalar Function with name julianday does not exist!
- provide the rewritten query in file clv-01.sql in directory experiments/correct-sql/adw-olap
- only provide sql code


Think hard.