import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import preprocessing_script as ps

def fill_miss_date(data):
    """
    copy 'created_at' column to index
    return dataframe with filled date index
    """
    # datetime_series = pd.to_datetime(data['created_at']) # I commend this row in order to make two plots have the same x axis
    datetime_series = pd.to_datetime(data['created_at'])
    datetime_index  = pd.DatetimeIndex(datetime_series.values) 
    data.set_index(datetime_index, inplace=True)
    data.sort_index(inplace=True)
    return data.asfreq('D')

def users_over_time():
    users_df, isBot_t, isBot_f = ps.clean_users()

    # Both Bot and None Value
    all_users_plot_df = users_df[['created_at', 'isBot']]
    all_users_plot_df['created_at'] = all_users_plot_df['created_at'].dt.floor('d')
    all_users_plot_df['isBot_t'] = (all_users_plot_df['isBot'] == 1).astype(int)
    all_users_plot_df['isBot_f'] = (all_users_plot_df['isBot'] == -1).astype(int)
    all_users_grouped_df = all_users_plot_df.groupby('created_at')[['isBot_t', 'isBot_f']].sum().reset_index()
    all_users_grouped_df_filled_missing = fill_miss_date(all_users_grouped_df)
    all_x_data = all_users_grouped_df_filled_missing.index
    all_y1_data = all_users_grouped_df_filled_missing['isBot_f'].fillna(0)
    all_y2_data = all_users_grouped_df_filled_missing['isBot_t'].fillna(0)
    user_counts = {'Not Bot': all_y1_data, 'Is Bot': all_y2_data}
    bottom = np.zeros(len(all_y1_data))

    # Only Bot: Actually this part is not neccessary, the 2nd plot can use all_x_data and all_y2_data
    isBot_t['created_at'] = isBot_t['created_at'].dt.floor('d')
    bot_users_grouped_df = isBot_t.groupby('created_at')['isBot'].count().to_frame("count").reset_index()
    # datetime_series = pd.to_datetime(grouped_df['created_at'])
    # datetime_index  = pd.DatetimeIndex(datetime_series.values)
    # grouped_df.set_index(datetime_index, inplace=True)
    # grouped_df.sort_index(inplace=True)
    bot_users_grouped_df_filled_missing = fill_miss_date(bot_users_grouped_df)  # Here input all_users `datatime_series` in order to make bot_only have the same x axis
    bot_x_data = bot_users_grouped_df_filled_missing.index
    bot_y_data = bot_users_grouped_df_filled_missing['count'].fillna(0)

    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(14, 8))

    for user, user_count in user_counts.items():
        p = ax1.bar(all_x_data, user_count, label=user, bottom=bottom)
        bottom += user_count
    ax1.legend()
    ax1.set_ylabel('Count')
    ax1.set_title('All User Count Over Time')

    #ax2.bar(bot_x_data, bot_y_data, color='coral')
    ax2.bar(all_x_data, all_y2_data, color='coral')
    # Make ticks on occurrences of each month:
    ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
    # Get only the month to show in the x-axis:
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    # '%b' means month as locale’s abbreviated name
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Count')
    ax2.set_title('Bot User Count Over Time')
    ax2.legend(['Bot Count'])
    plt.tight_layout() 
    plt.show()
