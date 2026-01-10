create table DimAccount(
	AccountKey integer not null primary key,
	AccountDescription varchar,
	AccountType varchar
);

create table DimCurrency(
	CurrencyKey integer not null primary key,
	CurrencyName varchar
);

create table DimGeography(
	GeographyKey integer not null primary key,
	City varchar,
	StateProvinceCode varchar,
	StateProvinceName varchar,
	CountryRegionCode varchar,
	EnglishCountryRegionName varchar,
	PostalCode varchar
);

create table DimCustomer(
	CustomerKey integer not null primary key,
	GeographyKey integer,
	FirstName varchar,
	LastName varchar,
	BirthDate date,
	MaritalStatus varchar,
	Gender varchar,
	YearlyIncome decimal(13,2),
	TotalChildren integer,
	NumberChildrenAtHome integer,
	EnglishEducation varchar,
	EnglishOccupation varchar,
	HouseOwnerFlag varchar,
	NumberCarsOwned integer,
  constraint FK_DimCustomer_DimGeography foreign key(GeographyKey) references DimGeography (GeographyKey)
);

create table DimDate(
	DateKey integer not null primary key,
	DayNumberOfWeek integer,
	EnglishDayNameOfWeek varchar,
	DayNumberOfMonth integer,
	DayNumberOfYear integer,
	WeekNumberOfYear integer,
	EnglishMonthName varchar,
	MonthNumberOfYear integer,
	CalendarQuarter integer,
	CalendarYear integer,
	CalendarSemester integer
);


create table DimDepartmentGroup(
	DepartmentGroupKey integer not null primary key,
	DepartmentGroupName varchar,
);

create table DimOrganization(
	OrganizationKey integer not null primary key,
	OrganizationName varchar,
	CurrencyKey integer,
  constraint FK_DimOrganization_DimCurrency foreign key (CurrencyKey) references DimCurrency (CurrencyKey)
);


create table DimProductCategory(
	ProductCategoryKey integer not null primary key,
	EnglishProductCategoryName varchar
);


create table DimProductSubcategory(
	ProductSubcategoryKey integer not null primary key,
	EnglishProductSubcategoryName varchar,
	ProductCategoryKey integer,
  constraint FK_DimProductSubcategory_DimProductCategory foreign key (ProductCategoryKey) references DimProductCategory (ProductCategoryKey)
);


create table DimProduct(
	ProductKey integer not null primary key,
	ProductSubcategoryKey integer,
	EnglishProductName varchar,
  constraint FK_DimProduct_DimProductSubcategory foreign key (ProductSubcategoryKey) references DimProductSubcategory (ProductSubcategoryKey)
);

create table DimPromotion(
	PromotionKey integer not null primary key,
	EnglishPromotionName varchar,
	DiscountPct float,
	EnglishPromotionType varchar,
	EnglishPromotionCategory varchar,
	StartDate datetime,
	EndDate datetime,
	MinQty integer,
	MaxQty integer
);

create table DimScenario(
	ScenarioKey integer not null primary key,
	ScenarioName varchar
);

create table FactFinance(
	FinanceKey integer,
	DateKey integer,
	OrganizationKey integer,
	DepartmentGroupKey integer,
	ScenarioKey integer,
	AccountKey integer,
	Amount float,
  constraint FK_FactFinance_DimScenario foreign key (ScenarioKey) references DimScenario (ScenarioKey),
  constraint FK_FactFinance_DimOrganization foreign key (OrganizationKey) references DimOrganization (OrganizationKey),
  constraint FK_FactFinance_DimDepartmentGroup foreign key (DepartmentGroupKey) references DimDepartmentGroup (DepartmentGroupKey),
  constraint FK_FactFinance_DimDate foreign key (DateKey) references DimDate (DateKey),
  constraint FK_FactFinance_DimAccount foreign key (AccountKey) references DimAccount (AccountKey)
);


create table FactInternetSales(
	ProductKey integer,
	OrderDateKey integer,
	DueDateKey integer,
	ShipDateKey integer,
	CustomerKey integer,
	PromotionKey integer,
	CurrencyKey integer,
	SalesOrderNumber varchar,
	SalesOrderLineNumber integer,
	OrderQuantity integer,
	UnitPrice decimal(13,2),
	SalesAmount decimal(13,2),
  constraint pk_FactInternetSales primary key (SalesOrderNumber, SalesOrderLineNumber),
  constraint FK_FactInternetSales_DimCurrency foreign key (CurrencyKey) references DimCurrency (CurrencyKey),
  constraint FK_FactInternetSales_DimCustomer foreign key (CustomerKey) references DimCustomer (CustomerKey),
  constraint FK_FactInternetSales_DimDate foreign key (OrderDateKey) references DimDate (DateKey),
  constraint FK_FactInternetSales_DimDate1 foreign key (DueDateKey) references DimDate (DateKey),
  constraint FK_FactInternetSales_DimDate2 foreign key (ShipDateKey) references DimDate (DateKey),
  constraint FK_FactInternetSales_DimProduct foreign key (ProductKey) references DimProduct (ProductKey),
  constraint FK_FactInternetSales_DimPromotion foreign key (PromotionKey) references DimPromotion (PromotionKey)
);



create table FactProductInventory(
	ProductKey integer,
	DateKey integer,
	Quantity integer,
  constraint pk_FactProductInventory primary key (ProductKey, DateKey),
  constraint FK_FactProductInventory_DimDate foreign key (DateKey)references DimDate (DateKey),
  constraint FK_FactProductInventory_DimProduct foreign key (ProductKey) references DimProduct (ProductKey)
);


