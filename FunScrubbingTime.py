import pandas as pd
import re
import numpy as np

# I: Import Data
# US MERGER DATA
us_data_path = "C:/Users/kevin/OneDrive/Desktop/RISK ARBITRAGE/SDC/US_Merger_Data_"
us_data_years = [1979, 1989, 1994, 1999, 2004, 2009, 2019]

US_MERGER_DATA = pd.read_csv(us_data_path + f"{us_data_years[0]}_{us_data_years[1]}.csv")
for i in range(1, len(us_data_years)-1):
    US_MERGER_DATA = pd.concat(
        [
            US_MERGER_DATA,
            pd.read_csv(us_data_path + f"{us_data_years[i]}_{us_data_years[i+1]}.csv")
        ]
        , ignore_index=True
    )
US_MERGER_DATA.columns = [name.replace("\n", " ") for name in US_MERGER_DATA.columns]

# INTERNATIONAL MERGER DATA
intl_data_path = "C:/Users/kevin/OneDrive/Desktop/RISK ARBITRAGE/SDC/Intl_Merger_Data_"
intl_data_years = []

# INTL_MERGER_DATA = pd.read_csv(intl_data_path + f"{intl_data_years[0]}_{intl_data_years[1]}.csv")
# for i in range(1, len(intl_data_years)-1):
#     INTL_MERGER_DATA = pd.concat(
#         [
#             INTL_MERGER_DATA,
#             pd.read_csv(intl_data_path + f"{intl_data_years[i]}_{intl_data_years[i+1]}.csv")
#         ]
#         , ignore_index=True
#     )
# INTL_MERGER_DATA.columns = [name.replace("\n", " ") for name in INTL_MERGER_DATA.columns]


# II: Data Scrubbing
# -> Remove "unnecessary" columns
US_MERGER_DATA = US_MERGER_DATA.drop(
    ["  Date Withdrawn", "  Date Effective", "Date Effective/ Unconditional", "Target Company  Date   of  Fin.",
     "History File Event", "Target Name", "Acquiror Name"], axis=1
)

# -> Drop points with missing labels
US_MERGER_DATA = US_MERGER_DATA.drop(US_MERGER_DATA[US_MERGER_DATA['Status'].isnull()].index.tolist())

# -> Explore labels
status = set()
for i in US_MERGER_DATA.index:
    status.add(US_MERGER_DATA.at[i, "Status"])
print(status)
#  {'Withdrawn', 'S Buyer', 'Part Comp', 'Status Unknown', 'Pending Reg.', 'Intent W', 'Intended', 'Pending', 'Completed', 'S Target'}
# Success: Completed, Part Comp,
# Failed: Withdrawn,
# Not Useful: Pending, Pending Reg. Status Unknown, Intended, S Buyer, S Target, Intent W
print("---- Label Counts ----")
print("Withdrawl", (US_MERGER_DATA["Status"] == "Withdrawn").sum())
print("Part Comp", (US_MERGER_DATA.Status == "Part Comp").sum())
print("Completed", (US_MERGER_DATA.Status == "Completed").sum())
# ---- Label Counts ----
# Withdrawl 7699
# Part Comp 3
# Completed 114263


# -> Drop points with "un-useful" labels:
status.remove("Withdrawn")
status.remove("Part Comp")
status.remove("Completed")
remove_indices = []
for stat in status:
    remove_indices.extend(US_MERGER_DATA.index[US_MERGER_DATA['Status'] == stat].tolist())
US_MERGER_DATA = US_MERGER_DATA.drop(remove_indices)


# -> 1-hot encoding for categorical variables
categorical_cols = ["Target Industry Sector", "Acquiror Industry Sector", "Target Nation", "Acquiror  Nation"]
new = pd.get_dummies(US_MERGER_DATA[categorical_cols], drop_first=False)
for new_col in new.columns:
    US_MERGER_DATA[new_col] = new[new_col]
US_MERGER_DATA = US_MERGER_DATA.drop(columns=categorical_cols)
del new


# -> Convert data types for each column as appropriate
US_MERGER_DATA[" Rank Date"] = pd.to_datetime(US_MERGER_DATA[" Rank Date"])
US_MERGER_DATA["  Date Announced"] = pd.to_datetime(US_MERGER_DATA["  Date Announced"])
colnames_dtype_map = {
    "Status": "category",
    "Value of Transaction ($mil)": "float64",
    "Ranking Value inc. Net Debt of Target ($Mil)": "float64",
    "Enterprise   Value   ($mil)": "float64",
    "  Equity Value      ($mil)": "float64",
    "Price  Per Share": "float64",
    'Target  Net Sales  LTM ($mil)': "float64",
    'EBIT Last Twelve Months ($ Mil)': "float64",
    'Pre-tax Income Last Twelve Months ($ Mil)': "float64",
    'Net Income Last Twelve Months ($ Mil)': "float64",
    'Target  Net Assets ($mil)': "float64",
    'Target Total Assets ($mil)': "float64",
    'Target  EBITDA  LTM ($mil)': "float64",
    'Target Book Value Per Share LTM (US$)': "float64",
    'Target Common Equity ($mil)': "float64",
    'Ratio of Offer Price to EPS': "float64"
}
for col, dtype in colnames_dtype_map.items():
    # replace all commas in numbers and 'np' and 'nm' values to null
    if dtype == "float64":
        for i in US_MERGER_DATA.index:
            if type(US_MERGER_DATA.at[i, col]) is float:
                pass
            elif type(US_MERGER_DATA.at[i, col]) is str:
                if re.search('^[\D]*$', US_MERGER_DATA.at[i, col]):
                    US_MERGER_DATA.at[i, col] = np.nan
                else:
                    US_MERGER_DATA.at[i, col] = US_MERGER_DATA.at[i, col].replace(",", "")
    US_MERGER_DATA[col] = US_MERGER_DATA[col].astype(dtype)

# -> Rename columns to make them more legible
US_MERGER_DATA.rename(columns={
    ' Rank Date': 'Rank Date',
    '  Date Announced': 'Announced Date',
    ' % of Shares Acq.': '% of Shares Acquired',
    '  % Owned After Trans- action': '% Owned After Transaction',
    '  % sought': '% Sought',
    'Value of Transaction ($mil)': 'Transaction Value',
    'Ranking Value inc. Net Debt of Target ($Mil)': 'Target Net Debt',
    'Enterprise   Value   ($mil)': 'Target Enterprise Value',
    '  Equity Value      ($mil)': 'Target Equity Value',
    'Target  Net Sales  LTM ($mil)': 'Target  Net Sales (YTD)',
    'EBIT Last Twelve Months ($ Mil)': 'Target EBIT (YTD)',
    'Pre-tax Income Last Twelve Months ($ Mil)': 'Target Pre-Tax Income (YTD)',
    'Net Income Last Twelve Months ($ Mil)': 'Target Net Income (YTD)',
    'Target  Net Assets ($mil)': 'Target Net Asset',
    'Target Total Assets ($mil)': 'Target Total Asset',
    'Target  EBITDA  LTM ($mil)': 'Target EBITDA (YTD)',
    'Target Book Value Per Share LTM (US$)': 'Target Book Value/Share (YTD)',
    'Target Common Equity ($mil)': 'Target Common Equity',
    'Target Earnings Per Share LTM (US$)': 'Target EPS (YTD)',
    'Ratio of Offer Price to EPS': 'Offer Price / EPS',
    'Target Total  Fees ($mil)': 'Target Total Adviser Fee',
    'Acquiror  Total   Fees  ($mil)': 'Acquiror Total Advisor Fee',
    'Target Share Price 1 Day Prior to Announcement ($)': 'Target Share Price 1 Day Prior To Announcement',
    'Target Share Price 1 Week Prior to Announcement ($)': 'Target Share Price 1 Week Prior To Announcement',
    'Target Share Price 4 Weeks Prior to Announcement ($)': 'Target Share Price 4 Weeks Prior To Announcement',
    ' Premium   1 day prior to announce-   ment   date': 'Premium 1 Day Prior To Announcement',
    ' Premium  1 week prior to announce-   ment   date': 'Premium 1 Week Prior To Announcement',
    ' Premium  4 weeks prior to ann. date': 'Premium 4 Weeks Prior To Announcement'
},  inplace=True)

print("---- Column Names and types ----")
colnames = US_MERGER_DATA.columns
for col in colnames:
    print("'" + col+"'", US_MERGER_DATA[col].dtypes)


print("---- Shape ----")
print(US_MERGER_DATA.shape)
print("---- Null Count ----")
print(US_MERGER_DATA.isnull().sum())

