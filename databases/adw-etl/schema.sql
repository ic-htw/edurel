create table DimCurrency(
	CurrencyKey integer not null primary key,
	CurrencyName varchar
);

create table DimCustomer(
	CustomerKey integer not null primary key,
	FirstName varchar,
	LastName varchar,
	City varchar,
	StateProvinceCode varchar,
	StateProvinceName varchar,
	CountryRegionCode varchar,
	EnglishCountryRegionName varchar,
	PostalCode varchar
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

create table DimProduct(
	ProductKey integer not null primary key,
	EnglishProductName varchar,
	EnglishProductSubcategoryName varchar,
	EnglishProductCategoryName varchar
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


