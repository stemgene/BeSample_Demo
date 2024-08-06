import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import preprocessing_script as ps
import pygraphviz as pgv

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

def generate_ancestor_pair(users_df):
    """
    1. convert uuid to user_id in order to display easily
    2. generate the pair of "came_from" and "user_id" as the pattern of f"{came_from} -> {userid};\n"
    3. save them to a txt file
    """
    userid_uuid = dict(zip(users_df['uuid'], users_df['user_id']))
    users_df['came_from_userid'] = users_df['came_from'].map(userid_uuid)

    with open('./outputs/came_from_userid.txt', 'w') as file:
        for index, row in users_df[~users_df['came_from_userid'].isna()].iterrows():
            came_from = int(row['came_from_userid'])
            userid = int(row['user_id'])
            file.write(f"{came_from} -> {userid};\n")
    print("outputs/came_from_userid.txt has been created.")
    return users_df

def generate_relaionship_figure():
    with open('./outputs/ancestor_relationship.gv.txt', 'r') as file:
        graph_data = file.read()

        graph = pgv.AGraph(string=graph_data)
        graph.draw('./outputs/graph.png', prog='dot')

def get_clusters(users_df):
    cluster1 = users_df[users_df['came_from_userid'] == 311921572]['user_id'].tolist()
    cluster1.extend(users_df[users_df['came_from_userid'] == 417084553]['user_id'].tolist())
    cluster1.extend([311921572, 716867449,417084553])
    cluster2 = users_df[users_df['came_from_userid'] == 668849234]['user_id'].tolist()
    cluster2.append(668849234)
    cluster3 = users_df[users_df['came_from_userid'] == 5465355038]['user_id'].tolist()
    cluster3.extend(users_df[users_df['came_from_userid'] == 890122204]['user_id'].tolist())
    cluster3.extend([5465355038, 5598448896, 420698029, 945424125, 706040182, 504595031, 5163505376, 735204037])
    cluster4 = users_df[users_df['came_from_userid'] == 473750820]['user_id'].tolist()
    cluster4.extend([5133726308, 473750820])
    cluster5 = users_df[users_df['came_from_userid'] == 438851599]['user_id'].tolist()
    cluster5.append(438851599)
    cluster6 = users_df[users_df['came_from_userid'] == 1194542274]['user_id'].tolist()
    cluster6.extend([1194542274, 818587263, 6607059188, 6659819686, 1273848861])
    cluster7 = users_df[users_df['came_from_userid'] == 1066085461]['user_id'].tolist()
    cluster7.append(1066085461)
    cluster8 = users_df[users_df['came_from_userid'] == 6176818872]['user_id'].tolist()
    cluster8.append(6176818872)
    cluster9 = users_df[users_df['came_from_userid'] == 892214992]['user_id'].tolist()
    cluster9.extend(users_df[users_df['came_from_userid'] == 1849996722]['user_id'].tolist())
    cluster9.extend(users_df[users_df['came_from_userid'] == 5895008754]['user_id'].tolist())
    cluster9.extend([892214992, 6778386523])
    cluster10 = users_df[users_df['came_from_userid'] == 5875951195]['user_id'].tolist()
    cluster10.extend(users_df[users_df['came_from_userid'] == 6731913800]['user_id'].tolist())
    cluster10.extend(users_df[users_df['came_from_userid'] == 6804306277]['user_id'].tolist())
    cluster10.extend(users_df[users_df['came_from_userid'] == 6850206527]['user_id'].tolist())
    cluster10.extend(users_df[users_df['came_from_userid'] == 6382561843]['user_id'].tolist())
    cluster10.extend(users_df[users_df['came_from_userid'] == 6874816982]['user_id'].tolist())
    cluster10.extend(users_df[users_df['came_from_userid'] == 6480646061]['user_id'].tolist())
    cluster10.extend(users_df[users_df['came_from_userid'] == 6723913136]['user_id'].tolist())
    cluster10.extend(users_df[users_df['came_from_userid'] == 5842137443]['user_id'].tolist())
    cluster10.extend(users_df[users_df['came_from_userid'] == 6855516580]['user_id'].tolist())
    cluster10.extend(users_df[users_df['came_from_userid'] == 6819342705]['user_id'].tolist())
    cluster10.extend([5875951195])
    cluster11 = users_df[users_df['came_from_userid'] == 879318569]['user_id'].tolist()
    cluster11.extend(users_df[users_df['came_from_userid'] == 703756276]['user_id'].tolist())
    cluster11.extend(users_df[users_df['came_from_userid'] == 565778395]['user_id'].tolist())
    cluster11.extend(users_df[users_df['came_from_userid'] == 1124522690]['user_id'].tolist())
    cluster11.extend(users_df[users_df['came_from_userid'] == 6013721077]['user_id'].tolist())
    cluster11.extend(users_df[users_df['came_from_userid'] == 691991934]['user_id'].tolist())
    cluster11.extend(users_df[users_df['came_from_userid'] == 1305235628]['user_id'].tolist())
    cluster11.extend(users_df[users_df['came_from_userid'] == 1075950373]['user_id'].tolist())
    cluster11.extend(users_df[users_df['came_from_userid'] == 6593476111]['user_id'].tolist())
    cluster11.extend(users_df[users_df['came_from_userid'] == 6526945831]['user_id'].tolist())
    cluster11.extend(users_df[users_df['came_from_userid'] == 6432216875]['user_id'].tolist())
    cluster11.extend(users_df[users_df['came_from_userid'] == 6713046063]['user_id'].tolist())
    cluster11.extend(users_df[users_df['came_from_userid'] == 6594837997]['user_id'].tolist())
    cluster11.extend(users_df[users_df['came_from_userid'] == 6523687198]['user_id'].tolist())
    cluster11.extend(users_df[users_df['came_from_userid'] == 6045101057]['user_id'].tolist())
    cluster11.extend(users_df[users_df['came_from_userid'] == 6717837324]['user_id'].tolist())
    cluster11.extend(users_df[users_df['came_from_userid'] == 6343298492]['user_id'].tolist())
    cluster11.extend(users_df[users_df['came_from_userid'] == 6470916055]['user_id'].tolist())
    cluster11.extend(users_df[users_df['came_from_userid'] == 1374938939]['user_id'].tolist())
    cluster11.extend(users_df[users_df['came_from_userid'] == 6375579324]['user_id'].tolist())
    cluster11.extend(users_df[users_df['came_from_userid'] == 6956224975]['user_id'].tolist())
    cluster11.extend([879318569, 831745576, 5614654774, 588886738])
    clusters = {
        "cluster1": cluster1,
        "cluster2": cluster2,
        "cluster3": cluster3,
        "cluster4": cluster4,
        "cluster5": cluster5,
        "cluster6": cluster6,
        "cluster7": cluster7,
        "cluster8": cluster8,
        "cluster9": cluster9,
        "cluster10": cluster10,
        "cluster11": cluster11
    }
    return clusters