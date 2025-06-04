from modules.topic import Topic


def test_topic():
    topic = Topic("玄戒", "玄戒O1")
    for video in topic.videos:
        print(video.to_json())
    
if __name__ == "__main__":
    test_topic()