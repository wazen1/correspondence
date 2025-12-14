import pandas as pd
import numpy as np
import frappe

print(f"Pandas version: {pd.__version__}")
print(f"Numpy version: {np.__version__}")

try:
    data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    df = pd.DataFrame(data)
    print("DataFrame created successfully")
    print(df)
except Exception as e:
    print(f"Error creating DataFrame: {e}")
