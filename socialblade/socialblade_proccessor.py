import requests
import sys
from time import sleep
from random import randint
from datetime import datetime
from dateutil.parser import parse
from bs4 import BeautifulSoup

# "/youtube/top/100",
# "/twitch/top/100/followers",
# "/twitch/top/100/channelviews",
# "/instagram/top/100/followers",
# "/instagram/top/100/following",
# "/instagram/top/100/media",
# "/twitter/top/100/followers",
# "/twitter/top/100/tweets",
# "/twitter/top/100/engagements",
LINKS = [
         "/mixer/top/100/most-followers",
         "/mixer/top/100/most-viewed",
         "/mixer/top/100/highest-level"]

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
        for link in LINKS:
            response = self._make_request(self.base_url + link)
            soup = BeautifulSoup(response.content, "html.parser")
            if "youtube" in link:
                wrapper = soup.find_all("div", attrs={"style": "float: left; width: 350px; line-height: 25px;"})
                for creator in wrapper:
                    a = creator.find("a", href=True)
                    url = a["href"]
                    url = self.base_url + url.replace(" ", "")
                    try:
                        user_data = self._get_youtube_user_info(url)
                        self.info.append(user_data)
                        sleep(randint(4, 10))
                    except Exception as e:
                        self.log.info("Failed to fetch youtube creator: {}".format(e))
            elif "twitch" in link:
                wrapper = soup.find("div", attrs={"class": "content-module-wide"})
                users = wrapper.find_all("a", href=True)
                for user in users:
                    try:
                        url = self.base_url + user["href"]
                        user_data = self._get_twitch_user_info(url)
                        self.info.append(user_data)
                        sleep(randint(4, 10))
                    except Exception as e:
                        self.log.info("Failed to fetch youtube creator: {}".format(e))
            elif "instagram" in link:
                wrapper = soup.find("div", attrs={"class": "content-module-wide"})
                users = wrapper.find_all("a", href=True)
                for user in users:
                    try:
                        url = self.base_url + user["href"]
                        user_data = self._get_instagram_user_info(url)
                        self.info.append(user_data)
                        sleep(randint(4, 10))
                    except Exception as e:
                        self.log.info("Failed to fetch youtube creator: {}".format(e))
            elif "twitter" in link:
                wrapper = soup.find("div", attrs={"class": "content-module-wide"})
                users = wrapper.find_all("a", href=True)
                for user in users:
                    try:
                        url = self.base_url + user["href"]
                        user_data = self._get_twitter_user_info(url)
                        self.info.append(user_data)
                        sleep(randint(4, 10))
                    except Exception as e:
                        self.log.info("Failed to fetch youtube creator: {}".format(e))
            elif "mixer" in link:
                users = soup.find_all("div", attrs={"style": "float: left; width: 270px; line-height: 25px;"})
                for user in users:
                    try:
                        user_link = user.find("a", href=True)
                        url = self.base_url + user_link["href"]
                        user_data = self._get_mixer_user_info(url)
                        self.info.append(user_data)
                        sleep(randint(4, 10))
                    except Exception as e:
                        self.log.info("Failed to fetch youtube creator: {}".format(e))
            # self.entity.save(users=self.info)

    def _get_mixer_user_info(self, url):
        user_data = dict()
        response = self._make_request(url)
        soup = BeautifulSoup(response.content, "html.parser")
        top_info = soup.find("div", {"id": "YouTubeUserTopInfoBlock"})
        user_data["platform"] = "mixer"
        user_data["date"] = datetime.now().strftime("%Y-%m-%d")
        screen_name = url.split("/")[-1]
        followers = top_info.find("span", text="Followers").find_next_sibling("span").text
        total_views = top_info.find("span", text="Total Views").find_next_sibling("span").text
        level = top_info.find("span", text="Level").find_next_sibling("span").text
        sparks = top_info.find("span", text="Sparks").find_next_sibling("span").text
        language = top_info.find("span", text="Language").find_next_sibling("span").text
        audience = top_info.find("span", text="Audience").find_next_sibling("span").text
        user_created = parse(top_info.find("span", text="User Created").find_next_sibling("span").text)
        user_data["name"] = screen_name
        user_data["followers"] = self._get_numeric_value(followers)
        user_data["total_views"] = self._get_numeric_value(total_views)
        user_data["level"] = self._get_numeric_value(level)
        user_data["sparks"] = self._get_numeric_value(sparks)
        user_data["language"] = language.strip().replace("\n", "")
        user_data["audience"] = audience.strip().replace("\n", "")
        user_data["user_created"] = user_created.strftime("%Y-%m-%d")
        user_data["total_grade"] = soup.find("p", text="TOTAL GRADE").find_previous_sibling("p").text.strip().replace("\n", "")
        user_data["follower_rank"] = self._get_numeric_value(soup.find("p", text="FOLLOWER RANK").find_previous_sibling("p").text)
        user_data["views_rank"] = self._get_numeric_value(soup.find("p", text="VIEWS RANK").find_previous_sibling("p").text)
        user_data["level_rank"] = self._get_numeric_value(soup.find("p", text="LEVEL RANK").find_previous_sibling("p").text)
        self.log.info(user_data)
        return user_data

    def _get_twitter_user_info(self, url):
        user_data = dict()
        response = self._make_request(url)
        soup = BeautifulSoup(response.content, "html.parser")
        top_info = soup.find("div", {"id": "YouTubeUserTopInfoBlockTop"})
        user_data["platform"] = "twitter"
        user_data["date"] = datetime.now().strftime("%Y-%m-%d")
        screen_name = url.split("/")[-1]
        followers = top_info.find("span", text="Followers").find_next_sibling("span").text
        following = top_info.find("span", text="Following").find_next_sibling("span").text
        likes = top_info.find("span", text="Likes").find_next_sibling("span").text
        tweets = top_info.find("span", text="Tweets").find_next_sibling("span").text
        user_created = parse(top_info.find("span", text="User Created").find_next_sibling("span").text)
        user_data["name"] = screen_name
        user_data["followers"] = self._get_numeric_value(followers)
        user_data["following"] = self._get_numeric_value(following)
        user_data["likes"] = self._get_numeric_value(likes)
        user_data["tweets"] = self._get_numeric_value(tweets)
        user_data["user_created"] = user_created.strftime("%Y-%m-%d")
        user_data["total_grade"] = soup.find("p", text="TOTAL GRADE").find_previous_sibling("p").text.strip().replace("\n", "")
        user_data["follower_rank"] = self._get_numeric_value(soup.find("p", text="FOLLOWER RANK").find_previous_sibling("p").text)
        user_data["avg_retweets"] = self._get_numeric_value(soup.find("p", text="AVERAGE RETWEETS").find_previous_sibling("p").text)
        user_data["avg_likes"] = self._get_numeric_value(soup.find("p", text="AVERAGE LIKES").find_previous_sibling("p").text)
        self.log.info(user_data)
        return user_data

    def _get_instagram_user_info(self, url):
        user_data = dict()
        response = self._make_request(url)
        soup = BeautifulSoup(response.content, "html.parser")
        user_data["platform"] = "instagram"
        user_data["date"] = datetime.now().strftime("%Y-%m-%d")
        screen_name = url.split("/")[-1]
        user_data["name"] = screen_name
        top_info = soup.find("div", {"id": "stats-top-data-module-wrap"})
        summary = soup.find("div", {"id": "twitch-summary-wrap"})
        followers = top_info.find("div", text="Followers").find_next_sibling("div").text
        following = top_info.find("div", text="Following").find_next_sibling("div").text
        pictures_uploaded = top_info.find("div", text="Pictures Uploaded").find_next_sibling("div").text
        avg_folloers = top_info.find("div", text="Avg Daily Followers").find_next_sibling("div").text
        instagram_id = top_info.find("div", text="Instagram ID").find_next_sibling("div").text
        socialblade_rank = summary.find("div", text="SB Rank").find_previous_sibling("div").text
        user_data["followers"] = self._get_numeric_value(followers)
        user_data["following"] = self._get_numeric_value(following)
        user_data["pictures_uploaded"] = self._get_numeric_value(pictures_uploaded)
        user_data["avg_daily_followers"] = self._get_numeric_value(avg_folloers)
        user_data["instagram_id"] = self._get_numeric_value(instagram_id)
        user_data["total_grade"] = summary.find("div", text="Rank").find_previous_sibling("div").text.strip().replace("\n", "")
        user_data["socialblade_rank"] = self._get_numeric_value(socialblade_rank)
        user_data["followers_in_30_days"] = int(summary.find_all("span", {"style": "color:#41a200; font-weight: bold; padding-left: 5px;"})[0].text)
        user_data["media_uploaded_in_30_days"] = int(summary.find_all("span", {"style": "color:#41a200; font-weight: bold; padding-left: 5px;"})[1].text)
        self.log.info(user_data)
        return user_data

    def _get_twitch_user_info(self, url):
        user_data = dict()
        response = self._make_request(url)
        soup = BeautifulSoup(response.content, "html.parser")
        user_data["platform"] = "twitch"
        user_data["date"] = datetime.now().strftime("%Y-%m-%d")
        screen_name = url.split("/")[-1]
        user_data["name"] = screen_name
        top_info = soup.find("div", {"style": "width: 360px; float: left; background: #fff;"}).find_all("p")
        followers = top_info[1].text.split("followers")[0]
        views = top_info[2].text.split("channel views")[0]
        views_rank = soup.find("p", text="FOLLOWER RANK").find_previous_sibling("p").text
        followers_rank = soup.find("p", text="VIEWS RANK").find_previous_sibling("p").text
        user_data["total_grade"] = top_info[0].text.strip().replace("\n", "")
        user_data["followers"] = self._get_numeric_value(followers)
        user_data["views"] = self._get_numeric_value(views)
        user_data["views_rank"] = self._get_numeric_value(views_rank)
        user_data["followers_rank"] = self._get_numeric_value(followers_rank)
        user_data["twitch_url"] = "https://twitch.tv/{}".format(screen_name)
        self.log.info(user_data)
        return user_data

    def _get_youtube_user_info(self, url):
        user_data = dict()
        response = self._make_request(url)
        if "Search Results" in response.text:
            soup = BeautifulSoup(response.content, "html.parser")
            wrapper = soup.find_all("div", attrs={"style": "width: 800px; height: 88px; float: left; position: relative;"})
            url = wrapper[0].find("a", href=True)
            response = self._make_request(self.base_url + url["href"])
        soup = BeautifulSoup(response.content, "html.parser")
        top_info = soup.find("div", {"id": "YouTubeUserTopInfoBlockTop"})
        user_data["platform"] = "youtube"
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
        user_data["subscriber_rank"] = self._get_numeric_value(s_rank)
        v_rank = soup.find("p", {"id": "afd-header-videoview-rank"}).text
        user_data["video_view_rank"] = self._get_numeric_value(v_rank)
        sb_rank = soup.find("p", {"id": "afd-header-sb-rank"}).text
        user_data["socialblade_rank"] = self._get_numeric_value(sb_rank)
        v_days = soup.find("span", {"id": "afd-header-views-30d"}).text
        user_data["views_for_he_last_30_days"] = self._get_numeric_value(v_days)
        s_days = soup.find("span", {"id": "afd-header-subs-30d"}).text
        user_data["subscribers_for_he_last_30_days"] = self._get_numeric_value(s_days)
        earnings = soup.find_all("p", {"style": "font-size: 1.4em; color:#41a200; font-weight: 600; padding-top: 20px;"})
        user_data["estimated_monthly_earnings"] = earnings[0].text.strip()
        user_data["estimated_yearly_earnings"] = earnings[1].text.strip()

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

    def _get_numeric_value(self, text):
        text = text.replace("\n", "").replace(",", "").replace("st", "").replace("nd", "").replace("rd", "")\
            .replace("th", "").strip()
        return int(text)

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
