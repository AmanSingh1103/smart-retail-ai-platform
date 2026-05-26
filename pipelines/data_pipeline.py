from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when

# Spark session
spark = SparkSession.builder \
    .appName("SmartRetailPipeline") \
    .getOrCreate()

# =========================
# RAW LAYER
# =========================

raw_df = spark.read.csv(
    "data/raw/retail_sales.csv",
    header=True,
    inferSchema=True
)

print("\n========== RAW DATA ==========")
raw_df.show()

# Save raw parquet
raw_df.write.mode("overwrite").parquet(
    "data/staged/raw_parquet"
)

# =========================
# STAGED LAYER
# =========================

staged_df = raw_df.dropna()

staged_df = staged_df.withColumn(
    "discount_flag",
    when(col("discount") > 10, "High")
    .otherwise("Normal")
)

print("\n========== STAGED DATA ==========")
staged_df.show()

# Save staged parquet
staged_df.write.mode("overwrite").parquet(
    "data/staged/staged_parquet"
)

# =========================
# CURATED LAYER
# =========================

curated_df = staged_df.groupBy(
    "product",
    "category"
).sum("sales")

print("\n========== CURATED DATA ==========")
curated_df.show()

# Save curated parquet
curated_df.write.mode("overwrite").parquet(
    "data/curated/curated_parquet"
)

# =========================
# SQL ANALYTICS
# =========================

staged_df.createOrReplaceTempView("sales_table")

result = spark.sql("""
SELECT
    product,
    AVG(sales) as avg_sales,
    MAX(sales) as max_sales
FROM sales_table
GROUP BY product
ORDER BY avg_sales DESC
""")

print("\n========== SQL ANALYTICS ==========")
result.show()

spark.stop()