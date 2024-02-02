import streamlit as st
from PIL import Image
import pandas as pd, numpy as np, yfinance as yf, pandas_ta as ta
import plotly.express as px
import base64
import matplotlib.pyplot as plt

# ---------------------------------#
# Page layout
# Page expands to full width
# st.beta_set_page_config(layout="wide")
# ---------------------------------#
# Title


def app():
    st.cache_resource
    st.cache_data
    ticker = st.sidebar.text_input("Ticker")
    start_date = st.sidebar.date_input("Start Date")
    end_date = st.sidebar.date_input("End Date")

    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        print("data->", data)
        fig = px.line(data, x=data.index, y=data["Adj Close"], title=ticker)
        st.plotly_chart(fig)

        pricing_data, fundamental_data, news, openai1, tech_indicator = st.tabs(
            [
                "Pricing Data",
                "Fundamental Data",
                "Top 10 News",
                "OpenAI ChatGPT",
                "Technical Analysis Dashboard",
            ]
        )

        with pricing_data:
            st.header("Price Movements")
            data2 = data
            data2["% Change"] = data["Adj Close"] / data["Adj Close"].shift(1) - 1
            data2.dropna(inplace=True)
            st.write(data2)
            annual_return = data["% Change"].mean() * 252 * 100
            st.write("Annual Return is ", annual_return, "%")
            st_dev = np.std(data2["% Change"]) * np.sqrt(252)
            st.write("Standard Deviation is ", st_dev * 100, "%")
            st.write("Risk Adj. Return is ", annual_return / (st_dev * 100))

        from alpha_vantage.fundamentaldata import FundamentalData

        with fundamental_data:
            API_key = open("API_KEY.txt").read()
            API_key = "CUJGLLJZGW2A77LA"
            fd = FundamentalData(key=API_key, output_format="pandas")
            st.subheader("Balance Sheet")
            balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
            bs = balance_sheet.T[2:]
            bs.columns = list(balance_sheet.T.iloc[0])
            st.write(bs)
            st.subheader("Income Statement")
            income_statement = fd.get_income_statement_annual(ticker)[0]
            is1 = income_statement.T[2:]
            is1.columns = list(income_statement.T.iloc[0])
            st.write(is1)
            st.subheader("Cash Flow Statement")
            cash_flow = fd.get_cash_flow_annual(ticker)[0]
            cf = cash_flow.T[2:]
            cf.columns = list(cash_flow.T.iloc[0])
            st.write(cf)

        from stocknews import StockNews

        with news:
            st.header(f"News of {ticker}")
            sn = StockNews(ticker, save_news=False)
            df_news = sn.read_rss()
            for i in range(10):
                st.subheader(f"News {i + 1}")
                st.write(df_news["published"][i])
                st.write(df_news["title"][i])
                st.write(df_news["summary"][i])
                title_sentiment = df_news["sentiment_title"][i]
                st.write(f"Title Sentiment {title_sentiment}")
                news_sentiment = df_news["sentiment_summary"][i]
                st.write(f"News Sentiment {news_sentiment}")

        # from pyChatGPT import ChatGPT
        # session_token = "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..MvuIIpZwG5-wRwJh.TR99Wj1SF6Ghpg2vCat43NXNylwEi6P1fyek8co_myu6zhvNONhqSKajk802tIii6XAe03fOxNabsWlpGVggqu9mfTaeriek_0Zfi4dR-v6UqCYhcEP8fD8KmGMPcvRQuoF9DuKuAbYfGY8wFRZZAPNb-7uQs8StbSuCWHYDzU2wrGtddOwIOXNIYoZ1xc26fGkxf8sQONrGJLiMx6_tei3NyU_V5mx8iDNvuCA27BQtyYSQMSHQKSsixsHGD54tWGEc31W7m77pqlw2hSGW5C-enObB4-JwwGyjjcaa-_k0x0fQ75EdDdlfSyo1aNl9JxwkF6PzeqNHvGRjx-i5TC4S9hjD9WsStZHlfWXTOti85q_dyRRUSrb1aORuyZyF89-8hVWdU6_-Hy9RMldo501qJ0Hq-H-DTHllXRLptJ2PVusOkKYEFaOSUONMUhEt2NmWEUwB6bKWl2odQ7dulrIrOEC45THwazuQyfwASYyxe9kZYRfcIyuVhX5uNG_Fxul0hlTHinoP8p0E_PBao_oMTQqJUeKGsqQvKDdxnK5WENu55YRnhXkuri6DQZ9Xql7A5p0wFU-v3mdTJXrpCWUFbezsD2zkrTesm5fxRvhWydn8MhIDMCcQ4D8zOgNoWbd_MEdQofZ-QRSG1PqsVSexmh5HkzDmDgzjg1rNxst4_G9JvlUWa74OPh85I8Me54xs1KLJ0U8PDHNKPJUgiUDAqDaPFD5_uSdBSk2Ahn0LM5tQB7fyyxE82laxOsVJYYYpVZ9tPDu3RppVbooaYnpeiwLMX6fKoLbqidL4sQLRild4N3LO0CXp94RNKHHUfMDsHiyGN5yJld7fWuTkEmOEO_MtYq434S6t0eX5ZlY-A_sJALnjRdStvI8Buk5yOt1Bnu6Cyt9YAaRn8PQ4jiRoO_7KGuyw125jp_iGJcwnQUCnNhIbOhUnDIKljHmHvMVtksi1BT9wRY0DevZRb9nt8uKZbiiKGdQdZ-noxZaxOtSh7O8PopCrFMuLUT8C_3B8xqukYuv1XneMClVLLPpi-WU40XwNzmCVO5xey4PS3TdbjgfRP4_YFwmCOnBfePybtGfQyr2SIdys2nzYeJ5nkK60HzD223v8GVOtFvnTiQP8RF2GicWBbe2JYx2xHciacXi6i3YZ0RzzFirSRMwwZ20ltnRXurblRAnQKpIhLfgPhuR4BQbWInMCdGt93o2DDGvt7MJLCB0--s-Vik17JTNZ4AHW2AarGoW88XZpJU5EhM0L4ZoCpzi0Hj-YLi0etiH_rlm4Fj-J1I0h7sgMYnmTuMaP5YdXOTLskFwBUWsu572fEZM9Q0Z6T7v_UpdMM08Iy7gcTK_chfBeqP07deVFWQiwkyQnXzuSzTzw4ymRwDmkyB0d1ZtJzA0BSEHEGvpsW4QCWpCwLeHJM0V7fDIFoPdrqVuTA68O-egqPRCutMSzI8QzY6UxvSXDl8e1ZbeQqnKAur4o6bEE1ZHjl5zFlXF1T1Q5OSq7eJIKjj8_8AQebcRQEFR_VVFUq-7pgzQ36DbsV8lY3vI26WdDgf2lVs0oi7mGgdz_u993v6YdcAAxpLU34W8L0BVNcEKVjmLUWJ-MqW9d9fPQcPR53_Qs_9acw6oHsnRrYo8YmRKD_jdq-47TYOtuTg2ljuAd7H2W2BNORNG9lE9sB3bvWjAl0MqgfgloJUZ38KUgtH2adxMP5ExgOZenIVlDip-YthS5sRNAdEpZNaPpjwIEtEra7UGZGM4dy0AQerSnNi9TwNv_uA_2VFxjucMWQIvRqJEZxK5GEQUlwUVlu3WXDSkHxrHwcAwntgZ5WzDhay1Y5iTAY3WlWBEkoke-4piefpfV7HeepGIPfkOb14N3O488SnBY1ZmkfHroKT7QIVrZmBpVYXin63MFBTnfMYr2u65ld7Gt3CvusQKD2qI7HfB1i7YR__zXXgOkFBL8qZOIpncNWrsdZCID44YooqnRXbBh42wG4QBzYgTx5LnLGrT_U-lM0o-eGUuCWwZ-sxM2sfquZzW1aSksJPICeqSpfqyB8QWbUAbWFl3eRIu5CDFgavEULZ-r-Q1_UZ_2iymUHk3QPw7UrKJmRaQnrvR4Ms0P-AlbPUwRvnq9BJtInxy1Z_zr7bWyr-oDbxhWbCU84FQ_o0zA39qPTnj0A-paI5hMQMWXTkFL77QwWt7PTZXxkKKIQO98MBR0UeaRqO3FGynySJ6YyYAMPKqaa3naxETRXIazzdSheI_8pXPtg8n2NIF1h1vc5g48q8SkHbec_ex4stwMwDdv1yeVe6JPqCkQMinNE7_XWkGRtaoQM8GYidRDx0Cah0Xj8xGyyQvdZAPTwS6JmC_pjBOM1fAIywDQM2gYAlnwLy6Yw7kHd9ToiBrjGH-xueI7PWcYMFduNa2-3ziP-7tRae1tMSovggI0GPl3m5oF98neZcX-p0SPIJbBMwGdDjijZHqm6NPTGxsMGby7MmG3chyHdbIanRtasPCaBqJi-_fjPTVLNnOj2lZkJlR8ZdyR9Tf0BOxp2nNts9d2uvyNZMy7R2JkUPV-Of2jG9MeqaRhVlBXAsDUth87w8KV_P1pCLqC7gn7hOlgSN-aRCYuoTk139tPRAsC1Q5-T-ZpCfl1Y091g4NZ02i53LmU9hahLNdYeDzw2W-ejlvcKyn-yencLVG6Yzjd-SWsXgCl-1mn6FdcGkT7qwM5iJqtPJC-7kqS7zXnwqGeQMVGNSSpynWVDKfTfAzk_i_JPdI2abc_JbhW4su-7sw2IH3Gmo-jcnUVtYJnznQVXf_lrLx67kCMnEDUYfOzhyrtTA-SkEwL-UA6.dE2R70Cp7QC0yqdWG2FMLw"
        # api2 = ChatGPT(session_token)
        # buy = api2.send_message(f"Summarize the 3 Reasons to buy {ticker} stock")
        # sell = api2.send_message(f"Summarize the 3 Reasons to sell {ticker} stock")
        # swot = api2.send_message(f"Summarize the SWOT analysis of {ticker} stock")

        with openai1:
            st.write("Open AI")
            # buy_reason, sell_reason, swot_analysis = st.tabs(["3 Reasons to buy", "3 Reasons to sell", "SWOT analysis"])

            # with buy_reason:
            #     st.subheader(f"3 reasons on why to buy {ticker} stock")
            #     st.write(buy["message"])
            # with sell_reason:
            #     st.subheader(f"3 reasons on why to sell {ticker} stock")
            #     st.write(sell["message"])
            # with swot_analysis:
            #     st.subheader(f"SWOT analysis of {ticker} stock")
            #     st.write(swot["message"])

        with tech_indicator:
            st.subheader("Technical Analysis Dashboard:")
            df = pd.DataFrame()
            ind_list = df.ta.indicators(as_list=True)
            st.write(ind_list)
            technical_indicator = st.selectbox("Tech Indicator", options=ind_list)
            method = technical_indicator
            indicator = pd.DataFrame(
                getattr(ta, method)(
                    low=data["Low"],
                    close=data["Close"],
                    high=data["High"],
                    open=data["Open"],
                    volume=data["Volume"],
                )
            )
            indicator["Close"] = data["Close"]
            st.write(indicator)
            fig_ind_new = px.line(indicator)
            st.plotly_chart(fig_ind_new)
            st.write(indicator)
    except (ValueError, NameError):
        print(
            st.markdown(
                """
                        ### Please choose your ticker, your start date and your end date!!!
                        """
            )
        )
