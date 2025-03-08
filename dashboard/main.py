import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mticker
import streamlit as st
sns.set(style='dark')


def create_count_users(df):
    # Create a new column 'count_users' in the dataframe
    total_registered = df["registered"].sum()
    total_casual = df["casual"].sum()

    return {
        "total_registered": total_registered,
        "total_casual": total_casual,
        "counts_user": total_registered + total_casual
    }


def create_season_patern(df):
    season_patern = df.groupby(
        "season")[["registered", "casual"]].sum().reset_index()
    return season_patern


def create_weather_pattern(df):
    weather_pattern = df.groupby("weathersit")[
        ["registered", "casual"]].sum().reset_index()
    return weather_pattern

def create_year(df):
    thn = df.groupby("yr")["cnt"].sum().reset_index()
    return thn

def create_month_pattern(df):
    df["mnth"] = pd.Categorical(df["mnth"], categories=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], ordered=True)
    monthly_trend = df.groupby(["yr", "mnth"])["cnt"].sum().reset_index()
    return monthly_trend


def create_weekday_pattern(df):
    weekday_pattern = df.groupby("weekday")[["cnt"]].sum().reindex(
        ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])
    return weekday_pattern


def create_workingday_pattern(df):
    workingday_pattern = df.groupby("workingday")[["cnt"]].sum()
    return workingday_pattern


def create_rfm_df(df):
    df["dteday"] = pd.to_datetime(df["dteday"])
    latest_date = df["dteday"].max()

    rfm_df = df.groupby(pd.Grouper(key="dteday", freq="M")).agg(
        Recency=("dteday", lambda x: (latest_date - x.max()).days),
        Frequency=("dteday", "count"),
        Monetary=("cnt", "sum")
    ).reset_index()

    rfm_df['month'] = rfm_df['dteday'].dt.to_period('M')
    monthly_rfm = rfm_df.groupby('month').agg(
        Recency=('Recency', 'mean'),
        Frequency=('Frequency', 'sum'),
        Monetary=('Monetary', 'sum')
    ).reset_index()

    monthly_frequency = rfm_df.groupby(rfm_df['dteday'].dt.to_period("M"))[
        'Frequency'].sum()

    return rfm_df, monthly_rfm, monthly_frequency

data_df = pd.read_csv("dashboard/dataa_df.csv")

counts_users = create_count_users(data_df)
season_pattern = create_season_patern(data_df)
weather_pattern = create_weather_pattern(data_df)
thn_tahun = create_year(data_df)
monthly_pattern = create_month_pattern(data_df)
weekday_pattern = create_weekday_pattern(data_df)
workingday_pattern = create_workingday_pattern(data_df)
rfm_df, monthly_rfm, monthly_frequency = create_rfm_df(data_df)


# Membuat sidebar
st.sidebar.title("Navigasi")
menu = st.sidebar.selectbox(
    "Halaman:", ["Beranda", "Pengguna", "Musim & Cuaca", "Riwayat Tahun", "Hari Kerja", "Analisis RFM"])
st.sidebar.write("Anda memilih:", menu)
# Menampilkan konten berdasarkan pilihan
if menu == "Beranda":
    st.title("Dashboard Analisis Penyewaan Sepeda")
    st.image("dashboard/bike-rental.png")
    st.caption("Copyright (c) :blue[Ergeape] 2025 :sunglasses:")

elif menu == "Pengguna":
    st.title("Jumlah Pengguna")
    st.metric("Total pengguna: ", counts_users["counts_user"])

    fig1 = plt.figure(figsize=(6, 4))
    sns.barplot(x=["Registered Users", "Casual Users"], y=[
        counts_users["total_registered"], counts_users["total_casual"]], palette="coolwarm")

    # Menambahkan angka di atas bar dalam format ribuan (1K, 10K, dll.)
    for i, count in enumerate([counts_users["total_registered"], counts_users["total_casual"]]):
        plt.text(i, count + 1000, f"{count:,}", ha='center')

    # Format angka di sumbu Y menjadi ribuan
    plt.gca().yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f'{int(x/1000)}K'))

    plt.title("Perbandingan Pengguna Registered vs Casual")
    plt.ylabel("Jumlah Pengguna")
    plt.xlabel("Tipe Pengguna")

    st.pyplot(fig1)

elif menu == "Musim & Cuaca":
    st.title("Pola berdasarkan Musim dan Cuaca")
    st.subheader("Jumlah Penyewa Berdasarkan Musim")
    fig2 = plt.figure(figsize=(12, 8))
    plt.bar(season_pattern['season'], season_pattern['registered'],
            label='Registered', color='royalblue')
    plt.bar(season_pattern['season'], season_pattern['casual'],
            label='Casual', color='sandybrown', bottom=season_pattern['registered'])
    plt.xlabel("Musim")
    plt.ylabel("Jumlah Pengguna")
    plt.legend()
    st.pyplot(fig2)

    fig3 = plt.figure(figsize=(12, 8))
    st.subheader("Jumlah Penyewa Berdasarkan Cuaca")
    plt.bar(weather_pattern['weathersit'], weather_pattern['registered'],
            label='Registered', color='royalblue')
    plt.bar(weather_pattern['weathersit'], weather_pattern['casual'],
            label='Casual', color='sandybrown', bottom=weather_pattern['registered'])
    plt.xlabel("Cuaca")
    plt.ylabel("Jumlah Pengguna")
    plt.legend()
    st.pyplot(fig3)

elif menu == "Riwayat Tahun":
    st.header("Jumlah penyewa sepeda dalam beberapa tahun")
    fig3 = plt.figure(figsize=(12, 6))
    sns.lineplot(data=monthly_pattern, x="mnth", y="cnt",
                 hue="yr", marker="o", palette="coolwarm")
    plt.xlabel("Bulan")
    plt.ylabel("Jumlah Penyewa")
    plt.title("Tren Peminjaman Sepeda per Bulan")
    plt.legend(title="Tahun")
    plt.grid(True)
    st.pyplot(fig3)
    st.write("Total Users")
    st.write(f"Tahun {thn_tahun.iloc[0, 0]} = {thn_tahun.iloc[0, 1]:,}")
    st.write(f"Tahun {thn_tahun.iloc[1, 0]} = {thn_tahun.iloc[1, 1]:,}")

elif menu == "Hari Kerja":
    st.header("Perbandingan antara hari kerja dan hari libur")
    fig4 = plt.figure(figsize=(6, 5))
    ax = sns.barplot(x="workingday", y="cnt",
                     data=workingday_pattern, palette="Blues")
    # Atur format sumbu Y menjadi ribuan tanpa desimal
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.0f}"))

    plt.xlabel("Working day")
    plt.ylabel("Jumlah penyewa")
    st.pyplot(fig4)

elif menu == "Analisis RFM":
    st.title("Analisis RFM")
    st.subheader("Recency Trend")
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(monthly_rfm['month'].astype(str),
             monthly_rfm['Recency'], marker='o', color='b', label='Recency')
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Days Since Last Transaction")
    ax1.legend()
    ax1.tick_params(axis='x', rotation=45)
    st.pyplot(fig1)

    # Frequency Trend
    st.subheader("Frequency per Bulan")
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    ax2.bar(monthly_frequency.index.astype(str),
            monthly_frequency.values, color='g', label='Frequency')
    ax2.set_xlabel("Bulan")
    ax2.set_ylabel("Total Transaksi")
    ax2.legend()
    ax2.tick_params(axis='x', rotation=45)
    st.pyplot(fig2)

    # Monetary Trend
    st.subheader("Monetary Trend")
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    ax3.plot(monthly_rfm['month'].astype(str),
             monthly_rfm['Monetary'], marker='o', color='r', label='Monetary')
    ax3.set_xlabel("Month")
    ax3.set_ylabel("Total Revenue")
    ax3.legend()
    ax3.tick_params(axis='x', rotation=45)
    st.pyplot(fig3)

st.sidebar.markdown("---")

min_date = data_df["dteday"].min()
max_date = data_df["dteday"].max()

with st.sidebar:

    st.write("Pilih rentang tanggal untuk melihat data")
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date, value=[min_date, max_date]
    )

# Footer di sidebar
st.sidebar.markdown("---")
st.sidebar.write("© 2025 Ergeape :sunglasses:")
