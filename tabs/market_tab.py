import streamlit as st
from db import list_item, get_market, buy_market_item

def render(username, followers, items):
    st.subheader("💱 Market")
    if items:
        sell_item = st.selectbox("Item to sell", items)
        price = st.number_input("Price (followers)",1,1000,50)
        if st.button("List for Sale"):
            list_item(username,sell_item,price)
            st.success(f"Listed {sell_item} for {price} followers.")

    st.divider()
    st.write("Active Listings:")
    for mid,seller,item,price,status,buyer in get_market():
        if seller!=username:
            if st.button(f"Buy {item} from {seller} ({price} followers)", key=f"buy{mid}"):
                if followers>=price:
                    followers-=price; items.append(item)
                    buy_market_item(mid,username)
                    st.success(f"Bought {item} for {price} followers!")
                else:
                    st.warning("Not enough followers!")

    return followers, items
