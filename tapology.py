import pandas as pd
import requests
import pycurl
import numpy as np
from bs4 import BeautifulSoup
import uuid
from io import BytesIO
from utility import joinurl, headers
import re

data_events = []
data_event_bouts = []
data_bouts = []
data_fighters = []

def getEventInfo(soup):
    event_id = uuid.uuid4().int
    event_name = soup.find("div", {"class": "eventPageHeaderTitles"}).select_one('h1').text
    if event_name.find(": "):
        name = event_name.split(": ")[0]
        sub_name = event_name.split(": ")[1]
    else:
        name = soup.find("div", {"class": "eventPageHeaderTitles"}).select_one('h1').text
        sub_name = None
    try:
        aka = soup.select_one('strong:contains("Also Known As") + span').text.strip()
    except AttributeError:
        aka = None
    #slug =
    venue = soup.select_one('strong:contains("Venue") + span').text.strip()
    try:
        location = soup.select_one('strong:contains("Location") + span').text.strip()
    except AttributeError:
        location = None
    try:
        promotion = soup.select_one('strong:contains("Promotion") + span').text.strip()
    except AttributeError:
        promotion = None
    try:
        ownership = soup.select_one('strong:contains("Ownership") + span').text.strip()
    except AttributeError:
        ownership = None
    try:
        co_promotion = soup.select_one('strong:contains("Co-Promoter") + span').text.strip()
    except AttributeError:
        co_promotion = None
    try:
        tv_announcers = soup.select_one('strong:contains("TV Announcers") + span').text.strip()
    except AttributeError:
        tv_announcers = None
    try:
        tv_ratings = soup.select_one('strong:contains("TV Ratings") + span').text.strip().split(' ')[0]
    except AttributeError:
        tv_ratings = None
    try:
        ring_announcer = soup.select_one('strong:contains("Ring Announcer") + span').text.strip()
    except AttributeError:
        ring_announcer = None
    try:
        post_fight_interviews = soup.select_one('strong:contains("Post-Fight Interviews") + span').text.strip()
    except:
        post_fight_interviews = None
    try:
        ppv_buys_buyrate = soup.select_one('strong:contains("PPV Buys / Buyrate") + span').text.strip()
    except AttributeError:
        ppv_buys_buyrate = None
    try:
        ticket_revenue_lg = soup.select_one('strong:contains("Ticket Revenue") + span').text.strip()
    except AttributeError:
        ticket_revenue_lg = None
    try:
        us_broadcast = soup.select_one('strong:contains("U.S. Broadcast") + span').text.strip()
    except AttributeError:
        us_broadcast = None
    try:
        prelims = soup.select_one('strong:contains("Prelims") + span').text.strip()
    except AttributeError:
        prelims = None
    try:
        tournament = soup.select_one('strong:contains("Tournament") + span').text.strip()
    except AttributeError:
        tournament = None
    try:
        attendance = soup.select_one('strong:contains("Attendance") + span').text.strip()
    except AttributeError:
        attendance = None
    try:
        matchmaker = soup.select_one('strong:contains("Matchmaker") + span').text.strip()
    except AttributeError:
        matchmaker = None
    event_date_time = soup.select_one("li.header").text
    date = re.search('(\d+.\d+.\d+)', event_date_time)[0] if re.search('(\d+.\d+.\d+)', event_date_time) else ''
    time = re.search('(\d+:\d+)', event_date_time)[0] if re.search('(\d+:\d+)', event_date_time) else ''
    event_date = time+'\n'+date
    timezone = "301"  # set default
    enclosure = soup.select_one('strong:contains("Enclosure") + span').text.strip()
    mma_bouts = soup.select_one('strong:contains("MMA Bouts") + span').text.strip()
    try:
        grappling_bouts = soup.select_one('strong:contains("Grappling Bouts") + span').text.strip()
    except AttributeError:
        grappling_bouts = None
    status = "active"  # set default

    newRowEvent = [event_id, name, sub_name, aka, venue, location, promotion, ownership, co_promotion, tv_ratings,
                   tv_announcers, ring_announcer, post_fight_interviews, ppv_buys_buyrate, ticket_revenue_lg,
                   us_broadcast, prelims, tournament, attendance, matchmaker, event_date, timezone, enclosure,
                   mma_bouts, grappling_bouts, status]
    data_events.append(newRowEvent)
    # df_events = pd.DataFrame(data_events,
    #                         columns=['event_id', 'name', 'sub_name', 'aka', 'venue',
    #                                  'location', 'promotion', 'ownership', 'co_promotion', 'tv_ratings',
    #                                  'tv_announcers', 'ring_announcer', 'post_fight_interviews', 'ppv_buys_buyrate',
    #                                  'ticket_revenue_lg', 'us_broadcast', 'prelims', 'tournament', 'attendance', 'matchmaker',
    #                                  'event_date', 'timezone', 'enclosure', 'mma_bouts', 'grappling_bouts', 'status'])
    # df_events.to_csv("fighter_events.csv", index=True, mode='a')

    return event_id

def getBoutInfo(soup, event_id):
    bout_id = uuid.uuid4().int
    event_date = re.search('(\d+.\d+.\d+)', soup.select_one('strong:contains("Date") + span').text.strip())[0]
    fighter_link = soup.find("span", {"class": "fName left"}).select_one('a')['href']
    fighter_id = getFighterData(fighter_link)
    opponent_link = soup.find("span", {"class": "fName right"}).select_one('a')['href']
    opponent_id = getFighterData(opponent_link)
    status = "confirmed"
    cancellation_reason = None
    try:
        bout_result = soup.find("div", {"class": "boutResultHolder"}).select_one("h4").text.strip()
    except AttributeError:
        status = "cancelled"

    if status == "cancelled":
        result = None
        try:
            cancellation_reason = soup.find("div", {"class": "transContent evenPadding"}).find('p').text
        except AttributeError:
            cancellation_reason = None
    elif status == "confirmed":
        if re.search("defeats", bout_result):
            result = "win"
        elif re.search("draw", bout_result):
            result = "draw"
        else:
            result = None
    boutPreResult_info = soup.findAll("h4")[1].text
    weight_class = re.search('(.*weight)', boutPreResult_info)[0].split()[-1]
    scheduled_weight = re.search('(\d+\.?\d? lbs)', boutPreResult_info)[0]
    fighters_recs = soup.find("div", {"class": "boutComparisonTable"}).select_one("tr").text.strip().split()
    rb_bout = fighters_recs[0]
    rb_bout_opponent = fighters_recs[-1]
    try:
        title_fight = soup.select_one('strong:contains("Title on Line") + span').text.strip()
    except AttributeError:
        title_fight = None
    try:
        referee = soup.select_one('strong:contains("Referee") + span').text.strip()
    except AttributeError:
        referee = None
    referee_id = None
    amateur = 0 if soup.select_one('strong:contains("Pro/Am") + span').text == "Professional" else 1
    on_site = 1
    tournament = None
    tournament_round = None
    disputed = None
    otn_fight = 0
    otn_knockout = 0
    otn_submission = 0
    otn_performance = 0
    injuries_sustained = None

    newBoutRow = [event_id, bout_id, event_date, fighter_id, opponent_id, result, status, cancellation_reason, weight_class,
                  scheduled_weight, rb_bout, rb_bout_opponent, title_fight, referee, referee_id, amateur, on_site, tournament,
                  tournament_round, disputed, otn_fight, otn_knockout, otn_submission, otn_performance, injuries_sustained]
    data_bouts.append(newBoutRow)
    # df_bouts = pd.DataFrame(data_bouts,
    #                              columns=['event_id', 'bout_id', 'event_date', 'fighter_id', 'opponent_id',
    #                                       'result', 'status', 'cancellation_reason', 'weight_class', 'scheduled_weight',
    #                                       'rb_bout', 'rb_bout_opponent', 'title_fight', 'referee', 'referee_id', 'amateur',
    #                                       'on_site', 'tournament', 'tournament_round', 'disputed', 'otn_fight', 'otn_knockout',
    #                                       'otn_submission', 'otn_performance', 'injuries_sustained'])
    # df_bouts.to_csv("fighter_bouts.csv", index=True, mode='a')

def getEventBoutInfo(soup, event_id):

    bout_position = soup.find("div", {"class": "fightCardBoutNumber"}).text
    result = soup.find("div", {"class": "fightCardResult"}).find("span", {"class": "result"}).text.strip()
    try:
        fn_method = result.split(', ')[0].strip()
        fn_move = result.split(', ')[1].strip()
    except:
        fn_method = result.strip()
        fn_move = None
    round_stucture = re.search('(\d.x.\d)', soup.find("div", {"class": "fightCardMatchup"}).text)[0]
    total_rounds = round_stucture[-1]
    round_time_lmt = round_stucture[0]+":00"
    fight_time = soup.find("div", {"class": "fightCardResult"}).find("span", {"class": "time"}).text.strip()
    final_round = re.search('(\d.?of.?\d.?)', fight_time)[0].split()[0] if re.search('(\d.?of.?\d.?)', fight_time) else total_rounds
    final_round_time = re.search('([0-5]?[0-9]:[0-5][0-9].Round)', fight_time)[0].split()[0] if re.search('([0-5]?[0-9]:[0-5][0-9].Round)', fight_time) else round_time_lmt
    total_fight_time = re.search('([0-5]?[0-9]:[0-5][0-9].Total)', fight_time)[0].split()[0] if re.search('([0-5]?[0-9]:[0-5][0-9].Total)', fight_time) else final_round_time
    billing = soup.find("div", {"class": "fightCardMatchup"}).find("span", {"class": "billing"}).text.strip()
    newRowEventBout = [event_id, bout_position, billing, fn_method, fn_move, round_stucture, total_rounds, total_fight_time,
                       final_round, final_round_time]
    data_event_bouts.append(newRowEventBout)
    # df_event_bouts = pd.DataFrame(data_event_bouts,
    #                            columns=['event_id', 'bout_position', 'billing', 'fn_method', 'fn_move', 'round_stucture',
    #                                     'total_rounds', 'total_fight_time', 'final_round', 'final_round_time'])
    # df_event_bouts.to_csv("event_bouts.csv", index=True, mode='a')


def getFighterData(fighter_link):
    # rank_url ="https://www.tapology.com/rankings/current-top-ten-heavyweight-mma-fighters-265-pounds"
    # response = requests.get(rank_url)
    # soup = BeautifulSoup(response.text,features="html.parser")
    #
    # fighter_links = [fighter['href'] for fighter in soup.select(".rankingItemsItemRow .name a[href]")]
    #
    # for fighter_link in fighter_links:
    url = "https://tapology.com" + fighter_link
    r = requests.get(url,headers=headers)
    soup = BeautifulSoup(r.text,features="html.parser")
    # Parsing info
    id = uuid.uuid4().int
    fid = soup.select_one('[name="fid"]').get('content')
    name = soup.select_one('strong:contains("Name:")+span').text.strip()
    first_name = name.split()[0]
    last_name = ' '.join(name.split()[1:])
    nickname = soup.select_one('strong:contains("Nickname:")+span').text.strip()
    dob = soup.select_one('strong:contains("Age")+span').text.strip()
    dod = None
    nationality = "NULL"
    weight_class = soup.select_one('strong:contains("Weight Class") + span').text.strip()
    last_weightIn = soup.select_one('strong:contains("Last Weigh-In:") + span').text.strip()
    height = re.search('(\d+cm)', soup.select_one('strong:contains("Height:") + span').text.strip())[0].replace("cm", '')
    reach = re.search('(\d+cm)', soup.select_one('strong:contains("Reach:") + span').text.strip())[0].replace("cm", '')
    birth_loc = soup.select_one('strong:contains("Born") + span').text.strip()
    current_streak = soup.select_one('strong:contains("Current Streak") + span').text.strip()
    last_fight = soup.select_one('strong:contains("Last Fight") + span').text.strip()
    current_loc = soup.select_one('strong:contains("Fighting out of") + span').text.strip()
    biography = fighter_link
    try:
        affiliation = soup.select_one('strong:contains("Affiliation")+span').text.strip()
        affiliation_link = soup.find("div", class_="fighterGymListName").find("a").get('href')
    except AttributeError:
        affiliation = None
        affiliation_link = None
    try:
        record = soup.select_one('strong:contains("Pro MMA Record:") + span').text.strip().split()
    except AttributeError:
        record = soup.select_one('strong:contains("Amateur MMA Record:") + span').text.strip().split()
    rec = re.search('(\d+-\d+-\d+)', record[0])[0]
    win = rec.split('-')[0]
    lose = rec.split('-')[1]
    draw = rec.split('-')[2]
    nc = re.search('(\d)', record[1])[0] if re.search('(\d)', record[1]) else 0
    newRowInfo = [id, fid, name, last_name, first_name, nickname, dob, dod, weight_class, last_weightIn, height, reach,
                  birth_loc, current_loc, current_streak, last_fight, affiliation, win, lose, draw, nc, biography]
    print(newRowInfo)
    data_fighters.append(newRowInfo)
    # df_fighters = pd.DataFrame(data_fighters, columns=['id','fid', 'name', 'last_name', 'first_name', 'nickname', 'dob',
    #                                                    'dod', 'weight_class', 'last_weightIn', 'height', 'reach',
    #                                                    'birth_loc', 'current_loc', 'current_streak', 'last_fight',
    #                                                    'affiliation', 'win', 'lose', 'draw', 'nc', 'biography'])
    # df_fighters.to_csv("fighter_info.csv", index=True, mode='a')
    return id

def run():
    events_list_url = "https://www.tapology.com/fightcenter?group=ufc&page={page}&region=&schedule=results"
    response = requests.get(events_list_url)
    soup = BeautifulSoup(response.text,features="html.parser")
    #event_links = [event['href'] for event in soup.select(".fightcenterEvents .left .promotion .name a[href]")]
    for event in soup.find_all('section', class_='fcListing'):
        # field 'sport' in bout data
        sport = event.find("div", {"class": "geography"}).find("span", {"class": "sport"}).text.strip()
        event_link = event.find("span", {"class": "name"}).find("a").get('href')
        event_response = requests.get(joinurl(event_link), headers=headers)
        event_soup = BeautifulSoup(event_response.text, features="html.parser")
        try:
            event_id = getEventInfo(event_soup)
        except AttributeError:
            pass

        try:
            li_bouts = event_soup.find('ul', class_='fightCard').find_all('li')
        except AttributeError:
            pass

        for li_bout in li_bouts:
            bout_link = li_bout.select(".fightCardMatchup a[href]")[0].get("href")
            bout_response = requests.get(joinurl(bout_link), headers=headers)
            bout_soup = BeautifulSoup(bout_response.text, features="html.parser")
            try:
                getEventBoutInfo(li_bout, event_id)
            except AttributeError:
                pass
            try:
                getBoutInfo(bout_soup, event_id)
            except AttributeError:
                pass

run()

df_events = pd.DataFrame(data_events,
                            columns=['event_id', 'name', 'sub_name', 'aka', 'venue',
                                     'location', 'promotion', 'ownership', 'co_promotion', 'tv_ratings',
                                     'tv_announcers', 'ring_announcer', 'post_fight_interviews', 'ppv_buys_buyrate',
                                     'ticket_revenue_lg', 'us_broadcast', 'prelims', 'tournament', 'attendance', 'matchmaker',
                                     'event_date', 'timezone', 'enclosure', 'mma_bouts', 'grappling_bouts', 'status'])
df_events.to_csv("fighter_events.csv", index=True, mode='w')

df_bouts = pd.DataFrame(data_bouts,
                                 columns=['event_id', 'bout_id', 'event_date', 'fighter_id', 'opponent_id',
                                          'result', 'status', 'cancellation_reason', 'weight_class', 'scheduled_weight',
                                          'rb_bout', 'rb_bout_opponent', 'title_fight', 'referee', 'referee_id', 'amateur',
                                          'on_site', 'tournament', 'tournament_round', 'disputed', 'otn_fight', 'otn_knockout',
                                          'otn_submission', 'otn_performance', 'injuries_sustained'])
df_bouts.to_csv("fighter_bouts.csv", index=True, mode='w')

df_event_bouts = pd.DataFrame(data_event_bouts, columns=['event_id', 'bout_position', 'billing', 'fn_method', 'fn_move',
                                                         'round_stucture', 'total_rounds', 'total_fight_time',
                                                         'final_round', 'final_round_time'])
df_event_bouts.to_csv("event_bouts.csv", index=True, mode='w')

df_fighters = pd.DataFrame(data_fighters, columns=['id','fid', 'name', 'last_name', 'first_name', 'nickname', 'dob',
                                                       'dod', 'weight_class', 'last_weightIn', 'height', 'reach',
                                                       'birth_loc', 'current_loc', 'current_streak', 'last_fight',
                                                       'affiliation', 'win', 'lose', 'draw', 'nc', 'biography'])
df_fighters.to_csv("fighter_info.csv", index=True, mode='w')



