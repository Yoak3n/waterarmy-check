from modules.topic import Topic
import functools
import time

def timing_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} 函数运行耗时: {end_time - start_time:.4f} 秒")
        return result
    return wrapper

@timing_decorator
def test_topic():
    topic = Topic("哈佛", "哈佛")
    topic.collect_comments()
    topic.export_to_file()
    
if __name__ == "__main__":
    test_topic()