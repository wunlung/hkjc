import pandas as pd
import math
line_mapping = {
 '(+2/+2.5)': 0,
 '(+2)': 1,
 '(+1.5/+2)': 2,
 '(+1.5)': 3, 
 '(+1/+1.5)': 4,
 '(+1)': 5,   
 '(+0.5/+1)':6,
 '(+0.5)':7,
 '(0/+0.5)':8,
 '(0)': 9 ,
 '(0/-0.5)':10,   
 '(-0.5)':11,   
 '(-0.5/-1)':12,
 '(-1)':13,
 '(-1/-1.5)':14,
 '(-1.5)':15,
 '(-1.5/-2)':16,
 '(-2)':17,
 '(-2/-2.5)':18,
 '(-2.5)':19,
 '(-2.5/-3)':20
}

def setFirstLine(x):
    x = x.sort_values(['TIME'])
    x['FIRST_LINE'] = x['LINE'].iloc[0]
    return x

def setLastLine(x):
    x = x.sort_values(['TIME'])
    x['LAST_LINE'] = x['LINE'].iloc[-1]
    return x

def getPrevious(x):
    x = x.sort_values(['TIME'])
    x['O_LINE_LEAD'] = x['O_LINE'].shift(1)
    return x

def update_home_change_by_line_change(rec):
    sign = ''
    if (rec['O_LINE'] != rec['O_LINE_LEAD']) and not math.isnan(rec['O_LINE_LEAD']):
        if rec['O_LINE_LEAD'] > rec['O_LINE']:
            sign = '+'
        elif rec['O_LINE_LEAD'] < rec['O_LINE']:
            sign = '-'
    else:
        sign = rec['HOME_CHANGE']
    return sign

def update_away_change_by_line_change(rec):
    sign = ''
    if (rec['O_LINE'] != rec['O_LINE_LEAD']) and not math.isnan(rec['O_LINE_LEAD']):
        if rec['O_LINE_LEAD'] < rec['O_LINE']:
            sign = '+'
        elif rec['O_LINE_LEAD'] > rec['O_LINE']:
            sign = '-'
    else:
        sign = rec['AWAY_CHANGE']
    return sign

def get_home_continuous_pattern(x):
    x = x.sort_values(['TIME'])
    trend_to_search = x['HOME_CHANGE'].astype(str).str.cat()
    x['HOME_TREND'] = trend_to_search
    return x

def get_awy_continuous_pattern(x):
    x = x.sort_values(['TIME'])
    trend_to_search = x['AWAY_CHANGE'].astype(str).str.cat()
    x['AWAY_TREND'] = trend_to_search
    return x

def get_handi_label(rec):
    rlabel = ''
    # handling Draw result
    for i in range(len(line_mapping)):
        if line_mapping[rec['LAST_LINE']] == i:
            if rec['HOME_SCORE'] + 2.25- i*0.25 - rec['AWAY_SCORE'] >0:
                rlabel = 'H'
            elif rec['HOME_SCORE'] + 2.25- i*0.25 - rec['AWAY_SCORE'] == 0:
                rlabel = 'D'
            else:
                rlabel = 'A'
    return rlabel


def get_win_ratio_sample(df, venue='H'):
    if not df.empty:
        sample = df[df.HANDI_LABEL == venue].ID.sum()
        win_ratio = round(df[df.HANDI_LABEL == venue].ID.sum() / df.ID.sum(),2)
    else:
        sample = win_ratio = 0
    return win_ratio, sample
    
def home_away_suggest(home_win_ratio,away_win_ratio):
    home_suggest_hands = away_suggest_hands = ''
    hand_4_threshold_up  = 1.1
    hand_4_threshold_low = hand_2_threshold_up = 0.8
    hand_2_threshold_low = hand_1_threshold_up = 0.7
    hand_1_threshold_low = 0.6
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
    return home_suggest_hands,away_suggest_hands

