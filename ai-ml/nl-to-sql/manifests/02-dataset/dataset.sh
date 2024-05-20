#!/bin/bash

PGPASSWORD=$OWNERPASSWORD psql -U $OWNERUSERNAME -d $DATABASE_NAME -h $POSTGRES_URL -c \
  "CREATE TABLE IF NOT EXISTS customers (
     CustomerID INTEGER PRIMARY KEY,
	   Name VARCHAR(100),
	   Gender VARCHAR(10),
	   Age INTEGER
   );
   CREATE TABLE IF NOT EXISTS transactions (
   	 TransactionID INTEGER PRIMARY KEY,
   	 Date DATE,
   	 CustomerID INTEGER,
   	 ProductCategory VARCHAR(50),
   	 Quantity INTEGER,
   	 PricePerUnit INTEGER,
   	 TotalAmount INTEGER
   );"

PGPASSWORD=$OWNERPASSWORD psql -U $OWNERUSERNAME -d $DATABASE_NAME -h $POSTGRES_URL -c \
   "\copy customers (CustomerID, Name, Gender, Age)
   FROM '/usr/local/dataset/customers.csv'
   WITH CSV HEADER DELIMITER AS ','"

PGPASSWORD=$OWNERPASSWORD psql -U $OWNERUSERNAME -d $DATABASE_NAME -h $POSTGRES_URL -c \
   "\copy transactions (TransactionID, Date, CustomerID, ProductCategory, Quantity, PricePerUnit, TotalAmount)
   FROM '/usr/local/dataset/transactions.csv'
   WITH CSV HEADER DELIMITER AS ','"

