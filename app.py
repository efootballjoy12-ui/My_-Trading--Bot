import streamlit as st
import yfinance as yf
import pandas as pd
import time

# অ্যাপের টাইটেল ও ইন্টারফেস
st.set_page_config(page_title="Quotex Real-Time Signal Bot", layout="wide")
st.title("🎯 Quotex Real-Time Signal Bot (1-Min Actual Time)")
st.write("এটি ১ মিনিটের লাইভ ডেটা বিশ্লেষণ করে তাৎক্ষণিক UP/DOWN সিগন্যাল তৈরি করে।")

# কারেন্সি পেয়ার ইনপুট (Quotex এ সাধারণত এগুলো থাকে)
ticker = st.selectbox(
    "ট্রেডিং পেয়ার সিলেক্ট করুন:",
    ["BTC-USD", "ETH-USD", "EURUSD=X", "GBPUSD=X", "JPY=X"]
)

# প্রতি ১০ সেকেন্ড পর পর অ্যাপটি নিজে নিজেই লাইভ ডেটা রিফ্রেশ করবে
if st.button("লাইভ সিগন্যাল ট্র্যাক করা শুরু করুন"):
    status_placeholder = st.empty()
    metrics_placeholder = st.empty()
    signal_placeholder = st.empty()
    chart_placeholder = st.empty()
    
    while True:
        status_placeholder.write("🔄 লাইভ মার্কেট ডেটা স্ক্যান করা হচ্ছে...")
        
        # ১ মিনিটের ইন্টারভ্যালে গত ১ দিনের ডেটা নেওয়া হচ্ছে
        data = yf.download(ticker, period="1d", interval="1m")
        
        if not data.empty:
            # MultiIndex কলাম ফিক্স
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            # Quotex এর জন্য কার্যকরী ইন্ডিকেটর (RSI) হিসাব
            # RSI ১৪ পিরিয়ড শর্ট-টার্ম ট্রেন্ড বুঝতে সাহায্য করে
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['RSI'] = 100 - (100 / (1 + rs))
            
            # সাম্প্রতিক দাম ও RSI ভ্যালু
            current_price = float(data['Close'].dropna().iloc[-1])
            latest_rsi = float(data['RSI'].dropna().iloc[-1])
            
            # স্ক্রিনে লাইভ প্রাইস আপডেট
            with metrics_placeholder.container():
                col1, col2 = st.columns(2)
                col1.metric(label=f"🔴 লাইভ মূল্য ({ticker})", value=f"${current_price:,.4f}")
                col2.metric(label="📊 বর্তমান RSI (14)", value=f"{latest_rsi:.2f}")
            
            # 🎯 ১ মিনিটের এক্সচুয়াল টাইম সিgনাল লজিক (UP / DOWN)
            with signal_placeholder.container():
                if latest_rsi < 35:
                    st.success(f"🚀 [ACTUAL TIME SIGNAL]: 🟢 UP (Call Trade Now) - মার্কেট Oversold জোন থেকে উপরে উঠছে!")
                elif latest_rsi > 65:
                    st.error(f"📉 [ACTUAL TIME SIGNAL]: 🔴 DOWN (Put Trade Now) - মার্কেট Overbought জোন থেকে নিচে নামছে!")
                else:
                    st.warning("⏳ [MARKET STATUS]: WAIT - বাজার এখন নিউট্রাল জোনে আছে, সঠিক সুযোগের অপেক্ষা করুন।")
            
            # লাইভ চার্ট আপডেট
            with chart_placeholder.container():
                st.subheader("১ মিনিটের ক্যান্ডেল ক্লোজ ট্রেন্ড চার্ট")
                st.line_chart(data['Close'].tail(30)) # সর্বশেষ ৩০ মিনিটের মুভমেন্ট
                
        else:
            status_placeholder.error("ডেটা লোড করা যায়নি। কিছুক্ষণ পর চেষ্টা করুন।")
            
        time.sleep(10) # প্রতি ১০ সেকেন্ড পর পর লুপটি অটো রিফ্রেশ হবে
