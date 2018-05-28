import requests
import sys
from time import sleep
from random import randint
from datetime import datetime
from dateutil.parser import parse
from bs4 import BeautifulSoup


class SocialbladeProcessor(object):
    def __init__(self, entity, log, retry=3):
        self.log = log
        self.retry = retry
        self.entity = entity
        self.base_url = "https://socialblade.com"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    def _make_request(self, url):
        retries = 0
        while retries <= self.retry:
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                return response
            except requests.exceptions.HTTPError as e:
                self.log.info("{}".format(e))
                sleep(30)
                break
            except Exception as e:
                self.log.info("{}: Failed to make request on try {}".format(e, retries))
                retries += 1
                if retries <= self.retry:
                    self.log.info("Trying again!")
                    continue
                else:
                    sys.exit("Max retries reached")

    def _get_users(self):
        self.info = []
        response = self._make_request(self.base_url + "/youtube/top/50")
        soup = BeautifulSoup(response.content, "html.parser")
        wrapper = soup.find_all("div", attrs={"style": "float: left; width: 350px; line-height: 25px;"})
        for creator in wrapper:
            a = creator.find("a", href=True)
            try:
                user_data = self._get_user_info(a["href"])
                self.info.append(user_data)
                sleep(randint(4, 10))
            except Exception as e:
                self.log.info("Failed to fetch creator: {}".format(e))
        self.entity.save(users=self.info)

    def _get_user_info(self, url):
        user_data = dict()
        response = self._make_request(self.base_url + url)
        soup = BeautifulSoup(response.content, "html.parser")
        top_info = soup.find("div", {"id": "YouTubeUserTopInfoBlockTop"})
        user_data["date"] = datetime.now().strftime("%Y-%m-%d")
        user_data["name"] = top_info.find("h1").text
        user_data["uploads"] = int(top_info.find("span", {"id": "youtube-stats-header-uploads"}).text)
        user_data["subscribers"] = int(top_info.find("span", {"id": "youtube-stats-header-subs"}).text)
        user_data["video_views"] = int(top_info.find("span", {"id": "youtube-stats-header-views"}).text)
        user_data["country"] = top_info.find("a", {"id": "youtube-user-page-country"}).text
        user_data["channel_type"] = top_info.find("a", {"id": "youtube-user-page-channeltype"}).text
        uc_div = top_info.find_all("div", {"class": "YouTubeUserTopInfo"})[-1]
        date_tmp = parse(uc_div.find("span", attrs={"style": "font-weight: bold;"}).text)
        user_data["user_created"] = date_tmp.strftime("%Y-%m-%d")
        user_data["total_grade"] = soup.find("span", {"id": "afd-header-total-grade"}).text
        s_rank = soup.find("p", {"id": "afd-header-subscriber-rank"}).text
        user_data["subscriber_rank"] = int(s_rank.replace(",", "").replace("st", "").replace("nd", "").replace("rd", "").replace("th", ""))
        v_rank = soup.find("p", {"id": "afd-header-videoview-rank"}).text
        user_data["video_view_rank"] = int(v_rank.replace(",", "").replace("st", "").replace("nd", "").replace("rd", "").replace("th", ""))
        sb_rank = soup.find("p", {"id": "afd-header-sb-rank"}).text
        user_data["socialblade_rank"] = int(sb_rank.replace(",", "").replace("st", "").replace("nd", "").replace("rd", "").replace("th", ""))
        v_days = soup.find("span", {"id": "afd-header-views-30d"}).text
        user_data["views_for_he_last_30_days"] = int(v_days.replace(",", ""))
        s_days = soup.find("span", {"id": "afd-header-subs-30d"}).text
        user_data["subscribers_for_he_last_30_days"] = int(s_days.replace(",", ""))

        social_list = soup.find("div", {"id": "YouTubeUserTopSocial"})
        for a in social_list.find_all("a", href=True):
            url = a["href"]
            if "youtube" in url:
                user_data["youtube_url"] = url
            if "facebook" in url:
                user_data["facebook_url"] = url
            if "twitter" in url:
                user_data["twitter_url"] = url
            if "instagram" in url:
                user_data["instagram_url"] = url
            if "google" in url:
                user_data["google_plus_url"] = url

        self.log.info(user_data)
        return user_data

    def _get_user_link(self, url):
        response = self._make_request(url)
        soup = BeautifulSoup(response.content, "html.parser")
        div = soup.find("div", attrs={"style": "width: 1200px; height: 88px; background: #fff; padding: 15px 30px; margin: 2px auto; border-bottom: 2px solid #e4e4e4;"})
        url = div.find("a", href=True)
        return url

    def fetch(self):
        self.log.info('Making request to Socialblade for daily creators export')
        self._get_users()
        return self
