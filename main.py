import json
from modules.get_comments import get_all_comments


def main():
    # 一次性抓取视频的5千条评论，触发了风控，所以需要分段获取
    # 评论上600后会漏掉一部分？是逻辑错误还是风控？
    r = get_all_comments("BV1TRjfzBEyB")
    with open('result.json', 'w', encoding='utf-8') as f:
        sub_count = 0
        for comment in r:
            sub_count += len(comment.children)
        output = {
            'comments': [comment.to_json() for comment in r],
            'count': len(r) + sub_count
        }
        json.dump(output, f, ensure_ascii=False, indent=4)
        

if __name__ == "__main__":
    main()
