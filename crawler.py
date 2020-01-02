import json
import os
import shutil
import urllib.parse
import argparse
import re
import math

import imagedownload

from bs4 import BeautifulSoup
import requests
import colorama
from colorama import Fore, Back, Style

img = 0
emotions = []
usernames = []
colorama.init()


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def download_image(content, folder, postimgdir, smileydir):
    global img
    global emotions
    if content == None:
        return
    if '<img' in content:
        innerSoup = BeautifulSoup(
            content, "html.parser")

        # 图片
        for j in innerSoup.find_all(class_="BDE_Image"):
            try:
                print('下载贴子图片: '+j['src']+'... ', end='')
                filename = "{0}.jpg".format(img)
                imagedownload.download_image(
                    j['src'], os.path.join(folder, postimgdir, filename))
                img += 1
                j['src'] = postimgdir + filename
                print(Fore.GREEN+'SUCCESS'+Fore.WHITE)
            except:
                print(Fore.RED+'FAILED'+Fore.WHITE)

        # 自定义表情包
        for j in innerSoup.find_all(class_="BDE_Meme"):
            try:
                print('下载贴子图片: '+j['src']+'... ', end='')
                filename = "{0}.jpg".format(img)
                imagedownload.download_image(
                    j['src'], os.path.join(folder, postimgdir, filename))
                img += 1
                j['src'] = postimgdir + filename
                print(Fore.GREEN+'SUCCESS'+Fore.WHITE)
            except:
                print(Fore.RED+'FAILED'+Fore.WHITE)

        # 默认表情
        for j in innerSoup.find_all(class_="BDE_Smiley"):
            try:
                print('下载表情... ', end='')
                filename = os.path.basename(j['src']).split('?')[0]
                if filename not in emotions:
                    imagedownload.download_smiley(
                        j['src'], os.path.join(folder, smileydir, filename))
                    emotions.append(filename)
                j['src'] = smileydir + filename
                print(Fore.GREEN+'SUCCESS'+Fore.WHITE)
            except:
                print(Fore.RED+'FAILED'+Fore.WHITE)
        return str(innerSoup)
    else:
        return content


def download_avatar(username, portrait, folder, avatardir):
    global usernames

    if username not in usernames:
        try:
            print('下载'+username+'的头像... ', end='')
            imagedownload.download_avatar(
                username, portrait, folder + avatardir + username + '.jpg')
            usernames.append(
                username)
            print(Fore.GREEN+'SUCCESS'+Fore.WHITE)
        except:
            print(Fore.RED+'FAILED'+Fore.WHITE)


def convert_link(content, folder, postimgdir, smileydir):
    if content == None:
        return

    if '<a' in content:
        innerSoup = BeautifulSoup(
            content, "html.parser")

        # 链接
        for j in innerSoup.find_all(class_="j-no-opener-url"):
            print('转换链接: ' + j['href']+'... ', end='')
            j['href'] = "redirect.html?url=" + \
                        urllib.parse.quote(j.text)
            print(Fore.GREEN+'SUCCESS'+Fore.WHITE)

        # @人
        for j in innerSoup.find_all(class_="at"):
            print('转换@人: ' + j['href']+'... ', end='')
            del j['onclick']
            del j['onmouseout']
            del j['onmouseover']
            if j['username'] == '':
                j['href'] = 'http://tieba.baidu.com/home/main?un=' + \
                            j.contents[0].string
            else:
                j['href'] = 'http://tieba.baidu.com/home/main?un=' + \
                            j['username']
            print(Fore.GREEN+'SUCCESS'+Fore.WHITE)
        return str(innerSoup)
    else:
        return content


def getinnerhtml(data):
    try:
        return data[data.find(">") + 1:data.rfind("</")]
    except:
        return ""


class Downloader:
    def __init__(self, tid, see_lz, max_page):
        self.tid = tid
        self.see_lz = see_lz
        self.max_page = max_page

        self.thread = {
            'pages': []
        }
        self.usernames = []
        self.smiley = []

        self.timere = r'\d\d\d\d-\d\d-\d\d \d\d:\d\d'

        self.page = 1

        self.folder = "saved/" + str(self.tid) + "/"
        self.imagedir = "img/"
        self.postimgdir = self.imagedir + "posts/"
        self.avatardir = self.imagedir + "avatars/"
        self.smileydir = self.imagedir + "smiley/"
        mkdir(self.folder)
        mkdir(self.folder + self.imagedir)
        mkdir(self.folder + self.postimgdir)
        mkdir(self.folder + self.avatardir)
        mkdir(self.folder + self.smileydir)

    def download(self):
        while self.page <= self.max_page:
            p = None
            for retry in range(3):
                try:
                    print('正在下载第' + str(self.page) + '页... ', end='')
                    p = self.getBasePage(self.page)
                    print(Fore.GREEN+'SUCCESS'+Fore.WHITE)
                    break
                except:
                    print(Fore.RED+'FAILED'+Fore.WHITE)

            for retry in range(3):
                try:
                    print('获取楼中楼信息... ', end='')
                    self.getMidPosts(p)
                    print(Fore.GREEN+'SUCCESS'+Fore.WHITE)
                    break
                except:
                    print(Fore.RED+'FAILED'+Fore.WHITE)

            self.thread['pages'].append(p)
            self.page += 1

    def getBasePage(self, page):
        posts = []
        url = 'https://tieba.baidu.com/p/{0}?see_lz={1}&pn={2}'.format(
            self.tid, self.see_lz, page)

        r = requests.get(url)
        response = r.text  # 服务器返回响应
        soup = BeautifulSoup(response, "html.parser")

        self.thread['title'] = soup.select(
            '#j_core_title_wrap > h3')[0]['title']

        floor = 0
        timetxt = soup.find_all(class_='tail-info')
        time = re.findall(self.timere, str(timetxt))

        pdata = soup.find_all(
            class_='l_post l_post_bright j_l_post clearfix')

        print(Fore.GREEN+'SUCCESS'+Fore.WHITE)

        for i in range(len(pdata)):
            post = json.loads(pdata[i]['data-field'])

            # 检测发帖人
            username = post['author']['user_name']

            download_avatar(
                username, post['author']['portrait'], self.folder, self.avatardir)

            # 下载贴子图片
            post['content']['content'] = download_image(
                post['content']['content'], self.folder, self.postimgdir, self.smileydir)

            # 转换贴子链接
            post['content']['content'] = convert_link(
                post['content']['content'], self.folder, self.postimgdir, self.smileydir)

            post['comments'] = None

            post['time'] = time[i]

            posts.append(post)

        return posts

    def getMidPosts(self, posts):
        r2 = requests.get(
            'https://tieba.baidu.com/p/totalComment?tid={0}&see_lz={1}&pn={2}'.format(self.tid, self.see_lz, self.page))
        response = r2.text  # 服务器返回响应

        midfloor = json.loads(response)

        print(Fore.GREEN+'SUCCESS'+Fore.WHITE)

        for i in midfloor['data']['comment_list']:
            midpost = midfloor['data']['comment_list'][i]['comment_info']

            for j in range(len(midpost)):
                element = midpost[j]
                element['content'] = download_image(
                    element['content'], self.folder, self.postimgdir, self.smileydir)

                # 转换贴子链接
                element['content'] = convert_link(
                    element['content'], self.folder, self.postimgdir, self.smileydir)

                midpost[j] = element

            midfloor['data']['comment_list'][i]['comment_info'] = midpost

            for j in range(len(posts)):
                element = posts[j]
                if element['content']['post_id'] == int(i):
                    print('添加id为{0}的楼中楼回复... '.format(i), end='')
                    posts[j]['comments'] = midfloor['data']['comment_list'][i]
                    posts[j]['comments']['comment_info'] = [
                        posts[j]['comments']['comment_info']]

                    print(Fore.GREEN+'SUCCESS'+Fore.WHITE)

                    midpages = math.ceil(
                        midfloor['data']['comment_list'][i]['comment_num'] / midfloor['data']['comment_list'][i][
                            'comment_list_num'])

                    if (midpages > 1):
                        for midpage in range(2, midpages + 1):
                            print('正在下载第{0}页的楼中楼{1}页... '.format(
                                self.page, midpage), end='')
                            for retry2 in range(3):
                                try:
                                    r3 = requests.get(
                                        'https://tieba.baidu.com/p/comment?tid={0}&pid={1}&pn={2}'.format(self.tid, i,
                                                                                                          midpage))
                                    soup2 = BeautifulSoup(
                                        r3.text, "html.parser")

                                    username2 = soup2.find_all(
                                        class_='lzl_single_post j_lzl_s_p first_no_border')
                                    username2.extend(soup2.find_all(
                                        class_='lzl_single_post j_lzl_s_p'))
                                    content = soup2.find_all(
                                        class_='lzl_content_main')
                                    time2 = soup2.find_all(
                                        class_='lzl_time')

                                    posts[j]['comments']['comment_info'].append(
                                        [])

                                    for k in range(len(username2)):
                                        rep = {
                                            "thread_id": self.tid,
                                            "post_id": i,
                                            "comment_id": None,
                                            "username": None,
                                            "user_id": None,
                                            "now_time": None,
                                            "content": None,
                                        }
                                        rep['content'] = getinnerhtml(
                                            str(content[k]))

                                        rep['content'] = download_image(
                                            rep['content'], self.folder, self.postimgdir, self.smileydir)

                                        # 转换贴子链接
                                        rep['content'] = convert_link(
                                            rep['content'], self.folder, self.postimgdir, self.smileydir)

                                        ud = json.loads(
                                            username2[k]['data-field'])
                                        rep['username'] = ud['user_name']
                                        rep['comment_id'] = ud['spid']
                                        download_avatar(
                                            ud['user_name'], ud['portrait'], self.folder, self.avatardir)
                                        rep['now_time'] = getinnerhtml(
                                            str(time2[k]))
                                        posts[j]['comments']['comment_info'][midpage - 1].append(
                                            rep)
                                    print(Fore.GREEN +
                                          'SUCCESS'+Fore.WHITE)
                                    break
                                except:
                                    print(Fore.RED+'FAILED'+Fore.WHITE)

        for i in midfloor['data']['user_list']:

            try:

                element = midfloor['data']['user_list'][i]
                username = element['user_name']

                try:
                    download_avatar(
                        username, element['portrait'], self.folder, self.avatardir)
                except:
                    nickname = element['nickname']
                    download_avatar(
                        nickname, element['portrait'], self.folder, self.avatardir)

            except:
                pass

    def save(self):

        # 复制模板文件
        print('复制文件... ', end='')
        for file in os.listdir('template/'):
            shutil.copyfile('template/' + file, self.folder + file)

        f = open(self.folder + 'data.js', 'w')
        f.write('let thread=')
        f.write(json.dumps(self.thread))
        f.write(
            ';let pn=1;let px=thread.pages.length;document.getElementById("jump").max=px;init(thread);')
        f.close()
        print(Fore.GREEN+'SUCCESS'+Fore.WHITE)
        print('下载完成')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tid', type=str,
                        help='thread id', required=True)
    parser.add_argument('-s', '--see_lz', type=int,
                        help='see lz. 0 or 1. default=0.', default=0)
    parser.add_argument('-p', '--pages', type=int,
                        help='pages to download. default=1.', default=1)
    args = parser.parse_args()

    dl = Downloader(args.tid, args.see_lz, args.pages)
    dl.download()
    dl.save()
