"""
FLO Customer Lifetime Value Prediction
--------------------------------------
BG/NBD + Gamma-Gamma CLTV modeli

Adımlar:
1. Aykırı değer baskılama
2. Recency, T, Frequency, Monetary hesaplama
3. BG/NBD ile satın alma tahmini (3 ve 6 ay)
4. Gamma-Gamma ile ortalama harcama tahmini
5. CLTV hesaplama + segmentasyon (A-B-C-D)
"""

import pandas as pd
import datetime as dt
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.plotting import plot_period_transactions
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)
pd.set_option("display.width", 500)
pd.set_option("display.float_format", lambda x: "%.4f" %x)

df_ = pd.read_csv("Datasets/flo_data_20k.csv")
dataframe = df_.copy()

def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquartile_range = quartile3 - quartile1
    up_limit = round(quartile3 + 1.5 * interquartile_range)
    low_limit = round(quartile1 - 1.5 * interquartile_range)
    return low_limit, up_limit

def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit

def create_cltv_prediction(dataframe, month=6, show_plot=False, export_csv=False):
    df = dataframe.copy()
    # Aykırı değerlerden kurtulalım
    replace_with_thresholds(df, "order_num_total_ever_online")
    replace_with_thresholds(df, "order_num_total_ever_offline")
    replace_with_thresholds(df, "customer_value_total_ever_online")
    replace_with_thresholds(df, "customer_value_total_ever_offline")

    # müşteri bazlı işlem sayısını ve parasal getiriyi hesaplayalım
    df["order_num_total"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
    df["customer_value"] = df["customer_value_total_ever_online"] + df["customer_value_total_ever_offline"]

    # tarih içeren sütunların veri tipini date yapalım
    df[[col for col in df.columns if col.__contains__("date")]] = df[
        [col for col in df.columns if col.__contains__("date")]].apply(pd.to_datetime)

    #son siparişten iki gün sonrasını analiz tarihi olarak belirleyelim. İstersek direkt tarih de seçebiliriz.
    today_date = df["last_order_date"].max() + pd.Timedelta(days=2)

    # CLTV metriklerini oluşturalım/düzenleyelim
    cltv_df = pd.DataFrame()
    cltv_df["customer_id"] = df["master_id"]
    cltv_df["recency_cltv_weekly"] = (df["last_order_date"] - df["first_order_date"]).dt.days / 7  # haftalık
    cltv_df["T_weekly"] = (today_date - df["first_order_date"]).dt.days / 7  # haftalık
    cltv_df["frequency"] = df["order_num_total"]
    cltv_df = cltv_df[(cltv_df["frequency"] > 1)]
    cltv_df["monetary_cltv_avg"] = (
            df.loc[cltv_df.index, "customer_value"] /
            df.loc[cltv_df.index, "order_num_total"]
    )

    cltv_df = cltv_df.set_index("customer_id")

    # BG-NBD modelini fit edelim
    bgf = BetaGeoFitter(penalizer_coef=0.001)
    bgf.fit(cltv_df["frequency"],
            cltv_df["recency_cltv_weekly"],
            cltv_df["T_weekly"])

    # 3 için müşterilerin beklenen satın alımlarını tahmin edelim
    cltv_df["exp_sales_3_months"] = bgf.predict(12,
                                                cltv_df["frequency"],
                                                cltv_df["recency_cltv_weekly"],
                                                cltv_df["T_weekly"])

    # 6 için müşterilerin beklenen satın alımlarını tahmin edelim
    cltv_df["exp_sales_6_months"] = bgf.predict(24,
                                                cltv_df["frequency"],
                                                cltv_df["recency_cltv_weekly"],
                                                cltv_df["T_weekly"])
    # Tahmin sonuçlarını gözlemleyelim
    if show_plot:
        plot_period_transactions(bgf)
        plt.show()

    # Gamma-Gamma modelini fit edelim
    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(cltv_df["frequency"],
            cltv_df["monetary_cltv_avg"])

    # müşterilerin ortalama bırakacakları değeri tahmin edelim
    cltv_df["exp_average_value"] = ggf.conditional_expected_average_profit(cltv_df["frequency"],
                                                                           cltv_df["monetary_cltv_avg"])
    #month parametresine göre (default 6 aylık) cltv hesaplayalım
    cltv = ggf.customer_lifetime_value(bgf,
                                       cltv_df["frequency"],
                                       cltv_df["recency_cltv_weekly"],
                                       cltv_df["T_weekly"],
                                       cltv_df["monetary_cltv_avg"],
                                       time=month,  # ay
                                       freq="W",  # T'nin frekans bilgisi (week)
                                       discount_rate=0.01)

    # Her iki dataframe için de customer_id sütunlarını indexten ayıralım
    cltv = cltv.reset_index()
    cltv_df = cltv_df.reset_index()

    # Dataframe'leri birleştirelim
    cltv_final = cltv_df.merge(cltv, on="customer_id", how="left")

    # clv değerlerine göre müşterileri segmentlere bölelim. Potansiyeli en yüksek olan A grubudur.
    cltv_final["segment"] = pd.qcut(cltv_final["clv"], 4, labels=["D", "C", "B", "A"])

    if export_csv:
        cltv_final.to_csv(f"cltv_output_{month}m.csv", index=False)
    return cltv_final


if __name__ == "__main__":
    last_df = create_cltv_prediction(dataframe, export_csv=True)
    print(last_df.head())
    print("\nCLTV hesaplama tamamlandı.")


