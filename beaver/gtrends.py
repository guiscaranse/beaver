from pytrends.request import TrendReq


def interest_score(keywords, pubtime):
    score = 0
    time1 = pubtime.subtract(weeks=1).to_w3c_string().split(':')[0] # De
    time2 = pubtime.to_w3c_string().split(':')[0] # Até
    trend = TrendReq(hl='pt-BR')
    trend.build_payload(kw_list=keywords, cat=0, timeframe=time1 + " " + time2, geo='BR',
                        gprop='news')

    # Interest Over Time
    interest_over_time_df = trend.interest_over_time().to_dict('records')
    for item in interest_over_time_df:
        score += list(item.values())[0]
    return score
