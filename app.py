import streamlit as st
import yfinance as yf
import pandas as pd

# অ্যাপের টাইটেল বা নাম
st.title("📈 AI Trading Signal Tracker")
st.write("এটি একটি অটোমেটেড টেকনিক্যাল অ্যানালিসিস অ্যাপ।")

# ইউজার কোন কয়েন দেখতে চায় তার ইনপুট
ticker = st.text_input("কয়েন বা স্টকের নাম লিখুন (যেমন: BTC-USD, ETH-USD, AAPL):", "BTC-USD")

if st.button("সিগন্যাল চেক করুন"):
    with st.spinner('ডেটা বিশ্লেষণ করা হচ্ছে...'):
        # ডেটা ডাউনলোড
        data = yf.download(ticker, period="100d", interval="1d")
        
        if not data.empty:
            # MultiIndex কলাম থাকলে তা একক কলামে রূপান্তর করা হচ্ছে
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            # ইন্ডিকেটর হিসাব
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            data['SMA_50'] = data['Close'].rolling(window=50).mean()
            
            # ডেটা থেকে সিঙ্গেল ভ্যালু নেওয়া নিশ্চিত করা হচ্ছে
            latest_sma20 = float(data['SMA_20'].dropna().iloc[-1])
            latest_sma50 = float(data['SMA_50'].dropna().iloc[-1])
            current_price = float(data['Close'].dropna().iloc[-1])
            
            # স্ক্রিনে দেখানো
            st.metric(label=f"বর্তমান মূল্য ({ticker})", value=f"${current_price:,.2f}")
            st.write(f"সর্বশেষ ২০ দিনের গড় দাম: ${latest_sma20:,.2f}")
            st.write(f"সর্বশেষ ৫০ দিনের গড় দাম: ${latest_sma50:,.2f}")
            
            st.markdown("---")
            # সিগন্যাল লজিক
            if latest_sma20 > latest_sma50:
                st.success("🟢 সিগন্যাল: BULLISH (বাজার উপরে যাওয়ার সম্ভাবনা আছে - BUY Signal)")
            else:
                st.error("🔴 সিগন্যাল: BEARISH (বাজার নিচে নামার সম্ভাবনা আছে - SELL Signal)")
                
            # চার্ট দেখানো
            st.subheader("মূল্যের চার্ট (সর্বশেষ ১০০ দিন)")
            chart_data = data[['Close', 'SMA_20', 'SMA_50']].dropna()
            st.line_chart(chart_data)
        else:
            st.error("সঠিক নাম লিখুন। ডেটা পাওয়া যায়নি।")
