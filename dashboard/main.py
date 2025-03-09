import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mticker
import streamlit as st
sns.set(style='dark')


def create_count_users(df):
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


def create_month_pattern(df):
    df["mnth"] = pd.Categorical(df["mnth"], categories=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], ordered=True)
    monthly_trend = df.groupby(["yr", "mnth"])["cnt"].sum().reset_index()
    return monthly_trend


def create_workingday_pattern(df):
    workingday_pattern = df.groupby("workingday")[["cnt"]].sum()
    return workingday_pattern


def apply_binning(df, method):
    df['dteday'] = pd.to_datetime(df['dteday'])

    if method == "Kuantil":
        df['Binning_Kuantil'] = pd.qcut(
            df['cnt'], q=3, labels=['Rendah', 'Sedang', 'Tinggi'])
        return df[['dteday', 'cnt', 'Binning_Kuantil']]

    elif method == "Nilai Tetap":
        max_cnt = df['cnt'].max()
        # Pastikan bins bertambah secara monotonis
        if max_cnt <= 4000:
            # Hilangkan batas 4000 jika max_cnt terlalu kecil
            bins = [0, 2000, max_cnt]
            labels = ['Rendah', 'Sedang']
        else:
            bins = [0, 2000, 4000, max_cnt]
            labels = ['Rendah', 'Sedang', 'Tinggi']

        df['Binning_Tetap'] = pd.cut(
            df['cnt'], bins=bins, labels=labels, include_lowest=True)
        return df[['dteday', 'cnt', 'Binning_Tetap']]

    elif method == "Hari":
        df['weekday'] = df['dteday'].dt.day_name()
        weekday_pattern = df.groupby("weekday", as_index=False)['cnt'].sum()
        return weekday_pattern


data_df = pd.read_csv("dataa_df.csv")

min_date = data_df["dteday"].min()
max_date = data_df["dteday"].max()

with st.sidebar:

    st.write("Pilih rentang tanggal untuk melihat data")
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date, value=[min_date, max_date]
    )

st.sidebar.markdown("---")

main_df = data_df[(data_df["dteday"] >= str(start_date))
                  & (data_df["dteday"] <= str(end_date))]

counts_users = create_count_users(main_df)
season_pattern = create_season_patern(main_df)
weather_pattern = create_weather_pattern(main_df)
monthly_pattern = create_month_pattern(main_df)
workingday_pattern = create_workingday_pattern(main_df)


# Membuat sidebar
st.sidebar.title("Navigasi")
menu = st.sidebar.selectbox(
    "Halaman:", ["Beranda", "Pengguna", "Musim & Cuaca", "Tren/bulan", "Hari Kerja", "Binning"])
st.sidebar.write("Anda memilih:", menu)
# Menampilkan konten berdasarkan pilihan
if menu == "Beranda":
    st.title("Dashboard Analisis Penyewaan Sepeda")
    st.image("bike-rental.png")
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

elif menu == "Tren/bulan":
    st.header("Tren Peminjaman Sepeda per Bulan")
    fig3 = plt.figure(figsize=(12, 6))
    sns.lineplot(data=monthly_pattern, x="mnth", y="cnt",
                 hue="yr", marker="o", palette="coolwarm")
    plt.xlabel("Bulan")
    plt.ylabel("Jumlah Penyewa")
    plt.legend(title="Tahun")
    plt.grid(True)
    st.pyplot(fig3)

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

elif menu == "Binning":
    st.title("Analisis Binning")
    binning_method = st.selectbox("Pilih variabel untuk binning", [
                                  "Kuantil", "Nilai Tetap", "Hari"])
    df_binned = apply_binning(main_df, binning_method)
    figbin, ax = plt.subplots(figsize=(10, 5))

    if binning_method == "Hari":
        sns.barplot(data=df_binned, x="weekday",
                    y="cnt", palette="coolwarm", ax=ax, order=["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
        ax.set_xlabel("Hari")
        ax.set_ylabel("Jumlah Penyewa")
        ax.set_title("Distribusi Penyewaan Berdasarkan Hari")
        plt.xticks(rotation=45)
    else:
        sns.countplot(data=df_binned,
                      x=df_binned.columns[-1], palette="coolwarm", ax=ax)
        ax.set_xlabel("Kategori Binning")
        ax.set_ylabel("Jumlah Penyewa")
        ax.set_title(f"Distribusi {binning_method}")

    st.pyplot(figbin)


# Footer di sidebar
st.sidebar.markdown("---")
st.sidebar.write("© 2025 Ergeape :sunglasses:")
