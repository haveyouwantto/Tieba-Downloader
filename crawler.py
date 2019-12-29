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


img = 0
emotions = []


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
            filename = "{0}.jpg".format(img)
            imagedownload.download_image(
                j.attrs['src'], os.path.join(folder, postimgdir, filename))
            img += 1
            j.attrs['src'] = postimgdir + filename

        # 自定义表情包
        for j in innerSoup.find_all(class_="BDE_Meme"):
            filename = "{0}.jpg".format(img)
            imagedownload.download_image(
                j.attrs['src'], os.path.join(folder, postimgdir, filename))
            img += 1
            j.attrs['src'] = postimgdir + filename

        # 默认表情
        for j in innerSoup.find_all(class_="BDE_Smiley"):
            filename = os.path.basename(j.attrs['src']).split('?')[0]
            if filename not in emotions:
                imagedownload.download_smiley(
                    j.attrs['src'], os.path.join(folder, smileydir, filename))
                emotions.append(filename)
            j.attrs['src'] = smileydir + filename
        return str(innerSoup)
    else:
        return content


def convert_link(content, folder, postimgdir, smileydir):
    if content == None:
        return

    if '<a' in content:
        innerSoup = BeautifulSoup(
            content, "html.parser")

        # 链接
        for j in innerSoup.find_all(class_="j-no-opener-url"):
            print('转换链接: '+j.attrs['href'])
            j.attrs['href'] = "redirect.html?url=" + \
                urllib.parse.quote(j.text)

        # @人
        for j in innerSoup.find_all(class_="at"):
            print('转换@人: '+j.attrs['href'])
            j.attrs['href'] = 'http://tieba.baidu.com/home/main?un=' + \
                j.attrs['username']
        return str(innerSoup)
    else:
        return content


def getinnerhtml(data):
    return data[data.find(">")+1:data.rfind("</")]


def download(no, see_lz, max_page):
    thread = {
        'pages': []
    }
    usernames = []
    smiley = []

    timere = r'\d\d\d\d-\d\d-\d\d \d\d:\d\d'

    page = 1

    def mkdir(path):
        if not os.path.exists(path):
            os.makedirs(path)

    folder = "saved/"+str(no) + "/"
    imagedir = "img/"
    postimgdir = imagedir + "posts/"
    avatardir = imagedir + "avatars/"
    smileydir = imagedir + "smiley/"
    mkdir(folder)
    mkdir(folder + imagedir)
    mkdir(folder + postimgdir)
    mkdir(folder + avatardir)
    mkdir(folder + smileydir)

    while page <= max_page:
        posts = []
        url = 'https://tieba.baidu.com/p/{0}?see_lz={1}&pn={2}'.format(
            no, see_lz, page)
        print('正在下载第' + str(page) + '页')
        r = requests.get(url)
        response = r.text  # 服务器返回响应

        soup = BeautifulSoup(response, "html.parser")

        thread['title'] = soup.select('#j_core_title_wrap > h3')[
            0].attrs['title']

        floor = 0
        timetxt = soup.find_all(class_='tail-info')
        time = re.findall(timere, str(timetxt))

        pdata = soup.find_all(class_='l_post l_post_bright j_l_post clearfix')

        for i in range(len(pdata)):
            post = json.loads(pdata[i].attrs['data-field'])

            # 检测发帖人
            username = post['author']['user_name']
            if username not in usernames:
                imagedownload.download_avatar(
                    username, post['author']['portrait'], folder + avatardir + username + '.jpg')
                usernames.append(username)

            # 下载贴子图片
            post['content']['content'] = download_image(
                post['content']['content'], folder, postimgdir, smileydir)

            # 转换贴子链接
            post['content']['content'] = convert_link(
                post['content']['content'], folder, postimgdir, smileydir)

            post['comments'] = None

            post['time'] = time[i]

            posts.append(post)

        print('获取楼中楼信息...')
        r2 = requests.get(
            'https://tieba.baidu.com/p/totalComment?tid={0}&see_lz={1}&pn={2}'.format(no, see_lz, page))
        response = r2.text  # 服务器返回响应

        midfloor = json.loads(response)

        for i in midfloor['data']['comment_list']:
            midpost = midfloor['data']['comment_list'][i]['comment_info']

            for j in range(len(midpost)):
                element = midpost[j]
                element['content'] = download_image(
                    element['content'], folder, postimgdir, smileydir)

                # 转换贴子链接
                element['content'] = convert_link(
                    element['content'], folder, postimgdir, smileydir)

                midpost[j] = element

            midfloor['data']['comment_list'][i]['comment_info'] = midpost

            for j in range(len(posts)):
                element = posts[j]
                if element['content']['post_id'] == int(i):
                    print('添加id为{0}的楼中楼回复'.format(i))
                    posts[j]['comments'] = midfloor['data']['comment_list'][i]
                    posts[j]['comments']['comment_info'] = [
                        posts[j]['comments']['comment_info']]

                    midpages = math.ceil(
                        midfloor['data']['comment_list'][i]['comment_num']/midfloor['data']['comment_list'][i]['comment_list_num'])

                    if(midpages > 1):
                        for midpage in range(2, midpages+1):
                            print('正在下载第{0}页的楼中楼{1}页'.format(page, midpage))
                            r3 = requests.get(
                                'https://tieba.baidu.com/p/comment?tid={0}&pid={1}&pn={2}'.format(no, i, midpage))
                            soup2 = BeautifulSoup(r3.text, "html.parser")

                            username2 = soup2.find_all(
                                class_='lzl_single_post j_lzl_s_p first_no_border')
                            username2.extend(soup2.find_all(
                                class_='lzl_single_post j_lzl_s_p'))
                            content = soup2.find_all(class_='lzl_content_main')
                            time2 = soup2.find_all(class_='lzl_time')

                            posts[j]['comments']['comment_info'].append([])

                            for k in range(len(username2)):
                                rep = {
                                    "thread_id": no,
                                    "post_id": i,
                                    "comment_id": None,
                                    "username": None,
                                    "user_id": None,
                                    "now_time": None,
                                    "content": None,
                                }
                                rep['content'] = getinnerhtml(str(content[k]))
                                ud = json.loads(
                                    username2[k].attrs['data-field'])
                                rep['username'] = ud['user_name']
                                rep['comment_id'] = ud['spid']
                                if ud['user_name'] not in usernames:
                                    imagedownload.download_avatar(
                                        ud['user_name'], ud['portrait'], folder + avatardir + ud['user_name'] + '.jpg')
                                    usernames.append(
                                        ud['user_name'])
                                rep['now_time'] = getinnerhtml(str(time2[k]))
                                posts[j]['comments']['comment_info'][midpage-1].append(
                                    rep)

        for i in midfloor['data']['user_list']:

            element = midfloor['data']['user_list'][i]
            username = element['user_name']

            try:
                if username not in usernames:
                    imagedownload.download_avatar(
                        username, element['portrait'], folder + avatardir + username + '.jpg')
                    usernames.append(username)
            except:
                nickname = element['nickname']
                if nickname not in usernames:
                    imagedownload.download_avatar(
                        nickname, element['portrait'], folder + avatardir + nickname + '.jpg')
                    usernames.append(nickname)

        thread['pages'].append(posts)

        page += 1

    # 复制模板文件
    print('复制文件')
    for file in os.listdir('template/'):
        shutil.copyfile('template/' + file, folder + file)

    f = open(folder + 'data.js', 'w')
    f.write('let thread=')
    f.write(json.dumps(thread))
    f.write(';let pn=1;let px=thread.pages.length;document.getElementById("jump").max=px;init(thread);')
    f.close()
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

    download(args.tid, args.see_lz, args.pages)
