from pyspark.sql.functions import (
    col,
    when,
    to_date,
    dayofmonth,
    month,
    dayofweek,
    avg,
    max as spark_max,
    sum as spark_sum
)

# ==================================================
# Azure Storage Configuration
# ==================================================

storage_account = "smartstorage321"

# NOTE:
# In Databricks notebook, paste storage key directly only for demo
# OR use Databricks secrets in production.
storage_key = "PASTE_STORAGE_ACCOUNT_KEY_IN_DATABRICKS_ONLY"

spark.conf.set(
    f"fs.azure.account.key.{storage_account}.blob.core.windows.net",
    storage_key
)

raw_path = f"wasbs://raw@{storage_account}.blob.core.windows.net/retail_sales.csv"
staged_path = f"wasbs://staged@{storage_account}.blob.core.windows.net/retail_sales_staged_parquet"
curated_path = f"wasbs://curated@{storage_account}.blob.core.windows.net/retail_sales_curated_parquet"
sql_output_path = f"wasbs://curated@{storage_account}.blob.core.windows.net/sql_analytics_parquet"

# ==================================================
# Raw Layer
# ==================================================

raw_df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(raw_path)
)

print("========== RAW DATA ==========")
display(raw_df)

# ==================================================
# Staged Layer
# Cleaning + Feature Engineering
# ==================================================

staged_df = (
    raw_df
    .dropna()
    .withColumn("date", to_date(col("date")))
    .withColumn("day", dayofmonth(col("date")))
    .withColumn("month", month(col("date")))
    .withColumn("weekday", dayofweek(col("date")))
    .withColumn(
        "discount_flag",
        when(col("discount") > 10, "High").otherwise("Normal")
    )
)

print("========== STAGED DATA ==========")
display(staged_df)

staged_df.write.mode("overwrite").parquet(staged_path)

print("Staged parquet saved successfully!")

# ==================================================
# Curated Layer
# Aggregated Analytics-Ready Data
# ==================================================

curated_df = (
    staged_df
    .groupBy("product", "category", "region")
    .agg(
        spark_sum("sales").alias("total_sales"),
        avg("sales").alias("avg_sales"),
        spark_max("sales").alias("max_sales"),
        avg("price").alias("avg_price"),
        spark_sum("discount").alias("total_discount")
    )
    .orderBy(col("total_sales").desc())
)

print("========== CURATED DATA ==========")
display(curated_df)

curated_df.write.mode("overwrite").parquet(curated_path)

print("Curated parquet saved successfully!")

# ==================================================
# Spark SQL Analytics
# ==================================================

staged_df.createOrReplaceTempView("sales_table")

sql_result = spark.sql("""
SELECT
    product,
    category,
    ROUND(AVG(sales), 2) AS avg_sales,
    MAX(sales) AS max_sales,
    SUM(sales) AS total_sales
FROM sales_table
GROUP BY product, category
ORDER BY total_sales DESC
""")

print("========== SPARK SQL ANALYTICS ==========")
display(sql_result)

sql_result.write.mode("overwrite").parquet(sql_output_path)

print("SQL analytics parquet saved successfully!")

# ==================================================
# Final Status
# ==================================================

print("DATA ENGINEERING PIPELINE COMPLETED SUCCESSFULLY")
print("RAW → STAGED → CURATED flow completed")
print("Staged parquet path:", staged_path)
print("Curated parquet path:", curated_path)
print("SQL analytics parquet path:", sql_output_path)