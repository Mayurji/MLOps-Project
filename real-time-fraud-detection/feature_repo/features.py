from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource, ValueType
from feast.types import Float32, Int32

# Entity for user
user = Entity(name="user_id", join_keys=["user_id"], value_type=ValueType.INT64)

# File source for historical data (even if we use online mostly)
# We can create a dummy parquet for initialization
data_source = FileSource(
    path="/home/mayur/Documents/MLOps-Project/real-time-fraud-detection/feature_repo/data/transactions.parquet",
    event_timestamp_column="event_timestamp",
)

# Feature view
transaction_fv = FeatureView(
    name="transaction_features",
    entities=[user], # entity is the key used to join the features
    ttl=timedelta(days=1), # time to live for the features
    schema=[
        Field(name="amount", dtype=Float32),
        Field(name="transaction_time", dtype=Float32),
        Field(name="user_age", dtype=Int32),
        Field(name="is_international", dtype=Int32),
        Field(name="avg_30d_spending", dtype=Float32),
    ],
    online=True, # online is true when we want to use the features in real-time
    source=data_source, # source is the data source for the features
)
