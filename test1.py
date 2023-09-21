import pandas as pd


data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35]
}
df = pd.DataFrame(data)
data = {
    'Name': 'David',
    'Age': 28
}
new_row = pd.Series(data)
df = df._append(new_row, ignore_index=True)
print(df)