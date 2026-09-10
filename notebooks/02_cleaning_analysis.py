"""NEXORAS — Pre-Cleaning Analysis Script"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\sih 2026\sample mvp\NEXORAS-sample-mvp")
from backend.ingestion.loader import load_all

data = load_all()

print("\n" + "=" * 70)
print("CLEANING ANALYSIS")
print("=" * 70)

# 1. MP Summary
ms = data["mp_summary"]
print("\n--- mp_summary: Financial Sanity ---")
neg_alloc = (ms["allocated_amount"] < 0).sum()
zero_alloc = (ms["allocated_amount"] == 0).sum()
neg_exp = (ms["total_expenditure"] < 0).sum()
over_alloc = (ms["total_expenditure"] > ms["allocated_amount"]).sum()
util_over = (ms["utilization_pct"] > 100).sum()
comp_over = (ms["completion_rate_pct"] > 100).sum()
print(f"  Negative allocated_amount: {neg_alloc}")
print(f"  Zero allocated_amount: {zero_alloc}")
print(f"  Negative total_expenditure: {neg_exp}")
print(f"  Expenditure > Allocated: {over_alloc}")
print(f"  Utilization > 100%: {util_over}")
print(f"  Completion rate > 100%: {comp_over}")
print(f"  Unique states: {ms['state'].nunique()}")
print(f"  Unique houses: {ms['house'].unique().tolist()}")

# 2. Expenditures
exp = data["expenditures"]
print("\n--- expenditures: Cleaning Needs ---")
print(f"  Total rows: {len(exp)}")
dup_count = exp.duplicated().sum()
print(f"  Duplicate rows: {dup_count}")
print(f"  After dedup: {exp.drop_duplicates().shape[0]}")
neg_amt = (exp["expenditure_amount"] < 0).sum()
zero_amt = (exp["expenditure_amount"] == 0).sum()
print(f"  Negative expenditure_amount: {neg_amt}")
print(f"  Zero expenditure_amount: {zero_amt}")
print(f"  Unique vendors: {exp['vendor'].nunique()}")
print(f"  Unique MPs: {exp['mp_name'].nunique()}")
print(f"  Payment statuses: {exp['payment_status'].value_counts().to_dict()}")
null_vendor = exp["vendor"].isnull().sum()
print(f"  Null vendor: {null_vendor}")

# 3. Completed works
cw = data["completed_works"]
print("\n--- completed_works: Cleaning Needs ---")
neg_final = (cw["final_amount"] < 0).sum()
zero_final = (cw["final_amount"] == 0).sum()
print(f"  Negative final_amount: {neg_final}")
print(f"  Zero final_amount: {zero_final}")
print(f"  Null work_description: {cw['work_description'].isnull().sum()}")
print(f"  Unique categories: {cw['category'].unique().tolist()}")
print(f"  Date range: {cw['completed_date'].min()} to {cw['completed_date'].max()}")

# 4. Recommended works
rw = data["recommended_works"]
print("\n--- recommended_works: Cleaning Needs ---")
neg_rec = (rw["recommended_amount"] < 0).sum()
zero_rec = (rw["recommended_amount"] == 0).sum()
print(f"  Negative recommended_amount: {neg_rec}")
print(f"  Zero recommended_amount: {zero_rec}")
print(f"  Null work_description: {rw['work_description'].isnull().sum()}")
print(f"  Unique categories: {rw['category'].unique().tolist()}")
print(f"  Date range: {rw['recommendation_date'].min()} to {rw['recommendation_date'].max()}")
