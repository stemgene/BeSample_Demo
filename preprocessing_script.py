import os
import re
import pandas as pd
import json
import random


def clean_users():
    # 1. Load data
    df = pd.read_csv("data/users_new.csv", sep="|")
    # 1.1 Divide json field into 3 columns
    rep_dict='{"public_ip": -1, "demo_speedrun": -1, "referral_ancestor": "00000000-0000-0000-0000-000000000000"}'
    df['data_fraud'] = df['data_fraud'].fillna(rep_dict)  # fill missing values
    result= df['data_fraud'].apply(lambda s: pd.json_normalize(json.loads(s)))  
    b = pd.concat(list(result), ignore_index=True)
    df = df.join(b)
    # 2. Fill missing values
    df['pined_msg_id'] = df['pined_msg_id'].fillna(-1.0)
    df['came_from'] = df['came_from'].fillna("00000000-0000-0000-0000-000000000000")
    df['lang'] = df['lang'].fillna("unknown")
    df['jira_task'] = df['jira_task'].fillna("AAA-000")
    df['ip'] = df['ip'].fillna("0.0.0.0")
    df['attentive'] = df['attentive'].map({'t': 1, 'f': 0})
    df['attentive'] = df['attentive'].fillna(-1)
    df['campaign'] = df['campaign'].fillna("unknown")
    df['username'] = df['username'].fillna("unknown")
    df['isBot'] = df['isBot'].map({'t': 1})
    df['isBot'] = df['isBot'].fillna(-1)
    df['lead_channel'] = df['lead_channel'].fillna("unknown")
    df['score'] = df['score'].fillna(random.choice(df[~(df['score'].isna())]['score']))
    df['public_ip'] = df['public_ip'].map({True: 1, False: 0})
    df['public_ip'] = df['public_ip'].fillna(-1)
    df['demo_speedrun'] = df['demo_speedrun'].map({True: 1, False: 0})
    df['demo_speedrun'] = df['demo_speedrun'].fillna(-1)
    df['referral_ancestor'] = df['referral_ancestor'].fillna("00000000-0000-0000-0000-000000000000")
    df = df.drop(['qa_range', 'data_fraud'], axis=1)
    # 3. Duplicates
    df = df.drop_duplicates(subset=['uuid'], keep='last', ignore_index=True)
    # 4. Data type
    df['created_at'] = pd.to_datetime(df['created_at'])
    # 5. Devide into true and false group
    isBot_t = df[df['isBot'] == 1]
    isBot_f = df[df['isBot'] == -1]
    return df, isBot_t, isBot_f

def clean_log():
    # 1. Load data
    df = pd.read_csv('./data/users_event_log.csv', sep=',', quotechar='"')
    # 2. Fill missing values
    df['created_at'] = df['created_at'].ffill()
    df['recaptcha_score'] = df['recaptcha_score'].fillna(-1)
    df['comment'] = df['comment'].fillna('unknown')
    df['proxy_used'] = df['proxy_used'].map({'t': 1})
    df['proxy_used'] = df['proxy_used'].fillna(-1)
    # 3. Data type
    df['created_at'] = pd.to_datetime(df['created_at'], format='mixed')
    return df

def clean_profile():
    # 1. Load data
    df = pd.read_csv('./data/profile.csv', sep=',', quotechar='"')
    # 1.1 Divide json field into 3 columns
    rep_dict='{"labels": "{}", "values": "{}", "responseId": "R_000000000000000", "displayedFields": "[]", "displayedValues": "{}"}'
    # 2. Fill missing values
    df['eyal_answers'] = df['eyal_answers'].fillna(rep_dict)  # fill missing values
    # 3. Data type
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.drop(['age', 'silvana_answers'], axis=1)
    return df

def clean_user_profile(users_df, profile_df):
    users_profile_df = users_df[['user_id', 'ip', 'created_at']].merge(profile_df[['user_id', 'created_at', 'demography_body', 'eyal_answers']], how='left', left_on='user_id', right_on='user_id', suffixes=('_user', '_profile')).drop_duplicates(subset='user_id')
    users_profile_df = users_profile_df.sort_values('created_at_user')
    users_not_in_profile_df = users_profile_df[users_profile_df['created_at_profile'].isna()]
    users_profile_df = users_profile_df.dropna(axis=0).reset_index(drop=True)
    users_profile_df['created_at_diff'] = users_profile_df['created_at_profile'] - users_profile_df['created_at_user']
    users_profile_df['date'] = users_profile_df['created_at_user'].dt.date

    return users_profile_df, users_not_in_profile_df

def main():
    clean_users()


if __name__ == "__main__":
    main()