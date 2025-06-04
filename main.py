import json
from modules.get_comments import get_all_comments


def main():

    # res = get_comments("BV1LQ7rz6EdU",1)
    # with open('comments.json', 'w', encoding='utf-8') as f:
    #     import json
    #     json.dump(res, f, ensure_ascii=False, indent=4)

    r = get_all_comments("BV1LQ7rz6EdU")
    with open('result.json', 'w', encoding='utf-8') as f:
        sub_count = 0
        for comment in r:
            sub_count += len(comment.children)
        output = {
            'comments': [comment.to_json() for comment in r],
            'count': len(r) + sub_count,
        }
        json.dump(output, f, ensure_ascii=False, indent=4)
        

if __name__ == "__main__":
    main()
