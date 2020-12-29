import pandas as pd
import numpy as np
max_len= 10
data = pd.DataFrame(columns=np.arange(max_len))
for i in range(10):
    reading = pd.DataFrame([np.arange(20)],columns=np.arange(20))
    data=data.append(reading, ignore_index=True)
remove_cols = [5,6]
data=data.drop(columns=remove_cols)

print()
