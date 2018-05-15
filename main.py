import blackhkjc as bh
import pandas as pd
import re
df = pd.read_pickle('handi.pkl')
df = df[df.MATCH_RESULT.apply(lambda x: len(re.sub('\(.*\) ','',x).split(':'))>1 )]
df['HOME_SCORE'] = df.MATCH_RESULT.apply(lambda x: int(re.sub('\(.*\) ','',x).split(':')[0].strip()) )
df['AWAY_SCORE'] = df.MATCH_RESULT.apply(lambda x: int(re.sub('\(.*\) ','',x).split(':')[1].strip()) )
df = df.groupby('ID').apply(lambda x:bh.setFirstLine(x))
df = df.groupby('ID').apply(lambda x:bh.setLastLine(x))
df['O_LINE'] = df.LINE.apply(lambda x: int(bh.line_mapping[x]))
df['O_FIRST_LINE'] = df.FIRST_LINE.apply(lambda x: int(bh.line_mapping[x]))
df = df.groupby('ID').apply(lambda x:bh.getPrevious(x))
df = df.reset_index(drop=True)
df.HOME_CHANGE = df.apply(lambda rec: '!!!' if (rec['HOME_CHANGE'] == rec['AWAY_CHANGE']) and (rec['HOME_CHANGE'] != '0') else
                         rec['HOME_CHANGE'],axis=1
                         )

df.AWAY_CHANGE = df.apply(lambda rec: '-' if (rec['HOME_CHANGE'] == '!!!') else
                         rec['AWAY_CHANGE'],axis=1
                         )

df.HOME_CHANGE = df.apply(lambda rec: '-' if (rec['HOME_CHANGE'] == '!!!') else
                         rec['HOME_CHANGE'],axis=1
                         )
df['HOME_CHANGE'] = df.apply(lambda rec: bh.update_home_change_by_line_change(rec),axis=1)
df['AWAY_CHANGE'] = df.apply(lambda rec: bh.update_away_change_by_line_change(rec),axis=1)
df = df.groupby('ID').apply(lambda x: bh.get_home_continuous_pattern(x))
df = df.groupby('ID').apply(lambda x: bh.get_awy_continuous_pattern(x))
number_repeating_patterns = 7
pattern = r'0-{' + str(number_repeating_patterns) + r'}'
df['A_PAT_FOUND'] = df.AWAY_TREND.apply(lambda x: 'Y' if re.findall(pattern,x) else 'N')
df['H_PAT_FOUND'] = df.HOME_TREND.apply(lambda x: 'Y' if re.findall(pattern,x) else 'N')
df['PAT_FOUND'] = df.apply(lambda rec: 'Y' if ((rec['A_PAT_FOUND'] =='Y') or (rec['H_PAT_FOUND']=='Y')) else 'N',axis=1)
df['HANDI_LABEL'] = df.apply(lambda rec:bh.get_handi_label(rec),axis=1)
df = df.reset_index(drop=True)
# Generate Summary
df_found = df[df['PAT_FOUND'] == 'Y']
summary = {}
summary['SAMPLE_SIZE'] = len(df_found.ID.unique())

for k,v in sorted(bh.line_mapping.items(),key=lambda x:x[1]):
    df_temp = df_found[(df_found.O_FIRST_LINE == v) ].groupby(['HANDI_LABEL','H_PAT_FOUND']).agg({"ID": pd.Series.nunique}).reset_index()

    if not df_temp.empty:
        df_N = df_temp[(df_temp['H_PAT_FOUND'] == 'N') & (df_temp['HANDI_LABEL'] != 'D')]

        if not df_N.empty:
            away_sample = df_N[df_N.HANDI_LABEL == 'A'].ID.sum()
            away_win_ratio = round(df_N[df_N.HANDI_LABEL == 'A'].ID.sum() / df_N.ID.sum(),2)
        else:
            away_sample = away_win_ratio = 0

        df_Y = df_temp[(df_temp['H_PAT_FOUND'] == 'Y') & (df_temp['HANDI_LABEL'] != 'D')]
        if not df_Y.empty:
            home_sample = df_Y[df_Y.HANDI_LABEL == 'H'].ID.sum()
            home_win_ratio = round(df_Y[df_Y.HANDI_LABEL == 'H'].ID.sum() / df_Y.ID.sum(),2)
        else:
            home_sample = home_win_ratio = 0
    else:
        home_sample = home_win_ratio = away_sample = away_win_ratio = 0
    
    hand_4_threshold_up  = 1.1
    hand_4_threshold_low = hand_2_threshold_up = 0.8
    hand_2_threshold_low = hand_1_threshold_up = 0.7
    hand_1_threshold_low = 0.6
    home_suggest_hands = away_suggest_hands = ''
    
    ############ Home Suggestion #################################
    if hand_1_threshold_up > home_win_ratio >= hand_1_threshold_low:
        home_suggest_hands = 'HOME, 1 hand'
    if hand_2_threshold_up > home_win_ratio >= hand_2_threshold_low:
        home_suggest_hands = 'HOME, 2 hands'
    if hand_4_threshold_up > home_win_ratio >= hand_4_threshold_low:
        home_suggest_hands = 'HOME, 4 hands'
    if hand_1_threshold_up > 1- home_win_ratio >= hand_1_threshold_low and home_win_ratio !=0:
        home_suggest_hands = 'RE(AWAY), 1 hand'
    if hand_2_threshold_up > 1- home_win_ratio >= hand_2_threshold_low and home_win_ratio !=0:
        home_suggest_hands = 'RE(AWAY), 2 hands'
    if hand_4_threshold_up > 1- home_win_ratio >= hand_4_threshold_low and home_win_ratio !=0:
        home_suggest_hands = 'RE(AWAY), 4 hands'
    
    
    ############ Away Suggestion #################################
    if hand_1_threshold_up > away_win_ratio >= hand_1_threshold_low:
        away_suggest_hands = 'AWAY, 1 hand'
    if hand_2_threshold_up > away_win_ratio >= hand_2_threshold_low:
        away_suggest_hands = 'AWAY, 2 hands'
    if hand_4_threshold_up > away_win_ratio >= hand_4_threshold_low:
        away_suggest_hands = 'AWAY, 4 hands'
    if hand_1_threshold_up > 1- away_win_ratio >= hand_1_threshold_low and away_win_ratio !=0:
        away_suggest_hands = 'RE(HOME), 1 hand'
    if hand_2_threshold_up > 1- away_win_ratio >= hand_2_threshold_low and away_win_ratio !=0:
        away_suggest_hands = 'RE(HOME), 2 hands'
    if hand_4_threshold_up > 1- away_win_ratio >= hand_4_threshold_low and away_win_ratio !=0:
        away_suggest_hands = 'RE(HOME), 4 hands'
        
    
    print(str(v).zfill(2),':', k.rjust(10, ' '), '------', 
          str(home_win_ratio).ljust(4, ' '), '('+str(home_sample).rjust(2,' ')+')',
          'VS', 
          str(away_win_ratio).ljust(5, ' '), '('+str(away_sample).rjust(2,' ')+')', ' '*10, home_suggest_hands.ljust(20, ' '),  away_suggest_hands )


df.to_csv('result.csv')
