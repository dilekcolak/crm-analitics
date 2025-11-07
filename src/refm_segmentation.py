############################################
#Görev 1: Veriyi anlama ve hazırlama
############################################
import pandas as pd
import datetime as dt

def data_prep(dataframe):
    dataframe = dataframe.copy()

    dataframe["order_num_total"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["customer_value_total"] = dataframe["customer_value_total_ever_online"] + dataframe["customer_value_total_ever_offline"]

    dataframe["first_order_date"] = pd.to_datetime(dataframe["first_order_date"])
    dataframe["last_order_date"] = pd.to_datetime(dataframe["last_order_date"])
    dataframe["last_order_date_online"] = pd.to_datetime(dataframe["last_order_date_online"])
    dataframe["last_order_date_offline"] = pd.to_datetime(dataframe["last_order_date_offline"])

    #bilgi amaçlı inceliyoruz sadece
    dataframe.groupby("order_channel").agg({"master_id": "nunique",
                                            "order_num_total": "sum",
                                            "customer_value_total": "sum"})

    dataframe.sort_values("customer_value_total", ascending=False)[["master_id", "order_num_total"]].head(10)
    dataframe.sort_values("order_num_total", ascending=False)[["master_id", "customer_value_total"]].head(10)

    return dataframe

#####################################################
#Görev 2: RFM Metriklerinin Hesaplanması
#####################################################

def compute_rfm(df):
    today_date = dt.datetime(2021, 6, 1)

    rfm = df.groupby("master_id").agg({"last_order_date": lambda date: (today_date - date.max()).days,
                                       "order_num_total": "sum",
                                       "customer_value_total": "sum"})
    rfm.columns = ["recency", "frequency", "monetary"]

    return rfm

#####################################################
#Görev 3: RFM Skorlarının Hesaplanması
#####################################################
def score_rfm(rfm):
    rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5])

    rfm["RF_SCORE"] = (rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str))

    return rfm

#####################################################
#Görev 4: RF Skorunun Segment Olarak Tanımlanması
#####################################################
def assign_segments(rfm):
    seg_map = {
        r'[1-2][1-2]': "hibernating",
        r'[1-2][3-4]': "at_Risk",
        r'[1-2][5]': "cant_loose",
        r'[3][1-2]': "about_to_sleep",
        r'[3][3]': "need_attention",
        r'[3-4][4-5]': "loyal_customers",
        r'[4][1]': "promising",
        r'[5][1]': "new_customers",
        r'[4-5][2-3]': "potential_loyalist",
        r'[5][4-5]': "champions",
    }

    rfm["segment"] = rfm["RF_SCORE"].replace(seg_map, regex=True)
    return rfm


#####################################################
#Görev 5: Aksiyon Zamanı
#####################################################

#Champions ve loyal_customers kategorisinde olan kadın müşteriler
def action_a(df, rfm):
    seg = rfm.loc[rfm["segment"].isin(["champions", "loyal_customers"])].reset_index()[["master_id"]]

    category = df[["master_id", "interested_in_categories_12"]].drop_duplicates()

    target = (seg.merge(category, on="master_id", how="left").loc[
                  lambda x: x["interested_in_categories_12"].str.contains("KADIN", case=False, na=False), [
                      "master_id"]].drop_duplicates())

    target.to_csv("loyal_champ_woman_customers.csv", index=False)
    return target

#Erkek ve çocuk ürünlerinde yapılacak indirim ile ilgilenecek olan müşteriler
def action_b(df, rfm):
    segments = rfm.loc[rfm["segment"].isin(["cant_loose", "about_to_sleep", "at_Risk"])].reset_index()[["master_id"]]
    cats = df[["master_id", "interested_in_categories_12"]].drop_duplicates()

    male_kids_pattern = r"(ERKEK|ÇOCUK|COCUK)"

    target_b = (segments.merge(cats, on="master_id", how="left").loc[
                    lambda x: x["interested_in_categories_12"].str.contains(male_kids_pattern, case=False, na=False), [
                        "master_id"]].drop_duplicates())
    target_b.to_csv("discount_male_kids.csv", index=False)
    return target_b

def main():
    pd.set_option('display.max_columns', None)
    pd.set_option("display.float_format", lambda x: '%.3f' % x)

    df_ = pd.read_csv("Datasets/flo_data_20k.csv")
    df = df_.copy()
    df = data_prep(df)

    rfm = compute_rfm(df)
    rfm = score_rfm(rfm)
    rfm = assign_segments(rfm)

    out_a = action_a(df, rfm)
    out_b = action_b(df, rfm)

    print(f"RFM hazır:  {len(rfm):,} müşteri")
    print(f"Görev 5-a kayıt sayısı: {out_a['master_id'].nunique():,}")
    print(f"Görev 5-b kayıt sayısı: {out_b['master_id'].nunique():,}")

if __name__ == "__main__":
    main()

