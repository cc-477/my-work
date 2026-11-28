import pandas as pd

p = r"data\henan_dirty.csv"
df = pd.read_csv(p, header=2)

print(df.shape)
print(df.head())
print(df.dtypes)
print(df[df.duplicated(keep=False)])
df = df.drop_duplicates()
print(df.shape)
df["GDP"] = df["GDP"].str.replace(",", "").astype(float)
df["增速(%)"] = pd.to_numeric(df["增速(%)"], errors="coerce")
print(df.dtypes)
print(df.isna().sum())
print(df[df["增速(%)"].isna()])
print(df["GDP"].mean())
print(df.sort_values("增速(%)", ascending=False).head(3))
df.to_csv(r"data\henan_clean.csv", index=False, encoding="utf-8-sig")
