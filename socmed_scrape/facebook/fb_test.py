import facebook as fb
import pandas as pd
import json, csv
from datetime import datetime, timedelta


def main(urllist_filename='test.csv', urllist={}):

    if not urllist:
        URLs = pd.read_csv(urllist_filename).values.tolist()

    try:
        #test.login()

        # page_details = []
        # page_details_filename = 'page_details_' + (datetime.utcnow() + timedelta(hours=8)).strftime('%Y%m%d%H%M') + '.csv'
        # for url in URLs:
        #     page_details.append(fb.get_page_details(url[0]))
        # df_page_details = pd.DataFrame(page_details)
        # df_page_details.to_csv(page_details_filename, index=0)

        post_details= []
        post_details_filename = 'post_details_' + (datetime.utcnow() + timedelta(hours=8)).strftime('%Y%m%d%H%M') + '.csv'
        df_post_details = pd.DataFrame()
        for url in URLs:
            post_details = (fb.get_latest_posts(url[0],10))
            if df_post_details.empty:
                df_post_details = pd.DataFrame(post_details)
            else:
                df_post_details = df_post_details.append(pd.DataFrame(post_details))
        df_post_details.to_csv(post_details_filename, index=0)
        

    except Exception as e:
        print(e)
   

    

    return "completed"
    

if __name__ == "__main__":
    main()