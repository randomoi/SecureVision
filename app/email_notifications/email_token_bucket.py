import time

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: This code was copied from referenced resources.
"""

# References:
# https://medium.com/@wanguiwawerub/rate-limiting-algorithms-token-bucket-c745c40005c
# https://python.plainenglish.io/unveiling-the-token-bucket-algorithm-an-ingenious-tool-for-api-rate-limiting-5e51a47865b7
# https://medium.com/coders-mojo/day-11-of-system-design-case-studies-series-design-api-rate-limiter-8627993c5a92
# https://dev.to/satrobit/rate-limiting-using-the-token-bucket-algorithm-3cjh
# https://code.activestate.com/recipes/511490-implementation-of-the-token-bucket-algorithm/

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = float(capacity) # maximum capacity 
        self.refill_rate = refill_rate # at ratetokens are refilled (per/sec)
        self.tokens = float(capacity) # current # of tokens in the bucket
        self.last_refill_time = time.time() # time of last token refill

 # consumes tokens from bucket
    def consume(self, tokens=1):
        if tokens <= self.refill():
            self.tokens -= tokens
            return True # if enough tokens to consume, returns true
        return False # if not, returns false

    def refill(self):
        now = time.time()
        elapsed = now - self.last_refill_time
        self.tokens = min(self.capacity, self.tokens + self.refill_rate * elapsed)
        self.last_refill_time = now
        return self.tokens # returns currect # of tokens after refill

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: This code was copied from referenced resources.
"""