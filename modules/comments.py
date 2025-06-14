import time
import json
import asyncio

from typing import List,Tuple
from tqdm import tqdm

from utils.requests import requests_get
from models import Comment, User
from utils.convert import bv2av

QUERY_URL = "https://api.bilibili.com/x/v2/reply"
SUB_REPLY_URL = "https://api.bilibili.com/x/v2/reply/reply" 

class CommentsCollector:
    def __init__(self, video_id:int |str, sort=2):
        self.video_id = video_id
        self.sort = sort
        self.queue = asyncio.Queue()
        self.root_comments = []

    def __extract_comments(self, data:list):
        for reply in data:
            rpid = reply['rpid']
            oid = reply['oid']
            user = reply['member']
            content = reply['content']
            text = ''
            if 'at_name_to_mid' in content:
                at_name = list(content['at_name_to_mid'].keys())[0]
                text = content['message'].lstrip(f"回复 @{at_name} :" )
            else:
                text = content['message']

            comment = Comment(
                rpid=rpid,
                oid=oid,
                user=User(uid=user['mid'], name=user['uname']),
                text=text
            )
            self.root_comments.append(comment)

    async def push_comments_tree_queue(self, page:int):
        while True:
            data = await self.queue.get()
            if data is None:
                break
            await self.process_data(data)

    async def process_data(self,data):
        print(f"Processing data for page...")
        # comments, count = extract_comments(data['replies'])


    def __get_comments_by_page(self, page:int) -> List[Comment]:
        """
        获取指定页数的评论
        :param page: 页数
        :return: 评论列表
        """
        if isinstance(self.video_id, str):
            if self.video_id.startswith('BV'):
                self.video_id = bv2av(self.video_id)
            else:
                raise ValueError("Invalid video ID format. Use 'AV' or 'BV' format.")
        params = {
            'oid': self.video_id,
            'pn': page,
            'type': 1,
            'sort': self.sort
        }
        res = requests_get(QUERY_URL, params=params)
        comments,c = extract_comments(res['data']['replies'])
        return comments
    def collect(self):
        get_all_comments(self.video_id, self.sort)

    def get_comments(self) -> List[Comment]:
        return self.root_comments

    def save_to_file(self, filename='comments.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([comment.to_json() for comment in self.root_comments], f, ensure_ascii=False, indent=4)

def get_comments(video_id:int |str, page=1, sort=2):
    '''
    :param video_id 评论区id，视频id
    :param page: 页数
    :param sort: 排序方式，0为按时间排序，2为按热度排序
    :return: 评论列表
    '''
    if isinstance(video_id, str):
        if video_id.startswith('BV'):
            video_id = bv2av(video_id)
        else:
            raise ValueError("Invalid video ID format. Use 'AV' or 'BV' format.")
    params = {
        'oid': video_id,
        'pn': page,
        'type': 1,
        'sort': sort
    }
    res = requests_get(QUERY_URL, params=params)
    return res

def get_all_comments(video_id:int |str, sort=2)-> List[Comment]:
    '''
    :param video_id 评论区id，视频id
    :param sort: 排序方式，0为按时间排序，2为按热度排序
    :return: 评论列表
    '''
    page = 1
    comments= []
    pbar = None
    count = 0
    while True:
        res = get_comments(video_id, page, sort)
        if res['code'] != 0:
            print(f"Warning:",res['message'])
            # raise Exception(f"Error fetching comments: {res['message']}")
            continue
        tip = f"获取{video_id}的评论，第{page}页"
        if pbar is None:
            with open('comments.json', 'w', encoding='utf-8') as f:
                json.dump(res, f, ensure_ascii=False, indent=4)
            # 总页数应根据根评论的总数，但现在的api中acount是所有评论的总数，包括子评论，所以除以20得到的页数会有很大误差
            # 只能选择将评论总数作为进度条的总数，而不是以总页数为进度条的总数
            total_comments = res['data']['page']['acount']
            pbar = tqdm(total=total_comments, desc=tip)
            # 处理置顶评论
            if 'top_replies' in res['data'] and res['data']['top_replies']:
                top_comments, top_sub_comments_count = extract_comments(res['data']['top_replies'])
                comments.extend(top_comments)
                pbar.update(top_sub_comments_count)
                count += top_sub_comments_count


        if res['data']['replies']:
            current_page_comments,current_page_comments_count = extract_comments(res['data']['replies'])
            comments.extend(current_page_comments)
            pbar.update(current_page_comments_count)
            count += current_page_comments_count
            pd = res['data']['page']['num']
            # 检查当前页是否与预期的页号相同，如果不同则打印警告信息
            # 这个检查是为了确保我们没有漏掉任何评论，因为api返回的页号可能与我们期望的不同
            if pd != page:
                print(f"Warning: Page number mismatch. Expected {page}, got {pd}.")
            page += 1
            if count >= 700:
                # 暂停60秒，避免过快过多请求导致风控
                for i in range(61):
                    time.sleep(1)
                    pbar.set_description(f"暂停中...{60-i}s")
                count = 0 
                pbar.set_description(tip) 
        else:
            break

    if pbar:
        pbar.set_description("获取评论完成")
        pbar.close()
    return comments

def extract_comments(data:list)-> Tuple[List[Comment],int]:
    ret = []
    count = 0

    for reply in data:
        rpid = reply['rpid']
        oid = reply['oid']
        user = reply['member']
        content = reply['content']
        text = ''
        if 'at_name_to_mid' in content:
            # If the comment contains mentions, we need to handle it differently
            # Extract the first mention and remove it from the text
            # This is a workaround for the issue where the comment text starts with "回复 @username :"
            # TODO 似乎可能会存在多个at_name_to_mid的情况，没看到具体的例子，发现了再改
            at_name = list(content['at_name_to_mid'].keys())[0]
            text = content['message'].lstrip(f"回复 @{at_name} :" )
        else:
            text = content['message']

        comment = Comment(
            rpid=rpid,
            oid=oid,
            user=User(uid=user['mid'], name=user['uname']),
            text=text
        )
        # 这两个函数怎么在左脚踩右脚
        # 触发风控的大头应该就是在这里，应该在检测到不是根评论时不调用get_comment_tree
        # 子评论应该不会再有子评论了，但replies字段为null时应该不会进入这个分支
        # 因此要考虑不再获取所有子评论
        # 或者考虑使用队列来依次获取，即意味着重构
        if ('replies' in reply) and reply['replies'] and reply['root'] == 0:
            comment.children,c  = get_comment_tree(oid, rpid)
            count += c
        else:
            comment.children = []
        count += 1
        ret.append(comment)
    return ret,count

def get_comment_tree_through_queue(oid:int, root:int) ->List[Comment]:
    """
    获取评论树的子评论
    :param oid: 视频id
    :param root: 根评论id
    :return: 子评论列表
    """
    comments = []
    page = 1
    total_pages = -1
    while total_pages == -1 or page <= total_pages:
        params = {
            'type': 1,
            'oid': oid,
            'root': root,
            'ps': 20,
            'pn': page,
        }
        res = requests_get(SUB_REPLY_URL, params=params)
        if res['code'] != 0:
            raise Exception(f"Error fetching comments: {res['message']}")
        if total_pages == -1:
            total_pages = res['data']['page']['count'] / 20 if res['data']['page']['count'] % 20 == 0 else res['data']['page']['count'] / 20 + 1
        pd = res['data']['page']['num']
        if pd != page:
            print(f"Warning: Sub-comment page number mismatch. Expected {page}, got {pd}.")
        page += 1
        current_page_comments, _ = extract_comments(res['data']['replies'])
        comments.extend(current_page_comments)
    return comments


def get_comment_tree(oid:int,root:int) ->Tuple[List[Comment],int]:
    page = 1
    total_pages = -1
    comments = []
    count = 0
    while total_pages == -1 or page <= total_pages:
        params = {
            'type': 1,
            'oid': oid,
            'root': root,
            'ps': 20,
            'pn': page,
        }
        res = requests_get(SUB_REPLY_URL, params=params)
        with open('sub_comments.json', 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=4)
        if res['code']!= 0:
            raise Exception(f"Error fetching comments: {res['message']}")
        if total_pages == -1:
            total_pages = res['data']['page']['count'] / 20 if res['data']['page']['count'] % 20 == 0 else res['data']['page']['count'] / 20 + 1
        pd = res['data']['page']['num']
        if pd!= page:
            print(f"Warning: Sub-comment page number mismatch. Expected {page}, got {pd}.")
            # 如果获取到的当前页为0，没有子评论，说明目前已被风控，直接返回
            # 解决办法是刷新cookie
            if pd == 0:
                return [],count
        page += 1
        # print(res['data']['replies'])
        current_page_comments,current_page_comments_count = extract_comments(res['data']['replies'])
        count += current_page_comments_count
        comments.extend(current_page_comments)
    return comments,count