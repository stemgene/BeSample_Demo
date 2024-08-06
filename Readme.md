## Description of documents and code files

### Dependencies

I've generated the `requirements.txt` by **conda**, but it's enough if only install all libraries in the first cell of the `final_submit.ipynb`. Sometimes, if you want to read an Microsoft Excel file, `openpyxl` needs be installed.

In order to generate the ancestor relationship network graph, please install the `pygraphviz`.

### Output files

#### user with scores

I've assigned the Bot score for every user in this table, `final_result.xlsx`, by the analysis of cluster, IP, registration time, user answer patterns and the similarity scores.

* `user_id`: 5070 user
* `cluster`: whether this user belongs to a cluster (a cluster means more than 10 users share with one ancestor).
* `ip` and `IP feature`: whether this user's IP address is normal or same with others
* `ip_isp`, `ip_org` and `ip_is_proxy`: other features of IP address, but I was not able to extract useful information
* `created_at`: I labeled peak registration date with colors.
* `QID11_TEXT_translated`: user answers of QID11 in English
* `QID11_answer_feature`: patterns of QID11 answers
* `eyal_QID154_TEXT_translated` and `QID154_answer_feature`: similar to above
* `same IP and similar answer`: whether this user has same IP and similar answer with other users
* `peak period`: whether this user registered at the peak date.
* `other features`: labeled the common ancestor of clusters
* score columns:
    * `cluster score`
    * `IP score`
    * `create_at_score`
    * `QID11_score`
    * `pattern_score_1`: similarity score with patterns1 (example answers of patterns with score <= 0.7)
    * `pattern_score_2`: similarity score with patterns2 (example answers of patterns with score > 0.7)
* `white list`: If I have high confidence that this user is a normal person, I will set this value to 0.
* `total_score`: the total score of whether user is a bot, if the score is higher than 0.7, the user is more likely a bot.

#### Other output files

I put the some essential and temporary files into the `./outputs` folder. The files below are used in the `final_submit.ipynb`, but I'll submit all output files in case you need it.

* "./outputs/520.xlsx" -- The 1st version of my final result. This file contains `user_id`, `cluster`, `IP`, `created_at`, `QID11_translated`, `QID11_pattern` and the scores. I spent majority time on analyzing this file.
* "./outputs/profile_QID11" -- only contains the answers of QID11
* "./outputs/cluster_QID11_answer.csv" -- only contains QID11 answers with 11 cluster users.
* "./outputs/Qid11_Qid154_answers.xlsx"  -- this file only contain answers of Qid11 and Qid154.
* "./outputs/translated_all_profile_answers.csv"  --  it's a big dataframe, contains all import user answers with their English translates. 
* "./outputs/ancestor_relationship.gv.txt" -- for draw the relationship plot
* "./outputs/came_from_userid.txt" -- contains ancestor relathinship
* "./outputs/patterns1.txt" -- example answers of patterns with score <= 0.7
* "./outputs/patterns2.txt" -- example answers of patterns with score > 0.7


### Code files

* `final_submit.ipynb`  --  The jupyter notebook file to demograph all data which I showed during the presentation.

In order to make the jupyter notebook file more concise, I put some functional code into several python files.

* preprocessing_script.py
* functions.py
* analyze_json.py

### Analysis file 

I combined the user answers with clusters, IP and created time, as well as answer patterns. This file contains the analysis of them.

I also put the metrics of the scoring mechanism into this Google Doc.

### Summary

I'm glad to have chance to participate in this project. 

I found it's hard to identify a single column to determine which user is a Bot or not. Therefore I created a scoring mechanism. 

However, there are still some detect in my scoring mechanism. For example, the total score tends to be lower than 0.7, because I didn't set individual pattern or feature as a high score, therefore once multiplied the weight of each faeture, the total score would be reduced.

Another important drawback is these metrics are so subjective, the scores should be set by someone more familiar with business.

Finally, there are some interesting tasks that I don't have time to do, such as analyzing the isp of IP address, or train the model to detect AI generated sentences, etc. I'd like to participate the further projects.

If you have any questions, feel free to reach out with me at hdongbos@gmail.com