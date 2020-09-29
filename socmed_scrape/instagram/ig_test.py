import instagram as ig
import pandas as pd
import json, csv
from datetime import datetime, timedelta


URLs = pd.read_csv('test.csv').values.tolist()

page_details = []
page_details_filename = 'ig_page_details_' + (datetime.utcnow() + timedelta(hours=8)).strftime('%Y%m%d%H%M') + '.csv'
for url in URLs:
    try:
        page_details.append(ig.get_page_details(url[0]))
        df_page_details = pd.DataFrame(page_details)
    except Exception as e:
        df_page_details = pd.DataFrame(page_details)
df_page_details.to_csv(page_details_filename, index=0)







