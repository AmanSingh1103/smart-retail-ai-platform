# Azure Data Factory Pipeline

## Pipeline Name
pl_copy_landing_to_raw

## Purpose
This pipeline copies the retail sales CSV file from the landing layer to the raw layer.

## Source
Container: landing  
File: retail_sales.csv

## Sink
Container: raw  
File: retail_sales.csv

## Flow
landing/retail_sales.csv → Azure Data Factory Copy Activity → raw/retail_sales.csv

## Status
Pipeline executed successfully and the raw file was created in Azure Blob Storage.