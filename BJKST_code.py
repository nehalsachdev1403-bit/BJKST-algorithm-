# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 02:36:48 2026

@author: Manvi
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 15:39:09 2026

@author: Manvi
"""

# BJKST Algorithm 1 -- counting distinct IP addresses in a big stream
import random
import time

# ---------- 1. Turn an IP address into a number in {1, ..., m} ----------
def ip_to_number(ip):
    n = 0
    for part in ip.split("."):
        n = n * 256 + int(part)
    return n + 1                     # so the number lies in 1 .. 2^32 = m

# ---------- 2. The hash function: h(x) = (a*x + b) mod p, plus 1 ----------
P = 2**127 - 1                        # a known prime
M = P

def make_hash():
    a = random.randrange(P)
    b = random.randrange(P)
    def h(x):
        return (a * x + b) % P + 1    # value in 1 .. M
    return h, a, b                    # Return function along with parameters a and b

# ---------- 3. BJKST Algorithm  ----------
def bjkst(stream, k):
    h, a, b = make_hash()             # Step 1: choose the random hash and keep a, b
    kept = set()                      # the k smallest hash values so far
    biggest = 0                       # the largest value inside 'kept'
    for ip in stream:                 # Step 2: process one element at a time
        v = h(ip_to_number(ip))
        if v in kept:                 # ssame element again: nothing to do
            continue
        if len(kept) < k:             # Step 3: still room, just keep it
            kept.add(v)
            if len(kept) == k:
                biggest = max(kept)
        elif v < biggest:             # smaller than the largest kept value
            kept.remove(biggest)
            kept.add(v)
            biggest = max(kept)
            
    if len(kept) < k:                 # fewer than k distinct values seen
        return len(kept), a, b        # small-stream rule: count them directly
        
    zk = biggest                      # Step 4: z_k = k-th smallest value
    return k * (M + 1) / zk, a, b     # Step 5: return estimate and hash parameters a, b
    

# ---------- 4. Make a big stream with many repeats ----------
def random_ip():
    return (str(random.randint(0, 255)) + "." + str(random.randint(0, 255)) + "."
            + str(random.randint(0, 255)) + "." + str(random.randint(0, 255)))

random.seed(1)
visitors = [random_ip() for i in range(50000)]          # 50,000 different visitors
stream = [random.choice(visitors) for i in range(1000000)]   # 1,000,000 visits

true_d = len(set(stream))             # exact answer (needs lots of memory!)
k = 10                                # we keep only 10 numbers (or 1000)

print("Stream length    :", len(stream))
print("True distinct d :", true_d)
print("We store only    :", k, "hash values")
print()

for trial in range(1, 6):             # each trial uses a new random hash
    start = time.perf_counter()
    est, a, b = bjkst(stream, k)      # Unpack estimate, a, and b
    end = time.perf_counter()
    runtime = end - start
    error = abs(est - true_d) / true_d * 100
    
    # Format hash function representation cleanly
    hash_func_str = f"h(x) = ({a}*x + {b}) % P + 1"
    
    print(f"Run {trial} : estimate = {round(est)}   error = {round(error, 1)}%   runtime = {runtime:.5f}s   hash = {hash_func_str}")